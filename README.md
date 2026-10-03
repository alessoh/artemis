# Artemis

Artemis is an agentic scientific discovery lab built on
[Omnigent](https://github.com/omnigent-ai/omnigent) for Challenge 03 of the
7th Global AI Hackathon. A visitor states a scientific question on the
website; a team of AI agents running inside Omnigent turns it into a
measurable experiment, runs it on real public data, and reports what it
learned with citations.

## Current phase: Phase 1, prove the plumbing

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

## Run Phase 1

From the repository root on your own computer:

```bash
pip install -r requirements-lab.txt
modal setup                                   # one-time Modal login
python scripts/make_secrets.py init           # generates 11 values, asks you for 4
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
values itself and asks you for the other four: a Neon database connection
string (from pg.new), your Modal token ID and secret, and your Anthropic key.
You never need to obtain anything from Omnigent; the script creates the
Omnigent secrets and Omnigent reads them from Modal when it starts.

## Security

Secrets live only in `.env` (git-ignored), in Modal secrets, and in Vercel
environment variables. The Anthropic key is injected into the agent
sandboxes only; the Omnigent server never holds it. The website reaches
Omnigent through a machine client whose token is scoped to session
endpoints, and a visitor needs the access code to start a session.
