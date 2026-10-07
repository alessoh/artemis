# Artemis routing lab, run 1: report

Session 60a600ded0794c62be81a7febf2bbca2, October 7, 2026. Written by the lab's Scribe; copied from the lab's final message. The lab's final solver is saved beside this file as experiment_final_run1.py (SHA-256 prefix aa1b808314cc, matching the report). Claude re-computed the test, scale and val tables from the per-instance costs and the snapshot's BKS, and every mean and win count matches.


## 1. Summary

The question, set in `lab/cvrp/program.md`, was this. If every solver gets the same short time limit on one CPU core (3 seconds per 100 customers), can the lab build a capacitated vehicle routing (CVRP) solver that gets closer to the best-known solutions (BKS) of the CVRPLIB X benchmark than PyVRP's default solver? And does what it learns carry over to larger instances it never saw?

On the 17 held-out test instances (105 to 547 customers), the answer is yes. The lab's solver had a mean gap to BKS of **0.5838%**, against **0.731%** for PyVRP default, and it beat PyVRP default on 12 of the 17 instances. On the 8 larger scale instances (626 to 978 customers), the two are **essentially tied on the mean (1.8856% vs 1.8738%)**. The lab's solver won on 6 of the 8, but lost heavily on one instance, X-n670-k130. The final solver is PyVRP 0.14.0's default search with one change: each customer considers its 20 nearest neighbours in the local search instead of 50. No solution beat a best-known solution.

| Split (seed 0, run once) | Instances | Lab solver mean gap % | PyVRP default mean gap % | Savings rule mean gap % | Lab beat PyVRP default |
|---|---|---|---|---|---|
| test | 17 | 0.5838 | 0.731 | 4.8232 | 12/17 |
| scale | 8 | 1.8856 | 1.8738 | 4.9581 | 6/8 |

## 2. Data and definitions

**Instances.** The data is the CVRPLIB X benchmark of Uchoa et al. (2017), 100 instances with 100 to 1,000 customers, together with the best-known solution costs. They come from the mirror in the PyVRP/Instances repository at commit `7474b068a8effa7f39448b241314b615c9271525`. The snapshot was built on 2026-10-07T16:29:34Z. According to `lab/cvrp/data/manifest.json`, the build recomputed all 100 published BKS costs with the harness's own cost code and matched every one exactly (`bks_recomputed_exactly: 100`). The snapshot stores the BKS costs but not the BKS routes.

**Rounding.** A solution's cost is the sum of Euclidean distances between consecutive stops, each rounded to the nearest integer with halves rounded up. This is the CVRPLIB convention. The harness checks every solution: each customer must be visited exactly once and no route may exceed the vehicle capacity. It then computes the cost itself. The solver never reports its own cost.

**Time limit.** Each instance gets 3.0 seconds per 100 customers on one CPU core (for example, 13.44 s for X-n449-k29 with 448 customers). Each solve runs in its own process. An answer is rejected if it arrives later than 1.03 × the limit plus 0.5 s, or if it uses more than 1.10 × the limit plus 4 s of CPU.

**Splits** (from the manifest):

| Split | Instances | Use |
|---|---|---|
| train | 52 | free probing |
| hunt | 15 | free probing; reserved for long record attempts |
| val | 8 | the experiment loop's metric (X-n115-k10, X-n162-k11, X-n209-k16, X-n256-k16, X-n303-k21, X-n359-k29, X-n449-k29, X-n561-k42) |
| test | 17 | held out, scored once by `final` (X-n106-k14 … X-n548-k50) |
| scale | 8 | held out, larger instances, scored once by `final` (X-n627-k43 … X-n979-k58) |

**Metric.** For each instance, gap = 100 × (cost − BKS) / BKS. The metric is the mean gap over the val instances with seed 0, and lower is better. The harness also reports the median gap, the worst gap, and on how many instances a solver beat the frozen PyVRP reference with the same seed.

**Pre-registered noise rule** (`program.md`). The solver stops on wall-clock time, so repeat runs of the same code differ. Before the run, identical PyVRP runs on val over seeds 0 to 4 gave mean gaps from 1.03 to 1.30 percent, a standard deviation of 0.085 percentage points. The keep rule was set from this:

- A trial is a *candidate* only if its seed-0 val mean gap is at least **0.15 percentage points** below the current best's.
- The Skeptic then reruns the trial on seeds 1 and 2. It is *kept* only if its mean gap over those two seeds is at least **0.10 percentage points** below the current best's on the same seeds.

