0% for d = 3 and 10 | free probing |
| val | 64 | the same design with n = 50 and 200 (60 regimes), plus noise at 5% and 20% for d = 3 and 10 (4 regimes); one dataset per regime | budgeted evaluations |
| test (sealed) | 90 synthetic + 5 real | 45 regimes the paper never ran, two datasets each: d = 4, 7, 15; n = 30, 300, 700; 2, 4 or 6 clusters; noise 0, 10 or 30%; uniform or Gaussian; new centres placed by a random walk at 0.85 to 1.15 times the paper's spacing. Five real datasets the paper did not use: aggregation, compound, jain, glass, yeast | run once by the humans |

The test datasets are drawn from a secret seed whose SHA-256 is `2287521b8b33edcf30eaf5fa0e67f7eaa8921f1e0f645196dc02cb218420d619`. They were never in the repository or the sandbox.

**The alpha grid.** A rule may choose one of 15 values, and any alpha it returns is snapped to the nearest of them in log scale: 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 8, 10, 15, 20 and 30 percent (`nulls.CHOICES`). The null tables store 23 levels from 0.1 to 40 percent (`data/manifest.json`, 10,000 Monte Carlo iterations each). The direction is "ascend" by default, or "descend". At dimensions the paper does not list, its schedule is interpolated log-linearly in d and snapped: d = 4 gives 8%, d = 7 gives 3%, d = 15 gives 0.3%, with the descending search for d of 10 and above.

**The port.** The harness clusters with `unccd.py`, a line-by-line Python port of the authors' R code. `data/port_validation.json` records 60 validation cases: 48 simulated and 12 real, 49 ascending and 11 descending. All 60 have labels, radii and intrinsic dimensions identical to the R output, with a largest silhouette difference of 2.2 × 10⁻¹⁶. (program.md says "51 validation cases"; the file itself records 60.)

**The metric.** For each dataset the harness clusters with the chosen settings and computes the adjusted Rand index between the clusters and the true labels, leaving out noise points. A regime's score is the mean ARI of its datasets, and a split's score is the mean over regimes. The 95% interval comes from a bootstrap over regimes (2,000 draws, seed 0). Comparisons between two rules are paired by regime.

**The keep rule.** A trial becomes a candidate only if its val mean ARI beats the current best by at least 0.005 and the lower end of the paired 95% interval is above 0. The Skeptic then reads the code and checks that it uses nothing about the datasets beyond X. It probes the trial on dev and, for a randomised rule, runs `recheck` on seeds 1 and 2, where the gain must hold. The formula has the same keep rule against the current formula. A formula may use only n and d, `math`, and at most three numeric constants.

**Pre-registered hypotheses** (test synthetic regimes, decided once by the humans):

- **H1.** The promoted experiment matches the paper's schedule: the lower end of the paired 95% interval of (experiment − schedule) is above −0.02.
- **H2.** The formula matches the promoted experiment: the lower end of the paired 95% interval of (formula − experiment) is above −0.02.

The humans will also report, without a pass mark, every rule's mean ARI on the five real datasets. They will report the experiment's differences from the fixed 1 percent, from the silhouette maximum and from the label-using ceiling.

**Fingerprint** (`frozen.json`):

| Item | SHA-256 |
|---|---|
| experiment.py (= trials/null_calibrated_silhouette.py) | 2732632753171e1241ad913f3e020c541ec7b68ca74cb1f874bfbf9877a547fd |
| formula.py (= trials/inverse_n_d2_formula.py) | 1dbe3c146c87a5f622f925f8fe0caa517320063d5d25f3043bea2d22c98165c1 |
| data | 7f404af31412196d67bacdbf178e66db0fc4bc804623650194f1aefe12c52b90 |
| harness.py | c19d056bdfff39d6a770697e5eb2663fa4f98f1710a7208fe76b567f3f3206bd |
| runner.py | 9be6f26b261c94d49f7115da607b6581803a3dad3b713c021263b9b9b5461b5b |
| kit.py | 4bead9b6200881012bdf3db11f2ccff48918316efa9760f3afca5541f03fa78e |
| unccd.py | 6e7fd1ac8b333ac0110e8a0335ca8970d0be196835a90f5f2b4b9812406e6c91 |
| nulls.py | a55376cc332e3be20edb34ac31d6b75533996cdf26c6dc1d12de2b7ca696e480 |

The two files on disk hash to the frozen values. Every ledger row carries harness c19d056bdfff and data 7f404af31412.

## 3. Baselines on val and dev

These are the harness's baselines from the ledger, with the kept rules beside them. The two ceilings use the true labels, so no label-free rule can reach them in general. They show how much room a perfect rule would have.

