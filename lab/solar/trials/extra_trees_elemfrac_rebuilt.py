"""Reconstruction of the lab's final model, extra_trees_elemfrac (commit 01352a9).

The original file existed only in the lab's sandbox, which was deleted when the
run was stopped. This version is rebuilt by Claude from the description in the
Scribe's report (Section 4) and is NOT byte-identical to the original; its
numbers are reported separately from the lab's.

Step 1: candidates with energy above hull <= 0.1 eV/atom go first.
Step 2: within each group, order by SLME predicted by an ExtraTrees regressor
(500 trees, at least 2 samples per leaf) trained on the train split, using
cheap DFT columns, composition-weighted Pauling electronegativity (mean and
max-min spread), chalcogen, heavier-halide and oxygen fractions, and the atomic
fraction of every element seen in train. Missing values are -1.

Pauling electronegativities are pymatgen's table
(github.com/materialsproject/pymatgen, dev_scripts/periodic_table_resources/
_periodic_table.yaml, key "X", commit 8461938).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor

STABLE_EHULL_EV = 0.1
NUMERIC = ["optb88vdw_bandgap", "formation_energy_peratom", "ehull", "n_elements", "nat",
           "spg_number", "density", "volume_per_atom"]
CHALCOGENS = ("S", "Se", "Te")
HALIDES = ("Cl", "Br", "I")
PAULING = {"Ac": 1.1, "Ag": 1.93, "Al": 1.61, "Am": 1.3, "As": 2.18, "At": 2.2, "Au": 2.54, "B": 2.04, "Ba": 0.89, "Be": 1.57, "Bi": 2.02, "Bk": 1.3, "Br": 2.96, "C": 2.55, "Ca": 1.0, "Cd": 1.69, "Ce": 1.12, "Cf": 1.3, "Cl": 3.16, "Cm": 1.3, "Co": 1.88, "Cr": 1.66, "Cs": 0.79, "Cu": 1.9, "Dy": 1.22, "Er": 1.24, "Es": 1.3, "Eu": 1.2, "F": 3.98, "Fe": 1.83, "Fm": 1.3, "Fr": 0.7, "Ga": 1.81, "Gd": 1.2, "Ge": 2.01, "H": 2.2, "Hf": 1.3, "Hg": 2.0, "Ho": 1.23, "I": 2.66, "In": 1.78, "Ir": 2.2, "K": 0.82, "Kr": 3.0, "La": 1.1, "Li": 0.98, "Lr": 1.3, "Lu": 1.27, "Md": 1.3, "Mg": 1.31, "Mn": 1.55, "Mo": 2.16, "N": 3.04, "Na": 0.93, "Nb": 1.6, "Nd": 1.14, "Ni": 1.91, "Np": 1.36, "O": 3.44, "Os": 2.2, "P": 2.19, "Pa": 1.5, "Pb": 2.33, "Pd": 2.2, "Pm": 1.13, "Po": 2.0, "Pr": 1.13, "Pt": 2.28, "Pu": 1.28, "Ra": 0.9, "Rb": 0.82, "Re": 1.9, "Rh": 2.28, "Rn": 2.2, "Ru": 2.2, "S": 2.58, "Sb": 2.05, "Sc": 1.36, "Se": 2.55, "Si": 1.9, "Sm": 1.17, "Sn": 1.96, "Sr": 0.95, "Ta": 1.5, "Tb": 1.1, "Tc": 1.9, "Te": 2.1, "Th": 1.3, "Ti": 1.54, "Tl": 1.62, "Tm": 1.25, "U": 1.38, "V": 1.63, "W": 2.36, "Xe": 2.6, "Y": 1.22, "Yb": 1.1, "Zn": 1.65, "Zr": 1.33, "false": 1.3}


def parse_composition(text: str) -> dict[str, float]:
    """Turn 'Cu:2 S:4 Sn:1 Zn:2' into atomic fractions."""
    counts: dict[str, float] = {}
    for token in str(text or "").split():
        element, _, count = token.partition(":")
        try:
            counts[element] = counts.get(element, 0.0) + float(count)
        except ValueError:
            continue
    total = sum(counts.values())
    return {e: c / total for e, c in counts.items()} if total else {}


def featurize(frame: pd.DataFrame, elements: list[str]) -> np.ndarray:
    """Cheap DFT columns plus composition features, missing values as -1."""
    base = frame[NUMERIC].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    extra = np.full((len(frame), 5 + len(elements)), 0.0)
    index = {e: i for i, e in enumerate(elements)}
    for row, text in enumerate(frame["composition"].tolist()):
        fractions = parse_composition(text)
        known = {e: f for e, f in fractions.items() if e in PAULING}
        weight = sum(known.values())
        if weight:
            mean = sum(PAULING[e] * f for e, f in known.items()) / weight
            values = [PAULING[e] for e in known]
            extra[row, 0] = mean
            extra[row, 1] = max(values) - min(values)
        else:
            extra[row, 0] = extra[row, 1] = -1.0
        extra[row, 2] = sum(fractions.get(e, 0.0) for e in CHALCOGENS)
        extra[row, 3] = sum(fractions.get(e, 0.0) for e in HALIDES)
        extra[row, 4] = fractions.get("O", 0.0)
        for element, fraction in fractions.items():
            if element in index:
                extra[row, 5 + index[element]] = fraction
    features = np.hstack([base, extra])
    features[~np.isfinite(features)] = -1.0
    return features


def rank(train: pd.DataFrame, candidates: pd.DataFrame, seed: int = 0) -> list[str]:
    """Return candidate jids, near-stable first, each group by predicted SLME."""
    labeled = train[pd.to_numeric(train["slme"], errors="coerce").notna()]
    elements = sorted({e for text in labeled["composition"] for e in parse_composition(text)})
    model = ExtraTreesRegressor(n_estimators=500, min_samples_leaf=2, random_state=seed, n_jobs=-1)
    model.fit(featurize(labeled, elements), pd.to_numeric(labeled["slme"]).to_numpy(dtype=float))
    predicted = model.predict(featurize(candidates, elements))
    ehull = pd.to_numeric(candidates["ehull"], errors="coerce")
    unstable = (~(ehull <= STABLE_EHULL_EV)).astype(int).to_numpy()
    ordered = candidates.assign(_unstable=unstable, _score=-predicted).sort_values(
        ["_unstable", "_score", "jid"], kind="mergesort")
    return ordered["jid"].drop_duplicates().tolist()