The budget was 60 val evaluations and 20 rechecks. The run had to close early if three consecutive waves of trials produced no kept improvement.

**Fingerprint** (`python lab/cvrp/harness.py fingerprint`; the same values are recorded in `final_test.json`):

| Component | SHA-256 |
|---|---|
| harness | `19d536f83935281735fb44e9e9656f67fc98de903e19369f0ad1961789af5d05` |
| runner | `ea89ac0d1041a20c911fca3563ce1bbfb1be29872e0cfd0aa3f92629df4c7689` |
| reference (PyVRP default) | `9437f04a6a1c663aa623e0a20a1682a274862f5e378d677e18b8e8a3c95b4193` |
| data snapshot | `4ffd5d6fe45d4822222e45f8e84f4d8762463306066ebaf9cea1ef5cc5ac7e41` |
| final experiment.py | `aa1b808314cca16d8355817e95b2e1f2dbf604d7b06c84b407840d3196f95f95` |

Every row in the ledger carries harness `19d536f83935` and snapshot `4ffd5d6fe45d`.

## 3. Baselines

The lab used two baselines. The first is the frozen **PyVRP default** (`lab/cvrp/reference.py`): PyVRP 0.14.0's `solve()` with all settings at their defaults, under the same time limit. The second is the **savings rule**, built into the harness: Clarke and Wright's parallel savings construction followed by 2-opt inside each route. It is deterministic and takes well under a second. At the start of the run, `experiment.py` was a copy of the reference, and the lab scored it as well to see how much identical code drifts between runs.

| Val baseline | Seeds | Mean gap % | Median % | Worst % |
|---|---|---|---|---|
| Savings rule | 0 | 6.8453 | 6.0419 | 9.4273 |
| PyVRP default (reference) | 0 | 0.9698 | 1.1589 | 1.5338 |
| Starting experiment.py (copy of reference) | 0 | 0.9818 | 1.1652 | 1.5901 |
| PyVRP default (reference) | 1, 2 | 0.9248 | 0.7969 | 2.2794 |
| Starting experiment.py | 1, 2 | 0.9257 | 0.7969 | 2.3175 |

Identical code scored 0.9698 and 0.9818. The 0.012-point difference comes from X-n359-k29 (1.5338 vs 1.5901) and X-n561-k42 (1.2595 vs 1.2992). It shows how much wall-clock stopping moves the result.

## 4. What the lab tried

The lab ran four waves of trials. Each trial is a copy of `experiment.py` with one idea changed, and is kept in `lab/cvrp/trials/`. The table lists every val evaluation in the ledger. The descriptions are the ledger's notes.

| Wave | Trial | Hypothesis (ledger note) | Val mean gap %, seed 0 | Median % | Worst % | Beat ref. | Kept? |
|---|---|---|---|---|---|---|---|
| — | starting experiment.py | copy of PyVRP default | 0.9818 | 1.1652 | 1.5901 | 0/8 | starting point |
| 1 | granular_20 | 20 nearest neighbours instead of 50 | **0.5439** | 0.5809 | 1.0429 | 6/8 | **yes** (recheck seeds 1, 2: 0.6573 vs 0.9257, 12/16 beat reference; commit `74a1fc9`) |
| 1 | light_perturb | perturbation 1–10 instead of 1–25 | 1.3507 | 1.67 | 2.3187 | 0/8 | no |
| 1 | route_decompose | 50% full PyVRP, then barycentre-route subproblems of ~120 customers | 0.9879 | 1.1096 | 1.7725 | 3/8 | no |
| 2 | granular_30 | 30 neighbours instead of 20 | 0.8613 | 1.008 | 1.2969 | 4/8 | no |
| 2 | string_ruin | 60% ILS, then SISR string removal + greedy reinsertion + short polish | 0.5655 | 0.6396 | 1.0899 | 7/8 | no |
| 2 | decompose_20 | 70% full (20 nb), then ~200-customer barycentre regions, 1 s subruns | 0.5601 | 0.63 | 0.9831 | 6/8 | no |
| 3 | stall_restart | own ILS loop (= PyVRP, 20 nb) + fresh restart after 30% of time without a new best | 0.5393 | 0.5624 | 1.0429 | 6/8 | no |
| 3 | srex_pool | own ILS loop (= PyVRP, 20 nb) + elite pool of 8 with SREX route-exchange crossover every 1000 iters | 0.6153 | 0.6143 | 1.691 | 6/8 | no |
| 3 | sisr_sparse | own ILS loop (= PyVRP, 20 nb), SISR kick on 1 in 25 iterations | 0.6504 | 0.7277 | 1.405 | 6/8 | no |
| 4 | ops_warmup40 | 40% with Relocate1/Swap11/SwapTails only, then full operators from that solution | 0.5188 | 0.4812 | 1.3525 | 6/8 | no |
| 4 | ops_minimal | only Relocate1, Swap11, SwapTails (20 nb) | 0.5445 | 0.4894 | 1.3289 | 6/8 | no |
| 4 | warmup_decompose | 40% lean operators, 30% full operators, last 30% barycentre region re-solves | 0.5306 | 0.4919 | 1.3253 | 6/8 | no |

