"""Run the Artemis lab on the vehicle-routing (CVRP) program.

Run from the artemis folder, on the cvrp-lab branch:

    python scripts/run_cvrp.py

With no arguments it does the next step that is needed, explaining each one:

1. Check   runs the frozen harness on your computer: fingerprints, the task,
           and one quick solve on a small practice instance
2. Launch  starts the six-agent lab in a Modal sandbox on the cvrp-lab branch
           and shows its progress here; the run continues in the cloud even if
           this window is closed

Individual steps, if you need them:

    python scripts/run_cvrp.py check
    python scripts/run_cvrp.py launch
    python scripts/run_cvrp.py watch SESSION_ID     # reconnect to a running lab
    python scripts/run_cvrp.py collect SESSION_ID   # save the report of a finished run
    python scripts/run_cvrp.py stop SESSION_ID      # save everything, then end the run
    python scripts/run_cvrp.py rebuild SESSION_ID   # rebuild the report from the local event log

Nothing secret is printed. Records are saved under runs/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import make_secrets as ms  # noqa: E402
from artemis_core import runs as lab_runs  # noqa: E402
from artemis_core.omnigent_api import (  # noqa: E402
    OmnigentAPIError,
    OmnigentClient,
    OmnigentConfigError,
    OmnigentSettings,
    build_agent_bundle,
    parse_sse_events,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CVRP = REPO_ROOT / "lab" / "cvrp"
SNAPSHOT = CVRP / "data" / "instances.json.gz"
MANIFEST = CVRP / "data" / "manifest.json"
AGENT_DIR = REPO_ROOT / "lab" / "agents" / "cvrp_lab"
RUNS = REPO_ROOT / "runs"
DEFAULT_REPO = "https://github.com/alessoh/artemis"
BRANCH = "cvrp-lab"
COMPLETE_MARKER = lab_runs.COMPLETE_MARKER
STREAM_SLICE_SECONDS = 600
SCRIPT = "python scripts/run_cvrp.py"

KICKOFF = f"""Run the Artemis routing program now (run 2), from setup to final report.

The question: within a short, fixed time limit on one CPU core (3 seconds per
100 customers), can this lab build a capacitated vehicle routing solver that
gets closer to the CVRPLIB X best-known solutions than PyVRP's default
solver, a state-of-the-art open-source library, on small and large problems
alike? This is run 2: it starts from run 1's kept solver, and the section
"Run 2: where run 1 left off" in lab/cvrp/program.md explains what changed.
Everything you need is in lab/cvrp. Read lab/cvrp/program.md first and follow
it exactly: setup, the experiment loop with the Skeptic's review, the single
final test, then the report.

Your very last message must contain, in this order: the full text of
runs/cvrp/report.md; the final ledger summary; the full source of
lab/cvrp/experiment.py in a fenced code block; and, on its own line at the
very end, {COMPLETE_MARKER}
"""


def say(step: str, text: str) -> None:
    """Print a step heading in plain words."""
    print(f"\n=== {step}: {text}")


def stop(message: str) -> int:
    """Print a failure explanation and return a non-zero exit code."""
    print(f"\nSTOPPED: {message}")
    print("Send Claude a screenshot of this window; no secrets are shown in it.")
    return 1


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot_ok() -> bool:
    """True when the snapshot and its manifest exist and agree."""
    if not (SNAPSHOT.exists() and MANIFEST.exists()):
        return False
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return manifest.get("sha256") == sha256_file(SNAPSHOT)


def run(command: list[str], env: dict[str, str] | None = None, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command from the repository root."""
    return subprocess.run(command, cwd=REPO_ROOT, env=env, text=True,
                          capture_output=capture, check=False, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- step 1
def cmd_check(_: argparse.Namespace | None = None) -> int:
    say("Check", "running the frozen harness on your computer")
    branch = run(["git", "branch", "--show-current"], capture=True).stdout.strip()
    if branch and branch != BRANCH:
        return stop(f"This folder is on the '{branch}' branch. Run: git checkout {BRANCH}")
    try:
        import numpy  # noqa: F401
        import pyvrp  # noqa: F401
    except ImportError:
        return stop("PyVRP or NumPy is missing. Run: pip install -r requirements-cvrp.txt")
    if not snapshot_ok():
        return stop("The routing data snapshot is missing or altered. Run: git pull")
    local_runs = RUNS / "cvrp_local_check"
    if local_runs.exists():
        shutil.rmtree(local_runs)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "ARTEMIS_RUNS_DIR": str(local_runs)}
    harness = str(CVRP / "harness.py")
    for args in (["fingerprint"], ["describe"],
                 ["probe", "--instances", "X-n101-k25", "--note", "local check"]):
        print(f"\n$ python lab/cvrp/harness.py {' '.join(args)}")
        result = run([sys.executable, harness, *args], env=env)
        if result.returncode != 0:
            return stop(f"The harness command '{args[0]}' failed.")
    print(f"\nLocal check passed. Its records are in {local_runs.relative_to(REPO_ROOT)}"
          " (not used by the lab).")
    return 0


