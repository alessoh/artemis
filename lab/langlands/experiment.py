"""The lab's current best experiment for Part B (the only file the lab edits).

score(train, rows, seed) returns one number per row in `rows`; a higher number
means "more likely rank 2". Each row is {"N": conductor, "bad": [[p, e, w_p],
...]} where p runs over the primes dividing N, e is the exponent of p in N
and w_p is the local root number (+1 or -1). `train` holds the same fields
plus "rank" (0 or 2) for every class with a smaller conductor.

The harness compares only classes that share a conductor, so a score helps
only through what it does with the signs w_p.

Starting point: the frozen simple rule from the harness, the number of split
multiplicative primes (e = 1 and w_p = -1). It ignores the training data.
"""


def score(train, rows, seed):
    """Count the multiplicative primes with local sign -1."""
    return [float(sum(1 for p, e, w in row["bad"] if e == 1 and w == -1)) for row in rows]
