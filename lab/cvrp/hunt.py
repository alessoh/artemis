"""Record hunting: run the lab's solver for a long time on one CVRPLIB instance.

The lab's loop uses short time limits so that sixty experiments fit in an
afternoon. A best-known solution (BKS) is only ever beaten by long runs, so
this script gives the promoted solver (lab/cvrp/experiment.py, or any trial)
many minutes and several independent seeds, keeps the best routes, and asks
the frozen harness to check them. A human runs it; the agents do not.

On Modal (one container per seed, all at once), from the artemis folder:

    modal run lab/cvrp/hunt.py --instance X-n801-k40 --minutes 60 --seeds 8

On this computer instead (seeds one after another, one core each):

    python lab/cvrp/hunt.py --local --instance X-n801-k40 --minutes 10 --seeds 2

Every seed's routes are saved under runs/cvrp/hunt/ in CVRPLIB format, the
best is checked with `harness.py verify`, and the verdict is appended to
runs/cvrp/records.tsv. Nothing is claimed as a record until it has also been
compared with the live CVRPLIB table, because the snapshot's BKS can be out
of date.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
MAX_MINUTES = 330  # stays inside the Modal function timeout below


def distance_matrix(coords: list[list[int]]) -> np.ndarray:
    """Rounded Euclidean distances (the same rule as the harness)."""
    xy = np.asarray(coords, dtype=np.float64)
    diff = xy[:, None, :] - xy[None, :, :]
    return np.floor(np.sqrt((diff ** 2).sum(axis=2)) + 0.5).astype(np.int64)


def run_solver(source: str, instance: dict, minutes: float, seed: int) -> dict:
    """Import the solver from *source* and run it on *instance* for *minutes*."""
    view = {
        "capacity": int(instance["capacity"]),
        "coords": np.asarray(instance["coords"], dtype=np.int64),
        "demands": np.asarray(instance["demands"], dtype=np.int64),
        "distance": distance_matrix(instance["coords"]),
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hunt_solver.py"
        path.write_text(source, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("hunt_solver", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        np.random.seed(seed)
        started = time.time()
        routes = module.solve(view, float(minutes) * 60.0, int(seed))
    return {"seed": seed, "seconds": round(time.time() - started, 1),
            "routes": [[int(v) for v in r] for r in routes if len(r)]}


# ---------------------------------------------------------------- Modal path
try:  # Modal is only needed for `modal run`; the harness and sandbox never import it.
    import modal

    app = modal.App("artemis-cvrp-hunt")
    _image = modal.Image.debian_slim(python_version="3.12").pip_install("numpy>=1.24", "pyvrp==0.14.0")

    @app.function(image=_image, cpu=1.0, memory=4096, timeout=6 * 3600)
    def hunt_remote(source: str, instance: dict, minutes: float, seed: int) -> dict:
        """One seed of one hunt, in its own container."""
        return run_solver(source, instance, minutes, seed)

    @app.local_entrypoint()
    def modal_main(instance: str, minutes: float = 30.0, seeds: int = 4,
                   experiment: str = "lab/cvrp/experiment.py") -> None:
        """Entry point for `modal run lab/cvrp/hunt.py --instance NAME ...`."""
        hunt(instance, minutes, seeds, experiment, remote=True)

except ImportError:  # pragma: no cover - exercised only where Modal is absent
    modal = None


def load_instance(name: str) -> dict:
    """Load one instance from the frozen snapshot through the harness."""
    sys.path.insert(0, str(HERE))
    import harness  # noqa: PLC0415 - imported late so Modal containers never need it
    instances = harness.load_instances()
    if name not in instances:
        raise SystemExit(f"Unknown instance {name}. Run `python lab/cvrp/harness.py describe`.")
    return instances[name]


def write_solution(path: Path, routes: list[list[int]], cost: int) -> None:
    """Save routes in the CVRPLIB solution format."""
    lines = [f"Route #{i}: {' '.join(map(str, r))}" for i, r in enumerate(routes, start=1)]
    path.write_text("\n".join(lines) + f"\nCost {cost}\n", encoding="utf-8")


def hunt(name: str, minutes: float, seeds: int, experiment: str, remote: bool) -> int:
    """Run the solver on *name* with *seeds* seeds; save and verify the best routes."""
    if not 0 < minutes <= MAX_MINUTES:
        raise SystemExit(f"--minutes must be between 0 and {MAX_MINUTES}")
    sys.path.insert(0, str(HERE))
    import harness  # noqa: PLC0415
    instance = load_instance(name)
    if instance["split"] in ("val", "test", "scale") and not harness.final_done():
        raise SystemExit(f"{name} is in the {instance['split']} split, which stays untouched until the "
                         "lab has run `final`. Hunt a train or hunt instance instead.")
    source_path = (REPO_ROOT / experiment).resolve() if not Path(experiment).is_absolute() else Path(experiment)
    source = source_path.read_text(encoding="utf-8")
    payload = {k: instance[k] for k in ("capacity", "coords", "demands")}
    print(f"Hunting {name} ({instance['customers']} customers, BKS {instance['bks']}) with "
          f"{harness.relative(source_path)} for {minutes} min x {seeds} seeds "
          f"({'Modal' if remote else 'this computer'}).", flush=True)
    if remote:
        results = list(hunt_remote.starmap([(source, payload, minutes, s) for s in range(seeds)]))
    else:
        results = []
        for s in range(seeds):
            print(f"  seed {s} ...", flush=True)
            results.append(run_solver(source, payload, minutes, s))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = harness.RUNS_DIR / "hunt" / f"{name}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    best = None
    for result in results:
        try:
            cost = harness.check_solution(instance, result["routes"])
        except harness.HarnessError as exc:
            print(f"  seed {result['seed']}: INVALID ({exc})")
            continue
        sol = out_dir / f"seed{result['seed']}.sol"
        write_solution(sol, result["routes"], cost)
        print(f"  seed {result['seed']}: cost {cost}  gap {harness.gap_pct(cost, instance['bks']):.3f}%  "
              f"({result['seconds']} s)")
        if best is None or cost < best[0]:
            best = (cost, sol)
    if best is None:
        print("No valid solution was produced.")
        return 1
    (out_dir / "source_experiment.py").write_text(source, encoding="utf-8")
    print(f"\nBest: {best[0]} (BKS {instance['bks']}). Checking it with the frozen harness:")
    return subprocess.run([sys.executable, str(HERE / "harness.py"), "verify", "--instance", name,
                           "--solution", str(best[1])], cwd=REPO_ROOT).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local", action="store_true", help="run on this computer instead of Modal")
    parser.add_argument("--instance", required=True)
    parser.add_argument("--minutes", type=float, default=10.0)
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--experiment", default="lab/cvrp/experiment.py")
    args = parser.parse_args(argv)
    if not args.local:
        print("To hunt on Modal run:  modal run lab/cvrp/hunt.py --instance NAME --minutes 60 --seeds 8")
        print("To hunt on this computer add --local.")
        return 2
    return hunt(args.instance, args.minutes, args.seeds, args.experiment, remote=False)


if __name__ == "__main__":
    sys.exit(main())