| Rule | val mean ARI [95% CI] | dev mean ARI [95% CI] |
|---|---|---|
| Paper's schedule | 0.9056 [0.8622, 0.9443] | 0.9378 [0.8823, 0.9800] |
| Fixed 1 percent | 0.8230 [0.7573, 0.8823] | 0.8782 [0.7902, 0.9545] |
| Fixed 5 percent (starting formula) | 0.8598 [0.8035, 0.9064] | 0.8916 [0.8196, 0.9561] |
| Silhouette maximum (starting experiment) | 0.9414 [0.8989, 0.9748] | 0.9568 [0.9028, 0.9918] |
| Ceiling: best alpha, ascending (labels) | 0.9648 [0.9427, 0.9830] | 0.9817 [0.9625, 0.9962] |
| Ceiling: best alpha and direction (labels) | 0.9677 [0.9455, 0.9858] | 0.9840 [0.9647, 0.9980] |
| **Kept experiment** | **0.9602 [0.9349, 0.9810]** | 0.9757 [0.9548, 0.9918] (probe)¹ |
| **Kept formula** | **0.9125 [0.8674, 0.9492]** | missing² |

¹ Dev probes are not written to the ledger. This figure comes from `notes/stress/ub_results.md`, whose trial chose the same alpha as the experiment on all 32 dev datasets. `fw_results.md` also records the experiment's dev score as 0.9757.
² No dev score for the kept formula is recorded in the ledger or the notes.

On val, the experiment sits 0.0046 below the ascending ceiling. This gap was computed per dataset from the details files; it equals 0.9648 − 0.9602 to rounding. The gap is smaller than the keep bar of 0.005, so on val a further ascending-search improvement to the experiment could not, even in principle, be accepted. On val the experiment exceeds the schedule by 0.0546 and the formula exceeds it by 0.0068 (differences of the ledger means). The formula falls 0.0477 below the experiment. The ledger holds no paired intervals for these three comparisons, because the harness only pairs a trial with the current incumbent of its own kind.

## 4. What the lab tried

The lab ran 11 waves of trials. It spent 15 of its 40 val evaluations on experiments (the first being the starting rule), 10 of its 12 on formulas (the first being the starting formula) and 2 of its 16 rechecks. There were three keeps, commits 01e6357, d568f3a and 71f9a96, all in waves 1 to 4; waves 5 to 11 kept nothing. The program allows the loop to end after three waves without a keep once at least 25 evaluations have been run (here 15 + 10). Every evaluation is in `runs/unccd_alpha/ledger.tsv`, with its archived code in `details/`. In the tables, Δ is the paired difference from the incumbent of the time, with its 95% interval.

**Experiment trials (val)**

| # | Trial | Idea, one line | Mean ARI [95% CI] | Δ vs incumbent [95% CI] | Outcome |
|---|---|---|---|---|---|
| 0 | experiment.py (start) | largest UN-CCD silhouette, ascend | 0.9414 [0.8989, 0.9748] | — | starting point |
| 1 | calinski_harabasz_max | largest Calinski–Harabasz index instead of silhouette | 0.9412 [0.8989, 0.9748] | −0.0002 [−0.0005, 0.0000] | not kept |
| 2 | null_calibrated_silhouette | silhouette minus its expectation s0(k) on Gaussian reference data | 0.9602 [0.9349, 0.9810] | +0.0188 [+0.0026, +0.0396] | **kept** (recheck below) |
| 3 | calibrated_direction | same score, over both search directions | 0.9608 [0.9342, 0.9832] | +0.0006 [−0.0067, +0.0086] | not kept |
| 4 | zscore_reference | score divided by the null spread, 20 references | 0.9521 [0.9232, 0.9762] | −0.0081 [−0.0223, +0.0013] | not kept |
| 5 | stability_arbiter | subsample stability arbitrates among the top three candidates | 0.9427 [0.9145, 0.9667] | −0.0176 [−0.0374, −0.0014] | not kept (significantly worse) |
| 6 | small_alpha_descend | descend allowed only for alpha ≤ 1% | 0.9630 [0.9384, 0.9835] | +0.0028 [0.0000, +0.0083] | not kept (< 0.005) |
| 7 | single_reference | simplification: one deterministic reference, one k-means start | 0.9514 [0.9177, 0.9776] | −0.0088 [−0.0224, +0.0013] | not kept |
| 8 | same_alpha_descend | switch to descend at the chosen alpha if same k and higher silhouette | 0.9602 [0.9349, 0.9810] | 0.0000 [0.0000, 0.0000] | not kept |
| 9 | gapk_silhouette | gap statistic picks k; raw silhouette picks alpha at that k | 0.9615 [0.9365, 0.9816] | +0.0013 [0.0000, +0.0039] | not kept |
| 10 | gapk_silhouette_descend | as 9, plus descend at alpha ≤ 1% | 0.9630 [0.9384, 0.9835] | +0.0028 [0.0000, +0.0083] | not kept |
| 11 | formula_window_silhouette | restrict choices to within a factor 4 of 240/(n d²) | 0.9591 [0.9330, 0.9797] | −0.0011 [−0.0054, +0.0014] | not kept |
| 12 | calibrated_authors_direction | direction by the authors' convention (descend iff d ≥ 10) | 0.9611 [0.9346, 0.9826] | +0.0009 [−0.0062, +0.0087] | not kept |
| 13 | gapk_descend_uncapped | as 10, descend at all 15 alphas | 0.9632 [0.9386, 0.9837] | +0.0030 [0.0000, +0.0088] | not kept |
| 14 | uniform_box_reference | uniform bounding-box reference instead of the moment-matched Gaussian | 0.9556 [0.9276, 0.9787] | −0.0046 [−0.0110, 0.0000] | not kept |

