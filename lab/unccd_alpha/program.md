# Artemis program: choosing UN-CCD's alpha without labels

This file is the human's instruction to the lab. It is written by Peter Alesso
(with Claude) and read by every agent. It is the only lever a human uses to
steer a run; agents never edit it.

## Where the question comes from

Shi, Ceyhan and Billor, "Clustering with Uniformity- and Neighbor-Based Random
Geometric Graphs" (arXiv:2501.06268v3), propose UN-CCD. Around every point it
grows a covering ball until a Monte Carlo test at level alpha rejects
complete spatial randomness inside the ball; balls that overlap are joined
into clusters, and the number of clusters is chosen by the silhouette. The
test compares the mean and median nearest-neighbour distance inside the ball
with their distribution for uniform points.

Everything depends on alpha. A smaller alpha lets balls grow larger. The
paper sets it by hand for each dimension, 15, 10, 5, 1 and 0.1 percent for
d = 2, 3, 5, 10 and 20, "after some trial-and-error process (not shown)",
which can only have been judged against the true labels; the authors' code
also uses the descending radius search for d of 10 and above. The paper
lists "automating the choice of the significance level" as future work, and
describes UN-CCD as needing little tuning. Artemis Project 1, an independent
reproduction (branch unccd-repro, docs/Artemis_UNCCD_Reproduction_Report.docx),
confirmed that the published simulation results come out of the authors'
code, and found that the real-data results depend on alpha values and search
directions chosen per dataset.

The question for this lab: **can a rule that sees only the unlabelled data
choose alpha, and the search direction, as well as the paper's hand-tuned
schedule?**

## What is expected, and what is new

Be honest about this in every message and in the report. Choosing a tuning
parameter by an internal criterion (silhouette, stability under resampling,
gap statistics) is standard practice in clustering; nobody expects a new
principle. What is new is a rule for this particular method, judged by a
frozen, pre-registered test on regimes the paper never ran, against the
paper's own schedule. A clean negative (no label-free rule matches the
schedule) would also be informative, because it would mean the "little
tuning" claim needs qualifying.

Note what "without labels" means here. The paper's schedule is itself a rule
that maps the dimension to alpha; it was tuned with labels on the paper's
simulation design, which is the design of the dev and val splits below. The
lab's rules are also developed on labelled dev and val data. The difference
is that the lab's rule decides from the dataset in front of it, and the test
asks whether it carries over to regimes neither was tuned on.

## The files

| File | Who changes it | What it is |
|------|----------------|------------|
| `lab/unccd_alpha/harness.py` | humans only | Loads the frozen data, runs every rule in a clean process, scores it, keeps the ledger. |
| `lab/unccd_alpha/runner.py` | humans only | Runs one rule's `choose()` on every dataset of a split in its own process. |
| `lab/unccd_alpha/kit.py` | humans only | The label-free toolkit a rule receives (below). |
| `lab/unccd_alpha/unccd.py` | humans only | UN-CCD in Python, a line-by-line port of the authors' R code; identical labels on all 51 validation cases (`data/port_validation.json`). |
| `lab/unccd_alpha/nulls.py` | humans only | The null tables and the alpha grid. |
| `lab/unccd_alpha/prepare_data.py`, `build_nulls.py`, `validation/` | humans only | Built the data. Never run them. |
| `lab/unccd_alpha/data/` | humans only | Null tables, the dev and val datasets, and the precomputed clusterings. |
| `lab/unccd_alpha/experiment.py` | the lab (only the Compiler promotes into it) | `choose(X, kit, seed)`. It starts as "the alpha whose clustering has the largest silhouette". |
| `lab/unccd_alpha/formula.py` | the lab (only the Compiler promotes into it) | `alpha_formula(n, d)`. It starts as a fixed 5 percent. |
| `lab/unccd_alpha/program.md` | humans only | This file. |

Trials live in `lab/unccd_alpha/trials/<name>.py` (a full copy of
experiment.py with one idea changed) or `trials/<name>_formula.py` (a copy of
formula.py).

## The interface

`choose(X, kit, seed)` receives one unlabelled dataset `X` (an n by d NumPy
array) and returns an alpha, or `{"alpha": a, "direction": "ascend" or
"descend"}` (the default direction is "ascend"). The alpha is snapped to the
nearest of the 15 grid values in log scale: 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5,
2, 3, 5, 8, 10, 15, 20 and 30 percent. The kit offers:

