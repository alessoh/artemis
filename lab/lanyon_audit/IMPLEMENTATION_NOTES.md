# Implementation notes, written before the lab is launched

`preregistration.md` was committed (59fbe2c) before any checking code existed. This file records how the code implements it, where it refines it, and what the humans saw before launch. All of it is disclosed in the final report.

## Refinements of the pre-registered definitions

1. **Exact eigenvalues.** C1 and C2 are confirmed with exact eigenvalues, not mpmath's 50-digit QR algorithm as the pre-registration says.
   - Every flux in the 72 specifications is a rational function of the state, parameters and coordinates, and every sample is a binary64 number.
   - So the Jacobian at a point is an exact rational matrix. Its characteristic polynomial is computed over the rationals, and its real roots are isolated exactly, with multiplicity, by SymPy.
   - The roots are then evaluated to 60 digits. Listed and solver speeds are evaluated at 50 digits with mpmath.
   - Reason: mpmath's QR failed to converge on the curved-spacetime Jacobians, which have repeated eigenvalues with Jordan blocks. Any floating-point eigenvalue routine is inaccurate there.
   - The pre-registered tolerances (1e-12) are unchanged.
2. **Unconfirmable points.** A point admissible in double precision can turn out, exactly, to have complex eigenvalues.
   - Such a point is skipped as unconfirmable and counted; the census confirms the next candidate instead.
   - Until five candidates are confirmed by the C1 discrepancy, and five by the ratio, the census keeps going down the list.
3. **H2 comparison.** "No larger than the census's minimum" is implemented as `search_min_ratio <= census_min_ratio_confirmed`, both confirmed exactly.
4. **H3 details.**
   - The C kernel is compiled with `gcc -O0 -ffp-contract=off -std=c99`.
   - The finite-difference step is 1e-6 × max(1, |u_j|).
   - The C dissipation speed is compared with the specification's, both in double precision.
5. **Exploratory analysis, not pre-registered.** A census with the parameter c fixed to 1 is run for the specifications that have one. It is labelled exploratory everywhere.

## Bugs found and fixed before launch
- **Floats in the exact Jacobian.** In the first version, the "exact" Jacobian was built with SymPy's lambdify, which printed the constant 1/2 as the float 0.5.
  - The characteristic polynomial was then not exact, so repeated eigenvalues split.
  - This made the 2D and 3D compressible Euler specifications appear to fail C1 and made most of their points unconfirmable.
  - The Jacobian is now built by exact substitution, and every entry is checked to be rational.
- **Unconfirmable points.** The census stopped when one candidate turned out to have complex eigenvalues; see item 2.

## What the humans saw before launch
While building and testing the harness, Claude ran:
- the census on the development seeds `dev-census-test`, `fixtest` and `TEST-SEED-NOT-FINAL`;
- the starting search on eval-1.

The specifications that fail are therefore known before the lab runs:
- **On the test seed:** C1 fails for the 6 IdealMHD and 6 GeneralRelativisticMaxwell specifications; C2 fails for those 12 and the 3 hyperbolic_maxwell specifications.
- **Prediction outcomes:**
  - P1 and P2 hold.
  - P3 fails: gr_hyperbolic_maxwell also fails C1.
  - P4 fails for the three gr_maxwell specifications, which fail C1 and C2 when c ≠ 1.
  - The other 57 specifications pass.

The predictions themselves were committed before any of this code existed, and the final seed has not been used. H1 is decided on the final seed, but its outcome is very unlikely to differ from the development seeds. The lab's contribution is H2, the adversarial search, plus the explanations.

## Independent review before launch, and the changes made
A separate Claude agent, which had not written the code, audited it before launch. It confirmed the following as correct:
- the parser, checked against four specifications by eye;
- the exact eigenvalues, with no floating-point numbers left in the Jacobian;
- the C1 and C2 definitions and the census parameters;
- the prediction mapping and the H1/H2 logic;
- the reality of the IdealMHD failure, matching the textbook MHD speeds to 3e-50.

It reported these problems, all fixed before launch:

1. **Wrong C prefix (critical).** H3 used the file name as Lanyon's C prefix, which is wrong for 27 of 72 specifications (the DG variants and viscous_burgers_isotropic). The prefix is now the physics table's `'name`. `final` first compiles a driver for all 144 tasks and checks the C dissipation speed against the specification's; this preflight passes for all 144.
2. **Box not enforced.** The sampling box was not enforced, so a search could beat the census by leaving it. The harness now scores only points in the census box: magnitude at most 10, declared-positive variables at least 1e-2, other values 0 or at least 1e-2 in magnitude. This makes the H2 comparison like for like. The pre-registration's H2 text does not mention a box; this is a stated refinement.
3. **Final seed reached the runner.** The final seed string reached the process that runs untrusted search code.
   - The harness now computes each task's search seed as SHA-256(seed|search|task). This is domain-separated from the census stream, and only the integers are sent.
   - The runner runs with `python -I`.
   - During `final`, the seed file is moved out of the lab folder while the search runs.
   - The humans also read the frozen search before `final`.
   - The audit hook is not a full sandbox. `final` is run by Claude in a fresh clone outside the lab's sandbox, and records the Python environment.
4. **Nothing saved until the end.** `final` now saves after H1, after H2 and after H3. H3 records a failure per task instead of stopping.
5. **Census coverage now reported.** The H1 output lists tasks with fewer than 400 census points. These are the IdealMHD tasks, where only about 0.1 percent of baseline draws have positive pressure.
6. **H3 tolerances.** The H3 speed comparison and finite-difference step are now relative, as pre-registered. The step is 1e-3 max|u| when a component is 0. H3 reads "not applicable" (null) when there are no violations.
7. **Budget loopholes.**
   - Probes are capped at 24 tasks.
   - `evaluate` and `recheck` refuse to run when `ARTEMIS_RUNS_DIR` is set.
   - The RESULT line now reports whether the numeric keep rule is met.
8. **Stray specification files.** The harness refuses to run if the specification files differ from the manifest.
