The report is written. I'm reading the full file and spot-checking the provenance claims the Scribe drew from snapshot.json.The provenance checks out. Reading the full report.# Artemis solar lab: which earth-abundant crystals to compute next for excellent solar absorbers

*Report by the Scribe, written from the lab's files: `lab/solar/program.md`, `lab/solar/harness.py`, `lab/solar/data/snapshot.json`, `runs/solar/ledger.tsv`, `runs/solar/final_test.json`, `runs/solar/shortlist.csv`, `runs/solar/compiler_notes.md`, `runs/solar/crosschecks/*.json`, `runs/solar/scout_brief.md`, `lab/solar/experiment.py`, `lab/solar/trials/mbj_corrected_gap.py`, and the git log. Every number below is copied from those files.*

## 1. Summary

The lab asked which earth-abundant, non-toxic inorganic crystals in NIST JARVIS-DFT should be computed next to find excellent solar absorbers as quickly as possible, and what the best search strategy teaches about good absorbers. Here "excellent" means a spectroscopic limited maximum efficiency (SLME) of at least 30 percent together with an energy above the convex hull of at most 0.1 eV/atom.

The best ordering puts near-stable materials first. Within that group it ranks candidates by SLME predicted from cheap DFT data and composition, using an ExtraTrees regressor. On the held-out test pool (429 materials, 4 hits) it found all four hits within its first 8 picks. A random order is expected to need 344.0 picks, so the acceleration is 43.0. The stability-gated Shockley-Queisser rule needed 20 picks (17.2) and the plain Shockley-Queisser rule needed 199 (1.729). With only four test hits this number is coarse, and the honest summary is "clearly better than the best simple rule, and far better than random".

The search teaches four things. Stability is the first filter. The useful OptB88vdW gap window is centred near 0.7 eV, not at the Shockley-Queisser 1.34 eV, because that functional underestimates gaps, and the window shifts with the anion. Regressing the continuous SLME works better than classifying hits. Composition carries information beyond the gap.

For what to compute next, the model's top 15 never-assessed candidates are listed in Section 6. Three of them (SmS, DyS, LaS) have a JARVIS gap of exactly 0.0 eV and are probably false positives. The Materials Project cross-check could not be run.

| Test pool (429 materials, 4 hits) | Evaluations to find all 4 hits | Acceleration | Average precision |
|---|---|---|---|
| Final model (ExtraTrees SLME regressor + stability gate) | 8 | **43.0** | 0.8125 |
| Shockley-Queisser gap rule + stability gate | 20 | 17.2 | 0.575 |
| Shockley-Queisser gap rule alone | 199 | 1.729 | 0.0333 |
| Random order (expected) | 344.0 | 1.0 | n/a |

## 2. Data and definitions

**Data.** The data come from the official JARVIS-Leaderboard SLME benchmark split (Choudhary et al., npj Computational Materials 10, 93 (2024); github.com/usnistgov/jarvis_leaderboard at commit `57afc55f94c8a6f4562f73a3173968cd4b2f83b1`). Each material is joined to the JARVIS-DFT 3D release of 2021-08-18 (Choudhary et al., npj Computational Materials 6, 173 (2020); figshare doi:10.6084/m9.figshare.6815699). SLME itself is the quantity JARVIS computes from TBmBJ optical spectra (Choudhary et al., Chem. Mater. 31, 5900 (2019)).

The frozen snapshot holds 55716 rows: 7250 train, 905 val, 906 test and 46655 unlabeled. The build checks in `snapshot.json` report the following. No benchmark material is missing from the release. No SLME value differs from the release by more than 0.01. One material (JVASP-96735) was listed in two splits and kept in the earlier one. Among labeled materials, 608 lack a TBmBJ gap and 14 lack an energy above hull. A missing hull energy counts as unstable.

The experiment sees only cheap columns: OptB88vdW band gap, formation energy, energy above hull, composition, space group, crystal system, density, volume per atom and atom count. SLME and the TBmBJ gap are hidden for the search pools. They are visible only in train.

