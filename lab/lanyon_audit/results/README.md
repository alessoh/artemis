# Final results of the Artemis Lanyon wave-speed audit

The humans ran `harness.py final` once, on 1 November 2026 (02:08 to 02:14 UTC), in a fresh clone of this branch outside the lab's sandbox.

## Files

- `final.json`: the harness's complete output. It holds the census, the search rows, H1, H2, H3, the exploratory c = 1 census and the environment record.
- `final_run.log`: the console output of that run.
- `frozen.json`: the lab's freeze record, as printed by the lab at the end of its run (session 29d986e2…).
- `final_seed.txt`: the final seed. Its SHA-256 is `ed1474dc…96b5`, the value committed in `preregistration.md` (59fbe2c), which the harness checked before running. The pre-registration lets the seed enter the repository after the final run, so anyone can now rerun `final`.

## Provenance of `experiment.py`

The lab froze its search at sandbox commit 3ffc72b. The sandbox cannot push, so that commit is not on GitHub. `experiment.py` was rebuilt here from the full text the lab printed in its closing report.

The rebuilt file's SHA-256 is `cbb132e50cf6e78122f61e1b4e9904d38f0cbe238e0a02fe30faec8e60eabf9a`. This equals `experiment_sha256` in `frozen.json`, and the harness refuses to run `final` otherwise. All seven judge fingerprints in `frozen.json` also match the files on this branch. `final.json` records git commit 8f0b461 with `experiment.py` replaced by the frozen file.

## Outcome

| Hypothesis | Result |
|---|---|
| H1, census on the final seed | Refuted. P1 (6 IdealMHD fail C1 and C2) and P2 (3 hyperbolic_maxwell pass C1, fail C2) were confirmed. P3 (gr_hyperbolic_maxwell) was refuted: these specifications also fail C1. P4 (the other 60 pass) was refuted for the 3 gr_maxwell specifications. 12 specifications fail C1 and 15 fail C2. |
| H2, lab search | Holds on all 30 violating tasks. There are no extra violations in the 114 passing tasks. The search scored S = 26.273031 and V = 30. |
| H3, Lanyon's compiled C kernels | Holds on all 30 tasks. The C dissipation speed equals the specification's, and the spectral radius of the finite-difference Jacobian of the C flux exceeds it. |

**Exploratory, c = 1.** The c = 1 census is not pre-registered. With c fixed to 1, only the three gr_hyperbolic_maxwell specifications still fail. Their smallest ratios are 0.84 to 0.91.
