"""Simple, numbered architecture diagram for the Artemis plain-language guide."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib import font_manager

for f in font_manager.findSystemFonts():
    if "Inter" in f:
        try:
            font_manager.fontManager.addfont(f)
        except Exception:
            pass
plt.rcParams["font.family"] = "Inter"

INK, MUTED = "#14213D", "#5B6577"
NAVY, TEAL, AMBER, PLUM, GREY = "#1F3A5F", "#0F766E", "#B45309", "#6D28D9", "#4B5563"
FILL = {NAVY: "#E8EEF6", TEAL: "#E3F2F0", AMBER: "#FBF1E4", PLUM: "#F1EBFB", GREY: "#F2F3F5"}


def card(ax, x, y, w, h, num, title, where, what, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.016",
                                lw=1.6, ec=color, fc=FILL[color]))
    tx = x + 0.012
    if num:
        ax.text(x + 0.022, y + h - 0.035, num, ha="center", va="center", color="white",
                fontsize=10, fontweight="bold", zorder=4,
                bbox=dict(boxstyle="circle,pad=0.3", fc=color, ec=color))
        tx = x + 0.046
    ax.text(tx, y + h - 0.035, title, ha="left", va="center", fontsize=11.5,
            fontweight="bold", color=INK)
    ax.text(x + 0.012, y + h - 0.085, where, ha="left", va="center", fontsize=8.8,
            color=color, fontweight="bold")
    ax.text(x + 0.012, y + h - 0.115, what, ha="left", va="top", fontsize=8.6, color=MUTED,
            linespacing=1.35)


def step(ax, x, y, n, color=INK):
    ax.text(x, y, str(n), ha="center", va="center", fontsize=9, fontweight="bold", color=color,
            zorder=6, bbox=dict(boxstyle="circle,pad=0.28", fc="white", ec=color, lw=1.6))


def arrow(ax, p1, p2, color=INK, both=False, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="<|-|>" if both else "-|>",
                                 mutation_scale=12, color=color, lw=1.6,
                                 connectionstyle=f"arc3,rad={rad}", zorder=2))


fig, ax = plt.subplots(figsize=(11, 6.6), dpi=220)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Client
card(ax, 0.01, 0.60, 0.15, 0.32, "", "You", "any web browser",
     "type a science\nquestion, watch\nthe lab work,\napprove key steps,\nread the report", GREY)

card(ax, 0.20, 0.60, 0.20, 0.32, "1", "Artemis website", "Vercel Pro",
     "the front door and the\nviewing window: intake\nform, live 3D lab view,\napprovals, report page", NAVY)
card(ax, 0.44, 0.60, 0.20, 0.32, "2", "Omnigent Server", "Modal or Databricks",
     "the switchboard: starts\nsessions, enforces safety\nrules and budgets,\nbroadcasts live events", TEAL)

# Runner with agents
card(ax, 0.68, 0.30, 0.31, 0.62, "3", "Omnigent Runner", "Modal sandbox",
     "the workbench: holds the model\nkeys; six agents think and run\nexperiments here", PLUM)
agents = ["Compiler", "Scout", "Planner", "Experimenters", "Skeptic", "Scribe"]
for i, a in enumerate(agents):
    col, row = i % 2, i // 2
    ax.add_patch(FancyBboxPatch((0.695 + col * 0.148, 0.585 - row * 0.08), 0.135, 0.058,
                                boxstyle="round,pad=0.003,rounding_size=0.012", lw=1.1,
                                ec=PLUM, fc="white"))
    ax.text(0.695 + col * 0.148 + 0.0675, 0.614 - row * 0.08, a, ha="center", va="center",
            fontsize=9.2, color=INK, fontweight="bold")
ax.text(0.835, 0.34, "three files:\nprogram.md · harness.py · experiment.py",
        ha="center", va="center", fontsize=7.8, color=PLUM, style="italic", linespacing=1.4)

card(ax, 0.20, 0.06, 0.44, 0.27, "4", "Lab notebook", "Neon Postgres via Vercel",
     "an append-only record of every question, source,\nhypothesis, experiment, result, decision and\napproval; the report is written from it", AMBER)
card(ax, 0.68, 0.02, 0.31, 0.22, "5", "Science libraries", "real public data only",
     "OpenAlex · arXiv · Europe PMC · PubChem\nMaterials Project · NIST JARVIS · OpenML", GREY)

# Journey arrows with numbered steps
arrow(ax, (0.164, 0.80), (0.198, 0.80))                     # you -> website
step(ax, 0.180, 0.86, "a")
arrow(ax, (0.404, 0.80), (0.436, 0.80))                     # website -> server
step(ax, 0.420, 0.86, "b")
arrow(ax, (0.644, 0.80), (0.676, 0.80))                     # server -> runner
step(ax, 0.660, 0.86, "c")
arrow(ax, (0.80, 0.296), (0.80, 0.244), both=True, color=PLUM)   # runner <-> libraries
step(ax, 0.835, 0.262, "d", PLUM)
arrow(ax, (0.676, 0.42), (0.644, 0.27), color=PLUM)          # runner -> notebook
step(ax, 0.66, 0.345, "e", PLUM)
arrow(ax, (0.676, 0.70), (0.644, 0.70), color=TEAL)          # runner -> server (events)
arrow(ax, (0.436, 0.70), (0.404, 0.70), color=TEAL)          # server -> website (events)
arrow(ax, (0.196, 0.70), (0.164, 0.70), color=TEAL)          # website -> you
step(ax, 0.420, 0.64, "f", TEAL)
arrow(ax, (0.30, 0.596), (0.30, 0.334), both=True, color=AMBER)  # website <-> notebook
step(ax, 0.30, 0.465, "g", AMBER)

fig.savefig("fig_simple.png", bbox_inches="tight", facecolor="white")
print("ok")
