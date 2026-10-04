"""Post-hoc robustness check (Claude, 2026-10-03), run after the lab's single final test.

The official test pool held only 4 hits. This repeats the comparison over 20
random halvings of every earth-abundant labeled material (train, val and test
pooled): one half is the search pool, everything else trains the model. It
scores the stability-gated Shockley-Queisser rule, the corrected-gap rule and
the rebuilt final model. Run from the repository root:

    python lab/solar/analysis/robustness.py docs/results/phase2_robustness.csv
"""
import sys, importlib.util, json
import numpy as np, pandas as pd
sys.path.insert(0, "lab/solar"); import harness as H
spec = importlib.util.spec_from_file_location("rb", "lab/solar/trials/extra_trees_elemfrac_rebuilt.py")
rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)

f = H.load_snapshot(); ab = H.load_abundance()
lab = f[f.split.isin(["train", "val", "test"])].drop(columns=["split"]).reset_index(drop=True)
ea = H.pool_mask(lab, ab).to_numpy()
hit = H.hit_mask(lab, lab["ehull"]).to_numpy()
print("labeled", len(lab), "earth-abundant", ea.sum(), "EA hits", (ea & hit).sum())

def corrected_gap_rank(train, cand):
    m = train.dropna(subset=["mbj_bandgap", "optb88vdw_bandgap"])
    m = m[(m.optb88vdw_bandgap > 0) & (m.mbj_bandgap > 0)]
    a, b = np.polyfit(m.optb88vdw_bandgap, m.mbj_bandgap, 1)
    th = H.hit_mask(train, train["ehull"])
    target = train[th]["mbj_bandgap"].median()
    d = (a * pd.to_numeric(cand.optb88vdw_bandgap, errors="coerce") + b - target).abs().fillna(np.inf)
    u = (~(pd.to_numeric(cand.ehull, errors="coerce") <= 0.1)).astype(int)
    return cand.assign(_u=u, _d=d).sort_values(["_u", "_d", "jid"], kind="mergesort").jid.tolist()

rows = []
ea_idx = np.flatnonzero(ea)
for seed in range(20):
    rng = np.random.default_rng(100 + seed)
    pool_idx = rng.choice(ea_idx, size=len(ea_idx) // 2, replace=False)
    in_pool = np.zeros(len(lab), bool); in_pool[pool_idx] = True
    train = lab[~in_pool].reset_index(drop=True)
    pool = lab[in_pool].sample(frac=1, random_state=seed).reset_index(drop=True)
    cand = pool[H.VISIBLE_COLUMNS]
    hidden = pool[["jid", "slme", "mbj_bandgap"]].copy()
    hidden["hit"] = H.hit_mask(hidden, pool["ehull"]).to_numpy(); hidden = hidden.set_index("jid")
    res = {"seed": seed, "pool": len(pool), "hits": int(hidden.hit.sum())}
    for name, ranking in (("sq_gap_stable", H.rank_sq_gap_stable(cand)),
                          ("corrected_gap", corrected_gap_rank(train, cand)),
                          ("model", rb.rank(train, cand, seed=0))):
        s = H.score_ranking(ranking, hidden)
        res[name + "_evals"] = s["evals_to_target"]; res[name + "_acc"] = s["acceleration"]; res[name + "_ap"] = s["average_precision"]
    res["target"] = s["target_hits"]
    rows.append(res); print(res, flush=True)
df = pd.DataFrame(rows)
df.to_csv(sys.argv[1], index=False)
r = df.sq_gap_stable_evals / df.model_evals
print("\nmedian accel  random=1  sq_gap_stable=%.1f  corrected_gap=%.1f  model=%.1f" % (df.sq_gap_stable_acc.median(), df.corrected_gap_acc.median(), df.model_acc.median()))
print("median AP     sq_gap_stable=%.3f  corrected_gap=%.3f  model=%.3f" % (df.sq_gap_stable_ap.median(), df.corrected_gap_ap.median(), df.model_ap.median()))
print("model fewer evals than sq_gap_stable in %d of %d splits; ties %d" % ((df.model_evals < df.sq_gap_stable_evals).sum(), len(df), (df.model_evals == df.sq_gap_stable_evals).sum()))
print("ratio sq_gap_stable/model evals: median %.2f, 10th pct %.2f, 90th pct %.2f" % (r.median(), r.quantile(.1), r.quantile(.9)))
