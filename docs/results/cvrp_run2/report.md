# Artemis routing lab, run 2: report

*CVRPLIB X benchmark, short fixed time limits, one CPU core. Run of October 7–8, 2026. Final solver: `lab/cvrp/experiment.py`, sha256 3406e1b80391a04d746333a5eba509c46399a249d716ac3729150d1ef56018e9, git commit 02a87d6.*

## 1. Summary

**The question.** The lab had 3 seconds per 100 customers on one CPU core. Could it build a solver for the capacitated vehicle routing problem (CVRP) that gets closer to the best-known solutions (BKS) of the CVRPLIB X benchmark than PyVRP's default solver? And does what it learns carry over to larger problems it never saw? Run 2 began from run 1's solver. That solver had helped on held-out problems under 600 customers but showed no gain on larger ones. Run 2 aimed to keep the small-problem gain and add a gain on large problems.

**The answer.** On large problems, yes. On the eight held-out problems with 626 to 978 customers, the final solver beat PyVRP default on every problem: a mean of 0.66 percentage points (pp) closer to the BKS, 95 percent interval [−0.8115, −0.4989], sign test p = 0.00781. On the 17 held-out test problems (105 to 547 customers) it was not shown to be better. The mean difference was −0.0987 pp, but the interval [−0.2483, 0.0441] includes zero, it won 9 problems and lost 8, and the sign test gives p = 1.0. Run 2 therefore fixed run 1's weakness on larger problems. It did not confirm run 1's gain on smaller ones.

**Headline numbers** (mean gap to BKS in percent; seeds 0, 1 and 2; same time limits for every solver):

| Held-out split | Problems | Final solver | PyVRP default | Savings rule |
|---|---|---|---|---|
| test (105–547 customers) | 17 | 0.5734 | 0.672 | 4.8232 |
| scale (626–978 customers) | 8 | 1.3454 | 2.0054 | 4.9581 |

No solution, from any solver, beat a best-known solution.

## 2. Data and definitions

**Instances.** The data are the 100 instances of the CVRPLIB X benchmark (Uchoa et al. 2017) with their best-known solution costs. They come as mirrored by the PyVRP/Instances repository at commit 7474b068a8effa7f39448b241314b615c9271525. The snapshot in `lab/cvrp/data/` is frozen. The manifest records that all 100 BKS costs were recomputed exactly with the harness's own cost code. Instance names count the depot, so X-n548-k50 has 547 customers.

**Rounding.** The cost of a solution is the sum of Euclidean distances between consecutive stops, each rounded to the nearest integer with halves rounded up (the CVRPLIB convention). The harness, not the solver, checks every solution: each customer must be visited exactly once and no route may exceed the vehicle capacity. The harness then computes the cost.

**Time limit.** Each solve gets 3.0 seconds per 100 customers on one CPU core, in its own process with one numerical thread. The answer must arrive within 1.03 times the limit plus 0.5 seconds. CPU use must stay within 1.10 times the limit plus 4 seconds.

**Splits.**

| Split | Instances | Use |
|---|---|---|
| train | 52 | free probing |
| hunt | 11 | free probing; reserved for long runs |
| val | 12 | the loop's metric (60 evaluations and 20 rechecks per run) |
| test | 17 | held out, used once by `final` |
| scale | 8 | held out (626–978 customers), used once by `final` |

The val set has 114 to 894 customers. Five val problems are above 500 customers (X-n561-k42, X-n655-k131, X-n749-k98, X-n876-k59, X-n895-k37); run 2 added the last four.

**Metric and keep rule.** The metric is the mean gap, 100 × (cost − BKS) / BKS, over the twelve val instances with seed 0. Lower is better. A trial becomes a candidate only if its seed-0 val mean is at least 0.15 pp below the current best's. A candidate is kept only if its mean over seeds 1 and 2 (the "recheck") is at least 0.10 pp below the current best's on the same seeds. The final test runs every held-out problem with seeds 0, 1 and 2 for the lab's solver and for PyVRP default. It then reports a paired comparison per problem: the gap averaged over seeds, the mean difference with a 95 percent bootstrap interval (10,000 draws), problems won and lost, and an exact two-sided sign test.

