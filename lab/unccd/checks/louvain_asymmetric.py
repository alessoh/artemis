"""Print the Louvain lines the authors captured in their own knit output, to compare
the asymmetric and aggregation entries with Table 13 of the paper.

    python lab/unccd/checks/louvain_asymmetric.py
"""
import html
import re
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "ccd"
f = VENDOR / "simulations/clustering/Algo_Compare_Clustering/Louvain/Simulation/Real_Data/Real_Data_Louvain.html"
text = f.read_text(encoding="utf-8", errors="ignore")
for line in re.findall(r"[A-Za-z_]+ x louvain: the ARI is [^\"<]*", text):
    print(html.unescape(line))
