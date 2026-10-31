#!/usr/bin/env python3
"""Compare the wave speeds in Lanyon's ideal_mhd_1d.rkt with the true eigenvalues
of the flux Jacobian defined in the same specification.

The flux and the listed wave speeds are transcribed by hand from
IdealMHD/specifications/ideal_mhd_1d.rkt (commit beeff1a). The script builds the
exact Jacobian with SymPy, evaluates it at random physical states and reports how
the specification's Lax-Friedrichs speed (amax = largest |listed speed| over the
left and right states) compares with the true spectral radius.

Usage: python3 check_mhd_wavespeeds.py [n_samples] [seed]
"""
import sys
import numpy as np
import sympy as sp

rho, mx, my, mz, Bx, By, Bz, E, g = sp.symbols("rho momx momy momz Bx By Bz energy gas_gamma", real=True)
U = [rho, mx, my, mz, Bx, By, Bz, E]

# Flux exactly as in the specification (x direction).
B2 = Bx**2 + By**2 + Bz**2
p = (g - 1) * (E - (sp.Rational(1, 2) * (mx**2 / rho + my**2 / rho + mz**2 / rho) + sp.Rational(1, 2) * B2))
pstar = p + sp.Rational(1, 2) * B2
F = [
    mx,
    (mx * mx / rho + pstar) - Bx * Bx,
    mx * my / rho - Bx * By,
    mx * mz / rho - Bx * Bz,
    sp.Integer(0),
    By * (mx / rho) - Bx * (my / rho),
    Bz * (mx / rho) - Bx * (mz / rho),
    (E + pstar) * (mx / rho) - Bx * (Bx * (mx / rho) + By * (my / rho) + Bz * (mz / rho)),
]
J = sp.Matrix(F).jacobian(U)
J_num = sp.lambdify((rho, mx, my, mz, Bx, By, Bz, E, g), J, "numpy")


def listed_speeds(r, px, py, pz, bx, by, bz, e, gam):
    """Wave speeds exactly as listed in the specification."""
    u = px / r
    pr = (gam - 1) * (e - (0.5 * (px * px + py * py + pz * pz) / r + 0.5 * (bx * bx + by * by + bz * bz)))
    vA = u - np.sqrt(bx * bx + by * by + bz * bz) / np.sqrt(r)   # as written in the spec
    cs = np.sqrt(gam * pr / r)
    s = vA * vA + cs * cs
    d = np.sqrt(max(s * s - 4 * vA * vA * cs * cs, 0.0))
    fast = np.sqrt(0.5 * (s + d))
    slow = np.sqrt(max(0.5 * (s - d), 0.0))
    return np.array([u - fast, u - slow, u - vA, u, u, u + vA, u + slow, u + fast])


def textbook_speeds(r, px, py, pz, bx, by, bz, e, gam):
    """Standard ideal-MHD characteristic speeds (fast, Alfven, slow, entropy)."""
    u = px / r
    pr = (gam - 1) * (e - (0.5 * (px * px + py * py + pz * pz) / r + 0.5 * (bx * bx + by * by + bz * bz)))
    a2 = gam * pr / r
    b2 = (bx * bx + by * by + bz * bz) / r
    bx2 = bx * bx / r
    disc = np.sqrt(max((a2 + b2) ** 2 - 4 * a2 * bx2, 0.0))
    cf = np.sqrt(0.5 * (a2 + b2 + disc))
    return u, cf


def random_state(rng):
    r = 10 ** rng.uniform(-1, 1)
    u = rng.normal(0, 2.0, 3)
    B = rng.normal(0, 1.5, 3)
    pr = 10 ** rng.uniform(-1, 1)
    gam = rng.choice([5 / 3, 1.4, 2.0])
    e = pr / (gam - 1) + 0.5 * r * (u @ u) + 0.5 * (B @ B)
    return (r, r * u[0], r * u[1], r * u[2], B[0], B[1], B[2], e, gam)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261031
    rng = np.random.default_rng(seed)
    ratios, under, eig_mismatch, textbook_ok = [], 0, 0, 0
    worst = (np.inf, None)
    for _ in range(n):
        sl, sr = random_state(rng), random_state(rng)
        true_rad = 0.0
        for s in (sl, sr):
            ev = np.linalg.eigvals(np.array(J_num(*s), dtype=float))
            true_rad = max(true_rad, np.max(np.abs(ev)))
            u, cf = textbook_speeds(*s)
            # sanity: the textbook fast speed should match the true spectral bound
            if abs(max(abs(u - cf), abs(u + cf)) - np.max(np.abs(ev.real))) < 1e-6 * (1 + abs(u) + cf):
                textbook_ok += 1
            lst = listed_speeds(*s)
            if np.max(np.abs(np.sort(lst) - np.sort(ev.real))) > 1e-6 * (1 + np.max(np.abs(ev))):
                eig_mismatch += 1
        amax = max(np.max(np.abs(listed_speeds(*sl))), np.max(np.abs(listed_speeds(*sr))))
        ratio = amax / true_rad
        ratios.append(ratio)
        if ratio < 1 - 1e-9:
            under += 1
        if ratio < worst[0]:
            worst = (ratio, (sl, sr))
    ratios = np.array(ratios)
    print(f"interfaces sampled: {n} (seed {seed})")
    print(f"states where listed speeds differ from true Jacobian eigenvalues: {eig_mismatch} of {2 * n}")
    print(f"states where textbook fast speed matches the true spectral bound: {textbook_ok} of {2 * n}")
    print(f"interfaces where spec amax < true max |eigenvalue|: {under} of {n} ({100 * under / n:.1f}%)")
    print(f"ratio amax / true: min {ratios.min():.3f}, 1st pct {np.percentile(ratios, 1):.3f}, median {np.median(ratios):.3f}")
    print("worst case (rho, momx, momy, momz, Bx, By, Bz, energy, gamma), left then right:")
    for s in worst[1]:
        print("  ", tuple(round(float(x), 4) for x in s))


if __name__ == "__main__":
    main()
