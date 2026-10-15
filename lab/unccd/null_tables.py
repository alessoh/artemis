"""Monte Carlo null tables for the UN-CCD spatial randomness test.

The UN-CCD test compares the mean and median nearest-neighbour distance (NND) of
the k points inside a candidate ball, divided by the ball's radius, with their
distribution for k points spread uniformly in a unit ball of the same dimension.
The authors' code stores the lower-tail quantiles of these two statistics for
every k = 1..n in a table (entry 1 is 0 by convention). Their tables for the
dimensions used here are not in their repository, and their own generator
(R/ccds/quantile_table.R) simulates a fresh point set for every k, which costs
O(n^3) per Monte Carlo iteration and is too slow on a small machine for n in
the thousands.

This module produces the same tables with one change of method: in each
iteration it draws one uniform sample of n_max points and uses its first k
points as the sample of size k. The first k points of an i.i.d. uniform sample
are themselves an i.i.d. uniform sample of size k, so each entry has exactly the
same marginal distribution as in the authors' generator; only the Monte Carlo
correlation between entries changes, and the test reads each entry on its own.
`validate` compares the two generators directly.

Quantiles use R's default (type 7), which is NumPy's "linear" method.

Usage:
    python lab/unccd/null_tables.py build --d 4 --n 400 --niter 10000
    python lab/unccd/null_tables.py validate --d 4 --n 40 --niter 4000
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TABLE_DIR = Path(os.environ.get("UNCCD_WORK", HERE / "work")) / "null_tables"
LEVELS = (0.80, 0.85, 0.90, 0.95, 0.99, 0.999)   # the "quant" labels used in the authors' drivers
BASE_SEED = 20261014


def uniform_ball(rng: np.random.Generator, n: int, d: int) -> np.ndarray:
    """n points uniform in the unit ball of R^d (the authors' rpoisball.unit)."""
    z = rng.standard_normal((n, d))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    r = rng.random(n) ** (1.0 / d)
    return z * r[:, None]


def prefix_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean and median NND of the first k points of x, for k = 1..n (entry k-1).

    cm[i, c] = min over l <= c, l != i, of |x_i - x_l|; for the prefix of size k
    the NND of point i < k is cm[i, k-1].
    """
    n = x.shape[0]
    sq = np.einsum("ij,ij->i", x, x)
    dist2 = sq[:, None] + sq[None, :] - 2.0 * (x @ x.T)
    np.maximum(dist2, 0.0, out=dist2)
    dist = np.sqrt(dist2)
    np.fill_diagonal(dist, np.inf)
    cm = np.minimum.accumulate(dist, axis=1)
    upper = np.triu(np.ones((n, n), dtype=bool))       # rows i <= column c
    ave = np.zeros(n)
    med = np.zeros(n)
    k = np.arange(1, n + 1)
    vals = np.where(upper, cm, 0.0)
    ave[1:] = vals.sum(axis=0)[1:] / k[1:]
    masked = np.where(upper, cm, np.nan)
    med[1:] = np.nanmedian(masked[:, 1:], axis=0)
    return ave, med                                     # entry 0 (k = 1) stays 0, as in the authors' tables


def simulate(d: int, n: int, niter: int, seed: int, report_every: int = 500) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    ave = np.empty((niter, n), dtype=np.float64)
    med = np.empty((niter, n), dtype=np.float64)
    t0 = time.time()
    for it in range(niter):
        ave[it], med[it] = prefix_stats(uniform_ball(rng, n, d))
        if report_every and (it + 1) % report_every == 0:
            el = time.time() - t0
            print(f"  d={d} n={n}: {it + 1}/{niter} iterations, {el:.0f}s elapsed, ~{el / (it + 1) * (niter - it - 1):.0f}s left", flush=True)
    return ave, med


def table_path(d: int, tag: str = "") -> Path:
    return TABLE_DIR / f"nn_null_d{d}{('_' + tag) if tag else ''}.npz"


def build(d: int, n: int, niter: int, seed: int | None = None, tag: str = "") -> Path:
    seed = BASE_SEED + d if seed is None else seed
    t0 = time.time()
    ave, med = simulate(d, n, niter, seed)
    out = {"d": d, "n": n, "niter": niter, "seed": seed, "method": "nested-prefix", "seconds": time.time() - t0}
    arrays = {}
    for q in LEVELS:
        key = label(q)
        arrays[f"ave_{key}"] = np.quantile(ave, 1.0 - q, axis=0, method="linear")
        arrays[f"med_{key}"] = np.quantile(med, 1.0 - q, axis=0, method="linear")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    p = table_path(d, tag)
    np.savez(p, meta=json.dumps(out), **arrays)
    export_csv(p)
    print(f"wrote {p} in {out['seconds']:.0f}s")
    return p


def label(q: float) -> str:
    """0.95 -> '95', 0.999 -> '999' (the authors' file labels)."""
    s = f"{q * 100:.6f}".rstrip("0").rstrip(".")
    return s.replace(".", "")


def export_csv(npz_path: Path) -> Path:
    """One CSV per table for the R driver: columns k, ave_<label>, med_<label>, ..."""
    z = np.load(npz_path)
    meta = json.loads(str(z["meta"]))
    cols = ["k"] + [f"{s}_{label(q)}" for q in LEVELS for s in ("ave", "med")]
    n = meta["n"]
    mat = np.column_stack([np.arange(1, n + 1)] + [z[c] for c in cols[1:]])
    csv = npz_path.with_suffix(".csv")
    np.savetxt(csv, mat, delimiter=",", header=",".join(cols), comments="", fmt="%.10g")
    return csv


def validate(d: int, n: int, niter: int, rscript: str = "Rscript") -> dict:
    """Generate the same table with the authors' R generator and with this one, and compare."""
    vendor = HERE / "vendor" / "ccd"
    rcode = f"""
suppressMessages({{library(MASS)}})
setwd("{vendor}")
source("R/ccds/quantile_table.R")
out <- list()
for (q in c({",".join(str(q) for q in LEVELS)})) {{
  s <- ccd_generate_quantile_table("NN", {d}, q, {n}, niter={niter}, cores=2, seed=7)
  out[[as.character(q)]] <- list(ave = s$average, med = s$median)
}}
cat(jsonlite::toJSON(out, digits = NA))
"""
    t0 = time.time()
    res = subprocess.run([rscript, "-e", rcode], capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(res.stderr[-3000:])
    r_tabs = json.loads(res.stdout)
    r_seconds = time.time() - t0
    t0 = time.time()
    ave, med = simulate(d, n, niter, seed=99, report_every=0)
    py_seconds = time.time() - t0
    report = {"d": d, "n": n, "niter": niter, "r_seconds": r_seconds, "py_seconds": py_seconds, "levels": {}}
    rng = np.random.default_rng(5)
    for q in LEVELS:
        lab = str(q)
        r_ave = np.array(r_tabs[lab]["ave"], dtype=float)
        r_med = np.array(r_tabs[lab]["med"], dtype=float)
        p_ave = np.quantile(ave, 1 - q, axis=0)
        p_med = np.quantile(med, 1 - q, axis=0)
        # Monte Carlo standard error of each quantile, by bootstrap over iterations
        boots_a, boots_m = [], []
        for _ in range(200):
            idx = rng.integers(0, niter, niter)
            boots_a.append(np.quantile(ave[idx], 1 - q, axis=0))
            boots_m.append(np.quantile(med[idx], 1 - q, axis=0))
        se_a = np.std(boots_a, axis=0) * np.sqrt(2)       # SE of a difference of two independent estimates
        se_m = np.std(boots_m, axis=0) * np.sqrt(2)
        ks = np.arange(2, n)                               # skip k = 1 (0 by convention)
        za = (p_ave[ks] - r_ave[ks]) / np.where(se_a[ks] > 0, se_a[ks], np.nan)
        zm = (p_med[ks] - r_med[ks]) / np.where(se_m[ks] > 0, se_m[ks], np.nan)
        report["levels"][lab] = {
            "max_abs_rel_diff_ave": float(np.nanmax(np.abs(p_ave[ks] / r_ave[ks] - 1))),
            "max_abs_rel_diff_med": float(np.nanmax(np.abs(p_med[ks] / r_med[ks] - 1))),
            "mean_z_ave": float(np.nanmean(za)), "sd_z_ave": float(np.nanstd(za)),
            "mean_z_med": float(np.nanmean(zm)), "sd_z_med": float(np.nanstd(zm)),
            "share_abs_z_gt_3": float(np.nanmean(np.abs(np.concatenate([za, zm])) > 3)),
        }
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--d", type=int, required=True)
    b.add_argument("--n", type=int, required=True)
    b.add_argument("--niter", type=int, default=10000)
    b.add_argument("--seed", type=int, default=None, help="default 20261014 + d")
    b.add_argument("--tag", type=str, default="", help="suffix for an independent second table, e.g. B")
    v = sub.add_parser("validate")
    v.add_argument("--d", type=int, required=True)
    v.add_argument("--n", type=int, default=40)
    v.add_argument("--niter", type=int, default=4000)
    v.add_argument("--out", type=str, default="")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.d, a.n, a.niter, a.seed, a.tag)
    else:
        rep = validate(a.d, a.n, a.niter)
        txt = json.dumps(rep, indent=2)
        print(txt)
        if a.out:
            Path(a.out).write_text(txt + "\n")


if __name__ == "__main__":
    main()
