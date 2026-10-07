# Run 1: lead agent's messages (excerpt from the watching window)

The start of the window was not captured; the report holds the full record.

```
anular_20 scored 0.5439% on seed 0 (current best 0.9818%), so it is a candidate and has gone to the Skeptic for recheck. The other two trials are still running.
[turn finished]
light_perturb made things worse at 1.3507%, so I've discarded it. Still waiting on route_decompose and the Skeptic's review of granular_20.
[turn finished]
**Wave 1 done:** granular_20 kept (0.9818 → 0.5439 on seed 0; recheck 0.6573 against 0.9257). light_perturb scored 1.3507 and route_decompose 0.9879, so both are discarded. Best is now 0.5439%.The Planner is drafting wave 2 on top of the new best (0.5439%). I'll collect its ideas when it finishes.
[turn finished]
That notice was for the Skeptic result I already collected. The Planner is still working on wave 2.
[turn finished]
Wave 2 is running: granular_30, decompose_20 and string_ruin. Best so far is 0.5439%.
[turn finished]
granular_30 scored 0.8613%, worse than the best, so I've discarded it. The Planner's train probes had already ruled out 12 and 15 neighbours, so 20 looks like the right setting. decompose_20 and string_ruin are still running.
[turn finished]
string_ruin scored 0.5655% against the best's 0.5439%, so it is not a candidate. Still waiting on decompose_20.
[turn finished]
**Wave 2 done:** granular_30 scored 0.8613%, string_ruin 0.5655% and decompose_20 0.5601%, so nothing was kept. Best is still 0.5439%. That is one wave in a row with no kept improvement.The Planner is working on bolder wave-3 ideas. I'll dispatch them when it reports.
[turn finished]
Wave 3 is running: stall_restart, srex_pool and sisr_sparse. Best so far is 0.5439%.
[turn finished]
stall_restart scored 0.5393%, which is within noise of the best, so it is not a candidate. srex_pool and sisr_sparse are still running.
[turn finished]
srex_pool scored 0.6153%, worse than the best, so I've discarded it. The harness now lists 0.5393% (stall_restart) as the lowest score in the ledger, but the solver we keep is still granular_20 at 0.5439%. Waiting on sisr_sparse.
[turn finished]
The Planner is screening wave-4 ideas on train instances before proposing them. I'll pick up its result when it finishes.
[turn finished]
Wave 4 is the last wave before the three-empty-waves stop rule applies. I'm running the Planner's top two screened ideas plus one bolder combination.Wave 4 is running: ops_warmup40, ops_minimal and warmup_decompose. Best so far is 0.5439%.
[turn finished]
ops_warmup40 scored 0.5188%, about 0.03 below the best, which is within noise and short of the 0.394 bar, so it is not a candidate. Two wave-4 trials are still running.
[turn finished]
ops_minimal scored 0.5445%, level with the best. It is not a candidate, and it isn't simpler code either, since it adds an operator list to the config. Waiting on warmup_decompose.
[turn finished]
The final test (test and scale splits) is running in the background. I'll check it in about 12 minutes.
[turn finished]
The final test is done. On test, the lab's solver scored 0.5838% against PyVRP default 0.731%, beating it on 12 of 17 instances. On scale it scored 1.8856% against 1.8738%: it won on 6 of 8 instances but lost badly on X-n670-k130. The hunt probe of the final solver is done; the matching PyVRP reference probe is still running.
[turn finished]
Both hunt probes are done: the final solver averaged 1.7921% against PyVRP default's 2.3391%. The Scribe is writing runs/cvrp/report.md.
[turn finished]
# Artemis routing run: can a lab-built solver beat PyVRP's default on the CVRPLIB X benchmark at short time limits?
```
