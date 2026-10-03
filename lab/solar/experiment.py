"""Artemis solar experiment: the one file the agents change.

rank(train, candidates, seed) receives two pandas DataFrames from the harness
and returns every candidate jid exactly once, in the order the lab would spend
its expensive SLME calculations on them. Nothing else is read: no files, no
network. Earlier entries matter most; the harness scores how quickly the
order reaches ten excellent, stable absorbers.

train       every material in the JARVIS SLME training split, including the
            labels slme (percent) and mbj_bandgap (eV), plus the visible columns.
candidates  the earth-abundant, non-toxic search pool with visible columns only:
            jid, formula, composition ("Cu:2 S:4 Sn:1 Zn:2"), elements,
            n_elements, nat, spg_number, spg_symbol, crys, density,
            volume_per_atom, optb88vdw_bandgap (eV), formation_energy_peratom
            (eV/atom), ehull (eV/atom).

Starting point: the textbook Shockley-Queisser heuristic, which orders
candidates by how close the cheap OptB88vdW band gap sits to 1.34 eV. It uses
no training data and ignores stability, so there is room to beat it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SQ_OPTIMUM_EV = 1.34


def rank(train: pd.DataFrame, candidates: pd.DataFrame, seed: int = 0) -> list[str]:
    """Return candidate jids ordered from most to least promising."""
    gap = pd.to_numeric(candidates["optb88vdw_bandgap"], errors="coerce")
    distance = (gap - SQ_OPTIMUM_EV).abs().fillna(np.inf)
    ordered = candidates.assign(_distance=distance).sort_values(
        ["_distance", "jid"], kind="mergesort"
    )
    return ordered["jid"].tolist()
