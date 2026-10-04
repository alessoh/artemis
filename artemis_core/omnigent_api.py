"""Minimal, dependency-light client for the Omnigent server REST API.

Artemis talks to Omnigent the same way in two places: the Vercel relay
(``app.py``) and the command-line smoke test (``scripts/smoke_test.py``).
Both import this module, so the wire protocol lives in exactly one file.

Authentication: the website logs in as a regular, non-admin Omnigent
account (``POST /auth/login``) and sends the returned session token as a
bearer token. A real account is required because Omnigent only launches
agents in managed sandboxes for sessions owned by a live account; sessions
created by the OAuth machine client are refused at launch. The machine
client (``POST /oauth/token``) remains supported for read-only checks.

Session flow (verified against Omnigent 0.16.0 source):

1. ``POST /v1/sessions`` as multipart with a JSON ``metadata`` part and a
   gzipped agent ``bundle`` part. ``host_type: "managed"`` tells the server
   to provision a fresh Modal sandbox to run the agent.
2. ``POST /v1/sessions/{id}/events`` with a ``message`` event carrying the
   user's text.
3. ``GET /v1/sessions/{id}/stream`` returns Server-Sent Events. The stream
   does not replay history, so callers reconcile with ``GET .../items``.
"""

from __future__ import annotations

import gzip
import io
import json
import os
import tarfile
import threading
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

# Seconds before a token's stated expiry at which we proactively re-mint.
_TOKEN_REFRESH_MARGIN_S = 60
# Connect and per-request timeouts for ordinary JSON calls.
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
# Posting a message is quick once the session is ready (see wait_until_ready).
# Modal's proxy ends any single request after 150 seconds, so stay below it.
_MESSAGE_TIMEOUT = httpx.Timeout(140.0, connect=10.0)
# How often and how long to poll a managed session while its sandbox launches.
_READY_POLL_SECONDS = 3.0
# SSE reads can sit idle between heartbeats; allow a generous read gap.
_STREAM_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=30.0)
# Files and folders never shipped inside an agent bundle.
_BUNDLE_EXCLUDES = {"__pycache__", ".DS_Store", ".git"}


class OmnigentConfigError(RuntimeError):
    """Raised when required Omnigent settings are missing or malformed."""


class OmnigentAPIError(RuntimeError):
    """Raised when the Omnigent server answers with a non-success status.

    :param message: Human-readable summary of the failed call.
    :param status_code: HTTP status returned by the server.
    :param body: Response body text, truncated for safety.
    """

    def __init__(self, message: str, status_code: int, body: str) -> None:
        super().__init__(f"{message} (HTTP {status_code}): {body[:500]}")
        self.status_code = status_code
        self.body = body


@dataclass(frozen=True)
class OmnigentSettings:
    """Connection settings for one Omnigent server.

    Two ways to authenticate are supported. The preferred one is a regular
    Omnigent user account (``username`` and ``password``): Omnigent only
    launches agents in managed sandboxes for sessions owned by a real
    account. The OAuth machine client (``client_id`` and ``client_secret``)
    is kept for read-only checks and older setups.

    :param base_url: Public HTTPS URL of the Omnigent server, without a
        trailing slash, e.g. ``https://alessoh--artemis-omnigent-server.modal.run``.
    :param client_id: Machine client identifier configured on the server.
    :param client_secret: Raw machine client secret (never logged).
    :param username: Omnigent account used by the website, e.g. ``artemis-web``.
    :param password: That account's password (never logged).
    """

    base_url: str
    client_id: str = ""
    client_secret: str = ""
    username: str = ""
    password: str = ""

    @property
    def uses_account(self) -> bool:
        """True when this client logs in as a regular Omnigent account."""
        return bool(self.username and self.password)

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> OmnigentSettings:
        """Build settings from environment variables.

        Reads ``OMNIGENT_URL`` plus either ``OMNIGENT_USERNAME`` and
        ``OMNIGENT_PASSWORD`` (preferred) or ``OMNIGENT_MACHINE_CLIENT_ID``
        and ``OMNIGENT_MACHINE_CLIENT_SECRET``.

        :param environ: Mapping to read from; defaults to ``os.environ``.
        :returns: Validated settings.
        :raises OmnigentConfigError: If the URL or both credential pairs are
            missing, or the URL is not an http(s) URL.
        """
        env = environ if environ is not None else os.environ

        def get(name: str) -> str:
            return (env.get(name) or "").strip()

        base_url = get("OMNIGENT_URL").rstrip("/")
        if not base_url:
            raise OmnigentConfigError("Missing environment variables: OMNIGENT_URL")
        if not base_url.startswith(("https://", "http://")):
            raise OmnigentConfigError("OMNIGENT_URL must start with https:// or http://")
        settings = cls(
            base_url=base_url,
            client_id=get("OMNIGENT_MACHINE_CLIENT_ID"),
            client_secret=get("OMNIGENT_MACHINE_CLIENT_SECRET"),
            username=get("OMNIGENT_USERNAME"),
            password=get("OMNIGENT_PASSWORD"),
        )
        if not settings.uses_account and not (settings.client_id and settings.client_secret):
            raise OmnigentConfigError(
                "Missing environment variables: OMNIGENT_USERNAME and OMNIGENT_PASSWORD"
            )
        return settings


