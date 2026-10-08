# Run 2: lead agent's messages (from the watching window)

```
n lab/cvrp/harness.py probe --instances X-n101-k25 --note local check
  X-n101-k25     seed 0  cost    27610  gap  0.069%  (3.03 s)
PROBE {"utc": "2026-10-07T21:05:34Z", "kind": "probe", "split": "probe", "experiment": "lab\\cvrp\\experiment.py", "experiment_sha12": "7f3bdcd9772b", "git_commit": "e211010", "seeds": "0", "harness_sha12": "c8440b1e0816", "snapshot_sha12": "e9543acc2aa0", "note": "local check", "instances": 1, "mean_gap_pct": 0.0689, "median_gap_pct": 0.0689, "worst_gap_pct": 0.0689, "seconds": 3.0, "cpu_seconds": 0.0, "status": "ok"}

Local check passed. Its records are in runs\cvrp_local_check (not used by the lab).

=== Launch: starting the six-agent routing lab in a Modal sandbox
Session 7f5a6aec4b1a4273b729e9cbb714126b created; workspace https://github.com/alessoh/artemis#cvrp-lab
  sandbox: provisioning
  sandbox: starting
  sandbox: connecting
Lab started. Its first steps install PyVRP and record the baselines.

Watching session 7f5a6aec4b1a4273b729e9cbb714126b. The lab keeps running in the cloud even if
you close this window; reconnect with:
  python scripts/run_cvrp.py watch 7f5a6aec4b1a4273b729e9cbb714126b

I'll start by reading the program.Setup step 1–4 done (fingerprints recorded). Now running baselines → evaluate → recheck in the background, and dispatching Scout and Planner in parallel.Baselines are running in the background. Dispatching the Planner for wave 1.Setup is running (baselines → starting evaluation → recheck), and the Scout and Planner are working. I'll wait for their results.Waiting on the setup run and the Scout and Planner.
[turn finished]
The run is already under way, so this continues it rather than starting over. Checking progress:Status: on val with seed 0, the baselines scored 5.97% mean gap for savings and 1.353% for PyVRP default. The starting solver (granular_20) is halfway through its evaluation, and the recheck runs after that. The Scout and Planner are still working, and I'll be woken when they or the timer finish.
[turn finished]
The starting solver scored a 0.8814% mean gap on val with seed 0, against 1.3534% for PyVRP default; it beat PyVRP on 10 of 12. Dispatching three Experimenters for wave 1.Wave 1 is under way with three trials: shape_neighbours, no_exhaustive_on_best and sector_decomposition. The best mean gap is still 0.8814%. I'll be woken when results arrive.
[turn finished]
The Scout's brief is saved to runs/cvrp/scout_notes.md with caveats. The reference recheck (seeds 1 and 2) is running, and the three wave-1 Experimenters are working. I'll wait for their results.The reference recheck finished: PyVRP default averaged 1.277% over seeds 1 and 2. The starting solver's recheck is running now, and the Experimenters are probing. I'll wait for their results.
[turn finished]
Setup is complete. Over the recheck seeds 1 and 2, the starting solver averaged 0.8715% against PyVRP default's 1.277%. The first wave-1 result, shape_neighbours, scored 0.9153%, which is not a candidate. The other two wave-1 trials are still running.
[turn finished]
The no_exhaustive_on_best trial scored 0.9276%, which is not a candidate. That leaves sector_decomposition from wave 1 still running.
[turn finished]
Wave 1 produced a candidate: sector_decomposition scored a 0.6795% mean gap, against 0.8814% for the current best. Sending it to the Skeptic, and asking the Planner for wave 2 at the same time.**Wave 1 status:** three trials were tried. shape_neighbours scored 0.9153% and no_exhaustive_on_best scored 0.9276%; neither helped. sector_decomposition scored 0.6795% and is a candidate now with the Skeptic. The kept best is still 0.8814%, with 4 of 60 evaluations used. I'm waiting on the Skeptic's verdict and the Planner's wave-2 plan.
[turn finished]
Wave 2 is dispatched with three variants of the sector trial: sector_size_150, decomp_more_rounds and route_cluster_groups. I'm still waiting on the Skeptic's verdict on sector_decomposition.
[turn finished]
The decomp_more_rounds trial scored 0.6572%: a tie with the base and not a candidate. I'm waiting on the other two wave-2 trials and the Skeptic.
[turn finished]
The route_cluster_groups trial scored 0.6706%, also a tie and not a candidate. One slip to record: that Experimenter named a test instance (X-n502-k39) in a probe. The harness refused it before anything ran, so no test data was used. I'm waiting on sector_size_150 and the Skeptic.
[turn finished]
The Skeptic approved sector_decomposition: its recheck mean was 0.7589%, under the 0.7715% bar. Promoting it:sector_decomposition is promoted and committed as 02a87d6. The new best is 0.6795% on seed 0 and 0.7589% on the recheck seeds. The last wave-2 trial, sector_size_150, is still running.
[turn finished]
The Planner is drafting wave 3; I'll be woken when it reports.
[turn finished]
Dispatching the three wave-3 trials.Wave 3 is dispatched with three trials: savings_start, sector_300 and savings_decomp_early. The best stays at 0.6795%. I'm waiting for their results.
[turn finished]
The savings_start trial scored 0.7554%, which is worse than the base and not a candidate. Two wave-3 trials are still pending.
[turn finished]
The sector_300 trial scored 0.7615%, also worse than the base. One thing stands out: X-n876 jumped by about 0.9 points under both sector_150 and sector_300, so the base's 0.856% on that instance may itself be a lucky draw. I'm waiting for savings_decomp_early.
[turn finished]
The Planner is working on bolder wave-4 ideas; I'll be woken when it reports.
[turn finished]
Wave 4 is dispatched with three penalty trials: low_penalty_all, short_route_penalty and penalty_scaled. The best stays at 0.6795%, with 10 of 60 evaluations used. I'm waiting for their results.
[turn finished]
The short_route_penalty trial scored 0.739%, not a candidate. One finding matters for the rest of the run: X-n876 moved by +0.69 points with code identical to the base, so the decomposition path is very noisy on that instance. I'm waiting on the other two penalty trials.
[turn finished]
The penalty_scaled trial scored 0.8774%, clearly worse than the base. Waiting on low_penalty_all.
[turn finished]
The Planner is working on wave 5; I'll be woken when it reports.
[turn finished]
The Planner backs one combined idea, alt_groups, plus an ablation, alt_only. Dispatching both.Wave 5 is dispatched with two trials: alt_groups and its ablation alt_only. The best stays at 0.6795%, with 13 of 60 evaluations used. I'm waiting for their results.
[turn finished]
alt_groups scored 0.6328%, a near-miss short of the 0.5295% bar. While alt_only runs, I'll look at the PyVRP 0.14 operator set myself.PyVRP 0.14 has no SWAP* and no crossover, which confirms the Planner's reading. I'm waiting on alt_only.
[turn finished]
Wave 6 is dispatched with two bold trials: hgs_crossover and sisr_perturbation. Each Experimenter measures on train first and runs a val evaluation only if its trial is on par with the base. I'm waiting for their results.
[turn finished]
The Planner is working on wave 7; I'll be woken when it reports.
[turn finished]
That notice was for the HGS result I already collected; the inbox is empty. Still waiting on the Planner's wave 7.
[turn finished]
Dispatching the three wave-7 trials.Wave 7 is dispatched with three trials built on alt_groups: alt_rounds_16, alt_groups_200 and alt_r16_from400. The best stays at 0.6795%, with 15 of 60 evaluations used. I'm waiting for their results.
[turn finished]
The alt_rounds_16 trial scored 0.6518%, worse than alt_groups and not a candidate. I'm waiting on the other two wave-7 trials.
[turn finished]
The alt_r16_from400 trial scored 0.6582%, also not a candidate. I'm waiting on alt_groups_200.
[turn finished]
The Planner is working on wave 8; I'll be woken when it reports.
[turn finished]
Wave 8 is running with three trials:
- **route_groups:** the number of decomposition groups is set by route count (about 15 routes per group) instead of customer count. It runs on val only if a short practice run on non-val instances passes.
- **route_groups_wedges:** the same rule applied to the kept solver, as a check on whether alt_groups' extra parts are worth keeping.
- **long_route_split:** more time for the whole-instance search before the solver splits the routes into groups, given only to instances with long routes. Same practice-run gate.

So far 18 of 60 evaluations are used and the best kept val mean gap is 0.6795. I'll collect the three results when they come in.
[turn finished]
route_groups failed its probe gate, so no val evaluation was spent on it. It made the many-short-route instances 0.185 pp worse on average (paired probe mean 1.4975 vs 1.3639 for alt_groups), which does not support the shape hypothesis in that form. The other two wave-8 trials are still running.
[turn finished]
long_route_split also failed its probe gate, so no val evaluation was spent on it. It was 0.132 pp worse than alt_groups across the six paired runs and lost five of the six pairs. route_groups_wedges is still running.
[turn finished]
Wave 8 is done and kept nothing:
- **route_groups:** failed its probe gate, 0.185 pp worse than alt_groups on the many-short-route instances. No val evaluation spent.
- **long_route_split:** failed its probe gate, 0.132 pp worse than alt_groups and lost five of six paired runs. No val evaluation spent.
- **route_groups_wedges:** evaluated on val at 0.7613. It was worse than the kept solver (0.6795) on four of the five large instances; n876 nearly doubled, from 0.856 to 1.629.

So sizing decomposition groups by number of routes does not help, and giving more time to the whole-instance search before decomposition hurts. The best kept val mean gap is still 0.6795 (sector_decomposition), with 19 of 60 evaluations used.

The run needs at least 40 evaluations before it may stop on a plateau. I've asked the Planner for a bolder wave 9: three ideas that go straight to val without probe gates. I'll dispatch the trials when its plan arrives.
[turn finished]
Wave 9 is running with three trials, all built on alt_groups and all going straight to val:
- **decomp_polish:** a short whole-instance polish in the last 15% of the time, after the group re-solves.
- **pure_decomp_savings:** skips the whole-instance phase and starts the group re-solves straight from the savings solution.
- **sub_lean:** a leaner search setup inside each group re-solve: shorter acceptance history and no extra full search after each new best.

The Planner doesn't expect any of them to reach the 0.5295 bar. They are there to show which part of the time budget matters. Best kept is still 0.6795, with 19 of 60 evaluations used. I'll collect the results as they come in.
[turn finished]
decomp_polish scored 0.6641 on val and is dropped. Moving 15% of the time from the group re-solves to a final whole-instance polish made the five large instances worse overall (gap sum 4.32 vs 3.94); only n655 improved. Twenty of 60 evaluations are used. pure_decomp_savings and sub_lean are still running.
[turn finished]
pure_decomp_savings scored 0.6502 on val: worse than alt_groups (0.6328) and nowhere near the 0.5295 bar. So a short whole-instance phase before decomposition still pays off; the gain from cutting that phase stops somewhere between 10% of the time and none. Twenty-one of 60 evaluations are used. sub_lean is still running.
[turn finished]
Wave 9 status: decomp_polish 0.6641, pure_decomp_savings 0.6502 and sub_lean 0.6644. No keep; best kept is still 0.6795, with 22 of 60 evaluations used. I'm asking the Planner for wave 10.Wave 9 kept nothing. All three trials were built on alt_groups (0.6328, the best unkept result) and all three scored worse than it:

| Trial | Val mean | Large-instance gap sum (alt_groups: 3.94) |
|---|---|---|
| decomp_polish (final whole-instance polish) | 0.6641 | 4.32 |
| pure_decomp_savings (no whole-instance phase) | 0.6502 | 4.151 |
| sub_lean (leaner search inside each group) | 0.6644 | 4.32 |

So the short whole-instance phase at the start is worth keeping, and none of these three changes beats the current group re-solves. One recurring signal: n655 improved in all three trials (0.076–0.111 vs 0.158), though that may be noise.

The best kept val mean gap is still 0.6795 (sector_decomposition), with 22 of 60 evaluations and 2 of 20 rechecks used. At least 18 more evaluations are needed before the run may stop on a plateau.

I've asked the Planner for wave 10:
- new structural ideas for the large instances;
- at least one trial that simplifies the kept solver;
- any untried lever below 500 customers, such as a custom between-route post-pass or a different PyVRP move set.

I'll dispatch the trials when the plan arrives.
[turn finished]
Wave 10 is running with three trials:
- **fleet_kmin:** limits the number of routes to the minimum the total demand allows, falling back to an unlimited fleet if that proves infeasible. The Planner found the solver often uses one or two spare routes, and those runs tend to have larger gaps.
- **sub_k12:** 12 nearest neighbours instead of 20 inside each group re-solve, so the search makes more moves per second.
- **one_pass_decomp:** a simplification test that re-solves each sector once instead of three rounds.

The Planner also checked two post-search passes offline on existing training-instance solutions and found them dead ends. A SWAP* pass gained a median of zero, and a final 2-opt pass gained almost nothing under 600 customers.

The best kept val mean gap is still 0.6795, with 22 of 60 evaluations used. I'll collect the results as they arrive.
[turn finished]
sub_k12 scored 0.767 on val and is dropped. Twelve neighbours in the group re-solves made four of the five large instances worse, and their gap sum rose from 3.94 to 5.55. The Experimenter worried that the small instances had also got worse, but n303 (0.828) and n449 (1.043) match the base exactly, so the small instances didn't move. Twenty-three of 60 evaluations are used, and fleet_kmin and one_pass_decomp are still running.
[turn finished]
fleet_kmin scored 2.6444 on val and is dropped. Limiting the fleet to the minimum number of routes made the search far worse on the nearly-full instances (n895 12.26, n449 7.16, n749 4.20). The spare route isn't wasted slack; it is what lets the search pack those instances. Twenty-four of 60 evaluations are used, and one_pass_decomp is still running.
[turn finished]
Wave 10 status: fleet_kmin 2.6444, sub_k12 0.767 and one_pass_decomp 0.7157. No keep; best kept is still 0.6795, with 25 of 60 evaluations used. I'm asking the Planner for wave 11.Wave 10 status: fleet_kmin 2.6444, sub_k12 0.767 and one_pass_decomp 0.7157. No keep; best kept is still 0.6795, with 25 of 60 evaluations used. I'm asking the Planner for wave 11.Wave 10 kept nothing, and all three trials scored worse than the kept solver (val seed 0):

| Trial | Val mean | What it showed |
|---|---|---|
| fleet_kmin | 2.6444 | Limiting the fleet to the minimum routes badly hurts the nearly full instances: n895 12.26, n449 7.16, n749 4.20. |
| sub_k12 | 0.767 | Fewer neighbours inside the group re-solves hurt four of the five large instances. |
| one_pass_decomp | 0.7157 | Re-cutting the sector borders over several rounds matters, mostly for n895 (1.792 vs 1.424). |

The best kept val mean gap is still 0.6795 (sector_decomposition), with 25 of 60 evaluations used. At least 15 more are needed before the run may stop on a plateau.

I've asked the Planner for wave 11. It is choosing three of these:
- combining earlier near-misses;
- more neighbours (about 30) inside the group re-solves;
- a softer way of handling spare routes;
- re-running the unchanged kept solver on seed 0 to measure val noise for the report.

I'll dispatch the trials when its plan arrives.
[turn finished]
Wave 11 is running with three val evaluations, all on alt_groups (0.6328, the best result not kept):
- **sub_k30:** 30 nearest neighbours inside the group re-solves instead of 20. Twelve made things clearly worse, so this tests the other direction.
- **sub_k45:** 45 neighbours, to show whether any gain keeps growing or levels off.
- **noise_repeat:** alt_groups run again unchanged on seed 0. It gives the report a direct measure of run-to-run noise, and shows whether alt_groups' 3.94 large-instance sum, the yardstick for waves 8–10, was a lucky draw.

The best kept val mean gap is still 0.6795, with 25 of 60 evaluations used. I'll collect the results as they come in.
[turn finished]
The noise repeat of alt_groups scored 0.6302 against 0.6328 the first time, so re-running the same code on the same seed moves the mean by only 0.003. The seven instances under 500 customers gave identical costs; only the large instances moved, by at most 0.073 (n561). Differences between trials on seed 0 therefore come mostly from the code change, not timing noise; the larger spread comes from changing the seed. Twenty-six of 60 evaluations are used, and sub_k30 and sub_k45 are still running.
[turn finished]
sub_k45 scored 0.7159 on val and is dropped: 45 neighbours raised the large-instance gap sum from 3.94 to 4.94. With twelve neighbours at 5.55, the default 20 looks close to the sweet spot. Twenty-seven of 60 evaluations are used. sub_k30 is still running.
[turn finished]
Wave 11 status: sub_k30 0.6459, sub_k45 0.7159, and the alt_groups noise repeat 0.6302 against 0.6328 before. No keep; best kept is still 0.6795, with 28 of 60 evaluations used.Wave 11 kept nothing. Val seed-0 means, against alt_groups at 0.6328:

| Trial | Val mean | Large-instance gap sum (alt_groups 3.94) |
|---|---|---|
| noise repeat of alt_groups | 0.6302 | 3.91 |
| sub_k30 (30 neighbours in each group re-solve) | 0.6459 | 4.10 |
| sub_k45 (45 neighbours) | 0.7159 | 4.94 |

- **Noise:** re-running the same code on the same seed moves the mean by only 0.003. The seven instances under 500 customers come out identical, and large instances move by at most 0.07. So differences between trials on seed 0 come from the code change; they may still not hold on other seeds.
- **Neighbours in the group re-solves:** 20 is near the best setting. Twelve gave a sum of 5.55, 30 gave 4.10 and 45 gave 4.94.
- **Route shape:** at 30 neighbours, the two long-route instances improved (n876 −0.138, n895 −0.041) while the short-route ones got worse. This is weak support for the hypothesis that neighbourhood size should depend on customers per route.

The best kept val mean gap is still 0.6795, with 28 of 60 evaluations used and 12 more needed before the run may stop. I've asked the Planner for wave 12. The options on the table:
- choosing the neighbour count in each group from its customers per route;
- a noise repeat of the kept solver;
- a two-round version of the kept solver, as a simplification test.

I'll dispatch the trials when the plan arrives.
[turn finished]
Wave 12 is running with three val trials, all built on alt_groups:
- **sub_k_shape:** each group re-solve gets its neighbour count from customers per route (between 20 and 40). That is about 31 for long-route n895 and stays at 20 for the short-route instances. It is the most direct test yet of the program's route-shape hypothesis.
- **alt_no_savings:** a simplification test that drops the savings starting solution and its code, to see whether it pays for itself.
- **alt_clusters_only:** a simplification test that uses only the cluster groups in every round and drops the angular wedges.

I'm not spending a recheck on alt_groups. Its seed-0 gain over the kept solver (about 0.05) is far below the 0.15 candidate bar, and the Planner agrees it couldn't pass the keep rule.

The best kept val mean gap is still 0.6795, with 28 of 60 evaluations used.
[turn finished]
alt_no_savings scored 0.6583 on val and is dropped. Without the savings start, the large-instance gap sum rose to 4.249 (alt_groups 3.94), all of it on n749 (1.437 vs 0.985); the other large instances improved slightly.

The Experimenter's ledger note for this run says the change "costs nothing". It was written before the result came in and contradicts it, so I'll flag it to the Scribe as wrong.

Twenty-nine of 60 evaluations are used, and sub_k_shape and alt_clusters_only are still running.
[turn finished]
alt_clusters_only scored 0.6449 on val. It drops the angular wedges and 21 lines of code, and its large-instance gap sum of 4.088 just meets the 4.10 cutoff. So one grouping rule is close to enough, but the trial is still a little worse than alt_groups (0.6328) and not a candidate. Thirty of 60 evaluations are used, and sub_k_shape is still running.
[turn finished]
Wave 12 status: sub_k_shape 0.6851, alt_no_savings 0.6583 and alt_clusters_only 0.6449. No keep; best kept is still 0.6795, with 31 of 60 evaluations used.Wave 12 kept nothing. All three trials were built on alt_groups (val mean 0.6328; the sum of its five large-instance gaps is about 3.92):

| Trial | Val mean | Large-instance gap sum | What it showed |
|---|---|---|---|
| sub_k_shape | 0.6851 | 4.569 | Choosing the neighbour count from customers per route fails here too. It gave n895 about 32 neighbours and n895 got much worse (1.625). |
| alt_no_savings | 0.6583 | 4.249 | The savings start is needed, mainly for n749. |
| alt_clusters_only | 0.6449 | 4.088 | Dropping the angular wedges is nearly free (21 fewer lines), but the trial is still slightly worse than alt_groups. |

The best kept val mean gap is still 0.6795, with 31 of 60 evaluations used. Nine more are needed before the run may stop on a plateau.

I've asked the Planner for wave 13 and a sketch of wave 14, including any bold attempt at the 0.5295 bar. I'll dispatch the trials when the plan arrives.
[turn finished]
Wave 13 is running: three val evaluations that measure noise rather than test new ideas.

The Planner corrected its earlier noise estimate. Two near-identical neighbour settings gave n895 gaps of 1.095 and 1.625, so on the large instances, trial-to-trial differences may be mostly the random search path rather than the code change. Each of the three runs keeps the code and changes only the random seed on the large instances; the seven small instances stay identical:
- **alt_reseed_1000:** alt_groups with the large-instance seed offset by 1000.
- **alt_reseed_2000:** the same with an offset of 2000.
- **clusters_reseed_1000:** the simpler alt_clusters_only variant with an offset of 1000.

Together they show how much each large instance moves between search paths, and so which earlier results were real code effects.

The best kept val mean gap is still 0.6795, with 31 of 60 evaluations used. I'll collect the results as they come in.
[turn finished]
The first noise run, alt_reseed_1000, scored 0.6851: alt_groups' exact code with only the large-instance seed changed. That is no better than the kept solver's 0.6795. Single large instances moved by up to ±0.4 (n561 +0.43, n895 +0.39, n876 −0.26), and the val mean by about 0.05. So alt_groups' seed-0 edge over the kept solver may be mostly a lucky search path. Thirty-two of 60 evaluations are used; alt_reseed_2000 and clusters_reseed_1000 are still running.
[turn finished]
clusters_reseed_1000 scored 0.6947 on val, against 0.6449 for the same alt_clusters_only code on its original seed. Four of the five large instances got worse and their gap sum rose from 4.088 to 4.686, so its seed-0 score also looks like a lucky search path. Thirty-three of 60 evaluations are used, and alt_reseed_2000 is still running.
[turn finished]
Wave 13 kept nothing. Its three noise runs show that changing only the random seed on the large instances moves single gaps by up to ±0.4 and the val mean by up to 0.05:

| Run (code unchanged, large-instance seed changed) | Val mean | Large-instance gap sum |
|---|---|---|
| alt_groups, seed 0 (two runs) | 0.6328 / 0.6302 | 3.94 / 3.91 |
| alt_groups, offset 1000 | 0.6851 | 4.569 |
| alt_groups, offset 2000 | 0.6367 | 3.989 |
| alt_clusters_only, seed 0 | 0.6449 | 4.088 |
| alt_clusters_only, offset 1000 | 0.6947 | 4.686 |

Across its three paths, alt_groups' large-instance sum averages about 4.17, against 4.50 for the kept solver on seed 0. That is worth about 0.03 on the val mean, far below the 0.15 needed to be a candidate. Most of what looked like progress in waves 5–12 was a lucky search path.

Wave 14 is now running, following the Planner's sketch for this case:
- **sector_reseed_1000** and **sector_reseed_2000:** the kept solver (sector_decomposition) with its large-instance seed offset. This gives it three search paths too, for a fair comparison with alt_groups in the report.
- **clusters_reseed_2000:** a third path for the simpler cluster-only variant.

The best kept val mean gap is still 0.6795, with 34 of 60 evaluations used. These three bring it to 37.
[turn finished]
clusters_reseed_2000 scored 0.6816 on val. Across its three search paths, alt_clusters_only averages about 0.674 (0.6449, 0.6947, 0.6816), level with the kept solver's 0.6795. Thirty-five of 60 evaluations are used; the two kept-solver reseed runs are still running.
[turn finished]
sector_reseed_2000 scored 0.6925 on val: the kept solver's code with only the large-instance seed changed, against 0.6795 on seed 0. Single large instances moved by up to ±0.27, but the mean moved by only 0.013. Thirty-six of 60 evaluations are used; sector_reseed_1000 is still running.
[turn finished]
Wave 14 is done and kept nothing; all three runs were noise measurements. Each solver has now been run on three different seeds on the large instances:

| Solver | Val means (seed 0 / +1000 / +2000) | Average | Large-instance gap sum (average) |
|---|---|---|---|
| sector_decomposition (kept) | 0.6795 / 0.7001 / 0.6925 | 0.6907 | about 4.64 |
| alt_groups | 0.6328 / 0.6851 / 0.6367 | 0.6515 | about 4.17 |
| alt_clusters_only | 0.6449 / 0.6947 / 0.6816 | 0.6737 | about 4.43 |

alt_groups does beat the kept solver consistently, but only by about 0.04 on the val mean. A candidate must be at least 0.15 better.

Another Experimenter named test instance X-n502-k39 in a practice run. The harness refused it before anything ran, so no test data was used; it goes in the report with the earlier slip.

The best kept val mean gap is still 0.6795, with 37 of 60 evaluations used. I've asked the Planner for wave 15, three final trials that bring the run to 40. Since no wave has kept anything since wave 1, the loop may then end.
[turn finished]
Wave 15 is running. It is the last wave before the 40-evaluation floor, and all three runs are measurements:
- **alt_reseed_3000** and **sector_reseed_3000:** a fourth search path for both alt_groups and the kept solver. The report will then have four paired comparisons of the two.
- **no_savings_reseed_1000:** a second path for alt_groups without its savings start. It settles whether "savings is needed" was a real finding or one noisy n749 result.

The Planner sees no remaining idea with a realistic chance of reaching 0.5295 and recommends ending the loop at 40. Once these three are in, I'll run the final held-out test on the kept solver, sector_decomposition. It is still the kept solver because alt_groups' gain of about 0.04 is well below the keep rule.

The best kept val mean gap is still 0.6795, with 37 of 60 evaluations used.
[turn finished]
alt_reseed_3000 scored 0.7429 on val, the worst of alt_groups' four search paths. Its large-instance gap sum was about 5.26, which lifts the four-path average to about 4.44 against 4.64 for the kept solver's first three paths. So alt_groups' edge is shrinking and looks more like noise. Thirty-eight of 60 evaluations are used; sector_reseed_3000 and no_savings_reseed_1000 are still running.
[turn finished]
no_savings_reseed_1000 scored 0.6672 on val. Over its two search paths, alt_groups without the savings start averages about 4.30 on the large-instance sum, inside alt_groups' own four-path range (3.94–5.26). So the savings start is not shown to matter, and the earlier n749 result was noise. Thirty-nine of 60 evaluations are used; sector_reseed_3000 is the last run before the 40-evaluation floor.
[turn finished]
experiment.py is clean at commit 02a87d6. Launching the final test.The final test is running, about 30 minutes. I'll check back on a timer.The experiment loop is over, and the final held-out test is running on the kept solver.

**Loop result:** the only kept improvement is still sector_decomposition. It moved the val mean gap from 0.8814 to 0.6795 in wave 1. The loop stopped under the plateau rule: 40 of 60 evaluations were used, no wave since wave 1 kept anything, and 2 of 20 rechecks were used.

**Last measurement:** I ran the kept solver and alt_groups, the best near-miss, on four different seeds for the large instances.

| Large-instance seed | Kept solver | alt_groups |
|---|---|---|
| 0 | 0.6795 | 0.6328 |
| +1000 | 0.7001 | 0.6851 |
| +2000 | 0.6925 | 0.6367 |
| +3000 | 0.7117 | 0.7429 |

alt_groups wins on three of the four seeds, and its average is about 0.03 better. That is a suggestive edge, not an established one, and far below the 0.15 needed to keep it. Most single-run differences on the large instances in earlier waves were within this seed noise.

**Final test:** it scores lab/cvrp/experiment.py, committed at 02a87d6, on every held-out problem with seeds 0, 1 and 2, next to PyVRP default. It is writing to runs/cvrp/final.log and takes about half an hour.

The first test results are coming in, for example X-n148-k46 at 0.062% and X-n214-k11 at 1.345%. I've set a 15-minute timer to check progress. After the test finishes, I'll run the larger-problem check on three hunt instances and then send everything to the Scribe for the report.
[turn finished]
The final test is about two-thirds done and still running. It has finished the held-out test problems and is now running PyVRP default on the larger scale problems. No summary or final_test.json exists yet, so I have no comparison numbers to report. I've set a 10-minute timer to check again.
[turn finished]
The final test is not finished yet. It has done PyVRP default and the kept solver on the held-out test set, then PyVRP default on the larger scale set, all on seeds 0, 1 and 2. It is now running the kept solver on the scale set and has done 4 of its 24 runs. No summary or final_test.json exists yet, so there are no comparison numbers to report. That leaves 20 runs of about 25 seconds each; I've set a 9-minute timer to check again.
[turn finished]
While that runs, I'll gather what the Scribe needs.Hunt probe: X-n783-k48 1.270%, X-n936-k151 4.068%, X-n1001-k43 1.248% (mean 2.1952). I'll also probe PyVRP default on the same three instances, so the Scribe has a like-for-like comparison.Hunt probe: X-n783-k48 1.270%, X-n936-k151 4.068%, X-n1001-k43 1.248% (mean 2.1952). I'll also probe PyVRP default on the same three instances, so the Scribe has a like-for-like comparison.The final test is done. The kept solver is the same as after wave 1: PyVRP for the whole instance, then three rounds of re-solving groups of nearby routes on instances of 500+ customers. The answer to the question is yes for large problems; for small ones, a win is not established.

| Held-out set | Kept solver mean gap | PyVRP default | Savings | Paired difference (95% interval) | Problems won / lost |
|---|---|---|---|---|---|
| Test, 106–548 customers (17 problems × 3 seeds) | 0.5734 | 0.672 | 4.8232 | −0.0987 pp [−0.2483, 0.0441] | 9 / 8 (sign test p = 1.0) |
| Scale, 627–979 customers (8 problems × 3 seeds) | 1.3454 | 2.0054 | 4.9581 | −0.66 pp [−0.8115, −0.4989] | 8 / 0 (p = 0.0078) |

- **Large problems:** the solver beats PyVRP default on every scale problem, and the whole interval is below zero.
- **Small problems:** it is not shown to win; the interval includes zero and it won 9 problems to 8. Below 500 customers the solver is plain PyVRP with 20 neighbours, run 1's change, which is all that could make a difference there.
- **Larger hunt instances** (seed 0, one run each; PyVRP default probed on the same three for comparison):

| Instance | Kept solver | PyVRP default |
|---|---|---|
| X-n783-k48 | 1.270% | 2.636% |
| X-n936-k151 | 4.068% | 4.577% |
| X-n1001-k43 | 1.248% | 2.633% |

- **Records:** no best-known solution was beaten; every gap is positive.

The best val mean gap is 0.6795, with 40 of 60 evaluations and 2 of 20 rechecks used. The loop stopped under the plateau rule.

I've written runs/cvrp/compiler_notes.md as the Scribe's map of the run and sent the Scribe all the result files to write runs/cvrp/report.md. Some points need care in the report:
- **Noise:** changing only the random seed on the large instances moves results about as much as most trial-to-trial differences did.
- **Shape hypothesis:** tying the number of neighbours to customers per route was not supported in any form tried.
- **Wrong ledger note:** the alt_no_savings entry says the change "costs nothing", but the result was worse.
- **Test-instance slips:** twice an Experimenter named test instance X-n502-k39 in a practice run; both times the harness refused before anything ran.

Once the report is in, I'll send the closing message: the report, the ledger summary, the solver source and the completion line.
[turn finished]
```
