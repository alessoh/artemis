"""Build the frozen CVRP data snapshot for the Artemis routing program.

Run once, by a human, from the artemis folder:

    python lab/cvrp/prepare_data.py

What it does
------------
1. Clones github.com/PyVRP/Instances at a pinned commit into a temporary
   folder. That repository mirrors the CVRPLIB "X" instances of Uchoa et al.
   (2017) together with their best-known solutions (BKS), using CVRPLIB's
   convention of rounding every distance to the nearest integer.
2. Parses each X instance (coordinates, demands, capacity).
3. Re-computes the cost of every published BKS with this program's own
   checker and refuses to continue unless all 100 match the published cost
   exactly. This is the test that the harness measures routes the way the
   rest of the field does.
4. Assigns the pre-registered splits (train, val, test, scale, hunt).
5. Writes lab/cvrp/data/instances.json.gz and lab/cvrp/data/manifest.json.

The BKS routes themselves are NOT copied into the repository, only their
costs, so no experiment can copy a published solution.

Options:
    --source PATH   use an existing clone of PyVRP/Instances instead of cloning
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SNAPSHOT = DATA_DIR / "instances.json.gz"
MANIFEST = DATA_DIR / "manifest.json"

SOURCE_REPO = "https://github.com/PyVRP/Instances"
SOURCE_COMMIT = "7474b068a8effa7f39448b241314b615c9271525"  # "Update BKS", 2026-08-19
SOURCE_FOLDER = "CVRP"

# ---- pre-registered splits (fixed 2026-10-07 by Claude, owner Peter Alesso) ----
# Instances with fewer than 600 customers form the loop's world: every tenth
# instance by size (positions 3, 13, 23, ...) is val, every fourth of the rest
# is test, and the remainder is train. Instances with 600 or more customers
# are split into "scale" (held out, reported in the final test as a check that
# gains carry over to larger problems) and "hunt" (open to probing and to long
# record-hunting runs).
LOOP_MAX_CUSTOMERS = 600
SCALE_COUNT = 8


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 of *data*."""
    return hashlib.sha256(data).hexdigest()


def nint(value: float) -> int:
    """CVRPLIB rounding: nearest integer, halves rounded up."""
    return int(math.floor(value + 0.5))


def parse_vrp(text: str) -> dict:
    """Parse a CVRPLIB X instance (EUC_2D, one depot at node 1)."""
    header: dict[str, str] = {}
    coords: dict[int, tuple[int, int]] = {}
    demands: dict[int, int] = {}
    depots: list[int] = []
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("NODE_COORD_SECTION"):
            section = "coords"
            continue
        if upper.startswith("DEMAND_SECTION"):
            section = "demands"
            continue
        if upper.startswith("DEPOT_SECTION"):
            section = "depot"
            continue
        if upper.startswith("EOF"):
            break
        if section is None:
            key, _, value = line.partition(":")
            header[key.strip().upper()] = value.strip().strip('"')
            continue
        parts = line.split()
        if section == "coords":
            coords[int(parts[0])] = (int(float(parts[1])), int(float(parts[2])))
        elif section == "demands":
            demands[int(parts[0])] = int(parts[1])
        elif section == "depot":
            node = int(parts[0])
            if node != -1:
                depots.append(node)
    dimension = int(header["DIMENSION"])
    if header.get("EDGE_WEIGHT_TYPE") != "EUC_2D":
        raise ValueError(f"{header.get('NAME')}: only EUC_2D is supported")
    if depots != [1]:
        raise ValueError(f"{header.get('NAME')}: expected a single depot at node 1, got {depots}")
    if sorted(coords) != list(range(1, dimension + 1)) or sorted(demands) != list(range(1, dimension + 1)):
        raise ValueError(f"{header.get('NAME')}: node numbering is not 1..{dimension}")
    return {
        "name": header["NAME"],
        "dimension": dimension,
        "customers": dimension - 1,
        "capacity": int(header["CAPACITY"]),
        "coords": [list(coords[i]) for i in range(1, dimension + 1)],
        "demands": [demands[i] for i in range(1, dimension + 1)],
    }


def parse_sol(text: str) -> tuple[list[list[int]], int]:
    """Parse a CVRPLIB solution: routes of customer indices 1..n and the cost."""
    routes: list[list[int]] = []
    cost = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("route"):
            _, _, rest = line.partition(":")
            routes.append([int(x) for x in rest.split()])
        elif line.lower().startswith("cost"):
            cost = int(round(float(line.split()[1])))
    if cost is None:
        raise ValueError("solution has no Cost line")
    return routes, cost


def route_cost(coords: list[list[int]], routes: list[list[int]]) -> int:
    """Total rounded Euclidean length; node 0 is the depot, customers 1..n."""
    total = 0
    for route in routes:
        previous = 0
        for node in route + [0]:
            (x1, y1), (x2, y2) = coords[previous], coords[node]
            total += nint(math.hypot(x1 - x2, y1 - y2))
            previous = node
    return total


