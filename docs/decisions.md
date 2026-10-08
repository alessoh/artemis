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
| 2026-10-08 | **Langlands program (branch `langlands-lab`):** tests R1 of "Euler's identity and the Langlands program". Part A (fixed): murmurations over Q by root number (C1) and the predicted flip over Q(sqrt 5) (C2, primary statistic rho_ss from finite signs of semistable classes). Part B (AutoResearch loop): within-conductor AUC of rank 2 against rank 0 from the local signs alone; H_B1 (simple rule: split multiplicative count) and H_B2 (lab's experiment), one-sided p < 0.01 on conductors 400,000 to 499,999. | Peter Alesso (questions); Claude (design) |
| 2026-10-08 | Data: Cremona ecdata at commit 25cec5e (N < 500,000) and the LMFDB Q(sqrt 5) file downloaded 2026-10-08; PARI 2.17.2 computes local root numbers only over Q, so finite signs over Q(sqrt 5) are computed for semistable classes (-a_P at each multiplicative prime). Checks passed: 17,314 Q classes, 3,333 semistable and 4,602 rank-known Q(sqrt 5) classes. | Claude |
| 2026-10-08 | Independent audit before any run found that Cremona's class-letter order leaks rank (AUC 0.564 on train from position alone). Fixed: rows go to experiments once per distinct (N, signs), deterministic; plus a stricter import allowlist, a runtime audit hook, archived trial code, and Part A run before the test split is marked used. | Audit agent; fixes by Claude |
| 2026-10-08 | Budgets: $60 cost limit, 700 tool calls, 40 val evaluations, 16 recheck seed runs, stop after three empty waves only once 25 evaluations are used. | Claude, to be confirmed by Peter Alesso |