The run used 13 of 60 val evaluations and 2 of 20 rechecks. After granular_20 was kept, a new trial needed a seed-0 val mean gap of about 0.394% or lower to become a candidate (0.5439 minus 0.15). No trial reached that bar. The best was ops_warmup40 at 0.5188. Waves 2, 3 and 4 kept nothing, so under the three-waves rule in `program.md` the run closed.

**What was learned.** The only change that clearly helped was the smallest one: shrinking the granular neighbourhood from 50 to 20 nearest neighbours. The likely reason is that, at these time limits, a narrower neighbourhood lets the search complete more iterations, and that matters more than the extra moves a wide neighbourhood allows. The run did not measure iteration counts, so this explanation is a hypothesis. Thirty neighbours scored worse on val than twenty (0.8613). In the Planner's free train screens, 12 and 15 neighbours were also worse than 20, so 20 sits near the best point of a curve rather than at one end of it.

The other ideas fell into three groups.

- *Perturbation strength and search memory.* Lighter perturbation (light_perturb, 1–10 instead of 1–25) was clearly worse on val. Train screens of perturbation 1–40, history lengths of 100 and 1000, and penalty updates every 100 iterations were also worse.
- *Larger structural additions on top of the 20-neighbour search.* These were decomposition into barycentre regions, SISR-style string removal (the ruin-and-recreate idea of Christiaens and Vanden Berghe), restarts on stall, an elite pool with SREX crossover, and an operator warm-up. All landed between about 0.52 and 0.65. That is no better than granular_20 by more than the noise rule allows, and several were slightly worse.
- *Final polishing.* In train screens, a final intra-route 2-opt / or-opt pass gained at most 0.04%. Adding the Relocate3 and Swap31 operators was neutral.

Two facts about PyVRP shaped these results. First, PyVRP 0.14's `solve()` is an iterated local search with late acceptance, not the hybrid genetic search of Vidal (2022). Second, on plain CVRP only Relocate1, Relocate2, Swap11, Swap21, Swap22 and SwapTails apply. Removing the other operators (ops_minimal) therefore changed little.

The per-instance details show that seed noise is large on single instances. X-n449-k29 ranged from 0.98% to 1.69% at seed 0 across near-identical solvers (for example, 1.0429 for granular_20, 0.9831 for decompose_20 and 1.691 for srex_pool). With only eight val instances, differences of a few hundredths of a point in the mean are not meaningful.

Val per instance (seed 0) for the baselines and the kept trial:

| Instance | Customers | Time limit (s) | BKS | Savings gap % | PyVRP default cost | gap % | granular_20 cost | gap % |
|---|---|---|---|---|---|---|---|---|
| X-n115-k10 | 114 | 3.42 | 12747 | 5.6876 | 12747 | 0.0 | 12747 | 0.0 |
| X-n162-k11 | 161 | 4.83 | 14138 | 9.0395 | 14174 | 0.2546 | 14174 | 0.2546 |
| X-n209-k16 | 208 | 6.24 | 30656 | 5.8194 | 31046 | 1.2722 | 30747 | 0.2968 |
| X-n256-k16 | 255 | 7.65 | 18839 | 9.4273 | 19008 | 0.8971 | 18926 | 0.4618 |
| X-n303-k21 | 302 | 9.06 | 21736 | 8.7413 | 21966 | 1.0582 | 21916 | 0.8281 |
| X-n359-k29 | 358 | 10.74 | 51505 | 3.9802 | 52295 | 1.5338 | 51900 | 0.7669 |
| X-n449-k29 | 448 | 13.44 | 55233 | 5.8027 | 56052 | 1.4828 | 55809 | 1.0429 |
| X-n561-k42 | 560 | 16.8 | 42717 | 6.2645 | 43255 | 1.2595 | 43016 | 0.7 |