def check_routes(instance: dict, routes: list[list[int]]) -> None:
    """Raise if the routes do not visit every customer once within capacity."""
    n = instance["customers"]
    seen = [node for route in routes for node in route]
    if sorted(seen) != list(range(1, n + 1)):
        raise ValueError(f"{instance['name']}: routes do not visit every customer exactly once")
    for route in routes:
        load = sum(instance["demands"][node] for node in route)
        if load > instance["capacity"]:
            raise ValueError(f"{instance['name']}: a route carries {load} > capacity {instance['capacity']}")


def assign_splits(sizes: dict[str, int]) -> dict[str, str]:
    """Pre-registered, deterministic split assignment (see module constants)."""
    names = sorted(sizes, key=lambda k: (sizes[k], k))
    loop = [k for k in names if sizes[k] < LOOP_MAX_CUSTOMERS]
    large = [k for k in names if sizes[k] >= LOOP_MAX_CUSTOMERS]
    split: dict[str, str] = {}
    rest = []
    for position, name in enumerate(loop):
        if position % 10 == 3:
            split[name] = "val"
        else:
            rest.append(name)
    for position, name in enumerate(rest):
        split[name] = "test" if position % 4 == 1 else "train"
    # Spread the scale set evenly over the large instances.
    step = len(large) / SCALE_COUNT
    scale_positions = {int(step * i + step / 2) for i in range(SCALE_COUNT)}
    for position, name in enumerate(large):
        split[name] = "scale" if position in scale_positions else "hunt"
    return split


def clone_source(target: Path) -> Path:
    """Clone the source repository at the pinned commit into *target*."""
    subprocess.run(["git", "clone", "-q", SOURCE_REPO, str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "checkout", "-q", SOURCE_COMMIT], check=True)
    return target


def build(source: Path) -> dict:
    """Parse, verify and split every X instance in *source*."""
    folder = source / SOURCE_FOLDER
    vrp_files = sorted(folder.glob("X-*.vrp"))
    if len(vrp_files) != 100:
        raise SystemExit(f"Expected 100 X instances in {folder}, found {len(vrp_files)}")
    instances = []
    file_hashes = {}
    for vrp_path in vrp_files:
        sol_path = vrp_path.with_suffix(".sol")
        vrp_bytes = vrp_path.read_bytes()
        sol_bytes = sol_path.read_bytes()
        file_hashes[vrp_path.name] = sha256_bytes(vrp_bytes)
        file_hashes[sol_path.name] = sha256_bytes(sol_bytes)
        instance = parse_vrp(vrp_bytes.decode("utf-8"))
        routes, published = parse_sol(sol_bytes.decode("utf-8"))
        check_routes(instance, routes)
        computed = route_cost(instance["coords"], routes)
        if computed != published:
            raise SystemExit(f"{instance['name']}: our cost {computed} != published BKS {published}")
        instance["bks"] = published
        instance["bks_routes"] = len(routes)
        instances.append(instance)
    split = assign_splits({i["name"]: i["customers"] for i in instances})
    for instance in instances:
        instance["split"] = split[instance["name"]]
    return {"instances": instances, "file_hashes": file_hashes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", help="existing clone of PyVRP/Instances (checked out at the pinned commit)")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        if args.source:
            source = Path(args.source)
            head = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            if head and head != SOURCE_COMMIT:
                raise SystemExit(f"{source} is at {head[:12]}, expected the pinned {SOURCE_COMMIT[:12]}")
        else:
            print(f"Cloning {SOURCE_REPO} at {SOURCE_COMMIT[:12]} ...")
            source = clone_source(Path(tmp) / "Instances")
        built = build(source)
    instances = built["instances"]
    payload = json.dumps({"instances": instances}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # mtime=0 keeps the gzip bytes identical on every rebuild.
    with open(SNAPSHOT, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as handle:
        handle.write(payload)
    counts: dict[str, int] = {}
    for instance in instances:
        counts[instance["split"]] = counts.get(instance["split"], 0) + 1
    manifest = {
        "source_repo": SOURCE_REPO,
        "source_commit": SOURCE_COMMIT,
        "source_note": "CVRPLIB X instances (Uchoa et al. 2017, doi:10.1016/j.ejor.2016.08.012) "
                       "and best-known solutions as mirrored by PyVRP/Instances; distances "
                       "rounded to the nearest integer.",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "instances": len(instances),
        "splits": counts,
        "sha256": sha256_bytes(SNAPSHOT.read_bytes()),
        "checks": {"bks_recomputed_exactly": len(instances)},
        "split_members": {s: sorted((i["name"] for i in instances if i["split"] == s),
                                    key=lambda k: int(k.split("-")[1][1:]))
                          for s in sorted(counts)},
        "source_file_sha256": built["file_hashes"],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {SNAPSHOT.relative_to(HERE.parent.parent)} ({len(instances)} instances, "
          f"sha {manifest['sha256'][:12]})")
    print("Splits: " + json.dumps(counts))
    print(f"All {len(instances)} published BKS costs re-computed exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
