"""Phase 2: run the Artemis lab on the flagship solar-absorber question.

Run from the artemis folder:

    python scripts/run_phase2.py

With no arguments it does the next step that is needed, explaining each one:

1. Data     builds the frozen JARVIS data snapshot on Modal (once, a few
            minutes) and saves it in lab/solar/data/
2. Check    runs the frozen harness on your computer: fingerprints, pool
            sizes, and the random and Shockley-Queisser baselines
3. Share    puts the snapshot on GitHub, because the lab's sandbox starts
            from a fresh copy of the repository there
4. Launch   starts the six-agent lab in a Modal sandbox and shows its
            progress here; the run continues in the cloud even if this
            window is closed

Individual steps, if you need them:

    python scripts/run_phase2.py data
    python scripts/run_phase2.py check
    python scripts/run_phase2.py launch
    python scripts/run_phase2.py watch SESSION_ID     # reconnect to a running lab
    python scripts/run_phase2.py collect SESSION_ID   # save the report of a finished run
    python scripts/run_phase2.py stop SESSION_ID      # save everything, then end the run
    python scripts/run_phase2.py rebuild SESSION_ID   # rebuild the report from the local event log

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
from artemis_core.omnigent_api import (  # noqa: E402
    OmnigentAPIError,
    OmnigentClient,
    OmnigentConfigError,
    OmnigentSettings,
    build_agent_bundle,
    parse_sse_events,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SOLAR = REPO_ROOT / "lab" / "solar"
SNAPSHOT = SOLAR / "data" / "solar_snapshot.csv.gz"
MANIFEST = SOLAR / "data" / "snapshot.json"
AGENT_DIR = REPO_ROOT / "lab" / "agents" / "solar_lab"
RUNS = REPO_ROOT / "runs"
DEFAULT_REPO = "https://github.com/alessoh/artemis"
BRANCH = "main"
COMPLETE_MARKER = "ARTEMIS-RUN-COMPLETE"
STREAM_SLICE_SECONDS = 600
KICKOFF = f"""Run the Artemis solar program from start to finish.

Question: among earth-abundant, non-toxic inorganic crystals in NIST JARVIS-DFT,
which ones should a lab compute next to find excellent solar absorbers fastest,
and what does the best search strategy teach us about what makes a good absorber?

Follow lab/solar/program.md exactly: setup, the experiment loop with your team
until the experiment budget is used up or progress stalls, the single final
held-out test, the shortlist of never-assessed materials with Materials Project
and literature cross-checks, and the report by the Scribe. Do not ask me whether
to continue. When everything is done, make your last message the full report,
then the final ledger summary, then the complete source code of
lab/solar/experiment.py in a python code block, then the shortlist CSV in a
code block (the sandbox cannot push to GitHub, so this message is the only copy
that leaves it), then a last line that reads exactly:
{COMPLETE_MARKER}
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
def cmd_data(_: argparse.Namespace | None = None) -> int:
    say("Data", "building the JARVIS snapshot on Modal (a few minutes)")
    modal_cli = shutil.which("modal")
    if modal_cli is None:
        return stop("The Modal command is not installed. Run: pip install modal")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = run([modal_cli, "run", str(SOLAR / "prepare_data.py")], env=env)
    if result.returncode != 0 or not snapshot_ok():
        return stop("Building the data snapshot did not finish (see the messages above).")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"\nSnapshot ready: {manifest['rows']} materials, fingerprint {manifest['sha256'][:12]}")
    print("Checks: " + json.dumps(manifest.get("checks", {})))
    return 0


# ---------------------------------------------------------------- step 2
def cmd_check(_: argparse.Namespace | None = None) -> int:
    say("Check", "running the frozen harness on your computer")
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
    except ImportError:
        return stop("pandas or numpy is missing. Run: pip install -r requirements-solar.txt")
    if not snapshot_ok():
        return stop("The data snapshot is missing or altered. Run: python scripts/run_phase2.py data")
    local_runs = RUNS / "solar_local_check"
    if local_runs.exists():
        shutil.rmtree(local_runs)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "ARTEMIS_RUNS_DIR": str(local_runs)}
    harness = str(SOLAR / "harness.py")
    for args in (["fingerprint"], ["describe"], ["baselines"],
                 ["evaluate", "--note", "starting experiment.py"]):
        print(f"\n$ python lab/solar/harness.py {' '.join(args)}")
        result = run([sys.executable, harness, *args], env=env)
        if result.returncode != 0:
            return stop(f"The harness command '{args[0]}' failed.")
    print(f"\nLocal check passed. Its ledger is in {local_runs.relative_to(REPO_ROOT)}"
          " (not used by the lab).")
    return 0


# ---------------------------------------------------------------- step 3
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
    """True when GitHub's copy of the manifest matches the local snapshot."""
    owner_repo = url.removeprefix("https://github.com/")
    raw = f"https://raw.githubusercontent.com/{owner_repo}/{BRANCH}/lab/solar/data/snapshot.json"
    try:
        response = httpx.get(raw, timeout=30, follow_redirects=True)
    except httpx.HTTPError:
        return False
    if response.status_code != 200:
        return False
    try:
        remote = response.json()
    except ValueError:
        return False
    local = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return remote.get("sha256") == local.get("sha256")