- `kit.n`, `kit.d`, `kit.alphas` (the grid), `kit.directions`;
- `kit.data()` and `kit.distances()`;
- `kit.cluster(alpha, direction)`: UN-CCD on X, a dict with `labels`,
  `silhouette` (the mean silhouette UN-CCD maximised), `balls`, `clusters`
  and `radii`. On dev and val these are precomputed, so the call is instant.
- `kit.cluster_points(points, alpha, direction)`: UN-CCD on any other point
  set of the same dimension (a subsample, a perturbed copy). Always computed;
  it costs real time (about 0.1 s for 200 points ascending, 1 to 30 s
  descending for 200 to 900 points).
- `kit.null_quantiles(alpha)`: the two null arrays for this dimension.
- `kit.silhouette(labels)`: the mean silhouette of any labelling of X.

`alpha_formula(n, d)` returns an alpha or `(alpha, direction)` from the
number of points and the dimension alone. It may import only `math` and may
contain at most three numeric constants other than 0, 1 and 2 (for example
two for alpha and one dimension threshold for the direction); arithmetic made
only of literals counts as one constant, and math.pi, math.e and strings
other than "ascend" and "descend" are not allowed. It must be a closed-form
expression: no loops or comprehensions, and no names other than n, d, math,
min, max, abs, round and its own local variables. This is the
"two-parameter formula" of hypothesis H2.

## The data (frozen; never edit, move or regenerate it)

All datasets follow the paper's simulation design (Section 4 and the authors'
generator): uniform clusters in balls of radius 0.8 to 1.2, or Gaussian
clusters with standard deviation 0.8 to 1.2, at the paper's centres (spacing
3 for uniform and 6 for Gaussian clusters); noise, where present, is uniform
over the data's bounding box and is left out of the ARI. Rows are shuffled.

- **dev** (free, `probe`): 32 datasets: uniform and Gaussian, d = 2, 3, 5, 10,
  20, n = 100, 2, 3 or 5 clusters, plus Gaussian noise regimes at 10 percent
  for d = 3 and 10.
- **val** (budgeted, `evaluate`): 64 datasets: the same design with n = 50 and
  200, plus noise regimes at 5 and 20 percent for d = 3 and 10.
