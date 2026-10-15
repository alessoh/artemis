"""Artemis Project 1 harness: independent reproduction of Shi, Ceyhan and Billor,
"Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs"
(arXiv:2501.06268v3).

This is the replication arm of Artemis, not an agent search: there is no mutable
experiment file. The harness runs the authors' own R code (see r/unccd_job.R)
on frozen inputs, records every result as one JSON file per job, and summarises
the results against the published tables with bootstrap confidence intervals.

Commands
    python lab/unccd/harness.py real   [--workers 2] [--perms 100] [--seeds 100]
    python lab/unccd/harness.py sim    --cells CELLS [--reps 1:100] [--chunk 10]
    python lab/unccd/harness.py summarize

CELLS is a comma-separated list such as "Uniform/20d/n200/3,Gaussian/10d/n50/2";
each names a driver script (distribution/dimension/size) and a number of clusters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
VENDOR = Path(os.environ.get("UNCCD_VENDOR", HERE / "vendor" / "ccd"))
WORK = Path(os.environ.get("UNCCD_WORK", HERE / "work"))
RESULTS = WORK / "results"
TABLES = WORK / "null_tables"
SIMCACHE = WORK / "simdata"
RJOB = HERE / "r" / "unccd_job.R"
OUT = ROOT / "docs" / "results" / "unccd_repro1"

sys.path.insert(0, str(HERE))
import prepare_data  # noqa: E402

# ---------------------------------------------------------------------------
# Published values (arXiv:2501.06268v3, Table 13) and the authors' driver settings
# ---------------------------------------------------------------------------
PUBLISHED_T13 = {  # method -> dataset -> (ARI, Sil, k)
    "KS-CCD": {"iris": (0.561, 0.578, 2), "seeds": (0.497, 0.468, 2), "user_knowledge": (0.005, 0.254, 2), "wholesale": (-0.013, 0.765, 2), "asymmetric": (0.691, 0.643, 4), "R15": (0.989, 0.753, 15), "D31": (0.948, 0.574, 31)},
    "RK-CCD": {"iris": (0.557, 0.393, 3), "seeds": (0.500, 0.164, 3), "user_knowledge": (0.052, 0.119, 2), "wholesale": (-0.002, 0.344, 2), "asymmetric": (0.730, 0.605, 4), "R15": (0.993, 0.753, 15), "D31": (0.814, 0.495, 30)},
    "UN-CCD": {"iris": (0.599, 0.445, 3), "seeds": (0.509, 0.467, 2), "user_knowledge": (0.091, 0.158, 2), "wholesale": (0.002, 0.113, 3), "asymmetric": (0.736, 0.606, 4), "R15": (0.975, 0.742, 15), "D31": (0.799, 0.474, 31)},
    "DBSCAN": {"iris": (0.544, 0.517, 2), "seeds": (0.003, 0.121, 1), "user_knowledge": (0.005, 0.198, 1), "wholesale": (0.006, 0.569, 1), "asymmetric": (0.467, 0.548, 3), "R15": (0.936, 0.702, 15), "D31": (0.350, 0.343, 15)},
    "K-means++": {"iris": (0.590, 0.459, 3), "seeds": (0.773, 0.404, 3), "user_knowledge": (0.202, 0.169, 4), "wholesale": (-0.007, 0.446, 3), "asymmetric": (0.882, 0.645, 5), "R15": (0.894, 0.678, 15), "D31": (0.912, 0.547, 31)},
    "Spectral": {"iris": (0.555, 0.475, 3), "seeds": (0.679, 0.349, 3), "user_knowledge": (0.189, 0.120, 4), "wholesale": (-0.012, 0.446, 3), "asymmetric": (0.975, 0.623, 5), "R15": (0.899, 0.611, 15), "D31": (0.778, 0.332, 31)},
    "Louvain": {"iris": (0.630, 0.436, 3), "seeds": (0.722, 0.394, 3), "user_knowledge": (0.149, 0.155, 5), "wholesale": (-0.004, 0.243, 6), "asymmetric": (0.805, 0.479, 8), "R15": (0.604, 0.644, 10), "D31": (0.371, 0.446, 9)},
}
DATASETS = ["iris", "seeds", "user_knowledge", "wholesale", "asymmetric", "R15", "D31"]

# From simulations/clustering/UN_CCDs/Simulations/Real_Data/Real_Data_UNCCD.R:
# (quantile level label, scan direction, dimension named in the table file)
DRIVER_UNCCD = {
    "iris": ("90", "ascend", 4), "seeds": ("95", "descend", 7), "user_knowledge": ("95", "ascend", 6),
    "wholesale": ("95", "ascend", 8), "asymmetric": ("80", "ascend", 2), "R15": ("85", "ascend", 2),
    "D31": ("85", "ascend", 2),
}
# D31 (n = 3,100) takes about 7 minutes per UN-CCD run on one core here, so it gets
# 5 shuffles per reading instead of 100: each run takes 7 to 18 minutes here. The cap was lowered from 20 to 10 to 5 for compute after the first two D31 results (original order, one shuffle) were in; the values played no part.
PERMS_CAP = {"D31": 5}
# Spectral clustering on D31 builds a 3,100 x 3,100 kernel and eigendecomposition per run;
# it gets 3 seeds (Louvain on D31 5; spectral on asymmetric 50) instead of 100, lowered for compute after the first spectral D31 run (45 minutes) was in.
BASELINE_SEED_CAP = {("spectral", "D31"): 3, ("louvain", "D31"): 5, ("spectral", "asymmetric"): 50}
DATA_D = {"iris": 4, "seeds": 7, "user_knowledge": 5, "wholesale": 6, "asymmetric": 2, "R15": 2, "D31": 2}

BASELINES = {"dbscan": "DBSCAN", "kmeanspp": "K-means++", "spectral": "Spectral", "louvain": "Louvain"}

# Simulation driver settings, read from the scripts (quantile level, direction)
SIM_LEVEL = {("Uniform", 2): "85", ("Uniform", 3): "90", ("Uniform", 5): "95", ("Uniform", 10): "99", ("Uniform", 20): "999",
             ("Gaussian", 2): "85", ("Gaussian", 3): "90", ("Gaussian", 5): "95", ("Gaussian", 10): "999", ("Gaussian", 20): "999"}


# ---------------------------------------------------------------------------
# Job execution
# ---------------------------------------------------------------------------
def job_id(job: dict) -> str:
    blob = json.dumps({k: v for k, v in sorted(job.items()) if k not in ("vendor", "cache")}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def table_csv(d: int, tag: str = "") -> str:
    p = TABLES / f"nn_null_d{d}{('_' + tag) if tag else ''}.csv"
    return str(p)   # run_all defers any job whose table is not built yet


def run_job(job: dict) -> dict:
    jid = job_id(job)
    out = RESULTS / f"{jid}.json"
    if out.exists():
        return json.loads(out.read_text())
    RESULTS.mkdir(parents=True, exist_ok=True)
    jf = WORK / "jobs" / f"{jid}.json"
    jf.parent.mkdir(parents=True, exist_ok=True)
    full = dict(job, vendor=str(VENDOR), cache=str(SIMCACHE))
    jf.write_text(json.dumps(full))
    tmp = out.with_suffix(".tmp")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    res = subprocess.run(["Rscript", str(RJOB), str(jf), str(tmp)], capture_output=True, text=True, env=env)
    if res.returncode != 0 or not tmp.exists():
        rec = {"status": "crash", "job": job, "stderr": res.stderr[-4000:]}
    else:
        rec = json.loads(tmp.read_text())
        tmp.unlink()
    rec["wall_seconds"] = time.time() - t0
    rec["job_id"] = jid
    out.write_text(json.dumps(rec))
    return rec


def run_all(jobs: list[dict], workers: int, label: str) -> list[dict]:
    waiting = [j for j in jobs if "table_csv" in j and not Path(j["table_csv"]).exists()]
    if waiting:
        print(f"[{label}] {len(waiting)} jobs deferred: their null table is not built yet", flush=True)
    jobs = [j for j in jobs if j not in waiting]
    todo = [j for j in jobs if not (RESULTS / f"{job_id(j)}.json").exists()]
    print(f"[{label}] {len(jobs)} jobs, {len(jobs) - len(todo)} already done, {len(todo)} to run on {workers} workers", flush=True)
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_job, j): j for j in todo}
        for f in as_completed(futs):
            done += 1
            r = f.result()
            if r.get("status") not in ("ok", None) or done % 10 == 0 or done == len(todo):
                el = time.time() - t0
                print(f"[{label}] {done}/{len(todo)} ({el / 60:.1f} min) last={r.get('status')} "
                      f"{r.get('job', {}).get('dataset', r.get('job', {}).get('script', ''))}", flush=True)
    return [run_job(j) for j in jobs]


# ---------------------------------------------------------------------------
# Job lists
# ---------------------------------------------------------------------------
def real_jobs(perms: int, seeds: int, datasets: list[str], kinds: tuple[str, ...] = ("real", "baseline")) -> list[dict]:
    jobs = []
    for ds in datasets:
        if "baseline" in kinds:
            for m in BASELINES:
                nseed = 1 if m == "dbscan" else min(seeds, BASELINE_SEED_CAP.get((m, ds), seeds))
                for s in range(1, nseed + 1):
                    jobs.append({"kind": "baseline", "dataset": ds, "method": m, "seed": s})
        if "real" not in kinds:
            continue
        lvl, direction, td = DRIVER_UNCCD[ds]
        # an independent second null table (seed 20261514 + d), original row order only
        jobs.append({"kind": "real", "variant": "driver_tableB", "dataset": ds, "level": lvl, "direction": direction,
                     "table_d": td, "table_csv": table_csv(td, "B"), "perm": 0, "fun": "UNCCD_clustering"})
        nperm = min(perms, PERMS_CAP.get(ds, perms))
        for p in range(nperm + 1):
            perm = 0 if p == 0 else 1000 + p
            # V1: the authors' driver exactly (level, direction, table dimension named in the driver)
            jobs.append({"kind": "real", "variant": "driver", "dataset": ds, "level": lvl, "direction": direction,
                         "table_d": td, "table_csv": table_csv(td), "perm": perm, "fun": "UNCCD_clustering"})
            # V2: the protocol as the paper states it (alpha = 1%, ascending scan, table for the data's dimension)
            jobs.append({"kind": "real", "variant": "stated", "dataset": ds, "level": "99", "direction": "ascend",
                         "table_d": DATA_D[ds], "table_csv": table_csv(DATA_D[ds]), "perm": perm, "fun": "UNCCD_clustering"})
            # V3: the driver with the table built for the data's actual dimension (only where they differ)
            if td != DATA_D[ds]:
                jobs.append({"kind": "real", "variant": "driver_dfix", "dataset": ds, "level": lvl, "direction": direction,
                             "table_d": DATA_D[ds], "table_csv": table_csv(DATA_D[ds]), "perm": perm, "fun": "UNCCD_clustering"})
    return jobs


def parse_cell(spec: str) -> tuple[str, int, int, int]:
    dist, dd, nn, k = spec.split("/")
    return dist, int(dd.rstrip("d")), int(nn.lstrip("n")), int(k)


def sim_jobs(cells: list[str], reps: tuple[int, int], chunk: int, tag: str = "",
             direction_override: str = "", level_override: str = "") -> list[dict]:
    jobs = []
    for spec in cells:
        dist, d, n, k = parse_cell(spec)
        script = f"simulations/clustering/UN_CCDs/Simulations/{dist}/{d}d/{d}d_235clusters_n{n}.R"
        direction = direction_override or ("descend" if d >= 10 else "ascend")
        lvl = level_override or SIM_LEVEL[(dist, d)]
        for a in range(reps[0], reps[1] + 1, chunk):
            b = min(a + chunk - 1, reps[1])
            jobs.append({"kind": "sim", "script": script, "dist": dist, "d": d, "n": n, "ncls": k,
                         "reps": list(range(a, b + 1)), "level": lvl, "direction": direction,
                         "table_d": d, "table_csv": table_csv(d, tag), "fun": "UNCCD_clustering"})
            if tag:
                jobs[-1]["table_tag"] = tag
            if direction_override or level_override:
                jobs[-1]["diagnostic"] = f"{direction}/{lvl}"
    return jobs


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------
def boot_ci(x: np.ndarray, B: int = 10000, seed: int = 0) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (B, len(x)))].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def load_results() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(RESULTS.glob("*.json"))]


def summarize() -> dict:
    recs = load_results()
    out: dict = {"real_unccd": {}, "baselines": {}, "sim": {}, "errors": []}
    for r in recs:
        if r.get("status") in ("error", "crash"):
            out["errors"].append({"job": r.get("job"), "status": r.get("status"),
                                  "message": r.get("message") or r.get("stderr", "")[-500:]})
    # --- real data, UN-CCD
    by = {}
    for r in recs:
        j = r.get("job", {})
        if j.get("kind") == "real" and r.get("status") == "ok":
            by.setdefault((j["variant"], j["dataset"]), []).append(r)
    for (variant, ds), rows in sorted(by.items()):
        orig = [x for x in rows if x["job"]["perm"] == 0]
        perm = [x for x in rows if x["job"]["perm"] != 0]
        ari = np.array([x["ari"] for x in perm])
        sil = np.array([np.nan if x["sil"] is None else x["sil"] for x in perm])
        ks = [x["k"] for x in perm]
        pub = PUBLISHED_T13["UN-CCD"][ds]
        out["real_unccd"].setdefault(variant, {})[ds] = {
            "published": {"ari": pub[0], "sil": pub[1], "k": pub[2]},
            "original_order": ({"ari": orig[0]["ari"], "sil": orig[0]["sil"], "k": orig[0]["k"],
                                "seconds": orig[0]["seconds"], "n": orig[0]["n"], "d": orig[0]["d"]} if orig else None),
            "permutations": {
                "count": len(perm), "ari_mean": float(np.mean(ari)) if len(ari) else None,
                "ari_ci95": boot_ci(ari), "ari_min": float(np.min(ari)) if len(ari) else None,
                "ari_max": float(np.max(ari)) if len(ari) else None,
                "ari_q05_q95": [float(np.quantile(ari, 0.05)), float(np.quantile(ari, 0.95))] if len(ari) else None,
                "sil_mean": float(np.nanmean(sil)) if len(sil) else None,
                "k_counts": {str(k): ks.count(k) for k in sorted(set(ks))},
                "share_k_equal_published": (sum(1 for k in ks if k == pub[2]) / len(ks)) if ks else None,
                "share_ari_within_0.01_of_published": float(np.mean(np.abs(ari - pub[0]) <= 0.01)) if len(ari) else None,
                "distinct_label_hashes": len({x.get("label_hash") for x in perm}),
            },
        }
    # --- baselines
    bb = {}
    for r in recs:
        j = r.get("job", {})
        if j.get("kind") == "baseline" and r.get("status") == "ok":
            bb.setdefault((j["method"], j["dataset"]), []).append(r)
    for (m, ds), rows in sorted(bb.items()):
        ari = np.array([x["ari"] for x in rows])
        ks = [x["k"] for x in rows]
        pub = PUBLISHED_T13[BASELINES[m]][ds]
        out["baselines"].setdefault(BASELINES[m], {})[ds] = {
            "published": {"ari": pub[0], "sil": pub[1], "k": pub[2]}, "runs": len(rows),
            "ari_mean": float(ari.mean()), "ari_ci95": boot_ci(ari), "ari_min": float(ari.min()), "ari_max": float(ari.max()),
            # published values are given to three decimals, so compare at that precision
            "share_runs_ari_below_published": float(np.mean(np.round(ari, 3) < pub[0])),
            "share_runs_ari_equal_published": float(np.mean(np.round(ari, 3) == pub[0])),
            "published_within_range": bool(np.round(ari.min(), 3) <= pub[0] <= np.round(ari.max(), 3)),
            "sil_mean": float(np.nanmean([np.nan if x["sil"] is None else x["sil"] for x in rows])),
            "k_counts": {str(k): ks.count(k) for k in sorted(set(ks))},
        }
    # --- simulations
    ss = {}
    for r in recs:
        j = r.get("job", {})
        if j.get("kind") == "sim":
            key = f"{j['dist']}/{j['d']}d/n{j['n']}/{j['ncls']}" + (f" [table {j['table_tag']}]" if j.get("table_tag") else "") + (f" [diagnostic {j['diagnostic']}]" if j.get("diagnostic") else "")
            for row in r.get("rows", []):
                ss.setdefault(key, []).append((row, j))
    for key, rows in sorted(ss.items()):
        # one result per repetition (a repetition run in two chunk layouts is counted once)
        uniq = {}
        for x, _ in rows:
            if x.get("status") == "ok":
                uniq.setdefault(x["rep"], x)
        ok = [uniq[r] for r in sorted(uniq)]
        ari = np.array([x["ari"] for x in ok])
        sil = np.array([x["sil"] for x in ok])
        k = int(key.split(" ")[0].split("/")[-1])
        sr = np.array([1.0 if x["k"] == k else 0.0 for x in ok])
        secs = np.array([x["seconds"] for x in ok])
        out["sim"][key] = {
            "reps": len(ok), "errors": len(rows) - len(ok),
            "ari_mean": float(ari.mean()) if len(ari) else None, "ari_ci95": boot_ci(ari),
            "sil_mean": float(sil.mean()) if len(sil) else None, "sil_ci95": boot_ci(sil),
            "sr_mean": float(sr.mean()) if len(sr) else None, "sr_ci95": boot_ci(sr),
            "seconds_per_rep_mean": float(secs.mean()) if len(secs) else None,
            "rep_range": [min(x["rep"] for x in ok), max(x["rep"] for x in ok)] if ok else None,
        }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT / 'summary.json'}: {len(recs)} records, {len(out['errors'])} errors")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("real")
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--perms", type=int, default=100)
    r.add_argument("--seeds", type=int, default=100)
    r.add_argument("--datasets", type=str, default=",".join(DATASETS))
    r.add_argument("--kinds", type=str, default="real,baseline")
    s = sub.add_parser("sim")
    s.add_argument("--cells", type=str, required=True)
    s.add_argument("--reps", type=str, default="1:100")
    s.add_argument("--chunk", type=int, default=10)
    s.add_argument("--workers", type=int, default=2)
    s.add_argument("--table-tag", type=str, default="", help="use the independent table nn_null_d<d>_<tag>.csv")
    s.add_argument("--direction", type=str, default="", help="diagnostic: override the driver's scan direction")
    s.add_argument("--level", type=str, default="", help="diagnostic: override the driver's quantile level label")
    sub.add_parser("summarize")
    a = ap.parse_args()

    subprocess.run([sys.executable, str(HERE / "prepare_data.py"), "--check"], check=True)
    if a.cmd == "real":
        run_all(real_jobs(a.perms, a.seeds, a.datasets.split(","), tuple(a.kinds.split(","))), a.workers, "real")
    elif a.cmd == "sim":
        lo, hi = (int(x) for x in a.reps.split(":"))
        run_all(sim_jobs(a.cells.split(","), (lo, hi), a.chunk, a.table_tag, a.direction, a.level), a.workers, "sim")
    else:
        summarize()


if __name__ == "__main__":
    main()
