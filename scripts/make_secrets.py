"""Create and distribute the secrets Artemis needs.

Run everything from the repository root on your own computer, so secret
values are generated locally and never pass through chat, email, or git.

    python scripts/make_secrets.py init     # generates secrets, collects your 2 values
    python scripts/make_secrets.py check    # validate .env without printing secrets
    python scripts/make_secrets.py modal    # push the two Modal secrets
    python scripts/make_secrets.py vercel   # show what to paste into Vercel
    python scripts/make_secrets.py materials-project   # optional: add the Materials Project key

What each subcommand does:

``init``
    Writes ``.env`` (git-ignored). Generates the Omnigent cookie secret, the
    first admin login, the machine client secret and its server-side HMAC
    digest, and a website access code. Reads your Modal token from the file
    ``modal setup`` already saved (``~/.modal.toml``). Then it collects the
    two values only you can supply, the Neon database address and your
    Anthropic key, straight from your clipboard: you copy each one in the
    browser and press Enter here. Nothing secret is shown on screen. Values
    are saved after each step, existing good values are never overwritten,
    and ``init`` is safe to re-run at any time.

``check``
    Confirms every required value is present and well formed, and that the
    machine client digest matches the cookie secret.

``modal``
    Runs ``modal secret create --force`` for ``artemis-omnigent-deploy``
    (read by the Omnigent server) and ``artemis-llm`` (injected only into
    agent sandboxes). Values are passed as process arguments to the Modal
    CLI on your machine and are not echoed.

``vercel``
    Prints the four variables to add under Vercel, Project Settings,
    Environment Variables. Two of them are secrets; copy them straight
    from your terminal into the Vercel dashboard.

``materials-project``
    Optional (Phase 2). Collects your Materials Project API key from the
    clipboard, saves it to ``.env`` and to the ``artemis-llm`` Modal secret,
    so the lab's Scout can cross-check candidate materials.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import os
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
PLACEHOLDER = "FILL_ME_IN"

# Default public URL of the Omnigent server on Modal. Modal web endpoints
# follow https://<workspace>--<app>-<function>.modal.run; the workspace is
# "alessoh", the app is "artemis-omnigent" and the function is "server".
DEFAULT_OMNIGENT_URL = "https://alessoh--artemis-omnigent-server.modal.run"
MACHINE_CLIENT_ID = "artemis-relay"
MACHINE_SUB = "artemis-relay"

# Values the user supplies, with how to find them. The Modal pair is normally
# read from ~/.modal.toml and is only asked for if that file is missing.
USER_KEYS = ["DATABASE_URL", "MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "OMNIGENT_ANTHROPIC_API_KEY"]
PROMPTS: dict[str, tuple[str, list[str], str]] = {
    "DATABASE_URL": (
        "Neon database address",
        [
            "In Vercel, open Storage, then your Neon database.",
            "Click 'Show secret', then copy the DATABASE_URL_UNPOOLED value.",
            "Clicking 'Copy Snippet' also works; the right line is picked out for you.",
        ],
        "a postgresql:// address (if you see stars, click 'Show secret' first)",
    ),
    "MODAL_TOKEN_ID": (
        "Modal token ID",
        ["At modal.com, open Settings, then API Tokens. The ID starts with ak-."],
        "a Modal token ID starting with ak-",
    ),
    "MODAL_TOKEN_SECRET": (
        "Modal token secret",
        ["Shown next to the token ID when you create a token. It starts with as-."],
        "a Modal token secret starting with as-",
    ),
    "OMNIGENT_ANTHROPIC_API_KEY": (
        "Anthropic API key",
        ["Copy your key from console.anthropic.com. It starts with sk-ant-."],
        "an Anthropic key starting with sk-ant-",
    ),
    "MP_API_KEY": (
        "Materials Project API key",
        [
            "Sign in at next-gen.materialsproject.org, then open your Dashboard",
            "(or go to next-gen.materialsproject.org/api) and copy the API key shown there.",
        ],
        "a Materials Project API key (a long run of letters and digits)",
    ),
}
# What a valid value looks like, used to pick it out of whatever was copied.
PATTERNS = {
    "DATABASE_URL": re.compile(r"postgres(?:ql)?(?:\+psycopg)?://[^\s'\"`]+"),
    "MODAL_TOKEN_ID": re.compile(r"\bak-[A-Za-z0-9]+"),
    "MODAL_TOKEN_SECRET": re.compile(r"\bas-[A-Za-z0-9]+"),
    "OMNIGENT_ANTHROPIC_API_KEY": re.compile(r"sk-ant-[A-Za-z0-9_\-]+"),
    "MP_API_KEY": re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9]{16,64}(?![A-Za-z0-9])"),
}
# When a whole .env snippet is copied, prefer these lines, in this order.
DATABASE_LINE_PREFERENCE = ["DATABASE_URL_UNPOOLED", "POSTGRES_URL_NON_POOLING", "DATABASE_URL", "POSTGRES_URL"]

# Values the server's Modal secret needs, in order.
DEPLOY_KEYS = [
    "DATABASE_URL",
    "OMNIGENT_ACCOUNTS_COOKIE_SECRET",
    "OMNIGENT_ACCOUNTS_BASE_URL",
    "OMNIGENT_ACCOUNTS_INIT_ADMIN_USERNAME",
    "OMNIGENT_ACCOUNTS_INIT_ADMIN_PASSWORD",
    "OMNIGENT_MACHINE_CLIENT_ID",
    "OMNIGENT_MACHINE_CLIENT_SECRET_HASH",
    "OMNIGENT_MACHINE_SUB",
    "MODAL_TOKEN_ID",
    "MODAL_TOKEN_SECRET",
]
# Values injected into agent sandboxes only. MP_API_KEY is optional: without it
# the lab still runs, but the Materials Project cross-check reports it is unavailable.
LLM_KEYS = ["OMNIGENT_ANTHROPIC_API_KEY", "MP_API_KEY"]
OPTIONAL_KEYS = {"MP_API_KEY"}
# Values the Vercel relay needs. The website logs in to Omnigent as a regular,
# non-admin account, because Omnigent only launches agents in managed
# sandboxes for sessions owned by a real account.
VERCEL_KEYS = [
    "OMNIGENT_URL",
    "OMNIGENT_USERNAME",
    "OMNIGENT_PASSWORD",
    "ARTEMIS_ACCESS_CODE",
]
VERCEL_SECRET_KEYS = {"OMNIGENT_PASSWORD", "ARTEMIS_ACCESS_CODE"}
WEB_ACCOUNT_USERNAME = "artemis-web"
# Kept locally only: the raw machine client secret (server stores its digest).
LOCAL_ONLY_KEYS = ["OMNIGENT_MACHINE_CLIENT_SECRET"]
ALL_KEYS = sorted(set(DEPLOY_KEYS + LLM_KEYS + VERCEL_KEYS + LOCAL_ONLY_KEYS))

ENV_TEMPLATE = """\
# Artemis secrets. This file is git-ignored. Never commit it or paste it into chat.
# Generated by scripts/make_secrets.py init. Any value still reading FILL_ME_IN is missing.

