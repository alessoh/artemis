"""Figures for the Project 1 reproduction report, drawn from the harness results.

    python lab/unccd/make_figures.py

Writes docs/results/unccd_repro1/fig_real_data.png and fig_seeds_order.png.
Colours: categorical slots 1 and 2 of the reference palette (validated: CVD and
normal-vision separation pass on the light surface).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "docs" / "results" / "unccd_repro1"
RESULTS = HERE / "work" / "results"

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#e6e5e0"
LABELS = {"iris": "iris", "seeds": "seeds", "user_knowledge": "knowledge", "wholesale": "wholesale",
          "asymmetric": "asymmetric", "R15": "R15", "D31": "D31"}
ORDER = ["iris", "seeds", "user_knowledge", "wholesale", "asymmetric", "R15", "D31"]


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def load_real():
    rows = []
    for p in RESULTS.glob("*.json"):
        r = json.loads(p.read_text())
        j = r.get("job", {})
        if j.get("kind") == "real" and r.get("status") == "ok":
            rows.append(r)
    return rows


def fig_real(summary: dict):
    u = summary["real_unccd"]
    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    style(ax)
    ys = np.arange(len(ORDER))[::-1]
    for y, ds in zip(ys, ORDER):
        drv = u.get("driver", {}).get(ds)
        if not drv:
            continue
        pub = drv["published"]["ari"]
        perm = drv["permutations"]
        if perm["count"]:
            lo, hi = perm["ari_min"], perm["ari_max"]
            ax.plot([lo, hi], [y, y], color=BLUE, alpha=0.35, linewidth=6, solid_capstyle="round", zorder=1)
        if drv["original_order"]:
            ax.scatter([drv["original_order"]["ari"]], [y], s=46, color=BLUE, edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.scatter([pub], [y], s=70, marker="D", facecolor="none", edgecolor=ORANGE, linewidth=1.8, zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels([LABELS[d] for d in ORDER], color=INK)
    ax.set_xlim(-0.05, 1.02)
    ax.set_xlabel("Adjusted Rand index", color=INK2, fontsize=9)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="D", linestyle="none", markerfacecolor="none", markeredgecolor=ORANGE, markeredgewidth=1.8, markersize=7, label="Published (Table 13)"),
               Line2D([], [], marker="o", linestyle="none", color=BLUE, markersize=7, label="Reproduced, original row order"),
               Line2D([], [], color=BLUE, alpha=0.35, linewidth=6, label="Range over row shuffles")]
    ax.legend(handles=handles, loc="lower left", fontsize=8, frameon=False, labelcolor=INK2)
    ax.set_title("UN-CCD on the real datasets, authors' driver settings", color=INK, fontsize=10.5, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_real_data.png", facecolor=SURFACE)
    plt.close(fig)


def fig_seeds(rows):
    drv = [r["ari"] for r in rows if r["job"]["dataset"] == "seeds" and r["job"]["variant"] == "driver" and r["job"]["perm"] != 0]
    st = [r["ari"] for r in rows if r["job"]["dataset"] == "seeds" and r["job"]["variant"] == "stated" and r["job"]["perm"] != 0]
    drv_k = [r["k"] for r in rows if r["job"]["dataset"] == "seeds" and r["job"]["variant"] == "driver" and r["job"]["perm"] != 0]
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    style(ax)
    rng = np.random.default_rng(0)
    marker_for_k = {2: "o", 3: "s", 4: "^"}
    for k in sorted(set(drv_k)):
        xs = [a for a, kk in zip(drv, drv_k) if kk == k]
        ax.scatter(xs, 1 + rng.uniform(-0.18, 0.18, len(xs)), s=16, marker=marker_for_k.get(k, "o"), color=BLUE,
                   edgecolor=SURFACE, linewidth=0.6, label=f"{k} clusters found", zorder=3)
    ax.scatter(st, 0 + rng.uniform(-0.18, 0.18, len(st)), s=16, color=ORANGE, edgecolor=SURFACE, linewidth=0.6, zorder=3)
    ax.axvline(0.509, color=INK2, linewidth=1, linestyle=(0, (3, 3)))
    ax.text(0.512, 1.42, "published 0.509", color=INK2, fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Stated protocol\n(alpha 1%, ascending)", "Authors' driver\n(alpha 5%, descending)"], color=INK, fontsize=8.5)
    ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel("Adjusted Rand index over 100 row shuffles of the seeds data", color=INK2, fontsize=9)
    ax.legend(loc="lower left", fontsize=7.5, frameon=False, labelcolor=INK2, ncol=3, bbox_to_anchor=(0.0, 0.33))
    fig.tight_layout()
    fig.savefig(OUT / "fig_seeds_order.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    summary = json.loads((OUT / "summary.json").read_text())
    rows = load_real()
    fig_real(summary)
    fig_seeds(rows)
    print("figures written to", OUT)


if __name__ == "__main__":
    main()
