"""The current best CVRP solver idea. Agents improve this file.

solve(instance, time_limit, seed) receives one instance and must return a
list of routes, each a list of customer numbers 1..n (the depot, 0, is
implied at both ends). The instance is a dictionary with:
    capacity  vehicle capacity (int)
    coords    (n+1) x 2 integer array; row 0 is the depot
    demands   length n+1 integer array; demands[0] is 0
    distance  (n+1) x (n+1) integer matrix of rounded Euclidean distances,
              exactly the distances the harness uses to score the routes
The harness measures the time and CPU used; one core and time_limit seconds.

Starting point for run 2: the solver run 1 kept (trial granular_20, saved as
docs/results/cvrp_run1/experiment_final_run1.py). It is PyVRP 0.14.0 with each
customer's granular neighbourhood cut from 50 to 20 nearest neighbours, so
each second of search tries more moves. Run 1 found it better than PyVRP's
default on held-out problems under 600 customers, but not on larger ones.
"""

from __future__ import annotations

import math
import time

import numpy as np
from pyvrp import Solution, Client, Depot, Location, ProblemData, SolveParams, VehicleType, solve as pyvrp_solve
from pyvrp.search import NeighbourhoodParams
from pyvrp.stop import MaxRuntime


def build_data(instance: dict) -> ProblemData:
    """Turn the harness's instance dictionary into PyVRP problem data."""
    coords = instance["coords"]
    demands = instance["demands"]
    distance = np.asarray(instance["distance"], dtype=np.int64)
    customers = len(demands) - 1
    locations = [Location(x=int(x), y=int(y)) for x, y in coords]
    clients = [Client(location=i, delivery=[int(demands[i])]) for i in range(1, customers + 1)]
    vehicles = [VehicleType(num_available=customers, capacity=[int(instance["capacity"])])]
    return ProblemData(locations=locations, clients=clients, depots=[Depot(location=0)],
                       vehicle_types=vehicles, distance_matrices=[distance],
                       duration_matrices=[np.zeros_like(distance)])


def _routes_of(data: ProblemData, solution) -> list[list[int]]:
    location = [client.location for client in data.clients()]
    return [[int(location[a.idx]) for a in route if a.is_client()]
            for route in solution.routes()]


def _route_cost(distance: np.ndarray, routes: list[list[int]]) -> int:
    total = 0
    for r in routes:
        path = [0] + r + [0]
        total += int(sum(distance[path[i], path[i + 1]] for i in range(len(path) - 1)))
    return total


def _solve_sub(instance: dict, routes: list[list[int]], t: float, seed: int) -> list[list[int]]:
    """Re-optimise a group of routes as an independent PyVRP problem."""
    customers = sorted(c for r in routes for c in r)
    idx = [0] + customers
    pos = {c: i for i, c in enumerate(idx)}
    distance = np.asarray(instance["distance"], dtype=np.int64)
    sub = {"capacity": instance["capacity"],
           "coords": np.asarray(instance["coords"])[idx],
           "demands": np.asarray(instance["demands"])[idx],
           "distance": distance[np.ix_(idx, idx)]}
    data = build_data(sub)
    init = Solution(data, [[pos[c] - 1 for c in r] for r in routes])
    params = SolveParams(neighbourhood=NeighbourhoodParams(num_neighbours=20))
    result = pyvrp_solve(data, stop=MaxRuntime(max(t, 0.01)), seed=seed, display=False,
                         params=params, initial_solution=init)
    best = result.best
    if not best.is_feasible():
        return routes
    new_routes = [[idx[c] for c in r] for r in _routes_of(data, best) if r]
    if _route_cost(distance, new_routes) < _route_cost(distance, routes):
        return new_routes
    return routes


def solve(instance: dict, time_limit: float, seed: int) -> list[list[int]]:
    """Return routes as lists of customer indices (1..n); the depot is 0."""
    start = time.perf_counter()
    deadline = start + time_limit - 0.3
    n = len(instance["demands"]) - 1
    n_sectors = n // 250
    data = build_data(instance)
    params = SolveParams(neighbourhood=NeighbourhoodParams(num_neighbours=20))
    if n_sectors < 2:
        result = pyvrp_solve(data, stop=MaxRuntime(time_limit), seed=seed, display=False,
                             params=params)
        return _routes_of(data, result.best)

    phase1 = 0.4 * time_limit - (time.perf_counter() - start)
    result = pyvrp_solve(data, stop=MaxRuntime(max(phase1, 0.1)), seed=seed, display=False,
                         params=params)
    routes = [r for r in _routes_of(data, result.best) if r]
    coords = np.asarray(instance["coords"], dtype=float)
    depot = coords[0]
    rounds = 3
    remaining = rounds * n_sectors
    for rnd in range(rounds):
        angles = []
        for r in routes:
            b = coords[r].mean(axis=0)
            angles.append(math.atan2(b[1] - depot[1], b[0] - depot[0]))
        order = sorted(range(len(routes)), key=lambda i: angles[i])
        shift = rnd * len(routes) // (rounds * n_sectors)
        order = order[shift:] + order[:shift]
        total = sum(len(r) for r in routes)
        groups, current, count = [], [], 0
        for i in order:
            current.append(routes[i])
            count += len(routes[i])
            if len(groups) < n_sectors - 1 and count >= total * (len(groups) + 1) / n_sectors:
                groups.append(current)
                current = []
        if current:
            groups.append(current)
        new_routes = []
        for g in groups:
            now = time.perf_counter()
            t = (deadline - now) / max(remaining, 1) - 0.05
            remaining -= 1
            if t > 0.05:
                new_routes.extend(_solve_sub(instance, g, t, seed + rnd))
            else:
                new_routes.extend(g)
        routes = [r for r in new_routes if r]
    return routes
