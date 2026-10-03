"""Record everything that happens during one lab test, for troubleshooting.

Run from the artemis folder after the server is deployed:

    python scripts/diagnose_phase1.py

It starts one test session exactly like the smoke test, and for up to six
minutes records, with timestamps:

* every live event Omnigent streams for the session,
* Omnigent's own view of the session every five seconds,
* the server logs of the Omnigent app on Modal, and
* the logs of the Modal sandboxes Omnigent starts.

Everything is written to one file, runs/diagnosis_<time>.txt, with keys,
tokens, passwords and database credentials removed. Attach that file in the
chat with Claude. The session is deleted at the end, which stops its sandbox.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from artemis_core.omnigent_api import (  # noqa: E402
    OmnigentAPIError,
    OmnigentClient,
    OmnigentSettings,
    build_agent_bundle,
    parse_sse_events,
)
from smoke_test import AGENT_DIR, DEFAULT_MESSAGE, load_dotenv  # noqa: E402

WATCH_SECONDS = 360
# Modal apps whose logs we capture: the Omnigent server and its sandboxes.
LOG_APPS = ["artemis-omnigent", "omnigent-sandboxes"]
TERMINAL = {"turn.completed", "turn.failed", "response.completed", "response.failed"}

# Patterns removed from everything written to the report.
REDACTIONS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]+"), "sk-ant-[REDACTED]"),
    (re.compile(r"\b(ak|as|wk|ws)-[A-Za-z0-9]{8,}"), r"\1-[REDACTED]"),
    (re.compile(r"(postgres(?:ql)?(?:\+psycopg)?://)[^@\s/]+@"), r"\1[REDACTED]@"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+"), r"\1[REDACTED]"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+"), "[JWT-REDACTED]"),
    (re.compile(r"(?i)((?:token|secret|password|api_key|apikey)[\"']?\s*[:=]\s*[\"']?)[^\s\"',}]+"), r"\1[REDACTED]"),
]


def redact(text: str, extra_secrets: list[str]) -> str:
    """Remove secrets from text: known values first, then generic patterns."""
    for value in extra_secrets:
        if value and len(value) >= 8:
            text = text.replace(value, "[REDACTED]")
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


class Timeline:
    """Thread-safe, timestamped list of report lines."""

    def __init__(self) -> None:
        self.t0 = time.monotonic()
        self.lines: list[str] = []
        self.lock = threading.Lock()

    def add(self, text: str, echo: bool = False) -> None:
        stamp = f"[{time.monotonic() - self.t0:7.1f}s] "
        with self.lock:
            self.lines.append(stamp + text)
        if echo:
            print(stamp + text, flush=True)


def tail_modal_logs(app_name: str, sink: Path) -> subprocess.Popen | None:
    """Start `modal app logs <app>` in the background, writing to *sink*."""
    modal_cli = shutil.which("modal")
    if modal_cli is None:
        return None
    handle = sink.open("w", encoding="utf-8", errors="replace")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        return subprocess.Popen(
            [modal_cli, "app", "logs", app_name],
            stdout=handle, stderr=subprocess.STDOUT, env=env, cwd=REPO_ROOT,
        )
    except OSError:
        handle.close()
        return None


def main() -> int:
    """Run one recorded test session and write the redacted report."""
    env = load_dotenv(REPO_ROOT / ".env")
    secret_values = [
        env.get(k, "") for k in (
            "DATABASE_URL", "OMNIGENT_ACCOUNTS_COOKIE_SECRET", "OMNIGENT_ACCOUNTS_INIT_ADMIN_PASSWORD",
            "OMNIGENT_MACHINE_CLIENT_SECRET", "OMNIGENT_MACHINE_CLIENT_SECRET_HASH", "MODAL_TOKEN_ID",
            "MODAL_TOKEN_SECRET", "OMNIGENT_ANTHROPIC_API_KEY", "ARTEMIS_ACCESS_CODE",
        )
    ]
    settings = OmnigentSettings.from_env(env)
    client = OmnigentClient(settings)
    timeline = Timeline()
    timeline.add(f"Omnigent server: {settings.base_url}", echo=True)

    log_dir = Path(tempfile.mkdtemp(prefix="artemis-logs-"))
    tailers = {app: tail_modal_logs(app, log_dir / f"{app}.log") for app in LOG_APPS}
    timeline.add("Started Modal log capture for: " + ", ".join(a for a, p in tailers.items() if p), echo=True)
    time.sleep(3)

    session_id = None
    done = threading.Event()
    try:
        timeline.add(f"health: {client.health()}", echo=True)
        client.check_credentials()
        timeline.add("credentials accepted", echo=True)
        session_id = client.create_session(build_agent_bundle(AGENT_DIR), "Artemis diagnosis", "managed")
        timeline.add(f"session created: {session_id}", echo=True)

        def watch() -> None:
            try:
                for event in parse_sse_events(client.stream_lines(session_id, max_seconds=WATCH_SECONDS + 30)):
                    etype = event.get("type", "?")
                    if etype == "response.output_text.delta":
                        timeline.add(f"stream: text delta {event.get('delta', '')!r}")
                    elif etype not in ("session.heartbeat", "response.heartbeat"):
                        timeline.add("stream: " + json.dumps(event)[:600], echo=etype.startswith("session.sandbox") or etype in TERMINAL)
                    if etype in TERMINAL:
                        done.set()
                        return
            except Exception as exc:
                timeline.add(f"stream ended with error: {exc!r}", echo=True)
            timeline.add("stream closed")

        threading.Thread(target=watch, daemon=True).start()
        time.sleep(1.5)

        def post() -> None:
            try:
                ack = client.post_user_message(session_id, DEFAULT_MESSAGE)
                timeline.add(f"message post answered: {ack}", echo=True)
            except OmnigentAPIError as exc:
                timeline.add(f"message post error: {exc}", echo=True)

        threading.Thread(target=post, daemon=True).start()
        timeline.add("message posted (in background)", echo=True)

        deadline = time.monotonic() + WATCH_SECONDS
        last = None
        while time.monotonic() < deadline and not done.is_set():
            try:
                snap = client.diagnose(session_id)
            except Exception as exc:  # keep recording no matter what
                snap = {"error": repr(exc)}
            compact = json.dumps(snap, default=str)
            if compact != last:
                timeline.add("snapshot: " + compact, echo=True)
                last = compact
            done.wait(5)
        timeline.add("finished: " + ("turn ended" if done.is_set() else f"no result after {WATCH_SECONDS}s"), echo=True)
    except OmnigentAPIError as exc:
        timeline.add(f"API error: {exc}", echo=True)
    finally:
        if session_id:
            try:
                client.delete_session(session_id)
                timeline.add("session deleted", echo=True)
            except OmnigentAPIError as exc:
                timeline.add(f"delete failed: {exc}", echo=True)
        time.sleep(5)  # let trailing log lines arrive
        for proc in tailers.values():
            if proc is not None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
        client.close()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPO_ROOT / "runs" / f"diagnosis_{stamp}.txt"
    out.parent.mkdir(exist_ok=True)
    parts = ["ARTEMIS PHASE 1 DIAGNOSIS (secrets removed)", f"utc: {stamp}", "", "== TIMELINE =="]
    parts += timeline.lines
    for app in LOG_APPS:
        path = log_dir / f"{app}.log"
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else "(no log captured)"
        lines = text.splitlines()
        parts += ["", f"== MODAL LOGS: {app} ({len(lines)} lines, last 600 shown) =="]
        parts += lines[-600:]
    out.write_text(redact("\n".join(parts), secret_values), encoding="utf-8")
    print(f"\nSaved {out.relative_to(REPO_ROOT)}")
    print("Attach that file in the chat with Claude (drag it into the message box).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
