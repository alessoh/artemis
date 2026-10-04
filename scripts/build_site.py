"""Build the Artemis website into public/ (static pages Vercel serves as-is).

Run from the repository root after changing anything under site/ or the
Phase 2 results:

    python scripts/build_site.py                                  # current Vercel address
    python scripts/build_site.py --site-url https://artemis.example.org   # your own domain

What it does, in order:

1. Copies site/assets (styles and scripts) and the self-hosted fonts into public/assets.
2. Bundles the Three.js hero (site/src/lattice.js) with esbuild into public/assets/lattice.js.
3. Reads the Phase 2 results (docs/results and the data snapshot) and writes the
   chart data and downloadable files into public/data.
4. Renders every page from site/templates and site/pages with its title,
   description, canonical address, social-card tags and structured data.
5. Writes sitemap.xml, robots.txt, llms.txt, llms-full.txt, the web manifest and
   the icons; with --images it also renders the social-card images.

The site address appears in canonical links, social cards and the sitemap,
so rebuild with --site-url whenever the domain changes. Build-time tools
(Node.js packages in site/node_modules and Playwright) are needed only here,
never on the server.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PUBLIC = ROOT / "public"
RESULTS = ROOT / "docs" / "results"
SNAPSHOT = ROOT / "lab" / "solar" / "data" / "solar_snapshot.csv.gz"
DEFAULT_SITE_URL = "https://artemis-ten-blond.vercel.app"
FLAGSHIP_PATH = "/results/solar-absorbers-2026-10-03"
BUILD_DATE = "2026-10-03"
REPO = "https://github.com/alessoh/artemis"

NAV = [
    {"key": "results", "label": "Results", "href": "/results"},
    {"key": "method", "label": "Method", "href": "/method"},
    {"key": "about", "label": "About", "href": "/about"},
]

# The lab's trials, copied from its ledger as reported in
# docs/results/phase2_run_2026-10-03/lab_report.md (section 3).
TRIALS = [
    ("Starting rule", "Band gap nearest 1.34 eV", 244, "1.72", "Starting point", ""),
    ("mbj_corrected_gap", "Stable first, gap target moved to the accurate-gap scale", 21, "19.97", "Kept", "tag-good"),
    ("gbm_hit_classifier", "Stable first, learned yes-or-no hit classifier", 18, "23.30", "Kept", "tag-good"),
    ("gbm_mbj_window", "Stable first, learned accurate-gap window", 22, "19.06", "Dropped", ""),
    ("slme_regressor", "Predict SLME itself instead of yes or no", 15, "27.96", "Kept", "tag-good"),
    ("ea_weighted_classifier", "Weight earth-abundant training materials more", 18, "23.30", "Dropped, tie", ""),
    ("minimal_features", "Simplify to 8 features", 33, "12.71", "Dropped", ""),
    ("mbj_gap_feature", "Add a predicted accurate gap as a feature", 14, "29.96", "Dropped", ""),
    ("reg_clf_rank_average", "Average the regressor and classifier rankings", 13, "32.26", "Rejected by Skeptic", "tag-warn"),
    ("drop_ehull_feature", "Use stability only as the gate", 15, "27.96", "Dropped, tie", ""),
    ("extra_trees_regressor", "Randomized trees instead of gradient boosting", 16, "26.21", "Dropped", ""),
    ("knn_analogue", "SLME of the 10 most similar known materials", 14, "29.96", "Rejected by Skeptic", "tag-warn"),
    ("extra_trees_elemfrac", "Randomized trees plus the fraction of each element", 13, "32.26", "Kept, final method", "tag-good"),
    ("stable_train_only", "Train only on near-stable materials", 13, "32.26", "Dropped, tie", ""),
    ("drop_structural_columns", "Remove structural columns", 14, "29.96", "Dropped", ""),
    ("threshold_weighting", "Weight materials near the 30 percent line", 13, "32.26", "Dropped, tie", ""),
    ("stable_plus_threshold", "Combine the two previous ties", 12, "34.95", "Rejected as overfitted", "tag-warn"),
    ("optimistic_ucb", "Favour uncertain predictions", 13, "32.26", "Dropped, tie", ""),
    ("magpie_lite_features", "Add 28 composition statistics", 14, "29.96", "Dropped", ""),
    ("anion_gap_window", "Add an anion-specific gap window", 14, "29.96", "Dropped", ""),
]

# The lab's top 15 never-assessed materials (lab report, section 6), checked
# against the snapshot by Claude. Notes summarise the report's cross-checks.
SHORTLIST = [
    ("JVASP-90503", "On the hull; ranked mainly for its composition"),
    ("JVASP-120881", "No literature found"),
    ("JVASP-78443", "Metallic at this level of theory; likely false positive"),
    ("JVASP-111073", "Literature says wide-gap; verify before trusting the rank"),
    ("JVASP-14566", "Metallic at this level of theory; likely false positive"),
    ("JVASP-114550", "No literature found"),
    ("JVASP-12510", "Second CuCl structure; as rank 4"),
    ("JVASP-59094", "No literature found"),
    ("JVASP-59095", "Not searched"),
    ("JVASP-10972", "Only unrelated literature"),
    ("JVASP-9128", "Not searched"),
    ("JVASP-12504", "Has band-gap literature"),
    ("JVASP-100007", "No literature found"),
    ("JVASP-115581", "No literature found"),
    ("JVASP-98069", "Metallic at this level of theory; likely false positive"),
]

FAQ = [
    ("What is Artemis?",
     "Artemis is an autonomous AI lab. It turns a scientific question into a measurable experiment, runs the "
     "experiment with a team of six AI agents on public data, tests the result once on held-out data, and "
     "publishes the report, code and data."),
    ("Did Artemis discover a new solar-cell material?",
     "Not yet. Its first run produced a faster way to choose which materials to calculate, and a ranked list of "
     "earth-abundant crystals that have no SLME value in JARVIS. Each candidate still needs the expensive "
     "calculation, and then laboratory work, before anyone can call it a discovery."),
    ("How much faster is the Artemis method?",
     "On the official held-out test (429 materials, 4 excellent absorbers, run once), the method found all four in "
     "8 expensive calculations; the textbook rule (stable materials first, band gap nearest 1.34 eV) needed 20 and "
     "random search about 344. In a later check of a rebuilt copy of the method on 20 random pools of 2,204 "
     "materials, it needed a median of 14.5 calculations to find 10 excellent absorbers, against 26 for a corrected "
     "band-gap rule, 47.5 for the textbook rule and about 1,161 for random search, and it beat the textbook rule in "
     "all 20 pools."),
    ("Who built Artemis?",
     "Peter Alesso built Artemis for Challenge 03 of the 7th Global AI Hackathon, working with Claude, Anthropic's "
     "AI assistant, as a coding partner. The code is open source under the MIT license."),
    ("Which AI models does Artemis use?",
     "Claude Opus 5.5 plans, designs and runs experiments, reviews them as the Skeptic, and writes the report. "
     "Claude Haiku 4.5 runs quick literature and database searches. The agents run in Omnigent, the open-source "
     "agent harness from Databricks, on Modal."),
    ("Where does the data come from?",
     "From NIST JARVIS-DFT and the JARVIS-Leaderboard, with crustal abundances from the CRC Handbook of Chemistry "
     "and Physics. The Materials Project and OpenAlex are used for cross-checks and literature searches."),
    ("Can I ask Artemis my own question?",
     "Yes. On the Lab page, describe your question. The lab's Compiler drafts a testable experiment: what to "
     "measure, which public data to use, baselines, risks, and whether Artemis can run it today. Starting a run "
     "needs an access code because it uses paid computing; every finished run is published on the Results page."),
    ("How does Artemis keep its results honest?",
     "The scoring code and data are frozen and fingerprinted. Success thresholds are fixed before any experiment. "
     "A separate Skeptic agent re-runs every apparent gain, and the held-out test is used exactly once. The final "
     "model of the first run was later rebuilt from its report; it matched the lab's practice score exactly and 14 "
     "of its 15 recommendations."),
    ("Is the code open source?",
     "Yes. The harness, agents, website and results are on GitHub at github.com/alessoh/artemis under the MIT "
     "license."),
]


# ---------------------------------------------------------------- helpers
def thousands(value: float | int | str) -> str:
    """Format a number with thousands separators (1161 -> 1,161)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:,.0f}" if number >= 100 else (f"{number:g}")


