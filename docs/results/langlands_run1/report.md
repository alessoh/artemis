The run is finished: both Part B hypotheses are supported on the held-out test conductors, and over Q(√5) the murmurations line up with the flipped sign, as predicted. All 1,069,314 classes in the snapshot are rank 0 or rank 2. The final test ran once, as the last step. The results and the code are committed (git e5a6c05 and earlier).

## 1. runs/langlands/report.md

# The archimedean sign, murmurations and local root numbers: report of the Artemis Langlands run

*Written by the Scribe. Every number below is copied from `runs/langlands/final_test.json`, `runs/langlands/final_part_A.json`, `runs/langlands/ledger.tsv`, the harness output recorded at setup, or a cited source. The definitions come from `lab/langlands/program.md` and `lab/langlands/harness.py`.*

## 1. Summary

The program tests research direction R1 of P. Alesso, "Euler's identity and the Langlands program" (research memo, 2026). The memo's premise is that Euler's identity, e^{iπ} = −1, is the root number of a real place. For an elliptic curve over Q this gives the familiar w(E) = −∏_{p|N} w_p. Over a totally real field of degree d the sign becomes (−1)^d ∏ w_v. So over Q(√5) it is **+** the product of the finite local signs, the opposite of the rule over Q for the same finite data. The memo asks two questions.

1. **Part A.** Murmurations correlate a_p with the root number. Over Q(√5), do they line up with +(product of finite local signs), the reverse of what the same rule gives over Q (the "predicted flip")?
2. **Part B.** Rank 0 and rank 2 curves over Q both have w = +1, so their local signs have the same product. Does the vector of local signs (w_p)_{p|N} still depend on rank among classes with the *same* conductor?

**The answers.** Part A reproduces the murmuration mirror image over Q. Over Q(√5) the pre-registered statistic is the correlation ρ_ss between the profile F_ss (signed by +S, where S is the product of the finite signs) and the profile M_Q over Q. It came out **ρ_ss = 0.5313, 95% interval [0.4605, 0.5944]**, so the verdict is **"consistent with the predicted flip"**. Deligne's formula and the data-build parity checks already implied this, so the result confirms theory rather than discovering anything. In Part B, local signs do carry rank information within a conductor, but the signal is weak. On held-out test conductors (400,000 to 499,999) the frozen simple rule (count the split multiplicative primes) has within-conductor AUC **0.521744** [0.516516, 0.52729], z = 8.591, p = 4.32e-18 (**H_B1 supported**). The lab's promoted experiment has AUC **0.542611** [0.535592, 0.549993], z = 15.114, p = 6.57e-52 (**H_B2 supported**). Both have permutation p = 0.0005. For scale, the positive control is a Nagao-type sum over a_p, which experiments never see. On the same pairs it reaches AUC **0.963781**, z = 160.017. Most of the rank-0 versus rank-2 difference therefore lives in the a_p at the good primes, not in the local signs.

## 2. Data and definitions

### 2.1 Data

The snapshot in `lab/langlands/data/` was built once by `prepare_data.py` and is fingerprinted. The Scribe did not open the data directory. The description below comes from `program.md` and the harness docstring.

| Source | Content |
|---|---|
| John Cremona's elliptic curve tables, github.com/JohnCremona/ecdata at commit 25cec5e | Every isogeny class over Q with N < 500,000 and rank 0 or 2 (790,258 rank 0, 279,056 rank 2; 1,069,314 classes): N, each bad prime with exponent and local root number, and a_p at good p < 100. |
| PARI/GP 2.17.2 | For every class over Q with N < 5,000 (17,314 classes): rank, global root number, local signs, and a_p at every good p ≤ N. Local signs, global sign and rank parity were checked against each other for every class. |
| LMFDB file for curves over Q(√5), downloaded 2026-10-08 | One curve per isogeny class, 4,605 classes with conductor norm below 5,000: conductor norm, rank, PARI's global root number, bad primes as (norm, exponent, a_P), the product of the finite signs for semistable classes, and a_P at degree-one primes P not dividing the conductor with norm up to the conductor norm. |

PARI computes local root numbers only over Q. Over Q(√5) the finite sign is therefore computed only for semistable classes, as S = ∏(−a_P) over the multiplicative primes. Classes with additive primes enter Part A only through PARI's global root number. According to `program.md`, the data build confirmed two things. First, for all 3,333 semistable classes over Q(√5), PARI's global root number equals +S. Second, for 4,602 of the 4,605 classes it equals (−1)^rank; the other three have only rank bounds in the LMFDB. Ranks are as recorded in Cremona's tables and the LMFDB.

**Fingerprints** (identical in `final_test.json` and `final_part_A.json`):

| Item | SHA-256 |
|---|---|
| harness | `f5cf8570c3c5f371a60856d274f31509eb0ad89d05b9ecb9430df26ac3273a9d` |
| runner | `e03f4619986918746f880dc97e8830f8f9fb0296b21a31eec8e26cc4fe9dd4b1` |
| data | `42345fcb4d935152950433bd4c899adbed94e4979a0b3a0d418423a476a696c8` |
| promoted experiment.py | `fbe1a6557a673fbeb154f17e778d16bc2b4d71c00215792c66322f270b0b975e` |

### 2.2 Part A definitions (pre-registered)

