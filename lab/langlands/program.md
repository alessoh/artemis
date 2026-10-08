# Artemis program: the archimedean sign, murmurations and local root numbers

This file is the human's instruction to the lab. It is written by Peter Alesso
(with Claude) and read by every agent. It is the only lever a human uses to
steer a run; agents never edit it.

## Where the questions come from

The program tests research direction R1 of P. Alesso, "Euler's identity and
the Langlands program" (research memo, 2026). The memo's starting point is
that Euler's identity, e^{i pi} = -1, is the root number of the real place:
the factor that the archimedean place contributes to the sign of a functional
equation. For an elliptic curve E over Q with conductor N, the global root
number is

    w(E) = -(product over p | N of the local root numbers w_p),

and the leading minus sign is that archimedean factor. Over a totally real
field of degree d there are d real places, so the sign becomes (-1)^d times
the product of the finite local signs. Over the real quadratic field
Q(sqrt 5) it is +(product of the finite signs): the opposite convention from
Q for the same finite data.

Murmurations are oscillations in the average of a_p(E) over curves ordered by
conductor, first seen by He, Lee, Oliver and Pozdnyakov (2022) and explained
for modular forms by Zubrilina (2023). Their leading term is a correlation
between a_p and the root number w(E). The memo asks two things.

1. If murmurations follow the true root number, then over Q(sqrt 5) they
   should line up with +(product of the finite local signs), the reverse of
   what the same rule gives over Q. This is the predicted flip.
2. Rank 0 and rank 2 curves over Q both have w = +1, so their local signs
   have the same product. Does the vector of local signs (w_p) for p | N
   depend on the rank at all, or does the whole rank 0 versus rank 2
   difference live in the a_p at the good primes?

The program has two parts. Part A answers question 1 with fixed measurements
that no agent can change. Part B answers question 2 with the AutoResearch
loop: the agents search for the clearest description of how the local signs
differ between rank 0 and rank 2, and one frozen test on held-out conductors
decides whether the difference is real.

## What is expected, and what is new

Be honest about this in every message and in the report.

Part A is a check of established theory more than a discovery. The formula
w = (-1)^d (product of local signs) is Deligne's, and the data build already
confirmed, for all 3,333 semistable isogeny classes over Q(sqrt 5) in the
snapshot, that PARI's global root number equals +(product of the finite
signs), and for 4,602 of the 4,605 classes that it equals (-1)^rank (the
other three have only rank bounds in the LMFDB). The flip is therefore
expected. What Part A adds is an explicit, pre-registered demonstration of
the archimedean sign inside the murmuration pattern over a real quadratic
field, using finite signs computed from the bad primes alone, and a measure
of how closely the pattern over Q(sqrt 5) matches the one over Q when both
are drawn against p / N. Whether murmurations over number fields have been
studied before is not known to the humans; the Scout must check.

Part B is open. The humans know of no published answer. An exploratory look
at the training conductors only (N below 300,000) found that, among classes
sharing a conductor, rank 2 classes tend to have more split multiplicative
primes (local sign -1 at a prime dividing N exactly once) than rank 0
classes: within-conductor AUC 0.508, z = 5.7. Weighting each such prime by
log(p) / p instead gave 0.498, so the direction may depend on the size of p.
While testing the harness the humans also saw the val numbers of the simple
rule (AUC 0.521) and of one trial model; the test conductors (400,000 to
500,000) have never been scored by anyone.

## The data (frozen; never edit, move or regenerate it)

`lab/langlands/data/`, built once by `prepare_data.py` and fingerprinted in
`manifest.json`:

| File | What it holds |
|------|---------------|
| `rank_signs.tsv.gz` | Every isogeny class over Q with conductor N < 500,000 and rank 0 or 2, from John Cremona's tables (github.com/JohnCremona/ecdata at commit 25cec5e): N, class, rank, each bad prime with its exponent and local root number, and a_p for the good primes below 100. 790,258 rank 0 and 279,056 rank 2 classes. |
| `murm_q.jsonl.gz` | Every class over Q with N < 5,000 (17,314 classes): rank, global root number, local signs, and a_p for every good prime p <= N, computed with PARI 2.17.2. Local signs, global sign and rank parity were checked against each other for every class. |
| `murm_k.jsonl.gz` | One curve per isogeny class over Q(sqrt 5) (4,605 classes with conductor norm below 5,000) from the LMFDB file downloaded on 2026-10-08: conductor norm, rank, PARI's global root number, the bad primes as (norm, exponent, a_P), the product of the finite local signs for semistable classes, and a_P for every degree-one prime P not dividing the conductor with norm up to the conductor norm. |