def spacegroup_html(symbol: str) -> str:
    """Fm-3m -> Fm3̅m (bar over the digit); P2_1/c -> P2<sub>1</sub>/c."""
    # The minus stays in the text (for copying, crawlers and screen readers) but is hidden visually.
    text = re.sub(r"-(\d)", r'<span class="ovl"><span class="vh">-</span>\1</span>', symbol)
    return re.sub(r"_(\d)", r"<sub>\1</sub>", text)


def formula_html(formula: str) -> str:
    """Cu2BrCl -> Cu<sub>2</sub>BrCl."""
    return re.sub(r"(\d+)", r"<sub>\1</sub>", formula)


def run(cmd: list[str], cwd: Path) -> None:
    """Run a build command, stopping with its output if it fails."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}\n{result.stdout}\n{result.stderr}")


# ---------------------------------------------------------------- data
def robustness() -> tuple[dict, dict]:
    """Summary numbers and chart data from the 20-pool robustness check."""
    rows = list(csv.DictReader(open(RESULTS / "phase2_robustness.csv", encoding="utf-8")))
    num = lambda r, k: float(r[k])
    random_evals = [num(r, "target") * (num(r, "pool") + 1) / (num(r, "hits") + 1) for r in rows]
    series = {
        "random": random_evals,
        "rule": [num(r, "sq_gap_stable_evals") for r in rows],
        "corrected": [num(r, "corrected_gap_evals") for r in rows],
        "model": [num(r, "model_evals") for r in rows],
    }
    ratios = [a / b for a, b in zip(series["rule"], series["model"])]
    med = {k: statistics.median(v) for k, v in series.items()}
    fmt_med = lambda v: f"{v:g}" if v < 100 else f"{v:.0f}"
    summary = {
        "pool_size": int(num(rows[0], "pool")),
        "ea_labeled": 4409,
        "median_random": round(med["random"]),
        "median_rule": fmt_med(med["rule"]),
        "median_corrected": fmt_med(med["corrected"]),
        "median_model": fmt_med(med["model"]),
        "acc_rule": f"{statistics.median(num(r, 'sq_gap_stable_acc') for r in rows):.1f}",
        "acc_corrected": f"{statistics.median(num(r, 'corrected_gap_acc') for r in rows):.1f}",
        "acc_model": f"{statistics.median(num(r, 'model_acc') for r in rows):.1f}",
        "ap_rule": f"{statistics.median(num(r, 'sq_gap_stable_ap') for r in rows):.3f}",
        "ap_corrected": f"{statistics.median(num(r, 'corrected_gap_ap') for r in rows):.3f}",
        "ap_model": f"{statistics.median(num(r, 'model_ap') for r in rows):.3f}",
        "ratio_median": f"{statistics.median(ratios):.2f}",
        "ratio_ge2": sum(1 for x in ratios if x >= 2),
        "wins": sum(1 for a, b in zip(series["model"], series["rule"]) if a < b),
        "wins_corrected": sum(1 for a, b in zip(series["model"], series["corrected"]) if a < b),
        "session_short": "501042555e83",
    }
    chart = {
        "title": "Calculations needed to find 10 excellent absorbers in 20 random pools",
        "rows": [
            {"label": "Random order", "color": "#8a8984", "values": [round(v, 1) for v in series["random"]], "median": med["random"]},
            {"label": "Textbook rule", "color": "#eb6834", "values": series["rule"], "median": med["rule"]},
            {"label": "Corrected-gap rule", "color": "#1baf7a", "values": series["corrected"], "median": med["corrected"]},
            {"label": "Artemis method", "color": "#2a78d6", "values": series["model"], "median": med["model"]},
        ],
    }
    return summary, chart


def shortlist_rows() -> list[dict]:
    """The 15 recommendations with their values from the frozen snapshot."""
    wanted = {jid for jid, _ in SHORTLIST}
    found: dict[str, dict] = {}
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["jid"] in wanted and row["split"] == "unlabeled" and row["jid"] not in found:
                found[row["jid"]] = row
    out = []
    for rank, (jid, note) in enumerate(SHORTLIST, start=1):
        row = found[jid]
        out.append({
            "rank": rank, "jid": jid, "formula": row["formula"], "formula_html": formula_html(row["formula"]),
            "spg": row["spg_symbol"], "spg_html": spacegroup_html(row["spg_symbol"]),
            "gap": f"{float(row['optb88vdw_bandgap']):.3f}",
            "ehull": f"{float(row['ehull']):.3f}", "formation_energy": row["formation_energy_peratom"], "note": note,
        })
    return out


def lab_report() -> tuple[str, str]:
    """The Scribe's report as markdown (without the lead's preamble) and as HTML."""
    text = (RESULTS / "phase2_run_2026-10-03" / "lab_report.md").read_text(encoding="utf-8")
    start = text.find("# Artemis solar lab")
    text = text[start:] if start >= 0 else text
    # Demote headings so the report nests under the page's own headings.
    shifted = re.sub(r"^(#{1,4}) ", lambda m: "#" * min(6, len(m.group(1)) + 2) + " ", text, flags=re.M)
    html = markdown.markdown(shifted, extensions=["tables", "fenced_code", "sane_lists"])
    html = html.replace("<table>", '<div class="table-wrap"><table class="data">').replace("</table>", "</table></div>")
    html = re.sub(r"(JVASP-\d+)", r'<span class="nowrap">\1</span>', html)
    return text, html


# ---------------------------------------------------------------- structured data
def crumbs(site: str, trail: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": site + path} for i, (name, path) in enumerate(trail)]}


def organization(site: str) -> dict:
    return {"@context": "https://schema.org", "@type": "Organization", "@id": site + "/#org", "name": "Artemis",
            "url": site + "/", "logo": site + "/icon-512.png", "sameAs": [REPO],
            "description": "An autonomous AI lab for scientific discovery that publishes everything it does.",
            "founder": {"@type": "Person", "name": "Peter Alesso"}}


def pages(site: str, r: dict) -> list[dict]:
    """Every page: template, output path, and its SEO metadata."""
    org = {"@type": "Organization", "@id": site + "/#org", "name": "Artemis", "url": site + "/"}
    report_ld = {
        "@context": "https://schema.org", "@type": "Report", "@id": site + FLAGSHIP_PATH + "#report",
        "headline": "Earth-abundant solar absorbers: which crystals to compute next",
        "description": ("Six AI agents searched NIST JARVIS-DFT for solar absorbers made of earth-abundant elements. On "
                        "held-out data their method found all 4 excellent absorbers in 8 expensive calculations, against 20 "
                        "for the textbook rule. A later check of a rebuilt copy on 20 pools needed a median of "
                        f"{r['median_model']} calculations against {r['median_rule']}, beating the textbook rule in {r['wins']} of 20."),
        "datePublished": BUILD_DATE, "dateModified": BUILD_DATE, "inLanguage": "en",
        "author": org, "publisher": org, "url": site + FLAGSHIP_PATH, "image": site + "/og/solar-result.png",
        "about": [{"@type": "Thing", "name": "Solar cell absorber materials"},
                  {"@type": "Thing", "name": "Spectroscopic limited maximum efficiency"},
                  {"@type": "Thing", "name": "Autonomous scientific discovery"}],
        "isBasedOn": [{"@type": "Dataset", "name": "JARVIS-DFT", "url": "https://jarvis.nist.gov/"},
                      {"@type": "Dataset", "name": "JARVIS-Leaderboard SLME benchmark",
                       "url": "https://github.com/usnistgov/jarvis_leaderboard"}],
        "citation": ["https://doi.org/10.1038/s41524-024-01259-w", "https://doi.org/10.1038/s41524-020-00440-1",
                     "https://doi.org/10.1021/acs.chemmater.9b02166"],
    }
    dataset_ld = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "Artemis robustness check: calculations to find 10 excellent solar absorbers in 20 random pools",
        "description": ("Post-hoc check run after the official test, using a rebuilt copy of the Artemis method. For 20 "
                        "random halvings of 4,409 earth-abundant JARVIS-DFT materials with known SLME (36 excellent "
                        "absorbers in total), the number of expensive evaluations random search, the textbook "
                        "stability-gated band-gap rule, a corrected-gap rule and the Artemis method needed to find 10 "
                        "materials with SLME of at least 30 percent and energy above hull of at most 0.1 eV per atom."),
        "url": site + FLAGSHIP_PATH + "#robustness", "creator": org, "datePublished": BUILD_DATE,
        "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
        "keywords": ["solar cells", "materials discovery", "JARVIS-DFT", "SLME", "autonomous research", "AI agents"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": site + "/data/phase2/robustness.csv"}],
        "variableMeasured": ["evaluations to 10 hits", "acceleration over random", "average precision"],
    }
    shortlist_ld = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "Artemis shortlist: 15 earth-abundant crystals to compute next for solar absorbers",
        "description": ("The top 15 earth-abundant JARVIS-DFT materials without an SLME value, ranked by the Artemis "
                        "method, with their OptB88vdW band gap, energy above hull, formation energy and notes. "
                        "Predictions, not measurements."),
        "url": site + FLAGSHIP_PATH + "#recommendations", "creator": org, "datePublished": BUILD_DATE,
        "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
        "keywords": ["solar absorbers", "earth-abundant materials", "JARVIS-DFT", "materials discovery"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": site + "/data/phase2/shortlist.csv"}],
    }
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    website_ld = {"@context": "https://schema.org", "@type": "WebSite", "@id": site + "/#site", "name": "Artemis",
                  "url": site + "/", "inLanguage": "en", "publisher": org,
                  "description": "An autonomous AI lab that turns scientific questions into measured experiments."}
    return [
        {"template": "index.html", "out": "index.html", "path": "/", "nav": "", "priority": "1.0",
         "title": "Artemis: an autonomous AI lab for materials discovery",
         "description": ("Open-source AI lab: agents turn a science question into a measured experiment. First run: solar "
                         "absorbers found in 8 calculations; the textbook rule needed 20."),
         "jsonld": [organization(site), website_ld], "scripts": []},
        {"template": "lab.html", "out": "lab.html", "path": "/lab", "nav": "lab", "priority": "0.8",
         "title": "Start an investigation | Artemis lab",
         "description": ("Propose a scientific question and watch the Artemis agents draft a testable experiment live, or "
                         "rerun the solar-absorber program. Finished runs are published."),
         "jsonld": [crumbs(site, [("Artemis", "/"), ("Start an investigation", "/lab")])], "scripts": ["/assets/md.js", "/assets/lab.js"]},
        {"template": "results.html", "out": "results.html", "path": "/results", "nav": "results", "priority": "0.9",
         "title": "Published lab runs | Artemis",
         "description": "Every investigation the Artemis lab has finished, with full reports, data and code, plus the runs in progress right now.",
         "jsonld": [crumbs(site, [("Artemis", "/"), ("Published lab runs", "/results")]),
                    {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Artemis results",
                     "url": site + "/results", "mainEntity": {"@type": "ItemList", "itemListElement": [
                         {"@type": "ListItem", "position": 1, "url": site + FLAGSHIP_PATH,
                          "name": "Earth-abundant solar absorbers: which crystals to compute next"}]}}],
         "scripts": ["/assets/results.js"]},
        {"template": "result_solar.html", "out": "results/solar-absorbers-2026-10-03.html", "path": FLAGSHIP_PATH,
         "nav": "results", "priority": "0.9", "og_type": "article", "og_image": "/og/solar-result.png",
         "published": BUILD_DATE,
         "og_alt": "Chart: on held-out data the Artemis method found all 4 excellent solar absorbers in 8 calculations, the textbook rule in 20",
         "title": "Earth-abundant solar absorbers to compute next | Artemis",
         "og_title": "Earth-abundant solar absorbers: which crystals to compute next",
         "description": ("AI agents ranked earth-abundant crystals to find excellent solar absorbers in 8 calculations "
                         "instead of 20 on held-out data, and list 15 materials to compute next."),
         "jsonld": [report_ld, dataset_ld, shortlist_ld, crumbs(site, [("Artemis", "/"), ("Published lab runs", "/results"),
                                                         ("Earth-abundant solar absorbers", FLAGSHIP_PATH)])], "scripts": []},
        {"template": "method.html", "out": "method.html", "path": "/method", "nav": "method", "priority": "0.7",
         "title": "How Artemis works: first principles, AutoResearch, six agents",
         "description": ("How Artemis works: first-principles framing, Karpathy's three-file AutoResearch loop, six AI "
                         "agents with separate jobs, and guardrails that keep results honest."),
         "jsonld": [crumbs(site, [("Artemis", "/"), ("How Artemis works", "/method")]),
                    {"@context": "https://schema.org", "@type": "TechArticle", "headline": "How the Artemis lab works",
                     "description": ("First-principles framing, a three-file AutoResearch loop, six AI agents with "
                                     "separate jobs, and guardrails."),
                     "image": site + "/og/artemis.png", "author": org, "publisher": org,
                     "datePublished": BUILD_DATE, "dateModified": BUILD_DATE, "url": site + "/method"}], "scripts": []},
        {"template": "about.html", "out": "about.html", "path": "/about", "nav": "about", "priority": "0.6",
         "title": "About Artemis: who built it, data sources and questions",
         "description": "Why Artemis exists, who built it, where its materials data comes from, and plain answers to the questions people ask most.",
         "jsonld": [crumbs(site, [("Artemis", "/"), ("About", "/about")]), faq_ld,
                    {"@context": "https://schema.org", "@type": "AboutPage", "url": site + "/about", "about": org}],
         "scripts": []},
        {"template": "run.html", "out": "results/run.html", "path": "/results/run", "nav": "results", "noindex": True,
         "title": "Lab run | Artemis", "description": "A saved Artemis lab run with its report.",
         "jsonld": [], "scripts": ["/assets/md.js", "/assets/results.js"]},
        {"template": "status.html", "out": "status.html", "path": "/status", "nav": "", "noindex": True,
         "title": "System status | Artemis", "description": "Live check of each part of the Artemis lab.",
         "jsonld": [], "scripts": ["/assets/status.js"]},
        {"template": "404.html", "out": "404.html", "path": "/404", "nav": "", "noindex": True,
         "title": "Page not found | Artemis", "description": "This page does not exist.", "jsonld": [], "scripts": []},
    ]


# ---------------------------------------------------------------- text files for crawlers and AI assistants
def llms_txt(site: str, r: dict) -> str:
    return f"""# Artemis

