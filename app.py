"""Artemis website backend for Vercel.

Vercel serves the pages in ``public/`` as static files and runs this FastAPI
app for ``/api/*``. The app relays between the browser and the Omnigent server
on Modal, and saves finished runs in the Neon database.

Lab runs (Phase 3)
------------------
``POST /api/runs``                      body ``{access_code, kind, question?}``; creates the session
``POST /api/runs/{id}/start?t=``        waits for the sandbox, sends the first message
``GET  /api/runs/{id}/stream?t=``       live Server-Sent Events; saves the run when it finishes
``POST /api/runs/{id}/finalize?t=``     saves a finished run now (idempotent)
``DELETE /api/runs/{id}?t=``            stops a run, keeping what it said so far
``GET  /api/results``                   saved and running runs (public)
``GET  /api/results/{id}``              one saved run with its report (public)
``GET  /api/cron/sync``                 Vercel Cron: saves runs nobody is watching

Phase 1 connection check (``/status`` page)
-------------------------------------------
``GET /api/status`` and ``/api/sessions...`` as before.

Starting anything costs money, so it needs the access code. A run's token is
an HMAC of its id keyed by the access code: the code never appears in a URL,
and a token unlocks only its own run. Reading saved results is public.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from collections.abc import Iterator
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from artemis_core import runs as lab_runs
from artemis_core import store
from artemis_core.omnigent_api import (
    OmnigentAPIError,
    OmnigentClient,
    OmnigentConfigError,
    OmnigentSettings,
    build_agent_bundle,
)

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
HELLO_AGENT_DIR = ROOT / "lab" / "agents" / "hello_lab"
# Close each relay connection comfortably inside Vercel Pro's 800 s limit.
RELAY_MAX_SECONDS = float(os.environ.get("ARTEMIS_RELAY_MAX_SECONDS", "720"))
# "managed" in production (a Modal sandbox per session); "external" only for local testing.
HOST_TYPE = os.environ.get("ARTEMIS_HOST_TYPE", "managed")
MAX_ACTIVE_RUNS = int(os.environ.get("ARTEMIS_MAX_ACTIVE_RUNS", "2"))
STALE_RUN_HOURS = float(os.environ.get("ARTEMIS_STALE_RUN_HOURS", "8"))
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{4,128}$")
MAX_MESSAGE_CHARS = 4000

app = FastAPI(title="Artemis", docs_url=None, redoc_url=None, openapi_url=None)


# ---------------------------------------------------------------- models
class SessionRequest(BaseModel):
    """Body of ``POST /api/sessions`` (connection check)."""

    access_code: str = Field(min_length=1, max_length=256)


class MessageRequest(BaseModel):
    """Body of ``POST /api/sessions/{id}/message`` (connection check)."""

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)


class RunRequest(BaseModel):
    """Body of ``POST /api/runs``."""

    access_code: str = Field(min_length=1, max_length=256)
    kind: str = Field(pattern="^(solar|proposal)$")
    question: str = Field(default="", max_length=lab_runs.MAX_QUESTION_CHARS + 500)


class StartRequest(BaseModel):
    """Body of ``POST /api/runs/{id}/start``; the question is resent in case the database is off."""

    kind: str = Field(pattern="^(solar|proposal)$")
    question: str = Field(default="", max_length=lab_runs.MAX_QUESTION_CHARS + 500)


# ---------------------------------------------------------------- helpers
@lru_cache(maxsize=1)
def get_client() -> OmnigentClient:
    """One Omnigent client per function instance (its login token is cached)."""
    return OmnigentClient(OmnigentSettings.from_env())


def access_code() -> str:
    """The configured access code; fails closed when it is missing."""
    code = os.environ.get("ARTEMIS_ACCESS_CODE", "").strip()
    if not code:
        raise HTTPException(status_code=503, detail="ARTEMIS_ACCESS_CODE is not configured")
    return code


def check_access_code(given: str) -> None:
    """Reject a wrong access code with a plain message."""
    if not hmac.compare_digest(access_code(), (given or "").strip()):
        raise HTTPException(status_code=403, detail="That access code is not correct.")


def stream_token(session_id: str) -> str:
    """The per-run token that unlocks start, stream, finalize and stop."""
    return hmac.new(access_code().encode(), session_id.encode(), hashlib.sha256).hexdigest()


def require_session_access(session_id: str, token: str) -> None:
    """Validate a run id and its token."""
    if not SESSION_ID_RE.fullmatch(session_id):
        raise HTTPException(status_code=400, detail="Malformed run id")
    if not hmac.compare_digest(stream_token(session_id), token or ""):
        raise HTTPException(status_code=403, detail="Invalid run token")


def upstream_error(exc: Exception) -> HTTPException:
    """Translate an Omnigent failure into a gateway error for the browser."""
    if isinstance(exc, OmnigentConfigError):
        return HTTPException(status_code=503, detail=f"The lab connection is not configured: {exc}")
    if isinstance(exc, OmnigentAPIError):
        return HTTPException(status_code=502, detail=f"The lab server answered with an error ({exc.status_code}).")
    return HTTPException(status_code=502, detail="The lab server could not be reached.")


def store_call(fn: Any, *args: Any) -> Any:
    """Call a store function, ignoring a missing or failing database."""
    if not store.available():
        return None
    try:
        return fn(*args)
    except Exception:  # the lab keeps working even if saving fails
        return None


def sse(event: dict[str, Any]) -> str:
    """Format one Artemis relay event.

    It starts with a blank line, which ends any upstream event whose closing
    blank line has not been relayed yet, so the two are never merged.
    """
    return f"\nevent: artemis.relay\ndata: {json.dumps({'type': 'artemis.relay', **event})}\n\n"


def finalize_run(session_id: str, delete_session: bool = True) -> dict[str, Any]:
    """Save a run if its final report exists; return what happened.

    :returns: ``{"state": "complete" | "running" | "missing", ...}``.
    """
    client = get_client()
    try:
        items = client.list_all_items(session_id)
    except OmnigentAPIError as exc:
        if exc.status_code == 404:
            return {"state": "missing"}
        raise
    messages = lab_runs.assistant_messages(items)
    report = lab_runs.final_report(messages)
    if report is None:
        store_call(store.save_messages, session_id, messages[-200:])
        return {"state": "running", "messages": len(messages)}
    existing = store_call(store.get_run, session_id) or {}
    fallback = existing.get("title") or "Artemis lab run"
    title = lab_runs.report_title(report, fallback)
    store_call(store.complete_run, session_id, title, report, messages[-200:])
    if delete_session:
        try:
            client.delete_session(session_id)  # stops the sandbox; the report is saved
        except OmnigentAPIError:
            pass
    return {"state": "complete", "title": title, "result_url": f"/results/run?id={session_id}"}


# ---------------------------------------------------------------- status
@app.get("/api/status")
def status() -> JSONResponse:
    """Configuration, server health, credentials and database, without secrets."""
    report: dict[str, Any] = {"configured": False, "server_ok": False, "credentials_ok": False,
                              "database": "not configured", "active_runs": None, "detail": ""}
    if store.available():
        try:
            report["active_runs"] = len(store.active_runs())
            report["database"] = "connected"
        except Exception as exc:
            report["database"] = f"error: {type(exc).__name__}"
    try:
        client = get_client()
    except OmnigentConfigError as exc:
        report["detail"] = str(exc)
        return JSONResponse(report)
    report["configured"] = True
    try:
        report["server_ok"] = client.health().get("status_code") == 200
        client.check_credentials()
        report["credentials_ok"] = True
    except Exception as exc:  # report, never raise, from a status probe
        report["detail"] = str(exc)[:300]
    return JSONResponse(report)


# ---------------------------------------------------------------- lab runs
@app.post("/api/runs")
def create_run(body: RunRequest) -> JSONResponse:
    """Create a managed lab session for a flagship run or a proposal."""
    check_access_code(body.access_code)
    kind = lab_runs.RUN_KINDS[body.kind]
    question = lab_runs.clean_question(body.question)
    if kind.needs_question and len(question) < 15:
        raise HTTPException(status_code=422, detail="Please describe the question in at least a sentence.")
    active = store_call(store.active_runs)
    if active is not None and len(active) >= MAX_ACTIVE_RUNS:
        raise HTTPException(status_code=429, detail=(
            f"{len(active)} runs are already in progress, the most the lab runs at once. "
            "Watch one of them on the Results page, or try again when one finishes."))
    try:
        session_id = get_client().create_session(
            build_agent_bundle(kind.agent_dir), f"Artemis: {kind.title}"[:120], HOST_TYPE,
            workspace=lab_runs.repo_workspace() if HOST_TYPE == "managed" else None)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    title = kind.title if body.kind == "solar" else (question.split("\n", 1)[0][:140] or kind.title)
    store_call(store.create_run, session_id, body.kind, title,
               lab_runs.SOLAR_QUESTION if body.kind == "solar" else question)
    return JSONResponse({"run_id": session_id, "token": stream_token(session_id), "kind": body.kind,
                         "title": title, "typical_minutes": kind.typical_minutes,
                         "saving": store.available()})


@app.post("/api/runs/{run_id}/start")
def start_run(run_id: str, body: StartRequest, t: str = Query(default="")) -> JSONResponse:
    """Wait for the sandbox with short polls, then send the first message."""
    require_session_access(run_id, t)
    saved = store_call(store.get_run, run_id) or {}
    kind = saved.get("kind") or body.kind
    question = saved.get("question") or body.question
    try:
        client = get_client()
        if HOST_TYPE == "managed":
            client.wait_until_ready(run_id, timeout_s=RELAY_MAX_SECONDS - 60)
        client.post_user_message(run_id, lab_runs.kickoff_message(kind, question))
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        store_call(store.set_status, run_id, "failed", "The lab could not start this run.")
        raise upstream_error(exc) from exc
    store_call(store.set_status, run_id, "running")
    return JSONResponse({"run_id": run_id, "state": "running"})


@app.get("/api/runs/{run_id}/stream")
def run_stream(run_id: str, t: str = Query(default="")) -> StreamingResponse:
    """Relay a run's live events; save it the moment its report is complete."""
    require_session_access(run_id, t)
    try:
        client = get_client()
    except OmnigentConfigError as exc:
        raise upstream_error(exc) from exc

    def generate() -> Iterator[str]:
        yield "retry: 1500\n\n"
        yield sse({"state": "connected"})
        turn_text = ""
        try:
            for line in client.stream_lines(run_id, max_seconds=RELAY_MAX_SECONDS):
                yield line + "\n"
                if not line.startswith("data:"):
                    continue
                try:
                    event = json.loads(line[5:].strip())
                except (json.JSONDecodeError, ValueError):
                    continue
                etype = event.get("type") if isinstance(event, dict) else None
                if etype == "response.output_text.delta":
                    turn_text += str(event.get("delta") or "")
                elif etype in ("turn.completed", "response.completed"):
                    if lab_runs.COMPLETE_MARKER in turn_text:
                        outcome: dict[str, Any] = {"state": "save_failed"}
                        # The stored history can lag the live stream by a moment.
                        for attempt in range(6):
                            try:
                                outcome = finalize_run(run_id)
                            except Exception:
                                outcome = {"state": "save_failed"}
                            if outcome.get("state") == "complete":
                                break
                            time.sleep(2 + attempt)
                        yield sse({**outcome, "outcome": outcome.get("state"), "state": "finished"})
                        return
                    turn_text = ""
        except OmnigentAPIError as exc:
            yield sse({"state": "upstream_error", "status": exc.status_code})
            return
        except Exception:  # network drop; the browser reconnects
            pass
        yield sse({"state": "rotating"})

    headers = {"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no", "Connection": "keep-alive"}
    return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)