def build_agent_bundle(agent_dir: Path) -> bytes:
    """Pack an agent directory into the gzipped tarball Omnigent expects.

    Mirrors ``omnigent.cli``: contents sit at the archive root
    (``arcname="."``) and the gzip mtime is pinned to zero so identical
    folders always produce byte-identical bundles.

    :param agent_dir: Directory containing the agent's ``config.yaml``.
    :returns: Bundle bytes ready for upload.
    :raises FileNotFoundError: If the directory or its ``config.yaml`` is
        missing.
    """
    agent_dir = Path(agent_dir)
    if not (agent_dir / "config.yaml").is_file():
        raise FileNotFoundError(f"No config.yaml in agent directory {agent_dir}")

    def _filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
        parts = Path(info.name).parts
        if any(part in _BUNDLE_EXCLUDES for part in parts):
            return None
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = 0
        return info

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            tar.add(str(agent_dir), arcname=".", filter=_filter)
    return buf.getvalue()


def login(http: httpx.Client, base_url: str, username: str, password: str) -> tuple[str, int]:
    """Log in to an Omnigent accounts server and return its session token.

    The token is the same signed session token the Omnigent web UI keeps in
    its cookie; the server also accepts it as ``Authorization: Bearer``.

    :returns: ``(token, expires_in_seconds)``.
    :raises OmnigentAPIError: On a network failure or rejected login.
    """
    try:
        resp = http.post(f"{base_url}/auth/login", json={"username": username, "password": password})
    except httpx.HTTPError as exc:
        raise OmnigentAPIError("Login network error", 0, repr(exc)) from exc
    if resp.status_code != 200:
        raise OmnigentAPIError(f"Login as {username!r} failed", resp.status_code, resp.text)
    payload = resp.json()
    token = payload.get("token")
    if not isinstance(token, str) or not token:
        raise OmnigentAPIError("Login response had no token", resp.status_code, resp.text)
    return token, int(payload.get("expires_in", 8 * 3600))


def ensure_account(
    base_url: str,
    admin_username: str,
    admin_password: str,
    username: str,
    password: str,
    http: httpx.Client | None = None,
) -> str:
    """Make sure a regular (non-admin) Omnigent account exists and can log in.

    Uses the admin login to mint a single-use invite, then registers the
    account with it, the same steps an admin takes in the Omnigent web UI.

    :returns: ``"exists"`` if the account already worked, else ``"created"``.
    :raises OmnigentAPIError: If the admin login, invite or registration fails.
    """
    own = http or httpx.Client(timeout=_DEFAULT_TIMEOUT, follow_redirects=False)
    try:
        try:
            login(own, base_url, username, password)
            return "exists"
        except OmnigentAPIError as exc:
            if exc.status_code != 401:
                raise
        admin_token, _ = login(own, base_url, admin_username, admin_password)
        headers = {"Authorization": f"Bearer {admin_token}"}
        invite = own.post(f"{base_url}/auth/invite", json={"is_admin": False}, headers=headers)
        if invite.status_code != 200:
            raise OmnigentAPIError("Creating an invite failed", invite.status_code, invite.text)
        token = invite.json().get("token", "")
        reg = own.post(
            f"{base_url}/auth/register",
            json={"invite": token, "username": username, "password": password},
        )
        if reg.status_code == 409:
            raise OmnigentAPIError(
                f"Account {username!r} already exists with a different password", 409, reg.text
            )
        if reg.status_code != 200:
            raise OmnigentAPIError(f"Registering {username!r} failed", reg.status_code, reg.text)
        login(own, base_url, username, password)
        return "created"
    finally:
        if http is None:
            own.close()


