"""Compare the Python port of UN-CCD (lab/unccd_alpha/unccd.py) with the authors' R code.

    Rscript lab/unccd_alpha/validation/r_reference.R lab/unccd_alpha/work/rref
    python lab/unccd_alpha/validation/validate_port.py lab/unccd_alpha/work/rref

For every reference case it runs the port on the same data and null-table
entries and reports whether the radii, the dominating balls and the labels are
identical, the largest difference in radius and in silhouette, and the time
taken by each implementation. Writes validation.json next to the cases.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unccd  # noqa: E402


def ari(a, b) -> float:
    """Adjusted Rand index (Hubert and Arabie), as mclust::adjustedRandIndex."""
    a = np.unique(np.asarray(a), return_inverse=True)[1]
    b = np.unique(np.asarray(b), return_inverse=True)[1]
    n = len(a)
    table = np.zeros((a.max() + 1, b.max() + 1))
    np.add.at(table, (a, b), 1)
    comb = lambda x: x * (x - 1) / 2.0  # noqa: E731
    s_ij = comb(table).sum()
    s_a = comb(table.sum(axis=1)).sum()
    s_b = comb(table.sum(axis=0)).sum()
    expected = s_a * s_b / comb(n)
    maximum = (s_a + s_b) / 2.0
    return float((s_ij - expected) / (maximum - expected)) if maximum != expected else 1.0


def main(folder: str) -> int:
    rows = []
    for path in sorted(Path(folder).glob("*.json")):
        if path.name == "validation.json":
            continue
        case = json.loads(path.read_text())
        X = np.asarray(case["X"], dtype=np.float64)
        t0 = time.time()
        out = unccd.cluster(X, case["env_ave"], case["env_med"], case["method"])
        g = unccd.graph(X, case["env_ave"], case["env_med"], case["method"])
        secs = time.time() - t0
        r_rad = np.asarray(case["radii"], dtype=np.float64)
        r_intd = np.asarray(case["int_d"], dtype=int) - 1
        r_lab = np.asarray(case["labels"], dtype=int)
        row = {
            "case": case["name"], "n": int(X.shape[0]), "d": int(X.shape[1]), "method": case["method"],
            "radii_identical": bool(np.array_equal(out["radii"], r_rad)),
            "radii_max_abs_diff": float(np.max(np.abs(out["radii"] - r_rad))),
            "int_d_identical": bool(np.array_equal(g["Int.D"], r_intd)),
            "labels_identical": bool(np.array_equal(out["labels"], r_lab)),
            "ari_port_vs_r": ari(out["labels"], r_lab),
            "si_abs_diff": abs(out["si"] - case["si"]),
            "si_ind_equal": out["si_ind"] == case["si_ind"],
            "ari_vs_truth_r": ari(r_lab, case["Y"]), "ari_vs_truth_port": ari(out["labels"], case["Y"]),
            "r_seconds": case["r_seconds"], "port_seconds": secs,
        }
        rows.append(row)
        flag = "OK " if row["labels_identical"] and row["radii_identical"] else "DIFF"
        print(f"{flag} {row['case']:<45} n={row['n']:<5} radii={row['radii_identical']!s:<5} "
              f"intD={row['int_d_identical']!s:<5} labels={row['labels_identical']!s:<5} "
              f"dsi={row['si_abs_diff']:.1e} R {row['r_seconds']:.1f}s port {secs:.1f}s")
    summary = {
        "cases": len(rows),
        "labels_identical": sum(r["labels_identical"] for r in rows),
        "radii_identical": sum(r["radii_identical"] for r in rows),
        "int_d_identical": sum(r["int_d_identical"] for r in rows),
        "max_si_abs_diff": max(r["si_abs_diff"] for r in rows) if rows else None,
        "rows": rows,
    }
    (Path(folder) / "validation.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\n{summary['labels_identical']}/{summary['cases']} identical labellings, "
          f"{summary['radii_identical']}/{summary['cases']} identical radii")
    return 0 if summary["labels_identical"] == summary["cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
