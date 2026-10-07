# Artemis program: vehicle routing on the CVRPLIB X benchmark

This file is the human's instruction to the lab. It is written by Peter Alesso
(with Claude) and read by every agent. It is the only lever a human uses to
steer a run; agents never edit it.

## The question

A delivery company sends trucks of fixed capacity from one depot to serve
every customer exactly once. The capacitated vehicle routing problem (CVRP)
asks for the routes with the shortest total distance. The CVRPLIB X
benchmark (Uchoa et al., European Journal of Operational Research 257, 845,
2017) holds 100 such problems with 100 to 1,000 customers, and the field
publishes a best-known solution (BKS) for each.

Within a short, fixed time limit on one CPU core (3 seconds per 100
customers), can this lab build a solver that gets closer to the best-known
solutions than PyVRP's default, a state-of-the-art open-source solver? And
does what it learns carry over to larger problems it never saw?

Separately, a human may later give the lab's final solver hours instead of
seconds on the largest instances (lab/cvrp/hunt.py). Any route shorter than a
published BKS would be a new record that anyone can check. That is a long
shot: the X benchmark has been attacked by the best groups in the field for
nearly a decade. The lab's job is the fixed-time question above.

## Run 2: where run 1 left off

Run 1 (October 7, 2026) kept one change: cutting each customer's granular
neighbourhood from PyVRP's default 50 nearest neighbours to 20, so each second
of search tries more moves. On its eight practice problems the mean gap fell
from 0.98 to 0.54 percent. On the 17 held-out test problems (all under 600
customers) the solver scored 0.58 percent against 0.73 for PyVRP default,
better on 12 of 17. On the 8 held-out larger problems (600 to 1,000
customers) it showed no gain. Run 1 stopped after 13 of its 60 evaluations
because three rounds in a row brought nothing new.

Run 2 starts from that solver (`lab/cvrp/experiment.py` is granular_20) and
changes four things, all decided by the humans before this run:

1. The practice set now has twelve problems: the same eight plus four larger
   ones (655, 749, 876 and 895 customers, with short and long routes). A gain
   must now hold on large problems to be kept.
2. The lab must use at least 40 of its 60 evaluations before the
   three-empty-rounds rule may end the loop.
3. The final test repeats every held-out problem with seeds 0, 1 and 2 for the
   lab's solver and for PyVRP default, and reports a paired comparison with a
   95 percent interval and a sign test.
4. The spending limit is 80 dollars.

The test and scale problems are the same as in run 1, so the two runs share
one yardstick. The humans saw run 1's results on them while designing run 2;
the agents never did, and never tuned anything on them.

The most useful goal for this run is a solver that keeps run 1's gain on
smaller problems and adds a gain on larger ones. One untested hypothesis:
the right neighbourhood size may depend on the shape of the problem, for
example on the typical number of customers per route, rather than being a
fixed 20. Any such rule must be computed from the instance itself, never
from a table of particular problems.

## The files

| File | Who changes it | What it is |
|------|----------------|------------|
| `lab/cvrp/harness.py` | humans only | Loads the frozen instances, checks every solution (each customer once, capacity respected), computes its length with CVRPLIB's rounding, enforces the time and CPU limits, writes the ledger. Never edit it. |
| `lab/cvrp/runner.py` | humans only | Runs one `solve()` in its own clean process so the harness can time it. Never edit it. |
| `lab/cvrp/reference.py` | humans only | The frozen PyVRP-default baseline. Never edit it. |
| `lab/cvrp/experiment.py` | the lab (only the Compiler promotes into it) | One function, `solve(instance, time_limit, seed)`, that returns routes. The current best solver. It starts as a copy of reference.py. |
| `lab/cvrp/program.md` | humans only | This file. |