**Fingerprints** (SHA-256, from `harness.py fingerprint`, repeated in `final_test.json`):

| Item | SHA-256 |
|---|---|
| harness (`lab/solar/harness.py`) | `2b69a2b905b2ff838f8e83a841e4063a32cbf4dce6c6f062623af73f41bc39b4` |
| snapshot (`solar_snapshot.csv.gz`) | `619cccd405318aae86f25b347f025ffbeadf8f8e237f9f03f06949007625c1bc` |
| abundance table (`crustal_abundance_crc97.csv`) | `f2a1800c2ff394353e9e17613f8e017b329c6dbb6d141e33b2bca7778ac6358a` |

Every ledger row carries the harness and snapshot prefixes `2b69a2b905b2` and `619cccd40531`, so all trials ran on the same harness and data.

**Earth-abundance and toxicity rule.** A material enters a search pool only if every element in it has a crustal abundance of at least 1 mg/kg. The abundances come from the CRC Handbook of Chemistry and Physics, 97th edition (2016-2017), section 14, page 17, "Abundance of Elements in the Earth's Crust and in the Sea". They were transcribed from the CRC column of the Wikipedia page cited in Section 8. The material must also contain none of Cd, Hg, Pb, Tl or As, and no radioactive element. After this filter the val pool has 465 materials, the test pool 429 and the unlabeled pool 22790 rows. The train split (7250 rows, 158 hits) is not filtered and keeps all elements.

**Pre-registered definitions** (fixed 2026-10-03, before any ranking method was tuned):

- *Hit:* SLME ≥ 30.0 % and energy above hull ≤ 0.1 eV/atom.
- *Primary metric, acceleration:* the expected number of evaluations a random order needs to find N hits, divided by the number this ordering needed. N is 10, or every hit in the pool if there are fewer. The harness computes the random expectation as N·(pool size + 1)/(pool hits + 1). The val pool has 9 hits and the test pool 4, so N was 9 and 4.
- *Also reported:* hits in the top 25, enrichment in the top 25, and average precision. These help interpret a result, but keep-or-discard decisions used acceleration only.

**Baselines** (defined in the harness): *random*; *sq_gap*, which orders by distance of the OptB88vdW gap from the Shockley-Queisser optimum of 1.34 eV; and *sq_gap_stable*, the same with near-stable materials (ehull ≤ 0.1) placed first.

| Val pool (465 materials, 9 hits) | Evaluations to 9 hits | Acceleration | Hits in top 25 | Average precision |
|---|---|---|---|---|
| random | 419.4 | 1.0 | n/a | n/a |
| sq_gap | 244 | 1.719 | 2 | 0.0734 |
| sq_gap_stable | 39 | 10.754 | 7 | 0.4757 |

## 3. What the lab tried

The lab used 26 of its 60 allowed val evaluations, counting the Skeptic's confirmation re-runs. It stopped under the program's rule after three consecutive waves (5, 6 and 7) produced no kept improvement. The table lists each distinct trial once, in ledger order. Re-runs reproduced the same numbers and are left out. Each kept trial was approved by the Skeptic and committed to git.

