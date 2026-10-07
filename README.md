# Artemis

Artemis is an agentic scientific discovery lab built on
[Omnigent](https://github.com/omnigent-ai/omnigent) for Challenge 03 of the
7th Global AI Hackathon. A visitor states a scientific question on the
website; a team of AI agents running inside Omnigent turns it into a
measurable experiment, runs it on real public data, and reports what it
learned with citations.

## Status

**Phase 1, prove the plumbing: complete** (October 3, 2026). A question typed
on the live Vercel site starts a fresh Modal sandbox, Claude answers, and the
reply streams back to the browser in about 20 seconds.

**Phase 2, the real lab: first run complete** (October 3, 2026; see
[`docs/Artemis_Phase2_Results.docx`](docs/Artemis_Phase2_Results.docx)). On the
held-out test, run once, the agents' method found all 4 excellent absorbers in
8 expensive calculations; the textbook rule needed 20 and random order about 344.
A later robustness check of a rebuilt copy, over 20 random pools, beat the
textbook rule in 20 of 20 and the corrected-gap rule in 19 of 20. Flagship
question: which earth-abundant crystals in NIST JARVIS-DFT (Cd, Hg, Pb, Tl, As
and radioactive elements excluded) should be computed next to find excellent
solar absorbers fastest? Six agents in one Omnigent session (Compiler, Scout,
Planner, Experimenter, Skeptic, Scribe) run the AutoResearch loop in
[`lab/solar`](lab/solar). Models: Claude Opus 5.5 for planning, experiments,
the Skeptic and the report; Claude Haiku 4.5 for the Scout's quick searches.
See [`docs/decisions.md`](docs/decisions.md).

**Phase 3, the public website: live** (October 3, 2026;
https://artemis-ten-blond.vercel.app). Light mode, a four-item menu (Results,
Method, About and a "Start an investigation" button),
SEO and GEO metadata, and live runs whose reports are saved in Neon Postgres
and published on the Results page. See
[`docs/Artemis_Phase3_Website.docx`](docs/Artemis_Phase3_Website.docx).

## Routing program (branch `cvrp-lab`)

The second Artemis program asks whether the lab can build a capacitated
vehicle routing (CVRP) solver that, with the same short time limit on one CPU
core (3 seconds per 100 customers), gets closer to the CVRPLIB X best-known
solutions than PyVRP's default solver. Records beyond that are attempted
separately with long runs.

```
lab/cvrp/program.md       the human's instructions (read by every agent)
lab/cvrp/harness.py       frozen: checks every route, CVRPLIB rounding, time and CPU limits, ledger
lab/cvrp/reference.py     frozen: PyVRP 0.14.0 default, the baseline
lab/cvrp/experiment.py    the one solver the agents improve: solve(instance, time_limit, seed)
lab/cvrp/prepare_data.py  built the snapshot from PyVRP/Instances at a pinned commit
lab/cvrp/hunt.py          long record-hunting runs (Modal or this computer), checked by the harness
lab/agents/cvrp_lab/      the six agents
scripts/run_cvrp.py       check, launch, watch, collect, stop, rebuild
```

The snapshot holds the 100 X instances and their best-known costs (not their
routes). Every published cost was re-computed exactly by the harness's own
checker. Splits: train 52, val 8, test 17 (fewer than 600 customers); scale 8
and hunt 15 (600 or more). Measured before any run: savings rule 6.85 percent
mean gap on val, PyVRP default 1.30 percent (seed 0), seed-to-seed standard
deviation 0.085 percentage points.

Run it from the artemis folder:

```
git fetch
git checkout cvrp-lab
pip install -r requirements-cvrp.txt
python scripts/run_cvrp.py
```

Run 1 (October 7, 2026) kept one change, a granular neighbourhood of 20
instead of 50: held-out test 0.58 percent against 0.73 for PyVRP default
(12 of 17 problems), and a tie on the larger scale problems. Its report and
final solver are in `docs/results/cvrp_run1/`, and its exact code is on the
`cvrp-run1` branch. Run 2 starts from that solver, adds four larger problems
to the practice set, must use at least 40 evaluations, repeats the final test
with three seeds and a paired comparison, and has an 80 dollar limit (see the
"Run 2" section of `lab/cvrp/program.md`).

Hunt for records afterwards, for example:

```
modal run lab/cvrp/hunt.py --instance X-n801-k40 --minutes 60 --seeds 8
```

## Phase 3: the website

```
site/templates, site/pages   Jinja2 page sources
site/assets                  CSS and JavaScript (menu, chart, live lab, results)
site/src/lattice.js          the Three.js crystal, bundled to public/assets/lattice.js
scripts/build_site.py        builds public/ (pages, sitemap, robots, llms.txt, OG images)
scripts/test_site.py         Playwright test of every page, link, button and a full run
public/                      the generated site that Vercel serves (committed)
app.py                       the API: /api/runs, /api/results, /api/cron/sync, /api/status
artemis_core/store.py        saved runs in Neon Postgres (schema artemis)
```

Rebuild the site after changing a page or the results:

```
python scripts/build_site.py
```

**Moving to your own domain.** Add the domain to the `artemis` project in
Vercel (Settings, Domains) and follow the DNS instructions Vercel shows. Then
rebuild with the new address so canonical links, the sitemap and llms.txt point
to it, and push:

```
python scripts/build_site.py --site-url https://your-domain.com
git add -A
git commit -m "Point the site at its own domain"
git push
```

**Environment variables in Vercel** (Settings, Environment Variables, never in
the repository): `OMNIGENT_URL`, `OMNIGENT_USERNAME`, `OMNIGENT_PASSWORD`,
`ARTEMIS_ACCESS_CODE` and the Neon `DATABASE_URL` are required. `CRON_SECRET`
is recommended: when set, Vercel's 15-minute cron sends it and outsiders cannot
trigger the sync. Redeploy after changing any of them.

**How results are saved.** Starting a run writes a row to `artemis.runs`. When
the lead agent finishes, the relay saves the report and deletes the sandbox
session; if the browser was closed, the cron job does the same within 15
minutes. Saved runs appear on `/results` and at `/results/run?id=...`.

## Phase 2: the lab

```
lab/solar/program.md      the human's instructions (read by every agent)
lab/solar/harness.py      frozen: data check, pool, hit, metric, time limit, ledger
lab/solar/experiment.py   the one function the agents improve: rank(train, candidates)
lab/solar/prepare_data.py builds the frozen data snapshot once (on Modal)
lab/solar/tools/          Materials Project lookup and literature search for the Scout
lab/agents/solar_lab/     the Omnigent team: lead plus five sub-agents, each with its model
scripts/run_phase2.py     one command: data, local check, share, launch and watch
```

**The question as an experiment.** SLME (spectroscopic limited maximum
efficiency, computed by JARVIS from TBmBJ optics) is the expensive measurement.
The experiment sees only cheap DFT properties and orders the candidates; the
harness then counts how many expensive evaluations that order needed to find
ten excellent, stable absorbers (SLME at least 30 percent, energy above hull at
most 0.1 eV/atom) and compares with random search. That ratio,
`acceleration`, is the metric. The pool is the official JARVIS-Leaderboard SLME
split, restricted to materials whose every element has a crustal abundance of
at least 1 mg/kg (CRC Handbook, 97th edition) and that contain no Cd, Hg, Pb,
Tl, As or radioactive element. The test pool is scored once, at the end.

**Run it** (from the artemis folder, after Phase 1):

```bash
pip install -r requirements-solar.txt
python scripts/make_secrets.py materials-project   # optional: Materials Project key
python scripts/run_phase2.py
```

`run_phase2.py` builds the data snapshot on Modal the first time, checks the
harness on your computer and prints the baselines, puts the snapshot on
GitHub (the lab's sandbox starts from a fresh clone), then launches the lab and
shows its progress. The run continues in the cloud if the window is closed;
`python scripts/run_phase2.py watch SESSION_ID` reconnects and saves the report.

**Limits on spending.** The lead agent has a $40 Omnigent cost budget and a cap
on tool calls; the harness allows 60 experiments per run. Setting a monthly
spend limit in the Anthropic console is still the surest backstop.

## Phase 1: how the plumbing works

Phase 1 connects every piece of the system with one simple test agent, so
any connection problem shows up in the first hours rather than the last.

```
Browser ──► Vercel relay (app.py) ──► Omnigent server (Modal) ──► agent sandbox (Modal) ──► Claude
   ▲                                          │
   └──────────── live Server-Sent Events ◄────┘
```

| Path | What it is |
|------|------------|
| `public/index.html` | The Phase 1 page: a signal path that lights up as real events arrive |
| `app.py` | FastAPI relay for Vercel: creates sessions, relays the live stream |
| `artemis_core/omnigent_api.py` | The one place the Omnigent REST protocol lives |
| `lab/modal_server.py` | Deploys the unmodified Omnigent server on Modal with managed sandboxes |
| `lab/agents/hello_lab/config.yaml` | The Phase 1 test agent (Claude Haiku 4.5, no tools) |
| `scripts/make_secrets.py` | Generates secrets locally and pushes them to Modal |
| `scripts/smoke_test.py` | Checks every hop and saves a timestamped record in `runs/` |
| `scripts/run_phase1.py` | One command: settings, Modal, deploy, account, test, Vercel values |
| `scripts/diagnose_phase1.py` | Records one test's events and Modal logs into a redacted report |
| `scripts/run_phase2.py` | Phase 2: data snapshot, local harness check, share, launch, watch |
| `docs/` | Design papers, guides, the decisions record, and their sources |

## Run Phase 1 (one command)

```bash
python scripts/run_phase1.py
```

It checks your settings, saves them to Modal, deploys the Omnigent server,
waits for it to start, runs the end-to-end test, and prints the four values
to add to Vercel. The individual commands below do the same steps one by one.

## Run Phase 1 step by step

From the repository root on your own computer:

```bash
pip install -r requirements-lab.txt
modal setup                                   # one-time Modal login
python scripts/make_secrets.py init           # copy 2 values in the browser, press Enter
python scripts/make_secrets.py check
python scripts/make_secrets.py modal          # saves two Modal secrets
modal deploy lab/modal_server.py              # deploys the Omnigent server
python scripts/smoke_test.py                  # proves server, sandbox, model, stream
python scripts/make_secrets.py vercel         # shows the Vercel variables to add
python scripts/smoke_test.py --via-website https://<your-vercel-url>
```

Phase 1 passes when both smoke tests print `PHASE 1 PASSED` and the website's
five stations all turn green.

## The .env file

`.env.example` only lists the variable names. Your real `.env` is created by
`python scripts/make_secrets.py init`, which generates eleven of the fifteen
values itself, reads your Modal token from the file `modal setup` saved, and
collects the last two from your clipboard: the Neon database address (Vercel,
Storage, your database, DATABASE_URL_UNPOOLED) and your Anthropic key. Copy
each one in the browser and press Enter in the terminal; nothing secret is
shown on screen.
You never need to obtain anything from Omnigent; the script creates the
Omnigent secrets and Omnigent reads them from Modal when it starts.

## Security

Secrets live only in `.env` (git-ignored), in Modal secrets, and in Vercel
environment variables. The Anthropic key is injected into the agent
sandboxes only; the Omnigent server never holds it. A visitor needs the
access code to start a session.

The website logs in to Omnigent as a regular, non-admin account
(`artemis-web`, created automatically by `run_phase1.py`). This matters:
Omnigent only launches agents in managed Modal sandboxes for sessions owned
by a real account, and silently leaves machine-client sessions stuck at
"connecting".
