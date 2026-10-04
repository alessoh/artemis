"""Build the frozen data snapshot for the Artemis solar-absorber question.

This is the "prepare" step of the AutoResearch contract. It runs once, by a
human, and its output is committed to the repository so that every agent and
every judge sees exactly the same numbers.

What it does
------------
1. Downloads five benchmark files from the NIST JARVIS-Leaderboard on GitHub,
   pinned to one commit, and checks each against a pinned SHA-256. These give
   the official SLME train/val/test split and, for each material, the SLME
   label and four other DFT properties.
2. Downloads the JARVIS-DFT 3D release that the leaderboard was built from
   (jdft_3d-8-18-2021, about 55,000 materials) from figshare, and takes from it
   only what the leaderboard files lack: the chemical formula, the elements in
   the unit cell, the space group, the density and the cell volume.
3. Adds every material in that release that was never assessed for SLME
   (split "unlabeled"), with its cheap properties from the release: these are
   the materials the lab can recommend computing next.
4. Writes data/solar_snapshot.csv.gz and data/snapshot.json (the manifest:
   SHA-256 of the snapshot and of every source file, row counts and checks).

How to run it
-------------
On Modal (recommended; nothing large is downloaded to your computer):

    modal run lab/solar/prepare_data.py

On your own computer (downloads about 300 MB):

    python lab/solar/prepare_data.py --local

Both produce byte-identical snapshots for the same sources.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SNAPSHOT_NAME = "solar_snapshot.csv.gz"
MANIFEST_NAME = "snapshot.json"

LEADERBOARD_COMMIT = "57afc55f94c8a6f4562f73a3173968cd4b2f83b1"
LEADERBOARD_BASE = (
    "https://raw.githubusercontent.com/usnistgov/jarvis_leaderboard/"
    f"{LEADERBOARD_COMMIT}/jarvis_leaderboard/benchmarks/AI/SinglePropertyPrediction/"
)
# file name -> (snapshot column, pinned SHA-256 of the zip)
LEADERBOARD_FILES = {
    "dft_3d_slme.json.zip": (
        "slme",
        "f929bd463c98af317d98de6641c48f6347e6a069af03a3d6266c3bd3cafc049a",
    ),
    "dft_3d_optb88vdw_bandgap.json.zip": (
        "optb88vdw_bandgap",
        "6d9f7f6a7c321497649afa10f11e5e3b17f5ae7de4ff508e5e1ec2ee7cfb59e9",
    ),
    "dft_3d_formation_energy_peratom.json.zip": (
        "formation_energy_peratom",
        "ffaef5d3512a29c93f005c8b9f014b467dfa561b1c23632524ff91bbfa6f759f",
    ),
    "dft_3d_ehull.json.zip": (
        "ehull",
        "25b7ca5c43f5dd54fc98ff01e46bc42033e22d0b9e20048d90d628ea35e169ff",
    ),
    "dft_3d_mbj_bandgap.json.zip": (
        "mbj_bandgap",
        "7aee71bfea2f67e10a9aad4cc6b83636b58e09b46e01c713a82a333e9632fd95",
    ),
}
DFT3D_URL = "https://ndownloader.figshare.com/files/29204826"
DFT3D_MEMBER = "jdft_3d-8-18-2021.json"
DFT3D_CITATION = (
    "Choudhary et al., npj Computational Materials 6, 173 (2020); "
    "JARVIS-DFT 3D release 2021-08-18, figshare doi:10.6084/m9.figshare.6815699"
)
LEADERBOARD_CITATION = (
    "Choudhary et al., npj Computational Materials 10, 93 (2024), JARVIS-Leaderboard; "
    f"github.com/usnistgov/jarvis_leaderboard at commit {LEADERBOARD_COMMIT}"
)

COLUMNS = [
    "jid",
    "split",
    "formula",
    "composition",
    "elements",
    "n_elements",
    "nat",
    "spg_number",
    "spg_symbol",
    "crys",
    "density",
    "volume_per_atom",
    "optb88vdw_bandgap",
    "formation_energy_peratom",
    "ehull",
    "mbj_bandgap",
    "slme",
]


SPLIT_ORDER = {"train": 0, "val": 1, "test": 2}
STRUCTURE_COLUMNS = ("formula", "composition", "elements", "n_elements", "nat", "spg_number",
                     "spg_symbol", "crys", "density", "volume_per_atom")


def jid_number(jid: str) -> int:
    """Return the numeric part of a JARVIS id such as 'JVASP-1002' (0 if none)."""
    tail = jid.rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else 0


class PrepareError(RuntimeError):
    """Raised with a plain-language message when the snapshot cannot be built."""


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 of *data*."""
    return hashlib.sha256(data).hexdigest()