@app.post("/api/runs/{run_id}/finalize")
def finalize(run_id: str, t: str = Query(default="")) -> JSONResponse:
    """Save a finished run now; reports 'running' if it has not finished."""
    require_session_access(run_id, t)
    try:
        return JSONResponse(finalize_run(run_id))
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc


@app.delete("/api/runs/{run_id}")
def stop_run(run_id: str, t: str = Query(default="")) -> JSONResponse:
    """Stop a run: keep what the lead said so far, then end the sandbox."""
    require_session_access(run_id, t)
    try:
        client = get_client()
        try:
            messages = lab_runs.assistant_messages(client.list_all_items(run_id))
            store_call(store.save_messages, run_id, messages[-200:])
        except OmnigentAPIError:
            pass
        client.delete_session(run_id)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    store_call(store.set_status, run_id, "stopped", "Stopped by the visitor.")
    return JSONResponse({"run_id": run_id, "state": "stopped"})


# ---------------------------------------------------------------- results
@app.get("/api/results")
def results() -> JSONResponse:
    """Runs saved in the database (the static flagship result is in /data/results.json)."""
    if not store.available():
        return JSONResponse({"database": False, "runs": []})
    try:
        return JSONResponse({"database": True, "runs": store.list_runs()})
    except Exception:
        return JSONResponse({"database": False, "runs": [], "detail": "The results database did not answer."})