Trials live in `lab/cvrp/trials/<name>.py`. Each is a full copy of
`experiment.py` with one idea changed. The data snapshot in `lab/cvrp/data/`
is frozen and fingerprinted; never edit, move or regenerate it. It holds the
instances and the BKS costs, but not the BKS routes.

## Setup (the Compiler does this once at the start of a run)

1. Read this file, `lab/cvrp/harness.py`, `lab/cvrp/reference.py` and
   `lab/cvrp/experiment.py`.
2. `pip install -r requirements-cvrp.txt` (PyVRP 0.14.0 and NumPy).
3. `python lab/cvrp/harness.py fingerprint` and record the four hashes.
4. `python lab/cvrp/harness.py describe` to see the splits, time limits and
   budgets.
5. `python lab/cvrp/harness.py baselines` to record the savings rule and
   PyVRP default on val (about three minutes).
6. `python lab/cvrp/harness.py evaluate --note "starting experiment.py"` to
   record the starting point.
7. `python lab/cvrp/harness.py recheck --note "starting experiment.py"`
   so the Skeptic has the current best's numbers on the recheck seeds.

## The metric

`mean_gap_pct` on the twelve val instances with seed 0: the average of
100 x (cost - BKS) / BKS. Lower is better; 0 means every route set matched
the best known. The harness also reports the median and worst gap and on how
many instances the trial beat the frozen PyVRP reference. Use those to
understand a result; keep or discard by the mean gap.

## Noise, measured before each run

The solver stops on wall-clock time, so the same code and seed can give a
slightly different answer on another run. Before run 1, identical PyVRP runs
on the eight-problem practice set gave a standard deviation of 0.085
percentage points across seeds. Before run 2, the starting solver
(granular_20) on the twelve-problem practice set gave mean gaps of 0.70 to
0.93 percent over seeds 0 to 4 on the build machine, a standard deviation of
0.094 points, while PyVRP default scored 1.20 to 1.23 percent. The sandbox is
faster than the build machine, so its absolute numbers will be lower; the
keep rule is unchanged from run 1 so the two runs are comparable:

- A trial is a candidate only if its seed-0 val mean gap is at least
  **0.15 percentage points** below the current best's.
- The Skeptic then runs `recheck` (seeds 1 and 2). The trial is kept only if
  its mean gap over those two seeds is at least **0.10 percentage points**
  below the current best's over the same two seeds.

## The experiment loop

Repeat until the budget is spent:

1. The Planner reads the ledger (`runs/cvrp/ledger.tsv`), the per-instance
   results in `runs/cvrp/details/`, the Scout's notes and the Skeptic's last
   review, and proposes the next two or three ideas, each a single, testable
   change with a one-line hypothesis.
2. Experimenters each copy `lab/cvrp/experiment.py` to
   `lab/cvrp/trials/<short-name>.py`, make that one change, check it on one
   or two train instances with `probe` (free), then run
   `python lab/cvrp/harness.py evaluate --experiment lab/cvrp/trials/<short-name>.py --note "<hypothesis>"`.
   Evaluations run one at a time; a second one waits its turn.
3. The Skeptic reviews every candidate (see the noise rule): it rechecks with
   new seeds, reads the diff, and probes train instances of other sizes.
4. If the Skeptic approves, the Compiler copies the trial over
   `lab/cvrp/experiment.py` and commits it with git
   (`git add lab/cvrp/experiment.py && git commit -m "keep: <idea> gap X -> Y"`).
   Otherwise the trial is discarded (it stays in the ledger, which is the point).

**NEVER STOP** to ask the human whether to continue. The human may be asleep.
Keep proposing, testing and reviewing ideas until the harness reports that the
experiment budget (60 val evaluations, 20 rechecks) is used up or the spending
limit is reached. Three consecutive waves with no kept improvement may end the
loop only after at least 40 evaluations have been used; before that, a
plateau means it is time for bolder ideas, not for stopping. Then close the
run. The final test takes about half an hour because it repeats every
held-out problem three times for both solvers. If you run out of ideas, re-read the ledger and the
per-instance details, combine near-misses, and try a bolder change.