# ---------------------------------------------------------------- step 2
def repo_url() -> str:
    """The public GitHub URL of this repository (from git, else the default)."""
    result = run(["git", "remote", "get-url", "origin"], capture=True)
    url = (result.stdout or "").strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.split(":", 1)[1]
    if url.endswith(".git"):
        url = url[:-4]
    return url if url.startswith("https://github.com/") else DEFAULT_REPO


def snapshot_on_github(url: str) -> bool:
    """True when GitHub's copy of the manifest on the branch matches the local one."""
    owner_repo = url.removeprefix("https://github.com/")
    raw = f"https://raw.githubusercontent.com/{owner_repo}/{BRANCH}/lab/cvrp/data/manifest.json"
    try:
        response = httpx.get(raw, timeout=30, follow_redirects=True)
        remote = response.json() if response.status_code == 200 else {}
    except (httpx.HTTPError, ValueError):
        return False
    local = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return remote.get("sha256") == local.get("sha256")


def make_client() -> OmnigentClient:
    """Build an Omnigent client from .env (the website's regular account)."""
    return OmnigentClient(OmnigentSettings.from_env(ms.read_env()))


item_text = lab_runs.item_text


def collect(client: OmnigentClient, session_id: str, out_dir: Path) -> Path | None:
    """Save every item of the session and of each sub-agent, plus the final report."""
    out_dir.mkdir(parents=True, exist_ok=True)
    items = client.list_all_items(session_id)
    (out_dir / "items.json").write_text(json.dumps({"data": items}, indent=2), encoding="utf-8")
    print(f"Saved {len(items)} items of the lead session.")
    try:
        children = client.list_child_sessions(session_id)
    except OmnigentAPIError as exc:
        print(f"Could not list the sub-agent sessions: {exc}")
        children = []
    if children:
        child_dir = out_dir / "subagents"
        child_dir.mkdir(exist_ok=True)
        (child_dir / "index.json").write_text(json.dumps(children, indent=2), encoding="utf-8")
        for child in children:
            child_id = str(child.get("id"))
            label = str(child.get("title") or child_id).replace(":", "_").replace("/", "_")
            try:
                child_items = client.list_all_items(child_id)
            except OmnigentAPIError as exc:
                print(f"  could not read {label}: {exc}")
                continue
            (child_dir / f"{label}_{child_id[:8]}.json").write_text(
                json.dumps({"data": child_items}, indent=2), encoding="utf-8")
        print(f"Saved the records of {len(children)} sub-agent sessions in {child_dir.name}/.")
    texts = [t for t in (item_text(i) for i in items) if t.strip()]
    if not texts:
        print("No assistant messages stored yet.")
        return None
    with_marker = [t for t in texts if COMPLETE_MARKER in t]
    final = with_marker[-1] if with_marker else texts[-1]
    if not with_marker:
        print("The lead has not posted its final report yet; saving its latest message.")
    report = out_dir / "report.md"
    report.write_text(final.replace(COMPLETE_MARKER, "").rstrip() + "\n", encoding="utf-8")
    return report


def describe_event(event: dict[str, Any]) -> str | None:
    """A one-line, secret-free description of a non-text stream event."""
    etype = str(event.get("type", ""))
    if etype == "session.sandbox_status":
        return f"[sandbox] {event.get('stage')}"
    item = event.get("item") if isinstance(event.get("item"), dict) else {}
    is_tool = ("tool" in etype or "function_call" in etype
               or item.get("type") in ("function_call", "tool_call", "custom_tool_call"))
    if is_tool:
        name = event.get("name") or item.get("name") or event.get("tool_name")
        if name and (etype.endswith("added") or etype.endswith("started") or etype.endswith("call")):
            return f"[tool] {name}"
        return None
    if etype in ("turn.completed", "response.completed"):
        return "[turn finished]"
    if etype in ("turn.failed", "response.failed", "response.error"):
        return f"[error] {json.dumps(event)[:300]}"
    return None


