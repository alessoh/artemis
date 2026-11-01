"""Aimed primitive search: each failing family is sampled at its derived weak spot.

search(info, kit, seed) reads the spec name and direction d from info and picks a branch.
For the four families with a known flaw it draws about 300 seeded candidates from
primitive variables in a target region, converts them to the conserved state by the
variable names in info["state"] / info["parameters"] (left state = right state), keeps
those inside the box (kit.in_box) and evaluates them; it then coordinate-descends the 5
best in log-magnitude (multiplicative steps on each nonzero value, zeros stay zero,
right state tied to left) with the remaining budget. Every other family, or a branch
that yields fewer than 5 admissible candidates, uses the pre-registered baseline sampler.

Target regions (u_d = velocity along d, b = |B|/sqrt(rho)):
- ideal_mhd: rho log-uniform [0.1, 10]; |B| <= 3 in a random direction; u_d = s b with
  s ~ U[0.8, 1.2], transverse velocity 0; p = q |B|^2 with q log-uniform [1e-8, 1e-3];
  gas_gamma ~ U(1.01, 10]. The listed "Alfven" speed is u - b, so amax = |u| + max(|u - b|, cs)
  ~ b at u = b, while the true fast speed is u + c_f >= 2b: ratio -> 1/2.
- hyperbolic_ideal_mhd: momentum 0; B = 0 with probability 1/2, else |B| log-uniform
  [1e-2, 0.1]; rho log-uniform [1, 10]; energy ~ U[0.01, 0.1]; gas_gamma ~ U(1.01, 2];
  chi ~ U[0.9, 1]; psi random. The GLM speeds +-chi are listed but left out of amax,
  so the ratio -> cs / chi.
- hyperbolic_maxwell: c ~ U[5, 10]; chi or gamma (one at random) = c U[0.9, 1], the other
  log-uniform up to c; random nonzero fields. amax = |c| omits c chi and c gamma.
- gr_(hyperbolic_)maxwell: c ~ U[5, 10]; alpha log-uniform [1e-2, 0.1]; beta_d = +-U[5, 10],
  transverse shift 0; one nonzero transverse D. The true transverse speed is ~ c^2 |beta_d|,
  the listed one alpha c + |beta_d|.
"""
import math

import numpy as np

LO = 0.01   # smallest nonzero magnitude in the box
HI = 10.0   # largest magnitude in the box
N_CAND = 300
N_START = 5


def _logu(rng, a, b):
    return float(math.exp(rng.uniform(math.log(a), math.log(b))))


def _snap(v):
    return 0.0 if abs(v) < LO else float(v)


def _unit(rng):
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)


def _ideal_mhd(rng, d, hyper):
    """Primitive draw -> dict of conserved values by name."""
    ax = "xyz"
    if hyper:
        rho = _logu(rng, 1.0, HI)
        B = np.zeros(3) if rng.random() < 0.5 else _logu(rng, LO, 0.1) * _unit(rng)
        B = np.array([_snap(x) for x in B])
        g = float(rng.uniform(1.01, 2.0))
        E = float(rng.uniform(LO, 0.1))
        out = {"rho": rho, "energy": E, "psi": _snap(_logu(rng, LO, HI) * rng.choice([-1.0, 1.0])),
               "gas_gamma": g, "chi": float(rng.uniform(0.9, 1.0))}
        for i in range(3):
            out["mom" + ax[i]] = 0.0
            out["B" + ax[i]] = float(B[i])
        return out
    rho = _logu(rng, 0.1, HI)
    B = rng.uniform(0.0, 3.0) * _unit(rng)
    B = np.array([_snap(x) for x in B])
    B2 = float(B @ B)
    b = math.sqrt(B2 / rho)
    u = np.zeros(3)
    u[d] = rng.uniform(0.8, 1.2) * b
    p = _logu(rng, 1e-8, 1e-3) * B2
    g = float(rng.uniform(1.01, HI))
    out = {"rho": rho, "gas_gamma": g,
           "energy": p / (g - 1.0) + 0.5 * rho * float(u @ u) + 0.5 * B2}
    for i in range(3):
        out["mom" + ax[i]] = _snap(rho * u[i])
        out["B" + ax[i]] = float(B[i])
    return out


def _hyp_maxwell(rng, d):
    c = float(rng.uniform(5.0, HI))
    big = c * float(rng.uniform(0.9, 1.0))
    other = _logu(rng, LO, c)
    out = {"c": c}
    if rng.random() < 0.5:
        out["chi"], out["gamma"] = big, other
    else:
        out["chi"], out["gamma"] = other, big
    for n in ("Ex", "Ey", "Ez", "Bx", "By", "Bz", "phi", "psi"):
        out[n] = _logu(rng, LO, HI) * float(rng.choice([-1.0, 1.0]))
    return out