The ranks are as recorded in Cremona's tables and the LMFDB. Over
Q(sqrt 5) PARI computes local root numbers only over Q, so the finite sign
is computed only where every bad prime is multiplicative (local sign -a_P);
classes with additive primes take part in Part A only through PARI's global
root number.

## The files

| File | Who changes it | What it is |
|------|----------------|------------|
| `lab/langlands/harness.py` | humans only | Loads the frozen data, runs every experiment in a clean process, computes every statistic, keeps the ledger. Never edit it. |
| `lab/langlands/runner.py` | humans only | Runs one `score()` in its own process. Never edit it. |
| `lab/langlands/prepare_data.py` | humans only | Built the snapshot. Never run it. |
| `lab/langlands/experiment.py` | the lab (only the Compiler promotes into it) | One function, `score(train, rows, seed)`. It starts as the frozen simple rule: the number of split multiplicative primes. |
| `lab/langlands/program.md` | humans only | This file. |

Trials live in `lab/langlands/trials/<name>.py`, each a full copy of
`experiment.py` with one idea changed.

## Part A: the fixed measurements

Bins: x = p / N (over Q(sqrt 5), p is the norm of a degree-one prime and N
the conductor norm) in ten bins of width 0.1 on [0, 1].

- **C1, reproduction over Q** (conductors 1,000 to 4,999). M_Q is the mean of
  w(E) a_p / sqrt(p) in each bin; P+ and P- are the means of a_p / sqrt(p)
  over classes with w = +1 and w = -1. Reproduced if P+ and P- are mirror
  images (their correlation and its 95 percent bootstrap interval below 0)
  and M_Q changes sign at least once.
- **C2, the predicted flip over Q(sqrt 5)** (conductor norms 1,000 to 4,999).
  F_ss is the mean of S a_P / sqrt(p) over semistable classes, S being the
  product of the finite local signs computed from the bad primes alone. The
  primary statistic is rho_ss, the correlation of F_ss with M_Q across the
  ten bins. The prediction is rho_ss > 0; the Q convention carried over
  unchanged would give rho_ss < 0. Verdict: consistent with the flip if the
  95 percent interval lies above 0, contradicting it if below 0, otherwise
  inconclusive. Also reported: rho_all over every class with PARI's root
  number, the first-bin values, and a sensitivity check that drops the
  classes with a model over Q (base changes, which inherit Q's a_p).

Intervals come from 2,000 bootstrap draws that resample whole conductors
(whole conductor norms over Q(sqrt 5), which keeps Galois-conjugate classes
together). The pilot ranges (N and norm below 1,000) may be computed at any
time with `python lab/langlands/harness.py murmurations`; the humans have
seen them (rho_ss = 0.47 on the pilot range, with F_ss staying positive
where M_Q turns negative, so the pattern over Q(sqrt 5) may sit on a
different scale of p / N). The confirmatory ranges are computed once, by
`final`.

## Part B: the AutoResearch loop

**The interface.** `score(train, rows, seed)` returns one float per row; a
higher score means "more likely rank 2". `train` is a list of
`{"N": 11, "bad": [[11, 1, -1]], "rank": 0}`, one per class with a smaller
conductor; `rows` are the classes to score, `{"N": ..., "bad": [...]}` only.
Experiments never see a_p, the curve, its label or its rank. The data
file's own order (Cremona's class letters) is correlated with rank, so it
never reaches an experiment: `train` is sorted by N, sign pattern and rank,
and `rows` holds each distinct pair of N and sign pattern once, sorted, with
every class that shares it receiving the same score. Classes with the same N
and the same signs are indistinguishable, so a fair score could not separate
them anyway. Everything is deterministic: the same code and seed give the
same numbers on every run.

**The metric.** Within-conductor AUC on val (conductors 300,000 to 399,999),
seed 0: over every pair of a rank 2 class and a rank 0 class with the same
N, the fraction in which the rank 2 class scores higher (ties count one
half). Classes with the same N have the same primes and exponents, so only
the signs can move this number away from 0.5. The harness also reports the
stratified Wilcoxon z, a one-sided p, and a 95 percent bootstrap interval
over conductors. Higher is better.

**Noise and the keep rule.** The val AUC has a bootstrap half-width of about
0.006, and paired differences between two trials about the same. So:

- A trial is a candidate only if its val AUC beats the current best by at
  least **0.002** and the lower end of the paired 95 percent interval
  (`delta_ci95_low`, reported by `evaluate`) is above 0.
