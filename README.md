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

**Phase 2, the real lab: built, waiting for its first live run.** Flagship
question: which earth-abundant, non-toxic crystals in NIST JARVIS-DFT should be
computed next to find excellent solar absorbers fastest? Six agents in one
Omnigent session (Compiler, Scout, Planner, Experimenter, Skeptic, Scribe) run
the AutoResearch loop in [`lab/solar`](lab/solar). Models: Claude Opus 5.5 for
planning, experiments, the Skeptic and the report; Claude Haiku 4.5 for the
Scout's quick searches. See [`docs/decisions.md`](docs/decisions.md).

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