## Rules

- `solve()` uses only its arguments. No files, no network, no reading the
  snapshot, no knowledge of which instance it is solving (the name and BKS
  are deliberately not passed).
- The harness reads each trial before running it and refuses it unless it
  imports only NumPy, PyVRP and these standard modules: math, heapq,
  itertools, collections, random, time, typing, functools, dataclasses,
  bisect, statistics, array, copy, enum and abc. It also refuses names that
  open files or inspect the interpreter (open, exec, eval, compile, getattr,
  sys, os, io and the like), double-underscore names other than `__name__`,
  and files with more than 300 numeric constants, a literal list longer than
  50 items or more than 2,000 characters of strings outside docstrings.
- One CPU core. No threads or processes. The harness runs each solve in its
  own process with one numerical thread, measures the time itself from the
  moment the process is ready, and rejects an answer that arrives later than
  1.03 x the limit plus half a second, or that used more than 1.10 x the
  limit plus 4 seconds of CPU.
- Use the time you are given, but stop a little early: PyVRP's
  `MaxRuntime(time_limit)` overshoots by a few hundredths of a second, which
  is allowed; anything slower is not.
- NumPy, PyVRP 0.14.0 and the standard library only; no new dependencies.
- Every trial is a complete, runnable file under 40 KB. Never paste in routes,
  distance tables or constants computed from val, test or scale instances.
  A setting computed by a general rule from the instance itself (for example
  from the average number of customers per route) is fine; a lookup of
  hand-tuned settings for particular sizes or problems is not.
- Probe freely on train and hunt instances. Never run anything on val
  instances outside `evaluate` and `recheck`, and never run anything on test
  or scale instances: those are touched once, by `final`.
- Budgets count the evaluations that were started, so an interrupted
  evaluation still counts. Never set the ARTEMIS_RUNS_DIR variable; the lab's
  ledger is runs/cvrp/ledger.tsv and nothing else counts.
- Never run `harness.py final` except as the last step of a run, by the
  Compiler, once. It scores lab/cvrp/experiment.py only.
- Never invent a number or a citation. Every claim in the report must trace
  to the ledger, the details files, the manifest or a source found by the
  Scout.

## Simplicity criterion

All else being equal, simpler is better. A small improvement that adds ugly
complexity is not worth keeping; removing something and getting an equal or
better result is a great outcome. A solver change an operations researcher
can describe in one paragraph beats an opaque pile of special cases with the
same score.

## Ideas to start from

- PyVRP's default search runs operators meant for richer problems (optional
  clients, shipments, groups). Keep only the operators that matter for plain
  CVRP so each second does more useful work.
- Tune the granular neighbourhood (how many nearest neighbours each customer
  considers) and the iterated local search settings for these time limits.
- Start the search from a good construction (Clarke and Wright savings, or a
  sweep by angle around the depot) through `initial_solution`.
- Split the time into several shorter runs with different seeds and keep the
  best, or restart from the best solution with a perturbation.
- For larger instances, decompose: solve clusters of routes (by angle or by
  barycentre) as sub-problems, then reassemble, as in the literature on very
  large CVRPs.
- Add a final improvement phase on the best solution (for example an exact
  or near-exact re-optimisation of each route's order).
- Look at which val instances have the largest gaps and what they have in
  common (route length, demand spread, depot position), then form an
  algorithmic hypothesis tested on train instances with the same character.

## The report

At the end the Scribe writes `runs/cvrp/report.md` for an operations
researcher: the question, the data and its fingerprint, the pre-registered
definitions and noise rule, the baselines, what was tried and what was
learned (from the ledger), the final solver in plain words, the held-out
results on test and scale next to PyVRP default and the savings rule, a
plain statement about records, the limits of the result, and every source.
Plain, smooth prose; tables for numbers.