def watch(client: OmnigentClient, session_id: str, out_dir: Path) -> int:
    """Print the lab's live progress until it reports completion."""
    out_dir.mkdir(parents=True, exist_ok=True)
    log = open(out_dir / "events.jsonl", "a", encoding="utf-8")
    print(f"\nWatching session {session_id}. The lab keeps running in the cloud even if")
    print("you close this window; reconnect with:")
    print(f"  {SCRIPT} watch {session_id}\n")
    turn_text = ""
    failures = 0
    try:
        while True:
            try:
                for event in parse_sse_events(client.stream_lines(session_id, STREAM_SLICE_SECONDS)):
                    failures = 0
                    log.write(json.dumps(event) + "\n")
                    etype = event.get("type")
                    if etype == "response.output_text.delta":
                        delta = str(event.get("delta") or "")
                        turn_text += delta
                        print(delta, end="", flush=True)
                        continue
                    line = describe_event(event)
                    if line:
                        print(f"\n{line}", flush=True)
                    if etype in ("turn.completed", "response.completed"):
                        if COMPLETE_MARKER in turn_text:
                            print("\n\nThe lab reports the run is complete.")
                            return 0
                        turn_text = ""
            except OmnigentAPIError as exc:
                failures += 1
                print(f"\n[connection] {exc}; reconnecting ({failures})", flush=True)
                if failures >= 10:
                    return stop("Lost the connection to the lab ten times in a row.")
                time.sleep(min(30, 3 * failures))
            except httpx.ReadTimeout:
                continue  # a quiet spell (the lead waiting on its team); reconnect
            except httpx.HTTPError as exc:
                failures += 1
                print(f"\n[connection] {type(exc).__name__}; reconnecting ({failures})", flush=True)
                if failures >= 10:
                    return stop("Lost the connection to the lab ten times in a row.")
                time.sleep(min(30, 3 * failures))
    except KeyboardInterrupt:
        print("\n\nStopped watching. The lab is still running; reconnect with:")
        print(f"  {SCRIPT} watch {session_id}")
        return 0
    finally:
        log.close()


def cmd_launch(_: argparse.Namespace | None = None) -> int:
    say("Launch", "starting the six-agent routing lab in a Modal sandbox")
    if not snapshot_ok():
        return stop("The routing data snapshot is missing. Run: git pull")
    url = repo_url()
    if not snapshot_on_github(url):
        return stop(f"GitHub's {BRANCH} branch does not have this data snapshot. Run: git pull, "
                    "then try again.")
    try:
        client = make_client()
    except OmnigentConfigError as exc:
        return stop(f".env is incomplete for Omnigent: {exc}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    workspace = f"{url}#{BRANCH}"
    try:
        session_id = client.create_session(build_agent_bundle(AGENT_DIR),
                                           "Artemis routing lab", "managed", workspace=workspace)
        print(f"Session {session_id} created; workspace {workspace}")
        client.wait_until_ready(session_id, timeout_s=600,
                                on_stage=lambda s: print(f"  sandbox: {s}", flush=True))
        client.post_user_message(session_id, KICKOFF)
    except OmnigentAPIError as exc:
        return stop(f"Omnigent refused or failed to start the lab: {exc}")
    out_dir = RUNS / f"cvrp_{stamp}_{session_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "session.json").write_text(json.dumps(
        {"session_id": session_id, "workspace": workspace, "started_utc": stamp,
         "snapshot_sha256": json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]},
        indent=2), encoding="utf-8")
    print("Lab started. Its first steps install PyVRP and record the baselines.")
    code = watch(client, session_id, out_dir)
    if code == 0:
        report = collect(client, session_id, out_dir)
        if report:
            print(f"\nReport saved to {report.relative_to(REPO_ROOT)}")
    client.close()
    return code