## 5. The final solver in plain words

The final solver is `lab/cvrp/experiment.py`, which is identical to `trials/granular_20.py` (SHA-256 prefix `aa1b808314cc`). It converts the instance into PyVRP's problem format: one depot, one vehicle type with the instance's capacity, as many vehicles as there are customers, and the harness's own rounded distance matrix. It then calls PyVRP 0.14.0's standard `solve()` until the time limit is reached and returns the best solution found.

The one change from PyVRP's defaults is that the local search's granular neighbourhood holds each customer's **20** nearest neighbours instead of **50**. In other words, the solver only tries to move a customer next to one of its 20 closest customers, and so it spends its few seconds on many cheap, promising moves rather than fewer broad ones. Everything else, including the iterated local search with late acceptance, the perturbation, the operators and the penalty management, is PyVRP's default. An operations researcher could reproduce the solver from this paragraph alone.

## 6. Held-out results on test and scale

`harness.py final` was run once, with seed 0, after the loop closed. It scored `experiment.py` and the frozen PyVRP reference on test and scale under the same time limits. The savings rule figures come from `final_test.json`.

| Split | Solver | Mean gap % | Median gap % | Worst gap % | Beat PyVRP default |
|---|---|---|---|---|---|
| test (17) | lab solver (granular_20) | **0.5838** | 0.4919 | 1.5096 | **12/17** |
| test (17) | PyVRP default | 0.731 | 0.6807 | 1.7096 | — |
| test (17) | savings rule | 4.8232 | 4.5681 | 8.9275 | — |
| scale (8) | lab solver (granular_20) | **1.8856** | 1.6524 | 4.5704 | **6/8** |
| scale (8) | PyVRP default | 1.8738 | 1.9225 | 2.944 | — |
| scale (8) | savings rule | 4.9581 | 4.6231 | 8.3024 | — |

**Test, per instance** (from `runs/cvrp/details/`; ✓ marks a lower cost than PyVRP default):

| Instance | Customers | Time limit (s) | BKS | PyVRP default cost | gap % | Lab solver cost | gap % | Lab better |
|---|---|---|---|---|---|---|---|---|
| X-n106-k14 | 105 | 3.15 | 26362 | 26439 | 0.2921 | 26570 | 0.789 | |
| X-n129-k18 | 128 | 3.84 | 28940 | 29137 | 0.6807 | 29026 | 0.2972 | ✓ |
| X-n148-k46 | 147 | 4.41 | 43448 | 43475 | 0.0621 | 43837 | 0.8953 | |
| X-n172-k51 | 171 | 5.13 | 45607 | 45784 | 0.3881 | 45779 | 0.3771 | ✓ |
| X-n190-k8 | 189 | 5.67 | 16980 | 17093 | 0.6655 | 17040 | 0.3534 | ✓ |
| X-n214-k11 | 213 | 6.39 | 10856 | 11002 | 1.3449 | 10932 | 0.7001 | ✓ |
| X-n233-k16 | 232 | 6.96 | 19230 | 19400 | 0.884 | 19487 | 1.3365 | |
| X-n251-k28 | 250 | 7.5 | 38684 | 39087 | 1.0418 | 38951 | 0.6902 | ✓ |
| X-n275-k28 | 274 | 8.22 | 21245 | 21474 | 1.0779 | 21280 | 0.1647 | ✓ |
| X-n294-k50 | 293 | 8.79 | 47161 | 47600 | 0.9309 | 47393 | 0.4919 | ✓ |
| X-n317-k53 | 316 | 9.48 | 78355 | 78368 | 0.0166 | 78420 | 0.083 | |
| X-n336-k84 | 335 | 10.05 | 139111 | 141236 | 1.5276 | 141211 | 1.5096 | ✓ |
| X-n376-k94 | 375 | 11.25 | 147713 | 147760 | 0.0318 | 147862 | 0.1009 | |
| X-n411-k19 | 410 | 12.3 | 19712 | 20049 | 1.7096 | 19891 | 0.9081 | ✓ |
| X-n459-k26 | 458 | 13.74 | 24139 | 24379 | 0.9942 | 24296 | 0.6504 | ✓ |
| X-n502-k39 | 501 | 15.03 | 69226 | 69376 | 0.2167 | 69342 | 0.1676 | ✓ |
| X-n548-k50 | 547 | 16.41 | 86700 | 87188 | 0.5629 | 87055 | 0.4095 | ✓ |

