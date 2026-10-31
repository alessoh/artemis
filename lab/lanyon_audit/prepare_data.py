"""Fetch Lanyon AI's seven solver repositories at the pinned commits and check them.

The repositories are cloned (Git LFS screen recordings skipped) into
lab/lanyon_audit/work/lanyon/<Repository>, or into $ARTEMIS_LANYON_ROOT, and are
never copied into the Artemis repository. Every file the audit reads, the 72
specifications and their 72 C implementations, must match the SHA-256 recorded
in data/manifest.json.

    python lab/lanyon_audit/prepare_data.py                    # clone if needed, then check
    python lab/lanyon_audit/prepare_data.py --check            # check only
    python lab/lanyon_audit/prepare_data.py --write-manifest   # humans, once, when building the lab
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judge import FAMILIES  # noqa: E402

ROOT = Path(os.environ.get("ARTEMIS_LANYON_ROOT", HERE / "work" / "lanyon"))
MANIFEST = HERE / "data" / "manifest.json"
URL = "https://github.com/lanyonai/{}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files(root: Path) -> list[Path]:
    files = []
    for family in FAMILIES:
        for spec in sorted((root / family / "specifications").glob("*.rkt")):
            files.append(spec)
            files.append(root / family / "implementations" / f"{spec.stem}.c")
    return files


def clone() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    for family, commit in FAMILIES.items():
        target = ROOT / family
        if not (target / ".git").exists():
            print(f"cloning {family} ...", flush=True)
            subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "--quiet", URL.format(family), str(target)],
                           check=True, env=env)
            subprocess.run(["git", "-C", str(target), "config", "core.autocrlf", "false"], check=True)
        head = subprocess.run(["git", "-C", str(target), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        if not head.startswith(commit):
            subprocess.run(["git", "-C", str(target), "checkout", "--quiet", commit], check=True, env=env)


def check() -> list[str]:
    if not MANIFEST.exists():
        return ["data/manifest.json is missing"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems = []
    for rel, expected in manifest["sha256"].items():
        path = ROOT / rel
        if not path.exists():
            problems.append(f"missing {rel}")
        elif sha256(path) != expected:
            problems.append(f"changed {rel}")
    found = {str(p.relative_to(ROOT)).replace(os.sep, "/") for p in tracked_files(ROOT) if p.exists()}
    extra = found - set(manifest["sha256"])
    if extra:
        problems.append(f"{len(extra)} files not in the manifest, e.g. {sorted(extra)[0]}")
    return problems


def write_manifest() -> None:
    files = tracked_files(ROOT)
    missing = [f for f in files if not f.exists()]
    if missing:
        raise SystemExit(f"missing files, e.g. {missing[0]}")
    manifest = {"commits": FAMILIES, "count_specs": sum(1 for f in files if f.suffix == ".rkt"),
                "sha256": {str(f.relative_to(ROOT)).replace(os.sep, "/"): sha256(f) for f in files}}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST} ({manifest['count_specs']} specifications)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-manifest", action="store_true")
    args = ap.parse_args()
    if not args.check:
        clone()
    if args.write_manifest:
        write_manifest()
        return 0
    problems = check()
    if problems:
        print("The Lanyon snapshot is missing or altered: " + "; ".join(problems[:5]))
        return 1
    print(f"Lanyon snapshot OK: {len(json.loads(MANIFEST.read_text())['sha256'])} files at the pinned commits "
          f"in {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