def find_out_dir(session_id: str) -> Path:
    """The runs/ folder for a session (a new one if this computer has none)."""
    matches = sorted(RUNS.glob(f"cvrp_*_{session_id}"))
    if matches:
        return matches[-1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return RUNS / f"cvrp_{stamp}_{session_id}"


def cmd_watch(args: argparse.Namespace) -> int:
    client = make_client()
    out_dir = find_out_dir(args.session_id)
    code = watch(client, args.session_id, out_dir)
    if code == 0:
        report = collect(client, args.session_id, out_dir)
        if report:
            print(f"\nReport saved to {report.relative_to(REPO_ROOT)}")
    client.close()
    return code


def cmd_collect(args: argparse.Namespace) -> int:
    client = make_client()
    out_dir = find_out_dir(args.session_id)
    report = collect(client, args.session_id, out_dir)
    client.close()
    if report is None:
        return 1
    print(f"Saved {report.relative_to(REPO_ROOT)} and items.json in {out_dir.relative_to(REPO_ROOT)}")
    return 0


def rebuild_from_events(out_dir: Path) -> Path | None:
    """Rebuild transcript.md and report.md from the locally saved events.jsonl."""
    log = out_dir / "events.jsonl"
    if not log.exists():
        print(f"No events.jsonl in {out_dir.relative_to(REPO_ROOT)}; nothing to rebuild from.")
        return None
    turns: list[str] = []
    current = ""
    with open(log, encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = event.get("type")
            if etype == "response.output_text.delta":
                current += str(event.get("delta") or "")
            elif etype in ("turn.completed", "response.completed", "turn.failed", "response.failed"):
                if current.strip():
                    turns.append(current)
                current = ""
    if current.strip():
        turns.append(current)
    if not turns:
        print("events.jsonl holds no message text.")
        return None
    transcript = out_dir / "transcript.md"
    transcript.write_text("\n\n---\n\n".join(t.strip() for t in turns) + "\n", encoding="utf-8")
    finals = [t for t in turns if COMPLETE_MARKER in t]
    report = out_dir / "report.md"
    report.write_text((finals[-1] if finals else turns[-1]).replace(COMPLETE_MARKER, "").strip() + "\n",
                      encoding="utf-8")
    print(f"Rebuilt {len(turns)} messages into {transcript.relative_to(REPO_ROOT)}")
    print(f"Saved {'the final report' if finals else 'the latest message'} to {report.relative_to(REPO_ROOT)}")
    return report


def cmd_rebuild(args: argparse.Namespace) -> int:
    matches = sorted(RUNS.glob(f"cvrp_*_{args.session_id}"))
    if not matches:
        return stop(f"No runs folder for session {args.session_id} on this computer.")
    return 0 if rebuild_from_events(matches[-1]) else 1


def cmd_stop(args: argparse.Namespace) -> int:
    client = make_client()
    out_dir = find_out_dir(args.session_id)
    try:
        report = collect(client, args.session_id, out_dir)
    except OmnigentAPIError as exc:
        report = None
        print(f"Could not save the session's records: {exc}")
    if report is None and not getattr(args, "force", False):
        return stop("The records were not saved, so the session was left running. "
                    "Fix the problem first, or add --force to end it anyway.")
    client.delete_session(args.session_id)
    client.close()
    print(f"Session {args.session_id} ended and its sandbox stopped. Records are in "
          f"{out_dir.relative_to(REPO_ROOT)}")
    return 0


def cmd_auto(args: argparse.Namespace) -> int:
    """Check, then launch."""
    code = cmd_check()
    if code:
        return code
    return cmd_launch(args)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    for name, func in (("check", cmd_check), ("launch", cmd_launch)):
        sub.add_parser(name).set_defaults(func=func)
    for name, func in (("watch", cmd_watch), ("collect", cmd_collect), ("stop", cmd_stop),
                       ("rebuild", cmd_rebuild)):
        p = sub.add_parser(name)
        p.add_argument("session_id")
        if name == "stop":
            p.add_argument("--force", action="store_true", help="end the session even if saving failed")
        p.set_defaults(func=func)
    args = parser.parse_args()
    func = getattr(args, "func", cmd_auto)
    try:
        return func(args)
    except OmnigentConfigError as exc:
        return stop(f".env is incomplete for Omnigent: {exc}")
    except OmnigentAPIError as exc:
        return stop(f"Omnigent error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