- The Skeptic then runs `recheck` (seeds 1 and 2). For a model that uses
  randomness, the gain must hold on both seeds (`delta_vs_best_by_seed`
  above 0 on each). A deterministic rule gives identical numbers on every
  seed, which is fine.
- The Skeptic also probes the trial (`probe`: fit below N = 200,000, score
  200,000 to 299,999) and rejects a gain that vanishes there.

**The final test** (once, by the Compiler, at the end). `experiment.py` is
trained on train and val together (seed 0) and scores the test conductors
(400,000 to 499,999). Pre-registered hypotheses, each one-sided at
p < 0.01 by both the normal approximation and 2,000 within-conductor
permutations:

- **H_B1.** The frozen simple rule (the number of split multiplicative
  primes) has within-conductor AUC above 0.5 on test.
- **H_B2.** The lab's promoted experiment has within-conductor AUC above 0.5
  on test.

The final also reports the promoted experiment minus the simple rule (paired
interval), and a positive control: a Nagao-type sum of -a_p log(p) / p over
the good primes below 100, which experiments never see, to show how large a
real rank signal looks on the same scale.

## Setup (the Compiler does this once at the start of a run)

1. Read this file, `lab/langlands/harness.py` and `lab/langlands/experiment.py`.
2. `pip install -r requirements-langlands.txt` (NumPy, SciPy, scikit-learn).
3. `python lab/langlands/harness.py fingerprint` and record the three hashes.
4. `python lab/langlands/harness.py describe`.
5. `python lab/langlands/harness.py murmurations` (the pilot ranges; free).
6. `python lab/langlands/harness.py baselines` (the simple rule and the
   positive control on val).
7. `python lab/langlands/harness.py evaluate --note "starting experiment.py"`.
8. `python lab/langlands/harness.py recheck --note "starting experiment.py"`.

## The experiment loop

Repeat until the budget is spent:

1. The Planner reads the ledger (`runs/langlands/ledger.tsv`), the Scout's
   notes and the Skeptic's last review, and proposes the next two or three
   ideas, each a single, testable change with a one-line hypothesis stated
   in number-theoretic terms.
2. Experimenters each copy `lab/langlands/experiment.py` to
   `lab/langlands/trials/<short-name>.py`, make that one change, check it
   with `probe` (free), then run
   `python lab/langlands/harness.py evaluate --experiment lab/langlands/trials/<short-name>.py --note "<hypothesis>"`.
   Evaluations run one at a time; a second one waits its turn.
3. The Skeptic reviews every candidate (see the keep rule): it rechecks with
   new seeds, reads the diff, and probes.
4. If the Skeptic approves, the Compiler copies the trial over
   `lab/langlands/experiment.py` and commits it with git
   (`git add lab/langlands/experiment.py && git add -f runs/langlands/ledger.tsv runs/langlands/details/*.code.txt && git commit -m "keep: <idea> auc X -> Y"`).
   Otherwise the trial is discarded (it stays in the ledger, which is the
   point). After a wave with nothing kept, the Compiler still commits the
   record (`git add -f runs/langlands/ledger.tsv runs/langlands/details/*.code.txt && git commit -m "ledger: wave N"`).

