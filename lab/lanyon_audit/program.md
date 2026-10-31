# Program: wave-speed audit of Lanyon AI's verified-solver specifications

This is the human's instruction file for the Artemis lab. Read it first, then read `preregistration.md`.

## The question
Lanyon AI (github.com/lanyonai) generates PDE solver kernels and Lean proofs from one specification per equation system. We study 72 specifications in seven repositories, covering:

- Maxwell, curved-spacetime Maxwell, compressible Euler, ideal MHD;
- electrostatic Vlasov;
- advection-diffusion and Burgers.

Each specification lists the wave speeds of its equations. Its numerical method uses a dissipation speed, `amax`, built from them. Lanyon's proofs never state that either agrees with the eigenvalues of the flux Jacobian.

The frozen judge checks, for each of the 144 (specification, direction) tasks:

- **C1**: are the listed speeds the eigenvalues of the Jacobian of the specification's own flux?
- **C2**: is `amax` at least the spectral radius at both interface states?

The judge uses exact eigenvalues: rational characteristic polynomials with real roots isolated exactly. The hypotheses (H1, H2, H3), the predictions and the definitions are fixed in `preregistration.md`. Do not change them.

Your job is H2: build the best adversarial search for C2 violations. For every task, find interface points where `amax` falls furthest below the true fastest wave speed. Then explain what you find.

## Files
**Frozen** (never edit; their SHA-256 is in every ledger row):
- `harness.py`, `runner.py`, `kit.py`, `judge.py`, `specs.py`, `ckernel.py`, `prepare_data.py`
- `data/manifest.json`, `preregistration.md`

**Lanyon's repositories:**
- They are cloned at pinned commits into `lab/lanyon_audit/work/lanyon/` by `prepare_data.py`. Never copy them into the repository.
- Read them freely: specifications, C kernels and proofs.
- AdvectionDiffusion has no licence, so do not quote its code at length.

**Mutable:**
- `experiment.py` is the current best search.
- `trials/<name>.py` holds one file per trial.

**Records:** `runs/lanyon_audit/ledger.tsv`, `runs/lanyon_audit/details/` and census files, all written by the harness.

## The experiment interface
`experiment.py` defines `search(info, kit, seed)` and returns at most 20 interface points for one task. A point is `{"L": [...], "R": [...], "P": [...], "X": [...]}`:

- `L` and `R` are the left and right states, in the order of `info["state"]`;
- `P` holds the parameters, in the order of `info["parameters"]`;
- `X` holds the coordinates, in the order of `info["coordinates"]`, shared by both sides.

`info` holds the task's names, assumptions, flux, listed speeds and solver speeds as text. It covers one task.

`kit` offers:

| Call | Cost | Returns |
|---|---|---|
| `kit.sample(rng)` | free | a point from the pre-registered baseline sampler |
| `kit.evaluate(point)` | 1 call | `{"ratio", "amax", "rho", "c1"}`, or None if the point is not admissible |
| `kit.side(state, P, X)` | 1 call | the listed speeds, eigenvalues and spectral radius of one state, or None |
| `kit.remaining()` | free | the calls left in the budget |

The budget is 4,000 calls per task. When it is spent, calls return None.

The harness scores a run itself:

1. It re-evaluates every returned point.
2. It confirms the three smallest ratios with exact eigenvalues.
3. **V** is the number of tasks with a confirmed violation.
4. **S** is the sum over those tasks of (1 − smallest confirmed ratio).

Larger is better. A point counts only if it is admissible as defined in `preregistration.md`:

- it satisfies the specification's declared assumptions;
- its speeds are real;
- its Jacobian eigenvalues are real;
- its spectral radius is at least 1e-8.

**The sampling box (enforced).** The pre-registered sampler draws magnitudes from 1e-2 to 1e1, and the harness scores only points inside that box, so that results stay comparable with the census. The box has three conditions:
- every value has magnitude at most 10;
- a variable declared positive is at least 1e-2;
- any other value is either exactly 0 or at least 1e-2 in magnitude.

`kit.in_box(point)` tells you, for free. `kit.evaluate` returns None for a point outside the box. The scoring counts such points as `outside_box`.

## Rules (the harness enforces several)
**What `search()` may use:**
- Only its arguments, NumPy, SciPy (optimize, stats, special, linalg) and the standard modules `math`, `random`, `itertools`, `heapq`, `collections`, `functools`, `bisect`, `statistics`, `copy` and `time`.
- No files, no network and no harness imports. Use one core.