@app.get("/api/results/{run_id}")
def result(run_id: str) -> JSONResponse:
    """One saved run with its report and the lead's messages."""
    if not SESSION_ID_RE.fullmatch(run_id):
        raise HTTPException(status_code=400, detail="Malformed run id")
    if not store.available():
        raise HTTPException(status_code=404, detail="No saved run with that id.")
    try:
        row = store.get_run(run_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The results database did not answer.") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="No saved run with that id.")
    return JSONResponse(row)


@app.get("/api/cron/sync")
def cron_sync(request: Request) -> JSONResponse:
    """Save runs that finished while nobody was watching; end stale ones.

    Vercel Cron calls this with ``Authorization: Bearer $CRON_SECRET`` when
    CRON_SECRET is set; then any other caller is refused.
    """
    secret = os.environ.get("CRON_SECRET", "")
    if secret and not hmac.compare_digest(request.headers.get("authorization", ""), f"Bearer {secret}"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not store.available():
        return JSONResponse({"database": False, "checked": 0})
    outcomes: dict[str, str] = {}
    now = datetime.now(timezone.utc)
    for row in store.active_runs():
        run_id = row["id"]
        try:
            outcome = finalize_run(run_id)
        except Exception as exc:
            outcomes[run_id] = f"error: {type(exc).__name__}"
            continue
        state = outcome["state"]
        if state == "missing":
            store_call(store.set_status, run_id, "failed", "The lab session ended without a report.")
        elif state == "running":
            started = datetime.strptime(row["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (now - started).total_seconds() > STALE_RUN_HOURS * 3600:
                try:
                    get_client().delete_session(run_id)
                except Exception:
                    pass
                store_call(store.set_status, run_id, "stopped",
                           f"Stopped after {STALE_RUN_HOURS:g} hours without a report.")
                state = "stopped"
        outcomes[run_id] = state
    return JSONResponse({"database": True, "checked": len(outcomes), "outcomes": outcomes})


# ---------------------------------------------------------------- connection check (Phase 1)
@app.post("/api/sessions")
def create_session(body: SessionRequest) -> JSONResponse:
    """Create a managed session running the small test agent."""
    check_access_code(body.access_code)
    try:
        session_id = get_client().create_session(build_agent_bundle(HELLO_AGENT_DIR),
                                                 "Artemis connection check", HOST_TYPE)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"session_id": session_id, "stream_token": stream_token(session_id)})


@app.post("/api/sessions/{session_id}/message")
def send_message(session_id: str, body: MessageRequest, t: str = Query(default="")) -> JSONResponse:
    """Send the test question once the sandbox is ready."""
    require_session_access(session_id, t)
    try:
        client = get_client()
        if HOST_TYPE == "managed":
            client.wait_until_ready(session_id, timeout_s=RELAY_MAX_SECONDS - 60)
        ack = client.post_user_message(session_id, body.message.strip())
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"session_id": session_id, "ack": ack})