**NEVER STOP** to ask the human whether to continue. The human may be asleep.
Keep proposing, testing and reviewing ideas until the harness reports that the
experiment budget (40 val evaluations, 16 recheck seed runs) is used up or the
spending limit is reached. Three consecutive waves with no kept improvement
may end the loop only after at least 25 evaluations have been used; before
that, a plateau means it is time for bolder ideas, not for stopping. A
trial that loses is still a result: the lab is mapping where the signal
lives, so a clean negative ("the signs at additive primes carry nothing
beyond the split count") is worth recording in the report. Then close the
run: `final`, then the report.

## Rules

- `score()` uses only its arguments. No files, no network, no reading the
  snapshot, no attempt to recover a class's identity, a_p or rank.
- The harness reads each trial once, checks those exact bytes, archives
  them with the result, and runs that copy. It refuses a trial unless it
  imports only NumPy, SciPy, scikit-learn and these standard modules: math,
  heapq, itertools, collections, random, time, functools, bisect,
  statistics, array, copy, enum and abc. Submodules are allowed only from a
  list (for example numpy.linalg, scipy.stats, scipy.optimize,
  sklearn.linear_model, sklearn.ensemble, sklearn.preprocessing,
  sklearn.metrics); anything that reads files (scipy.io, sklearn.datasets,
  numpy.lib and the like) is refused, and so is `import *`. It also refuses
  names that open files or inspect the interpreter (open, exec, eval,
  getattr, sys, os, io and the like), any attribute whose name starts with
  an underscore, double-underscore names other than the bare `__name__`, any
  string containing a double underscore, integers larger than 2**63, and
  files with more than 300 numeric constants, a literal longer than 50
  items, a string longer than 200 characters, or more than 2,000 characters
  of strings outside docstrings.
- The process that runs `score()` also guards itself: after NumPy, SciPy
  and scikit-learn are loaded, it may read files only inside the Python
  installation (and its own copy of the trial), and may not write files,
  start processes or open network connections.
- One core: the harness runs each `score()` in its own process with one
  numerical thread and a minimal environment. The process gets up to 300
  seconds to read its input and import, then 600 seconds for `score()`, and
  a run that used more than 1.10 times its wall time in CPU (plus 30
  seconds) is rejected.
- Every trial is a complete, runnable file under 40 KB. Never paste in
  tables computed from val or test conductors. A rule stated in terms of p,
  e and w_p is fine; a lookup of particular conductors is not.
- Probe freely. Never run anything on val outside `evaluate` and `recheck`,
  and never run anything on test: it is touched once, by `final`.
- Budgets count evaluations that were started, so an interrupted evaluation
  still counts. Never set the ARTEMIS_RUNS_DIR variable; the lab's ledger is
  runs/langlands/ledger.tsv and nothing else counts.
- Never run `harness.py final` except as the last step of a run, by the
  Compiler, once. It scores lab/langlands/experiment.py only.
- Never invent a number or a citation. Every claim in the report must trace
  to the ledger, the details files, the manifest, final_test.json or a source
  found by the Scout.

## How the result is protected

The labels are public mathematics: anyone can download Cremona's tables, and
the snapshot sits in the sandbox. So the integrity of the final result rests
on four things, not on secrecy. The harness gives an experiment nothing but
N and the signs, in an order that carries no rank, and its static check and
separate process keep the experiment away from files. Every trial's exact
code is archived with its scores in `runs/langlands/details/`. Every command
every agent runs is recorded in the session transcript, which the humans
keep and search for any command that touches `lab/langlands/data/` outside
the harness or sets ARTEMIS_RUNS_DIR. And the humans re-run `final`
themselves on the promoted `experiment.py` after the run and compare. The
Compiler also commits the ledger and the archived trial code after every
wave, so a reset budget or a vanished trial would show in the history. The
static check's limits still leave room for about 30,000 bits of constants in
a trial, too little to carry the val labels but enough for a targeted
lookup, which is why the archived code is read before any result is
accepted.

## Simplicity criterion

The goal is understanding, not a leaderboard. A rule a number theorist can
state in one sentence (for example "count the split multiplicative primes
above 7", whether or not that particular rule works) beats a gradient-boosted model with the same AUC, and the report
must say in plain words what the kept experiment looks at. All else being
equal, simpler is better; removing something and getting an equal or better
result is a great outcome.

## Ideas to start from

- Split the count of -1 signs by reduction type: multiplicative (e = 1)
  versus additive (e >= 2), and look at p = 2 and p = 3 separately, where
  additive reduction and its local signs are most varied.
- Test whether the direction of the effect depends on the size of p (small
  primes against large ones), as the log(p) / p weighting hints.
- Within a conductor the number of -1 signs is always odd. Compare 1 against
  3 or more, rather than a raw count.
- Use the training data: a conditional logistic regression that compares
  classes only within the same conductor matches the metric exactly.
- Form hypotheses from the Birch and Swinnerton-Dyer formula: a split
  multiplicative prime has Tamagawa number c_p = v_p(Delta), which can be
  large, while a non-split one has c_p of 1 or 2. The data do not include
  c_p, so this can only guide which features to try.
- Look at which conductors carry the signal (number of bad primes, size of
  N, whether 2 or 3 divides N), then state a hypothesis and test it.

## The report

At the end the Scribe writes `runs/langlands/report.md` for a number
theorist: the two questions and where they come from, the data and its
fingerprint, the pre-registered definitions, Part A's results with the
verdict and the two profiles side by side, Part B's baselines, what was
tried and what was learned (from the ledger), the final experiment in plain
words, the held-out results for H_B1 and H_B2 next to the positive control,
what is expected and what is new (as stated above), the limits (ranks as
recorded in the tables, a small sample over Q(sqrt 5), Galois-conjugate
pairs, the choice of p / N as the scale, the humans' look at train, pilot
and val numbers), and every source. Plain, smooth prose; tables for numbers.
