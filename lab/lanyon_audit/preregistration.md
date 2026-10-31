# Pre-registration: wave-speed audit of Lanyon AI's 72 verified-solver specifications

Committed on 31 October 2026, before any code exists that checks all 72 specifications. Hypotheses, predictions, definitions and the final seed's fingerprint are fixed here. Later changes to this file will show in git history; any change to the rules below after this commit must be reported as a deviation.

## Question
Lanyon AI's verified-solver repositories each pair a specification with a C kernel and Lean proofs. A specification lists the characteristic wave speeds of its PDE and the Lax-Friedrichs (Rusanov) dissipation speed its numerical method uses. The proofs never state that either agrees with the eigenvalues of the flux Jacobian.

For every specification and every coordinate direction, this audit asks two things:

- **C1, consistency.** Are the listed wave speeds the eigenvalues of the Jacobian of the specification's own flux?
- **C2, dissipation bound.** Is the method's dissipation speed at least the spectral radius of that Jacobian at both the left and right states?

## Material
There are 72 specification files (`specifications/*.rkt`), read at these pinned commits of github.com/lanyonai:

| Repository | Commit | Specs |
|---|---|---|
| MaxwellEquations | 801558f | 6 |
| GeneralRelativisticMaxwell | b13da44 | 6 |
| CompressibleEuler | a736aa5 | 6 |
| IdealMHD | beeff1a | 6 |
| ElectrostaticVlasov | f43676e | 6 |
| AdvectionDiffusion | 71d2724 | 21 |
| BurgersEquation | dd9b081 | 21 |

A task is one (specification, direction) pair, one per coordinate. Phase-space coordinates count for Vlasov.

The files are cloned at run time and never copied into the Artemis repository; AdvectionDiffusion carries no licence. Their SHA-256 values are recorded in `data/manifest.json` when the harness is built.

## Definitions (frozen)
**Interface point.** A point is the left state U_L, the right state U_R, the parameters P, and coordinate values X. X is shared by both sides, because a coordinate is continuous across an interface.

**Baseline sampler (seeded):**
1. Every state variable, on each side independently, gets a uniform random sign and a magnitude that is log-uniform on [1e-2, 1e1]. So does every parameter and every coordinate.
2. A variable the specification constrains by `(> v 0.0)` or `(>= v 0.0)` is drawn positive.
3. A draw is rejected unless every declared state assumption holds on both sides and every declared parameter assumption holds.

**Admissible point.** All of the following hold on both sides:
- every listed wave speed and the dissipation speed evaluate to finite real numbers;
- every eigenvalue of the flux Jacobian is real, with imaginary part at most 1e-9 × (1 + spectral radius);
- the spectral radius on at least one side is at least 1e-8.

**C1 mismatch.** The sorted listed speeds and the sorted Jacobian eigenvalues at U_L or U_R differ by more than 1e-12 × (1 + spectral radius) in some entry. This must be confirmed in 50-digit arithmetic (mpmath).

**C2 violation.** amax < (1 − 1e-12) × max(ρ(J(U_L)), ρ(J(U_R))), confirmed in 50-digit arithmetic.
- amax is the larger magnitude of the method's two speeds (the solver's `'speeds` entry) at the point.
- ρ is the spectral radius of the Jacobian.
- The ratio r = amax / max(ρ_L, ρ_R) is reported.

**Census.** For each task, 400 admissible points from the baseline sampler (at most 400,000 draws). The seed is derived from the final seed and the task name. A specification fails C1 (or C2) if any task of it has a confirmed C1 mismatch (or C2 violation).

## Predictions, made before the census code exists
Claude has read the specifications of MaxwellEquations, IdealMHD (1D and 2D), CompressibleEuler (1D), ElectrostaticVlasov (1x1v) and GeneralRelativisticMaxwell (gr_maxwell_1d). It has not read gr_hyperbolic_maxwell, the Burgers or the advection-diffusion files.

| | Specifications | Prediction | Confidence |
|---|---|---|---|
| P1 | 6 IdealMHD | fail C1 and fail C2 | high |
| P2 | 3 hyperbolic_maxwell | pass C1, fail C2 (cleaning waves faster than \|c\| when c > 1 and chi or gamma > 1) | high |
| P3 | 3 gr_hyperbolic_maxwell | same pattern as P2 (pass C1, fail C2) | low, not inspected |
| P4 | the other 60 | pass C1 and C2 | — |

P4 covers:
- maxwell, 3;
- gr_maxwell, 3;
- isothermal and compressible Euler, 6;
- es_vlasov, 6;
- advection-diffusion, 21;
- Burgers, 21.

## Hypotheses (decided on the final seed, once)
- **H1, census.** The census on the final seed matches P1 to P4 exactly. Each prediction is also reported on its own, as confirmed or refuted.
- **H2, lab search.** For every task with a confirmed C2 violation in the census, the lab's frozen search, run on the final seed, returns a confirmed violation with a ratio r no larger than the census's minimum for that task. The number of tasks where the search finds a confirmed violation that the census missed is reported, exploratory and not part of H2.
- **H3, shipped code.** For every task with a confirmed C2 violation in the census, evaluate Lanyon's compiled C kernel at the census's worst point. Both of these must hold:
  - its Lax-Friedrichs speed family gives the same dissipation speed as the specification, with relative difference at most 1e-9;
  - the spectral radius of a central finite-difference Jacobian of the C flux (relative step 1e-6) exceeds that speed by more than 1e-6 relative.

  This shows the violation is present in the code Lanyon ships, independently of the SymPy route.

## Final seed
- The SHA-256 of the final seed file (32 hex characters and a newline) is `ed1474dc162934bf7da8bd64afbecd39bf585237ac843997420e9b7e8e9796b5`.
- The seed is held by the humans and enters the repository only after the final run.
- The lab works on a separate development seed.
