"""Cross-check candidate materials against the Materials Project.

Usage (from the repository root):

    python lab/solar/tools/mp_lookup.py Cu2ZnSnS4 BaZrS3 ...

For each formula it prints, as JSON, the Materials Project entries with that
reduced formula: material id, band gap (PBE/GGA, eV), whether the gap is
direct, energy above hull (eV/atom), whether the entry is on the hull, whether
it is purely theoretical (no matching ICSD experimental structure), and the
space group. The API key is read from the environment variable MP_API_KEY and
is never printed.

Materials Project band gaps are GGA/GGA+U gaps and usually underestimate the
true gap; compare trends, not absolute values, with JARVIS OptB88vdW gaps.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://api.materialsproject.org/materials/summary/"
FIELDS = [
    "material_id", "formula_pretty", "band_gap", "is_gap_direct",
    "energy_above_hull", "is_stable", "theoretical", "symmetry",
]
CITATION = ("Jain et al., APL Materials 1, 011002 (2013); Materials Project, "
            "https://materialsproject.org")


def lookup(formula: str, api_key: str, limit: int = 10) -> dict:
    """Return the Materials Project entries for one reduced formula."""
    query = urllib.parse.urlencode({
        "formula": formula, "_fields": ",".join(FIELDS), "_limit": str(limit),
    })
    request = urllib.request.Request(
        f"{ENDPOINT}?{query}",
        headers={"x-api-key": api_key, "accept": "application/json",
                 "user-agent": "artemis-lab/0.2"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            reason = "the API key was refused" if exc.code in (401, 403) else f"HTTP {exc.code}"
            return {"formula": formula, "error": reason}
        except urllib.error.URLError as exc:
            return {"formula": formula, "error": f"network error: {exc.reason}"}
    entries = []
    for doc in payload.get("data", []):
        symmetry = doc.get("symmetry") or {}
        entries.append({
            "material_id": doc.get("material_id"),
            "formula": doc.get("formula_pretty"),
            "band_gap_ev": doc.get("band_gap"),
            "is_gap_direct": doc.get("is_gap_direct"),
            "energy_above_hull_ev_per_atom": doc.get("energy_above_hull"),
            "is_stable": doc.get("is_stable"),
            "theoretical": doc.get("theoretical"),
            "spacegroup": symmetry.get("symbol"),
            "url": f"https://next-gen.materialsproject.org/materials/{doc.get('material_id')}",
        })
    entries.sort(key=lambda e: (e["energy_above_hull_ev_per_atom"] is None,
                                e["energy_above_hull_ev_per_atom"] or 0.0))
    return {"formula": formula, "entries": entries}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    api_key = os.environ.get("MP_API_KEY", "").strip()
    if not api_key:
        print(json.dumps({"error": "MP_API_KEY is not set in this environment; "
                                   "the Materials Project cross-check is unavailable."}))
        return 1
    results = [lookup(formula, api_key) for formula in argv]
    print(json.dumps({"source": CITATION, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