- **Bins.** x = p/N in ten bins of width 0.1 on [0, 1]; the last bin includes x = 1. Over Q(√5), p is the norm of a degree-one prime P not dividing the conductor, and N is the conductor norm.
- **C1 (over Q, N from 1,000 to 4,999).** M_Q(b) is the mean of w(E)·a_p/√p in bin b. P+ and P− are the means of a_p/√p over classes with w = +1 and w = −1. C1 counts as *reproduced* if corr(P+, P−) has its 95% interval below 0 (the mirror image) and M_Q changes sign at least once.
- **C2 (over Q(√5), conductor norm from 1,000 to 4,999).** F_ss(b) is the mean of S·a_P/√p over semistable classes. The primary statistic is ρ_ss, the Pearson correlation of F_ss with M_Q across the ten bins. The prediction is ρ_ss > 0. Carrying the Q convention over unchanged would give ρ_ss < 0. The verdict is "consistent with the predicted flip" if the 95% interval lies above 0, "contradicts the prediction" if it lies below 0, and "inconclusive" otherwise. Also reported: ρ_all, which uses F_all over every class with PARI's root number; the first-bin values; and a sensitivity check without classes that have a model over Q (base changes).
- **Intervals.** 2,000 bootstrap draws (seed 0) resampling whole conductors over Q and whole conductor norms over Q(√5). Resampling whole norms keeps Galois-conjugate classes together.

### 2.3 Part B definitions (pre-registered)

- **Splits by conductor.** Train N < 300,000: 645,851 classes, 159,694 of rank 2. Val 300,000 ≤ N < 400,000: 213,519 classes. Test 400,000 ≤ N < 500,000: 209,944 classes, 59,548 of rank 2, touched once by `final`. The free probe fits below N = 200,000 and scores 200,000 to 299,999.
- **Interface.** An experiment is `score(train, rows, seed)`. It sees only N and the list of bad primes as [p, e, w_p] (plus rank in `train`). It never sees a_p, curves, labels or Cremona's class order. Each distinct (N, sign pattern) is scored once.
- **Metric.** Within-conductor AUC: over all pairs of a rank 2 class and a rank 0 class with the same N, the fraction in which the rank 2 class scores higher (ties count ½). Classes sharing N share primes and exponents, so only the signs can move the AUC away from 0.5. The harness also reports the stratified Wilcoxon z, a one-sided p and a 95% bootstrap interval over conductors.
- **Keep rule.** A trial must beat the current best val AUC by ≥ 0.002, and the lower end of the paired 95% interval must be above 0. The Skeptic then rechecks with seeds 1 and 2 and probes, rejecting a gain that vanishes on the probe.
- **Final hypotheses.** Each is one-sided at p < 0.01, by both the normal approximation and 2,000 within-conductor permutations. **H_B1:** the frozen simple rule (the number of multiplicative primes with w_p = −1, i.e. split multiplicative) has AUC > 0.5 on test. **H_B2:** the promoted experiment, trained on train plus val with seed 0, has AUC > 0.5 on test.
- **Positive control.** The sum over good p < 100 of −a_p·log(p)/p. It uses a_p, which experiments never see.

### 2.4 Part B baselines on val (setup, from the ledger)

| Baseline | Val AUC | 95% interval | z |
|---|---|---|---|
| split_count (the simple rule) | 0.521045 | [0.515417, 0.527059] | 8.439 |
| nagao_ap25 (positive control) | 0.966455 | [0.965065, 0.967879] | 165.194 |

## 3. Part A: murmurations over Q and over Q(√5)

### 3.1 Pilot (setup, free; N and norm below 1,000)

| | Range | Sample | Statistic | Outcome |
|---|---|---|---|---|
| C1 | N 11–999 | 2,463 classes, 707 conductors | mirror corr −0.9171 [−0.9352, −0.8933]; 3 sign changes of M_Q | reproduced |
| C2 | norm < 1,000 | 517 semistable classes, 128 norms | ρ_ss 0.4654 [0.2679, 0.6122] | consistent with the predicted flip |

The humans had seen these pilot numbers before the run.

### 3.2 Confirmatory ranges (computed once, by `final`)

| | C1 over Q | C2 over Q(√5) |
|---|---|---|
| Range | N 1,000–4,999 | norm 1,000–4,999 |
| Sample | 14,851 classes, 2,730 conductors | 2,816 semistable classes over 451 norms; 3,973 classes over 538 norms in all |

**The profiles side by side, by bin of x = p/N:**

| Bin | M_Q | P+ | P− | F_ss | F_all | F_ss without rational models |
|---|---|---|---|---|---|---|
| [0.0, 0.1) | 0.1087 | 0.0892 | −0.1267 | 0.0677 | 0.0659 | 0.0679 |
| [0.1, 0.2) | −0.0445 | −0.0588 | 0.0312 | −0.037 | −0.0401 | −0.0372 |
| [0.2, 0.3) | −0.0427 | −0.0495 | 0.0363 | 0.0084 | 0.0065 | 0.0087 |
| [0.3, 0.4) | 0.0518 | 0.0394 | −0.0632 | 0.0395 | 0.0368 | 0.0398 |
| [0.4, 0.5) | 0.0778 | 0.0696 | −0.0854 | 0.0496 | 0.0503 | 0.0501 |
| [0.5, 0.6) | 0.0536 | 0.049 | −0.0578 | 0.0593 | 0.0609 | 0.0596 |
| [0.6, 0.7) | 0.0123 | 0.006 | −0.0182 | 0.0596 | 0.0631 | 0.0601 |
| [0.7, 0.8) | −0.0333 | −0.0366 | 0.0303 | 0.0515 | 0.0508 | 0.0515 |
| [0.8, 0.9) | −0.0546 | −0.0645 | 0.0456 | 0.0469 | 0.0487 | 0.0478 |
| [0.9, 1.0] | −0.0609 | −0.0544 | 0.0669 | 0.0384 | 0.0359 | 0.039 |

**Statistics and verdicts:**