**Size limits:** the file must be under 40 KB, with at most 200 numeric constants.

**Physics knowledge is welcome.** Constructing states from primitive variables, Galilean shifts, extreme field orientations and local optimisation are all fair. Hard-coding a point found in an earlier run is not; the Skeptic rejects it. The search must find its points from the seed.

**Never run** `harness.py final`, and never look for the final seed. The census refuses the final seed anyway.

**Never run** `prepare_data.py --write-manifest`, and never edit `data/`.

## Setup (the Compiler does these once)
1. Run `pip install -r requirements-lanyon-audit.txt`.
2. Run `python lab/lanyon_audit/prepare_data.py`, which clones Lanyon's seven repositories and checks every file against the manifest. If it reports the snapshot missing or altered, stop and report exactly that.
3. Run `python lab/lanyon_audit/harness.py fingerprint` and then `describe`.
4. Run `python lab/lanyon_audit/harness.py census --seed dev`. It takes about 15 minutes. Record which specifications fail C1 and C2 on the development seed, and how that compares with the predictions printed at the end.
5. Run `python lab/lanyon_audit/harness.py evaluate --experiment lab/lanyon_audit/experiment.py --note "starting search"`. This gives the incumbent's score.

## The loop
**Free tools:**
- `probe` (14 tasks by default; `--tasks TEXT` selects at most 24) checks a trial before it costs anything.
- `census --tasks TEXT` examines one family on the dev seed.

**Budgeted tools** (they refuse to run if `ARTEMIS_RUNS_DIR` is set):
- `evaluate` runs all 144 tasks on seed eval-1. The budget is 30.
- `recheck` runs seeds eval-2 and eval-3. The budget is 10 runs.

**Keep rule.** A trial is a candidate only if all three hold:
1. its `evaluate` gives ΔS ≥ 0.05 and ΔV ≥ 0 against the incumbent (the RESULT line's `meets_numeric_keep_rule`);
2. its `recheck` gives S on both seeds at least the incumbent's eval-1 S;
3. the Skeptic approves it.

The Skeptic checks the absence of hard-coded points and of tricks, and that the explanation is physically right. Only the Compiler promotes a trial to `experiment.py`.

**Simplicity.** Prefer searches a physicist could describe in two sentences. A search that is equally good but simpler is a win.

**NEVER STOP** to ask the human whether to continue. Keep going until:
- the evaluation budget is used up;
- the spending limit stops you; or
- three consecutive waves bring no kept improvement, and at least 15 evaluations have been used.

## Ideas to try
1. Draw primitive variables (density, velocity, pressure, field) and convert them to the conserved state. This gives admissible MHD and Euler states far more often than the baseline, whose MHD states are mostly at negative pressure.
2. Add a uniform flow (Galilean shift) to both states. The MHD specification's Alfvén speed includes the flow velocity, so its error grows with u.
3. For each family, read `info["listed_speeds"]` and `info["solver_speeds"]`, and work out where `amax` falls furthest short of the true speeds. Then aim the search there. Examples:
   - small lapse α in the curved-spacetime specifications;
   - c > 1 with large χ and γ in hyperbolic Maxwell;
   - a strong transverse magnetic field in MHD.
4. Local optimisation of the ratio from the best sampled points, using Nelder–Mead or coordinate descent within the box.
5. Spend the budget where it pays. Tasks with no violation after a few hundred calls are likely sound; move on.

## What the lab must also explain
The Scribe's report gives, for every family:
- whether it fails C1 and C2 on the dev seed;
- a short derivation of why: the true eigenvalues against the listed ones, from the specification's own flux;
- the smallest ratio found, and the conditions under which the failure appears.

The report also includes the exploratory analysis with c fixed to 1 (`census --c1`), for the specifications that have a parameter c. That is the setting Lanyon evidently intends, and it shows which failures remain there.

Quote only harness output and the specification files. Never invent a number. Label everything beyond H1 to H3 as exploratory.

## Close
1. Run `python lab/lanyon_audit/harness.py freeze`.
2. Commit the frozen record and the ledger.
3. Dispatch the Scribe for `runs/lanyon_audit/report.md`.

The humans run `final` afterwards on the secret seed. It decides H1, H2 and H3; H3 compiles Lanyon's own C kernels at the census's worst points.
