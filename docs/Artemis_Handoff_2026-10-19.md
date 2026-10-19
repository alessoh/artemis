# Artemis handoff, 19 October 2026

This is a starting point for a new chat. It summarises everything done in this project's long working chat (3 to 19 October 2026). The living status note is `claude/artemis_phase1_status.md` in the project, and every artifact named here is on GitHub.

## How to start the next chat
Open a new chat in the project "Artemis - Scientific Discovery" and begin with:

> Read claude/artemis_handoff_2026-10-19.md and claude/artemis_phase1_status.md in the project, then clone github.com/alessoh/artemis (all branches). We are continuing from that handoff. Today I want to ...

## Standing preferences and rules
- Write documents as well-edited Word files, in smooth narrative prose, without bullet points or em dashes. Code in Python, written as complete files, double-checked.
- Never invent data: use real, live, authenticated data. Ask which LLMs to use, offering a selection of open and closed models.
- Say so when the answer is unknown.
- Secrets live only in `.env`, Modal secrets and Vercel environment variables. Never ask for secrets in chat.
- Run transcripts in `runs/` can contain the Anthropic key. They must stay private and are never committed.
- Do not put the user's gmail address in papers or public documents. The paper uses alesso@alum.mit.edu.
- Byline: H. P. Alesso, AI HIVE.
- The authors' UN-CCD repository has no licence, so it is cloned at run time and never vendored.

## Infrastructure
- Website: artemis-ten-blond.vercel.app (Vercel). It has an intake page ("Start an investigation") and uses Neon Postgres through Vercel Storage.
- Omnigent 0.16 server: https://alessoh--artemis-omnigent-server.modal.run. Agents run in managed Modal sandboxes, and the website logs in as `artemis-web`.
- Repository: github.com/alessoh/artemis (public, MIT licence).
- The user runs labs from Windows, in Anaconda PowerShell with the conda environment `artemis`. The launch scripts are `scripts/run_*.py`.

## Branch heads (19 Oct 2026)
| Branch | Head | Contents |
|---|---|---|
| main | 119c69f | Core, solar lab, website, Phase 1 to 3 documents, 100 research proposals |
| cvrp-lab | b6a920e | Vehicle-routing program, runs 1 and 2 |
| langlands-lab | fb4acb4 | Langlands/elliptic-curve program, results, replication, the paper and its arXiv package in `docs/paper_euler/` |
| unccd-repro | 27b191b | UN-CCD Project 1: reproduction |
| unccd-alpha-lab | 86c0507 | UN-CCD Project 2: alpha lab and results, note to authors, Artemis vs Parzival review |

Note: main does not contain the later programs. Merging the branches is an open task.

## Completed work and verified results
- **Phase 1 and 3.** The end-to-end plumbing works, and the public website is live (light mode; 249 Playwright checks passed).
- **Solar (Phase 2).** Earth-abundant solar absorbers from JARVIS-DFT. Artemis found all 4 hits in 8 evaluations, against 20 for the textbook rule and about 344 for random search, roughly 2.5 to 3 times faster than the textbook rule.
- **Routing (cvrp-lab).** Sector decomposition on problems with at least 500 customers.
  - Gap to the best known solutions: 1.3454% for Artemis against 2.0054% for PyVRP, a paired difference of −0.66 percentage points [−0.81, −0.50]. Artemis won on 8 of 8 instances.
  - The test on small problems was not significant.
- **Langlands (langlands-lab).**
  - Part A: rho_ss = 0.5313 [0.4605, 0.5944].
  - Part B, held-out AUC: 0.522 for the pre-registered rule and 0.543 for the lab's rule (z = 8.6 and 15.1). Replicated exactly.
  - Paper: "Euler's Identity, Elliptic Curves and an AI Laboratory", 13 pages. The arXiv package is ready in `docs/paper_euler/`.
- **UN-CCD Project 1 (reproduction of Shi, Ceyhan and Billor, arXiv:2501.06268v3).**
  - 14 of 15 simulation cells reproduce.
  - The real-data driver uses alpha of 5 to 20%, not the stated 1%. Results depend on row order, the Louvain asymmetric entry is the aggregation row, and the code and paper differ in 13 places.
- **UN-CCD Project 2 (choosing alpha without labels).** The lab's rule is a null-calibrated silhouette.
  - Sealed test: rule 0.928, paper's schedule 0.863, oracle 0.954.
  - H1 holds: +0.065 [0.036, 0.098].
  - H2 fails, as predicted: the formula alpha = 240/(n d²) scored 0.883.
- **Note to the UN-CCD authors.** A short, friendly letter with links: `docs/Artemis_UNCCD_Note_to_Authors.docx`. Rui Shi holds a PhD, so "Dr." is correct for all three authors.
- **Artemis vs Parzival.** Scorecard 38 of 50 against 18. Parzival is a fork whose only distinct file is Recursive's `train.py` with nine settings changed. Its rank of #6 of 137 is unverified.

## Open items (user's decisions first)
1. **Euler paper.**
   - Read and revise the paper; the "Use of AI tools" statement says the author revised it.
   - Obtain a math.NT endorsement.
   - Upload `Alesso_Euler_Elliptic_AI_Lab_arXiv.zip` and paste the metadata from the guide.
   - The TeXstudio errors were only a missing `figures/` folder.
2. **UN-CCD authors.** Send the note with the two reports attached. A short covering email can be drafted on request.
3. **Parzival.** A screenshot of the live leaderboard would confirm or correct its #6 rank.
4. **Merge the branches** into main, and bring the agents' ledgers out of the sandbox (pushes from the sandbox are blocked).
5. **Suggested capabilities.**
   - A GPU program on Modal, for example Karpathy's benchmark run under Artemis rules with a sealed test.
   - Shared memory across runs, in the style of Ensue.
6. **UN-CCD follow-ups.**
   - Project 1's remaining Modal sweep (`lab/unccd/modal_sweep.py`, never yet run on Modal).
   - RK-CCD and KS-CCD.
   - Projects 3 to 6 from `docs/Artemis_UNCCD_Projects.docx`.
7. **Website.** Custom domain, rebuild with `--site-url`, and set CRON_SECRET.

## Operating notes learned the hard way
- Claude's cloud workspace shuts down when idle and kills background jobs. Run long computations only while actively monitoring them.
- The agents' Anthropic key is visible in sandbox process lists.
- Windows CRLF conversion broke the data fingerprints. `.gitattributes` now marks `lab/unccd_alpha/data/** -text`.
- arXiv now runs BibTeX itself and advises against `\pdfoutput`. Abstracts are limited to 1,920 characters.
- Word documents are built from `docs/source/*_content.js` concatenated with `guide_helpers.js`, then run with `NODE_PATH=$(npm root -g) node`.
