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

Starting point: PyVRP 0.14.0 with its default settings (identical to the
frozen lab/cvrp/reference.py baseline).
"""

from __future__ import annotations

import numpy as np
from pyvrp import Client, Depot, Location, ProblemData, SolveParams, VehicleType, solve as pyvrp_solve
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


def solve(instance: dict, time_limit: float, seed: int) -> list[list[int]]:
    """Return routes as lists of customer indices (1..n); the depot is 0."""
    data = build_data(instance)
    params = SolveParams(neighbourhood=NeighbourhoodParams(num_neighbours=20))
    result = pyvrp_solve(data, stop=MaxRuntime(time_limit), seed=seed, display=False,
                         params=params)
    location = [client.location for client in data.clients()]
    return [[int(location[a.idx]) for a in route if a.is_client()]
            for route in result.best.routes()]
