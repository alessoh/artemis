"""Phase 1 smoke test: prove every connection in the Artemis lab, end to end.

Run from the repository root after the Omnigent server is deployed:

    python scripts/smoke_test.py
    python scripts/smoke_test.py --message "Which materials make good solar absorbers?"
    python scripts/smoke_test.py --via-website https://artemis-xyz.vercel.app

Direct mode (the default) talks to the Omnigent server with the machine
credentials in ``.env`` and checks five hops in order:

1. Server reachable        GET /health answers.
2. Credentials accepted    POST /oauth/token mints a machine token.
3. Session created         POST /v1/sessions with host_type "managed".
4. Sandbox and model       the live stream shows the sandbox reach "ready"
                           and the model's reply arrive as text deltas.
5. History persisted       GET /v1/sessions/{id}/items returns the turn.

``--via-website`` runs the same journey through the deployed Vercel relay
instead, which also proves the website hop and its streaming.

Every run writes a JSON record to ``runs/`` with timestamps for each hop,
so Phase 1 leaves real, reproducible evidence rather than a claim.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from artemis_core.omnigent_api import (  # noqa: E402
    OmnigentAPIError,
    OmnigentClient,
    OmnigentConfigError,
    OmnigentSettings,
    build_agent_bundle,
    parse_sse_events,
)

AGENT_DIR = REPO_ROOT / "lab" / "agents" / "hello_lab"
RUNS_DIR = REPO_ROOT / "runs"
DEFAULT_MESSAGE = "Which earth-abundant materials could make efficient solar cells?"
TERMINAL_EVENTS = {"turn.completed", "turn.failed", "response.completed", "response.failed"}


def load_dotenv(path: Path) -> dict[str, str]:
    """Read KEY=VALUE pairs from a .env file without printing them.

    :param path: Path to the .env file.
    :returns: Parsed values; empty when the file does not exist.
    """
    values: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class HopRecorder:
    """Collect pass or fail results with elapsed times for each hop."""

    def __init__(self) -> None:
        self.started = time.monotonic()
        self.hops: list[dict[str, Any]] = []

    def elapsed(self) -> float:
        """Seconds since the run began."""
        return round(time.monotonic() - self.started, 2)

    def record(self, name: str, ok: bool, detail: str = "") -> bool:
        """Record and print one hop result.

        :param name: Hop name.
        :param ok: Whether it passed.
        :param detail: Short human-readable detail.
        :returns: ``ok``, so callers can chain on it.
        """
        entry = {"hop": name, "ok": ok, "t_seconds": self.elapsed(), "detail": detail}
        self.hops.append(entry)
        mark = "PASS" if ok else "FAIL"
        print(f"[{entry['t_seconds']:>7.2f}s] {mark}  {name}" + (f"  ({detail})" if detail else ""))
        return ok


def watch_stream(lines_iter, events: queue.Queue, stop: threading.Event) -> None:
    """Background worker: push decoded SSE events onto a queue.

    :param lines_iter: Iterator of raw SSE lines.
    :param events: Queue receiving ``(kind, payload)`` tuples.
    :param stop: Set by the main thread to end early.
    """
    try:
        for event in parse_sse_events(lines_iter):
            events.put(("event", event))
            if stop.is_set():
                return
    except Exception as exc:  # surfaced to the main thread as data
        events.put(("error", repr(exc)))
    finally:
        events.put(("closed", None))


def start_poster(post) -> dict[str, Any]:
    """Send the message on a background thread.

    For a managed session Omnigent holds the post open until the sandbox
    is ready, so the main thread keeps reading the stream meanwhile.

    :param post: Zero-argument callable that sends the message.
    :returns: Dict that receives ``ack`` or ``error`` plus the ``thread``.
    """
    box: dict[str, Any] = {}

    def _run() -> None:
        try:
            box["ack"] = post()
        except Exception as exc:  # recorded and reported by the caller
            box["error"] = str(exc)[:400]

    box["thread"] = threading.Thread(target=_run, daemon=True)
    box["thread"].start()
    return box


def consume(events: queue.Queue, recorder: HopRecorder, timeout_s: float) -> dict[str, Any]:
    """Read stream events until the turn ends or the timeout passes.

    :returns: Summary with the reply text, stages seen and event counts.
    """
    summary: dict[str, Any] = {"reply": "", "stages": [], "event_types": {}, "terminal": None, "errors": []}
    sandbox_ready_marked = False
    first_text_marked = False
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            kind, payload = events.get(timeout=1.0)
        except queue.Empty:
            continue
        if kind == "closed":
            break
        if kind == "error":
            summary["errors"].append(payload)
            break
        etype = payload.get("type", "?")
        summary["event_types"][etype] = summary["event_types"].get(etype, 0) + 1
        if etype == "session.sandbox_status":
            stage = payload.get("stage")
            summary["stages"].append(stage)
            print(f"[{recorder.elapsed():>7.2f}s]       sandbox stage: {stage}")
            if stage == "failed":
                summary["errors"].append(payload.get("error") or "sandbox launch failed")
                recorder.record("Sandbox launched", False, str(payload.get("error")))
                break
            if stage == "ready" and not sandbox_ready_marked:
                sandbox_ready_marked = recorder.record("Sandbox launched", True, "stage ready")
        elif etype == "response.output_text.delta":
            if not first_text_marked:
                if not sandbox_ready_marked:
                    sandbox_ready_marked = recorder.record("Sandbox launched", True, "inferred from model output")
                first_text_marked = recorder.record("Model replied", True, "first text delta received")
            summary["reply"] += str(payload.get("delta") or "")
        elif etype in ("response.error", "turn.failed", "response.failed"):
            summary["errors"].append(json.dumps(payload)[:400])
        if etype in TERMINAL_EVENTS:
            summary["terminal"] = etype
            break
    return summary


def run_direct(message: str, timeout_s: float, keep: bool, host_type: str = "managed") -> dict[str, Any]:
    """Run the five-hop check directly against the Omnigent server."""
    recorder = HopRecorder()
    env = {**load_dotenv(REPO_ROOT / ".env")}
    env.update({k: v for k, v in os.environ.items() if k.startswith(("OMNIGENT_", "ARTEMIS_"))})
    try:
        settings = OmnigentSettings.from_env(env)
    except OmnigentConfigError as exc:
        recorder.record("Configuration", False, str(exc))
        return {"mode": "direct", "hops": recorder.hops}

    client = OmnigentClient(settings)
    result: dict[str, Any] = {"mode": "direct", "omnigent_url": settings.base_url, "message": message}
    session_id = None
    try:
        health = client.health()
        if not recorder.record("Server reachable", health.get("status_code") == 200, f"HTTP {health.get('status_code')}"):
            return {**result, "hops": recorder.hops}
        client.check_credentials()
        recorder.record("Credentials accepted", True, "machine token minted")

        session_id = client.create_session(build_agent_bundle(AGENT_DIR), "Artemis Phase 1 smoke test", host_type)
        result["session_id"] = session_id
        recorder.record("Session created", True, session_id)

        events: queue.Queue = queue.Queue()
        stop = threading.Event()
        worker = threading.Thread(
            target=watch_stream,
            args=(client.stream_lines(session_id, max_seconds=timeout_s), events, stop),
            daemon=True,
        )
        worker.start()
        time.sleep(1.0)  # let the stream subscribe before the first message
        poster = start_poster(lambda: client.post_user_message(session_id, message))
        print(f"[{recorder.elapsed():>7.2f}s]       message sent; watching sandbox launch and model reply")

        summary = consume(events, recorder, timeout_s)
        stop.set()
        poster["thread"].join(timeout=5)
        if poster.get("error"):
            summary["errors"].append("message post: " + poster["error"])
        result["stream"] = summary
        ok_turn = summary["terminal"] in ("turn.completed", "response.completed") and bool(summary["reply"].strip())
        recorder.record("Turn completed", ok_turn, summary["terminal"] or "no terminal event before timeout")
        if summary["errors"]:
            print("       errors: " + " | ".join(summary["errors"])[:800])

        items = client.list_items(session_id)
        count = len(items.get("data") or items.get("items") or [])
        recorder.record("History persisted", count > 0, f"{count} items stored")
    except OmnigentAPIError as exc:
        recorder.record("API call", False, str(exc))
    finally:
        if session_id and not keep:
            try:
                client.delete_session(session_id)
                print(f"[{recorder.elapsed():>7.2f}s]       session deleted (sandbox terminated)")
            except OmnigentAPIError as exc:
                print(f"       cleanup warning: {exc}")
        client.close()
    return {**result, "hops": recorder.hops}


def run_via_website(base_url: str, message: str, timeout_s: float, access_code: str) -> dict[str, Any]:
    """Run the journey through the deployed Vercel relay."""
    recorder = HopRecorder()
    base = base_url.rstrip("/")
    result: dict[str, Any] = {"mode": "website", "website_url": base, "message": message}
    with httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0)) as http:
        status = http.get(f"{base}/api/status")
        body = status.json() if status.headers.get("content-type", "").startswith("application/json") else {}
        if not recorder.record("Website reachable", status.status_code == 200, f"HTTP {status.status_code}"):
            return {**result, "hops": recorder.hops}
        recorder.record("Server reachable via website", bool(body.get("server_ok")), json.dumps(body)[:200])
        recorder.record("Credentials accepted via website", bool(body.get("credentials_ok")), "")

        created = http.post(f"{base}/api/sessions", json={"access_code": access_code})
        if created.status_code != 200:
            recorder.record("Session created via website", False, created.text[:200])
            return {**result, "hops": recorder.hops}
        info = created.json()
        recorder.record("Session created via website", True, info["session_id"])
        result["session_id"] = info["session_id"]
        token = {"t": info["stream_token"]}

        events: queue.Queue = queue.Queue()
        stop = threading.Event()

        def website_lines():
            url = f"{base}/api/sessions/{info['session_id']}/stream"
            timeout = httpx.Timeout(connect=10, read=120, write=30, pool=30)
            with httpx.stream("GET", url, params=token, timeout=timeout) as resp:
                resp.raise_for_status()
                yield from resp.iter_lines()

        threading.Thread(target=watch_stream, args=(website_lines(), events, stop), daemon=True).start()
        time.sleep(1.5)

        def post_via_website() -> dict[str, Any]:
            r = httpx.post(f"{base}/api/sessions/{info['session_id']}/message", params=token,
                           json={"message": message}, timeout=httpx.Timeout(300.0, connect=10.0))
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            return r.json()

        poster = start_poster(post_via_website)
        summary = consume(events, recorder, timeout_s)
        stop.set()
        poster["thread"].join(timeout=5)
        if poster.get("error"):
            summary["errors"].append("message post: " + poster["error"])
        result["stream"] = summary
        ok_turn = summary["terminal"] in ("turn.completed", "response.completed") and bool(summary["reply"].strip())
        recorder.record("Turn completed via website", ok_turn, summary["terminal"] or "no terminal event before timeout")
        if summary["errors"]:
            print("       errors: " + " | ".join(summary["errors"])[:800])
        gone = http.delete(f"{base}/api/sessions/{info['session_id']}", params=token)
        print(f"[{recorder.elapsed():>7.2f}s]       session delete via website: HTTP {gone.status_code}")
    return {**result, "hops": recorder.hops}


def main() -> int:
    """Parse arguments, run the chosen mode, print and save the record."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Message to send to the test agent.")
    parser.add_argument("--timeout", type=float, default=240.0, help="Seconds to wait for the turn to finish.")
    parser.add_argument("--keep", action="store_true", help="Keep the session (and sandbox) after the test.")
    parser.add_argument("--via-website", metavar="URL", help="Run through the deployed Vercel website instead.")
    parser.add_argument("--host-type", choices=["managed", "external"], default="managed",
                        help="managed (default): server launches a Modal sandbox; external: use your own runner.")
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    if args.via_website:
        code = os.environ.get("ARTEMIS_ACCESS_CODE") or load_dotenv(REPO_ROOT / ".env").get("ARTEMIS_ACCESS_CODE", "")
        record = run_via_website(args.via_website, args.message, args.timeout, code)
    else:
        record = run_direct(args.message, args.timeout, args.keep, args.host_type)
    record["started_at"] = started_at
    record["passed"] = bool(record["hops"]) and all(h["ok"] for h in record["hops"])

    reply = (record.get("stream") or {}).get("reply", "").strip()
    if reply:
        print("\nAgent reply:\n" + reply)
    RUNS_DIR.mkdir(exist_ok=True)
    out = RUNS_DIR / f"phase1_smoke_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"\n{'PHASE 1 PASSED' if record['passed'] else 'PHASE 1 NOT YET PASSING'}  (record saved to {out.relative_to(REPO_ROOT)})")
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
