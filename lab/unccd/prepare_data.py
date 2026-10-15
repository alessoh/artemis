"""Artemis Project 1 (UN-CCD reproduction): fetch and fingerprint the authors' code.

The authors' repository carries no licence file, so its code is not copied into
this repository. This script clones it at a pinned commit into lab/unccd/vendor
(ignored by git), checks the commit, and writes a snapshot file with SHA-256
fingerprints of every file the reproduction reads. The harness refuses to run
if any fingerprint has changed.

Usage:
    python lab/unccd/prepare_data.py            # clone (if needed) and fingerprint
    python lab/unccd/prepare_data.py --check    # verify the snapshot only
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
VENDOR = Path(os.environ.get("UNCCD_VENDOR", HERE / "vendor" / "ccd"))
SNAPSHOT = HERE / "data" / "snapshot.json"

REPO_URL = "https://github.com/Rui-Shi/Cluster-Catch-Digraphs-for-Clustering-and-Outlier-Detection"
PINNED_COMMIT = "9bc803219933be17e28ccc0af703844ebf97ea5a"  # 9 October 2026, HEAD when Project 1 began

# Files the reproduction reads: the method code, the data generator, the real data
# and the authors' drivers (read for their settings, never edited).
TRACKED = [
    "methods/clustering/UN-CCDs.R",
    "methods/outlier_detection/UN-MCCD.R",
    "R/ccds/UN_CCD.R",
    "R/ccds/ccdfunctions.R",
    "R/ccds/NN_Dist_Est.R",
    "R/ccds/quantile_table.R",
    "R/ccds/mKNN_CCD_functions.R",
    "R/general_functions/Uni-Gau_cls.R",
    "data/clustering/Real_Data_Collection.R",
    "data/clustering/iris.data",
    "data/clustering/seeds_dataset.txt",
    "data/clustering/user_knowlege.xls",
    "data/clustering/Wholesale customers data.csv",
    "data/clustering/asymmetric.txt",
    "data/clustering/asymmetric_label.txt",
    "data/clustering/R15.txt",
    "data/clustering/D31.txt",
    "simulations/clustering/UN_CCDs/Simulations/Real_Data/Real_Data_UNCCD.R",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def clone() -> None:
    if not (VENDOR / ".git").exists():
        VENDOR.parent.mkdir(parents=True, exist_ok=True)
        print(f"cloning {REPO_URL}")
        git("clone", "-q", REPO_URL, str(VENDOR))
    git("fetch", "-q", "origin", cwd=VENDOR)
    git("checkout", "-q", PINNED_COMMIT, cwd=VENDOR)
    head = git("rev-parse", "HEAD", cwd=VENDOR)
    if head != PINNED_COMMIT:
        sys.exit(f"vendor checkout is at {head}, expected {PINNED_COMMIT}")


def fingerprints() -> dict:
    out = {}
    for rel in TRACKED:
        p = VENDOR / rel
        if not p.exists():
            sys.exit(f"missing file in the authors' repository: {rel}")
        out[rel] = sha256(p)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the snapshot without writing")
    args = ap.parse_args()
    if args.check:
        snap = json.loads(SNAPSHOT.read_text())
        now = fingerprints()
        bad = [k for k in snap["files"] if snap["files"][k] != now.get(k)]
        head = git("rev-parse", "HEAD", cwd=VENDOR)
        if bad or head != snap["commit"]:
            sys.exit(f"snapshot mismatch: commit {head}; changed files {bad}")
        print("snapshot verified")
        return
    clone()
    snap = {"repo": REPO_URL, "commit": PINNED_COMMIT, "files": fingerprints()}
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snap, indent=2) + "\n")
    print(f"wrote {SNAPSHOT} ({len(snap['files'])} files)")


if __name__ == "__main__":
    main()