The kept trial uses randomness for its reference samples, so the Skeptic ran `recheck`. Seed 1 gave 0.9615 [0.9365, 0.9816], a gain of +0.0201 [+0.0026, +0.0423]. Seed 2 gave 0.9602 [0.9349, 0.9810], a gain of +0.0188 [+0.0026, +0.0396]. Both were compared with the incumbent at seed 0.

**Formula trials (val)**

| # | Trial | Formula | Mean ARI [95% CI] | Δ vs incumbent [95% CI] | Outcome |
|---|---|---|---|---|---|
| 0 | formula.py (start) | 5%, ascend | 0.8598 [0.8035, 0.9064] | — | starting point |
| 1 | geometric_d_decay | 0.3 · 0.5^(d−2), ascend | 0.8905 [0.8418, 0.9355] | +0.0308 [−0.0102, +0.0727] | not kept |
| 2 | inverse_square_d_ascend | 1.2/d², ascend | 0.9020 [0.8535, 0.9416] | +0.0422 [+0.0033, +0.0827] | **kept** |
| 3 | inverse_square_descend | 1.2/d², descend for d ≥ 10 | 0.9229 [0.8856, 0.9559] | +0.0210 [−0.0109, +0.0549] | not kept |
| 4 | inverse_n_d2 | 240/(n d²), ascend | 0.9125 [0.8674, 0.9492] | +0.0105 [+0.0021, +0.0207] | **kept** |
| 5 | inverse_n_d2_descend10 | 240/(n d²), descend for d ≥ 10 | 0.9257 [0.8868, 0.9592] | +0.0132 [−0.0180, +0.0456] | not kept |
| 6 | steeper_d | 400/(n d^2.55), ascend | 0.9158 [0.8736, 0.9540] | +0.0033 [−0.0201, +0.0286] | not kept |
| 7 | sat10_cubic | 500/(n min(d,10)³), ascend | 0.9122 [0.8649, 0.9502] | −0.0002 [−0.0067, +0.0062] | not kept |
| 8 | descend_large_n | 240/(n d²), descend for n ≥ 100 | 0.9232 [0.8826, 0.9595] | +0.0107 [−0.0187, +0.0419] | not kept |
| 9 | descend_band | 240/(n d²), descend iff d ≥ 10 and n·alpha ≥ 1 | 0.9303 [0.8934, 0.9624] | +0.0178 [+0.0026, +0.0403] | passed the numeric rule; **rejected by the Skeptic** |

**Screens that never reached val.** Five ideas were tested only on dev or on the lab's own simulations and stopped there, so none used val budget. In the matched-null silhouette screen, the trial lost to the incumbent in every Gaussian stress cell, by between −0.110 and −0.222 (`notes/stress/mn_*`). The calibrated gap screen was mixed: +0.040 [+0.006, +0.084] at n = 30, d = 15, and −0.004 to +0.000 elsewhere (`notes/stress/gap_*`). The sad_trimmed_k screen gave results identical to small_alpha_descend on every cell (`notes/stress/tk_*`). Two formula screens rounded out the set: fitting a power law to simulations (sim_fit_power_formula, `notes/simfit/`) and a dimension band for the descending search (dim_band_descend_formula, `notes/dimband/`). Both failed decision rules set in advance and are described below.

**What was learned.**

*The silhouette needs a null baseline that depends on k.* The raw silhouette tends to favour few clusters even when there is no structure. Subtracting s0(k), the silhouette that k-means with k groups reaches on a structureless Gaussian sample with X's mean and covariance, was the one change that clearly helped on val. Its whole val gain comes from four datasets, all Gaussian with five clusters, where the silhouette maximum had merged clusters (from the details files):

| val # | Regime | Silhouette max: alpha, ARI | Kept experiment: alpha, ARI |
|---|---|---|---|
| 50 | Gaussian, d = 10, n = 50, k = 5 | 1.5%, 0.3553 | 8%, 0.6023 |
| 53 | Gaussian, d = 10, n = 200, k = 5 | 20%, 0.3649 | 0.5%, 0.7730 |
| 56 | Gaussian, d = 20, n = 50, k = 5 | 0.1%, 0.2544 | 1%, 0.4216 |
| 59 | Gaussian, d = 20, n = 200, k = 5 | 5%, 0.3599 | 8%, 0.7409 |

All other 60 val datasets scored the same under the two rules. Because the gain rests on so few datasets, the lab checked it on its own simulations of the test design (`notes/stress/`, described in Section 7). There the experiment beat the silhouette maximum in every Gaussian cell: +0.179 [+0.087, +0.272] at n = 30, d = 15; +0.152 [+0.071, +0.238] at n = 300, d = 7; +0.075 [+0.021, +0.137] at n = 300, d = 4 with 30% noise; and +0.176 [+0.096, +0.262] at n = 700, d = 7 with 10% noise (30 datasets per cell). In the uniform cell the two rules tied at 0.999.