def _gr_maxwell(rng, d):
    ax = "xyz"
    c = float(rng.uniform(5.0, HI))
    out = {"c": c, "alpha": _logu(rng, LO, 0.1), "chi": _logu(rng, LO, c), "gamma": _logu(rng, LO, c)}
    for i in range(3):
        out["D" + ax[i]] = 0.0
        out["B" + ax[i]] = 0.0
        out["beta_" + ax[i]] = 0.0
    out["beta_" + ax[d]] = float(rng.uniform(5.0, HI)) * float(rng.choice([-1.0, 1.0]))
    t = [i for i in range(3) if i != d]
    out["D" + ax[t[int(rng.integers(2))]]] = _logu(rng, LO, HI) * float(rng.choice([-1.0, 1.0]))
    out["phi"] = 0.0
    out["psi"] = 0.0
    return out


def _branch(info):
    s = info["spec"]
    if s.startswith("hyperbolic_ideal_mhd"):
        return lambda rng, d: _ideal_mhd(rng, d, True)
    if s.startswith("ideal_mhd"):
        return lambda rng, d: _ideal_mhd(rng, d, False)
    if s.startswith("hyperbolic_maxwell"):
        return _hyp_maxwell
    if s.startswith("gr_maxwell") or s.startswith("gr_hyperbolic_maxwell"):
        return _gr_maxwell
    return None


def _to_point(info, vals, rng):
    """Map named values to a point; any unnamed variable gets 0 (coordinates random)."""
    if any(n not in vals for n in info["state"] + info["parameters"]):
        return None
    L = [float(vals[n]) for n in info["state"]]
    P = [float(vals[n]) for n in info["parameters"]]
    X = [_logu(rng, LO, HI) * float(rng.choice([-1.0, 1.0])) for _ in info["coordinates"]]
    return {"L": L, "R": list(L), "P": P, "X": X}


def _baseline(kit, rng, found):
    tries = 0
    while kit.remaining() > 0 and tries < 400_000:
        tries += 1
        p = kit.sample(rng)
        r = kit.evaluate(p)
        if r is not None:
            found.append((r["ratio"], p))


def _descend(kit, point, ratio, found):
    """Coordinate descent on log|v| of the tied state L=R and the parameters."""
    nS = len(point["L"])
    vec = list(point["L"]) + list(point["P"])

    def make(v):
        return {"L": v[:nS], "R": v[:nS], "P": v[nS:], "X": point["X"]}

    best = ratio
    h = 0.5
    while h > 1e-4 and kit.remaining() > 0:
        improved = False
        for i in range(len(vec)):
            if vec[i] == 0.0:
                continue
            for sgn in (1.0, -1.0):
                if kit.remaining() <= 0:
                    break
                v = list(vec)
                v[i] = vec[i] * math.exp(sgn * h)
                p = make(v)
                if not kit.in_box(p):
                    continue
                r = kit.evaluate(p)
                if r is not None and r["ratio"] < best:
                    best, vec, improved = r["ratio"], v, True
                    found.append((best, p))
                    break
        if not improved:
            h *= 0.5
    return best


def search(info, kit, seed):
    rng = np.random.default_rng(seed)
    found = []
    draw = _branch(info)
    d = info["coordinates"].index(info["direction"])
    if draw is not None:
        cands = []
        tries = 0
        while len(cands) < N_CAND and tries < 20 * N_CAND and kit.remaining() > 0:
            tries += 1
            p = _to_point(info, draw(rng, d), rng)
            if p is None:
                break
            if not kit.in_box(p):
                continue
            r = kit.evaluate(p)
            if r is not None:
                cands.append((r["ratio"], len(cands), p))
        if len(cands) >= N_START:
            cands.sort(key=lambda t: (t[0], t[1]))
            found += [(q, p) for q, _, p in cands]
            starts = cands[:N_START]
            for k, (q, _, p) in enumerate(starts):
                share = kit.remaining() // (N_START - k)
                stop = kit.remaining() - share
                kit_budget = _Budget(kit, stop)
                _descend(kit_budget, p, q, found)
        else:
            found += [(q, p) for q, _, p in cands]
    _baseline(kit, rng, found)
    found.sort(key=lambda item: item[0])
    return [p for _, p in found[:20]]


class _Budget:
    """Caps the calls one descent may use (stops when the kit has `stop` calls left)."""

    def __init__(self, kit, stop):
        self.kit = kit
        self.stop = stop

    def remaining(self):
        return max(0, self.kit.remaining() - self.stop)

    def in_box(self, p):
        return self.kit.in_box(p)

    def evaluate(self, p):
        if self.remaining() <= 0:
            return None
        return self.kit.evaluate(p)