@app.get("/api/sessions/{session_id}/stream")
def relay_stream(session_id: str, t: str = Query(default="")) -> StreamingResponse:
    """Relay the test session's events."""
    require_session_access(session_id, t)
    try:
        client = get_client()
    except OmnigentConfigError as exc:
        raise upstream_error(exc) from exc

    def generate() -> Iterator[str]:
        yield "retry: 1500\n\n"
        yield sse({"state": "connected"})
        try:
            for line in client.stream_lines(session_id, max_seconds=RELAY_MAX_SECONDS):
                yield line + "\n"
        except OmnigentAPIError as exc:
            yield sse({"state": "upstream_error", "status": exc.status_code})
            return
        except Exception:
            pass
        yield sse({"state": "rotating"})

    headers = {"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no", "Connection": "keep-alive"}
    return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)


@app.get("/api/sessions/{session_id}/items")
def session_items(session_id: str, t: str = Query(default="")) -> JSONResponse:
    """Stored history of the test session."""
    require_session_access(session_id, t)
    try:
        return JSONResponse(get_client().list_items(session_id))
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc


@app.delete("/api/sessions/{session_id}")
def end_session(session_id: str, t: str = Query(default="")) -> JSONResponse:
    """End the test session and its sandbox."""
    require_session_access(session_id, t)
    try:
        get_client().delete_session(session_id)
    except (OmnigentConfigError, OmnigentAPIError) as exc:
        raise upstream_error(exc) from exc
    return JSONResponse({"deleted": session_id})


# ---------------------------------------------------------------- pages
def not_found_page() -> HTMLResponse:
    """The site's 404 page (a plain one if the file is not bundled)."""
    page = PUBLIC / "404.html"
    if page.exists():
        return HTMLResponse(page.read_text(encoding="utf-8"), status_code=404)
    return HTMLResponse("<!doctype html><title>Page not found</title><h1>Page not found</h1>"
                        '<p><a href="/">Go to the Artemis home page</a></p>', status_code=404)


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException) -> Response:
    """JSON errors for the API; the 404 page for everything else."""
    if request.url.path.startswith("/api/") or exc.status_code != 404:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    return not_found_page()


if os.environ.get("ARTEMIS_SERVE_STATIC") == "1":
    # Local development only: serve public/ the way Vercel does (cleanUrls).
    @app.get("/{path:path}", include_in_schema=False)
    def static_pages(path: str) -> Response:
        """Serve /x from public/x.html, public/x or public/x/index.html."""
        clean = path.strip("/")
        if clean.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        if ".." in clean:
            return not_found_page()
        candidates = [PUBLIC / "index.html"] if not clean else [
            PUBLIC / f"{clean}.html", PUBLIC / clean, PUBLIC / clean / "index.html"]
        for candidate in candidates:
            if candidate.is_file():
                return FileResponse(candidate)
        return not_found_page()