*The reference must look like the data.* Replacing the moment-matched Gaussian with a uniform sample over X's bounding box (uniform_box_reference) changed only two val datasets, both for the worse (−0.0046 overall). On the stress simulations it lost 0.039 to 0.116 in every Gaussian cell. In 27 of its 28 changed choices it moved to fewer clusters. Using one deterministic reference (single_reference) or z-scoring by the null spread (zscore_reference) also lost on val. Five references with the mean difference, as kept, worked best of the variants tried.

*Val is saturated for the experiment.* Once the experiment was kept, its distance to the ascending ceiling on val (0.0046) was below the keep bar (0.005). Every later experiment trial was therefore at best a near-tie on val. The strongest of them, gapk_silhouette_descend, gained only +0.0028 on val, but +0.0445 [+0.0093, +0.0866] on the hardest stress cell (n = 30, d = 15). It is the strongest rule the lab did not promote. The program's keep rule is decided on val, so it stays a trial.

*No label-free rule for the search direction helped robustly.* Letting the calibrated score choose the direction (calibrated_direction), allowing descend only at small alpha (small_alpha_descend), switching at the chosen alpha (same_alpha_descend) and following the authors' d ≥ 10 convention (calibrated_authors_direction) all gave val changes between 0.0000 and +0.0028. None had an interval clear of zero by the keep bar. On the formula side, descending for d ≥ 10 raised the val mean in two trials, but each time with an interval that included zero. In the lab's simulations, descending at the formula's alpha lost or tied at every dimension tested (`notes/dimband/`). Descending for d = 5 gave −0.127 [−0.201, −0.060] and for d = 15 (n ≤ 300) gave −0.050 [−0.120, −0.001].

*The formula's form.* The kept formula holds n·alpha, the expected number of balls that reject CSR by chance, at 240/d². A simulation fit of alpha = a·n^(−b)·d^(−c) found the optimum flat (`notes/simfit/`). The current 240/(n d²) scored 0.8036 on held-out cells at the test's d and n. The best fitted alternatives gained only +0.0036 [−0.031, +0.040] and +0.0095 [−0.025, +0.042], short of the +0.01 gain set in advance, so no trial was run. Two such alternatives were later run on val anyway: steeper_d (+0.0033) and sat10_cubic (−0.0002). Neither passed.

*The rejected descend_band formula.* This trial passed the numeric keep rule (+0.0178 [+0.0026, +0.0403]), but the Skeptic rejected it. Its trial file admits that the band (descend only when d ≥ 10 and 240/d² ≥ 1, in effect d = 10 to 15) was formulated after seeing the per-dataset val results of inverse_n_d2_descend10. That trial had gained at d = 10 and lost at d = 20, so the band was fitted to val. On the test dimensions (4, 7, 15) it would change only d = 15. At d = 15 the lab's own simulations show descending is worse at the formula's alpha: −0.050 [−0.120, −0.001] for n ≤ 300. The change would therefore probably hurt the formula on test and work against H2. We report it as a val result that should not be trusted.

## 5. The kept rule and formula, in plain words

**The experiment (null-calibrated silhouette).** For a dataset X with n points in d dimensions, the rule runs UN-CCD with the ascending radius search at each of the 15 alphas on the grid. Each run gives k clusters and their mean silhouette s. Five reference samples of n points are then drawn from a single Gaussian with X's sample mean and covariance; a reference sample has no cluster structure but the same overall shape. For each k that occurred, k-means (k-means++ seeding, best of three starts) splits each reference into k groups. The average silhouette of those splits is s0(k), the silhouette that k clusters reach by chance. The rule chooses the alpha whose clustering has the largest s − s0(k), with ties going to the smaller alpha, and always uses the ascending search. Clusterings with one cluster, or with one cluster per point, are never chosen unless every alpha gives one cluster; then the plain largest silhouette is used. The rule sees only X and a seed. Its k-means is written in NumPy, because scikit-learn's KMeans reads /proc, which the harness sandbox forbids. In one sentence: take the alpha at which UN-CCD's silhouette most exceeds what the same number of clusters would score on featureless Gaussian data of the same shape.

The alphas it chose on val, by dimension (from the details files; each val dimension has 12 datasets, plus 2 noise datasets at d = 3 and 10):

| d | Alphas chosen (count) | Paper's schedule |
|---|---|---|
| 2 | 0.1% (3), 0.75% (2), 1.5% (1), 3% (1), 10% (1), 30% (4) | 15% |
| 3 | 0.1% (3), 0.2% (1), 0.3% (1), 0.5% (1), 1.5% (2), 2% (2), 3% (1), 8% (1), 15% (1), 30% (1) | 10% |
| 5 | 0.1% (8), 0.5% (1), 1% (1), 20% (1), 30% (1) | 5% |
| 10 | 0.1% (6), 0.5% (2), 0.75% (2), 1.5% (1), 8% (2), 15% (1) | 1%, descend |
| 20 | 0.1% (6), 0.3% (1), 0.75% (1), 1% (2), 2% (1), 8% (1) | 0.1%, descend |

