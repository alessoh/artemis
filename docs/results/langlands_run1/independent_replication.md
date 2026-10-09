# Independent replication of the Langlands run (Claude, 2026-10-08)

Session 5604bfb2f87a405f8752a5502414125c. The lab's commits stayed in its sandbox, so the promoted
experiment was rebuilt from the code block in the lab's final message.

- Rebuilt `experiment.py` SHA-256: fbe1a6557a673fbeb154f17e778d16bc2b4d71c00215792c66322f270b0b975e,
  identical to the lab's promoted file. It passes the harness's static check.
- Fresh clone of `langlands-lab` at 1ca1673; harness f5cf8570..., runner e03f4619..., data 42345fcb...,
  identical to the lab's fingerprints.
- `harness.py final` run once with ARTEMIS_RUNS_DIR in a scratch folder (`final_test_replication.json`).

Every reported number reproduced exactly: C1 mirror correlation -0.9824 [-0.9861, -0.9771];
C2 rho_ss 0.5313 [0.4605, 0.5944], rho_all 0.519, without rational models 0.5273;
H_B1 AUC 0.521744 (z 8.591); H_B2 AUC 0.542611 [0.535592, 0.549993] (z 15.114);
experiment minus simple rule +0.020866 [0.014059, 0.027839]; positive control 0.963781.

The experiment's internal gate did not fire on the final fit (its test scores differ from the base rule r).

## Post hoc checks on test (not pre-registered; the test split was already spent)

| Rule | Test within-conductor AUC [95% CI] | z |
|---|---|---|
| r = (-1 signs at p >= 5) - (-1 signs at p = 2, 3) | 0.531024 [0.525832, 0.53649] | 12.96 |
| m5_mult + 3 D - 2 m23 (Rohrlich-deviation integer rule) | 0.534564 [0.528907, 0.54021] | 12.49 |
| D alone: additive p >= 5 whose sign differs from (-1/p) | 0.517874 [0.513463, 0.522795] | 8.95 |

These rules were formed on train and val, so these numbers are out-of-sample in practice, but they
were not named in advance and should be confirmed on fresh conductors before being stated as results.

Paired comparisons on test (post hoc, 2,000 bootstrap draws over conductors):
r minus the pre-registered simple rule +0.00928 [0.003497, 0.015005];
Rohrlich integer rule minus r +0.003541 [-0.000469, 0.00757];
D alone minus the simple rule -0.00387 [-0.010907, 0.003288].
The size rule's gain is clear; the Rohrlich-deviation reading is not established by these checks.
