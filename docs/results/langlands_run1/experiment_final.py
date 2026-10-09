"""Trial additive_legendre_mod4: shape_empirical_bayes with additive p >= 5
tokens split by p mod 4.

Trial change vs. the parent: every token with p >= 5 and e == 2 (additive)
carries an extra field p % 4 (1 or 3), in both the shape and the pattern;
all other tokens carry a fixed placeholder. Hypothesis: the only arithmetic
in the mod-12 split is (-1/p) (Rohrlich: w_p = (-1/p) for I0*, In*, II, II*),
so a -1 at additive p = 1 mod 4 flags the rarer types III/III*/IV/IV*.

Parent docstring follows.

score(train, rows, seed) returns one number per row in `rows`; a higher number
means "more likely rank 2". Each row is {"N": conductor, "bad": [[p, e, w_p],
...]} where p runs over the primes dividing N, e is the exponent of p in N
and w_p is the local root number (+1 or -1). `train` holds the same fields
plus "rank" (0 or 2) for every class with a smaller conductor.

The harness compares only classes that share a conductor, so a score helps
only through what it does with the signs w_p.

Base rule r: the number of bad primes p >= 5 with w_p = -1 minus the number
of bad primes p in {2, 3} with w_p = -1, every exponent.

Change: each bad prime becomes a token (size class of p in {2}, {3}, 5-97,
>= 101; min(e, 2); w_p). A class's sign pattern is the sorted tuple of its
tokens and its conductor shape is the same tuple without the signs (all
classes of one conductor share a shape). From train, using only conductors
that have both ranks, each pattern gets a rank-2 log-odds
log((n2 + 0.5) / (n0 + 0.5)) centred on the class-weighted mean of its
shape (est). The score is r + n/(n+K) * (c*est - (r - mean r of the shape)),
with c = 1/slope of a weighted fit of est on centred r, n = n2 + n0; unseen
patterns keep r. K in {10, 30, 100, 300} is chosen by fitting on train
conductors below 2/3 of the largest train N and measuring within-conductor
AUC on the rest; then the table is refit on all of train. Gate: if the best
internal AUC does not beat r's internal AUC by at least 0.002, the score is
r unchanged. Deterministic; the seed is ignored.
Hypothesis: the effect of a -1 sign at p >= 5 depends on which other local
types share the conductor, which only a shape-conditioned table captures.
"""

import math
from bisect import bisect_left, bisect_right
from collections import defaultdict

KS = (10.0, 30.0, 100.0, 300.0)
GATE = 0.002


def base_r(bad):
    s = 0
    for p, e, w in bad:
        if w == -1:
            s += 1 if p >= 5 else -1
    return float(s)


def size_class(p):
    if p == 2:
        return 0
    if p == 3:
        return 1
    if p <= 97:
        return 2
    return 3


def keys(bad):
    toks = sorted((size_class(p), min(e, 2),
                   (p % 4) if (p >= 5 and e == 2) else -1, w)
                  for p, e, w in bad)
    pattern = tuple(toks)
    shape = tuple((a, b, m) for a, b, m, c in toks)
    return shape, pattern


def fit_table(classes):
    """classes: list of (N, shape, pattern, r, rank). Returns model dict."""
    by_n = defaultdict(set)
    for N, sh, pa, r, rk in classes:
        by_n[N].add(rk)
    both = set(N for N, s in by_n.items() if len(s) == 2)
    cnt = defaultdict(lambda: [0, 0])
    rval = {}
    for N, sh, pa, r, rk in classes:
        if N not in both:
            continue
        c = cnt[(sh, pa)]
        if rk == 2:
            c[1] += 1
        else:
            c[0] += 1
        rval[(sh, pa)] = r
    # shape means of log-odds and r (class weighted)
    sw = defaultdict(float)
    slo = defaultdict(float)
    sr = defaultdict(float)
    lo = {}
    for key, (n0, n2) in cnt.items():
        sh = key[0]
        n = n0 + n2
        v = math.log((n2 + 0.5) / (n0 + 0.5))
        lo[key] = v
        sw[sh] += n
        slo[sh] += n * v
        sr[sh] += n * rval[key]
    est = {}
    rc = {}
    wts = {}
    for key, v in lo.items():
        sh = key[0]
        est[key] = v - slo[sh] / sw[sh]
        rc[key] = rval[key] - sr[sh] / sw[sh]
        wts[key] = float(sum(cnt[key]))
    # weighted least squares of est on centred r (both already centred per shape)
    sxy = sum(wts[k] * rc[k] * est[k] for k in est)
    sxx = sum(wts[k] * rc[k] * rc[k] for k in est)
    syy = sum(wts[k] * est[k] * est[k] for k in est)
    slope = sxy / sxx if sxx > 0 else 0.0
    if slope > 1e-9:
        c = 1.0 / slope
    elif syy > 0 and sxx > 0:
        c = math.sqrt(sxx / syy)
    else:
        c = 0.0
    rbar = dict((sh, sr[sh] / sw[sh]) for sh in sw)
    return {"est": est, "n": wts, "c": c, "rbar": rbar}


def apply_model(model, sh, pa, r, K):
    key = (sh, pa)
    if key not in model["est"]:
        return r
    n = model["n"][key]
    lam = n / (n + K)
    rcen = r - model["rbar"][sh]
    return r + lam * (model["c"] * model["est"][key] - rcen)


def within_auc(items):
    """items: list of (N, score, rank). Pooled within-conductor AUC."""
    by_n = defaultdict(lambda: ([], []))
    for N, s, rk in items:
        if rk == 2:
            by_n[N][1].append(s)
        else:
            by_n[N][0].append(s)
    num = 0.0
    den = 0.0
    for N, (s0, s2) in by_n.items():
        if not s0 or not s2:
            continue
        s0.sort()
        n0 = len(s0)
        for x in s2:
            lo_i = bisect_left(s0, x)
            hi_i = bisect_right(s0, x)
            num += lo_i + 0.5 * (hi_i - lo_i)
        den += n0 * len(s2)
    return num / den if den > 0 else 0.5


def score(train, rows, seed):
    """Shape-conditioned empirical-Bayes log-odds shrunk toward r, gated."""
    classes = []
    for t in train:
        sh, pa = keys(t["bad"])
        classes.append((t["N"], sh, pa, base_r(t["bad"]), t["rank"]))
    rs = [base_r(row["bad"]) for row in rows]
    if not classes:
        return rs
    maxn = max(c[0] for c in classes)
    split = maxn * 2.0 / 3.0
    fit_part = [c for c in classes if c[0] < split]
    hold = [c for c in classes if c[0] >= split]
    model = fit_table(fit_part)
    base_auc = within_auc([(c[0], c[3], c[4]) for c in hold])
    best_k = None
    best_auc = -1.0
    for K in KS:
        a = within_auc([(c[0], apply_model(model, c[1], c[2], c[3], K), c[4])
                        for c in hold])
        if a > best_auc:
            best_auc = a
            best_k = K
    if best_auc < base_auc + GATE:
        return rs
    model = fit_table(classes)
    out = []
    for row, r in zip(rows, rs):
        sh, pa = keys(row["bad"])
        out.append(float(apply_model(model, sh, pa, r, best_k)))
    return out