The experiment does not follow a dimension schedule. It picks the grid's smallest value, 0.1%, for 26 of the 64 val datasets, and values spread over the whole range for the rest.

**The formula.** alpha = 240/(n d²), snapped to the grid, always with the ascending search. Each of the n balls is tested against CSR at level alpha, so n·alpha is the expected number of chance rejections. The formula holds that count at 240/d² (60 at d = 2, 9.6 at d = 5, 2.4 at d = 10, 0.6 at d = 20). Larger samples and higher dimensions therefore get a stricter per-ball test. It has one numeric constant and uses only n and d. The snapped alphas it gives (computed from formula.py with the harness's `nulls.snap`):

| n \ d | 2 | 3 | 4 | 5 | 7 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|
| 30 (test) | 30% | 30% | 30% | 30% | 15% | 8% | 3% | 2% |
| 50 (val) | 30% | 30% | 30% | 20% | 10% | 5% | 2% | 1% |
| 100 (dev) | 30% | 30% | 15% | 10% | 5% | 2% | 1% | 0.5% |
| 200 (val) | 30% | 15% | 8% | 5% | 2% | 1% | 0.5% | 0.3% |
| 300 (test) | 20% | 8% | 5% | 3% | 1.5% | 0.75% | 0.3% | 0.2% |
| 700 (test) | 8% | 3% | 2% | 1.5% | 0.75% | 0.3% | 0.2% | 0.1% |
| Paper's schedule | 15% | 10% | 8% | 5% | 3% | 1% (desc.) | 0.3% (desc.) | 0.1% (desc.) |

At n = 200 the formula reproduces the paper's schedule closely at d = 4 to 10, but uses the ascending search where the schedule descends.

## 6. What is new and what is not

Choosing a tuning parameter by an internal criterion is standard practice in clustering. The silhouette is reviewed by Shutaywi and Kachouie (2021) and validation indices in general by Hassan et al. (2024). Comparing a criterion with its value on a structureless reference distribution is the idea of the gap statistic (Tibshirani, Walther and Hastie, 2001). Choosing a parameter by the agreement of resampled partitions is the stability approach (von Luxburg, 2010; Monti et al., 2003; Dudoit and Fridlyand, 2002). The kept rule borrows the gap statistic's calibration against a reference and applies it to the silhouette. Nobody should read it as a new principle.

What is new is narrower. The lab built a label-free rule for UN-CCD's significance level specifically, and a one-constant formula in n and d. Both are frozen and will be judged by a pre-registered test, on regimes the paper never ran, against the paper's own hand-tuned schedule. Within cluster catch digraphs, earlier variants set their scale parameter by a test against CSR rather than by an outside criterion (Manukyan and Ceyhan, 2019; Shi, Ceyhan and Billor, 2025). The Scout's searches found no prior work that chooses UN-CCD's alpha, or the search direction, without labels.

## 7. Limits

**Simulated data in the paper's family.** Dev and val use the paper's own design and fixed centres. The test's synthetic part uses new dimensions (4, 7, 15), new sample sizes (30, 300, 700), up to 30% noise and random-walk centres. Only five test datasets are real. The val results show what the rules do in the design the schedule was tuned for. They cannot show transfer.

**One dataset per val regime.** The val interval is a bootstrap over 64 regimes with one dataset each. The kept experiment's whole val gain over the silhouette maximum comes from four datasets (Section 4). Twenty-three val evaluations, 14 experiment and 9 formula trials, were judged against the same 64 datasets. The 0.005 bar and the paired interval protect against noise, but they do not correct for selecting the best of many trials.

**A 15-value grid.** Alpha is snapped to 15 values from 0.1% to 30%. The experiment chose the grid's smallest value for 26 of 64 val datasets, and the largest for 6. Its preferred alpha may therefore sometimes lie outside the grid.

**The humans' look at dev and val.** The humans built the lab with dev and val in view, and the paper's schedule was itself tuned with labels on this design. The val datasets, with their labels, are in the sandbox. Every trial's code was archived and read before any result was accepted, but only the sealed test protects the conclusions.

**The search direction.** The val gains from descending at d ≥ 10 seen in some formula trials did not appear in the lab's simulations with random-walk centres. The difference may come from val's fixed centres. The test (random-walk centres, d = 15) will show which pattern holds.

**The lab's stress simulations are its own approximation.** `notes/stress/stress.py` was written from program.md alone, not from the test generator, and assumes that n counts noise points. It ran four cells close to the test regimes with 30 datasets each. The table below shows the cell means: the experiment, silhouette maximum, schedule and ascending ceiling are from `notes/stress/results.md`. The best fixed alpha per cell and the frozen formula's score are not in any note's text. The Scribe computed them from the per-alpha ARIs stored, at three decimals, in the `curve` field of `notes/stress/raw_*_r30.json`. (`results.md`'s own "formula" column is 1.2/d², the formula current at wave 3, not the frozen one.)

