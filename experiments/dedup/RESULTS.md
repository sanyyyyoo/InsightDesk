# Dedup v1: offline experiments on case representation and retrieval

Branch `dedup-experiments`, created from the frozen `data-recalibration`
baseline (`f9fcf73`). The baseline code is unchanged. Everything runs
offline in memory: no Supabase or Pinecone reads or writes.

- Harness: `replay_lab.py` (same replay logic and case metrics as
  `scraper/evaluate_threshold_replay.py`, plus pairwise clustering P/R/F1,
  retrieval recall, and arrival-order runs)
- Runs: `run_experiments.py` (round 1), `run_template_check.py` (round 2)
- Raw results: `results/grid.csv`, `results/order_sensitivity.csv`,
  `results/templates_removed.csv`

Data: `data/synthetic_ground_truth.csv` (488 complaints, 32 issue ids).

## 0. Baseline reproduced exactly

`first` representative, Top-5, threshold 0.5858 gives **107 cases, 18
contaminated, 35 cross-issue assignments**. This is identical to
`data/threshold_replay_summary.csv`, so every comparison below uses the
same setup as Dedup v1.

## 1. Retrieval is not the bottleneck

| Top-K | Retrieval recall* | Cases | Cross-issue | Pair precision | Pair recall |
|---|---:|---:|---:|---:|---:|
| **5** | 0.976 | 107 | **35** | **0.834** | 0.217 |
| 10 | 0.987 | 104 | 42 | 0.795 | 0.216 |
| 20 | 0.989 | 101 | 50 | 0.749 | 0.215 |

\*Retrieval recall: of the complaints whose issue already has a case, the
share where a case of that issue is in the candidate set.

Top-5 already surfaces a correct-issue case 97.6% of the time. Larger K
adds almost nothing to recall but gives the cross-encoder more chances to
cross the threshold, so cross-issue merges rise (35 → 50).
**Keep Top-5.**

## 2. Case representation: no significant gain (round 1, original data)

k = 5, threshold 0.5858, mean ± sd over 4 arrival orders (original + 3 shuffles):

| Representative | Cases | Cross-issue | Pair precision | Pair recall | Largest-case coverage |
|---|---:|---:|---:|---:|---:|
| **first (v1)** | 109.3 ± 2.2 | **33.0 ± 2.8** | **0.828 ± 0.028** | **0.207 ± 0.010** | **0.364 ± 0.019** |
| medoid | 110.0 ± 1.6 | 36.5 ± 1.9 | 0.802 ± 0.021 | 0.203 ± 0.008 | 0.359 ± 0.015 |
| centroid | 109.8 ± 1.7 | 36.5 ± 5.7 | 0.800 ± 0.035 | 0.202 ± 0.008 | 0.356 ± 0.011 |
| multi (best of 3 members) | 72.8 ± 9.4 | 111 ± 44 | 0.449 ± 0.202 | 0.320 ± 0.020 | 0.452 ± 0.008 |

- Medoid and centroid are **within order noise** of the first complaint
  (differences are smaller than the spread between arrival orders).
- Multi-representative is **harmful**: taking the best match over several
  members chains unrelated complaints together (up to 226 cross-issue
  assignments at 0.50).
- At a stricter threshold (0.70), medoid and centroid are slightly purer
  (8 and 6 cross-issue vs 12 for first) but split issues further (127–129
  cases).

## 3. The evaluation data is the bottleneck (round 2)

