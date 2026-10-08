"""Build the frozen data snapshot for the Artemis Langlands program.

Run once, by a human, from the artemis folder (needs PARI through cypari2):

    python lab/langlands/prepare_data.py

Sources
-------
1. John Cremona's elliptic curve tables (github.com/JohnCremona/ecdata) at a
   pinned commit: one curve per isogeny class over Q for every conductor
   N < 500,000 (files curves/*), with its rank, and the Atkin-Lehner signs at
   the bad primes and a_p for p < 100 (files aplist/*).
2. The LMFDB list of all elliptic curves over Q(sqrt 5) (field 2.2.5.1),
   downloaded by Peter Alesso on 2026-10-08 and committed as
   data/raw/lmfdb_ec_nf_2.2.5.1_20261008.txt.

What it writes (lab/langlands/data/)
-------------------------------------
rank_signs.tsv.gz  every class over Q with rank 0 or 2: conductor, rank, the
                   bad primes with exponent and local root number, and a_p for
                   the good primes below 100.
murm_q.jsonl.gz    every class over Q with 11 <= N < 5,000: rank, global root
                   number, local root numbers, and a_p for every good prime
                   p <= N (computed with PARI).
murm_k.jsonl.gz    one curve per isogeny class over Q(sqrt 5): conductor norm,
                   rank (or null if the LMFDB gives only bounds), PARI's global
                   root number w, the bad primes as (norm, exponent, a_P), the
                   product of finite local signs where every bad prime is
                   multiplicative (local sign -a_P; null otherwise, since this
                   PARI computes local root numbers only over Q), and a_P for
                   every degree-one prime P not dividing the conductor with
                   norm <= the conductor norm.
manifest.json      sources, SHA-256 of every output, counts and checks.

Checks (the build stops if any fails)
-------------------------------------
Over Q: for every class written to murm_q, PARI's local root numbers equal
Cremona's Atkin-Lehner signs, w = -(product of local signs), and w = (-1)^rank.
Over Q(sqrt 5): for every class, PARI's conductor norm equals the LMFDB's,
the reduction type agrees with a_P at each bad prime, w = (-1)^rank where the
rank is known, and for every semistable class w = +(product of the finite
local signs -a_P), the sign of the two real places being (-1)^2 = +1.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
RAW_K = DATA / "raw" / "lmfdb_ec_nf_2.2.5.1_20261008.txt"
ECDATA_REPO = "https://github.com/JohnCremona/ecdata"
ECDATA_COMMIT = "25cec5ecfec8b9f016eb1631ac633194c2bed39f"
MAX_N = 500_000
MURM_Q_MAX_N = 5_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def factor_small(n: int) -> list[tuple[int, int]]:
    """Trial-division factorisation (n < 10**6)."""
    out, p = [], 2
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            out.append((p, e))
        p += 1 if p == 2 else 2
    if n > 1:
        out.append((n, 1))
    return out


def primes_upto(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n + 1) if sieve[i]]


P25 = primes_upto(100)
assert len(P25) == 25


def clone_ecdata(target: Path) -> Path:
    subprocess.run(["git", "-c", "gc.auto=0", "clone", "-q", "--filter=blob:none", "--sparse",
                    ECDATA_REPO, str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "-c", "gc.auto=0", "checkout", "-q", ECDATA_COMMIT], check=True)
    subprocess.run(["git", "-C", str(target), "-c", "gc.auto=0", "sparse-checkout", "set", "curves", "aplist"],
                   check=True)
    return target


def read_q(ecdata: Path) -> list[dict]:
    """One row per isogeny class over Q with N < MAX_N."""
    curves: dict[tuple[int, str], tuple[str, int]] = {}
    for path in sorted((ecdata / "curves").glob("curves.*")):
        for line in open(path, encoding="ascii"):
            f = line.split()
            curves[(int(f[0]), f[1])] = (f[3], int(f[4]))
    rows = []
    for path in sorted((ecdata / "aplist").glob("aplist.*")):
        for line in open(path, encoding="ascii"):
            f = line.split()
            N, code = int(f[0]), f[1]
            if N >= MAX_N:
                continue
            a25, bq = f[2:27], f[27:]
            ai, rank = curves[(N, code)]
            signs: dict[int, int] = {}
            ap_good: list[int | None] = []
            for p, v in zip(P25, a25):
                if N % p == 0:
                    signs[p] = 1 if v == "+" else -1
                    ap_good.append(None)
                else:
                    ap_good.append(int(v))
            for s in bq:
                signs[int(s[2:-1])] = 1 if s[0] == "+" else -1
            fac = factor_small(N)
            if sorted(signs) != [p for p, _ in fac]:
                raise SystemExit(f"{N}{code}: signs at {sorted(signs)} but bad primes {fac}")
            rows.append({"N": N, "class": code, "ai": ai, "rank": rank,
                         "bad": [(p, e, signs[p]) for p, e in fac], "ap25": ap_good})
    if len(rows) != len(curves):
        raise SystemExit(f"{len(rows)} aplist rows but {len(curves)} classes")
    return rows


def write_rank_signs(rows: list[dict], path: Path) -> dict:
    counts = {0: 0, 2: 0}
    with gzip.open(path, "wt", encoding="ascii", compresslevel=9) as out:
        out.write("N\tclass\trank\tbad\tap25\n")
        for r in rows:
            if r["rank"] not in (0, 2):
                continue
            prod = 1
            for _, _, s in r["bad"]:
                prod *= s
            if -prod != 1:  # rank 0 and 2 both have w = +1
                raise SystemExit(f"{r['N']}{r['class']}: rank {r['rank']} but w = {-prod}")
            counts[r["rank"]] += 1
            bad = ";".join(f"{p}:{e}:{s:+d}" for p, e, s in r["bad"])
            ap = ",".join("" if a is None else str(a) for a in r["ap25"])
            out.write(f"{r['N']}\t{r['class']}\t{r['rank']}\t{bad}\t{ap}\n")
    return counts


def build_murm_q(rows: list[dict], pari, path: Path) -> dict:
    n = checked = 0
    with gzip.open(path, "wt", encoding="ascii", compresslevel=9) as out:
        for r in rows:
            if r["N"] >= MURM_Q_MAX_N:
                continue
            E = pari.ellinit(pari(r["ai"]))
            prod = 1
            for p, _, s in r["bad"]:
                if int(pari.ellrootno(E, p)) != s:
                    raise SystemExit(f"{r['N']}{r['class']}: local root number at {p} disagrees")
                prod *= s
            w = int(pari.ellrootno(E))
            if w != -prod or w != (-1) ** r["rank"]:
                raise SystemExit(f"{r['N']}{r['class']}: root number check failed")
            an = [int(x) for x in pari.ellan(E, r["N"])]
            ap = [(p, an[p - 1]) for p in primes_upto(r["N"]) if r["N"] % p]
            out.write(json.dumps({"N": r["N"], "class": r["class"], "rank": r["rank"], "w": w,
                                  "bad": r["bad"], "ap": ap}, separators=(",", ":")) + "\n")
            n += 1
            checked += 1
    return {"classes": n, "root_number_checks_passed": checked}


def read_k() -> list[dict]:
    rows, seen = [], set()
    for line in open(RAW_K, encoding="utf-8"):
        if not line.startswith('"'):
            continue
        f = line.rstrip("\n").split("\t")
        label, klass = json.loads(f[0]), json.loads(f[1])
        if klass in seen:
            continue                      # one curve per isogeny class (a_P is an isogeny invariant)
        seen.add(klass)
        rank = f[5].strip()
        rows.append({"label": label, "class": klass, "norm": int(f[4]),
                     "rank": int(rank) if rank.isdigit() else None, "ai": json.loads(f[9])})
    return rows


def build_murm_k(pari, path: Path) -> dict:
    nf = pari("nfinit(y^2-y-1)")
    rows = read_k()
    max_norm = max(r["norm"] for r in rows)
    degree_one: dict[int, list] = {}
    for p in primes_upto(max_norm):
        degree_one[p] = [pr for pr in pari.idealprimedec(nf, p) if int(pr[3]) == 1]
    n = rank_checked = semistable_n = 0
    with gzip.open(path, "wt", encoding="ascii", compresslevel=9) as out:
        for r in rows:
            coeffs = pari([pari(f"{a}+{b}*y") for a, b in r["ai"]])
            E = pari.ellinit(coeffs, nf)
            red = pari.ellglobalred(E)
            cond = red[0]
            if int(pari.idealnorm(nf, cond)) != r["norm"]:
                raise SystemExit(f"{r['label']}: conductor norm disagrees with the LMFDB")
            fa = pari.idealfactor(nf, cond)
            bad = []
            semistable = True
            prod = 1
            for i in range(int(fa.matsize()[0])):
                pr, e = fa[i, 0], int(fa[i, 1])
                a_bad = int(pari.ellap(E, pr))      # 1 split, -1 non-split multiplicative, 0 additive
                if (e == 1) != (a_bad in (1, -1)) or (e > 1 and a_bad != 0):
                    raise SystemExit(f"{r['label']}: reduction type and a_P at a bad prime disagree")
                if e == 1:
                    prod *= -a_bad                  # local root number at a multiplicative prime
                else:
                    semistable = False              # additive: local sign not computed here
                bad.append((int(pari.idealnorm(nf, pr)), e, a_bad))
            w = int(pari.ellrootno(E))
            finite_sign = prod if semistable else None
            if semistable:
                semistable_n += 1
                if w != prod:              # two real places, each contributing -1, so w = +product
                    raise SystemExit(f"{r['label']}: w != product of finite local signs")
            if r["rank"] is not None:
                if w != (-1) ** r["rank"]:
                    raise SystemExit(f"{r['label']}: root number disagrees with rank parity")
                rank_checked += 1
            ap = []
            for p in primes_upto(r["norm"]):
                for pr in degree_one[p]:
                    if int(pari.idealval(nf, cond, pr)) == 0:
                        ap.append((p, int(pari.ellap(E, pr))))
            out.write(json.dumps({"label": r["label"], "class": r["class"], "norm": r["norm"],
                                  "rank": r["rank"], "w": w, "finite_sign": finite_sign,
                                  "bad": bad, "ap": ap},
                                 separators=(",", ":")) + "\n")
            n += 1
    return {"classes": n, "rank_parity_checks_passed": rank_checked,
            "semistable_classes": semistable_n, "semistable_sign_checks_passed": semistable_n}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ecdata", help="existing ecdata clone at the pinned commit (curves/ and aplist/)")
    args = parser.parse_args()
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(2 * 10 ** 9)
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        if args.ecdata:
            ecdata = Path(args.ecdata)
            head = subprocess.run(["git", "-C", str(ecdata), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            if head != ECDATA_COMMIT:
                raise SystemExit(f"{ecdata} is at {head[:12]}, expected {ECDATA_COMMIT[:12]}")
        else:
            print("Cloning Cremona's ecdata (about 300 MB) ...", flush=True)
            ecdata = clone_ecdata(Path(tmp) / "ecdata")
        print("Reading the tables over Q ...", flush=True)
        rows = read_q(ecdata)
    rank_counts = write_rank_signs(rows, DATA / "rank_signs.tsv.gz")
    print(f"rank_signs: {rank_counts}", flush=True)
    print("Computing a_p over Q for N < 5,000 with PARI ...", flush=True)
    q_info = build_murm_q(rows, pari, DATA / "murm_q.jsonl.gz")
    print(f"murm_q: {q_info}", flush=True)
    print("Computing a_P over Q(sqrt 5) with PARI ...", flush=True)
    k_info = build_murm_k(pari, DATA / "murm_k.jsonl.gz")
    print(f"murm_k: {k_info}", flush=True)
    outputs = ["rank_signs.tsv.gz", "murm_q.jsonl.gz", "murm_k.jsonl.gz"]
    manifest = {
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {
            "ecdata": {"repo": ECDATA_REPO, "commit": ECDATA_COMMIT,
                       "note": "J. E. Cremona, elliptic curve data over Q, conductors below 500,000"},
            "lmfdb_q_sqrt5": {"file": "raw/lmfdb_ec_nf_2.2.5.1_20261008.txt", "sha256": sha256(RAW_K),
                              "note": "LMFDB elliptic curves over 2.2.5.1, downloaded 2026-10-08 "
                                      "(query field_label = 2.2.5.1, 9721 curves)"},
            "pari": str(pari.version()),
        },
        "counts": {"q_classes_below_500000": len(rows), "rank_signs": rank_counts,
                   "murm_q": q_info, "murm_k": k_info},
        "sha256": {name: sha256(DATA / name) for name in outputs},
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