**Fingerprints** (sha256, from `final_test.json`):

| File | sha256 |
|---|---|
| harness.py | 636766b31f5a6ca07ddb780b57e76b7966c25491cc9dc45f5ad7d882a4cc7fbc |
| runner.py | ea89ac0d1041a20c911fca3563ce1bbfb1be29872e0cfd0aa3f92629df4c7689 |
| reference.py (PyVRP default) | 9437f04a6a1c663aa623e0a20a1682a274862f5e378d677e18b8e8a3c95b4193 |
| data snapshot | e9543acc2aa0c6e98dde78cd77260059068e2e8c75c121de9ddae26faf8e500c |

**Baselines on val** (from `setup.log` and the ledger):

| Solver | Seeds | Mean gap | Median | Worst |
|---|---|---|---|---|
| Savings rule (Clarke–Wright + 2-opt) | 0 | 5.9741 | 5.811 | 9.4273 |
| PyVRP default | 0 | 1.3534 | 1.4436 | 2.6311 |
| PyVRP default | 1, 2 | 1.277 | 1.0012 | 2.6792 |
| Starting solver (run 1's granular_20) | 0 | 0.8814 | 0.805 | 2.0785 |
| Starting solver (run 1's granular_20) | 1, 2 | 0.8715 | 0.7782 | 1.9853 |

## 3. What the lab tried

The run used 40 of its 60 val evaluations and 2 of its 20 rechecks. The first evaluation recorded the starting point. The second recheck approved the only change kept. After wave 1 no wave kept anything. Having used at least 40 evaluations, the loop stopped under program.md's plateau rule. The final test ran once. The run's dollar spend against the 80-dollar limit is not recorded in the files available to me.

All mean gaps below are from the ledger (val, seed 0). Wave numbers come from the Compiler's notes. After the keep, a trial needed a val mean of 0.5295 or lower to become a candidate. None came closer than 0.6302.

| Wave | Trial | Hypothesis (shortened from the ledger note) | Val mean gap | Kept |
|---|---|---|---|---|
| — | starting solver | run 1's granular_20 | 0.8814 | (start) |
| 1 | shape_neighbours | neighbourhood size k = clamp(8 + customers per route, 12, 32) | 0.9153 | no |
| 1 | no_exhaustive_on_best | skip the full local-search pass on each new best | 0.9276 | no |
| 1 | **sector_decomposition** | **from 500 customers: 40% global search, then 3 rounds of re-solving angular groups of routes** | **0.6795** | **yes** (recheck 0.7589 vs 0.8715) |
| 2 | decomp_more_rounds | 20% global phase, 6 rounds | 0.6572 | no |
| 2 | route_cluster_groups | randomised barycentre clusters instead of angular sectors | 0.6706 | no |
| 2 | sector_size_150 | smaller sectors (~150 customers), decompose from 300 customers | 0.81 | no |
| 3 | savings_start | global phase starts from a savings solution | 0.7554 | no |
| 3 | sector_300 | larger sectors (n//300) | 0.7615 | no |
| 3 | savings_decomp_early | savings start, 10% global phase, 5 rounds | 0.66 | no |
| 4 | short_route_penalty | low starting load penalty on short-route instances | 0.739 | no |
| 4 | penalty_scaled | low starting penalty scaled by customers per route | 0.8774 | no |
| 4 | low_penalty_all | low starting penalty everywhere | 0.8923 | no |
| 5 | alt_groups | savings start, 10% global phase, 6 rounds alternating sectors and clusters | 0.6328 | no |
| 5 | alt_only | alternating groups, 4 rounds, no savings start | 0.6562 | no |
| 7 | alt_rounds_16 | alt_groups with 16 rounds | 0.6518 | no |
| 7 | alt_r16_from400 | 16 rounds, decompose from 400 customers | 0.6582 | no |
| 7 | alt_groups_200 | ~200-customer groups, 10 rounds | 0.6543 | no |
| 8 | route_groups_wedges | group size set by route count instead of customer count | 0.7613 | no |
| 9 | decomp_polish | decompose to 85% of the time, then global polish | 0.6641 | no |
| 9 | pure_decomp_savings | no global phase; decompose straight from savings routes | 0.6502 | no |
| 9 | sub_lean | lighter local-search settings in sub-solves | 0.6644 | no |
| 10 | sub_k12 | neighbourhood 12 in sub-solves | 0.767 | no |
| 10 | fleet_kmin | cap the fleet at the minimum number of vehicles | 2.6444 | no (worst instance 12.2596) |
| 10 | one_pass_decomp | a single decomposition round | 0.7157 | no |
| 11 | alt_groups (repeat) | identical code and seed, to measure noise | 0.6302 | — |
| 11 | sub_k45 | neighbourhood 45 in sub-solves | 0.7159 | no |
| 11 | sub_k30 | neighbourhood 30 in sub-solves | 0.6459 | no |
| 12 | alt_no_savings | alt_groups without the savings start | 0.6583 | no |
| 12 | alt_clusters_only | clusters in every round, no sectors | 0.6449 | no |
| 12 | sub_k_shape | sub-solve neighbourhood k = clamp(8 + customers per route, 20, 40) | 0.6851 | no |
| 13 | alt_reseed_1000 | noise: alt_groups, large-instance seed +1000 | 0.6851 | — |
| 13 | clusters_reseed_1000 | noise: alt_clusters_only, seed +1000 | 0.6947 | — |
| 13 | alt_reseed_2000 | noise: alt_groups, seed +2000 | 0.6367 | — |
| 14 | clusters_reseed_2000 | noise: alt_clusters_only, seed +2000 | 0.6816 | — |
| 14 | sector_reseed_2000 | noise: kept solver, seed +2000 | 0.6925 | — |
| 14 | sector_reseed_1000 | noise: kept solver, seed +1000 | 0.7001 | — |
| 15 | alt_reseed_3000 | noise: alt_groups, seed +3000 | 0.7429 | — |
| 15 | no_savings_reseed_1000 | noise: alt_no_savings, seed +1000 | 0.6672 | — |
| 15 | sector_reseed_3000 | noise: kept solver, seed +3000 | 0.7117 | — |

Four further ideas never reached val. A hybrid-genetic crossover (hgs_crossover) and a SISR-style ruin-and-recreate perturbation (sisr_perturbation) were dropped after train probes in wave 6. Two route-count grouping ideas failed the probe gate in wave 8 against alt_groups on train and hunt instances. route_groups was +0.185 pp worse on the eight short-route pairs. long_route_split was +0.132 pp worse on average and lost 5 of 6 pairs. Both figures check out against the probe details files.

**What was learned.** The one real gain came from decomposition on large instances. The kept solver first runs PyVRP on the whole problem for 40 percent of the time. It then re-solves groups of neighbouring routes as small, separate problems. The recheck shows where the gain came from. On seeds 1 and 2, the summed gap over the five large val instances fell from 5.8501 to 4.4851 and from 5.9006 to 4.594. The seven smaller instances, where the code is unchanged, moved by at most 0.031 in sum. Every later idea refined the decomposition or tuned the search below 500 customers, and none passed the candidate bar. Many variants of the decomposition clustered around a val mean of 0.63 to 0.67: more rounds, different group shapes, a savings start, no global phase, different sub-problem neighbourhoods. That cluster is within the noise described below, not a ranking.

**Noise is the main methodological lesson.** The solver stops on wall-clock time, so repeated runs differ. The lab measured how much:

- *Same code, same seed.* alt_groups run twice gave val means of 0.6328 and 0.6302. That is a difference of 0.003 on the mean and at most 0.07 on a single instance (X-n561-k42). The seven instances under 500 customers came out identical.
- *Same code, different seed on the large-instance path.* Changing only the seed offset of the decomposition moved the five-instance large sum by roughly ±0.3 to 0.5 and single instances by up to about 0.6. Sums of per-instance gaps, computed from the details files:

| Solver | Offset 0 | +1000 | +2000 | +3000 | Val means at those offsets |
|---|---|---|---|---|---|
| sector_decomposition (kept) | 4.503 | 4.751 | 4.659 | 4.889 | 0.6795 / 0.7001 / 0.6925 / 0.7117 |
| alt_groups | 3.942 | 4.570 | 3.990 | 5.264 | 0.6328 / 0.6851 / 0.6367 / 0.7429 |

  Across these four paired seed paths, alt_groups was ahead on three and behind on one. The paired differences reported by the Compiler (kept minus alt) are 0.56, 0.18, 0.67 and −0.37. That corresponds to roughly 0.02 on the val mean. alt_groups' edge is suggestive but not established, so the simpler kept solver stayed.
- *Seed 0 was a lucky draw on the small instances.* The kept solver's seven-instance small sum was 3.651 on seed 0, against 4.856 and 4.277 on seeds 1 and 2.
- *Unchanged code still drifts slightly.* Below 500 customers the kept solver runs the same code as the starting solver. Yet on seed 0 they differed on three of the seven small val instances (X-n209-k16, X-n359-k29, X-n449-k29), with small sums of 3.945 and 3.651. About 0.025 of the kept trial's 0.2019 seed-0 improvement therefore came from timing noise, not from the change. The recheck, where the small sums matched closely, is the better estimate.
- *Consequence.* On a single seed path, per-instance differences below about 0.3 pp should not be read as effects. Several apparent per-instance effects in waves 8 to 12 fall within this range, for example the per-instance results of the shape-based neighbourhood rules.

**The shape hypothesis was not supported.** program.md suggested that the right neighbourhood size might depend on the typical number of customers per route. The lab tried several forms, each computed from the instance itself:

- a global rule k = clamp(8 + q, 12, 32), where q is customers per route (shape_neighbours: 0.9153 against 0.8814 for fixed k = 20);
- group sizes set by route count (route_groups failed the probe gate; route_groups_wedges: 0.7613 against 0.6795);
- a per-group rule for sub-problems, k = clamp(8 + q, 20, 40) (sub_k_shape: 0.6851).

Starting load penalties chosen by route length (short_route_penalty 0.739, penalty_scaled 0.8774) did not help either.

**The alt_no_savings ledger note is wrong.** Its ledger note says that removing the savings start "costs nothing on large instances". The Compiler reports that this note was written before the result came in, and the result does not support it. On seed 0 the large-instance sum was 4.248 against 3.942 for alt_groups (val mean 0.6583 against 0.6328), so it was worse on that path. On the +1000 path it was 4.355 against 4.570, better on that path. Taken together, the savings start is not shown to matter either way.

**Below 500 customers, nothing helped.** Wave 1 and the Planner's offline checks tried history length, perturbation, operator choice, restarts, penalties, neighbourhood size, a savings start, decomposition below 500 customers and symmetric proximity. They also tried a SWAP* post-pass on final train solutions and intra-route 2-opt. None gave a lever (Compiler's notes; these offline checks are not in the ledger).

## 4. Final method

The final solver is PyVRP 0.14.0's default search, an iterated local search as the trial notes in the ledger describe it, with one setting changed. A second phase is added for large instances.

On every instance, each customer's granular neighbourhood is cut from PyVRP's default 50 nearest neighbours to 20, so each second of search tries more moves. This is run 1's change. Instances with fewer than 500 customers get nothing else: the solver is plain PyVRP with 20 neighbours for the whole time limit.

At 500 customers or more, the solver splits the time into two phases.

1. **Global phase.** PyVRP with 20 neighbours runs on the whole instance for 40 percent of the time limit.
2. **Decomposition phase.** Three rounds follow. In each round, every route is reduced to its barycentre (the average position of its customers). Routes are sorted by the angle of that barycentre around the depot. The sorted list is cut into n // 250 consecutive angular sectors with about the same number of customers each, so 2 sectors at 500–749 customers and 3 at 750–999. The starting point of the cut rotates from round to round so that sector borders move. Each sector's routes become a small CVRP of their own. PyVRP re-solves it, starting from those routes, with an equal share of the remaining time. The new routes replace the old ones only if they are feasible and shorter.

The solver stops 0.3 seconds before the limit. It uses only the instance it is given (coordinates, demands, capacity and distances), and every setting is computed from that instance. The approach belongs to the family of route-based decomposition methods for large CVRPs; the Scout pointed to Santini et al. (2023) on decomposition strategies. The specific rules (40 percent, three rounds, about 250 customers per sector) are the lab's choices.

## 5. Held-out results on test and scale

The final test ran once, with seeds 0, 1 and 2 for both the lab's solver and PyVRP default on every held-out problem. The savings rule is deterministic and ran once per problem. All runs were valid.

| Split | Solver | Runs | Mean gap | Median | Worst | Beats PyVRP default (same seed) |
|---|---|---|---|---|---|---|
| test | final solver | 51 | 0.5734 | 0.5831 | 1.5096 | 32/51 |
| test | PyVRP default | 51 | 0.672 | 0.6655 | 1.8415 | — |
| test | savings rule | 17 | 4.8232 | 4.5681 | 8.9275 | — |
| scale | final solver | 24 | 1.3454 | 1.2767 | 3.3506 | 22/24 |
| scale | PyVRP default | 24 | 2.0054 | 1.9866 | 3.8768 | — |
| scale | savings rule | 8 | 4.9581 | 4.6231 | 8.3024 | — |

**Paired comparison with PyVRP default** (from `final_test.json`; per problem, gap averaged over the three seeds; negative means the final solver is better):

| Split | Problems | Mean difference (pp) | 95% interval | Problems won / lost | Sign test p (two-sided) | Pairs won / lost |
|---|---|---|---|---|---|---|
| test | 17 | −0.0987 | [−0.2483, 0.0441] | 9 / 8 | 1.0 | 32 / 19 |
| scale | 8 | −0.66 | [−0.8115, −0.4989] | 8 / 0 | 0.00781 | 22 / 2 |
| pooled | 25 | −0.2783 | [−0.4316, −0.1262] | 17 / 8 | 0.10775 | 54 / 21 |

On **scale** the result is clear. The final solver was better on every one of the eight problems, by 0.21 to 0.91 pp per problem (seed-averaged, from the details files). The interval lies well below zero.

On **test** the result is not established. The interval includes zero and the problems split 9 to 8. Fifteen of the 17 test problems have fewer than 500 customers. On those the final solver is exactly run 1's solver, plain PyVRP with k = 20, so any difference there comes from that one change. Computed from the details files, those fifteen problems give a mean difference of −0.0896 pp, with 7 won and 8 lost. Only X-n502-k39 and X-n548-k50 reach the decomposition. The final solver was better on both, by 0.0443 and 0.2887 pp, and won all 6 seed pairs. The pooled result is negative with an interval excluding zero, but it is driven by scale. Its sign test (p = 0.10775) is not significant.

**Comparison with run 1.** program.md quotes run 1's held-out results.

| Split | Run 1 | Run 2 |
|---|---|---|
| test | 0.58 vs 0.73 for PyVRP default; better on 12 of 17 | 0.5734 vs 0.672; better on 9 of 17 problems (seed-averaged), 32 of 51 pairs; interval includes zero |
| scale | "no gain" (numbers not given in program.md) | 1.3454 vs 2.0054; better on 8 of 8; interval [−0.8115, −0.4989] |

Run 2 fixed run 1's weakness on larger problems. The decomposition turns "no gain" above 600 customers into a gain on every scale problem. On smaller problems the picture changed in the other direction. Run 1's test result apparently came from a single run per problem, since program.md lists the three-seed repeat as new in run 2. Under three seeds and a paired test, the same k = 20 solver no longer shows a reliable gain below 500 customers. Run 1's 12-of-17 should be read with the noise above in mind. The PyVRP default's own test mean also differed between the runs (0.73 against 0.672) on the same problems.

**Hunt probe.** After the final test, the Compiler ran both solvers once (seed 0, normal time limits) on three hunt instances. This is a single-seed probe, not a test result and not a long hunt run.

| Instance | Final solver: gap (cost) | PyVRP default: gap (cost) |
|---|---|---|
| X-n783-k48 | 1.270% (73305) | 2.636% (74294) |
| X-n936-k151 | 4.068% (138114) | 4.577% (138789) |
| X-n1001-k43 | 1.248% (73258) | 2.633% (74260) |
| mean | 2.1952 | 3.2818 |

## 6. Records

No new records. No solution in this run beat a best-known solution. Every gap in every details file, for every solver, split and seed, is zero or positive. A few runs matched a BKS exactly (gap 0.000): X-n115-k10 in the val runs, X-n275-k28 (seed 2, final solver) and X-n148-k46 (seed 1, PyVRP default) on test. Equalling a BKS is not a record. The harness's `verify` command was not run on any solution: no `runs/cvrp/records.tsv` exists. With no cost below a BKS anywhere, there was nothing to verify. The long hunt with `lab/cvrp/hunt.py` was not part of this run.

## 7. Limits

- **Short time limits.** Every result is for 3 seconds per 100 customers, between 3.15 and 29.34 seconds per held-out problem. Ranking at longer limits may differ, and nothing here speaks to how the solver compares with PyVRP default given minutes or hours.
- **One machine.** All runs used one sandbox, one core. program.md notes that the sandbox is faster than the build machine where the pre-run noise was measured, so absolute gaps are not portable.
- **Twelve practice problems, five of them large.** Every keep or discard rested on seed 0 over twelve val problems, plus seeds 1 and 2 for the one candidate. The noise study shows that a single seed path moves the large-instance sum by ±0.3 to 0.5. Only differences well above that can be trusted, which is why near-misses such as alt_groups were not kept.
- **Seed 0 flattered the val numbers.** Seed 0 was a favourable draw on the small val instances. The kept trial's seed-0 gain also included about 0.025 of timing noise on unchanged code.
- **The held-out set is shared with run 1.** The test and scale problems are the same as in run 1. The humans saw run 1's results on them while designing run 2, including the instruction to target larger problems. The agents never saw these results and never tuned on test or scale. Still, the held-out sets are no longer untouched by the design process.
- **Test is mostly unchanged code.** Fifteen of the seventeen test problems run the same solver as run 1, so test says little about run 2's change. The evidence for the decomposition comes from scale (eight problems) and two test problems.
- **Process incidents.** Twice an Experimenter named the test instance X-n502-k39 in a train probe. Both times the harness refused before running anything, so no test data was used. These refusals do not appear in the ledger, which records only runs that started. The account comes from the Compiler's notes. The ledger also records two train probes that were invalid because the trial file raised an error on import (low_penalty_all and short_route_penalty). They were fixed before evaluation.
- **No written Skeptic review in my sources.** I had no written Skeptic review. From the ledger and notes: the Skeptic rechecked the one candidate (0.7589 against a bar of 0.7715) and probed it on four non-val (train or hunt) instances (mean 1.7573 against 2.2633 for the then-current best). Caveats raised during the loop, such as the alt_no_savings note and the limits of per-instance effects, are reported above.
- **Spending.** The 80-dollar limit is stated in program.md. The actual spend is missing from my sources.

## 8. Sources

Data and tools:

- Uchoa et al. (2017). *European Journal of Operational Research* 257, 845. https://doi.org/10.1016/j.ejor.2016.08.012 (the CVRPLIB X benchmark; citation as given in program.md, DOI as recorded in the data manifest).
- PyVRP/Instances repository, commit 7474b068a8effa7f39448b241314b615c9271525. https://github.com/PyVRP/Instances (source of the instances and BKS costs).
- Wouda, Lan and Kool (2024). PyVRP: A high-performance VRP solver package. *INFORMS Journal on Computing*. https://doi.org/10.1287/ijoc.2023.0055 (the baseline solver and the base of the lab's solver; version 0.14.0).
- CVRPLIB, galgos.inf.puc-rio.br/cvrplib (address as given in the harness). The harness points here for checking a possible record against the current BKS table.

Literature returned by the Scout (`runs/cvrp/scout_notes.md`), with the Compiler's caveats:

- Vidal (2022). Hybrid genetic search for the CVRP: Open-source implementation and SWAP* neighborhood. *Computers & Operations Research* 140, 105643. https://doi.org/10.1016/j.cor.2021.105643
- Christiaens and Vanden Berghe (2022). Combining hybrid genetic search with ruin-and-recreate for solving the CVRP. *Journal of Heuristics* 28. https://doi.org/10.1007/s10732-022-09500-9
- Santini et al. (2023). Decomposition strategies for vehicle routing heuristics. *INFORMS Journal on Computing*. https://doi.org/10.1287/ijoc.2023.1288. *Caveat: the author list has not been checked against the DOI, so only the first author is named here.*
- Dörpinghaus and Gschwind (2024). *European Journal of Operational Research*. https://doi.org/10.1016/j.ejor.2024.05.033 (on operator ranking in ALNS, as the Scout described it; title not recorded).
- Schede et al. (2019). *Journal of Vehicle Routing Algorithms*. https://doi.org/10.1007/s41604-019-00010-9 (on automatic algorithm configuration of VRP solvers, as the Scout described it; title not recorded).

Further caveats from the Scout's notes. The Scout's tables of neighbourhood sizes and scaling were its own suggestions, not published results. The claim that PyVRP 0.14 adapts operator weights online and includes SWAP*, 2-opt and 3-opt in its default CVRP operators is unverified. The Planner found the default operators to be Relocate1, Relocate2, Swap11, Swap21, Swap22 and SwapTails. Toth and Vigo (2003) was not recovered by the Scout and is not cited.

Lab files: `lab/cvrp/program.md`, `lab/cvrp/harness.py`, `lab/cvrp/experiment.py`, `lab/cvrp/data/manifest.json`, `runs/cvrp/ledger.tsv`, `runs/cvrp/details/`, `runs/cvrp/final_test.json`, `runs/cvrp/final.log`, `runs/cvrp/setup.log`, `runs/cvrp/hunt_probe.log`, `runs/cvrp/hunt_probe_reference.log`, `runs/cvrp/compiler_notes.md`, `runs/cvrp/scout_notes.md`.

---

## Final ledger summary

**Run usage:** 40 of 60 val evaluations and 2 of 20 rechecks. One change was kept: sector_decomposition, commit 02a87d6.

**Best val mean gap (seed 0):**
- **Kept solver:** 0.6795. The recheck on seeds 1 and 2 gave 0.7589.
- **Starting solver:** 0.8814 (recheck 0.8715).
- **Baselines:** PyVRP default 1.3534 and savings 5.9741.
- **Lowest number in the ledger:** 0.6302, from the alt_groups noise repeat. It was never a candidate and was not kept.

**Held-out results** (final run once, seeds 0–2, mean gap %):

| Split | experiment.py | PyVRP default | Savings | Paired diff (95% CI) | Problems won/lost | Sign p |
|---|---|---|---|---|---|---|
| test (17) | 0.5734 | 0.672 | 4.8232 | −0.0987 [−0.2483, 0.0441] | 9 / 8 | 1.0 |
| scale (8) | 1.3454 | 2.0054 | 4.9581 | −0.66 [−0.8115, −0.4989] | 8 / 0 | 0.00781 |
| pooled (25) | — | — | — | −0.2783 [−0.4316, −0.1262] | 17 / 8 | 0.10775 |

**Hunt probe** (seed 0, X-n783-k48, X-n936-k151, X-n1001-k43): experiment.py has a mean gap of 2.1952, against 3.2818 for PyVRP default. No best-known solution was beaten.

---

*Copied from the lab's final message (session 7f5a6aec4b1a4273b729e9cbb714126b). The final solver is saved beside this file as experiment_final_run2.py; its SHA-256 (3406e1b80391...) matches the report. Claude re-checked the sign-test p-values (0.00781, 0.10775, 1.0) and the hunt-probe gaps against the snapshot's best-known costs; all match.*