def cmd_share(_: argparse.Namespace | None = None) -> int:
    say("Share", "putting the snapshot on GitHub so the lab's sandbox can use it")
    url = repo_url()
    if snapshot_on_github(url):
        print("GitHub already has this snapshot.")
        return 0
    steps = [
        ["git", "pull", "--ff-only"],
        ["git", "add", "lab/solar/data/solar_snapshot.csv.gz", "lab/solar/data/snapshot.json"],
        ["git", "commit", "-m", "Add the frozen JARVIS solar data snapshot"],
        ["git", "push"],
    ]
    for command in steps:
        print("$ " + " ".join(command))
        result = run(command)
        if result.returncode != 0 and command[1] != "commit":
            print("\nGit could not upload the snapshot from this computer. That is fine:")
            print("attach these two files to your chat with Claude, and Claude will add them:")
            print(f"  {SNAPSHOT}")
            print(f"  {MANIFEST}")
            return 1
    for _ in range(12):
        if snapshot_on_github(url):
            print("Snapshot is on GitHub.")
            return 0
        time.sleep(5)
    print("Pushed, but GitHub does not show the snapshot yet; wait a minute and run this again.")
    return 1


# ---------------------------------------------------------------- step 4
def make_client() -> OmnigentClient:
    """Build an Omnigent client from .env (the website's regular account)."""
    values = ms.read_env()
    settings = OmnigentSettings.from_env(values)
    return OmnigentClient(settings)


def item_text(item: Any) -> str:
    """Best-effort extraction of assistant text from a stored session item."""
    if not isinstance(item, dict):
        return ""
    data = item.get("data") if isinstance(item.get("data"), dict) else item
    role = data.get("role") or item.get("role")
    if role not in (None, "assistant"):
        return ""
    parts = data.get("content")
    if isinstance(parts, str):
        return parts
    texts = []
    for part in parts or []:
        if isinstance(part, dict) and part.get("type") in ("output_text", "text"):
            texts.append(str(part.get("text") or ""))
    return "".join(texts)


def collect(client: OmnigentClient, session_id: str, out_dir: Path) -> Path | None:
    """Save every item of the session and of each sub-agent, plus the final report.

    The report is the lead's last assistant message (the run's kickoff asks
    for the full report there).
    """
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
    print(f"  python scripts/run_phase2.py watch {session_id}\n")
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
                # A quiet spell (the lead waiting on its team); just reconnect.
                continue
            except httpx.HTTPError as exc:
                failures += 1
                print(f"\n[connection] {type(exc).__name__}; reconnecting ({failures})", flush=True)
                if failures >= 10:
                    return stop("Lost the connection to the lab ten times in a row.")
                time.sleep(min(30, 3 * failures))
    except KeyboardInterrupt:
        print("\n\nStopped watching. The lab is still running; reconnect with:")
        print(f"  python scripts/run_phase2.py watch {session_id}")
        return 0
    finally:
        log.close()


def cmd_launch(args: argparse.Namespace | None = None) -> int:
    say("Launch", "starting the six-agent lab in a Modal sandbox")
    if not snapshot_ok():
        return stop("The data snapshot is missing. Run: python scripts/run_phase2.py data")
    url = repo_url()
    if not snapshot_on_github(url):
        return stop("GitHub does not have this snapshot yet. Run: python scripts/run_phase2.py share")
    try:
        client = make_client()
    except OmnigentConfigError as exc:
        return stop(f".env is incomplete for Omnigent: {exc}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    workspace = f"{url}#{BRANCH}"
    try:
        session_id = client.create_session(build_agent_bundle(AGENT_DIR),
                                           "Artemis solar lab", "managed", workspace=workspace)
        print(f"Session {session_id} created; workspace {workspace}")
        client.wait_until_ready(session_id, timeout_s=600,
                                on_stage=lambda s: print(f"  sandbox: {s}", flush=True))
        client.post_user_message(session_id, KICKOFF)
    except OmnigentAPIError as exc:
        return stop(f"Omnigent refused or failed to start the lab: {exc}")
    out_dir = RUNS / f"phase2_{stamp}_{session_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "session.json").write_text(json.dumps(
        {"session_id": session_id, "workspace": workspace, "started_utc": stamp,
         "snapshot_sha256": json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]},
        indent=2), encoding="utf-8")
    print("Lab started. Its first steps install packages and record the baselines.")
    code = watch(client, session_id, out_dir)
    if code == 0:
        report = collect(client, session_id, out_dir)
        if report:
            print(f"\nReport saved to {report.relative_to(REPO_ROOT)}")
    client.close()
    return code


def find_out_dir(session_id: str) -> Path:
    """The runs/ folder for a session (a new one if this computer has none)."""
    matches = sorted(RUNS.glob(f"phase2_*_{session_id}"))
    if matches:
        return matches[-1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return RUNS / f"phase2_{stamp}_{session_id}"


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
    """Rebuild transcript.md and report.md from the locally saved events.jsonl.

    The watcher records every streamed event, so the lead's messages survive
    even after Omnigent deletes the session. Text is grouped by turn.
    """
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
    """Rebuild the report from the local event log (works after a session is deleted)."""
    matches = sorted(RUNS.glob(f"phase2_*_{args.session_id}"))
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
    """Do whichever steps are still needed, in order."""
    if not snapshot_ok():
        code = cmd_data()
        if code:
            return code
    code = cmd_check()
    if code:
        return code
    code = cmd_share()
    if code:
        return code
    return cmd_launch(args)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    for name, func in (("data", cmd_data), ("check", cmd_check), ("share", cmd_share),
                       ("launch", cmd_launch)):
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
