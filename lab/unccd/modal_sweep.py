"""Run the full UN-CCD simulation reproduction on Modal (500 repetitions per cell).

This is the same harness as lab/unccd/harness.py, fanned out over Modal containers.
It needs nothing beyond a Modal account: no API keys, no secrets.

    pip install modal          # once
    modal setup                # once, signs in to your Modal account
    modal run lab/unccd/modal_sweep.py                          # all 120 cells, 500 repetitions
    modal run lab/unccd/modal_sweep.py --cells "Uniform/20d/n200/3" --reps 1:500
    modal run lab/unccd/modal_sweep.py --dry-run                # count jobs, run nothing

Results are written into lab/unccd/work/results/ on your machine, one JSON per job,
so that `python lab/unccd/harness.py summarize` folds them into the summary.

Untested on Modal from the build session (that workspace had no Modal credentials).
The first run should be a dry run and then a single small cell.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

LAB = Path(__file__).resolve().parent
REMOTE_LAB = "/root/lab/unccd"
VENDOR = "/opt/ccd"
WORK = "/data/work"

COMMIT = "9bc803219933be17e28ccc0af703844ebf97ea5a"
REPO = "https://github.com/Rui-Shi/Cluster-Catch-Digraphs-for-Clustering-and-Outlier-Detection"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "r-base-core", "r-cran-mclust", "r-cran-igraph", "r-cran-mass", "r-cran-cluster",
                 "r-cran-jsonlite", "r-cran-here", "r-cran-dplyr", "r-cran-readxl")
    .pip_install("numpy==2.1.3")
    .run_commands(f"git clone -q {REPO} {VENDOR} && cd {VENDOR} && git checkout -q {COMMIT}")
    .env({"UNCCD_VENDOR": VENDOR, "UNCCD_WORK": WORK, "OMP_NUM_THREADS": "1"})
    .add_local_dir(str(LAB), REMOTE_LAB, ignore=["vendor", "work", "__pycache__"])
)
volume = modal.Volume.from_name("artemis-unccd-repro", create_if_missing=True)
app = modal.App("artemis-unccd-repro", image=image)

DISTS = ["Uniform", "Gaussian"]
DIMS = [2, 3, 5, 10, 20]
SIZES = [50, 100, 200, 500]
NCLS = [2, 3, 5]


@app.function(volumes={"/data": volume}, cpu=4.0, memory=8192, timeout=6 * 3600)
def build_table(d: int, n: int) -> str:
    import subprocess
    import sys
    p = Path(WORK) / "null_tables" / f"nn_null_d{d}.csv"
    if not p.exists():
        subprocess.run([sys.executable, f"{REMOTE_LAB}/null_tables.py", "build", "--d", str(d), "--n", str(n),
                        "--niter", "10000"], check=True)
        volume.commit()
    return str(p)


@app.function(volumes={"/data": volume}, cpu=1.0, memory=4096, timeout=12 * 3600, retries=1)
def run_chunk(job: dict) -> dict:
    import sys
    sys.path.insert(0, REMOTE_LAB)
    volume.reload()
    import harness  # noqa: E402  (reads UNCCD_VENDOR and UNCCD_WORK)
    job = dict(job, table_csv=harness.table_csv(job["d"]))
    rec = harness.run_job(job)
    volume.commit()
    return rec


@app.local_entrypoint()
def main(cells: str = "", reps: str = "1:500", chunk: int = 25, dry_run: bool = False):
    lo, hi = (int(x) for x in reps.split(":"))
    if cells:
        cell_list = cells.split(",")
    else:
        cell_list = [f"{dist}/{d}d/n{n}/{k}" for dist in DISTS for d in DIMS for n in SIZES for k in NCLS]
    dims = sorted({int(c.split("/")[1].rstrip("d")) for c in cell_list})
    level = {("Uniform", 2): "85", ("Uniform", 3): "90", ("Uniform", 5): "95", ("Uniform", 10): "99",
             ("Uniform", 20): "999", ("Gaussian", 2): "85", ("Gaussian", 3): "90", ("Gaussian", 5): "95",
             ("Gaussian", 10): "999", ("Gaussian", 20): "999"}
    jobs = []
    for spec in cell_list:
        dist, dd, nn, k = spec.split("/")
        d, n, k = int(dd.rstrip("d")), int(nn.lstrip("n")), int(k)
        script = f"simulations/clustering/UN_CCDs/Simulations/{dist}/{d}d/{d}d_235clusters_n{n}.R"
        for a in range(lo, hi + 1, chunk):
            b = min(a + chunk - 1, hi)
            jobs.append({"kind": "sim", "script": script, "dist": dist, "d": d, "n": n, "ncls": k,
                         "reps": list(range(a, b + 1)), "level": level[(dist, d)],
                         "direction": "descend" if d >= 10 else "ascend", "table_d": d,
                         "fun": "UNCCD_clustering"})
    print(f"{len(cell_list)} cells, {len(jobs)} chunks of up to {chunk} repetitions, null tables for d = {dims}")
    if dry_run:
        return
    list(build_table.starmap([(d, 500) for d in dims]))
    out = LAB / "work" / "results"
    out.mkdir(parents=True, exist_ok=True)
    done = 0
    for rec in run_chunk.map(jobs, order_outputs=False, return_exceptions=True):
        if isinstance(rec, Exception):
            print("chunk failed:", repr(rec)[:300])
            continue
        (out / f"modal_{rec['job_id']}.json").write_text(json.dumps(rec))
        done += 1
        if done % 50 == 0:
            print(f"{done}/{len(jobs)} chunks done")
    print(f"finished: {done}/{len(jobs)} chunks written to {out}")