class _TokenCache:
    """Thread-safe cache for one client-credentials access token."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at = 0.0

    def get(self, mint: Callable[[], tuple[str, int]]) -> str:
        """Return a valid token, minting a new one when needed.

        :param mint: Zero-argument callable returning ``(token, expires_in)``.
        :returns: A bearer token string.
        """
        with self._lock:
            if self._token and time.time() < self._expires_at - _TOKEN_REFRESH_MARGIN_S:
                return self._token
            token, expires_in = mint()
            self._token = token
            self._expires_at = time.time() + max(int(expires_in), _TOKEN_REFRESH_MARGIN_S + 1)
            return token

    def clear(self) -> None:
        """Forget the cached token so the next call re-mints."""
        with self._lock:
            self._token = None
            self._expires_at = 0.0


class OmnigentClient:
    """Synchronous Omnigent REST client scoped to what Artemis needs.

    :param settings: Server URL and machine credentials.
    :param http: Optional pre-built ``httpx.Client`` (useful in tests).
    """

    def __init__(self, settings: OmnigentSettings, http: httpx.Client | None = None) -> None:
        self.settings = settings
        self._http = http or httpx.Client(timeout=_DEFAULT_TIMEOUT, follow_redirects=False)
        self._tokens = _TokenCache()

    # ── authentication ──────────────────────────────────────────────

    def _mint_token(self) -> tuple[str, int]:
        """Obtain an access token: account login if configured, else machine client.

        :returns: ``(access_token, expires_in_seconds)``.
        :raises OmnigentAPIError: If the server rejects the credentials.
        """
        if self.settings.uses_account:
            return login(self._http, self.settings.base_url, self.settings.username, self.settings.password)
        try:
            resp = self._http.post(
                f"{self.settings.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                },
            )
        except httpx.HTTPError as exc:
            raise OmnigentAPIError("Token exchange network error", 0, repr(exc)) from exc
        if resp.status_code != 200:
            raise OmnigentAPIError("Token exchange failed", resp.status_code, resp.text)
        payload = resp.json()
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise OmnigentAPIError("Token response had no access_token", resp.status_code, resp.text)
        return token, int(payload.get("expires_in", 3600))

    def _auth_headers(self) -> dict[str, str]:
        """Return the Authorization header for the current token."""
        return {"Authorization": f"Bearer {self._tokens.get(self._mint_token)}"}

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an authenticated request, re-minting once on a 401.

        :param method: HTTP method.
        :param path: Path beginning with ``/``.
        :returns: The successful response.
        :raises OmnigentAPIError: On any non-2xx status after the retry, or on
            a network failure (reported with status code 0).
        """
        url = f"{self.settings.base_url}{path}"
        extra_headers = kwargs.pop("headers", {})
        for attempt in range(2):
            headers = {**extra_headers, **self._auth_headers()}
            try:
                resp = self._http.request(method, url, headers=headers, **kwargs)
            except httpx.HTTPError as exc:
                raise OmnigentAPIError(f"{method} {path} network error", 0, repr(exc)) from exc
            if resp.status_code == 401 and attempt == 0:
                self._tokens.clear()
                continue
            if 300 <= resp.status_code < 400:
                raise OmnigentAPIError(
                    f"{method} {path} was cut off by the hosting proxy (Modal ends requests "
                    "that stay open longer than 150 seconds)",
                    resp.status_code,
                    resp.headers.get("location", ""),
                )
            if resp.status_code >= 400:
                raise OmnigentAPIError(f"{method} {path} failed", resp.status_code, resp.text)
            return resp
        raise OmnigentAPIError(f"{method} {path} failed", resp.status_code, resp.text)

    # ── health and identity ─────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Call ``GET /health`` without authentication.

        :returns: The decoded JSON body, or ``{"status_code": n}`` when the
            body is not JSON.
        """
        try:
            resp = self._http.get(f"{self.settings.base_url}/health")
        except httpx.HTTPError as exc:
            return {"status_code": 0, "error": repr(exc)}
        try:
            body = resp.json()
        except ValueError:
            body = {}
        body["status_code"] = resp.status_code
        return body

    def check_credentials(self) -> bool:
        """Mint a token to prove the machine credentials are accepted.

        :returns: ``True`` on success.
        :raises OmnigentAPIError: If the server rejects them.
        """
        self._tokens.clear()
        self._auth_headers()
        return True

    # ── sessions ────────────────────────────────────────────────────

    def create_session(
        self,
        bundle: bytes,
        title: str,
        host_type: str = "managed",
        workspace: str | None = None,
    ) -> str:
        """Create a session from an uploaded agent bundle.

        :param bundle: Gzipped agent tarball from :func:`build_agent_bundle`.
        :param title: Human-readable session title.
        :param host_type: ``"managed"`` (default) has the server provision a
            Modal sandbox for this session; ``"external"`` waits for a
            runner you start yourself, which is useful for local testing.
        :param workspace: For a managed session, an optional public git URL
            (``https://github.com/org/repo#branch``) that Omnigent clones
            into the sandbox as the agent's working directory.
        :returns: The new session id.
        :raises ValueError: For an unknown host type, or a workspace on an
            external session.
        """
        if host_type not in ("managed", "external"):
            raise ValueError(f"host_type must be 'managed' or 'external', got {host_type!r}")
        metadata: dict[str, Any] = {"title": title}
        if host_type != "external":
            metadata["host_type"] = host_type
        if workspace:
            if host_type != "managed":
                raise ValueError("a git workspace is only supported for managed sessions")
            metadata["workspace"] = workspace
        resp = self._request(
            "POST",
            "/v1/sessions",
            data={"metadata": json.dumps(metadata)},
            files={"bundle": ("agent.tar.gz", bundle, "application/gzip")},
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
        session_id = resp.json().get("session_id")
        if not isinstance(session_id, str) or not session_id:
            raise OmnigentAPIError("Session create returned no session_id", resp.status_code, resp.text)
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Return the session snapshot from ``GET /v1/sessions/{id}``."""
        return self._request("GET", f"/v1/sessions/{session_id}").json()

    def post_user_message(self, session_id: str, text: str) -> dict[str, Any]:
        """Send a user message to a session.

        Call :meth:`wait_until_ready` first for a managed session: while its
        sandbox is still launching, Omnigent holds this request open, and
        Modal's proxy would cut it off after 150 seconds.

        :param session_id: Target session id.
        :param text: The message text.
        :returns: The server's acknowledgement, e.g. ``{"queued": true, ...}``.
        """
        event = {
            "type": "message",
            "data": {"role": "user", "content": [{"type": "input_text", "text": text}]},
        }
        return self._request(
            "POST", f"/v1/sessions/{session_id}/events", json=event, timeout=_MESSAGE_TIMEOUT
        ).json()

    def wait_until_ready(
        self,
        session_id: str,
        timeout_s: float = 420.0,
        on_stage: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        """Poll a session until its managed sandbox has fully launched.

        Readiness means the session is bound to a host and Omnigent no longer
        reports a sandbox launch in progress. Every poll is a short request,
        so no single call approaches Modal's 150-second limit.

        :param session_id: Session to watch.
        :param timeout_s: Give up after this many seconds.
        :param on_stage: Optional callback receiving each new launch stage.
        :returns: The ready session snapshot.
        :raises OmnigentAPIError: If the launch fails or times out.
        """
        deadline = time.monotonic() + timeout_s
        last_stage = None
        while True:
            snap = self.get_session(session_id)
            status = snap.get("sandbox_status") or None
            stage = status.get("stage") if isinstance(status, dict) else None
            if stage and stage != last_stage:
                last_stage = stage
                if on_stage:
                    on_stage(stage)
            if stage == "failed":
                raise OmnigentAPIError("Sandbox launch failed", 0, str(status.get("error")))
            if stage in (None, "ready") and snap.get("host_id"):
                return snap
            if time.monotonic() > deadline:
                raise OmnigentAPIError(
                    f"Sandbox not ready after {int(timeout_s)} seconds", 0, f"last stage: {last_stage}"
                )
            time.sleep(_READY_POLL_SECONDS)

    def diagnose(self, session_id: str) -> dict[str, Any]:
        """Collect Omnigent's own view of a session and its host for troubleshooting.

        Contains no secrets: status fields, error messages, and harness readiness.

        :param session_id: Session to inspect.
        :returns: A small dictionary of diagnostic fields.
        """
        report: dict[str, Any] = {}
        try:
            snap = self.get_session(session_id)
        except OmnigentAPIError as exc:
            return {"session_lookup_error": str(exc)[:300]}
        for key in (
            "status", "sandbox_status", "host_id", "host_online", "runner_id", "runner_online",
            "harness", "llm_model", "inference_configured", "inference_error", "last_task_error",
        ):
            report[key] = snap.get(key)
        host_id = snap.get("host_id")
        if host_id:
            try:
                host = self._request("GET", f"/v1/hosts/{host_id}").json()
                report["host_status"] = host.get("status")
                harnesses = host.get("configured_harnesses") or {}
                report["host_claude_sdk"] = harnesses.get("claude-sdk")
            except OmnigentAPIError as exc:
                report["host_lookup_error"] = str(exc)[:200]
        return report

    def list_items(self, session_id: str, after: str | None = None, limit: int = 100) -> dict[str, Any]:
        """Return one page of persisted conversation items, oldest first.

        :param session_id: Session to read.
        :param after: Cursor: return items after this item id.
        :param limit: Page size (Omnigent allows 1 to 1000).
        :returns: ``{"data": [...], "first_id", "last_id", "has_more"}``.
        """
        params: dict[str, Any] = {"limit": limit, "order": "asc"}
        if after:
            params["after"] = after
        return self._request("GET", f"/v1/sessions/{session_id}/items", params=params).json()

    def list_all_items(self, session_id: str) -> list[dict[str, Any]]:
        """Return every persisted item of a session, following pagination."""
        items: list[dict[str, Any]] = []
        after: str | None = None
        while True:
            page = self.list_items(session_id, after=after, limit=1000)
            data = page.get("data") or []
            items.extend(data)
            if not page.get("has_more") or not data:
                return items
            after = page.get("last_id") or data[-1].get("id")

    def list_child_sessions(self, session_id: str) -> list[dict[str, Any]]:
        """Return summaries of every sub-agent session spawned by a session."""
        children: list[dict[str, Any]] = []
        after: str | None = None
        while True:
            params: dict[str, Any] = {"limit": 1000, "order": "asc"}
            if after:
                params["after"] = after
            page = self._request("GET", f"/v1/sessions/{session_id}/child_sessions",
                                 params=params).json()
            data = page.get("data") or []
            children.extend(data)
            if not page.get("has_more") or not data:
                return children
            after = page.get("last_id") or data[-1].get("id")

    def delete_session(self, session_id: str) -> None:
        """Delete a session; for managed hosts this terminates the sandbox."""
        self._request("DELETE", f"/v1/sessions/{session_id}")

    def stream_lines(self, session_id: str, max_seconds: float | None = None) -> Iterator[str]:
        """Yield raw SSE lines from ``GET /v1/sessions/{id}/stream``.

        Lines are yielded exactly as received (without the trailing newline)
        so a relay can forward them verbatim. Iteration stops when the
        server closes the stream, when ``data: [DONE]`` arrives, or when
        ``max_seconds`` elapses.

        :param session_id: Session to watch.
        :param max_seconds: Optional wall-clock cap for this connection.
        :yields: SSE text lines, including blank separator lines.
        """
        started = time.monotonic()
        url = f"{self.settings.base_url}/v1/sessions/{session_id}/stream"
        headers = {"Accept": "text/event-stream", **self._auth_headers()}
        with self._http.stream("GET", url, headers=headers, timeout=_STREAM_TIMEOUT) as resp:
            if resp.status_code >= 400:
                resp.read()
                raise OmnigentAPIError("Stream open failed", resp.status_code, resp.text)
            for line in resp.iter_lines():
                yield line
                if line.strip() == "data: [DONE]":
                    return
                if max_seconds is not None and time.monotonic() - started > max_seconds:
                    return

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()


def parse_sse_events(lines: Iterator[str]) -> Iterator[dict[str, Any]]:
    """Turn raw SSE lines into decoded event dicts.

    Follows Omnigent's framing: optional ``event:`` line, then a ``data:``
    line holding a JSON envelope, separated by blank lines. Non-JSON
    payloads are skipped.

    :param lines: Raw SSE lines, e.g. from :meth:`OmnigentClient.stream_lines`.
    :yields: Decoded JSON objects that contain a ``type`` key.
    """
    for line in lines:
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict) and "type" in decoded:
            yield decoded