The synthetic generator adds the same stock sentences to complaints of
**any** issue: 58% end with one of 4 closers (e.g. "Happening consistently,
not a one-off."), and ~150 start with "Update:", "Following up on this:"
and similar. Round 2 removes them from the evaluation data only; the
production pipeline is unchanged.

k = 5, threshold 0.5858, mean ± sd over 4 arrival orders:

| Evaluation data | Representative | Cases | Cross-issue | Pair precision | Pair recall |
|---|---|---:|---:|---:|---:|
| with stock phrases (v1) | first | 109.3 ± 2.2 | 33.0 ± 2.8 | 0.828 ± 0.028 | 0.207 ± 0.010 |
| **stock phrases removed** | **first** | **96.0 ± 1.6** | **20.3 ± 4.3** | **0.926 ± 0.020** | **0.268 ± 0.005** |
| stock phrases removed | medoid | 100.0 ± 0.8 | 20.3 ± 3.3 | 0.917 ± 0.018 | 0.247 ± 0.003 |
| stock phrases removed | centroid | 99.8 ± 1.3 | 21.3 ± 5.0 | 0.911 ± 0.027 | 0.247 ± 0.003 |

In the original arrival order, at 0.5858 with stock phrases removed:
**contaminated cases 18 → 6**, **pure-case rate 0.83 → 0.94**, and
cross-issue assignments 35 → 24.

With the phrases removed, the first-complaint representative still
matches or beats medoid and centroid.

Threshold sweep, first representative, stock phrases removed (original order):

| Threshold | Cases | Contaminated | Cross-issue | Pair P | Pair R | Pair F1 | Largest-case coverage |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.30 | 50 | 13 | 55 | 0.787 | 0.644 | 0.709 | 0.671 |
| 0.40 | 68 | 7 | 40 | 0.816 | 0.398 | 0.535 | 0.570 |
| 0.50 | 82 | 7 | 29 | 0.861 | 0.334 | 0.482 | 0.481 |
| 0.5858 | 96 | 6 | 24 | 0.908 | 0.265 | 0.410 | 0.389 |
| 0.70 | 112 | 2 | 8 | 0.964 | 0.207 | 0.341 | 0.326 |

## 4. Conclusions

1. **Finalise the first complaint as the case representative.** No
   alternative beats it beyond arrival-order noise, it is the simplest, and
   it is fully explainable. Report medoid and centroid as tested
   alternatives with no significant gain, and multi-representative as
   harmful (chaining).
2. **Keep Top-5 retrieval.** Retrieval recall is already 97.6%; a larger K
   only adds false merges.
3. **Regenerate the synthetic data without shared stock phrases** (or vary
   them per issue), then **recalibrate the threshold** on it. The stock
   phrases alone account for about a third of the cross-issue errors and
   two-thirds of the contaminated cases. Do not strip them in production:
   they are a property of the generator, not of real complaints.
4. **Recall stays low (pairwise ≈ 0.27) even on clean data:** each issue
   still splits into about 3 cases. The remaining gap is in the scorer and
   the labels, not in representation or retrieval. Issue ids group
   different symptoms (e.g. "MFA enrollment times out" vs "authenticator
   won't pair"), which even a human might not merge. Next steps:
   - issue-family vs case-level labels (split broad issue ids into
     sub-issues), with human adjudication of a sample;
   - a three-way decision (merge / uncertain / new) around the threshold,
     sending the uncertain band to operator review;
   - fine-tuning the cross-encoder on complaint pairs, then recalibrating.

## 5. E4: text normalisation before dedup (held-out issues)

Protocol (`compare_pipelines.py --text <mode>`): 5 random splits of the 32
issues into halves; each pipeline's threshold is picked on one half
(best pairwise F1 with precision >= 0.90) and scored on the other half,
then swapped: 10 held-out runs per row. Each held-out half has 16 issues.

| Text mode | LLM calls | Pipeline | Pair P | Pair R | Pair F1 | Cases (16 issues) | Contaminated |
|---|---:|---|---:|---:|---:|---:|---:|
| raw | 0 | v1 (CE) | 0.900 ± 0.064 | 0.215 ± 0.027 | 0.345 ± 0.031 | 56.2 | 5.4 |
| raw | 0 | online-cos | 0.917 ± 0.048 | 0.462 ± 0.051 | 0.612 ± 0.037 | 34.4 | 4.8 |
| raw | 0 | batch-cos | 0.891 ± 0.109 | 0.697 ± 0.075 | 0.774 ± 0.038 | 22.7 | 2.1 |
| boilerplate (E4a) | 0 | v1 (CE) | 0.895 ± 0.118 | 0.472 ± 0.162 | 0.593 ± 0.140 | 36.3 | 2.5 |
| boilerplate (E4a) | 0 | online-cos | 0.900 ± 0.102 | 0.694 ± 0.162 | 0.765 ± 0.091 | 23.9 | 2.4 |
| boilerplate (E4a) | 0 | batch-cos | 0.893 ± 0.071 | 0.775 ± 0.065 | 0.825 ± 0.024 | 19.4 | 2.5 |
| LLM issue statement (E4b) | 50 | v1 (CE) | 0.880 ± 0.119 | 0.516 ± 0.074 | 0.640 ± 0.034 | 31.5 | 2.5 |
| LLM issue statement (E4b) | 50 | online-cos | 0.917 ± 0.064 | 0.736 ± 0.106 | 0.810 ± 0.053 | 22.4 | 3.0 |
| LLM issue statement (E4b) | 50 | batch-cos | 0.906 ± 0.084 | 0.860 ± 0.079 | 0.877 ± 0.047 | 18.8 | 1.8 |

- E4a (label-free boilerplate suppression) removed exactly the generator's
  10 stock phrases and nothing else: its cleaned text is identical to the
  hand-stripped text for all 488 complaints, so its rows equal the
  `stripped` run (`pipelines_all-MiniLM-L6-v2_stripped.csv`).
- E4b used 50 Groq calls (10 complaints per call, 2 retries), cached in
  `results/llm_normalized.csv`.
- Independent check: `verify_results.py` rebuilds every online-cos and
  batch-cos run and recounts pairs with scikit-learn's
  `pair_confusion_matrix`: 80/80 runs match (`results/verify_all.log`).
- Held-out precision varies a lot between splits (sd 0.06-0.12, worst
  single run 0.64), i.e. a threshold tuned on some issues does not always
  transfer to others. This is the case for the uncertain band + review.
- Caveat: the synthetic filler is repeated verbatim, which makes E4a easy.
  Real complaints vary their filler, so E4a vs E4b must be repeated on
  real data before drawing conclusions.