def download(url: str, timeout_s: float = 900.0) -> bytes:
    """Download *url* fully into memory, with a short progress line."""
    import requests

    print(f"  downloading {url}")
    started = time.time()
    with requests.get(url, stream=True, timeout=timeout_s) as response:
        response.raise_for_status()
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=1 << 20):
            chunks.append(chunk)
            total += len(chunk)
        data = b"".join(chunks)
    print(f"    {total / 1e6:.1f} MB in {time.time() - started:.0f} s")
    return data


def read_leaderboard(zip_bytes: bytes) -> dict[str, dict[str, float]]:
    """Return {split: {jid: value}} from one leaderboard benchmark zip."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise PrepareError(f"expected one file in the benchmark zip, found {names}")
        payload = json.loads(archive.read(names[0]))
    return {split: {str(k): float(v) for k, v in rows.items()} for split, rows in payload.items()}


def fmt(value: object) -> str:
    """Format a value for the CSV: empty for missing, compact repr for floats."""
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return repr(round(value, 6))
    return str(value)


def as_float(value: object) -> float | None:
    """Convert a JARVIS field to float; JARVIS writes missing values as 'na'."""
    if value is None or value == "na" or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(out) else out


def cell_volume(lattice: list[list[float]]) -> float | None:
    """Return the absolute determinant of a 3x3 lattice matrix, or None."""
    try:
        (a1, a2, a3), (b1, b2, b3), (c1, c2, c3) = lattice
    except (TypeError, ValueError):
        return None
    det = a1 * (b2 * c3 - b3 * c2) - a2 * (b1 * c3 - b3 * c1) + a3 * (b1 * c2 - b2 * c1)
    return abs(det)


def structure_fields(entry: dict) -> dict[str, object]:
    """Extract the structure-derived columns from one dft_3d record."""
    atoms = entry.get("atoms") or {}
    site_elements = [str(e) for e in atoms.get("elements") or []]
    counts = Counter(site_elements)
    nat = len(site_elements)
    volume = cell_volume(atoms.get("lattice_mat"))
    spg = entry.get("spg_number")
    try:
        spg = int(spg) if spg not in (None, "na", "") else None
    except (TypeError, ValueError):
        spg = None
    return {
        "formula": entry.get("formula") or "",
        "composition": " ".join(f"{el}:{counts[el]}" for el in sorted(counts)),
        "elements": " ".join(sorted(counts)),
        "n_elements": len(counts),
        "nat": nat if nat else None,
        "spg_number": spg,
        "spg_symbol": entry.get("spg_symbol") or "",
        "crys": entry.get("crys") or "",
        "density": as_float(entry.get("density")),
        "volume_per_atom": (volume / nat) if (volume and nat) else None,
        "dft3d_slme": as_float(entry.get("slme")),
    }


def build_snapshot() -> tuple[bytes, dict]:
    """Download the pinned sources and return (snapshot .csv.gz bytes, manifest)."""
    sources = []
    print("Step 1 of 3: JARVIS-Leaderboard benchmark files (pinned commit)")
    columns: dict[str, dict[str, dict[str, float]]] = {}
    for name, (column, pinned_sha) in LEADERBOARD_FILES.items():
        url = LEADERBOARD_BASE + name
        data = download(url, timeout_s=120)
        digest = sha256_bytes(data)
        if digest != pinned_sha:
            raise PrepareError(
                f"{name} does not match its pinned fingerprint "
                f"(expected {pinned_sha[:12]}, got {digest[:12]}). Stopping."
            )
        columns[column] = read_leaderboard(data)
        sources.append({"name": name, "url": url, "sha256": digest, "bytes": len(data)})

    # A material listed in two splits stays in the earliest one (train before
    # val before test), so nothing known in training can reappear as a search target.
    split_of: dict[str, str] = {}
    in_two_splits: list[str] = []
    for split in sorted(columns["slme"], key=lambda s: SPLIT_ORDER.get(s, 9)):
        for jid in columns["slme"][split]:
            if jid in split_of:
                in_two_splits.append(jid)
                continue
            split_of[jid] = split
    print(f"  SLME benchmark: {len(split_of)} materials " + ", ".join(
        f"{s} {len(r)}" for s, r in columns["slme"].items()))

    flat: dict[str, dict[str, float]] = {}
    for column, splits in columns.items():
        merged: dict[str, float] = {}
        for rows in splits.values():
            merged.update(rows)
        flat[column] = merged

    print("Step 2 of 3: JARVIS-DFT 3D release 2021-08-18 (structures and formulas)")
    blob = download(DFT3D_URL)
    sources.append({"name": DFT3D_MEMBER + ".zip", "url": DFT3D_URL,
                    "sha256": sha256_bytes(blob), "bytes": len(blob)})
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        records = json.loads(archive.read(DFT3D_MEMBER))
    del blob
    print(f"  {len(records)} materials in the release")
    wanted = set(split_of)
    structure: dict[str, dict[str, object]] = {}
    unlabeled: list[dict[str, object]] = []
    labeled_outside_benchmark = 0
    seen_unlabeled: set[str] = set()
    duplicate_unlabeled = 0
    for entry in records:
        jid = str(entry.get("jid", ""))
        if not jid:
            continue
        if jid in wanted:
            structure[jid] = structure_fields(entry)
        elif jid in seen_unlabeled:
            duplicate_unlabeled += 1
        elif as_float(entry.get("slme")) is not None:
            labeled_outside_benchmark += 1
        else:
            # Never assessed for SLME: these are the materials the lab can
            # actually recommend computing next. Cheap columns come from the
            # same 2021 release the leaderboard was built from.
            info = structure_fields(entry)
            if not info["elements"]:
                continue
            seen_unlabeled.add(jid)
            unlabeled.append({
                "jid": jid, "split": "unlabeled",
                **{k: info[k] for k in STRUCTURE_COLUMNS},
                "optb88vdw_bandgap": as_float(entry.get("optb88vdw_bandgap")),
                "formation_energy_peratom": as_float(entry.get("formation_energy_peratom")),
                "ehull": as_float(entry.get("ehull")),
                "mbj_bandgap": as_float(entry.get("mbj_bandgap")),
                "slme": None,
            })
    del records

    print("Step 3 of 3: joining and writing the snapshot")
    print(f"  {len(unlabeled)} materials in the release were never assessed for SLME")
    missing_structure = sorted(wanted - set(structure))
    slme_mismatch = 0
    rows_out = []
    for jid in sorted(split_of, key=lambda j: (SPLIT_ORDER.get(split_of[j], 9), jid_number(j), j)):
        info = structure.get(jid)
        if info is None:
            continue
        dft3d_slme = info.get("dft3d_slme")
        label = flat["slme"][jid]
        if dft3d_slme is not None and abs(dft3d_slme - label) > 0.011:
            slme_mismatch += 1
        row = {
            "jid": jid,
            "split": split_of[jid],
            **{k: info[k] for k in STRUCTURE_COLUMNS},
            "optb88vdw_bandgap": flat["optb88vdw_bandgap"].get(jid),
            "formation_energy_peratom": flat["formation_energy_peratom"].get(jid),
            "ehull": flat["ehull"].get(jid),
            "mbj_bandgap": flat["mbj_bandgap"].get(jid),
            "slme": label,
        }
        rows_out.append(row)
    labeled = list(rows_out)
    unlabeled.sort(key=lambda r: (jid_number(str(r["jid"])), str(r["jid"])))
    rows_out.extend(unlabeled)

    text = io.StringIO()
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in rows_out:
        writer.writerow([fmt(row[c]) for c in COLUMNS])
    raw = text.getvalue().encode("utf-8")
    # mtime=0 and no file name make the gzip bytes reproducible.
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0, compresslevel=9) as gz:
        gz.write(raw)
    snapshot = buffer.getvalue()

    per_split = Counter(r["split"] for r in rows_out)
    manifest = {
        "file": SNAPSHOT_NAME,
        "sha256": sha256_bytes(snapshot),
        "csv_sha256": sha256_bytes(raw),
        "rows": len(rows_out),
        "rows_per_split": dict(sorted(per_split.items())),
        "columns": COLUMNS,
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": sources,
        "citations": [LEADERBOARD_CITATION, DFT3D_CITATION],
        "checks": {
            "benchmark_materials": len(split_of),
            "listed_in_two_splits_kept_in_earliest": sorted(in_two_splits),
            "missing_from_dft3d_release": len(missing_structure),
            "missing_examples": missing_structure[:10],
            "slme_differs_from_release_by_more_than_0.01": slme_mismatch,
            "unlabeled_materials": len(unlabeled),
            "slme_known_but_outside_benchmark_left_out": labeled_outside_benchmark,
            "repeated_unlabeled_records_dropped": duplicate_unlabeled,
            "labeled_missing_optb88vdw_bandgap": sum(r["optb88vdw_bandgap"] is None for r in labeled),
            "labeled_missing_ehull": sum(r["ehull"] is None for r in labeled),
            "labeled_missing_formation_energy": sum(r["formation_energy_peratom"] is None for r in labeled),
            "labeled_missing_mbj_bandgap": sum(r["mbj_bandgap"] is None for r in labeled),
            "missing_elements": sum(not r["elements"] for r in rows_out),
        },
    }
    print(f"  {len(rows_out)} rows written; checks: {json.dumps(manifest['checks'])}")
    return snapshot, manifest


def write_outputs(snapshot: bytes, manifest: dict, data_dir: Path = DATA_DIR) -> None:
    """Write the snapshot and manifest into *data_dir* and print where they went."""
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / SNAPSHOT_NAME).write_bytes(snapshot)
    (data_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"Saved {data_dir / SNAPSHOT_NAME}  ({len(snapshot) / 1e6:.2f} MB)")
    print(f"Saved {data_dir / MANIFEST_NAME}")
    print(f"Snapshot fingerprint (SHA-256): {manifest['sha256']}")


# ---------------------------------------------------------------- Modal path
try:  # Modal is only needed for `modal run`; the sandbox and harness never import it.
    import modal

    app = modal.App("artemis-solar-prepare")
    _image = modal.Image.debian_slim(python_version="3.12").pip_install("requests>=2.31")

    @app.function(image=_image, memory=16384, cpu=2.0, timeout=3600)
    def build_on_modal() -> tuple[bytes, dict]:
        """Run build_snapshot inside a Modal container and return its results."""
        return build_snapshot()

    @app.local_entrypoint()
    def modal_main() -> None:
        """Entry point for `modal run lab/solar/prepare_data.py`."""
        print("Building the snapshot on Modal (this takes a few minutes)...")
        snapshot, manifest = build_on_modal.remote()
        write_outputs(snapshot, manifest)

except ImportError:  # pragma: no cover - exercised only where Modal is absent
    modal = None


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for running the build on this computer."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--local", action="store_true",
                        help="download and build on this computer instead of on Modal")
    args = parser.parse_args(argv)
    if not args.local:
        print("To build on Modal run:  modal run lab/solar/prepare_data.py")
        print("To build on this computer run:  python lab/solar/prepare_data.py --local")
        return 2
    try:
        snapshot, manifest = build_snapshot()
    except PrepareError as exc:
        print(f"\nCould not build the snapshot: {exc}")
        return 1
    write_outputs(snapshot, manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
