# Artemis decisions

Each decision names the person who made it, so it can be questioned and
changed by asking that person (step one of the Musk algorithm).

| Date | Decision | Owner |
|------|----------|-------|
| 2026-10-03 | Run open-source Omnigent ourselves: server on Modal, agents in server-managed Modal sandboxes. Databricks Free Edition is not used for the lab. | Peter Alesso |
| 2026-10-03 | Website on Vercel Pro (project `artemis`); database is Neon Postgres created through Vercel Storage. | Peter Alesso |
| 2026-10-03 | The website logs in to Omnigent as the non-admin account `artemis-web`; Omnigent refuses managed launches for machine-client sessions. | Claude, from testing |
| 2026-10-03 | Phase 1 (prove the plumbing) passed on the live system. | Verified on the live site |
| 2026-10-03 | **Flagship question:** earth-abundant solar-cell absorber materials, screened with the Materials Project and NIST JARVIS databases. | Peter Alesso |
| 2026-10-03 | **Models:** Claude Opus 5.5 (`claude-opus-5-5`) for the agents that plan, design experiments and write the report (Compiler, Planner, Experimenters, Scribe); Claude Haiku 4.5 (`claude-haiku-4-5`) for quick literature and data searches (Scout). | Peter Alesso |
| 2026-10-03 | **Skeptic** also runs on Claude (Opus 5.5) for now, rather than another vendor's model. | Peter Alesso |
| 2026-10-03 | **Data:** labels, split and cheap properties from the JARVIS-Leaderboard SLME benchmark (commit 57afc55, SHA-256 pinned per file); formulas and structures from the JARVIS-DFT 3D release of 2021-08-18 it was built from; never-assessed materials from that release form the recommendation pool. Built once on Modal and committed with its fingerprint. | Claude, approved by plan |
| 2026-10-03 | **Earth-abundant:** every element at least 1 mg/kg in the crust (CRC Handbook 97th ed., sec. 14 p. 17); excluded Cd, Hg, Pb, Tl, As and radioactive elements. | Claude (thresholds from the Phase 2 plan) |
| 2026-10-03 | **Hit (pre-registered):** SLME at least 30 percent and energy above hull at most 0.1 eV/atom. Chosen after seeing only aggregate SLME counts per split. | Claude |
| 2026-10-03 | **Metric:** acceleration = random-search expected evaluations to find 10 hits divided by the evaluations the ranking needed; keep or discard on the val pool; test pool scored once by `harness.py final`. | Claude |
| 2026-10-03 | **Budgets:** $40 Omnigent cost budget and 900 tool calls for the lead; 60 val experiments per run in the harness; 300 s per `rank()` call. | Claude, to be confirmed by Peter Alesso |
| 2026-10-03 | **First live run** (session 501042555e83): final model ExtraTrees SLME regressor with a stability gate; val 32.262 (13 evaluations), test 43.0 (8 evaluations vs 20 for the stability-gated rule). Lab report and lead transcript in `docs/results/phase2_run_2026-10-03/`. | Lab run, checked by Claude |
| 2026-10-03 | The final model's code was lost with the sandbox; `lab/solar/trials/extra_trees_elemfrac_rebuilt.py` rebuilds it from the report and reproduces the lab's val result exactly (13 evaluations, AP 0.899) and 14 of its 15 shortlist entries. | Claude |
| 2026-10-03 | Post-hoc robustness check over 20 random halvings of all earth-abundant labeled materials: the rebuilt model needed fewer evaluations than the stability-gated rule in 20 of 20 splits (median 14.5 vs 47.5 to find 10 hits). `lab/solar/analysis/robustness.py`, `docs/results/phase2_robustness.csv`. | Claude |
| 2026-10-03 | Harness change (new fingerprint): the unlabeled pool keeps one row per jid, because the 2021 release repeats four materials with identical values. Val and test scoring are unchanged. | Claude |
| 2026-10-03 | **Website (Phase 3):** light mode only; static pages built by Python and Jinja2 into `public/` and served by Vercel; FastAPI only for `/api/*`; menu limited to Results, Method, About and one "Start an investigation" button. | Peter Alesso (light mode, simple menu); Claude (structure) |
| 2026-10-03 | Copy leads with the held-out result (8 vs 20 vs about 344) and labels the 20-pool check as post hoc on a rebuilt model; "non-toxic" is not used because the pool can contain beryllium and nickel. | Claude, from the accuracy audit |
| 2026-10-03 | Visitors may read everything; starting a run needs `ARTEMIS_ACCESS_CODE`; at most 2 runs at once; Lab-page proposals use a read-only intake agent with a $3 budget. | Claude, to be confirmed by Peter Alesso |
| 2026-10-07 | **Second program: vehicle routing** on CVRPLIB X, on the `cvrp-lab` branch. | Peter Alesso |
| 2026-10-07 | **Data:** the 100 X instances and BKS costs from PyVRP/Instances at commit 7474b06 (2026-08-19); every BKS re-computed exactly with the harness checker; BKS routes not stored, so experiments cannot copy them. The live CVRPLIB site could not be reached from the workspace, so a claimed record must also be checked against the live table. | Claude |
| 2026-10-07 | **Pre-registered rules:** 3 s per 100 customers on one core; metric = mean gap to BKS on 8 val instances, seed 0; 60 val evaluations and 20 rechecks per run; test (17) and scale (8) used once by `final`; keep a trial only if seed-0 gain >= 0.15 points and the gain on seeds 1-2 >= 0.10 points (noise SD measured at 0.085). | Claude, to be confirmed by Peter Alesso |
| 2026-10-07 | **Baselines:** Clarke-Wright savings + 2-opt (textbook) and PyVRP 0.14.0 default (state-of-the-art library). The starting experiment equals PyVRP default. | Claude |
| 2026-10-07 | Timed evaluations run one at a time (file lock), because parallel solvers would share the CPU and score worse. | Claude |
| 2026-10-07 | **Routing run 1 result** (session 60a600de): one kept change, PyVRP granular neighbourhood 50 -> 20. Held-out test 0.5838% vs PyVRP default 0.731% (12/17 wins); scale 1.8856% vs 1.8738% (tie on the mean, 6/8 wins). 13 of 60 evaluations used. Claude re-computed every table from the per-instance costs. Run 1's code is kept on branch `cvrp-run1`. | Lab run, checked by Claude |
| 2026-10-07 | **Security:** run 1's Skeptic found the agents' Anthropic key visible in sandbox process lists, so it may appear in saved transcripts (runs/.../items.json, subagents/). Rotate the key; never share or commit those transcript files. | Claude |
| 2026-10-07 | **Routing run 2 design:** start from run 1's solver; val = the 8 run-1 problems + 4 larger ones (X-n655-k131, X-n749-k98, X-n876-k59, X-n895-k37); at least 40 evaluations before the three-empty-waves stop rule; final = test and scale with seeds 0, 1, 2 and a paired comparison (bootstrap interval, sign test); same test and scale problems as run 1 (disclosed: humans saw run 1's results on them). | Claude, approved by Peter Alesso |
| 2026-10-07 | Spending limit for routing run 2: $80. | Peter Alesso |
| 2026-10-07 | Disclosure: to test the new three-seed final code, Claude ran both solvers on 2 test and 2 scale problems in the workspace (results discarded; no design choice used them). | Claude |
| 2026-10-07 | **Routing run 2 result** (session 7f5a6aec): one kept change, sector decomposition for 500+ customers on top of run 1's solver. Held-out scale (626-978 customers, 3 seeds): 1.3454% vs PyVRP default 2.0054%, paired -0.66 pp [-0.81, -0.50], 8/8 problems, sign p = 0.0078. Held-out test (105-547): 0.5734% vs 0.672%, -0.10 pp [-0.25, +0.04], 9/8, not significant, so run 1's small-problem gain did not replicate. 40 of 60 evaluations used. | Lab run, checked by Claude |
| 2026-10-07 | Independent replication by Claude on the workspace (one seed, slower machine): scale 1.295% vs 1.544%, 7 of 8 problems better; X-n670-k130 lost. | Claude |
| 2026-10-07 | lab/cvrp/experiment.py on this branch is now run 2's final solver; run 1's is in docs/results/cvrp_run1/. | Claude |