> Artemis is an open-source autonomous AI lab for scientific discovery. It turns a scientific question into a measured experiment, runs it with six AI agents on public data, tests the result once on held-out data, and publishes the report, code and data. In its first run (October 3, 2026) the agents built a way to choose earth-abundant solar-cell materials to calculate that found every excellent candidate on held-out data in 8 expensive calculations, where the textbook rule needed 20.

Key facts:

- Question: which earth-abundant crystals in NIST JARVIS-DFT should be calculated next to find excellent solar absorbers fastest. Excellent means a spectroscopic limited maximum efficiency (SLME) of at least 30 percent and an energy above the convex hull of at most 0.1 eV per atom. Earth-abundant means every element has a crustal abundance of at least 1 mg/kg; Cd, Hg, Pb, Tl, As and radioactive elements are excluded.
- Official held-out test (429 materials, 4 excellent absorbers, run once): Artemis method 8 calculations to find all 4; textbook rule (stable materials first, then band gap nearest 1.34 eV) 20; random search about 344.
- Later robustness check by the Artemis team, using a rebuilt copy of the method on 20 random halves of the same 4,409 materials (36 excellent absorbers in total, so the pools overlap): median calculations to find 10 excellent absorbers were {r['median_model']} for Artemis, {r['median_corrected']} for a corrected band-gap rule, {r['median_rule']} for the textbook rule and about {r['median_random']:,} for random search. Artemis beat the textbook rule in {r['wins']} of 20 pools.
- The results are computational predictions from DFT data, not laboratory measurements, and no new material has been confirmed.
- Agents: Compiler, Scout, Planner, Experimenter, Skeptic and Scribe. Models: Claude Opus 5.5 and Claude Haiku 4.5. Harness: Omnigent (open source, from Databricks) on Modal.
- Built by Peter Alesso for Challenge 03 of the 7th Global AI Hackathon. Code under the MIT license.