| # | Trial | Hypothesis (ledger note, shortened) | Evals to 9 hits | Val acceleration | Val AP | Kept? |
|---|---|---|---|---|---|---|
| 0 | starting `experiment.py` | Shockley-Queisser gap rule (same as sq_gap) | 244 | 1.719 | 0.0734 | starting point |
| 1 | mbj_corrected_gap | stability gate + rank by distance of linearly corrected gap from the median TBmBJ gap of train hits | 21 | 19.971 | 0.713 | **kept** (bfcfb8b) |
| 2 | gbm_hit_classifier | stability gate + gradient-boosted hit classifier on cheap + composition features | 18 | 23.3 | 0.8838 | **kept** (bc69480) |
| 3 | gbm_mbj_window | stability gate + gradient-boosted TBmBJ-gap prediction, rank by distance to hit median | 22 | 19.064 | 0.4554 | no |
| 4 | slme_regressor | stability gate + gradient-boosted SLME regressor instead of hit classifier | 15 | 27.96 | 0.838 | **kept** (0354ac3) |
| 5 | ea_weighted_classifier | hit classifier with ×3 weight on train rows made only of pool elements | 18 | 23.3 | 0.7968 | no (tie) |
| 6 | minimal_features | simplification: hit classifier on 8 features | 33 | 12.709 | 0.893 | no |
| 7 | mbj_gap_feature | out-of-fold predicted TBmBJ gap as an extra regressor feature | 14 | 29.957 | 0.7715 | no |
| 8 | reg_clf_rank_average | average of regressor rank and classifier rank | 13 | 32.262 | 0.8725 | no (Skeptic rejected) |
| 9 | drop_ehull_feature | simplification: ehull used only as the gate | 15 | 27.96 | 0.8 | no (tie) |
| 10 | extra_trees_regressor | ExtraTrees (500 trees, leaf 2) instead of gradient boosting | 16 | 26.212 | 0.8109 | no |
| 11 | knn_analogue | SLME of the 10 nearest train materials | 14 | 29.957 | 0.8123 | no (Skeptic rejected) |
| 12 | extra_trees_elemfrac | ExtraTrees SLME regressor + element-fraction vector | 13 | **32.262** | 0.899 | **kept** (01352a9), final model |
| 13 | stable_train_only | train the regressor only on rows with ehull ≤ 0.2 | 13 | 32.262 | 0.9355 | no (tie) |
| 14 | drop_structural_columns | simplification: drop structural columns | 14 | 29.957 | 0.8878 | no |
| 15 | threshold_weighting | ×3 weight on train rows with SLME 20-40 | 13 | 32.262 | 0.9149 | no (tie) |
| 16 | stable_plus_threshold | combine trials 13 and 15 | 12 | 34.95 | 0.928 | no (Skeptic rejected as val overfitting) |
| 17 | optimistic_ucb | mean + 0.5·std of tree predictions | 13 | 32.262 | 0.9288 | no (tie) |
| 18 | magpie_lite_features | add 28 Magpie-style composition statistics | 14 | 29.957 | 0.9161 | no |
| 19 | anion_gap_window | add gap minus the anion class's train-hit median gap | 14 | 29.957 | 0.8935 | no |

Two things should be clear before reading the table as a leaderboard. First, the val pool has only 9 hits, and acceleration is set by the position of the ninth one. Moving that hit by one place changes the score in large steps: 13 evaluations give 32.262, 14 give 29.957 and 12 give 34.95. Second, the **highest val number in the ledger, 34.95, belongs to a rejected trial**. stable_plus_threshold combined two trials that had each only tied the current model. In the Skeptic's train cross-validation it did worse than the kept model (mean acceleration 63.6 against 72.3, AP 0.656 against 0.682), so it was judged to be fitted to the val pool. The best kept val score is 32.262. For the same reason, the regressor-classifier rank average reached 32.262 but was rejected: it tied in train cross-validation (30.65 against 30.75) and doubled the number of models.

The Skeptic's train cross-validation is a second check that does not depend on the 9 val hits. It supports each kept step, but as a moderate gain rather than a decisive one:

| Step | Skeptic's train-CV evidence (from `compiler_notes.md`) |
|---|---|
| corrected-gap target vs 1.34 eV target (both gated) | median acceleration 26.2 vs 16.5 on earth-abundant train halves (23 hits); 25.5 vs 5.2 on all-element train (158 hits); learned OptB88vdW target stayed in 0.68–0.77 eV over 20 random splits |
| hit classifier vs corrected-gap rule | won 18 of 25 folds; AP 0.607 vs 0.480 (a gain of about 15–25 %) |
| SLME regressor vs hit classifier | mean acceleration 47.8 vs 37.5; AP 0.611 vs 0.607; 13 wins, 7 losses |
| ExtraTrees + element fractions vs gradient-boosted regressor | acceleration 33.4 vs 30.3; AP 0.630 vs 0.592; element fractions added little over ExtraTrees alone |

