"""Build the frozen datasets for Artemis Project 2 (choosing alpha without labels).

Run once by the humans; agents never run it.

    python lab/unccd_alpha/prepare_data.py dev-val          # writes data/dev.npz, data/val.npz, manifest
    python lab/unccd_alpha/prepare_data.py test --seed-file PATH --out DIR
                                                          # the sealed test split, built after the run

The simulated data follow the paper's design (arXiv:2501.06268v3, Section 4,
and the authors' generator R/general_functions/Uni-Gau_cls.R):

* Uniform clusters: points uniform in a ball of radius r ~ U(0.8, 1.2) around
  each centre. Gaussian clusters: N(centre, r^2 I) with r ~ U(0.8, 1.2) (the
  authors' code; the paper's text says Delta ~ U(0.8, 1.2)).
* Centres (the paper's layout): mu1 = (3, ..., 3), mu2 = mu1 + c e1,
  mu3 = mu1 + c e1 + c e2, mu4 = mu1 + (c - 0.5) e2, mu5 = mu1 + (2c - 0.5) e1,
  with c = 3 for uniform and c = 6 for Gaussian clusters (the authors' drivers).
* Cluster sizes: round(n / k) each, the first one less for k = 3 (as the drivers).
* Noise (Section 4.3): round(l * n) extra points uniform over the bounding box
  of the cluster points, widened by 10 percent on each side; labelled -1. The
  paper's noise layout is three Gaussian clusters at mu1, mu1 + 6 e1, mu1 + 6 e2.

The held-out test regimes change what the dev and val splits never show:
dimensions 4, 7 and 15; sizes 30, 300 and 700; 2, 4 or 6 clusters; noise up to
30 percent; and new centres, placed by a random walk at distances c * U(0.85,
1.15) from an existing centre and at least 0.8 c from every other. The list of
test regimes is fixed by a public seed; the datasets themselves are drawn from
a secret seed whose SHA-256 is published in program.md before the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))
import nulls  # noqa: E402

DEV_SEED = 20261015_01
VAL_SEED = 20261015_02
TEST_REGIME_SEED = 20261015_03          # public: which regimes are in the test split
SEP = {"uniform": 3.0, "gaussian": 6.0}


# ---------------------------------------------------------------- generators
def uniform_ball(rng, n, d):
    return nulls.uniform_ball(rng, n, d)


def paper_centres(dist: str, d: int, k: int) -> np.ndarray:
    c = SEP[dist]
    base = np.full(d, 3.0)
    e = np.eye(d)
    mus = [base, base + c * e[0], base + c * e[0] + c * e[1], base + (c - 0.5) * e[1],
           base + (2 * c - 0.5) * e[0]]
    order = {2: [0, 1], 3: [0, 1, 2], 5: [0, 1, 2, 3, 4]}[k]
    return np.array([mus[i] for i in order])


def noise_layout_centres(d: int) -> np.ndarray:
    base = np.full(d, 3.0)
    e = np.eye(d)
    return np.array([base, base + 6 * e[0], base + 6 * e[1]])


def paper_sizes(n: int, k: int) -> list[int]:
    m = int(round(n / k))
    sizes = [m] * k
    if k == 3:
        sizes[0] = m - 1
    return sizes


def random_centres(rng, dist: str, d: int, k: int) -> np.ndarray:
    c = SEP[dist]
    for _attempt in range(10_000):
        centres = [np.full(d, 3.0)]
        ok = True
        while len(centres) < k:
            for _try in range(500):
                anchor = centres[rng.integers(len(centres))]
                u = rng.standard_normal(d)
                u /= np.linalg.norm(u)
                cand = anchor + c * rng.uniform(0.85, 1.15) * u
                if min(np.linalg.norm(cand - x) for x in centres) >= 0.8 * c:
                    centres.append(cand)
                    break
            else:
                ok = False
                break
        if ok:
            return np.array(centres)
    raise RuntimeError("could not place the centres")


def make_dataset(rng, dist: str, d: int, centres: np.ndarray, sizes: list[int], noise: float):
    parts, labels = [], []
    for j, (mu, m) in enumerate(zip(centres, sizes)):
        r = rng.uniform(0.8, 1.2)
        if dist == "uniform":
            pts = uniform_ball(rng, m, d) * r + mu
        else:
            pts = mu + r * rng.standard_normal((m, d))
        parts.append(pts)
        labels.append(np.full(m, j))
    X = np.vstack(parts)
    y = np.concatenate(labels)
    if noise > 0:
        m = int(round(noise * len(X)))
        lo, hi = X.min(axis=0), X.max(axis=0)
        pad = 0.1 * (hi - lo)
        Z = rng.uniform(lo - pad, hi + pad, size=(m, d))
        X = np.vstack([X, Z])
        y = np.concatenate([y, np.full(m, -1)])
    perm = rng.permutation(len(X))                # no information in the row order
    return X[perm], y[perm]


# ---------------------------------------------------------------- regimes
def dev_val_regimes(split: str) -> list[dict]:
    sizes = {"dev": (100,), "val": (50, 200)}[split]
    out = []
    for dist in ("uniform", "gaussian"):
        for d in (2, 3, 5, 10, 20):
            for n in sizes:
                for k in (2, 3, 5):
                    out.append({"dist": dist, "d": d, "n": n, "k": k, "noise": 0.0, "layout": "paper"})
    noise_levels = {"dev": (0.10,), "val": (0.05, 0.20)}[split]
    for d in (3, 10):
        for l in noise_levels:
            out.append({"dist": "gaussian", "d": d, "n": 200, "k": 3, "noise": l, "layout": "noise"})
    return out


def test_regimes() -> list[dict]:
    """45 regimes: for each dimension and size, 5 of the 18 combinations of
    distribution, number of clusters and noise level, drawn with a public seed."""
    rng = np.random.default_rng(TEST_REGIME_SEED)
    out = []
    for d in (4, 7, 15):
        for n in (30, 300, 700):
            combos = [{"dist": dist, "d": d, "n": n, "k": k, "noise": l, "layout": "random"}
                      for dist in ("uniform", "gaussian") for k in (2, 4, 6) for l in (0.0, 0.1, 0.3)]
            pick = sorted(rng.choice(len(combos), size=5, replace=False).tolist())
            out.extend(combos[i] for i in pick)
    return out


def build_split(regimes: list[dict], seed: int, reps: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    X_list, y_list, meta = [], [], []
    for i, reg in enumerate(regimes):
        for rep in range(reps):
            if reg["layout"] == "paper":
                centres, sizes = paper_centres(reg["dist"], reg["d"], reg["k"]), paper_sizes(reg["n"], reg["k"])
            elif reg["layout"] == "noise":
                centres, sizes = noise_layout_centres(reg["d"]), [int(round(reg["n"] / 3))] * 3
            else:
                centres = random_centres(rng, reg["dist"], reg["d"], reg["k"])
                sizes = [int(round(reg["n"] / reg["k"]))] * reg["k"]
            X, y = make_dataset(rng, reg["dist"], reg["d"], centres, sizes, reg["noise"])
            X_list.append(X)
            y_list.append(y)
            meta.append({**reg, "regime": i, "rep": rep, "n_points": int(len(X))})
    return {"X": X_list, "y": y_list, "meta": meta}


def save_split(split: dict, path: Path) -> None:
    arrays = {}
    for i, (X, y) in enumerate(zip(split["X"], split["y"])):
        arrays[f"X{i}"] = X
        arrays[f"y{i}"] = y
    np.savez_compressed(path, meta=json.dumps(split["meta"]), **arrays)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_manifest() -> dict:
    files = sorted([p for p in DATA.rglob("*") if p.is_file() and p.name != "manifest.json"])
    manifest = {"sha256": {str(p.relative_to(DATA)): sha256_file(p) for p in files},
                "alphas": list(nulls.ALPHAS), "null_iterations": nulls.NITER}
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


# ---------------------------------------------------------------- real held-out data
REAL_TEST = {
    # name: (file, separator, feature columns, label column, standardise) as in the authors' loader
    "aggregation": ("aggregation.txt", None, (0, 1), 2, False),
    "compound": ("compound.txt", None, (0, 1), 2, False),
    "jain": ("jain.txt", None, (0, 1), 2, False),
    "glass": ("glass.txt", ",", tuple(range(1, 10)), 10, False),
    "yeast": ("yeast.data", None, tuple(range(1, 9)), 9, True),
}


def load_real(folder: Path) -> dict:
    """The five held-out real datasets, from the authors' repository's data folder.

    Preprocessing follows the authors' loader (Real_Data_Collection_full.R):
    yeast is standardised column by column, the others are used as they are.
    Rows with identical features are removed, keeping the first, so that no
    two points coincide (the authors remove rows identical in features and
    label).
    """
    out = {}
    for name, (fname, sep, cols, ycol, scale) in REAL_TEST.items():
        rows = []
        for line in (folder / fname).read_text().splitlines():
            if not line.strip():
                continue
            parts = line.split(sep) if sep else line.split()
            rows.append(parts)
        X = np.array([[float(r[c]) for c in cols] for r in rows])
        labels = [r[ycol].strip() for r in rows]
        _, y = np.unique(labels, return_inverse=True)
        if scale:
            X = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
        _, keep = np.unique(X, axis=0, return_index=True)
        keep = np.sort(keep)
        out[name] = (X[keep], y[keep])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["dev-val", "test", "manifest"])
    ap.add_argument("--seed-file", type=str, default="")
    ap.add_argument("--out", type=str, default="")
    ap.add_argument("--real-folder", type=str, default=str(HERE.parent / "unccd" / "vendor" / "ccd" / "data" / "clustering"))
    a = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    if a.what == "dev-val":
        for split, seed in (("dev", DEV_SEED), ("val", VAL_SEED)):
            s = build_split(dev_val_regimes(split), seed)
            save_split(s, DATA / f"{split}.npz")
            print(f"{split}: {len(s['meta'])} datasets")
        m = write_manifest()
        print(f"manifest: {len(m['sha256'])} files")
    elif a.what == "manifest":
        m = write_manifest()
        print(f"manifest: {len(m['sha256'])} files")
    else:
        seed = int(Path(a.seed_file).read_text().strip())
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        s = build_split(test_regimes(), seed, reps=2)
        save_split(s, out / "test_synthetic.npz")
        real = load_real(Path(a.real_folder))
        save_split({"X": [v[0] for v in real.values()], "y": [v[1] for v in real.values()],
                    "meta": [{"name": k, "n_points": int(len(v[0])), "d": int(v[0].shape[1]),
                              "k": int(len(np.unique(v[1]))), "noise": 0.0} for k, v in real.items()]},
                   out / "test_real.npz")
        print(f"test: {len(s['meta'])} synthetic datasets, {len(real)} real datasets in {out}")


if __name__ == "__main__":
    main()
