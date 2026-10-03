"""One command that brings the Artemis lab online and tests it.

Run from the artemis folder:

    python scripts/run_phase1.py

It does, in order, explaining each step as it goes:

1. Settings     makes sure .env is complete (asks only for anything missing)
2. Modal        saves the settings into your Modal account
3. Deploy       starts the Omnigent server on Modal; if Modal gives it a
                different web address than expected, it fixes the settings
                and deploys again by itself
4. Wake-up      waits until the server answers (about a minute the first time)
5. Test         runs the end-to-end smoke test and prints the result
6. Vercel       shows the four values to add to your Vercel project

Safe to run again at any time.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_secrets as ms  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https://[a-z0-9-]+\.modal\.run")
HEALTH_WAIT_SECONDS = 360


def say(step: str, text: str) -> None:
    """Print a step heading in plain words."""
    print(f"\n=== {step}: {text}")


def stop(message: str) -> int:
    """Print a failure explanation and return a non-zero exit code."""
    print(f"\nSTOPPED: {message}")
    print("Send Claude a screenshot of this window; no secrets are shown in it.")
    return 1


def push_settings(values: dict[str, str]) -> None:
    """Save both Modal secrets (exits with a clear message if Modal refuses)."""
    ms.run_modal_secret("artemis-omnigent-deploy", {k: values[k] for k in ms.DEPLOY_KEYS})
    ms.run_modal_secret("artemis-llm", {k: values[k] for k in ms.LLM_KEYS})


def deploy() -> str | None:
    """Run `modal deploy`, show its output live, and return the server URL.

    :returns: The ``*.modal.run`` URL Modal printed, or ``None`` on failure.
    """
    modal_cli = shutil.which("modal")
    if modal_cli is None:
        return None
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(
        [modal_cli, "deploy", "lab/modal_server.py"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    url = None
    assert proc.stdout is not None
    for line in proc.stdout:
        print("   " + line.rstrip())
        match = URL_RE.search(line)
        if match:
            url = match.group(0)
    if proc.wait() != 0:
        return None
    return url


def wait_for_health(url: str) -> bool:
    """Poll the server's /health endpoint until it answers or time runs out."""
    deadline = time.monotonic() + HEALTH_WAIT_SECONDS
    dots = 0
    while time.monotonic() < deadline:
        try:
            if httpx.get(f"{url}/health", timeout=10).status_code == 200:
                print(" ready.")
                return True
        except httpx.HTTPError:
            pass
        print("." if dots else "   waiting", end="", flush=True)
        dots += 1
        time.sleep(5)
    print()
    return False


def main() -> int:
    """Run every Phase 1 step in order."""
    try:
        sys.stdout.reconfigure(errors="replace")  # type: ignore[attr-defined]
    except AttributeError:
        pass
    os.chdir(REPO_ROOT)

    say("Step 1 of 6", "checking your settings")
    if ms.validate(ms.read_env()):
        print("   Some settings are missing; collecting them now.")
        if ms.cmd_init(type("Args", (), {"reenter": None})()) != 0:
            return stop("settings are still incomplete.")
    problems = ms.validate(ms.read_env())
    if problems:
        return stop("these settings need attention: " + "; ".join(problems))
    values = ms.read_env()
    print("   Settings complete.")
    print(f"   Database:      {ms.mask('DATABASE_URL', values['DATABASE_URL'])}")
    print(f"   Modal token:   {ms.mask('MODAL_TOKEN_ID', values['MODAL_TOKEN_ID'])}")
    print(f"   Anthropic key: {ms.describe_key(values['OMNIGENT_ANTHROPIC_API_KEY'])}")

    say("Step 2 of 6", "saving the settings into your Modal account")
    push_settings(values)

    say("Step 3 of 6", "starting the Omnigent server on Modal (a minute or two)")
    url = deploy()
    if not url:
        return stop("the Modal deploy did not finish. The lines above say why.")
    expected = values["OMNIGENT_ACCOUNTS_BASE_URL"].rstrip("/")
    if url != expected:
        print(f"   Modal chose the address {url}; updating settings and deploying again.")
        values["OMNIGENT_ACCOUNTS_BASE_URL"] = url
        values["OMNIGENT_URL"] = url
        ms.save_env(values)
        push_settings(values)
        if not deploy():
            return stop("the second Modal deploy did not finish. The lines above say why.")
    print(f"   Server address: {url}")

    say("Step 4 of 6", "waiting for the server to wake up (first start sets up the database)")
    if not wait_for_health(url):
        return stop(f"the server did not answer within {HEALTH_WAIT_SECONDS // 60} minutes. "
                    "Run  modal app logs artemis-omnigent  to see why.")

    say("Step 5 of 6", "testing the whole lab with one question (up to three minutes)")
    result = subprocess.run([sys.executable, "scripts/smoke_test.py"], cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        return stop("the lab test did not pass. The FAIL line above names the broken part.")

    say("Step 6 of 6", "last step, in your browser")
    print("   In Vercel, open the artemis project > Settings > Environment Variables,")
    print("   add the four lines below (name on the left, value on the right of =),")
    print("   then go to Deployments, open the top one's menu, and click Redeploy.\n")
    for key in ms.VERCEL_KEYS:
        print(f"   {key}={values[key]}")
    print("\nThe lab is online. Visit your Vercel site and click 'Run the check'.")
    print("Your access code for the site is the ARTEMIS_ACCESS_CODE value above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