| Cell (30 datasets) | Experiment | Silhouette max | Schedule | Frozen formula 240/(n d²) | Best single alpha in cell (labels) | Ascending ceiling (labels) |
|---|---|---|---|---|---|---|
| n = 30, d = 15, k = 6, Gaussian | 0.562 | 0.383 | 0.330 | 0.452 (3%) | 0.452 (3%) | 0.617 |
| n = 300, d = 7, k = 4, uniform | 0.999 | 0.999 | 0.999 | 0.999 (1.5%) | 0.999 | 0.999 |
| n = 300, d = 7, k = 4, Gaussian | 0.961 | 0.809 | 0.835 | 0.862 (1.5%) | 0.881 (0.75%) | 0.965 |
| n = 300, d = 4, k = 3, Gaussian, 30% noise | 0.851 | 0.775 | 0.702 | 0.748 (5%) | 0.771 (1.5%) | 0.858 |
| n = 700, d = 7, k = 4, Gaussian, 10% noise | 0.933 | 0.757 | 0.790 | 0.834 (0.75%) | 0.834 (0.75%) | 0.937 |

In every Gaussian cell, even the best single alpha chosen with the labels trails the experiment by 0.080 to 0.110. The frozen formula trails it by 0.099 to 0.110. Any rule that gives one alpha per (n, d) has this handicap, because most of the experiment's advantage comes from variation between datasets within a cell. **This is the lab's prediction, stated before `final`: H2 (formula within 0.02 of the experiment) is likely to fail on test.** For H1 the same simulations point the other way. The experiment was above the schedule in every non-trivial cell, and on val it exceeds the schedule by 0.0546. These are the lab's own simulations, not the test, so they show a direction, not the outcome.

**Weak spots of the kept rule.** Under 30% noise the experiment twice chose five clusters where there are three, in 2 of 30 stress datasets, losing 0.06 and 0.08 to the silhouette maximum. The null reference s0(k) falls with k, so heavy noise can favour a fragmented clustering. At n = 30, d = 15 the reference covariance is estimated from 30 points, yet the rule still beat the silhouette maximum there (0.562 against 0.383).

**Implementation.** The sandbox blocked scikit-learn's KMeans, so the rule uses its own NumPy k-means. The null tables cap n by dimension (`notes/simfit/results.md`): 800 at d = 2, 300 at d = 3, 5, 10 and 20, and 1,000 at d = 4, 7 and 15. The test's dimensions are therefore covered up to n = 700.

**What the Skeptic flagged.** The descend_band formula was rejected because its band was fitted to val after the fact and would work against H2 on test (Section 4). The ledger keeps it as a numeric pass that was not promoted.

**Literature.** Three of the Scout's leads were dropped because their metadata could not be verified: Ben-Hur, Elisseeff and Guyon (2002); Tibshirani and Walther (2005) on prediction strength; and Lange et al. (2004). Beyer et al. (1999), Clark and Evans (1954) and Diggle (2003) were dropped for the same reason. The Scout's statement that a random nearest neighbour is "closer in high d" is backwards: at fixed n, the expected nearest-neighbour distance scale n^(−1/d) grows with d.

## 8. Sources

Each entry's metadata was checked against Crossref, arXiv or OpenAlex on 2026-10-16. Corrections to the Scout's notes are marked.

1. Shi, R., Ceyhan, E. and Billor, N. (2025). Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs. arXiv:2501.06268 (version 3 used). https://arxiv.org/abs/2501.06268v3
2. Manukyan, A. and Ceyhan, E. (2019). Parameter Free Clustering with Cluster Catch Digraphs (Technical Report). arXiv:1912.11926. https://arxiv.org/abs/1912.11926
3. Tibshirani, R., Walther, G. and Hastie, T. (2001). Estimating the number of clusters in a data set via the gap statistic. *Journal of the Royal Statistical Society Series B* 63(2), 411–423. https://doi.org/10.1111/1467-9868.00293
4. von Luxburg, U. (2010). Clustering Stability: An Overview. *Foundations and Trends in Machine Learning* 2(3), 235–274. https://doi.org/10.1561/2200000008
5. Monti, S., Tamayo, P., Mesirov, J. and Golub, T. (2003). Consensus Clustering: A Resampling-Based Method for Class Discovery and Visualization of Gene Expression Microarray Data. *Machine Learning* 52(1–2), 91–118. https://doi.org/10.1023/a:1023949509487
6. Dudoit, S. and Fridlyand, J. (2002). A prediction-based resampling method for estimating the number of clusters in a dataset. *Genome Biology* 3(7), research0036. https://doi.org/10.1186/gb-2002-3-7-research0036 (*Correction: the Scout attributed this DOI to Ben-Hur et al.; Crossref gives Dudoit and Fridlyand.*)
7. Shutaywi, M. and Kachouie, N. N. (2021). Silhouette Analysis for Performance Evaluation in Machine Learning with Applications to Clustering. *Entropy* 23(6), 759. https://doi.org/10.3390/e23060759
8. Hassan, B. A., Tayfor, N. B., Hassan, A. A., Ahmed, A. M., Rashid, T. A. and Abdalla, N. N. (2024). From A-to-Z review of clustering validation indices. *Neurocomputing* 601, 128198. https://doi.org/10.1016/j.neucom.2024.128198
9. DeVinney, J. and Priebe, C. E. (2006). A new family of proximity graphs: Class cover catch digraphs. *Discrete Applied Mathematics* 154(14), 1975–1982. https://doi.org/10.1016/j.dam.2006.04.004 (*the Scout listed it as "Priebe et al."*)
10. Ceyhan, E. and Priebe, C. E. (2005). The use of domination number of a random proximity catch digraph for testing spatial patterns of segregation and association. *Statistics & Probability Letters* 73(1), 37–50. https://doi.org/10.1016/j.spl.2005.02.012
11. Ceyhan, E., Priebe, C. E. and Wierman, J. C. (2006). Relative density of the random r-factor proximity catch digraph for testing spatial patterns of segregation and association. *Computational Statistics & Data Analysis* 50(8), 1925–1964. https://doi.org/10.1016/j.csda.2005.03.002 (*the Scout dated it 2005; Crossref gives the 2006 issue*)
12. Hinneburg, A., Aggarwal, C. C. and Keim, D. A. (2000). What Is the Nearest Neighbor in High Dimensional Spaces? OpenAlex W1595303882 (no DOI). https://openalex.org/W1595303882 (*the Scout attributed it to Beyer et al.*)

