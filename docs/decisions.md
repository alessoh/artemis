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