# ---- Omnigent server (Modal secret: artemis-omnigent-deploy) ----
# Postgres address from Vercel > Storage > Neon (DATABASE_URL_UNPOOLED).
DATABASE_URL={DATABASE_URL}
# 32 random bytes as hex; signs Omnigent login cookies and machine tokens.
OMNIGENT_ACCOUNTS_COOKIE_SECRET={OMNIGENT_ACCOUNTS_COOKIE_SECRET}
# The Omnigent server's public URL on Modal (printed by `modal deploy`).
OMNIGENT_ACCOUNTS_BASE_URL={OMNIGENT_ACCOUNTS_BASE_URL}
# Login for the Omnigent web UI admin account.
OMNIGENT_ACCOUNTS_INIT_ADMIN_USERNAME={OMNIGENT_ACCOUNTS_INIT_ADMIN_USERNAME}
OMNIGENT_ACCOUNTS_INIT_ADMIN_PASSWORD={OMNIGENT_ACCOUNTS_INIT_ADMIN_PASSWORD}
# Machine client used by the Vercel relay (OAuth client-credentials grant).
OMNIGENT_MACHINE_CLIENT_ID={OMNIGENT_MACHINE_CLIENT_ID}
OMNIGENT_MACHINE_CLIENT_SECRET_HASH={OMNIGENT_MACHINE_CLIENT_SECRET_HASH}
OMNIGENT_MACHINE_SUB={OMNIGENT_MACHINE_SUB}
# Modal API token so the server can launch agent sandboxes
# (read from ~/.modal.toml, which `modal setup` created).
MODAL_TOKEN_ID={MODAL_TOKEN_ID}
MODAL_TOKEN_SECRET={MODAL_TOKEN_SECRET}

