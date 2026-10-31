#!/usr/bin/env python3
"""First-order Rusanov (local Lax-Friedrichs) runs of 1D ideal MHD using the flux of
Lanyon's ideal_mhd_1d.rkt, with two choices of the dissipation speed amax:
  'spec'     : the specification's wave-speed formula (as in the C kernel)
  'textbook' : the standard fast magnetosonic speed |u| + c_f
The time step uses CFL * dx / max(amax) computed with the same speed the scheme uses,
as a driver built on the kernels would. Reports positivity failures and blow-up.

Usage: python3 briowu_probe.py
"""
import numpy as np

G = 2.0  # Brio-Wu adiabatic index


def prim_to_cons(r, u, v, w, bx, by, bz, p, g):
    e = p / (g - 1) + 0.5 * r * (u * u + v * v + w * w) + 0.5 * (bx * bx + by * by + bz * bz)
    return np.array([r, r * u, r * v, r * w, bx, by, bz, e])


def pressure(U, g):
    r, mx, my, mz, bx, by, bz, e = U
    return (g - 1) * (e - 0.5 * (mx * mx + my * my + mz * mz) / r - 0.5 * (bx * bx + by * by + bz * bz))


def flux(U, g):
    r, mx, my, mz, bx, by, bz, e = U
    p = pressure(U, g)
    ps = p + 0.5 * (bx * bx + by * by + bz * bz)
    u, v, w = mx / r, my / r, mz / r
    return np.array([
        mx,
        mx * mx / r + ps - bx * bx,
        mx * my / r - bx * by,
        mx * mz / r - bx * bz,
        np.zeros_like(r),
        by * u - bx * v,
        bz * u - bx * w,
        (e + ps) * u - bx * (bx * u + by * v + bz * w),
    ])


def speed_spec(U, g):
    r, mx, my, mz, bx, by, bz, e = U
    u = mx / r
    p = pressure(U, g)
    vA = u - np.sqrt(bx * bx + by * by + bz * bz) / np.sqrt(r)
    cs = np.sqrt(np.maximum(g * p / r, 0.0))
    s = vA * vA + cs * cs
    fast = np.sqrt(0.5 * (s + np.sqrt(np.maximum(s * s - 4 * vA * vA * cs * cs, 0.0))))
    return np.maximum(np.abs(u - fast), np.abs(u + fast))


def speed_textbook(U, g):
    r, mx, my, mz, bx, by, bz, e = U
    u = mx / r
    p = pressure(U, g)
    a2 = np.maximum(g * p / r, 0.0)
    b2 = (bx * bx + by * by + bz * bz) / r
    bx2 = bx * bx / r
    cf = np.sqrt(0.5 * (a2 + b2 + np.sqrt(np.maximum((a2 + b2) ** 2 - 4 * a2 * bx2, 0.0))))
    return np.abs(u) + cf


def run(left, right, g, speed, nx=800, t_end=0.1, cfl=0.9, x0=0.5):
    x = (np.arange(nx) + 0.5) / nx
    dx = 1.0 / nx
    U = np.where(x < x0, prim_to_cons(*left, g)[:, None], prim_to_cons(*right, g)[:, None])
    t, steps, min_p, min_r = 0.0, 0, np.inf, np.inf
    while t < t_end and steps < 200000:
        a = speed(U, g)
        if not np.all(np.isfinite(a)):
            return dict(status="non-finite speed", t=t, steps=steps, min_p=min_p, min_r=min_r)
        dt = min(cfl * dx / np.max(a), t_end - t)
        Ue = np.concatenate([U[:, :1], U, U[:, -1:]], axis=1)  # outflow boundaries
        UL, UR = Ue[:, :-1], Ue[:, 1:]
        amax = np.maximum(speed(UL, g), speed(UR, g))
        Fi = 0.5 * (flux(UL, g) + flux(UR, g)) - 0.5 * amax * (UR - UL)
        U = U - dt / dx * (Fi[:, 1:] - Fi[:, :-1])
        t += dt
        steps += 1
        p = pressure(U, g)
        min_p, min_r = min(min_p, p.min()), min(min_r, U[0].min())
        if not np.all(np.isfinite(U)):
            return dict(status="blew up (NaN/inf)", t=t, steps=steps, min_p=min_p, min_r=min_r)
    status = "ok" if (min_p > 0 and min_r > 0) else "positivity lost"
    return dict(status=status, t=t, steps=steps, min_p=min_p, min_r=min_r)


CASES = {
    # name: (left primitives, right primitives, gamma, t_end); primitives r,u,v,w,Bx,By,Bz,p
    "Brio-Wu": ((1, 0, 0, 0, 0.75, 1, 0, 1), (0.125, 0, 0, 0, 0.75, -1, 0, 0.1), 2.0, 0.1),
    "Brio-Wu, flow +2 (Galilean shift)": ((1, 2, 0, 0, 0.75, 1, 0, 1), (0.125, 2, 0, 0, 0.75, -1, 0, 0.1), 2.0, 0.05),
    "Ryu-Jones 2a": ((1.08, 1.2, 0.01, 0.5, 2 / np.sqrt(4 * np.pi), 3.6 / np.sqrt(4 * np.pi), 2 / np.sqrt(4 * np.pi), 0.95),
                     (1, 0, 0, 0, 2 / np.sqrt(4 * np.pi), 4 / np.sqrt(4 * np.pi), 2 / np.sqrt(4 * np.pi), 1), 5 / 3, 0.2),
    "Strong field, low beta": ((1, 0, 0, 0, 1.0, 5, 0, 0.1), (0.5, 0, 0, 0, 1.0, -5, 0, 0.05), 5 / 3, 0.05),
    "Fast transverse flow": ((1, 0, 3, 0, 0.5, 2, 0, 1), (1, 0, -3, 0, 0.5, -2, 0, 1), 5 / 3, 0.1),
}

if __name__ == "__main__":
    for name, (L, R, g, tend) in CASES.items():
        for label, sp in (("spec", speed_spec), ("textbook", speed_textbook)):
            res = run(L, R, g, sp, t_end=tend)
            print(f"{name:36s} {label:9s} {res['status']:22s} steps={res['steps']:6d} "
                  f"min p={res['min_p']:.3e} min rho={res['min_r']:.3e}")
