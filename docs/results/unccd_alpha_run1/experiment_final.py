"""Null-calibrated silhouette: choose the alpha whose silhouette most exceeds its no-structure expectation.

For each alpha on the grid, UN-CCD is run with the ascending radius search and
gives a clustering with k clusters and mean silhouette s. The silhouette tends
to be high for small k even when there is no structure, so it is compared with
a reference: five samples of n points drawn from a single Gaussian with the
same mean and covariance as X, each split into k groups by k-means, give the
average silhouette s0(k) that k clusters reach on structureless data. The rule
chooses the alpha with the largest s - s0(k); ties go to the smaller alpha.
Clusterings with one cluster (or one cluster per point) are never chosen,
unless every alpha gives a single cluster, in which case the plain largest
silhouette is used. Only the unlabelled data and the seed are used.
"""
import numpy as np
from sklearn.metrics import silhouette_score

B = 5


def kmeans(R, k, n_init, rng, max_iter=100):
    """Plain k-means (k-means++ seeding, Lloyd iterations), best of n_init by inertia.

    Written in NumPy because sklearn's KMeans probes the thread pool by reading
    /proc, which the harness sandbox forbids.
    """
    n = R.shape[0]
    sq = (R * R).sum(axis=1)
    best_lab, best_inertia = None, np.inf
    for _ in range(n_init):
        centers = [R[rng.integers(n)]]
        d2 = ((R - centers[0]) ** 2).sum(axis=1)
        for _ in range(1, k):
            tot = d2.sum()
            idx = rng.integers(n) if tot <= 0 else rng.choice(n, p=d2 / tot)
            centers.append(R[idx])
            d2 = np.minimum(d2, ((R - R[idx]) ** 2).sum(axis=1))
        C = np.array(centers)
        lab = None
        for _ in range(max_iter):
            D = sq[:, None] - 2.0 * R @ C.T + (C * C).sum(axis=1)[None, :]
            new = D.argmin(axis=1)
            if lab is not None and np.array_equal(new, lab):
                break
            lab = new
            for j in range(k):
                m = lab == j
                if m.any():
                    C[j] = R[m].mean(axis=0)
        D = sq[:, None] - 2.0 * R @ C.T + (C * C).sum(axis=1)[None, :]
        lab = D.argmin(axis=1)
        inertia = float(D[np.arange(n), lab].sum())
        if inertia < best_inertia:
            best_lab, best_inertia = lab, inertia
    return best_lab


def choose(X, kit, seed):
    X = np.asarray(X, dtype=float)
    n, d = X.shape
    results = []
    for alpha in kit.alphas:
        r = kit.cluster(alpha, "ascend")
        results.append((alpha, int(r["clusters"]), float(r["silhouette"])))

    ks = sorted({k for _, k, _ in results if 2 <= k < n})
    if not ks:
        best_alpha, best_value = kit.alphas[0], -np.inf
        for alpha, k, s in results:
            if s > best_value:
                best_alpha, best_value = alpha, s
        return {"alpha": best_alpha, "direction": "ascend"}

    rng = np.random.default_rng(seed)
    mean = X.mean(axis=0)
    cov = np.atleast_2d(np.cov(X.T)) + 1e-9 * np.eye(d)
    L = np.linalg.cholesky(cov)
    refs = [mean + rng.standard_normal((n, d)) @ L.T for _ in range(B)]

    s0 = {}
    for k in ks:
        vals = []
        for R in refs:
            lab = kmeans(R, k, 3, np.random.default_rng(seed))
            if len(np.unique(lab)) < 2:
                vals.append(0.0)
            else:
                vals.append(float(silhouette_score(R, lab)))
        s0[k] = float(np.mean(vals))

    best_alpha, best_value = kit.alphas[0], -np.inf
    for alpha, k, s in results:
        if k < 2 or k >= n:
            continue
        value = s - s0[k]
        if value > best_value:
            best_alpha, best_value = alpha, value
    return {"alpha": best_alpha, "direction": "ascend"}