**Scale, per instance:**

| Instance | Customers | Time limit (s) | BKS | PyVRP default cost | gap % | Lab solver cost | gap % | Lab better |
|---|---|---|---|---|---|---|---|---|
| X-n627-k43 | 626 | 18.78 | 62164 | 63346 | 1.9014 | 63154 | 1.5926 | ✓ |
| X-n670-k130 | 669 | 20.07 | 146332 | 150640 | 2.944 | 153020 | 4.5704 | |
| X-n716-k35 | 715 | 21.45 | 43373 | 44216 | 1.9436 | 44129 | 1.743 | ✓ |
| X-n766-k71 | 765 | 22.95 | 114417 | 116648 | 1.9499 | 117087 | 2.3336 | |
| X-n801-k40 | 800 | 24.0 | 73311 | 74438 | 1.5373 | 74044 | 0.9998 | ✓ |
| X-n856-k95 | 855 | 25.65 | 88965 | 89691 | 0.8161 | 89446 | 0.5407 | ✓ |
| X-n916-k207 | 915 | 27.45 | 329179 | 335191 | 1.8264 | 334560 | 1.6347 | ✓ |
| X-n979-k58 | 978 | 29.34 | 118976 | 121441 | 2.0718 | 120963 | 1.6701 | ✓ |

The per-instance costs of the savings rule on test and scale are missing: `final_test.json` records only its summary, and no details file holds them.

**Reading the results.** On test, the lab's solver lowered the mean gap from 0.731% to 0.5838% and the median from 0.6807% to 0.4919%, and it won on 12 of 17 instances. It lost on five instances: X-n106-k14, X-n148-k46, X-n233-k16, X-n317-k53 and X-n376-k94. On three of these (X-n148-k46, X-n317-k53, X-n376-k94), PyVRP default was already within 0.07% of BKS.

On scale, the lab's solver had the lower median (1.6524% vs 1.9225%) and won on 6 of 8 instances. However, one large loss on X-n670-k130 (4.5704% against 2.944%) and a smaller one on X-n766-k71 (2.3336% vs 1.9499%) pull its mean to 1.8856%, slightly above PyVRP default's 1.8738%. The honest summary is that the improvement carried over to larger instances in most cases but not on average. On scale the mean is a tie.

**Additional probe on hunt instances (not a held-out score).** After the final run, the lab compared both solvers on three hunt instances using the free `probe` command (seed 0, same time rule). Hunt instances may be probed freely, so these numbers are informative but not held out.

| Instance | Lab solver gap % | PyVRP default gap % |
|---|---|---|
| X-n641-k35 | 1.3897 | 2.3915 |
| X-n819-k171 | 2.0048 | 2.1616 |
| X-n1001-k43 | 1.9819 | 2.4642 |
| mean | 1.7921 | 2.3391 |

## 7. Records

**No solution in this run beat a best-known solution.** No cost in the ledger or in any details file is below its BKS. The closest results were exact matches with the BKS, at 0.000% gap. On the val instance X-n115-k10 (cost 12747 = BKS), PyVRP default and nearly every trial reached it. One free train probe (string_ruin_ta on X-n167-k10, cost 20557 = BKS) did as well. No `harness.py verify` calls were made, and the long hunt runs (`lab/cvrp/hunt.py`) were not part of this run. The lab therefore makes no claim of a new record.

## 8. Limits

- **One seed on the held-out splits.** Test and scale were scored once, with seed 0. Single-instance noise is large: on X-n449-k29, near-identical solvers ranged from 0.98% to 1.69% at seed 0. So individual per-instance wins and losses, and the scale mean in particular, should not be overread.
- **A small val set.** The loop selected on eight instances. The kept change passed the pre-registered recheck on seeds 1 and 2 (0.6573 vs 0.9257). Still, the later trials that came close to it (0.5188 to 0.6504 on val) were each run on one seed, so they cannot be reliably ranked against it or against one another.
- **Tiny time limits.** Everything here was measured at 3 seconds per 100 customers. Whether 20 neighbours still beats the default of 50 with minutes or hours per instance was not tested.
- **One machine.** Wall-clock stopping ties the results to this machine's speed. On a faster or slower CPU the solver would run a different number of iterations and could give different gaps.
- **Python-level loops.** Several trials (stall_restart, srex_pool, sisr_sparse, string_ruin, the decomposition variants) wrapped PyVRP in Python control loops. Under these short limits that overhead may cost search time, so these results are not a fair verdict on the ideas themselves; native implementations were not tried.
- **The scale result is a tie on the mean.** Whatever the solver learned on instances of up to about 560 customers did not clearly carry over to 626–978 customers: it won 6 of 8 instances but one bad instance erased the gain in the mean.
- **The improvement is a tuning, not a new algorithm.** The final solver is PyVRP with one parameter changed. The result says that PyVRP's default neighbourhood size is too wide for very short runs on X instances. It does not show a new method.

