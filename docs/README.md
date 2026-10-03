# Artemis documents

| Document | What it covers |
|----------|----------------|
| `Artemis_Architecture_Discussion_Paper_01.docx` | First-principles review of the challenge, the generalized three-file AutoResearch contract, the six agents, and the original architecture proposal |
| `Artemis_Explained_Simply.docx` | Plain-language guide to the five pieces of the system and the plan |
| `Artemis_Phase1_Runbook.docx` | Step-by-step instructions for bringing the Phase 1 lab online |
| `Artemis_Vercel_Import_Guide.docx` | Click-by-click guide to importing this repository into Vercel |
| `Artemis_Phase2_Runbook.docx` | The Phase 2 lab: the question as an experiment, the team, what is tested, the steps you run |
| `decisions.md` | Decisions made so far, each traced to the person who made it |

Note: the Phase 1 runbook predates two later fixes. The setup is now one
command, `python scripts/run_phase1.py`, and the website logs in to Omnigent
as the regular account `artemis-web` rather than the machine client. The
repository README describes the current process.

## Rebuilding the documents

`source/` holds the scripts that produced the figures and Word files.
Figures are drawn with matplotlib (`python figures.py`, `python fig_simple.py`);
the Word files are built with the `docx` npm package. `build_doc.js` is
standalone; the other four are built by joining the shared helpers with
their content file, for example:

```bash
cd docs/source
python figures.py && python fig_simple.py
cat guide_helpers.js guide_content.js > build_guide.js && node build_guide.js
```
