"""Artemis website backend for Vercel (Phase 1: the plumbing relay).

Vercel runs this FastAPI app as a Python function, and serves
``public/index.html`` as the page. The app is a thin, stateless relay
between the browser and the Omnigent server on Modal:

``GET  /api/status``
    Reports whether the Omnigent server answers and accepts our machine
    credentials. Safe to call without an access code; reveals no secrets.

``POST /api/sessions``
    Body ``{"access_code": str}``. Checks the access code, creates a managed
    Omnigent session running the hello_lab test agent, and returns
    ``{"session_id", "stream_token"}`` straight away.

``POST /api/sessions/{id}/message?t=<stream_token>``
    Body ``{"message": str}``. Waits (with short polls) until the managed
    Modal sandbox has launched, then sends the user's message. The browser
    opens the stream first and watches the launch stages while this waits.

``GET  /api/sessions/{id}/stream?t=<stream_token>``
    Relays the session's Server-Sent Events verbatim. Each connection ends
    before Vercel's function limit and tells the browser to reconnect, so
    a session can be watched for hours.

``GET  /api/sessions/{id}/items?t=<stream_token>``
    Returns stored history so a reconnecting page can catch up.

``DELETE /api/sessions/{id}?t=<stream_token>``
    Ends the session, which terminates its Modal sandbox.

The stream token is an HMAC of the session id keyed by the access code, so
the code itself never appears in a URL, and a token only unlocks the one
session it was issued for.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from artemis_core.omnigent_api import (
    OmnigentAPIError,
    OmnigentClient,
    OmnigentConfigError,
    OmnigentSettings,
    build_agent_bundle,
)

AGENT_DIR = Path(__file__).resolve().parent / "lab" / "agents" / "hello_lab"
# Close each relay connection comfortably inside Vercel Pro's 800 s limit.
RELAY_MAX_SECONDS = float(os.environ.get("ARTEMIS_RELAY_MAX_SECONDS", "720"))
# "managed" in production (a Modal sandbox per session); "external" only for local testing.
HOST_TYPE = os.environ.get("ARTEMIS_HOST_TYPE", "managed")
# Omnigent session ids look like "conv_..." ; reject anything unexpected.
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{4,128}$")
MAX_MESSAGE_CHARS = 4000

app = FastAPI(title="Artemis relay", docs_url=None, redoc_url=None, openapi_url=None)


class SessionRequest(BaseModel):
    """Body of ``POST /api/sessions``."""

    access_code: str = Field(min_length=1, max_length=256)


class MessageRequest(BaseModel):
    """Body of ``POST /api/sessions/{id}/message``."""

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)


@lru_cache(maxsize=1)
def get_client() -> OmnigentClient:
    """Build one Omnigent client per function instance (token is cached).

    :raises OmnigentConfigError: If Omnigent environment variables are missing.
    """
    return OmnigentClient(OmnigentSettings.from_env())


def access_code() -> str:
    """Return the configured access code or fail closed.

    :raises HTTPException: 503 when ``ARTEMIS_ACCESS_CODE`` is not set.
    """
    code = os.environ.get("ARTEMIS_ACCESS_CODE", "").strip()
    if not code:
        raise HTTPException(status_code=503, detail="ARTEMIS_ACCESS_CODE is not configured")
    return code


def stream_token(session_id: str) -> str:
    """Derive the per-session token that unlocks stream, items and delete."""
    return hmac.new(access_code().encode(), session_id.encode(), hashlib.sha256).hexdigest()


def require_session_access(session_id: str, token: str) -> None:
    """Validate a session id and its stream token.

    :raises HTTPException: 400 for a malformed id, 403 for a bad token.
    """
    if not SESSION_ID_RE.fullmatch(session_id):
        raise HTTPException(status_code=400, detail="Malformed session id")
    if not hmac.compare_digest(stream_token(session_id), token or ""):
        raise HTTPException(status_code=403, detail="Invalid stream token")


def upstream_error(exc: Exception) -> HTTPException:
    """Translate an Omnigent failure into a gateway error for the browser."""
    if isinstance(exc, OmnigentConfigError):
        return HTTPException(status_code=503, detail=f"Relay not configured: {exc}")
    if isinstance(exc, OmnigentAPIError):
        return HTTPException(status_code=502, detail=f"Omnigent error {exc.status_code}: {exc.body[:300]}")
    return HTTPException(status_code=502, detail=f"Upstream error: {exc!r}"[:400])


@app.get("/api/status")
def status() -> JSONResponse:
    """Report configuration, server health and credential acceptance."""
    report = {"configured": False, "server_ok": False, "credentials_ok": False, "omnigent_url": None, "detail": ""}
    try:
        client = get_client()
    except OmnigentConfigError as exc:
        report["detail"] = str(exc)
        return JSONResponse(report)
    report["configured"] = True
    report["omnigent_url"] = client.settings.base_url
    try:
        health = client.health()
        report["server_ok"] = health.get("status_code") == 200
        client.check_credentials()
        report["credentials_ok"] = True
    except Exception as exc:  # report, never raise, from a status probe
        report["detail"] = str(exc)[:300]
    return JSONResponse(report)


@app.post("/api/sessions")
def create_session(body: SessionRequest) -> JSONResponse:
    """Create a managed lab session; the message is sent separately."""
    if not hmac.compare_digest(access_code(), body.access_code.strip()):
        raise HTTPException(status_code=403, detail="Incorrect access code")
    try:
        session_id = get_client().create_session(build_agent_bundle(AGENT_DIR), "Artemis Phase 1", HOST_TYPE)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"session_id": session_id, "stream_token": stream_token(session_id)})


@app.post("/api/sessions/{session_id}/message")
def send_message(session_id: str, body: MessageRequest, t: str = Query(default="")) -> JSONResponse:
    """Send a user message; may wait while a managed sandbox launches."""
    require_session_access(session_id, t)
    try:
        client = get_client()
        if HOST_TYPE == "managed":
            # Short polls while Modal starts the sandbox; posting earlier would
            # hold one request open past Modal's 150-second proxy limit.
            client.wait_until_ready(session_id, timeout_s=RELAY_MAX_SECONDS - 60)
        ack = client.post_user_message(session_id, body.message.strip())
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"session_id": session_id, "ack": ack})


@app.get("/api/sessions/{session_id}/stream")
def relay_stream(session_id: str, t: str = Query(default="")) -> StreamingResponse:
    """Relay one session's Server-Sent Events to the browser."""
    require_session_access(session_id, t)
    try:
        client = get_client()
    except OmnigentConfigError as exc:
        raise upstream_error(exc) from exc

    def generate() -> Iterator[str]:
        # Ask EventSource to reconnect quickly when this connection closes.
        yield "retry: 1500\n\n"
        yield 'event: artemis.relay\ndata: {"type": "artemis.relay", "state": "connected"}\n\n'
        try:
            for line in client.stream_lines(session_id, max_seconds=RELAY_MAX_SECONDS):
                yield line + "\n"
        except OmnigentAPIError as exc:
            yield f'event: artemis.relay\ndata: {{"type": "artemis.relay", "state": "upstream_error", "status": {exc.status_code}}}\n\n'
            return
        except Exception:  # network drop; the browser will reconnect
            pass
        yield 'event: artemis.relay\ndata: {"type": "artemis.relay", "state": "rotating"}\n\n'

    headers = {"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no", "Connection": "keep-alive"}
    return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)


@app.get("/api/sessions/{session_id}/items")
def session_items(session_id: str, t: str = Query(default="")) -> JSONResponse:
    """Return stored history for catch-up after a reconnect."""
    require_session_access(session_id, t)
    try:
        return JSONResponse(get_client().list_items(session_id))
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc


@app.delete("/api/sessions/{session_id}")
def end_session(session_id: str, t: str = Query(default="")) -> JSONResponse:
    """Delete the session, terminating its Modal sandbox."""
    require_session_access(session_id, t)
    try:
        get_client().delete_session(session_id)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"deleted": session_id})