Internal sources: `lab/unccd_alpha/program.md`, `harness.py`, `kit.py`, `nulls.py`, `experiment.py` and `formula.py`; `data/manifest.json` and `data/port_validation.json`; `runs/unccd_alpha/ledger.tsv`, `details/` and `frozen.json`; and `runs/unccd_alpha/notes/` (scout_label_free_tuning.md, scout_ccd_csr.md, stress/, simfit/, dimband/). program.md also cites the Artemis Project 1 reproduction report (branch unccd-repro, docs/Artemis_UNCCD_Reproduction_Report.docx), which this report did not consult.

## 9. Test results (to be added by the humans after `harness.py final`)

> **PLACEHOLDER: not filled in by the lab.** The test split is not in the sandbox, and the lab did not run `final`. The humans will run `python lab/unccd_alpha/harness.py final` on exactly the files fingerprinted in `frozen.json` and add the following here:
>
> - **H1** (experiment − schedule, test synthetic regimes): mean difference, paired 95% CI, pass/fail (lower end > −0.02).
> - **H2** (formula − experiment, test synthetic regimes): mean difference, paired 95% CI, pass/fail (lower end > −0.02).
> - Every rule's mean ARI on the five real datasets (aggregation, compound, jain, glass, yeast).
> - The experiment's differences from the fixed 1 percent, the silhouette maximum and the label-using ceiling.
>
> The lab's prediction, recorded before `final` (Section 7): H2 is likely to fail.

---

## 2. Val results: the kept rule and formula beside every baseline

All figures are from the harness ledger: mean ARI over 64 regimes, with a 95% bootstrap interval over regimes.

| Rule | val mean ARI | 95% CI |
|---|---|---|
| **Kept experiment: null-calibrated silhouette** | **0.9602** | [0.9349, 0.9810] |
| **Kept formula: 240/(n d²), ascend** | **0.9125** | [0.8674, 0.9492] |
| paper_schedule | 0.9056 | [0.8622, 0.9443] |
| fixed_0.01 | 0.8230 | [0.7573, 0.8823] |
| fixed_0.05 (the starting formula) | 0.8598 | [0.8035, 0.9064] |
| silhouette_max (the starting experiment) | 0.9414 | [0.8989, 0.9748] |
| oracle_ascend (uses labels) | 0.9648 | [0.9427, 0.9830] |
| oracle_any (uses labels) | 0.9677 | [0.9455, 0.9858] |

How the two were kept, as paired differences from the incumbent of the time:
- **Experiment:** +0.0188 [+0.0026, +0.0396]. Rechecks gave 0.9615 on seed 1 and 0.9602 on seed 2.
- **Formula:** +0.0105 [+0.0021, +0.0207] against the earlier formula 1.2/d², which scored 0.9020.

## 3. Source of lab/unccd_alpha/experiment.py

