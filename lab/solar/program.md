# Artemis program: earth-abundant solar absorbers

This file is the human's instruction to the lab. It is written by Peter Alesso
(with Claude) and read by every agent. It is the only lever a human uses to
steer a run; agents never edit it.

## The question

Among earth-abundant, non-toxic inorganic crystals in NIST JARVIS-DFT, which
ones should a lab compute next to find excellent solar absorbers fastest, and
what does the best search strategy teach us about what makes a good absorber?

An excellent absorber here means a material whose spectroscopic limited
maximum efficiency (SLME, computed by JARVIS from TBmBJ optical spectra;
Choudhary et al., Chem. Mater. 31, 5900, 2019) is at least 30 percent and
which is thermodynamically near-stable (energy above hull at most 0.1 eV/atom).
SLME is the expensive measurement. The cheap information is everything an
ordinary DFT relaxation gives: the OptB88vdW band gap, formation energy,
energy above hull, composition and crystal structure.

## The three files

| File | Who changes it | What it is |
|------|----------------|------------|
| `lab/solar/harness.py` | humans only | Loads the frozen data snapshot, defines the pool, the hit and the metric, runs experiments under a time limit, writes the ledger. Never edit it. |
| `lab/solar/experiment.py` | the lab (only the Compiler promotes into it) | One function, `rank(train, candidates, seed)`, that orders the candidate pool. The current best idea. |
| `lab/solar/program.md` | humans only | This file. |

Trials live in `lab/solar/trials/<name>.py`. Each is a full copy of
`experiment.py` with one idea changed. The data snapshot in `lab/solar/data/`
is frozen and fingerprinted; never edit, move or regenerate it.

## Setup (the Compiler does this once at the start of a run)

1. Read this file, `lab/solar/harness.py`, `lab/solar/experiment.py`.
2. `pip install -r requirements-solar.txt` if pandas or scikit-learn is missing.
3. `python lab/solar/harness.py fingerprint` and record the three hashes.
4. `python lab/solar/harness.py describe` to see the pool, hits and budgets.
5. `python lab/solar/harness.py baselines` to record random and the two
   Shockley-Queisser baselines in the ledger.
6. `python lab/solar/harness.py evaluate --note "starting experiment.py"` to
   record the starting point.

## The metric

`acceleration` on the val pool: how many times fewer expensive SLME
evaluations the ordering needs to find ten hits than a random ordering
would. Random search scores 1.0. Higher is better. The harness also reports
hits in the top 25, enrichment in the top 25 and average precision; use them
to understand a result, but keep or discard by `acceleration`.

## The experiment loop

Repeat until the budget is spent:

1. The Planner reads the ledger (`runs/solar/ledger.tsv`), the Scout's notes
   and the Skeptic's last review, and proposes the next two or three ideas,
   each a single, testable change with a one-line hypothesis.
2. Experimenters each copy `lab/solar/experiment.py` to
   `lab/solar/trials/<short-name>.py`, make that one change, and run
   `python lab/solar/harness.py evaluate --experiment lab/solar/trials/<short-name>.py --note "<hypothesis>"`.
3. The Skeptic reviews every trial that beats the current best: it reads the
   diff against `experiment.py`, re-runs the evaluation to confirm the number,
   and looks for leakage, overfitting to the val pool, and complexity that is
   not paying for itself.
4. If the Skeptic approves, the Compiler copies the trial over
   `lab/solar/experiment.py` and commits it with git
   (`git add lab/solar/experiment.py && git commit -m "keep: <idea> acceleration X -> Y"`).
   Otherwise the trial is discarded (it stays in the ledger, which is the point).

**NEVER STOP** to ask the human whether to continue. The human may be asleep.
Keep proposing, testing and reviewing ideas until the harness reports that the
experiment budget is used up or the lab's spending limit is reached; then
write the report. If you run out of ideas, re-read the ledger, the Scout's
findings and the failures, and combine near-misses; try more radical changes.

## Rules

- Experiments use only the `train` and `candidates` arguments. No files, no
  network, no reading the snapshot. The harness refuses code that tries, and
  the Skeptic checks the diff anyway.
- Pandas, NumPy and scikit-learn are available; no new dependencies.
- One call to `rank()` must finish within 300 seconds.
- Every trial is a complete, runnable file. Keep each change small enough
  that the ledger note explains it in one sentence.
- Never run `harness.py final` except as the last step of a run, by the
  Compiler, once. The test pool is touched exactly once.
- Never invent a number, a material property or a citation. Every claim in
  the report must trace to the ledger, the snapshot, the Materials Project or
  a published source found by the Scout.

## Simplicity criterion

All else being equal, simpler is better. A small improvement that adds ugly
complexity is not worth keeping; removing something and getting an equal or
better result is a great outcome. Because the val pool is small, treat an
improvement of less than 0.3 in `acceleration` as noise unless it comes with
a clear physical reason. A rule a materials scientist can read in one
paragraph beats a black box with the same score.

## Ideas to start from

- Put near-stable candidates (ehull at most 0.1) first: the hit definition
  requires it.
- Learn the systematic OptB88vdW gap underestimate from `train`
  (`mbj_bandgap` and `slme` are known there) and rank by the corrected gap.
- Train a regressor or classifier on `train` for SLME or for the hit itself,
  using the cheap columns plus composition features (fractions of each
  element, mean electronegativity, chalcogen or halide content).
- Combine a learned score with the stability gate, and compare with the
  Shockley-Queisser heuristic alone.
- Use space group or crystal system as a signal for direct gaps.
- Penalize metallic or near-zero gaps, and gaps above 2.5 eV.
- Look at what the best trial gets wrong (which hits it ranks low) using
  only train-set analogues, and form a physical hypothesis.

## Cross-checks outside JARVIS

For the final shortlist (`python lab/solar/harness.py shortlist -n 15`), the
Scout runs `python lab/solar/tools/mp_lookup.py <formula> ...` to see what the
Materials Project reports for the same compositions (stability, gap, whether
the material is known experimentally), and
`python lab/solar/tools/literature.py "<formula> solar absorber"` to find
published work. Agreement and disagreement both go in the report.

## The report

At the end the Scribe writes `runs/solar/report.md` for a scientifically
literate reader: the question, the data and its fingerprint, the pre-registered
definitions, the baselines, what was tried and what was learned (from the
ledger), the final held-out test result compared with the baselines on the
same test pool, the shortlist with Materials Project and literature
cross-checks, the limits of the result, and every source. Plain, smooth
prose; tables for numbers.