| Statistic | Value | 95% interval |
|---|---|---|
| C1 mirror correlation corr(P+, P−) | −0.9824 | [−0.9861, −0.9771] |
| C1 sign changes of M_Q | 3 | – |
| C1 first bin of M_Q | 0.1087 | [0.1065, 0.1109] |
| **C1 verdict** | **reproduced** | |
| C2 ρ_ss (primary) | **0.5313** | **[0.4605, 0.5944]** |
| C2 ρ_all (all 3,973 classes, PARI's root number) | 0.519 | [0.463, 0.5684] |
| C2 ρ, semistable without rational models (2,779 classes) | 0.5273 | [0.4609, 0.5869] |
| C2 first bin of F_ss | 0.0677 | [0.0622, 0.0729] |
| **C2 verdict** | **consistent with the predicted flip** | |

### 3.3 What this shows and what it does not

Over Q, the profiles for w = +1 and w = −1 are near-perfect mirror images, and the w-weighted mean oscillates, changing sign three times. This reproduces the murmurations of He, Lee, Oliver and Pozdnyakov on the conductor range 1,000–4,999.

Over Q(√5), weighting a_P/√p by **+S** gives a profile that correlates positively with M_Q, and the whole interval lies above 0. Both profiles start with a clear positive first bin and dip negative in the second. Had the Q convention (−S) carried over, the correlation would have been negative. The conclusion survives three checks: using PARI's global root number over all classes, including those with additive primes (ρ_all = 0.519); dropping the 37 semistable classes with a model over Q, i.e. 2,816 minus 2,779, whose a_P are inherited from Q (ρ = 0.5273); and the smaller pilot range.

**This flip was expected.** Deligne's formula gives w = (−1)^d ∏ w_v. The data build had already confirmed, class by class, that PARI's global root number equals +S for every semistable class over Q(√5) and equals (−1)^rank for 4,602 of 4,605 classes. Murmurations are a correlation between a_P and the true root number, so once w = +S is known, F_ss is simply the murmuration profile over Q(√5) weighted by w. Its positive alignment with M_Q is the expected consequence, not independent evidence about the sign. What Part A adds is narrower: an explicit, pre-registered demonstration of the archimedean factor inside the murmuration pattern over a real quadratic field, using finite signs computed from the bad primes alone, plus a measure of how closely the two patterns agree on the p/N scale.

That agreement is only partial. ρ_ss ≈ 0.53 is far from 1. The two profiles agree at small x, but beyond x = 0.6 they part: M_Q turns negative from the bin [0.7, 0.8) onward, while F_ss stays positive in every bin from [0.2, 0.3) to the end. The humans had noticed the same pattern on the pilot range, and program.md raises the possibility that the pattern over Q(√5) sits on a different scale of p/N. The run did not test any other scale, so this question is open.

## 4. Part B: what the lab tried and what it learned

### 4.1 Budget and course of the loop

The lab used **25 of 40** val evaluations and **14 of 16** recheck seed runs. Three ideas were kept (git commits):

| Commit | Kept idea | Val AUC |
|---|---|---|
| 0f2c5f6 | `minus_sign_by_size`: #{p ≥ 5 : w_p = −1} − #{p ∈ {2, 3} : w_p = −1}, any exponent | 0.521045 → 0.529967 |
| 493c94d | `shape_empirical_bayes`: shape-conditioned empirical-Bayes table over local-type sign patterns, shrunk to the rule above | 0.529967 → 0.534418 |
| b342c92 | `additive_legendre_mod4`: the same table, with additive primes p ≥ 5 split by p mod 4 | 0.534418 → 0.539002 (final) |

The loop ended after four consecutive waves without a keep (waves 8–11), with 25 evaluations used, which the program allows.

### 4.2 Every val evaluation (from the ledger)

Δ is the paired difference from the current best at the time, with its 95% interval.

| # | Trial | Hypothesis (ledger note) | Val AUC [95% CI] | Δ vs best [95% CI] | Outcome |
|---|---|---|---|---|---|
| 0 | experiment.py (start) | simple rule: split multiplicative primes | 0.521045 [0.515417, 0.527059] | – | starting point |
| 1 | split_small_vs_large | split mult. primes p ≥ 5 minus split at 2, 3 | 0.524639 [0.517882, 0.531411] | +0.003594 [−0.002022, 0.009697] | not kept |
| 2 | minus_sign_by_size | all −1 signs p ≥ 5 minus −1 signs at 2, 3 | 0.529967 [0.523494, 0.536288] | +0.008922 [0.002887, 0.01536] | **kept** |
| 3 | clogit_sign_buckets | pairwise conditional logit on 12 sign buckets (size × type) | 0.535286 [0.529024, 0.541324] | +0.005320 [0.000999, 0.009903] vs minus_sign_by_size | rejected by Skeptic: gain vanished on probe |
| 4 | reverse_only_additive_23 | reverse −1 at 2, 3 only when additive | 0.52805 [0.522796, 0.5334] | −0.001917 [−0.005998, 0.00185] | not kept |
| 5 | drop_23 | ablation: −1 signs at p ≥ 5 only | 0.531232 [0.524664, 0.537555] | +0.001266 [−0.002839, 0.005404] | tie, not kept |
| 6 | inverse_log_weight | −1 signs weighted 1/log p | 0.528575 [0.521661, 0.535669] | −0.001392 [−0.004163, 0.001464] | not kept |
| 7 | clogit_three_counts | conditional logit on s5_mult, s5_add, s23 | 0.527943 [0.5213, 0.534501] | −0.002024 [−0.005126, 0.00102] | not kept |
| 8 | additive_residue_gate | additive −1 at p ≥ 5 counted only for p ≡ 3 mod 4 | 0.526021 [0.51896, 0.533265] | −0.003946 [−0.005955, −0.001969] | clean negative |
| 9 | log_p_weight | −1 signs weighted log p | 0.531175 [0.524514, 0.538051] | +0.001209 [−0.001739, 0.004005] | tie, not kept |
| 10 | conductor_context_hamming | tie-break by mean Hamming distance to other patterns at same N | 0.532688 [0.526319, 0.539288] | +0.002721 [0.001161, 0.004389] | rejected by Skeptic (see 4.3) |
| 11 | shape_empirical_bayes | shape-conditioned empirical-Bayes pattern log-odds, gated | 0.534418 [0.527242, 0.541302] | +0.004451 [0.000521, 0.008355] | **kept** |
| 12 | gated_pairwise_gbm | gated pairwise HistGBM on 11 sign/shape features | 0.529967 [0.523494, 0.536288] | 0.0 [0.0, 0.0] | gate fired; identical to parent |
| 13 | pooled_minus_counts | table pooled across shapes by −1 count signature | 0.536283 [0.529397, 0.542958] | +0.001865 [−0.001795, 0.005884] | tie, not kept |
| 14 | mask_signs_at_2_3 | table ignores signs at 2 and 3 | 0.533116 [0.526724, 0.539203] | −0.001302 [−0.004999, 0.002506] | not kept |
| 15 | merge_size_classes | size classes 2, 3, ≥ 5 only | 0.533452 [0.526297, 0.540315] | −0.000966 [−0.003921, 0.001694] | not kept |
| 16 | additive_type_by_p_mod_12 | tokens add p mod 12 at additive p ≥ 5 | 0.538055 [0.531974, 0.544189] | +0.003637 [0.00055, 0.007072] | rejected by Skeptic (see 4.3) |
| 17 | additive_legendre_mod4 | tokens add p mod 4 at additive p ≥ 5 | 0.539002 [0.532747, 0.545367] | +0.004584 [0.001881, 0.007528] | **kept (final)** |
| 18 | rohrlich_split_count_rule | 4-weight conditional logit, additive −1 split by p mod 4 | 0.53645 [0.530643, 0.542337] | +0.002032 [−0.00407, 0.008536] | not kept |
| 19 | rohrlich_deviation_rule | integer rule m5_mult + 3·D − 2·m23 | 0.536115 [0.530286, 0.542138] | −0.002888 [−0.008593, 0.003187] | not kept |
| 20 | exact_exponent_at_2_3 | exact exponent at 2 and 3 in tokens | 0.538091 [0.531209, 0.545126] | −0.000911 [−0.005192, 0.003337] | not kept |
| 21 | deviation_prior_nogate | table with Rohrlich-deviation prior, no gate | 0.542006 [0.536533, 0.547288] | +0.003003 [−0.000119, 0.006265] | near-miss |
| 22 | deviation_token_pooling | additive tokens as Rohrlich-deviation flag, residue pooled | 0.542221 [0.536629, 0.547582] | +0.003218 [−0.000069, 0.006586] | near-miss |
| 23 | largest_prime_token_p2gtN | size class 3 = p ≥ 5 with p² > N | 0.540603 [0.534535, 0.546494] | +0.0016 [−0.001007, 0.004233] | not kept |
| 24 | rohrlich_at_3 | Rohrlich deviation extended to 3² ∥ N | 0.542514 [0.536624, 0.547975] | +0.003512 [−0.000096, 0.007283] | near-miss |

Ideas that failed on the free probe and never reached val included the following. Probe AUCs are from the ledger. The current experiment scored 0.530432 on the probe before the p mod 4 keep and 0.5325 after it.

| Probe-only trial | Probe AUC | Comparison |
|---|---|---|
| hierarchical_backoff | 0.525533 | below the table's 0.530432 (falls back to the count rule) |
| count_rule_by_shape_group | 0.525533 | same |
| pairwise_bradley_terry | 0.53304 | below deviation_prior_nogate's 0.536112 |
| bagged_k | 0.534212 | below 0.536112 |
| hierarchical_shrinkage | 0.535717 | below 0.536112 |
| legendre_agreement_residual (γ·Σ w_p(M/p) at multiplicative p ≥ 5) | 0.531486 at best | every forced γ gave between 0.526463 and 0.531486, below the 0.5325 base |
| stack_deviation_p2gtN | 0.536237 | below deviation_token_pooling's 0.536268 |

### 4.3 What was learned about where the signal lives

**Parity rules out simple thresholds.** A rank 0 or rank 2 class has w = +1 = −∏ w_p, so every such class has an odd number of −1 local signs. Within a conductor, counts therefore move in steps of two, and one-dimensional thresholds on a single count are of little use.

**The size of p sets the direction.** A −1 sign at a prime p ≥ 5 points towards rank 2, while a −1 sign at p = 2 or 3 points towards rank 0. Counting all −1 signs at p ≥ 5 and subtracting those at 2 and 3, whatever the exponent, raised val AUC from 0.521045 to 0.529967. This was the largest single gain of the run, and it is a rule a number theorist can state in one sentence. Dropping 2 and 3 altogether (drop_23) and weighting by log p or 1/log p changed nothing measurable or did slightly worse.

**Flexible models overfit.** Conditional-logit models over sign buckets matched the metric exactly and looked good on val (clogit_sign_buckets, 0.535286). The Skeptic rejected that trial because its gain vanished on the probe: 0.524893 there, against 0.525533 for the count rule. The pairwise gradient-boosted model's internal gate fired, leaving it identical to its parent. A Bradley–Terry pair fit and several hierarchical shrinkage schemes also failed on the probe. What did help (shape_empirical_bayes) was a conservative, shrunk table of how often each exact pattern of local types carries rank 2, compared only among conductors of the same "shape".

**The Skeptic rejected two candidates that met the numeric keep rule.** conductor_context_hamming (0.532688) scored a class by how far its signs are from the other sign patterns at the same N. It depends on the harness's deduplicated set of patterns at a conductor, not on the class's own signs. additive_type_by_p_mod_12 (0.538055) gained only +0.0011 on the probe, and a placebo split by p mod 5 did as well. The probe scores were 0.5315 for p mod 12 against 0.530432 for the parent, and 0.531956 for the p mod 5 placebo.

**Rohrlich's formulas explain what helped.** For additive reduction at p ≥ 5, Rohrlich's formulas give the local root number in terms of Kodaira type (see the root-number sources in Section 9): w_p = (−1/p) for types I0\*, In\*, II and II\*; w_p = (−3/p) for IV and IV\*; and w_p = (−2/p) for III and III\*. A sign that differs from (−1/p) is therefore a marker of types III, III\*, IV or IV\*. The lab's evidence:

- Splitting additive tokens at p ≥ 5 by p mod 4, i.e. by the value of (−1/p), helped on val: +0.004584 [0.001881, 0.007528]. On the probe it scored 0.5325 against 0.530432.
- The Skeptic's placebo splits stayed flat on the probe. Hash-based splits gave 0.52886 and 0.529958, and the other controls fell between 0.530163 and 0.53233, against 0.5325 for the p mod 4 split. Splitting by p mod 3 alone hurt (0.529755).
- A four-weight count rule was fitted on the probe's training part. It gave s5_mult +0.0993, additive −1 at p ≡ 1 mod 4 **+0.4006**, additive −1 at p ≡ 3 mod 4 **−0.2404**, and s23 −0.1779. At p ≡ 1 mod 4, (−1/p) = +1, so a −1 sign there is a deviation from (−1/p). At p ≡ 3 mod 4, (−1/p) = −1, so a −1 sign is the expected value and a +1 sign is the deviation. What matters is therefore the deviation, which marks types III/III\*/IV/IV\*.
- An unfitted integer rule built on this reading, m5_mult + 3·D − 2·m23, reached val 0.536115. Here D counts the deviations from (−1/p) at additive p ≥ 5. That is above minus_sign_by_size but below the table it was compared with.

Three later trials built the deviation flag into the table: deviation_prior_nogate (0.542006, Δ +0.003003 [−0.000119, 0.006265]), deviation_token_pooling (0.542221, Δ +0.003218 [−0.000069, 0.006586]), and rohrlich_at_3, which extended the idea to 3² ∥ N (0.542514, Δ +0.003512 [−0.000096, 0.007283]). Each beat the best by more than 0.002, but **each paired interval includes 0**, so none met the keep rule. The val set had also been used to select among them, so even these point gains would be optimistic. largest_prime_token_p2gtN (0.540603, +0.0016) fell short on both counts.

**Clean negatives.** Counting additive −1 signs only at p ≡ 3 mod 4 (additive_residue_gate) is significantly worse: −0.003946 [−0.005955, −0.001969]. Masking the signs at 2 and 3 inside the table, merging the size classes, and using exact exponents at 2 and 3 all tied or lost. Adding Legendre-symbol agreement at multiplicative primes (legendre_agreement_residual) hurt for every γ tried on the probe.

## 5. The final experiment in plain words

The promoted `experiment.py` (additive_legendre_mod4) works in three layers.

1. **A counting rule.** Start from r = (number of bad primes p ≥ 5 with w_p = −1) − (number of bad primes p = 2 or 3 with w_p = −1), counting every exponent.
2. **A refined description of each local factor.** Each bad prime becomes a token with four fields: its size class (p = 2, p = 3, 5 ≤ p ≤ 97, or p ≥ 101); whether it is multiplicative (e = 1) or additive (e ≥ 2); for additive primes p ≥ 5 only, p mod 4, i.e. the value of (−1/p); and its sign w_p. A class's *pattern* is its sorted list of tokens. Its *shape* is the same list without the signs, and every class of a given conductor has the same shape.
3. **A cautious correction from training data.** The training conductors are used, but only those with both ranks present. For each pattern the experiment computes the rank 2 log-odds log((n2 + ½)/(n0 + ½)), centres it on its shape's mean, and rescales it to the units of r through a weighted fit. The score is r pulled towards this estimate with weight n/(n + K), where n is the number of training classes with that pattern. Patterns never seen in training keep r. K is chosen from {10, 30, 100, 300} by fitting on the lower two-thirds of the training conductors and scoring the rest. If no K beats r there by at least 0.002, the experiment returns r unchanged. The method is deterministic, and the seed is ignored.

In one sentence: *count the −1 signs at primes p ≥ 5, subtract those at 2 and 3, then nudge the score by how often the exact pattern of local types carried rank 2 among training conductors of the same shape, where the only arithmetic beyond the size of p is whether an additive prime p ≥ 5 is 1 or 3 mod 4.* By Rohrlich's formulas, that last distinction lets the table tell the generic additive types (sign equal to (−1/p)) from types III/III\*/IV/IV\*. In the final run the experiment was refitted on train and val together. `final_test.json` does not record whether the internal gate fired.

## 6. Held-out results (test, N 400,000–499,999; from `final_test.json`)

Test has 209,944 classes (59,548 of rank 2), giving 775,454 within-conductor pairs over 18,316 conductors.

| Score | Test AUC | 95% CI | z | one-sided p | permutation p | Verdict |
|---|---|---|---|---|---|---|
| **H_B1**: simple rule (split multiplicative count) | 0.521744 | [0.516516, 0.52729] | 8.591 | 4.32e-18 | 0.0005 | **supported** |
| **H_B2**: promoted experiment | 0.542611 | [0.535592, 0.549993] | 15.114 | 6.57e-52 | 0.0005 | **supported** |
| Experiment minus simple rule (paired) | +0.020866 | [0.014059, 0.027839] | – | – | – | – |
| Positive control: Nagao-type sum over a_p, p < 100 | 0.963781 | [0.962087, 0.965424] | 160.017 | – | – | – |

The 0.0005 permutation p-values come from 2,000 permutations, so the smallest possible value is 1/2001 ≈ 0.0005. The test numbers agree closely with val: 0.521045 for the simple rule and 0.539002 for the experiment there. Both pre-registered hypotheses hold. The paired gain of the experiment over the simple rule is about two AUC points, and its interval excludes 0. Even so, the sign signal is an order of magnitude weaker than the a_p signal shown by the control.

## 7. What is expected and what is new

**Expected.** Part A over Q reproduces the murmurations of He, Lee, Oliver and Pozdnyakov. The flip over Q(√5) follows from Deligne's formula and from the parity checks in the data build. Its confirmation here is a demonstration, not a discovery.

**New, as far as the Scout's searches went.**

- *Part A.* The Scout found no published murmurations over real quadratic fields or for Hilbert modular forms. So the observation that murmurations over Q(√5), weighted by +(product of the finite signs), align positively with those over Q (ρ_ss = 0.5313 [0.4605, 0.5944]) was not found in the literature. The Scout's searches found "Variations on murmurations" (arXiv:2505.01093), which works over Q. program.md describes it as weighting murmurations by products of local root numbers over sets of places, but the Scout could not confirm what it shows about local root numbers.
- *Part B.* The Scout found no published conductor-matched study of local signs against rank. The run shows that a within-conductor dependence exists on held-out conductors, but it is weak: AUC about 0.54 against about 0.96 for the a_p control. The main interpretive finding is new as far as the Scout's searches went: the useful information sits in the size of p (−1 at p ≥ 5 points towards rank 2, −1 at 2 or 3 towards rank 0) and in additive primes whose sign departs from (−1/p), i.e. Kodaira types III/III\*/IV/IV\* by Rohrlich's formulas. The reading came out of exploratory selection on val, and the trials that encoded it most directly were near-misses whose intervals include 0. It should be treated as a hypothesis for a fresh test, not a confirmed result. Related work on rank and local data that the Scout did find concerns Tamagawa numbers and positive rank, and Mestre–Nagao sums with learned or neural refinements (Section 9). Those papers use a_p or Tamagawa data, not conductor-matched local signs.

## 8. Limits

- **Ranks as recorded.** Ranks are taken from Cremona's tables and the LMFDB. Over Q(√5), three of the 4,605 classes have only rank bounds.
- **A small sample over Q(√5), with Galois-conjugate pairs.** C2 rests on 2,816 semistable classes over 451 conductor norms; the pilot used 517 classes over 128 norms. Galois-conjugate classes are not independent, which is why the bootstrap resamples whole norms. The result depends on one snapshot of the LMFDB database of curves over Q(√5), downloaded 2026-10-08.
- **Small conductors.** The Part A ranges, pilot and confirmatory, cover only conductors and norms below 5,000.
- **The choice of scale.** Both profiles were drawn against p/N with N the conductor (norm). The two profiles part beyond x = 0.6, which may mean the pattern over Q(√5) lives on another scale. No other scale was tested.
- **Part A's correlation is modest.** ρ_ss ≈ 0.53 across ten bins shows the expected sign alignment, not a close match of shapes.
- **The Part B effect is small.** Test AUC is 0.542611, against 0.963781 for the a_p control.
- **Many looks at val.** There were 25 val evaluations and several near-misses, so the val numbers of the selected experiment, and especially of the near-misses, are optimistic. Only the single test run is free of selection.
- **Earlier looks by the humans.** Before the run the humans looked at the training conductors (an exploratory within-conductor AUC of 0.508, z = 5.7, for the split count; 0.498 with log(p)/p weights). They also saw the pilot murmuration numbers and the val numbers of the simple rule (AUC 0.521) and of one trial model. The test conductors had never been scored.
- **Snapshot.** All results are tied to the fingerprinted data snapshot (data SHA-256 `42345fcb…a696c8`).
- **Disclosed deviation.** In wave 1 the Planner ran a read-only script directly on the training rows (N < 300,000) of `lab/langlands/data`, producing train-only per-bucket AUCs. Afterwards all agents were told to use only the harness. No val or test conductor was touched outside `evaluate`, `recheck` and `final`. Some experimenters also ran throwaway diagnostic copies through the free probe; these appear in the ledger as probe rows (for example tmp_lar_force and the pairwise_bradley_terry_tmp files).
- **Citation uncertainty.** The Scout attributed the Inventiones paper "Murmurations" (doi:10.1007/s00222-025-01347-8) inconsistently, first to He, Lee, Oliver and Pozdnyakov and later to Zubrilina. Its authorship is unconfirmed here. The content of "Variations on murmurations" regarding local root numbers was not confirmed.

## 9. Sources

**The program**
- P. Alesso, "Euler's identity and the Langlands program", research memo, 2026, research direction R1 (no public link).

**Data and software**
- J. Cremona, elliptic curve data: https://github.com/JohnCremona/ecdata (commit 25cec5e).
- The LMFDB, elliptic curves over Q(√5) (file downloaded 2026-10-08): https://www.lmfdb.org
- PARI/GP 2.17.2: https://pari.math.u-bordeaux.fr

**Murmurations**
- Y.-H. He, K.-H. Lee, T. Oliver, A. Pozdnyakov, "Murmurations of elliptic curves", arXiv:2204.10140 (https://arxiv.org/abs/2204.10140); Experimental Mathematics, 2024, https://doi.org/10.1080/10586458.2024.2382361
- "Murmurations", Inventiones Mathematicae, 2025, https://doi.org/10.1007/s00222-025-01347-8 (authorship uncertain; see Limits).
- N. Zubrilina, "Distribution of local signs of modular forms and murmurations of Fourier coefficients", Mathematika, 2025, https://doi.org/10.1112/mtk.70028
- "Murmurations and explicit formulas", arXiv:2306.10425, https://arxiv.org/abs/2306.10425
- "Variations on murmurations", arXiv:2505.01093 (https://arxiv.org/abs/2505.01093), https://doi.org/10.1142/s2810939225400052 (content on local root numbers not confirmed).
- Related murmuration variants: arXiv:2607.20853 (https://arxiv.org/abs/2607.20853), arXiv:2608.01337 (https://arxiv.org/abs/2608.01337), arXiv:2506.01640 (https://arxiv.org/abs/2506.01640), arXiv:2504.09944 (https://arxiv.org/abs/2504.09944), arXiv:2603.22807 (https://arxiv.org/abs/2603.22807), https://doi.org/10.2140/ant.2026.20.299, https://doi.org/10.1017/s0305004125101515

**Root numbers, local root numbers and parity** (cited for Rohrlich's local root number formulas)
- "Root numbers and parity", Crelle, 2011, https://doi.org/10.1515/crelle.2011.060
- Root number formulas: https://doi.org/10.1007/bf02567689 (1994); https://doi.org/10.1112/blms/bdn034 (2008); arXiv:1502.04251 (https://arxiv.org/abs/1502.04251)

**Rank and local or a_p data**
- "Tamagawa numbers and positive rank of elliptic curves", 2026, https://doi.org/10.1017/s0305004126101947
- M. Kazalicki, D. Vlah, https://doi.org/10.1007/s40993-023-00462-w
- Learned Mestre–Nagao sums, https://doi.org/10.1142/s2810939225400040
- CNN and Mestre–Nagao sums, https://doi.org/10.1007/s40993-026-00784-5

**Further sources found by the Scout**
- https://doi.org/10.1112/s1461157016000152
- https://doi.org/10.1142/9789813272880_0060
- https://doi.org/10.1016/j.jsc.2022.08.017

---

## 2. Final results (from `final_part_A.json` and `final_test.json`; `harness.py final` was run once)

**Part A**

| | Verdict | Main statistic | Supporting values |
|---|---|---|---|
| **C1** (over Q, N 1,000–4,999; 14,851 classes, 2,730 conductors) | **reproduced** | mirror corr(P+, P−) −0.9824 [−0.9861, −0.9771] | 3 sign changes of M_Q; first bin of M_Q 0.1087 [0.1065, 0.1109] |
| **C2** (over Q(√5), norm 1,000–4,999; 2,816 semistable classes, 451 norms) | **consistent with the predicted flip** | **ρ_ss 0.5313, 95% interval [0.4605, 0.5944]** | ρ_all 0.519 [0.463, 0.5684]; without rational models 0.5273 [0.4609, 0.5869]; first bin of F_ss 0.0677 [0.0622, 0.0729] |

**Part B** (test N 400,000–499,999: 209,944 classes, 59,548 of rank 2; 775,454 pairs over 18,316 conductors)

| | AUC [95% CI] | z | one-sided p | permutation p | Verdict |
|---|---|---|---|---|---|
| **H_B1** (simple rule, split multiplicative count) | 0.521744 [0.516516, 0.52729] | 8.591 | 4.32e-18 | 0.0005 | **supported** |
| **H_B2** (promoted experiment) | 0.542611 [0.535592, 0.549993] | 15.114 | 6.57e-52 | 0.0005 | **supported** |
| Positive control nagao_ap25 | 0.963781 [0.962087, 0.965424] | 160.017 | – | – | – |

- **Experiment minus simple rule (paired):** +0.020866 [0.014059, 0.027839].
- **Budget:** 25 of 40 val evaluations and 14 of 16 recheck seed runs were used.
- **Path of the best val AUC:** 0.521045 → 0.529967 → 0.534418 → 0.539002.

## 3. lab/langlands/experiment.py

```python
"""Trial additive_legendre_mod4: shape_empirical_bayes with additive p >= 5
tokens split by p mod 4.

Trial change vs. the parent: every token with p >= 5 and e == 2 (additive)
carries an extra field p % 4 (1 or 3), in both the shape and the pattern;
all other tokens carry a fixed placeholder. Hypothesis: the only arithmetic
in the mod-12 split is (-1/p) (Rohrlich: w_p = (-1/p) for I0*, In*, II, II*),
so a -1 at additive p = 1 mod 4 flags the rarer types III/III*/IV/IV*.

Parent docstring follows.

score(train, rows, seed) returns one number per row in `rows`; a higher number
means "more likely rank 2". Each row is {"N": conductor, "bad": [[p, e, w_p],
...]} where p runs over the primes dividing N, e is the exponent of p in N
and w_p is the local root number (+1 or -1). `train` holds the same fields
plus "rank" (0 or 2) for every class with a smaller conductor.

The harness compares only classes that share a conductor, so a score helps
only through what it does with the signs w_p.

Base rule r: the number of bad primes p >= 5 with w_p = -1 minus the number
of bad primes p in {2, 3} with w_p = -1, every exponent.

Change: each bad prime becomes a token (size class of p in {2}, {3}, 5-97,
>= 101; min(e, 2); w_p). A class's sign pattern is the sorted tuple of its
tokens and its conductor shape is the same tuple without the signs (all
classes of one conductor share a shape). From train, using only conductors
that have both ranks, each pattern gets a rank-2 log-odds
log((n2 + 0.5) / (n0 + 0.5)) centred on the class-weighted mean of its
shape (est). The score is r + n/(n+K) * (c*est - (r - mean r of the shape)),
with c = 1/slope of a weighted fit of est on centred r, n = n2 + n0; unseen
patterns keep r. K in {10, 30, 100, 300} is chosen by fitting on train
conductors below 2/3 of the largest train N and measuring within-conductor
AUC on the rest; then the table is refit on all of train. Gate: if the best
internal AUC does not beat r's internal AUC by at least 0.002, the score is
r unchanged. Deterministic; the seed is ignored.
Hypothesis: the effect of a -1 sign at p >= 5 depends on which other local
types share the conductor, which only a shape-conditioned table captures.
"""

import math
from bisect import bisect_left, bisect_right
from collections import defaultdict

KS = (10.0, 30.0, 100.0, 300.0)
GATE = 0.002


def base_r(bad):
    s = 0
    for p, e, w in bad:
        if w == -1:
            s += 1 if p >= 5 else -1
    return float(s)


def size_class(p):
    if p == 2:
        return 0
    if p == 3:
        return 1
    if p <= 97:
        return 2
    return 3


def keys(bad):
    toks = sorted((size_class(p), min(e, 2),
                   (p % 4) if (p >= 5 and e == 2) else -1, w)
                  for p, e, w in bad)
    pattern = tuple(toks)
    shape = tuple((a, b, m) for a, b, m, c in toks)
    return shape, pattern


def fit_table(classes):
    """classes: list of (N, shape, pattern, r, rank). Returns model dict."""
    by_n = defaultdict(set)
    for N, sh, pa, r, rk in classes:
        by_n[N].add(rk)
    both = set(N for N, s in by_n.items() if len(s) == 2)
    cnt = defaultdict(lambda: [0, 0])
    rval = {}
    for N, sh, pa, r, rk in classes:
        if N not in both:
            continue
        c = cnt[(sh, pa)]
        if rk == 2:
            c[1] += 1
        else:
            c[0] += 1
        rval[(sh, pa)] = r
    # shape means of log-odds and r (class weighted)
    sw = defaultdict(float)
    slo = defaultdict(float)
    sr = defaultdict(float)
    lo = {}
    for key, (n0, n2) in cnt.items():
        sh = key[0]
        n = n0 + n2
        v = math.log((n2 + 0.5) / (n0 + 0.5))
        lo[key] = v
        sw[sh] += n
        slo[sh] += n * v
        sr[sh] += n * rval[key]
    est = {}
    rc = {}
    wts = {}
    for key, v in lo.items():
        sh = key[0]
        est[key] = v - slo[sh] / sw[sh]
        rc[key] = rval[key] - sr[sh] / sw[sh]
        wts[key] = float(sum(cnt[key]))
    # weighted least squares of est on centred r (both already centred per shape)
    sxy = sum(wts[k] * rc[k] * est[k] for k in est)
    sxx = sum(wts[k] * rc[k] * rc[k] for k in est)
    syy = sum(wts[k] * est[k] * est[k] for k in est)
    slope = sxy / sxx if sxx > 0 else 0.0
    if slope > 1e-9:
        c = 1.0 / slope
    elif syy > 0 and sxx > 0:
        c = math.sqrt(sxx / syy)
    else:
        c = 0.0
    rbar = dict((sh, sr[sh] / sw[sh]) for sh in sw)
    return {"est": est, "n": wts, "c": c, "rbar": rbar}


def apply_model(model, sh, pa, r, K):
    key = (sh, pa)
    if key not in model["est"]:
        return r
    n = model["n"][key]
    lam = n / (n + K)
    rcen = r - model["rbar"][sh]
    return r + lam * (model["c"] * model["est"][key] - rcen)


def within_auc(items):
    """items: list of (N, score, rank). Pooled within-conductor AUC."""
    by_n = defaultdict(lambda: ([], []))
    for N, s, rk in items:
        if rk == 2:
            by_n[N][1].append(s)
        else:
            by_n[N][0].append(s)
    num = 0.0
    den = 0.0
    for N, (s0, s2) in by_n.items():
        if not s0 or not s2:
            continue
        s0.sort()
        n0 = len(s0)
        for x in s2:
            lo_i = bisect_left(s0, x)
            hi_i = bisect_right(s0, x)
            num += lo_i + 0.5 * (hi_i - lo_i)
        den += n0 * len(s2)
    return num / den if den > 0 else 0.5


def score(train, rows, seed):
    """Shape-conditioned empirical-Bayes log-odds shrunk toward r, gated."""
    classes = []
    for t in train:
        sh, pa = keys(t["bad"])
        classes.append((t["N"], sh, pa, base_r(t["bad"]), t["rank"]))
    rs = [base_r(row["bad"]) for row in rows]
    if not classes:
        return rs
    maxn = max(c[0] for c in classes)
    split = maxn * 2.0 / 3.0
    fit_part = [c for c in classes if c[0] < split]
    hold = [c for c in classes if c[0] >= split]
    model = fit_table(fit_part)
    base_auc = within_auc([(c[0], c[3], c[4]) for c in hold])
    best_k = None
    best_auc = -1.0
    for K in KS:
        a = within_auc([(c[0], apply_model(model, c[1], c[2], c[3], K), c[4])
                        for c in hold])
        if a > best_auc:
            best_auc = a
            best_k = K
    if best_auc < base_auc + GATE:
        return rs
    model = fit_table(classes)
    out = []
    for row, r in zip(rows, rs):
        sh, pa = keys(row["bad"])
        out.append(float(apply_model(model, sh, pa, r, best_k)))
    return out
```