- **test** (sealed): not in the repository or the sandbox. The humans draw it
  from a secret seed whose SHA-256 is
  `2287521b8b33edcf30eaf5fa0e67f7eaa8921f1e0f645196dc02cb218420d619`
  (of the seed's decimal digits and a newline), and run `final` once the
  lab's files are frozen. It holds 45
  regimes the paper never ran, two datasets each: d = 4, 7 and 15; n = 30,
  300 and 700; 2, 4 or 6 clusters; noise 0, 10 or 30 percent; uniform or
  Gaussian; and new centres placed by a random walk at spacing 0.85 to 1.15
  times the paper's. The regime list is fixed by `prepare_data.test_regimes()`.
  It also holds five real datasets the paper did not use: aggregation,
  compound and jain (from the clustering basic benchmark), glass and yeast
  (UCI), preprocessed as in the authors' loader.

## The metric

For each dataset the harness clusters with the chosen settings using the
frozen port and computes the adjusted Rand index (ARI) between the clusters
and the true labels over the cluster points. A regime's score is the mean ARI
of its datasets; the split's score is the mean over regimes, with a 95 percent
bootstrap interval over regimes (2,000 draws, seed 0). Comparisons between two
rules are paired by regime. Higher is better.

`python lab/unccd_alpha/harness.py baselines` scores, on val: the paper's
schedule, a fixed 1 percent (the real-data protocol the paper states), a fixed
5 percent, the silhouette maximum (the starting experiment), and two ceilings
that use the labels: the best alpha per dataset with the ascending search,
and with either search. The ceilings show how much a perfect rule could gain.

## The keep rule

A trial is a candidate only if its val mean ARI beats the current best by at
least **0.005** and the lower end of the paired 95 percent interval
(`delta_ci95_low`) is above 0. The Skeptic then reviews it: it reads the
diff, checks that the rule uses no information about the datasets beyond X
(no lookup of particular datasets, no constants fitted to individual val
datasets), probes it on dev, and, for a rule that uses randomness, runs
`recheck` (seeds 1 and 2), where the gain must hold on both seeds. A
deterministic rule gives identical numbers on every seed.

The formula has its own keep rule: a formula trial replaces formula.py if its
val mean ARI beats the current formula's by at least 0.005 with the lower end
of the paired interval above 0, after the Skeptic's review.

## Pre-registered hypotheses (decided once, on test, by the humans)

- **H1.** The lab's promoted experiment matches the paper's schedule on the
  held-out synthetic regimes: the lower end of the paired 95 percent interval
  of (experiment minus schedule) is above -0.02. At dimensions the paper does
  not list, the schedule's alpha is interpolated log-linearly in d between
  its neighbours (4: 8, 7: 3, 15: 0.3 percent after snapping), with the
  descending search for d of 10 and above.
- **H2.** The lab's formula matches the promoted experiment on the held-out
  synthetic regimes: the lower end of the paired 95 percent interval of
  (formula minus experiment) is above -0.02.

Also reported, without a pass mark: every rule's mean ARI on the five real
datasets, and the differences between the experiment and the fixed 1
percent, the silhouette maximum and the label-using ceiling.

## Setup (the Compiler does this once at the start of a run)

1. Read this file, `lab/unccd_alpha/harness.py`, `kit.py` and `experiment.py`.
2. `pip install -r requirements-unccd-alpha.txt` (NumPy, SciPy, scikit-learn).
3. `python lab/unccd_alpha/harness.py fingerprint` and record the hashes.
4. `python lab/unccd_alpha/harness.py describe`.
5. `python lab/unccd_alpha/harness.py baselines` (val; free).
6. `python lab/unccd_alpha/harness.py baselines --split dev` (free).
7. `python lab/unccd_alpha/harness.py evaluate --note "starting experiment.py"`.
8. `python lab/unccd_alpha/harness.py formula --note "starting formula.py"`.

## The experiment loop

Repeat until the budget is spent:

1. The Planner reads the ledger (`runs/unccd_alpha/ledger.tsv`), the details
   files, the Scout's notes and the Skeptic's last review, and proposes the
   next two or three ideas, each a single, testable change with a one-line
   hypothesis in statistical terms.
2. Experimenters each copy `experiment.py` (or `formula.py`) to
   `lab/unccd_alpha/trials/<short-name>.py` (or `<short-name>_formula.py`),
   make that one change, check it with `probe` (free, on dev), then run
   `python lab/unccd_alpha/harness.py evaluate --experiment lab/unccd_alpha/trials/<short-name>.py --note "<hypothesis>"`
   (or `formula --formula ...`). Evaluations run one at a time.
3. The Skeptic reviews every candidate under the keep rule.
4. If approved, the Compiler copies the trial over `experiment.py` (or
   `formula.py`) and commits:
   `git add lab/unccd_alpha/experiment.py lab/unccd_alpha/formula.py && git add -f runs/unccd_alpha/ledger.tsv runs/unccd_alpha/details/*.code.txt && git commit -m "keep: <idea> X -> Y"`.
   After a wave with nothing kept, commit the record alone
   (`git add -f runs/unccd_alpha/ledger.tsv runs/unccd_alpha/details/*.code.txt && git commit -m "ledger: wave N"`).

**NEVER STOP** to ask the human whether to continue. The human may be asleep.
Keep proposing, testing and reviewing until the experiment budget (40 val
evaluations; 16 recheck runs; 12 formula evaluations) is used up or the
spending limit is reached. Three consecutive waves with no kept improvement
may end the loop only after at least 25 evaluations; before that, a plateau
means bolder ideas. Work on the formula alongside the experiment: at least a
third of the waves should include a formula trial. A trial that loses is
still a result.

Close the run with `python lab/unccd_alpha/harness.py freeze` (it records the
exact experiment.py and formula.py the humans will test), commit
`runs/unccd_alpha/frozen.json` with `git add -f`, then the report. The lab
does not run `final`: the test split is not in the sandbox.

## Rules

- `choose()` uses only its arguments. No files, no network, no reading of the
  data folder, no attempt to identify a particular dataset. A rule stated in
  terms of n, d, distances, silhouettes, stability or the null tables is fine;
  a table of settings for particular val datasets is not.
- The harness reads each trial once, checks those exact bytes, archives them
  with the result, and runs that copy. It refuses a trial unless it imports
  only NumPy, SciPy, scikit-learn and these standard modules: math, heapq,
  itertools, collections, random, time, functools, bisect, statistics, array,
  copy, enum and abc (submodules only from a list; nothing that reads files).
  It refuses names that open files or inspect the interpreter (open, exec,
  eval, getattr, sys, os, io, gc and the like), any attribute starting with an
  underscore, any string containing a double underscore, more than 100 numeric
  constants, a literal longer than 30 items, a string longer than 200
  characters, or more than 2,000 characters of strings outside docstrings.
- The process that runs `choose()` guards itself: after its imports it may
  read files only inside the Python installation and the lab's frozen code,
  and may not write files, start processes or open network connections.
- One core: each run gets one numerical thread. A val evaluation gets 40
  minutes for all 64 datasets; on test, the 90 synthetic datasets get 4
  hours and the 5 real datasets another 4 hours.
  On test, too, kit.cluster() reads a cache that the humans precompute, so
  only cluster_points costs real time. A rule that
  calls `cluster_points` many times on large, descending searches can exceed
  the limit; keep the cost of the rule in mind.
- Probe freely on dev. Never run anything on val outside `evaluate`,
  `recheck` and `formula`. Budgets count evaluations that were started.
  Never set ARTEMIS_RUNS_DIR or ARTEMIS_UNCCD_TEST_DIR.
- Never download the real test datasets or any other clustering benchmark,
  and never search for the test seed. The transcripts are kept and searched.
- Never invent a number or a citation. Every claim in the report must trace
  to the ledger, the details files, the manifest or a source found by the
  Scout.

## How the result is protected

The test datasets are never in the repository or the sandbox: they are
drawn from a seed committed only by its hash, from regimes listed in public
code but never run before, and the humans score nothing on them until the
lab's files are frozen. The real test datasets are public, so the program
forbids looking at them and the humans search the transcripts. The lab's
final files are fixed by `freeze` and committed; the humans run `final` on
exactly those files and publish the full output. The val datasets are in the
sandbox with their labels, so a rule could in principle be fitted to them;
the archived code of every trial is read before any result is accepted, and
the test decides the hypotheses in any case.

## Simplicity criterion

The goal is a rule a statistician can state in a sentence and trust on new
data. "Take the alpha at which the silhouette is largest, but never below the
null expectation of ..." beats a learned model with the same val score. The
report must say in plain words what the kept rule and formula do. Removing
something and getting an equal or better result is a great outcome.

## Ideas to start from

- The silhouette maximum is the obvious label-free choice; check where it
  fails on dev (the per-dataset output of `probe` shows the chosen alpha and
  the ARI) before improving it.
- Stability: cluster subsamples (`cluster_points`) at each alpha and prefer
  the alpha whose partitions agree most, measured by ARI between overlapping
  subsamples.
- The null scaling: the expected nearest-neighbour distance of n uniform
  points in d dimensions scales like n^(-1/d), and the null quantiles are in
  `null_quantiles()`. A rule that sets alpha so the typical ball holds a
  given number of points, or so a given fraction of points are caught by
  balls, needs no clustering at all.
- Plateaus: alphas where the number of clusters stays the same over several
  neighbouring grid values are a classic sign of real structure.
- Direction: the authors use the descending search at d of 10 and above. Test
  whether a rule should choose the direction too, and how.
- For the formula, try alpha = a * n^b * c^d forms against the schedule's
  shape, with one threshold on d for the direction.

## The report

At the end the Scribe writes `runs/unccd_alpha/report.md` for a
statistician: the question and where it comes from, the data and its
fingerprint, the pre-registered definitions and hypotheses, the baselines on
val (including the label-using ceilings), what was tried and what was
learned (from the ledger), the kept rule and formula in plain words, their
val results beside the baselines, what is expected and what is new, the
limits (simulated data in the paper's family, a 15-value grid, one dataset
per val regime, the humans' look at the dev and val data while building the
lab), and every source. It states clearly that the test results will be
added by the humans after `final`. Plain, smooth prose; tables for numbers.
