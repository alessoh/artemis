"""Search the published literature for a material or a topic.

Usage (from the repository root):

    python lab/solar/tools/literature.py "Cu2ZnSnS4 solar absorber" [-n 8]

Searches OpenAlex (journal articles, with DOIs and citation counts) and falls
back to arXiv if OpenAlex is unavailable. Prints JSON with title, year,
venue, DOI or URL, and citation count for each result, so every claim in a
report can be traced to a real source. Nothing is invented: if both services
fail, the error is printed instead.

Optional environment variables: OPENALEX_API_KEY (used if set) and
ARTEMIS_CONTACT_EMAIL (sent as OpenAlex's polite-pool "mailto").
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "artemis-lab/0.2 (scientific discovery research)"


def fetch(url: str, timeout: float = 30.0) -> bytes:
    """GET *url* and return the body."""
    request = urllib.request.Request(url, headers={"user-agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def search_openalex(query: str, n: int) -> list[dict]:
    """Return up to *n* works from OpenAlex, most relevant first."""
    params = {"search": query, "per-page": str(n),
              "select": "title,publication_year,doi,cited_by_count,primary_location,id"}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    if os.environ.get("ARTEMIS_CONTACT_EMAIL"):
        params["mailto"] = os.environ["ARTEMIS_CONTACT_EMAIL"]
    payload = json.loads(fetch("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))
    works = []
    for item in payload.get("results", []):
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        works.append({
            "title": item.get("title"),
            "year": item.get("publication_year"),
            "venue": source.get("display_name"),
            "doi": item.get("doi"),
            "url": item.get("doi") or item.get("id"),
            "cited_by": item.get("cited_by_count"),
            "database": "OpenAlex",
        })
    return works


def search_arxiv(query: str, n: int) -> list[dict]:
    """Return up to *n* preprints from arXiv, most relevant first."""
    params = {"search_query": f"all:{query}", "start": "0", "max_results": str(n),
              "sortBy": "relevance"}
    body = fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    works = []
    for entry in root.findall("a:entry", ns):
        title = " ".join((entry.findtext("a:title", default="", namespaces=ns)).split())
        published = entry.findtext("a:published", default="", namespaces=ns)
        works.append({
            "title": title,
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "venue": "arXiv",
            "doi": None,
            "url": entry.findtext("a:id", default="", namespaces=ns),
            "cited_by": None,
            "database": "arXiv",
        })
    return works


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search OpenAlex, then arXiv.")
    parser.add_argument("query")
    parser.add_argument("-n", type=int, default=8)
    args = parser.parse_args(argv)
    errors = []
    for name, searcher in (("OpenAlex", search_openalex), ("arXiv", search_arxiv)):
        try:
            works = searcher(args.query, args.n)
        except (urllib.error.URLError, ET.ParseError, json.JSONDecodeError, TimeoutError) as exc:
            errors.append(f"{name}: {exc}")
            continue
        print(json.dumps({"query": args.query, "results": works, "errors": errors}, indent=2))
        return 0
    print(json.dumps({"query": args.query, "results": [], "errors": errors}, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