These cross-validation figures come from separate analyses with different fold designs, so compare numbers only within a row. The Planner tested more than 40 variants on train, and none improved on the ExtraTrees model by more than fold noise.

**What was learned.** Stability does most of the early work. Adding the ehull ≤ 0.1 gate to the Shockley-Queisser rule raised val acceleration from 1.719 to 10.754, and on the test pool from 1.729 to 17.2. The second lesson is the gap scale. JARVIS's OptB88vdW gaps are systematically smaller than its TBmBJ gaps. A straight-line fit on 6029 train materials gives TBmBJ ≈ 1.2958 × OptB88vdW + 0.4057 eV. The median TBmBJ gap of train hits is 1.3455 eV, which this fit maps to an OptB88vdW gap of about 0.725 eV. Aiming at 0.725 eV instead of 1.34 eV nearly doubled val acceleration (10.754 to 19.971).

The train split shows the same picture directly. Every train hit with a known TBmBJ gap (138 of 158) lies between 0.92 and 1.66 eV, with a median of 1.35 eV. The median OptB88vdW gap of hits is only 0.66 eV. Among stable train materials, the hit rate is 49–53 % at OptB88vdW gaps of 0.3–0.8 eV, 14 % at 1.2–1.4 eV and under 2 % above 1.8 eV.

The window also depends on the anion. The median OptB88vdW gap of train hits is 0.992 eV for halides (53 hits), 0.260 eV for chalcogenides (28), 0.046 eV for oxides (5) and 0.6455 eV for the rest (72). An explicit anion-specific window feature (trial 19) did not improve the learned model. In train cross-validation, simple corrected-gap rules, whether global or per anion class, reached about half the learned model's acceleration (22.8 and 23.8 against 50.0). So the gap alone is not enough. About 12 % (19 of 152) of stable materials with zero OptB88vdW gap are still hits, and composition carries real signal. Regressing SLME beat classifying hits with both gradient boosting and ExtraTrees. One plausible reading, not tested separately, is that near-misses just below 30 % still show the model which direction is better.

Train hits cluster in alkali halides and fluorides (K, Rb and Na with F, Br and I) and in Sb, In, Ag, Cu and Zn compounds, and 62 of the 158 are cubic. The Scout's literature-based guess that chalcogenides dominate stable high-SLME materials had no source, and it does not hold on train.

## 4. The final method

The final ranking (`lab/solar/experiment.py`, sha12 `132b7bb5c349`, commit 01352a9) works in two steps. First, every candidate with an energy above hull of at most 0.1 eV/atom goes ahead of every candidate that is less stable or has no hull energy. Second, within each group, candidates are ordered by SLME predicted by a model trained on the 7250 labeled train materials.