## 9. Sources

- Uchoa et al., "New benchmark instances for the Capacitated Vehicle Routing Problem," *European Journal of Operational Research* 257, 845–858, 2017. doi:10.1016/j.ejor.2016.08.012, https://doi.org/10.1016/j.ejor.2016.08.012 (cited in `program.md` and the data manifest). Source of the X instances.
- PyVRP/Instances repository, commit `7474b068a8effa7f39448b241314b615c9271525`, https://github.com/PyVRP/Instances. Mirror of the X instances and BKS used for the frozen snapshot.
- CVRPLIB, http://galgos.inf.puc-rio.br/cvrplib (named in the harness as the place to confirm any record, since the snapshot's BKS may be out of date).
- Wouda, Lan, Kool, "PyVRP: a high-performance VRP solver package," *INFORMS Journal on Computing*, 2024. doi:10.1287/ijoc.2023.0055, https://doi.org/10.1287/ijoc.2023.0055. The baseline solver and the library the final solver uses.
- Vidal, "Hybrid genetic search for the CVRP: open-source implementation and SWAP\* neighborhood," *Computers & Operations Research* 140, 105643, 2022. doi:10.1016/j.cor.2021.105643, https://doi.org/10.1016/j.cor.2021.105643. Cited for hybrid genetic search, the SWAP\* neighbourhood and the granular neighbourhoods used in modern CVRP local search.
- Toth and Vigo (eds.), *Vehicle Routing: Problems, Methods, and Applications*, 2nd ed., SIAM, 2014. doi:10.1137/1.9781611973594, https://doi.org/10.1137/1.9781611973594. General reference for the CVRP and classical heuristics.
- Santini, Schneider, Vidal, Vigo, "Decomposition strategies for vehicle routing heuristics," *INFORMS Journal on Computing* 35(3), 2023. doi:10.1287/ijoc.2023.1288, https://doi.org/10.1287/ijoc.2023.1288. Cited for the barycentre/route decomposition idea behind the decomposition trials.
- SISR (Christiaens and Vanden Berghe): the string-removal ruin-and-recreate idea behind the string_ruin and sisr_sparse trials. Unverified reference: the lab did not confirm its bibliographic details, so none are given.
- Clarke and Wright (1964) savings heuristic, as named in the harness for the savings baseline. The lab did not verify its bibliographic details.

The Scout's literature brief, compiled from OpenAlex and arXiv, was used for orientation only. It contained numeric claims and descriptions that could not be verified, and this report repeats none of them. Each work above is cited only for the general idea it is known for.

---

## Final ledger summary

The run stopped after waves 2, 3 and 4 kept nothing, which is the program's three-empty-waves rule.

- **Budget used:** 13 of 60 val evaluations and 2 of 20 rechecks.
- **One kept change:** granular_20 (commit `74a1fc9`).
- **Best kept val mean gap:** 0.5439% on seed 0, and 0.6573% on recheck seeds 1 and 2.
  - Starting point: 0.9818% on seed 0, 0.9257% on seeds 1 and 2.
  - PyVRP default on val: 0.9698% on seed 0, 0.9248% on seeds 1 and 2.
  - Savings rule on val: 6.8453%.
- **Lowest val score of any trial:** ops_warmup40 at 0.5188%. It missed the 0.394 candidate bar, so it was not kept.

| Final (seed 0, run once) | Lab solver | PyVRP default | Savings |
|---|---|---|---|
| test mean gap % (17 instances) | **0.5838** (beat PyVRP on 12/17) | 0.731 | 4.8232 |
| scale mean gap % (8 instances) | **1.8856** (beat PyVRP on 6/8) | 1.8738 | 4.9581 |
| hunt probe, 3 instances (free, not held out) | 1.7921 | 2.3391 | — |

- **Records:** none. No cost was below a BKS.
- **Security:** the Skeptic reported that each agent's API key appears in full in its process command line (`ps aux`), so any process on this host can read it. Rotate the key and keep it out of process arguments.

## Final solver: lab/cvrp/experiment.py
