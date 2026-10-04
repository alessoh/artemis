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