The model is an ensemble of 500 randomized decision trees (scikit-learn's ExtraTreesRegressor, minimum 2 samples per leaf). Its inputs are only what an ordinary DFT relaxation and the formula provide:

- the OptB88vdW gap, formation energy per atom, energy above hull, number of elements, number of atoms, space-group number, density and volume per atom;
- the composition-weighted mean Pauling electronegativity and the electronegativity spread;
- the atomic fractions of chalcogens (S, Se, Te), heavier halides (Cl, Br, I) and oxygen;
- a vector giving the atomic fraction of each element that appears in train.

Missing values are set to −1. Ties are broken by JARVIS identifier.

Readers who want the method in one paragraph should use the simpler kept rule, `mbj_corrected_gap`, which keeps most of the physics. Put near-stable materials first. Then rank by how close the OptB88vdW gap, converted linearly to the TBmBJ scale, is to the typical TBmBJ gap of known excellent absorbers. In practice this means an OptB88vdW gap near 0.7 eV, not 1.34 eV. That rule scored 19.971 on val. The learned model scored 32.262 on val, and in train cross-validation roughly doubled the acceleration of rules of this kind.

## 5. Held-out result

The Compiler ran `harness.py final` once, at the end, on the test pool with the committed model (`final_test.json`, 2026-10-04T00:54:38Z). The baselines were scored on the same 429 materials.

| Test pool: 429 materials, 4 hits | Evaluations to find all 4 | Acceleration | Hits in top 25 | Enrichment in top 25 | Average precision |
|---|---|---|---|---|---|
| **Final model** | **8** | **43.0** | 4 | 17.16 | 0.8125 |
| sq_gap_stable | 20 | 17.2 | 4 | 17.16 | 0.575 |
| sq_gap | 199 | 1.729 | 1 | 4.29 | 0.0333 |
| random | 344.0 (simulated mean 344.99) | 1.0 | n/a | n/a | n/a |

The test result agrees in direction with val, where the model scored 32.262 against 10.754 for sq_gap_stable. It should be read with care. With four hits, acceleration depends on where a single material lands, and a shift of a few places would change 43.0 a lot. The stability-gated baseline also put all four hits in its top 25, so the model's advantage on test is in the order within the first 25, not in which materials made it there. Average precision (0.8125 against 0.575) points the same way.

## 6. Recommendations: what to compute next

`harness.py shortlist -n 15` retrained the final model on train plus val labels and ranked the 22790-row never-assessed earth-abundant unlabeled pool. One problem had to be worked around. The harness refused the committed `experiment.py` on this pool because the frozen pool repeats four identifiers: JVASP-100669 Ca2Mg ×2, JVASP-113961 Li2BN2 ×2, JVASP-116461 Zn3Mo3O8 ×3 and JVASP-97311 LiBS2O8 ×3. That leaves 22784 unique materials. The Compiler made `lab/solar/trials/final_dedup_for_shortlist.py` (sha12 `532b1eae515d`, commit 1f87e68), which differs from the final model only in removing repeated identifiers from its output. Its val ranking was checked and is identical to the final model's.

**Materials Project cross-check: unavailable.** `mp_lookup.py` returned "MP_API_KEY is not set in this environment; the Materials Project cross-check is unavailable." This report therefore has no Materials Project stability, gap or experimental-existence data for any candidate.

**Literature cross-check.** The Scout searched OpenAlex with `literature.py "<formula> band gap"`. The tool returns titles and DOIs, not property values, so this report quotes no values from those papers. A gap value for CuCl that the Scout mentioned did not appear in the tool output and is not used. Searches were run for 10 of the 14 distinct formulas. Na10SrSn12, Sr2Ge, DyS and LaS were not searched, so for them the literature cross-check is missing.

The shortlist file does not record predicted SLME values, so none are given. The gap, formation energy and hull energy below are JARVIS OptB88vdW values from `shortlist.csv`.

| Rank | JARVIS ID | Formula | Space group | OptB88vdW gap (eV) | Formation energy (eV/atom) | E above hull (eV/atom) | Literature (OpenAlex) | Materials Project |
|---|---|---|---|---|---|---|---|---|
| 1 | JVASP-90503 | Rb2NiF6 | Fm-3m (cubic) | 1.606 | −2.36246 | 0.0 | one first-principles study (pssb 2022) | unavailable |
| 2 | JVASP-120881 | SrBeBr2 | Fm-3m (cubic) | 1.039 | −0.84604 | 0.064185 | no results | unavailable |
| 3 | JVASP-78443 | SmS | Fm-3m (cubic) | 0.0 | −2.17019 | 0.057804 | 1980s band-structure papers | unavailable |
| 4 | JVASP-111073 | CuCl | F-43m (cubic) | 0.586 | −0.44562 | 0.0 | described as wide-gap | unavailable |
| 5 | JVASP-14566 | DyS | Fm-3m (cubic) | 0.0 | −2.14212 | 0.032083 | not searched | unavailable |
| 6 | JVASP-114550 | BaZnCl2 | P4mm (tetragonal) | 1.107 | −1.56891 | 0.020275 | no results | unavailable |
| 7 | JVASP-12510 | CuCl | Pa-3 (cubic) | 0.59 | −0.42305 | 0.011285 | as rank 4 | unavailable |
| 8 | JVASP-59094 | Na10CaSn12 | I-43m (cubic) | 0.775 | −0.31712 | 0.0 | no results | unavailable |
| 9 | JVASP-59095 | Na10SrSn12 | I-43m (cubic) | 0.776 | −0.32036 | 0.0 | not searched | unavailable |
| 10 | JVASP-10972 | SrCaGe | Pnma (orthorhombic) | 0.471 | −0.71249 | 0.0 | only unrelated results | unavailable |
| 11 | JVASP-9128 | Sr2Ge | Pnma (orthorhombic) | 0.388 | −0.63223 | 0.0 | not searched | unavailable |
| 12 | JVASP-12504 | CuBr | Pa-3 (cubic) | 0.317 | −0.24627 | 0.013285 | gap and band-structure papers | unavailable |
| 13 | JVASP-100007 | Cu2BrCl | R-3m (trigonal) | 0.423 | −0.22102 | 0.0 | no results | unavailable |
| 14 | JVASP-115581 | BaZnF2 | P4mm (tetragonal) | 1.347 | −2.49285 | 0.0 | no results | unavailable |
| 15 | JVASP-98069 | LaS | Cmce (orthorhombic) | 0.0 | −2.36006 | 0.082082 | not searched | unavailable |

**How to use this list.** Twelve of the 15 candidates are near-stable and have a non-zero OptB88vdW gap: Rb2NiF6, SrBeBr2, both CuCl entries, BaZnCl2, Na10CaSn12, Na10SrSn12, SrCaGe, Sr2Ge, CuBr, Cu2BrCl and BaZnF2. These are the natural first TBmBJ/SLME calculations. Ten of these twelve have OptB88vdW gaps between 0.317 and 1.107 eV. That range overlaps the 0.3–0.8 eV band where stable train materials were most often hits. Notes on individual candidates follow.

- **Rb2NiF6** (rank 1) is on the hull in JARVIS. Its 1.606 eV OptB88vdW gap is well above the 0.7 eV window, so the model is relying on composition: alkali fluorides are common among train hits. The literature search found one first-principles study of Rb2MF6 crystals (M = Si, Ni, Pd) under pressure (pssb 2022). It found no experimental or photovoltaic work, and the tool output gives no values to compare.
- **SrBeBr2, BaZnCl2, BaZnF2, Na10CaSn12 and Cu2BrCl** returned no literature at all, and no Materials Project data exist here. JARVIS is the only source for them. They are untested predictions, and checking whether they exist experimentally is an open first step. The same holds for **Na10SrSn12** and **Sr2Ge**, which were not searched, and for **SrCaGe**, whose search returned only unrelated compounds.
- **CuCl** (ranks 4 and 7, two polymorphs) is a real disagreement. JARVIS gives OptB88vdW gaps of 0.586 and 0.59 eV. The literature includes a paper on "Band gap energy and binding energies of Z3-excitons in CuCl" (Solid State Commun. 1995) and describes γ-CuCl as a wide-band-gap material (J. Cryst. Growth 2005). The lab's files do not say which JARVIS entry corresponds to γ-CuCl. The likely explanation is the GGA-type underestimate described in Section 3, but if the true gap is wide, CuCl would absorb little of the solar spectrum and would be a poor absorber despite its rank. Its TBmBJ gap and SLME, the calculations this list exists to prioritise, will settle the question. **CuBr** (rank 12) has an experimental and theoretical literature on its gap and band structure (J. Appl. Phys. 2004; Phys. Rev. B 1976; a 2005 data compilation on γ-CuBr), but the tool output gives no values, so agreement with JARVIS's 0.317 eV cannot be judged here.
- **SmS, DyS and LaS** (ranks 3, 5 and 15) have an OptB88vdW gap of exactly 0.0 eV: they are metallic at this level of theory. The model probably ranks them high because of rock-salt chalcogenide analogues in train. 19 of 152 stable zero-gap train materials are hits, so this is not impossible, but these three are the likeliest false positives on the list and should be computed last, if at all. For SmS, the literature consists of 1980s band-structure papers on its Coulomb gap and its f-d hybridisation gap (J. Phys. C 1983 and 1986). The titles suggest an electronic structure more subtle than a simple band gap. They give no values, but they are one more reason for caution. DyS and LaS were not searched.

## 7. Limits

- **Small pools.** The val pool has 9 hits and the test pool 4. Acceleration moves in coarse steps, the gaps between kept trials are a few val positions, and the test figure of 43.0 depends on four materials. The kept steps are supported by train cross-validation, but by moderate gains, not decisive ones.
- **Val overfitting risk.** Each trial was chosen after seeing val scores. The highest val score (34.95) came from a rejected combination of two ties, which shows how easily the val pool can be overfit. The single test evaluation guards against this, but with only four hits it guards weakly.
- **DFT-level labels.** Hits are defined by JARVIS's TBmBJ-based SLME and OptB88vdW hull energies, not by measurement. The OptB88vdW-to-TBmBJ gap correction found here is an empirical fit within JARVIS, and the literature brief gave no source for its size.
- **SLME is a proxy.** It is a theoretical efficiency limit computed from the absorption spectrum. It does not capture defects, carrier transport, band alignment, dopability or interface losses, which decide real device efficiency. The Scout's brief notes such losses for known earth-abundant absorbers, such as voltage loss in kesterites and defect-rich interfaces in FeS2.
- **No synthesis or device data.** Nothing in this study tells whether a shortlisted compound can be made, is stable in air or moisture, or has ever been made into a device. Several shortlisted compounds returned no literature at all.
- **Missing cross-checks.** The Materials Project lookup failed for lack of an API key, so no independent stability or gap data were obtained. Literature searches returned titles only, and four shortlisted formulas were not searched.
- **Pool definition.** The toxicity screen excludes only Cd, Hg, Pb, Tl, As and radioactive elements, and the abundance cutoff is 1 mg/kg. Readers with stricter hazard or supply criteria should re-screen the shortlist themselves. The train split is not filtered, so the model also learns from compounds outside the earth-abundant set. A trial that up-weighted earth-abundant train rows (ea_weighted_classifier) only tied.
- **Data quirks.** 608 labeled materials lack a TBmBJ gap. The unlabeled pool contains four repeated identifiers, which required the de-duplicated shortlist copy described in Section 6. One material appears in two benchmark splits and was kept in the earlier one.
- **Skeptic's caveats on the final model.** Element fractions add little over ExtraTrees alone in train cross-validation. With seed 3 the model needs 14 val evaluations instead of 13 (29.957 instead of 32.262).

## 8. Sources

**Data and definitions**
- K. Choudhary et al., JARVIS-Leaderboard, npj Computational Materials 10, 93 (2024). Benchmark files from https://github.com/usnistgov/jarvis_leaderboard at commit `57afc55f94c8a6f4562f73a3173968cd4b2f83b1` (for example https://raw.githubusercontent.com/usnistgov/jarvis_leaderboard/57afc55f94c8a6f4562f73a3173968cd4b2f83b1/jarvis_leaderboard/benchmarks/AI/SinglePropertyPrediction/dft_3d_slme.json.zip).
- K. Choudhary et al., JARVIS, npj Computational Materials 6, 173 (2020), https://doi.org/10.1038/s41524-020-00440-1. JARVIS-DFT 3D release 2021-08-18, figshare doi:10.6084/m9.figshare.6815699 (https://ndownloader.figshare.com/files/29204826).
- K. Choudhary et al., SLME in JARVIS-DFT, Chem. Mater. 31, 5900 (2019). No link is recorded in the lab's files.
- CRC Handbook of Chemistry and Physics, 97th edition (2016-2017), section 14, p. 17, "Abundance of Elements in the Earth's Crust and in the Sea". Transcribed from the CRC column of https://en.wikipedia.org/wiki/Abundance_of_elements_in_Earth%27s_crust.
- Materials Project: A. Jain et al., APL Materials 1, 011002 (2013), https://materialsproject.org. Queried but unavailable in this run.

**Literature found by the Scout's tool (OpenAlex) for shortlisted compounds**
- Rb2NiF6: "First-Principles Calculations of Pressure Effects on the Structural, Electronic, Elastic, and Thermodynamic Properties of Rb2MF6 (M = Si, Ni, Pd) Crystals", physica status solidi (b) (2022), https://doi.org/10.1002/pssb.202100607
- SmS: "The role of the Coulomb gap in the self-consistent band structure of SmS", J. Phys. C (1986), https://doi.org/10.1088/0022-3719/19/14/015
- SmS: "The f-d hybridisation gap in golden SmS", J. Phys. C (1986), https://doi.org/10.1088/0022-3719/19/31/003
- SmS: "KKR relativistic electronic structure for SMS", J. Phys. C (1983), https://doi.org/10.1088/0022-3719/16/5/015
- CuCl: "Band gap energy and binding energies of Z3-excitions in CuCl", Solid State Communications (1995), https://doi.org/10.1016/0038-1098(95)00007-0
- CuCl: "Encapsulation of the heteroepitaxial growth of wide band gap γ-CuCl on silicon substrates", Journal of Crystal Growth (2005), https://doi.org/10.1016/j.jcrysgro.2005.10.053
- CuCl, CuBr: "Photonic band gaps in highly ionic medium: CuCl, CuBr, CuI", Infrared Physics & Technology (2002), https://doi.org/10.1016/s1350-4495(02)00162-7
- CuBr: "Effective mass approximation for two extreme semiconductors: Band gap of PbS and CuBr nanoparticles", Journal of Applied Physics (2004), https://doi.org/10.1063/1.1691184
- CuBr: "Cuprous bromide (gamma-CuBr) band structure, energy gaps" (2005), https://doi.org/10.1007/10681719_38
- CuBr: "Temperature-dependent photoemission studies of the electronic states of CuBr", Physical Review B (1976), https://doi.org/10.1103/physrevb.14.4551

**Background from the Scout's brief (cited only where used above)**
- Kesterite voltage losses and CuSbS2/CuSbSe2 back-surface-field layers: Prog. Photovolt. (2023), https://doi.org/10.1002/pip.3743
- FeS2 and SnS absorbers: Front. Chem. (2019), https://doi.org/10.3389/fchem.2019.00297

**Lab records**
- Ledger `runs/solar/ledger.tsv`; final result `runs/solar/final_test.json`; shortlist `runs/solar/shortlist.csv`; raw cross-check output `runs/solar/crosschecks/`; Compiler's notes `runs/solar/compiler_notes.md`.
- Git commits: bfcfb8b, bc69480, 0354ac3, 01352a9 (kept models); 9ce26d9 (discarded trials of waves 5–7, kept for the record); 1f87e68 (de-duplicated shortlist copy); 99db481 (frozen data snapshot).

---

**Final ledger summary**

- **Best kept val acceleration:** 32.262 from extra_trees_elemfrac, which needed 13 evaluations to find all 9 val hits (AP 0.899, commit 01352a9). The highest val number in the ledger, 34.95 from stable_plus_threshold, belongs to a trial the Skeptic rejected as overfitting the val pool. 26 of the 60 allowed val evaluations were used. The loop stopped because waves 5, 6 and 7 brought no kept improvement.
- **Final test acceleration:** 43.0. The final model found all 4 test hits in 8 evaluations, against 344.0 expected for random. Hits in top 25: 4; enrichment in top 25: 17.16; AP 0.8125.
- **Baselines on test (429 materials, 4 hits):**

| Baseline | Acceleration | Evaluations to find all 4 hits | Other |
|---|---|---|---|
| random | 1.0 | 344.0 | simulated mean 344.99 |
| sq_gap | 1.729 | 199 | AP 0.0333 |
| sq_gap_stable | 17.2 | 20 | 4 hits in top 25, AP 0.575 |