## Pages

- [First result: earth-abundant solar absorbers]({site}{FLAGSHIP_PATH}): full report, held-out test, robustness check, materials to compute next
- [How Artemis works]({site}/method): first principles, the three-file AutoResearch loop, the six agents and guardrails
- [Published lab runs]({site}/results): every finished run
- [Start an investigation]({site}/lab): propose a question or rerun the flagship program
- [About]({site}/about): who built Artemis, data sources, frequently asked questions

## Data

- [Robustness check, 20 pools (CSV)]({site}/data/phase2/robustness.csv)
- [Top 15 materials to compute next (CSV)]({site}/data/phase2/shortlist.csv)
- [The lab's own report (Markdown)]({site}/data/phase2/lab_report.md)

## Optional

- [Full text for language models]({site}/llms-full.txt)
- [Source code on GitHub]({REPO})
"""


def llms_full(site: str, r: dict, shortlist: list[dict], report_md: str) -> str:
    rows = "\n".join(f"{s['rank']}. {s['formula']} ({s['jid']}), space group {s['spg']}, quick (OptB88vdW) band gap {s['gap']} eV, "
                     f"energy above hull {s['ehull']} eV/atom. {s['note']}." for s in shortlist)
    faq = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in FAQ)
    report = re.sub(r"^(#{1,4}) ", lambda m: "#" * min(6, len(m.group(1)) + 2) + " ", report_md, flags=re.M)
    return f"""# Artemis: full text for language models

Source: {site}/ . Code: {REPO} (MIT license). Last updated {BUILD_DATE}.

## What Artemis is

Artemis is an open-source autonomous AI lab for scientific discovery, built by Peter Alesso for Challenge 03 of the 7th Global AI Hackathon, with Claude (Anthropic's AI assistant) as a coding partner. A run follows five steps: the Compiler frames the question as a fixed test with a pre-registered threshold and metric; the Scout searches the literature; the Planner and Experimenters try ideas in waves against a frozen scoring harness; the Skeptic re-runs and checks every apparent gain; and the Compiler runs the held-out test exactly once before the Scribe writes the report.

## How it works

The design follows Andrej Karpathy's three-file AutoResearch pattern and Elon Musk's first-principles "algorithm". Three files define each investigation: harness.py (frozen by humans: data check, candidate pool, success threshold, metric, time limit and experiment log, all fingerprinted), experiment.py (the one file the agents change: a function that ranks candidates), and program.md (the human's instructions, including "never stop" until the experiment budget is spent).

Agents and models: Compiler (Claude Opus 5.5) leads the run and runs the final test once; Scout (Claude Haiku 4.5) searches literature and databases; Planner (Opus 5.5) proposes ideas; Experimenter (Opus 5.5) implements and scores one idea each, several in parallel; Skeptic (Opus 5.5) reproduces and challenges every gain; Scribe (Opus 5.5) writes the report. They run in one Omnigent session (the open-source agent harness from Databricks) inside a Modal sandbox.

Guardrails: spending and tool-call caps enforced by Omnigent policies; Scout, Planner and Skeptic cannot edit files; destructive commands are blocked; the harness refuses experiments that read files or use the network, limits the number of experiments, and allows the held-out test once.

## First result: earth-abundant solar absorbers (October 3, 2026)

Question: among earth-abundant inorganic crystals in NIST JARVIS-DFT, which should a lab calculate next to find excellent solar absorbers fastest? An excellent absorber has a spectroscopic limited maximum efficiency (SLME) of at least 30 percent and an energy above the convex hull of at most 0.1 eV per atom. Earth-abundant means every element has a crustal abundance of at least 1 mg/kg (CRC Handbook, 97th edition); Cd, Hg, Pb, Tl, As and radioactive elements are excluded.

Final method: near-stable materials first; within each group, rank by SLME predicted by 500 randomized decision trees (ExtraTreesRegressor) trained on 7,250 JARVIS materials, using cheap DFT properties and composition.

Official held-out test (429 materials, 4 hits, used once): Artemis 8 calculations to find all 4; textbook rule (stable first, then band gap nearest 1.34 eV) 20; band-gap rule alone 199; random about 344.

Robustness check (run after the official test by the Artemis team, using a rebuilt copy of the final method; 20 random halves of 4,409 materials containing 36 excellent absorbers, so the pools overlap and are not independent): median calculations to find 10 hits were {r['median_model']} for Artemis, {r['median_corrected']} for the corrected-gap rule, {r['median_rule']} for the textbook rule and about {r['median_random']:,} for random search. Artemis beat the textbook rule in {r['wins']} of 20 pools; the median ratio was {r['ratio_median']}.

Lessons: stability is the first filter; the quick OptB88vdW band gap of excellent absorbers is near 0.7 eV because that method underestimates gaps (their accurate TBmBJ gaps are near 1.35 eV); composition adds information beyond the gap.

Top 15 earth-abundant materials without an SLME value in JARVIS, to calculate next (predictions, not discoveries):

{rows}

Limits: labels are computational (SLME from DFT optics); the official pools were small (9 and 4 hits); the robustness check was post hoc; the Materials Project cross-check did not run in this session.

## Frequently asked questions

{faq}

## The lab's own report

{report}
"""


# ---------------------------------------------------------------- icons and social images
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#f4f6f9"/><g fill="none" stroke="#14203b" stroke-width="1.6"><path d="M8 8h16v16H8z"/><path d="M8 8l8 8 8-8M8 24l8-8 8 8"/></g><circle cx="8" cy="8" r="3.4" fill="#2343c8"/><circle cx="24" cy="8" r="3.4" fill="#c27c00"/><circle cx="8" cy="24" r="3.4" fill="#c27c00"/><circle cx="24" cy="24" r="3.4" fill="#2343c8"/><circle cx="16" cy="16" r="2.6" fill="#14203b"/></svg>
"""


def render_images(r: dict) -> None:
    """Render icons and 1200x630 social cards with headless Chromium (Playwright)."""
    from playwright.sync_api import sync_playwright

    fonts = (PUBLIC / "assets" / "fonts").as_uri()
    base_css = f"""
      @font-face {{ font-family: S; src: url('{fonts}/schibsted-grotesk-latin-wght-normal.woff2'); font-weight: 400 900; }}
      * {{ margin: 0; box-sizing: border-box; }}
      body {{ width: 1200px; height: 630px; background: #f4f6f9; font-family: S, Arial; color: #14203b; position: relative; overflow: hidden; }}
      .band {{ position: absolute; left: 0; right: 0; top: 0; height: 10px; background: linear-gradient(90deg,#5b3cc4,#2a78d6 22%,#1baf7a 44%,#e3b11a 64%,#eb6834 82%,#c8352f); }}
      .brand {{ position: absolute; left: 72px; top: 64px; display: flex; gap: 14px; align-items: center; font-size: 34px; font-weight: 700; }}
      .brand svg {{ width: 48px; height: 48px; }}
    """
    mark = FAVICON_SVG.replace('<rect width="32" height="32" rx="7" fill="#f4f6f9"/>', "")
    home = f"""<html><head><style>{base_css}
      h1 {{ position: absolute; left: 72px; top: 170px; width: 640px; font-size: 62px; line-height: 1.06; letter-spacing: -2px; font-weight: 700; }}
      p {{ position: absolute; left: 72px; top: 470px; width: 620px; font-size: 26px; line-height: 1.35; color: #46526d; }}
      .lattice {{ position: absolute; right: 70px; top: 120px; width: 400px; height: 400px; }}
    </style></head><body><div class="band"></div><div class="brand">{mark}Artemis</div>
      <h1>An AI lab that runs its own experiments and shows its work.</h1>
      <p>First result: solar absorbers found in 8 calculations where the textbook rule needed 20.</p>
      <svg class="lattice" viewBox="0 0 200 200"><g stroke="#aeb8cb" stroke-width="2.4" fill="none"><path d="M40 70h90v90H40zM80 40h90v90H80zM40 70l40-30M130 70l40-30M40 160l40-30M130 160l40-30M85 115h0"/></g>
      <g fill="#2343c8"><circle cx="40" cy="70" r="13"/><circle cx="130" cy="160" r="13"/><circle cx="170" cy="40" r="13"/><circle cx="80" cy="130" r="13"/></g>
      <g fill="#d08a0a"><circle cx="130" cy="70" r="16"/><circle cx="40" cy="160" r="16"/><circle cx="80" cy="40" r="16"/><circle cx="170" cy="130" r="16"/></g></svg>
    </body></html>"""
    bars = [("Random search", 344, "#8a8984"), ("Textbook rule", 20, "#eb6834"), ("Artemis method", 8, "#2a78d6")]
    import math
    scale = lambda v: 40 + 560 * (math.log10(v) - math.log10(4)) / (math.log10(500) - math.log10(4))
    bar_html = "".join(
        f'<div class="row"><span class="label">{label}</span><span class="bar" style="width:{scale(v):.0f}px;background:{c}"></span>'
        f'<span class="val">{thousands(v) if v >= 100 else f"{v:g}"}</span></div>' for label, v, c in bars)
    result = f"""<html><head><style>{base_css}
      h1 {{ position: absolute; left: 72px; top: 150px; width: 1060px; font-size: 52px; line-height: 1.08; letter-spacing: -1.5px; font-weight: 700; }}
      .chart {{ position: absolute; left: 72px; top: 330px; }}
      .row {{ display: flex; align-items: center; gap: 18px; height: 64px; }}
      .label {{ width: 270px; font-size: 26px; font-weight: 600; }}
      .bar {{ height: 30px; border-radius: 4px; display: inline-block; }}
      .val {{ font-size: 28px; font-weight: 700; }}
      .note {{ position: absolute; left: 72px; bottom: 34px; font-size: 21px; color: #6b7690; }}
    </style></head><body><div class="band"></div><div class="brand">{mark}Artemis</div>
      <h1>Earth-abundant solar absorbers: which crystals to compute next</h1>
      <div class="chart">{bar_html}</div>
      <div class="note">Expensive calculations to find all 4 excellent absorbers in the held-out test of 429 materials (log scale)</div>
    </body></html>"""
    icon = f"""<html><head><style>* {{ margin: 0 }} body {{ width: 512px; height: 512px; background: #f4f6f9; display: grid; place-items: center; }} svg {{ width: 400px; height: 400px; }}</style></head>
      <body>{mark}</body></html>"""
    (PUBLIC / "og").mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        card = PUBLIC / "og" / "_card.html"  # loaded from disk so the local fonts apply
        for html, out in ((home, "og/artemis.png"), (result, "og/solar-result.png")):
            card.write_text(html, encoding="utf-8")
            page.goto(card.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            page.screenshot(path=str(PUBLIC / out))
        page = browser.new_page(viewport={"width": 512, "height": 512})
        card.write_text(icon, encoding="utf-8")
        page.goto(card.as_uri(), wait_until="load")
        page.screenshot(path=str(PUBLIC / "icon-512.png"))
        browser.close()
        card.unlink()
    from PIL import Image
    big = Image.open(PUBLIC / "icon-512.png").convert("RGB")
    big.resize((180, 180), Image.LANCZOS).save(PUBLIC / "apple-touch-icon.png")
    big.resize((192, 192), Image.LANCZOS).save(PUBLIC / "icon-192.png")
    big.resize((32, 32), Image.LANCZOS).save(PUBLIC / "favicon-32.png")


# ---------------------------------------------------------------- main
def build(site_url: str, images: bool) -> None:
    site = site_url.rstrip("/")
    node_modules = SITE / "node_modules"
    if not (node_modules / "three").exists():
        run(["npm", "install", "--silent"], SITE)

    keep = {name: (PUBLIC / name).read_bytes() for name in
            ("og/artemis.png", "og/solar-result.png", "icon-512.png", "icon-192.png", "apple-touch-icon.png", "favicon-32.png")
            if (PUBLIC / name).exists()}
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "assets" / "fonts").mkdir(parents=True)
    for name, data in keep.items():
        (PUBLIC / name).parent.mkdir(parents=True, exist_ok=True)
        (PUBLIC / name).write_bytes(data)

    # 1. assets and fonts
    for src in (SITE / "assets").iterdir():
        shutil.copy2(src, PUBLIC / "assets" / src.name)
    font_files = [
        node_modules / "@fontsource-variable/schibsted-grotesk/files/schibsted-grotesk-latin-wght-normal.woff2",
        node_modules / "@fontsource-variable/source-serif-4/files/source-serif-4-latin-opsz-normal.woff2",
    ]
    for font in font_files:
        shutil.copy2(font, PUBLIC / "assets" / "fonts" / font.name)
    for license_dir in ("@fontsource-variable/schibsted-grotesk", "@fontsource-variable/source-serif-4"):
        lic = node_modules / license_dir / "LICENSE"
        if lic.exists():
            shutil.copy2(lic, PUBLIC / "assets" / "fonts" / (license_dir.split("/")[-1] + "-OFL.txt"))

    # 2. Three.js hero bundle
    run([str(node_modules / ".bin" / "esbuild"), "src/lattice.js", "--bundle", "--minify", "--format=iife",
         "--target=es2019", "--legal-comments=none", f"--outfile={PUBLIC / 'assets' / 'lattice.js'}"], SITE)

    # 3. data
    r, chart = robustness()
    shortlist = shortlist_rows()
    report_md, report_html = lab_report()
    data_dir = PUBLIC / "data" / "phase2"
    data_dir.mkdir(parents=True)
    (data_dir / "robustness.json").write_text(json.dumps(chart), encoding="utf-8")
    shutil.copy2(RESULTS / "phase2_robustness.csv", data_dir / "robustness.csv")
    (data_dir / "lab_report.md").write_text(report_md, encoding="utf-8")
    with open(data_dir / "shortlist.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "jarvis_id", "formula", "space_group", "optb88vdw_gap_ev", "energy_above_hull_ev_per_atom",
                         "formation_energy_ev_per_atom", "note"])
        for s in shortlist:
            writer.writerow([s["rank"], s["jid"], s["formula"], s["spg"], s["gap"], s["ehull"], s["formation_energy"], s["note"]])
    static_results = [{
        "path": FLAGSHIP_PATH, "title": "Earth-abundant solar absorbers: which crystals to compute next",
        "summary": ("Six agents built a ranking method that found all 4 excellent solar absorbers on held-out data in "
                    "8 expensive calculations, against 20 for the textbook rule. A later check of a rebuilt copy beat "
                    f"the textbook rule in {r['wins']} of 20 pools. Includes 15 materials to compute next."),
        "kpi": "8 vs 20", "kpi_label": "calculations to find every excellent absorber on held-out data",
        "kind_label": "Flagship program", "date": BUILD_DATE, "date_label": "October 3, 2026",
    }]
    (PUBLIC / "data" / "results.json").write_text(json.dumps({"results": [
        {**item, "url": site + item["path"]} for item in static_results]}, indent=2), encoding="utf-8")

    # 4. pages
    version = hashlib.sha256(b"".join((PUBLIC / "assets" / n).read_bytes() for n in sorted(os.listdir(PUBLIC / "assets"))
                                      if (PUBLIC / "assets" / n).is_file())).hexdigest()[:10]
    env = Environment(loader=FileSystemLoader([str(SITE / "templates"), str(SITE / "pages")]),
                      autoescape=select_autoescape(["html"]), trim_blocks=False, lstrip_blocks=False)
    env.filters["thousands"] = thousands
    trials = [{"name": n, "idea": i, "evals": e, "acc": a, "outcome": o, "tag": t, "kept": o.startswith("Kept")}
              for n, i, e, a, o, t in TRIALS]
    all_pages = pages(site, r)
    for meta in all_pages:
        meta.setdefault("og_image", "/og/artemis.png")
        html = env.get_template(meta["template"]).render(
            page=meta, nav=NAV, site_url=site, version=version, flagship_path=FLAGSHIP_PATH, r=r,
            trials=trials, shortlist=shortlist, lab_report_html=report_html, static_results=static_results,
            faq=[{"q": q, "a": a} for q, a in FAQ])
        out = PUBLIC / meta["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")

    # 5. crawler and assistant files
    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{site}{m['path']}</loc><lastmod>{today}</lastmod><priority>{m['priority']}</priority></url>"
        for m in all_pages if not m.get("noindex"))
    (PUBLIC / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(
        "# Artemis welcomes search engines and AI assistants.\n"
        "User-agent: *\nAllow: /\nDisallow: /api/\n\n"
        "User-agent: GPTBot\nAllow: /\nDisallow: /api/\n\nUser-agent: ClaudeBot\nAllow: /\nDisallow: /api/\n\n"
        "User-agent: PerplexityBot\nAllow: /\nDisallow: /api/\n\nUser-agent: Google-Extended\nAllow: /\n\n"
        f"Sitemap: {site}/sitemap.xml\n", encoding="utf-8")
    (PUBLIC / "llms.txt").write_text(llms_txt(site, r), encoding="utf-8")
    (PUBLIC / "llms-full.txt").write_text(llms_full(site, r, shortlist, report_md), encoding="utf-8")
    (PUBLIC / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    (PUBLIC / "site.webmanifest").write_text(json.dumps({
        "name": "Artemis", "short_name": "Artemis", "start_url": "/", "display": "standalone",
        "background_color": "#f4f6f9", "theme_color": "#f4f6f9",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2), encoding="utf-8")
    if images or not (PUBLIC / "og" / "artemis.png").exists():
        render_images(r)
    print(f"Built {len(all_pages)} pages into {PUBLIC.relative_to(ROOT)} for {site} (assets version {version}).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Artemis website into public/.")
    parser.add_argument("--site-url", default=os.environ.get("ARTEMIS_SITE_URL", DEFAULT_SITE_URL),
                        help="the public address of the site, e.g. https://artemis.example.org")
    parser.add_argument("--images", action="store_true", help="re-render the social-card images and icons")
    args = parser.parse_args()
    if not re.match(r"^https://[a-z0-9.-]+(:\d+)?$", args.site_url.rstrip("/")):
        print("--site-url must look like https://example.org (https, no path).")
        return 2
    build(args.site_url, args.images)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