```python
"""Null-calibrated silhouette: choose the alpha whose silhouette most exceeds its no-structure expectation.

For each alpha on the grid, UN-CCD is run with the ascending radius search and
gives a clustering with k clusters and mean silhouette s. The silhouette tends
to be high for small k even when there is no structure, so it is compared with
a reference: five samples of n points drawn from a single Gaussian with the
same mean and covariance as X, each split into k groups by k-means, give the
average silhouette s0(k) that k clusters reach on structureless data. The rule
chooses the alpha with the largest s - s0(k); ties go to the smaller alpha.
Clusterings with one cluster (or one cluster per point) are never chosen,
unless every alpha gives a single cluster, in which case the plain largest
silhouette is used. Only the unlabelled data and the seed are used.
"""
import numpy as np
from sklearn.metrics import silhouette_score

B = 5


def kmeans(R, k, n_init, rng, max_iter=100):
    """Plain k-means (k-means++ seeding, Lloyd iterations), best of n_init by inertia.

    Written in NumPy because sklearn's KMeans probes the thread pool by reading
    /proc, which the harness sandbox forbids.
    """
    n = R.shape[0]
    sq = (R * R).sum(axis=1)
    best_lab, best_inertia = None, np.inf
    for _ in range(n_init):
        centers = [R[rng.integers(n)]]
        d2 = ((R - centers[0]) ** 2).sum(axis=1)
        for _ in range(1, k):
            tot = d2.sum()
            idx = rng.integers(n) if tot <= 0 else rng.choice(n, p=d2 / tot)
            centers.append(R[idx])
            d2 = np.minimum(d2, ((R - R[idx]) ** 2).sum(axis=1))
        C = np.array(centers)
        lab = None
        for _ in range(max_iter):
            D = sq[:, None] - 2.0 * R @ C.T + (C * C).sum(axis=1)[None, :]
            new = D.argmin(axis=1)
            if lab is not None and np.array_equal(new, lab):
                break
            lab = new
            for j in range(k):
                m = lab == j
                if m.any():
                    C[j] = R[m].mean(axis=0)
        D = sq[:, None] - 2.0 * R @ C.T + (C * C).sum(axis=1)[None, :]
        lab = D.argmin(axis=1)
        inertia = float(D[np.arange(n), lab].sum())
        if inertia < best_inertia:
            best_lab, best_inertia = lab, inertia
    return best_lab


def choose(X, kit, seed):
    X = np.asarray(X, dtype=float)
    n, d = X.shape
    results = []
    for alpha in kit.alphas:
        r = kit.cluster(alpha, "ascend")
        results.append((alpha, int(r["clusters"]), float(r["silhouette"])))

    ks = sorted({k for _, k, _ in results if 2 <= k < n})
    if not ks:
        best_alpha, best_value = kit.alphas[0], -np.inf
        for alpha, k, s in results:
            if s > best_value:
                best_alpha, best_value = alpha, s
        return {"alpha": best_alpha, "direction": "ascend"}

    rng = np.random.default_rng(seed)
    mean = X.mean(axis=0)
    cov = np.atleast_2d(np.cov(X.T)) + 1e-9 * np.eye(d)
    L = np.linalg.cholesky(cov)
    refs = [mean + rng.standard_normal((n, d)) @ L.T for _ in range(B)]

    s0 = {}
    for k in ks:
        vals = []
        for R in refs:
            lab = kmeans(R, k, 3, np.random.default_rng(seed))
            if len(np.unique(lab)) < 2:
                vals.append(0.0)
            else:
                vals.append(float(silhouette_score(R, lab)))
        s0[k] = float(np.mean(vals))

    best_alpha, best_value = kit.alphas[0], -np.inf
    for alpha, k, s in results:
        if k < 2 or k >= n:
            continue
        value = s - s0[k]
        if value > best_value:
            best_alpha, best_value = alpha, value
    return {"alpha": best_alpha, "direction": "ascend"}
```

## Source of lab/unccd_alpha/formula.py

```python
"""Alpha falls with both the number of points and the square of the dimension: alpha = 240 / (n * d^2), always with the ascending radius search. Since n balls are each tested against CSR, n*alpha is the expected number of balls that reject CSR by chance alone; this holds that count at 240/d^2 (d=2: 60, d=5: 9.6, d=10: 2.4, d=20: 0.6), so a larger n gets a smaller per-ball alpha. Uses n and d."""


def alpha_formula(n, d):
    return 240 / (n * d ** 2), "ascend"
```

## 4. runs/unccd_alpha/frozen.json

```json
{
  "utc": "2026-10-16T00:05:48Z",
  "git_commit": "2827ea6",
  "experiment_sha256": "2732632753171e1241ad913f3e020c541ec7b68ca74cb1f874bfbf9877a547fd",
  "formula_sha256": "1dbe3c146c87a5f622f925f8fe0caa517320063d5d25f3043bea2d22c98165c1",
  "fingerprint": {
    "harness": "c19d056bdfff39d6a770697e5eb2663fa4f98f1710a7208fe76b567f3f3206bd",
    "runner": "9be6f26b261c94d49f7115da607b6581803a3dad3b713c021263b9b9b5461b5b",
    "kit": "4bead9b6200881012bdf3db11f2ccff48918316efa9760f3afca5541f03fa78e",
    "unccd": "6e7fd1ac8b333ac0110e8a0335ca8970d0be196835a90f5f2b4b9812406e6c91",
    "nulls": "a55376cc332e3be20edb34ac31d6b75533996cdf26c6dc1d12de2b7ca696e480",
    "data": "7f404af31412196d67bacdbf178e66db0fc4bc804623650194f1aefe12c52b90"
  }
}
```

ARTEMIS-RUN-COMPLETE
[turn finished]


The lab reports the run is complete.
Saved 357 items of the lead session.