# ---- Agent sandboxes (Modal secret: artemis-llm) ----
# Your Anthropic API key. Only the sandboxes receive it; the server never does.
OMNIGENT_ANTHROPIC_API_KEY={OMNIGENT_ANTHROPIC_API_KEY}
# Optional: Materials Project API key for cross-checking candidate materials.
# Add it with: python scripts/make_secrets.py materials-project
MP_API_KEY={MP_API_KEY}

# ---- Vercel relay (Vercel project environment variables) ----
OMNIGENT_URL={OMNIGENT_URL}
# The regular Omnigent account the website logs in as (created automatically).
OMNIGENT_USERNAME={OMNIGENT_USERNAME}
OMNIGENT_PASSWORD={OMNIGENT_PASSWORD}
# Code a visitor must enter before the website will start a lab session.
ARTEMIS_ACCESS_CODE={ARTEMIS_ACCESS_CODE}

# ---- Local only ----
# Raw machine client secret; the server stores only its HMAC digest above.
OMNIGENT_MACHINE_CLIENT_SECRET={OMNIGENT_MACHINE_CLIENT_SECRET}
"""


# ── .env file helpers ───────────────────────────────────────────────


def read_env(path: Path = ENV_PATH) -> dict[str, str]:
    """Parse a simple KEY=VALUE .env file, ignoring comments and blanks.

    :param path: File to read.
    :returns: Mapping of keys to values (empty if the file is absent).
    """
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def save_env(values: dict[str, str], path: Path = ENV_PATH) -> None:
    """Write all values to .env using the commented template.

    :param values: Mapping containing every key in :data:`ALL_KEYS`.
    :param path: Destination file.
    """
    path.write_text(ENV_TEMPLATE.format(**values), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def client_secret_digest(client_secret: str, cookie_secret_hex: str) -> str:
    """Compute the digest Omnigent stores for the machine client secret.

    Matches ``omnigent.server.device_grant_store.hash_secret``: HMAC-SHA256
    keyed by the cookie secret bytes, hex encoded.

    :param client_secret: The raw client secret.
    :param cookie_secret_hex: ``OMNIGENT_ACCOUNTS_COOKIE_SECRET`` as hex.
    :returns: 64-character hex digest.
    """
    key = bytes.fromhex(cookie_secret_hex)
    return hmac.new(key, client_secret.encode("utf-8"), hashlib.sha256).hexdigest()


def is_filled(value: str | None) -> bool:
    """Return True when a value is present and not the placeholder."""
    return bool(value) and value != PLACEHOLDER


# ── recognising, extracting and masking user-supplied values ────────


def looks_valid(key: str, value: str | None) -> bool:
    """Return True when a user-supplied value has the expected shape."""
    if not is_filled(value):
        return False
    if key in ("MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"):
        return not re.search(r"\s", value or "")
    return bool(PATTERNS[key].fullmatch(value or ""))


def _unquote(text: str) -> str:
    """Strip whitespace and one layer of matching quotes."""
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"`":
        text = text[1:-1].strip()
    return text


def extract_value(key: str, copied: str) -> str:
    """Pick the wanted value out of whatever text was copied.

    Accepts the bare value, a ``NAME=value`` line, a quoted value, a ``psql``
    command, or a whole multi-line .env snippet.

    :param key: Which value is wanted.
    :param copied: Raw clipboard or typed text.
    :returns: The extracted value, or ``""`` if none was found.
    """
    text = (copied or "").replace("\r", "")
    if not text.strip():
        return ""
    if key == "DATABASE_URL":
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for wanted in DATABASE_LINE_PREFERENCE:
            for line in lines:
                if line.startswith(wanted + "="):
                    candidate = _unquote(line.split("=", 1)[1])
                    match = PATTERNS[key].search(candidate)
                    if match:
                        return match.group(0)
    match = PATTERNS[key].search(text)
    if match:
        return match.group(0)
    if key in ("MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"):
        single = _unquote(text)
        if single and not re.search(r"\s", single):
            return single
    return ""


def describe_key(value: str) -> str:
    """Show the start and last four characters of a key, as consoles do."""
    return f"{value[:10]}...{value[-4:]}" if len(value) > 18 else mask("OMNIGENT_ANTHROPIC_API_KEY", value)


def mask(key: str, value: str) -> str:
    """Describe a secret without revealing it, e.g. for a confirmation line."""
    if key == "DATABASE_URL":
        parts = urlsplit(value)
        host = parts.hostname or "unknown host"
        return f"{parts.scheme}://(hidden)@{host}{parts.path}"
    prefix = {"MODAL_TOKEN_ID": "ak-", "MODAL_TOKEN_SECRET": "as-",
              "OMNIGENT_ANTHROPIC_API_KEY": "sk-ant-"}.get(key, "")
    shown = prefix if prefix and value.startswith(prefix) else value[:2]
    return f"{shown}... ({len(value)} characters)"


# ── automatic sources ───────────────────────────────────────────────


def modal_token_from_environment() -> tuple[str, str] | None:
    """Return a Modal token pair from MODAL_TOKEN_ID / MODAL_TOKEN_SECRET."""
    token_id = os.environ.get("MODAL_TOKEN_ID", "").strip()
    token_secret = os.environ.get("MODAL_TOKEN_SECRET", "").strip()
    if looks_valid("MODAL_TOKEN_ID", token_id) and looks_valid("MODAL_TOKEN_SECRET", token_secret):
        return token_id, token_secret
    return None


def modal_token_from_cli_config() -> tuple[str, str] | None:
    """Return the Modal token pair that ``modal setup`` saved, if any.

    Reads ``~/.modal.toml`` (or ``MODAL_CONFIG_PATH``) and picks the profile
    named by ``MODAL_PROFILE``, else the active profile, else the only one.

    :returns: ``(token_id, token_secret)`` or ``None``.
    """
    path = Path(os.environ.get("MODAL_CONFIG_PATH") or (Path.home() / ".modal.toml"))
    if not path.is_file():
        return None
    try:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:  # unreadable or Python older than 3.11
        return None
    profiles = {name: section for name, section in data.items() if isinstance(section, dict)}
    chosen = profiles.get(os.environ.get("MODAL_PROFILE", ""))
    if chosen is None:
        active = [section for section in profiles.values() if section.get("active")]
        if active:
            chosen = active[0]
        elif len(profiles) == 1:
            chosen = next(iter(profiles.values()))
    if not chosen:
        return None
    token_id = str(chosen.get("token_id", "")).strip()
    token_secret = str(chosen.get("token_secret", "")).strip()
    if looks_valid("MODAL_TOKEN_ID", token_id) and looks_valid("MODAL_TOKEN_SECRET", token_secret):
        return token_id, token_secret
    return None


def read_clipboard() -> str:
    """Return the current clipboard text, or ``""`` if it cannot be read.

    Uses tkinter (bundled with Python and conda), then falls back to the
    platform's own clipboard command.
    """
    try:
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        try:
            return root.clipboard_get()
        finally:
            root.destroy()
    except Exception:
        pass
    if sys.platform == "win32":
        commands = [["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"]]
    elif sys.platform == "darwin":
        commands = [["pbpaste"]]
    else:
        commands = [["wl-paste", "-n"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "-b", "-o"]]
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0 and result.stdout:
            return result.stdout
    return ""


# ── interactive collection ──────────────────────────────────────────


def ask_value(key: str) -> str:
    """Collect one value: copy it in the browser, then press Enter here.

    Anything typed or pasted at the prompt is hidden and used directly; an
    empty Enter reads the clipboard instead. Type ``s`` to skip.

    :param key: Which value to collect.
    :returns: The value, or ``""`` when skipped.
    """
    title, how, description = PROMPTS[key]
    print(f"\n{title}")
    for line in how:
        print(f"  {line}")
    while True:
        try:
            typed = getpass.getpass("  Copy it, then press Enter here (or type s to skip): ").strip()
        except EOFError:
            return ""
        if typed.lower() == "s":
            print("  Skipped. Run this command again later to add it.")
            return ""
        source = typed or read_clipboard()
        if not source.strip():
            print("  Your clipboard looks empty. Copy the value in your browser, then press Enter again.")
            continue
        value = extract_value(key, source)
        if value:
            print(f"  OK, received {mask(key, value)}")
            return value
        print(f"  That doesn't look like {description}.")
        print(f"  What I received has {len(source.strip())} characters. Copy it again, then press Enter.")


REENTER_GROUPS = {
    "database": ["DATABASE_URL"],
    "anthropic": ["OMNIGENT_ANTHROPIC_API_KEY"],
    "modal": ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"],
    "materials": ["MP_API_KEY"],
}


def cmd_init(args: argparse.Namespace) -> int:
    """Create or complete .env, generating secrets and collecting the rest."""
    current = read_env()
    values = {key: current.get(key, "") for key in ALL_KEYS}
    reenter = set(getattr(args, "reenter", None) or [])
    for group in reenter:
        for key in REENTER_GROUPS[group]:
            values[key] = ""

    def keep_or(key: str, generated: str) -> None:
        if not is_filled(values.get(key)):
            values[key] = generated

    keep_or("OMNIGENT_ACCOUNTS_COOKIE_SECRET", secrets.token_hex(32))
    keep_or("OMNIGENT_ACCOUNTS_INIT_ADMIN_USERNAME", "admin")
    keep_or("OMNIGENT_ACCOUNTS_INIT_ADMIN_PASSWORD", secrets.token_urlsafe(18))
    keep_or("OMNIGENT_MACHINE_CLIENT_ID", MACHINE_CLIENT_ID)
    keep_or("OMNIGENT_MACHINE_SUB", MACHINE_SUB)
    keep_or("OMNIGENT_MACHINE_CLIENT_SECRET", secrets.token_urlsafe(32))
    keep_or("ARTEMIS_ACCESS_CODE", secrets.token_urlsafe(9))
    keep_or("OMNIGENT_USERNAME", WEB_ACCOUNT_USERNAME)
    keep_or("OMNIGENT_PASSWORD", secrets.token_urlsafe(24))
    keep_or("OMNIGENT_ACCOUNTS_BASE_URL", DEFAULT_OMNIGENT_URL)
    keep_or("OMNIGENT_URL", values["OMNIGENT_ACCOUNTS_BASE_URL"])
    # The digest always follows the current cookie secret and client secret.
    values["OMNIGENT_MACHINE_CLIENT_SECRET_HASH"] = client_secret_digest(
        values["OMNIGENT_MACHINE_CLIENT_SECRET"], values["OMNIGENT_ACCOUNTS_COOKIE_SECRET"]
    )
    # A user value that is missing or malformed (say, a mis-paste) is asked for again.
    for key in USER_KEYS:
        if not looks_valid(key, values.get(key)):
            values[key] = PLACEHOLDER
    save_env(values)
    print("Generated the Omnigent and website secrets.")

    # Modal token: reuse the one `modal setup` saved on this computer.
    if not (looks_valid("MODAL_TOKEN_ID", values["MODAL_TOKEN_ID"])
            and looks_valid("MODAL_TOKEN_SECRET", values["MODAL_TOKEN_SECRET"])):
        found = None if "modal" in reenter else (modal_token_from_environment() or modal_token_from_cli_config())
        if found:
            values["MODAL_TOKEN_ID"], values["MODAL_TOKEN_SECRET"] = found
            save_env(values)
            print(f"Modal token: found the one `modal setup` saved ({mask('MODAL_TOKEN_ID', found[0])}).")
    else:
        print("Modal token: already saved.")

    # Anthropic key: reuse one already set in this terminal's environment,
    # unless the user asked to enter it fresh.
    if "anthropic" not in reenter and not looks_valid("OMNIGENT_ANTHROPIC_API_KEY", values["OMNIGENT_ANTHROPIC_API_KEY"]):
        env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if looks_valid("OMNIGENT_ANTHROPIC_API_KEY", env_key):
            values["OMNIGENT_ANTHROPIC_API_KEY"] = env_key
            save_env(values)
            print(f"Anthropic key: used ANTHROPIC_API_KEY already set on this computer ({describe_key(env_key)}).")
            print("  If that is not the key you want, run:  python scripts/make_secrets.py init --reenter anthropic")

    missing = [key for key in USER_KEYS if values[key] == PLACEHOLDER]
    if missing and sys.stdin.isatty():
        print(f"\n{len(missing)} value(s) to go. For each one: copy it in your browser, then")
        print("come back to this window and press Enter. Nothing secret is shown here.")
        print("(Do not press Ctrl+C in this window; that stops the script.)")
        try:
            for key in missing:
                answer = ask_value(key)
                if answer:
                    values[key] = answer
                    save_env(values)
        except KeyboardInterrupt:
            print("\n\nStopped. Everything entered so far is saved; run the same command to continue.")
            return 1

    still_missing = [key for key in USER_KEYS if values[key] == PLACEHOLDER]
    print(f"\nSaved {ENV_PATH}")
    if still_missing:
        print("Still missing: " + ", ".join(still_missing))
        print("Run  python scripts/make_secrets.py init  again to add them.")
        return 1
    print("All values present. Next: python scripts/make_secrets.py check")
    return 0


# ── validation and distribution ─────────────────────────────────────


def validate(values: dict[str, str]) -> list[str]:
    """Return a list of human-readable problems with the .env values."""
    problems: list[str] = []
    for key in ALL_KEYS:
        if key not in OPTIONAL_KEYS and not is_filled(values.get(key)):
            problems.append(f"{key} is missing (run: python scripts/make_secrets.py init)")
    if problems:
        return problems
    if not re.fullmatch(r"[0-9a-f]{64,}", values["OMNIGENT_ACCOUNTS_COOKIE_SECRET"]):
        problems.append("OMNIGENT_ACCOUNTS_COOKIE_SECRET must be at least 64 lowercase hex characters")
    else:
        expected = client_secret_digest(
            values["OMNIGENT_MACHINE_CLIENT_SECRET"], values["OMNIGENT_ACCOUNTS_COOKIE_SECRET"]
        )
        if not hmac.compare_digest(expected, values["OMNIGENT_MACHINE_CLIENT_SECRET_HASH"]):
            problems.append("OMNIGENT_MACHINE_CLIENT_SECRET_HASH does not match; re-run init")
    for key in USER_KEYS:
        if not looks_valid(key, values[key]):
            problems.append(f"{key} does not look right; re-run init to enter it again")
    if is_filled(values.get("MP_API_KEY")) and not looks_valid("MP_API_KEY", values["MP_API_KEY"]):
        problems.append("MP_API_KEY does not look right; run: python scripts/make_secrets.py materials-project")
    for key in ("OMNIGENT_ACCOUNTS_BASE_URL", "OMNIGENT_URL"):
        if not values[key].startswith("https://"):
            problems.append(f"{key} must start with https://")
    if values["OMNIGENT_URL"].rstrip("/") != values["OMNIGENT_ACCOUNTS_BASE_URL"].rstrip("/"):
        problems.append("OMNIGENT_URL and OMNIGENT_ACCOUNTS_BASE_URL should be the same URL")
    reserved = {"admin", "local", "public", values["OMNIGENT_ACCOUNTS_INIT_ADMIN_USERNAME"]}
    if values["OMNIGENT_MACHINE_SUB"] in reserved:
        problems.append("OMNIGENT_MACHINE_SUB must be a distinct, non-admin name")
    if values["OMNIGENT_USERNAME"] in reserved | {values["OMNIGENT_MACHINE_SUB"]}:
        problems.append("OMNIGENT_USERNAME must differ from the admin and machine names")
    if len(values["OMNIGENT_PASSWORD"]) < 12:
        problems.append("OMNIGENT_PASSWORD must be at least 12 characters; re-run init")
    return problems


def cmd_check(_: argparse.Namespace) -> int:
    """Validate .env and report problems without printing any secret."""
    values = read_env()
    if not values:
        print("No .env found. Run: python scripts/make_secrets.py init")
        return 1
    problems = validate(values)
    if problems:
        print("Problems found in .env:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(".env looks complete and consistent.")
    print(f"  Database: {mask('DATABASE_URL', values['DATABASE_URL'])}")
    print(f"  Modal token: {mask('MODAL_TOKEN_ID', values['MODAL_TOKEN_ID'])}")
    print(f"  Anthropic key: {describe_key(values['OMNIGENT_ANTHROPIC_API_KEY'])}")
    if is_filled(values.get("MP_API_KEY")):
        print(f"  Materials Project key: {mask('MP_API_KEY', values['MP_API_KEY'])}")
    else:
        print("  Materials Project key: not added (optional; python scripts/make_secrets.py materials-project)")
    print("Next: python scripts/make_secrets.py modal")
    return 0


def run_modal_secret(name: str, pairs: dict[str, str]) -> None:
    """Create or replace one Modal secret using the Modal CLI.

    :param name: Secret name.
    :param pairs: Key/value pairs to store.
    :raises SystemExit: If the Modal CLI is missing or the command fails.
    """
    modal_cli = shutil.which("modal")
    if modal_cli is None:
        sys.exit("The Modal CLI is not installed. Run: pip install modal, then: modal setup")
    args = [modal_cli, "secret", "create", name, *[f"{k}={v}" for k, v in pairs.items()], "--force"]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        # Modal's own error text does not include the secret values.
        sys.exit(f"modal secret create {name} failed:\n{result.stderr.strip() or result.stdout.strip()}")
    print(f"Modal secret '{name}' saved with {len(pairs)} values.")


def cmd_modal(_: argparse.Namespace) -> int:
    """Push artemis-omnigent-deploy and artemis-llm to Modal."""
    values = read_env()
    problems = validate(values)
    if problems:
        print("Fix .env first (python scripts/make_secrets.py check).")
        return 1
    run_modal_secret("artemis-omnigent-deploy", {k: values[k] for k in DEPLOY_KEYS})
    run_modal_secret("artemis-llm", {k: values[k] for k in LLM_KEYS if is_filled(values.get(k))})
    print("Next: modal deploy lab/modal_server.py")
    return 0


def cmd_materials_project(_: argparse.Namespace) -> int:
    """Collect the Materials Project key via the clipboard and save it to Modal."""
    values = read_env()
    if not values:
        print("No .env found. Run: python scripts/make_secrets.py init")
        return 1
    if not sys.stdin.isatty():
        print("Run this command in a terminal window so it can read your clipboard.")
        return 1
    print("Nothing secret is shown here. (Do not press Ctrl+C in this window.)")
    try:
        answer = ask_value("MP_API_KEY")
    except KeyboardInterrupt:
        print("\nStopped. Nothing was changed.")
        return 1
    if not answer:
        return 1
    values = {key: values.get(key, "") for key in ALL_KEYS}
    values["MP_API_KEY"] = answer
    save_env(values)
    print(f"Saved the Materials Project key to {ENV_PATH}")
    problems = validate(values)
    if problems:
        print("The key is saved locally, but .env has other problems, so Modal was not updated:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    run_modal_secret("artemis-llm", {k: values[k] for k in LLM_KEYS if is_filled(values.get(k))})
    print("The lab's agents will receive it the next time a session starts.")
    return 0


def cmd_vercel(_: argparse.Namespace) -> int:
    """Print the Vercel environment variables to add in the dashboard."""
    values = read_env()
    missing = [k for k in VERCEL_KEYS if not is_filled(values.get(k))]
    if missing:
        print("Missing in .env: " + ", ".join(missing))
        return 1
    print("Add these in Vercel > artemis project > Settings > Environment Variables")
    print("(environments: Production, Preview, Development). Mark the secret ones Sensitive.\n")
    for key in VERCEL_KEYS:
        tag = "  [secret]" if key in VERCEL_SECRET_KEYS else ""
        print(f"{key}={values[key]}{tag}")
    print("\nThen redeploy the project so the new values take effect.")
    return 0


def main() -> int:
    """Parse arguments and dispatch to a subcommand."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create .env and collect your values")
    init.add_argument("--reenter", nargs="+", choices=sorted(REENTER_GROUPS),
                      help="discard saved values and enter them again, e.g. --reenter anthropic database")
    init.set_defaults(func=cmd_init)
    for name, func in (("check", cmd_check), ("modal", cmd_modal), ("vercel", cmd_vercel),
                       ("materials-project", cmd_materials_project)):
        sub.add_parser(name).set_defaults(func=func)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
