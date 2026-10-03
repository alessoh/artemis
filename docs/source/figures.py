"""Draw the two figures for the Artemis architecture discussion paper.

Figure 1: system architecture (browser, Vercel, research ledger, Omnigent lab, data sources).
Figure 2: the discovery loop built on the generalized three-file contract.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager

for f in font_manager.findSystemFonts():
    if "Inter" in f:
        try:
            font_manager.fontManager.addfont(f)
        except Exception:
            pass
plt.rcParams["font.family"] = "Inter"

INK = "#14213D"
MUTED = "#5B6577"
NAVY = "#1F3A5F"
TEAL = "#0F766E"
AMBER = "#B45309"
RED = "#9F1239"
PALE = {"navy": "#E8EEF6", "teal": "#E3F2F0", "amber": "#FBF1E4", "red": "#FBE9EE", "grey": "#F2F3F5"}


def box(ax, x, y, w, h, title, sub=None, edge=NAVY, fill="#FFFFFF", tsize=10.5, ssize=8.2, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.014",
                                linewidth=1.3, edgecolor=edge, facecolor=fill))
    if sub:
        ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", fontsize=tsize,
                color=INK, fontweight="bold" if bold else "normal")
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center", fontsize=ssize, color=MUTED,
                linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=tsize, color=INK,
                fontweight="bold" if bold else "normal")


def band(ax, x, y, w, h, label, fill, edge):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                linewidth=1.0, edgecolor=edge, facecolor=fill, linestyle=(0, (4, 3))))
    ax.text(x + 0.012, y + h - 0.022, label, ha="left", va="top", fontsize=9, color=edge,
            fontweight="bold")


def arrow(ax, p1, p2, color=INK, both=False, rad=0.0, lw=1.4, ls="-"):
    style = "<|-|>" if both else "-|>"
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=11, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls))


def figure_architecture(path):
    fig, ax = plt.subplots(figsize=(11, 8.2), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Layer 1: browser
    band(ax, 0.02, 0.835, 0.96, 0.145, "BROWSER  ·  artemis domain on Vercel", PALE["navy"], NAVY)
    pages = [("Intake", "state the problem"), ("Mission Control", "live 3D lab view"),
             ("Approvals", "human gates"), ("Evidence Graph", "cited sources"),
             ("Report", "Word and PDF export")]
    pw = 0.172
    for i, (t, s) in enumerate(pages):
        box(ax, 0.04 + i * (pw + 0.015), 0.848, pw, 0.078, t, s, edge=NAVY, tsize=9.8, ssize=7.8)

    # Layer 2: Vercel server side + ledger
    band(ax, 0.02, 0.585, 0.62, 0.205, "VERCEL", PALE["navy"], NAVY)
    box(ax, 0.04, 0.6, 0.18, 0.125, "Intake API", "creates Omnigent\nsession from problem", edge=NAVY)
    box(ax, 0.24, 0.6, 0.18, 0.125, "Stream Relay", "SSE proxy with resume;\ninjects identity header", edge=NAVY)
    box(ax, 0.44, 0.6, 0.18, 0.125, "Report Builder", "renders ledger into\n.docx and PDF", edge=NAVY)

    band(ax, 0.66, 0.585, 0.32, 0.205, "RESEARCH RECORD", PALE["grey"], MUTED)
    box(ax, 0.68, 0.6, 0.28, 0.125, "Append-only Ledger (Postgres)",
        "questions, evidence, hypotheses,\nexperiments, results, decisions, approvals", edge=MUTED, tsize=9.8)

    # Layer 3: Omnigent lab
    band(ax, 0.02, 0.19, 0.96, 0.375, "OMNIGENT", PALE["teal"], TEAL)
    agents = [("Compiler", "question to metric\nand frozen harness"), ("Scout", "literature and\ndata evidence"),
              ("Planner", "budget, two or more\ntests, picks one"), ("Experimenter ×N", "edits experiment.py\nkeep or revert"),
              ("Skeptic", "controls, stats,\ntries to falsify"), ("Scribe", "cited report\nfrom the ledger")]
    aw = 0.142
    for i, (t, s) in enumerate(agents):
        box(ax, 0.04 + i * (aw + 0.012), 0.345, aw, 0.11, t, s, edge=TEAL, tsize=9.6, ssize=7.6)
    for i in range(len(agents) - 1):
        x1 = 0.04 + i * (aw + 0.012) + aw
        arrow(ax, (x1 + 0.002, 0.40), (x1 + 0.011, 0.40), color=TEAL, lw=1.2)
    # feedback arc from Skeptic back to Planner
    arrow(ax, (0.04 + 4 * (aw + 0.012) + aw * 0.5, 0.46), (0.04 + 2 * (aw + 0.012) + aw * 0.5, 0.46),
          color=AMBER, rad=0.35, lw=1.5)
    ax.text(0.04 + 3 * (aw + 0.012) + aw * 0.5, 0.548, "surprising result reopens an assumption",
            ha="center", va="center", fontsize=7.8, color=AMBER, style="italic")

    box(ax, 0.04, 0.21, 0.44, 0.105, "Sentinel policies (stateful, above the harness)",
        "spend caps, tool permissions, egress rules,\napproval required for consequential actions", edge=RED, fill=PALE["red"], tsize=9.6)
    box(ax, 0.50, 0.21, 0.46, 0.105, "Omnibox sandboxes + compute",
        "OS-isolated worktrees per experiment;\nCPU in sandbox, GPU via Modal or Lightning when needed", edge=TEAL, tsize=9.6)

    # Layer 4: data sources
    band(ax, 0.02, 0.02, 0.96, 0.145, "LIVE SCIENTIFIC SOURCES  ·  real, authenticated, cited  ·  reached through MCP and Python tools", PALE["amber"], AMBER)
    srcs = ["OpenAlex", "arXiv", "Europe PMC", "PubChem", "Materials Project", "NIST JARVIS", "OpenML"]
    sw = 0.123
    for i, s in enumerate(srcs):
        box(ax, 0.035 + i * (sw + 0.012), 0.035, sw, 0.07, s, edge=AMBER, tsize=9.2)

    # Vertical connectors
    arrow(ax, (0.13, 0.844), (0.13, 0.729), both=True)
    arrow(ax, (0.33, 0.844), (0.33, 0.729), both=True)
    arrow(ax, (0.53, 0.844), (0.53, 0.729), both=True)
    arrow(ax, (0.13, 0.596), (0.13, 0.459), both=True, color=TEAL)
    arrow(ax, (0.33, 0.459), (0.33, 0.596), color=TEAL)
    arrow(ax, (0.82, 0.596), (0.88, 0.459), both=True, color=MUTED)
    arrow(ax, (0.624, 0.66), (0.676, 0.66), color=MUTED)
    arrow(ax, (0.73, 0.206), (0.73, 0.109), both=True, color=AMBER)

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure_loop(path):
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Left column: the three-file contract
    band(ax, 0.02, 0.06, 0.34, 0.9, "THE THREE-FILE CONTRACT", PALE["grey"], MUTED)
    box(ax, 0.045, 0.66, 0.29, 0.2, "program.md",
        "written by the client with the Compiler;\nobjective, rules, budget, ideas;\nthe human's only steering lever",
        edge=NAVY, fill=PALE["navy"], tsize=11)
    box(ax, 0.045, 0.39, 0.29, 0.2, "harness.py   (frozen)",
        "real data loaders, controls, baseline,\nthe sacred evaluate() metric;\nhash-locked after human approval",
        edge=RED, fill=PALE["red"], tsize=11)
    box(ax, 0.045, 0.12, 0.29, 0.2, "experiment.py   (mutable)",
        "the hypothesis expressed as code;\nthe only file agents may edit;\ngit commit per attempt",
        edge=TEAL, fill=PALE["teal"], tsize=11)

    # Right: the loop as a ring of six stages
    import math
    cx, cy, r = 0.70, 0.5, 0.33
    stages = [("Question", "client + Compiler"), ("Evidence", "Scout"), ("Hypothesis", "Planner"),
              ("Experiment", "Experimenter ×N"), ("Result", "Skeptic"), ("Decision", "Planner + human")]
    pts = []
    for i, (t, s) in enumerate(stages):
        ang = math.pi / 2 - i * 2 * math.pi / len(stages)
        x = cx + r * math.cos(ang) * 0.70
        y = cy + r * math.sin(ang)
        pts.append((x, y))
        edge = AMBER if t == "Decision" else TEAL
        box(ax, x - 0.075, y - 0.06, 0.15, 0.12, t, s, edge=edge, tsize=10.5, ssize=8)
    for i in range(len(pts)):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy)
        sx, sy = a[0] + dx / d * 0.095, a[1] + dy / d * 0.08
        ex, ey = b[0] - dx / d * 0.095, b[1] - dy / d * 0.08
        arrow(ax, (sx, sy), (ex, ey), color=TEAL if i < 5 else AMBER, rad=-0.18, lw=1.5)

    ax.text(cx, cy + 0.07, "keep if evaluate()", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.text(cx, cy + 0.025, "improves, else revert", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.text(cx, cy - 0.075, "NEVER STOP until budget,\nconvergence, or a human gate",
            ha="center", fontsize=8.2, color=MUTED, linespacing=1.3)

    # Contract to loop links
    arrow(ax, (0.339, 0.76), (pts[0][0] - 0.079, pts[0][1]), color=NAVY, rad=-0.1, ls=(0, (3, 2)))
    arrow(ax, (0.339, 0.22), (pts[3][0] - 0.079, pts[3][1] - 0.01), color=TEAL, rad=0.1, ls=(0, (3, 2)))
    arrow(ax, (0.339, 0.45), (pts[4][0] - 0.079, pts[4][1]), color=RED, rad=0.0, ls=(0, (3, 2)))

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    figure_architecture("fig1_architecture.png")
    figure_loop("fig2_loop.png")
    print("ok")
