"""Post hoc checks on the test conductors for the Langlands run (not pre-registered).

Run from the artemis folder on the langlands-lab branch, after the run's final test:

    python docs/results/langlands_run1/posthoc_checks.py

It scores three simple rules suggested by the laboratory's analysis on the test
conductors (400,000 <= N < 500,000) with the frozen harness's within-conductor
statistics, and compares them pairwise. Nothing is written to the ledger.
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "lab" / "langlands"))
import harness as h  # noqa: E402


def legendre_minus_one(p: int) -> int:
    """(-1/p) for an odd prime p."""
    return 1 if p % 4 == 1 else -1


def main() -> int:
    table = h.RankTable()
    idx = table.split("test")
    rank2 = table.rank[idx] == 2

    def rule(fn):
        return np.array([fn(table.signs(int(i))) for i in idx], dtype=float)

    r = rule(lambda b: sum((1 if p >= 5 else -1) for p, e, w in b if w == -1))
    d = rule(lambda b: sum(1 for p, e, w in b if p >= 5 and e >= 2 and w != legendre_minus_one(p)))
    m5 = rule(lambda b: sum(1 for p, e, w in b if p >= 5 and e == 1 and w == -1))
    m23 = rule(lambda b: sum(1 for p, e, w in b if p < 5 and w == -1))
    simple = h.split_count_scores(table, idx)

    def parts(scores):
        return h.within_parts(scores, table.N[idx], rank2)

    rules = {"size rule r": r, "Rohrlich integer rule m5 + 3D - 2 m23": m5 + 3 * d - 2 * m23,
             "departure count D": d}
    for name, scores in rules.items():
        print(name, h.within_summary(parts(scores)))
    print("r minus simple rule", h.paired_delta(parts(r), parts(simple)))
    print("integer rule minus r", h.paired_delta(parts(m5 + 3 * d - 2 * m23), parts(r)))
    print("D minus simple rule", h.paired_delta(parts(d), parts(simple)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
