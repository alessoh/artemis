"""Starting search: the pre-registered baseline sampler, spent on the whole budget.

search(info, kit, seed) draws points from the baseline sampler, evaluates each
with the kit until the call budget is used, and returns the points with the
smallest ratio amax / spectral radius. It knows nothing about the physics and
is the starting point the lab improves on.
"""
import numpy as np


def search(info, kit, seed):
    rng = np.random.default_rng(seed)
    found = []
    tries = 0
    while kit.remaining() > 0 and tries < 400_000:
        tries += 1
        p = kit.sample(rng)
        r = kit.evaluate(p)
        if r is not None:
            found.append((r["ratio"], p))
    found.sort(key=lambda item: item[0])
    return [p for _, p in found[:20]]
