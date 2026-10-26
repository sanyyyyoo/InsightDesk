# InsightDesk paper: sentence-by-sentence audit

> **Status (2026-10-27):** the findings below were fixed. Missing results were re-run or recomputed (`experiments/dedup/results/llm_batch_shuffle_results.txt`, `llm_labeller_pairwise.txt`, `paper_checks.txt`, `spike_v2_selection_results.txt`, `reports/topics/topic_coherence_results.txt`); the app now implements the paper's boilerplate cleaning, 5,000-character truncation, Groq JSON mode, cached judge decisions, re-joining and the vague alarm on by default, the department override, the General Support fallback and an escalation record; the paper text was corrected and rebuilt. The audit is kept as the record of what was found.

**Audited text:** `reports/paper/InsightDesk_paper.docx` (current version). It contains 274 sentences, 26 table rows and 29 references, numbered S0–S369; section headings are dividers, not claims.
**Evidence searched (all paths are relative to `D:\PBL\`):**
- `InsightDesk-dedup/experiments/dedup/` (experiment code, `results/` with 344 result and rule files, `labelling/`, `labels/`)
- `InsightDesk-dedup/data/external/` (datasets)
- `InsightDesk-claude-review/backend/`, `web/src/`, `tests/` (the app)
- `InsightDesk-claude-review/reports/` (baselines, Endava, topics, replay/RCA), excluding `reports/paper` and `reports/ppt`, which are derived from the paper and would be circular (the one exception: the team-made deck title slide, used only for the author, guide and institute names)
- `InsightDesk-claude-review/research_notes/` and the two literature-review reports (for literature claims)

**How it was checked:**
- Every number was searched across the evidence files, and each match was read by hand.
- Where no file prints a number, I recomputed it read-only from the saved data or ran the project's own scripts without writing over their outputs, and classified it as **Inference**.
- Statements with no local evidence are **Hallucination**, as your rule requires. For literature references this means "not backed by any local file", not necessarily "false".

**Totals:** 189 Fact · 122 Inference · 21 Hallucination (of 332 audited items).

## Most important findings (fix before submission)

**Unsupported (Hallucination):**
1. **S230 / S361: "shuffling the input order leaves only 54% of its grouped pairs intact".** No saved experiment shows this. The only saved stability test shows the opposite: identical prompts give 99.5% identical pairs (`results/llm_batch_baseline_A.txt:7`). The 54% appears only in Claude's memory note. This is the paper's main argument against the batch-LLM baseline.
2. **S21, S249, S250: "21 words on average".** The measured mean is 28.1 words (338 scored reviews) or 25.8 (all 450); the median is 19–20.
3. **S229: "LLM labellers … precision 0.68–0.71".** No result file holds this (memory note only).
4. **S242: "only 2 held-out Play Store reviews scored above t_high".** No file reports this, and `results/review_stats.txt:1` shows 20 auto-joins at or above t_high.
5. **S153: "(p = 0.01 gave 3.35 on bug reports)".** This number is not in any file. The selection grid that does exist (`spike_detector_v2_rule.md:16-20`) was written for the per-case detector, not the vague alarm.
6. **S97, S108, S114: the running example's S* = 0.71 and its outcome are illustrative values.** Label them as illustrative in the text.
7. **S7: "Academic Year 2025–26"** and **S17: "hundreds of complaints a day"** have no source.
8. **References [6], [7], [9], [12], [17], [18], [24], [29]** are not in the local literature notes. They may be real, but nothing local backs them.

**Wrong or misleading (Inference, with a contradiction):**
9. **S101, S105, S195: the thresholds.** The paper says t_high 0.8306 and t_low 0.26 were "set once on a labelled tuning half". In fact:
   - These two values come from calibrating on all 338 Play Store reviews (the `ext_playstore` runs, `e5_three_way.py:870-872`). That set includes the halves used for scoring.
   - The held-out Play Store results use thresholds recalibrated on each half: t_high 0.70–0.77 and t_low 0.24–0.30 (`results/sensitivity_results.txt:72`).
   - So the headline P 0.83 was not measured at 0.8306.
10. **S82: "Text beyond 5,000 characters is truncated".** The API rejects such text (`backend/models/complaint.py:13`, `max_length=5000`); only the replay script truncates.
11. **S83–S86: boilerplate suppression** (8 complaints, cosine 0.90, mean below 0.30) exists only in the experiment harness (`normalize.py:100-102`). The deployed `clean_text` (`backend/services/preprocess.py:174`) does not do it.
12. **S112, S164, S174: "JSON mode" and "every decision is cached".** Both are true for experiments and replays. The live app calls Groq without `response_format` and does not cache judge decisions (`backend/llm/provider.py:83-105`).
13. **S45: entity-matching F1 "89.6–98.4".** The local source table gives 76.4–98.4 (Amazon-Google 76.38 is left out).
14. **S178, S193: κ = 0.74 is the second round, after a re-check.** The first round gave 0.568 (`build_recheck_sheet.py:2`, reproduced). I reproduced 0.743 [0.630, 0.837] from `labelling/team_labels_round2.csv`, but no file stores the printed value.
15. **S254: "Baselines tuned on Firefox itself".** The Firefox CLAP and BERTopic numbers use the published or default settings, not settings tuned on Firefox.
16. **S266: "h = 2 was chosen on … a first Firefox sample".** The rule says Firefox sample 2 (`cusum_confirm_rule.md:3-5`).
17. **S363 (Table III): "Firefox, 3 samples … 0.87–0.96".** Firefox precision is 0.92–0.96; the 0.87 is Thunderbird's.
18. **S368: "BM25F 0.41–0.44".** The local values are BM25 0.40–0.44 and REP-full 0.43–0.44, so neither matches exactly.
19. **S289: "pairwise precision there (0.61–0.64)".** For the unseen company it is 0.589 (`ci_corrected/ci_bootstrap.txt:15`).
20. **S13, S366: "0.89 on an unseen company" is not printed anywhere.** I recomputed it as B-cubed precision 0.887. Also, "case precision" throughout is B-cubed precision (`one_company_score.py:56-63`), not "purity of each case" as S207 defines it.
21. **S138: the list of largest topics skips "Email" (11 cases).** That topic is larger than "crashes" (10).
22. **S137–S139: the topic statistics (306 / 44 / 41, c_v 0.49) can only be reproduced from a temporary `topics.json` in Claude's scratchpad.** Save it to the repo.
23. **S190, S200: two `[TODO: …]` placeholders are still in the paper.**
24. **S352, S362: "z > 2 per tag" for SentiSum is not in the notes.** They describe a z-score with an ML sensitivity setting.

---
**S0**
1. [STATEMENT]: InsightDesk: LLM-Verified Grouping of Customer Complaints into Problem Cases for Incident Detection and Escalation
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked/ppt/slides/slide1.xml (project title 'InsightDesk - Intelligent complaint triage system'); title wording itself only in InsightDesk-claude-review/reports/paper/build_docx.py
4. [CONFIDENCE LEVEL]: Medium — The system name is in the files; the exact title is the paper's own wording, not a stated fact.

**S1**
1. [STATEMENT]: Krushnam Sadrani, Sanyogita Shinde, Krisha Sinnarkar
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked/ppt/slides/slide1.xml: 'Krisha Sinnarkar(Roll No.-61) / Sanyogita Shinde(Roll No.-60) / Krushnam Sadrani(Roll No.- 40)'
4. [CONFIDENCE LEVEL]: High — All three names appear on the deck title slide.

**S2**
1. [STATEMENT]: Department of Artificial Intelligence & Data Science, K.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked/ppt/slides/slide1.xml: 'Department of AI-DS, K.J. Somaiya Institute of Technology, Sion, Mumbai'
4. [CONFIDENCE LEVEL]: High — Stated on the title slide.

**S3**
1. [STATEMENT]: J.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: same as above
4. [CONFIDENCE LEVEL]: High — Fragment of the institute name split by the sentence splitter.

**S4**
1. [STATEMENT]: Somaiya Institute of Technology, Sion, Mumbai
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: same as above
4. [CONFIDENCE LEVEL]: High — Fragment of the institute name.

**S5**
1. [STATEMENT]: Under the guidance of Prof.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked/ppt/slides/slide1.xml: 'Guide:Prof.Ganesh Wadmare'
4. [CONFIDENCE LEVEL]: High — Stated on the title slide.

**S6**
1. [STATEMENT]: Ganesh Wadmare
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: same as above
4. [CONFIDENCE LEVEL]: High — Fragment of the guide's name.

**S7**
1. [STATEMENT]: Academic Year 2025–26
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no file states the academic year; the deck shows the date 26/6/2023)
4. [CONFIDENCE LEVEL]: Medium — Plausible, but nothing in the folder states '2025–26'.

**S8**
1. [STATEMENT]: Abstract— Support teams receive the same problem described in many different words.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/RESULTS.md:107-111 (issues split into differently worded cases); InsightDesk-dedup/experiments/dedup/labels/playstore_codebook.csv
4. [CONFIDENCE LEVEL]: Medium — This is a motivation statement; the data shows paraphrased duplicates but no file states it as a finding.

**S9**
1. [STATEMENT]: Counting, alerting and escalation all depend on first grouping these raw complaints into problem-level cases, yet published systems either cluster offline into topics, rely on per-ticket classification, or need structured telemetry.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:11,148-149; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:10,94; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:54
4. [CONFIDENCE LEVEL]: Medium — The notes support topic/version, category and telemetry approaches; 'published systems either…' is a generalisation.

**S10**
1. [STATEMENT]: We present InsightDesk, an online pipeline that assigns each arriving complaint to a problem case: similarity retrieval over diverse case exemplars narrows each complaint to at most five candidate cases, a calibrated similarity band settles clear matches and clear non-matches, an LLM judge makes one bounded decision whenever similarity alone is not conclusive, and a periodic re-joining pass merges cases that online decisions split.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:30-31,45-66 (T_HIGH/T_LOW band, MAX_EXEMPLARS=5, top-5, PROMPT_GATED); InsightDesk-claude-review/backend/services/rejoin.py:1-13
4. [CONFIDENCE LEVEL]: High — Every component named is implemented in the backend.

**S11**
1. [STATEMENT]: On top of cases it computes per-case spike signals with a Poisson CUSUM, groups related cases for alerting, raises a separate alarm for vague complaints that fit no case, and escalates only after human approval.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:1-36; InsightDesk-claude-review/backend/services/alert_groups.py:1-14; InsightDesk-claude-review/backend/services/unassigned_spikes.py; InsightDesk-claude-review/backend/services/escalation_policy.py:6-26
4. [CONFIDENCE LEVEL]: High — CUSUM, alert groups, vague alarm and the escalation policy all exist in code; human approval is enforced in the escalate route.

**S12**
1. [STATEMENT]: On 338 human-labelled Play Store reviews of six help-desk products, InsightDesk reaches pairwise precision 0.83, recall 0.35 and F1 0.49, against F1 0.05–0.25 for published app-review grouping and topic-model baselines on the same data.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:26 'R1 + RJ1 (deployed) P 0.834 R 0.351 F1 0.494'; InsightDesk-claude-review/reports/baselines/baselines_results.txt:5,7 (CLAP published F1 0.049, BERTopic F1 0.254); 338 rows in InsightDesk-dedup/data/external/playstore_scored.csv
4. [CONFIDENCE LEVEL]: High — Every number matches the files. But the held-out runs calibrate t_high per tuning half (0.70–0.77, sensitivity_results.txt:72), not the deployed 0.8306.

**S13**
1. [STATEMENT]: With the same upper threshold it reaches precision 0.87–0.96 on Bugzilla duplicate benchmarks (F1 0.78–0.79), case precision 0.92 on three unseen products and 0.89 on an unseen company.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:26,35,44 (Firefox P 0.922/0.959/0.963); InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:11,23 (F1 0.780, 0.790; Thunderbird P 0.873); InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:12-13 (B-cubed P 0.928–0.940); LOPO B-cubed P 0.887 recomputed from InsightDesk-dedup/experiments/dedup/results/playstore_e5_assignments_llm_perproduct_wideband_exemplars_top5_founder_gated_lopo.csv
4. [CONFIDENCE LEVEL]: Medium — The numbers are reproducible, but '0.89' is not printed in any file (I recomputed it). 'Case precision' is B-cubed precision. And 0.92 for unseen products depends on which LLM key is used (0.928 Claude key / 0.924 ChatGPT key, harness run).

**S14**
1. [STATEMENT]: On outbreaks injected into real complaint streams, its CUSUM detects 76–91% on bug-report streams and 42–43% on short-review streams at under one false alarm per 100 windows, where the per-tag z-score rule common in feedback-analytics tools detects none, and outages made only of vague complaints are detected in all cases.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/cusum_confirm_results.txt:2-3 (0.76, 0.91); InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:15-16 (0.42, 0.43, false 0.06); InsightDesk-dedup/experiments/dedup/results/vague_area_spike_results.txt:7-8 and InsightDesk-dedup/experiments/dedup/results/vague_counter_confirm_results.txt:4-5 (n=10/20 detected 1.00)
4. [CONFIDENCE LEVEL]: High — All figures appear in the result files. 'Detected in all cases' holds only for vague outages of 10+ complaints (n=5: 0.46–0.52).

**S15**
1. [STATEMENT]: Keywords— Complaint intelligence, duplicate detection, LLM-as-a-judge, sentence embeddings, online clustering, spike detection, Poisson CUSUM, sentiment analysis, BERTopic, root-cause analysis, human-in-the-loop.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Keyword list; topics map to backend modules (dedup_r1.py, spike_detection.py, sentiment/, clustering_service.py, rca_service.py)
4. [CONFIDENCE LEVEL]: High — These are descriptive keywords, each matching an implemented module.


## I. INTRODUCTION

**S17**
1. [STATEMENT]: A B2B SaaS support desk sees hundreds of complaints a day.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no file measures daily complaint volume of a B2B SaaS desk)
4. [CONFIDENCE LEVEL]: Medium — This is an unsourced framing claim.

**S18**
1. [STATEMENT]: The operational questions are problem-level: how many customers are hit by the same issue, is it suddenly growing, what is the likely cause, and who must act.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked (problem slide); InsightDesk_PROJECT_GUIDE.md
4. [CONFIDENCE LEVEL]: Low — A motivational statement with no data behind it.

**S19**
1. [STATEMENT]: Answering them requires a step that most tools skip or hide: deciding, as each complaint arrives, whether it reports a problem already known or a new one.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:54 (VoC tools group by tag/theme)
4. [CONFIDENCE LEVEL]: Medium — 'Most tools' is a generalisation from the industry notes.

**S20**
1. [STATEMENT]: This step is hard for three reasons.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Rhetorical lead-in to sentences 21–23
4. [CONFIDENCE LEVEL]: High — No factual content of its own.

**S21**
1. [STATEMENT]: First, complaints are short and noisy (21 words on average in our Play Store data) and two reports of one problem often share almost no vocabulary.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED. Recomputed from InsightDesk-dedup/data/external/playstore_scored.csv: mean 28.1 words (338 scored), playstore_all.csv mean 25.8 / median 19 (450)
4. [CONFIDENCE LEVEL]: High — No file states 21 words, and the measured mean is 26–28 words (the median is 19–20).

**S22**
1. [STATEMENT]: Second, the decision must be online and stable: a case that changes membership when the input order changes cannot carry counts, spike history or an escalation record.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_rule.md:32-35 (stable case ids as the online advantage); InsightDesk-dedup/experiments/dedup/results/RESULTS.md:41 (arrival orders)
4. [CONFIDENCE LEVEL]: Medium — This is a design argument the files make, not a measurement.

**S23**
1. [STATEMENT]: Third, a wrong merge is costly, because it inflates a case and can trigger a false escalation.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/escalation_policy.py:6-26 (counts drive eligibility)
4. [CONFIDENCE LEVEL]: Medium — It follows from the escalation rule (≥3 reports), but the cost is not measured.

**S24**
1. [STATEMENT]: The contributions of this paper are:
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Lead-in
4. [CONFIDENCE LEVEL]: High — No claim.

**S25**
1. [STATEMENT]: • An online retrieve-then-verify grouping method for raw complaints: exemplar-based case retrieval, a similarity band calibrated from labelled pairs with a per-channel lower threshold (Section IV-C), and an LLM judge consulted only inside the band, followed by an LLM-verified case re-joining pass.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:30-66; InsightDesk-claude-review/backend/services/rejoin.py:1-13; InsightDesk-claude-review/tests/test_tlow_channel.py (per-channel t_low)
4. [CONFIDENCE LEVEL]: High — All parts exist in code, including the per-channel t_low test.

**S26**
1. [STATEMENT]: • Per-case incident signals built on those cases: a Poisson CUSUM spike detector on small counts and alert groups over related cases, with a human-approved escalation policy.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:26-36; InsightDesk-claude-review/backend/services/alert_groups.py:1-14; InsightDesk-claude-review/backend/services/escalation_policy.py
4. [CONFIDENCE LEVEL]: High — Implemented.

**S27**
1. [STATEMENT]: • A vague-complaint alarm: complaints too vague to join any case (“the app is not working”) are counted per product and tested for a surge, so an outage that customers describe only vaguely still raises an alert.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/unassigned_spikes.py; InsightDesk-dedup/experiments/dedup/results/vague_counter_confirm_rule.md
4. [CONFIDENCE LEVEL]: High — The vague-complaint counter per product is implemented and tested.

**S28**
1. [STATEMENT]: To our knowledge no published system monitors the complaints its grouping cannot place.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:82; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:94 (no single system combines...)
4. [CONFIDENCE LEVEL]: Medium — The notes searched for such systems but do not state this specific negative; it is hedged with 'to our knowledge'.

**S29**
1. [STATEMENT]: • An evaluation on human-labelled real complaints, independent Bugzilla duplicate labels, unseen products and an unseen company, with pre-declared acceptance rules and cluster-bootstrap confidence intervals whose coverage we verify by simulation.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/*_rule.md (pre-declared rules, e.g. tlow_confirm_rule.md:1 'written 2026-10-19, before running'); InsightDesk-dedup/experiments/dedup/results/ci_correction_note.md:20-31 (coverage simulation)
4. [CONFIDENCE LEVEL]: High — Rules and the coverage check exist.

**S30**
1. [STATEMENT]: • A head-to-head comparison against published grouping methods, topic models, embedding thresholds, a tuned cross-encoder pipeline and general-purpose LLMs on identical data.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt; InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt; InsightDesk-dedup/experiments/dedup/results/external_ce_comparison.txt; InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_A.txt
4. [CONFIDENCE LEVEL]: High — Each comparison has a result file.

**S31**
1. [STATEMENT]: Section II reviews related work.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Document structure (paper section II)
4. [CONFIDENCE LEVEL]: High — Structural.

**S32**
1. [STATEMENT]: Section III states the problem and gives the architecture, and Section IV describes each phase of the methodology in detail.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Document structure
4. [CONFIDENCE LEVEL]: High — Structural.

**S33**
1. [STATEMENT]: Section V covers the implementation, Section VI the data and evaluation protocol, and Section VII the results.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Document structure
4. [CONFIDENCE LEVEL]: High — Structural.

**S34**
1. [STATEMENT]: Sections VIII and IX conclude and outline future work.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Document structure
4. [CONFIDENCE LEVEL]: High — Structural.


## II. LITERATURE SURVEY

**S36**
1. [STATEMENT]: Work relevant to InsightDesk falls into four families, compared with their parameters in Table I.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table I in the paper
4. [CONFIDENCE LEVEL]: High — Structural.


## A. App-Review Mining and Emerging-Issue Detection

**S38**
1. [STATEMENT]: Mining app reviews for software engineering is a mature field [1].
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:139 (mapping study); Dąbrowski SLR cited in InsightDesk-claude-review/reports/Raw complaint dedup literature review.md
4. [CONFIDENCE LEVEL]: Medium — A literature review in the notes supports it.

**S39**
1. [STATEMENT]: MERIT [2] tracks topics across app versions with an online joint sentiment-topic model and flags topics whose share rises in a new version, explaining them with extracted phrases.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:28 (MERIT/AOBST, TSE 2022), 148 ('Per-version… extractive explanation')
4. [CONFIDENCE LEVEL]: High — Matches the research notes.

**S40**
1. [STATEMENT]: Earlier, CLAP [21] grouped reviews that report the same bug with DBSCAN over textual features for release planning.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:58-62 ('CLAP… cluster individual reviews that report the same bug'); InsightDesk-claude-review/reports/baselines/baselines_results.txt:5 (eps 0.6 DBSCAN reimplemented)
4. [CONFIDENCE LEVEL]: High — In the notes and reimplemented.

**S41**
1. [STATEMENT]: These systems work per version or per topic rather than per problem case, and none decides membership online.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:148-149 ('Per-version, not per-case windows')
4. [CONFIDENCE LEVEL]: Medium — 'None decides membership online' is a generalisation over the systems surveyed.


## B. Duplicate Detection and LLM Judges

**S43**
1. [STATEMENT]: A recent large study of duplicate bug-report detection [3] finds that classic retrieval such as REP [22] remains competitive with deep models, and Cupid [4] improves it by letting an LLM extract the essentials of each report first (Recall-Rate@10 0.60–0.65).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/Raw complaint dedup literature review.md:88 'Cupid | LLM extracts essentials, then REP retrieval | 0.602 / 0.637 / 0.654'; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/semantic_dedup_methods.md:47
4. [CONFIDENCE LEVEL]: High — The numbers round to 0.60–0.65.

**S44**
1. [STATEMENT]: Bi-encoders such as SBERT [23] give indexable embeddings, while cross-encoders built on BERT [24] are more accurate but cannot be indexed.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: General background; not in notes
4. [CONFIDENCE LEVEL]: Medium — This is standard knowledge, and the TOSEM paper is in the notes, but the bi- vs cross-encoder statement has no local source.

**S45**
1. [STATEMENT]: LLMs used zero-shot as matchers reach F1 89.6–98.4 on entity-matching benchmarks [5], and LLM judges agree with human preferences on many tasks [6], [7]; their known position and verbosity biases argue for bounding each decision, which InsightDesk does with retrieval and calibrated thresholds.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/semantic_dedup_methods.md:72-84 (GPT-4 zero-shot F1: 89.61, 95.78, 89.67, 76.38, 89.82, 98.41)
4. [CONFIDENCE LEVEL]: High — The F1 range is misreported: the local table runs 76.4–98.4, and 89.6 is not the minimum. The position/verbosity-bias claim and refs [6],[7] have no local source.


## C. Near-Duplicate and Semantic Deduplication

**S47**
1. [STATEMENT]: SimHash [25] and MinHash-LSH [26] detect copies at web scale, and SemDeDup [8] removes pairs of embeddings closer than a small distance ε.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/Raw complaint dedup literature review.md:141 'SemDeDup | … | ε = 0.00095–0.03'; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/near_dup_streaming_clustering.md:55; SimHash/MinHash in InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/near_dup_streaming_clustering.md
4. [CONFIDENCE LEVEL]: High — In the notes.

**S48**
1. [STATEMENT]: Embedding benchmarks [9] show that no single model leads on every clustering task.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder) (MTEB not mentioned in any local note)
4. [CONFIDENCE LEVEL]: Low — This may be true of MTEB, but nothing local supports it.

**S49**
1. [STATEMENT]: These methods target near-copies, not paraphrases of the same problem.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt:3-4 (MinHash F1 0.197, SimHash 0.115 on paraphrase data)
4. [CONFIDENCE LEVEL]: High — Supported by the measured failure of the near-copy methods.


## D. Incident Management and Feedback Analytics

**S51**
1. [STATEMENT]: iPACK [10] links customer tickets to incidents using cloud alerts (F1 0.87–0.94), and TickIt [11] groups and escalates tickets with an LLM (F1 0.88).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:97 'TickIt's dedup F1 of 0.879 and iPACK's 0.871-0.935'; :14 (iPACK input: tickets plus cloud alerts)
4. [CONFIDENCE LEVEL]: High — Matches the notes.

**S52**
1. [STATEMENT]: LLM-based root-cause recommendation for cloud incidents [12], [13] grounds its explanations in telemetry, in the spirit of retrieval-augmented generation [15].
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:94 ('Telemetry plus LLMs is used for RCA (RCACopilot…)')
4. [CONFIDENCE LEVEL]: Medium — Supported for RCACopilot; Ahmed et al. [12] has no local note.

**S53**
1. [STATEMENT]: Commercial voice-of-customer tools such as SentiSum [14] detect anomalies per tag or theme, typically with z-scores, and publish neither their grouping method nor its accuracy.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:11,54,57 ('Z-score vs ~100-day baseline', 'no case dedup documented')
4. [CONFIDENCE LEVEL]: High — Matches the notes.


## E. Research Gaps Addressed

**S55**
1. [STATEMENT]: Three gaps shape InsightDesk.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Lead-in
4. [CONFIDENCE LEVEL]: High — No claim.

**S56**
1. [STATEMENT]: First, existing systems group by topic, version or predefined category, not into problem cases decided online as complaints arrive, so they cannot carry a stable count per problem.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:148-149; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:10
4. [CONFIDENCE LEVEL]: Medium — A generalisation from the surveyed systems.

**S57**
1. [STATEMENT]: Second, spike detection in feedback tools runs on per-tag z-scores, which are unstable at the zero-to-two complaints per window that a single problem produces, and nothing monitors the complaints that the grouping cannot place.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:3-6 (z-score detector 0%); InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:57
4. [CONFIDENCE LEVEL]: Medium — The z-score failure is measured; 'nothing monitors' is a generalisation.

**S58**
1. [STATEMENT]: Third, no published system we found combines online problem-case grouping of raw complaint text with per-case spike detection, cause explanation and human-approved escalation, and reports labelled accuracy for the grouping step.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:94 ('No single published system found com[bines]…'); InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:127
4. [CONFIDENCE LEVEL]: Medium — The notes support it with 'found' scope.

**S59**
1. [STATEMENT]: TABLE I
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.

**S60**
1. [STATEMENT]: COMPARATIVE LITERATURE SURVEY
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.


## III. PROPOSED SYSTEM


## A. Problem Statement

**S63**
1. [STATEMENT]: Help-desk and customer-support platforms such as Vision Helpdesk, Zendesk, Freshdesk, Intercom and ServiceNow, and the companies that use them, receive complaints from app reviews, support tickets, chat and web forms.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked slide3.xml (same text); Zendesk/Freshdesk/Intercom/ServiceNow appear in data/external/new_apps_all.csv and playstore_all.csv
4. [CONFIDENCE LEVEL]: Medium — The platform names are in the data, but that these channels receive complaints is background.

**S64**
1. [STATEMENT]: The same problem is reported many times in different words, so agents triage it again and again, and no one sees how many customers a single problem affects.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/RESULTS.md:107-111
4. [CONFIDENCE LEVEL]: Low — A motivation statement, not a measurement.

**S65**
1. [STATEMENT]: Existing tools group complaints by theme (“login”) rather than by problem (“the OTP never arrives”): keyword rules and topic models mix different problems, and a single similarity threshold either merges unrelated complaints or misses paraphrases.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:7 (BERTopic P 0.158); InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:6 (cosine only P 0.844 R 0.052)
4. [CONFIDENCE LEVEL]: High — The theme-vs-problem and single-threshold failures are measured.

**S66**
1. [STATEMENT]: Feedback tools flag spikes with z-scores on whole categories, which miss a new problem growing from a low base.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:3-6; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:57
4. [CONFIDENCE LEVEL]: Medium — The z-score failure is measured on case counts, not on 'whole categories'.

**S67**
1. [STATEMENT]: There is a need for a system that groups raw complaints into problem-level cases as they arrive with high precision, tracks each case’s volume to raise incidents early, adds sentiment, topic and root cause, and routes each incident to the responsible department after a person approves it.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Requirements statement
4. [CONFIDENCE LEVEL]: Medium — Normative; no factual claim.


## B. System Architecture Overview

**S69**
1. [STATEMENT]: InsightDesk runs nine phases in four stages: Fig. 1 shows the flowchart of the pipeline and Fig. 2 its system architecture.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/paper/img (Fig. 1, Fig. 2); InsightDesk-claude-review/backend/main.py:20-27
4. [CONFIDENCE LEVEL]: High — The figures exist; 'nine phases' is the paper's own structuring.

**S70**
1. [STATEMENT]: In the first stage, intake and grouping (phases 1–4), each complaint is cleaned, embedded and either joined to an existing case, opened as a new case, or set aside as too vague to place.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:82 (routes auto_merge | judge_merge | new_* | vague)
4. [CONFIDENCE LEVEL]: High — Implemented routes.

**S71**
1. [STATEMENT]: In the second stage, case upkeep (phases 5–6), a re-joining pass every 6 hours merges cases that describe one problem, and each case receives a sentiment label, a topic and the department responsible for that topic.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/main.py:20-27 (REJOIN_INTERVAL_HOURS 6, topic clustering); InsightDesk-claude-review/backend/services/rejoin.py:42 (REJOIN_ENABLED)
4. [CONFIDENCE LEVEL]: High — Implemented, but re-joining runs only when REJOIN_ENABLED=1.

**S72**
1. [STATEMENT]: In the third stage, incident signals (phases 7–8), complaint counts per case in 6-hour windows feed a Poisson CUSUM spike detector, and vague complaints feed a separate per-product alarm.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:26; InsightDesk-claude-review/backend/services/unassigned_spikes.py:59
4. [CONFIDENCE LEVEL]: High — Implemented.

**S73**
1. [STATEMENT]: In the fourth stage, action (phase 9), an eligible case receives an LLM-written root-cause explanation, and an email reaches the department only after a person approves it.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rca_service.py:24-29; InsightDesk-claude-review/backend/services/escalation_policy.py
4. [CONFIDENCE LEVEL]: High — Implemented.

**S74**
1. [STATEMENT]: Cases carry counts, a spike history and an escalation record in Supabase (PostgreSQL); case exemplar vectors live in Pinecone.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/database/schema.sql:23-101 (cases with spike_status/score/detected_at, complaint_windows, case_rca); InsightDesk-claude-review/backend/services/dedup_r1.py:131 (Pinecone ids)
4. [CONFIDENCE LEVEL]: Medium — Counts and RCA are stored. Spike state is stored as latest values only, not a history table, and I found no explicit escalation-record column.

**S75**
1. [STATEMENT]: Sentiment and topic labels are attached to cases for the dashboard and routing and are not used in the grouping decisions.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py (no use of sentiment/topic in decide)
4. [CONFIDENCE LEVEL]: High — Grouping code does not read sentiment or topics.


## IV. METHODOLOGY

**S77**
1. [STATEMENT]: This section describes each phase in detail: its input, the rule it applies with its parameters, and its output.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Structural
4. [CONFIDENCE LEVEL]: High — No claim.

**S78**
1. [STATEMENT]: Fig. 1 shows the path of a complaint through these phases, and Equations (1)–(11) give each rule.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/paper/build_docx.py:30-46 (11 equations)
4. [CONFIDENCE LEVEL]: High — There are 11 equations in the build script.

**S79**
1. [STATEMENT]: Throughout, a running example follows the complaint “Can’t log in since the update, the OTP never arrives”.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/worked_example.txt:5-7 (OTP complaints exist in the synthetic set)
4. [CONFIDENCE LEVEL]: Medium — This is an illustrative example; the exact sentence is not in the data.


## A. Phase 1 – Intake and Cleaning

**S81**
1. [STATEMENT]: A signed-in customer submits a complaint through the React dashboard or an API client; the FastAPI service stores it with its product, user and source channel (for example web form, app review or chat).
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/models/complaint.py; InsightDesk-claude-review/web/src/pages/customer/SubmitComplaintPage.tsx; InsightDesk-claude-review/backend/database/schema.sql:46-64
4. [CONFIDENCE LEVEL]: Medium — Product and user are stored. I did not confirm a 'source channel' field in the schema shown.

**S82**
1. [STATEMENT]: Text beyond 5,000 characters is truncated.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/models/complaint.py:13 'complaint_text: str = Field(min_length=10, max_length=5000)'; InsightDesk-claude-review/replay_real_data.py:138 '[:5000]'
4. [CONFIDENCE LEVEL]: High — The API REJECTS text over 5,000 characters (validation error); only the replay script truncates. The sentence misdescribes the API.

**S83**
1. [STATEMENT]: Cleaning uses label-free boilerplate suppression.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/normalize.py:100-120 (boilerplate_suppress); InsightDesk-claude-review/backend/services/preprocess.py:174-200 (clean_text has NO boilerplate step)
4. [CONFIDENCE LEVEL]: High — True for the experiment harness; the deployed backend's clean_text does not do boilerplate suppression.

**S84**
1. [STATEMENT]: The text is split into segments (sentences, clauses and a lead-in phrase).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/normalize.py:120 ff. (segments)
4. [CONFIDENCE LEVEL]: Medium — Experiment harness only.

**S85**
1. [STATEMENT]: A segment is a boilerplate candidate when it recurs in at least 8 complaints with segment cosine similarity of at least 0.90, and it is confirmed as boilerplate when the remaining text of those complaints is unrelated (mean cosine below 0.30), as with greetings such as “Hi team, please help”.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/normalize.py:100-102 'NEAR_COPY = 0.90 … MIN_HOSTS = 8 … MAX_HOST_COHESION = 0.30'
4. [CONFIDENCE LEVEL]: High — Exact constants match, but they live in the experiment harness, not the app.

**S86**
1. [STATEMENT]: Boilerplate is dropped while at least one segment is always kept; the text is lower-cased and stripped of punctuation and stop words.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/preprocess.py:174-200 (lower-case, strip punctuation, STOPWORDS)
4. [CONFIDENCE LEVEL]: High — The lower-casing and stop-word part matches the app; the boilerplate part is harness-only.

**S87**
1. [STATEMENT]: Negations (not, never, can’t) are kept, because “works” and “doesn’t work” must not look alike.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/preprocess.py:62-172 (STOPWORDS has no 'not'/'never')
4. [CONFIDENCE LEVEL]: Medium — 'not'/'never' are kept, but punctuation stripping turns can't into 'can t' and 'can' is a stop word, so only 't' survives.

**S88**
1. [STATEMENT]: The original text is kept for display and for the LLM judge.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:826 'judge_text = boilerplate_suppress(df["complaint_text"]…)'; InsightDesk-claude-review/backend/services/dedup_r1.py (founder_text)
4. [CONFIDENCE LEVEL]: Medium — The judge sees the original or lightly cleaned text.

**S89**
1. [STATEMENT]: For the running example, only the complaint itself remains.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Illustrative
4. [CONFIDENCE LEVEL]: Low — Part of the running example; not measured.


## B. Phase 2 – Embedding and Case Retrieval

**S91**
1. [STATEMENT]: Let x be a complaint and e(x) the L2-normalised MiniLM [19] embedding of its cleaned text (384 dimensions), so similarity is the dot product s(x, y) = e(x)·e(y).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/embedding_service.py; InsightDesk-dedup/experiments/dedup/e5_three_way.py:827 'normalize_embeddings=True'
4. [CONFIDENCE LEVEL]: High — The MiniLM 384-d normalised embedding is used.

**S92**
1. [STATEMENT]: Each case C keeps a set E_C of at most five exemplars.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:45 'MAX_EXEMPLARS = 5'
4. [CONFIDENCE LEVEL]: High — Exact constant.

**S93**
1. [STATEMENT]: A new member m of C is added to E_C only if it is not already represented:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:46,164 'DIVERSE_SIM = 0.85'
4. [CONFIDENCE LEVEL]: High — Exact rule.

**S94**
1. [STATEMENT]: The score of complaint x against case C is its best match among the exemplars, and only cases of the same product are considered:
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:184 'store.query(vec, QUERY_VECTORS, product)'
4. [CONFIDENCE LEVEL]: Medium — Correct when a product is given; with a blank product there is no filter (the staging demo uses that).

**S95**
1. [STATEMENT]: Exemplars let one case match differently worded reports of the same problem, which a single centroid cannot.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/multi_exemplar_rule.md; InsightDesk-dedup/experiments/dedup/results/e8_exemplars_playstore.csv
4. [CONFIDENCE LEVEL]: Medium — Exemplar experiments exist; 'which a single centroid cannot' is overstated (RESULTS.md:50 found centroid ≈ first).

**S96**
1. [STATEMENT]: Each exemplar is stored in Pinecone with its case, product, vague flag and the text of the complaint that founded the case; one query returns the 60 nearest vectors, which are ranked per case by their best exemplar.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:47 'QUERY_VECTORS = 60'
4. [CONFIDENCE LEVEL]: High — Exact constant.

**S97**
1. [STATEMENT]: For the running example, the closest case is “OTP not received on login” with S* = 0.71.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (illustrative; no run produced S* = 0.71 for this text)
4. [CONFIDENCE LEVEL]: High — A made-up example value; label it 'illustrative' in the paper.


## C. Phase 3 – Calibrated Decision Band

**S99**
1. [STATEMENT]: For the best candidate C* with score S* = S(x, C*), the decision is
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/paper/build_docx.py:33-35 (Eq. 3)
4. [CONFIDENCE LEVEL]: High — Equation text.

**S100**
1. [STATEMENT]: where J is the LLM judge (Phase 4).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:104
4. [CONFIDENCE LEVEL]: High — Judge call.

**S101**
1. [STATEMENT]: Both thresholds are set once on a labelled tuning half, using only pairs within the same product.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:69-110 (band_thresholds on emb[tune], per product); InsightDesk-dedup/experiments/dedup/e5_three_way.py:870-872 (calibrate_on uses the WHOLE calibration dataset)
4. [CONFIDENCE LEVEL]: High — True for held-out experiments. The deployed values 0.8306/0.26 come from calibrating on all 338 Play Store reviews (ext_playstore runs), not a tuning half.

**S102**
1. [STATEMENT]: With y_i the true problem of complaint i and s_ij the similarity of complaints i and j:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/paper/build_docx.py:36-37
4. [CONFIDENCE LEVEL]: High — Equation definitions.

**S103**
1. [STATEMENT]: so that automatic joins are at least 97% correct on tuning data, and
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:56 'HIGH_PRECISION = 0.97', :78
4. [CONFIDENCE LEVEL]: High — Exact rule.

**S104**
1. [STATEMENT]: the 20th percentile of duplicate-pair similarities, so that 80% of true duplicate pairs lie at or above the band’s lower edge.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:95-106 'WIDE_RECALL = 0.80 … np.quantile(s[same], 1 - WIDE_RECALL)'
4. [CONFIDENCE LEVEL]: High — Exact rule.

**S105**
1. [STATEMENT]: Calibrated on the Play Store tuning data this gives t_low = 0.26 and t_high = 0.8306.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/playstore_e5_three_way_llm_perproduct_wideband_exemplars_top5_founder_gated_lopo.csv rows (t_low 0.2596, t_high 0.8306087851524353); InsightDesk-claude-review/backend/services/dedup_r1.py:30-31
4. [CONFIDENCE LEVEL]: High — The values are real, but they come from ALL Play Store reviews (ext runs), not the 'tuning data' of the held-out halves, which use 0.70–0.77 / 0.24–0.30 (sensitivity_results.txt:72).

**S106**
1. [STATEMENT]: The 20th-percentile rule proved conservative on short text: raising the lower threshold to 0.40 on app reviews improved precision and recall together while sending fewer complaints to the judge, and the setting was confirmed on unseen apps under a pre-declared rule, whereas on long bug reports it made no real difference (Section VII-B).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:90-97 (A3/A4); InsightDesk-dedup/experiments/dedup/results/tlow_short_text_results.txt:2-4 'RULE: ADOPT'; InsightDesk-dedup/experiments/dedup/results/tlow_confirm_results.txt:2-4 'keep t_low = 0.26'
4. [CONFIDENCE LEVEL]: High — Matches the files.

**S107**
1. [STATEMENT]: The deployed system therefore uses a per-channel lower threshold and one upper threshold for every channel:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/tests/test_tlow_channel.py; InsightDesk-claude-review/backend/services/dedup_r1.py:30-31
4. [CONFIDENCE LEVEL]: High — Per-channel t_low is implemented and tested.

**S108**
1. [STATEMENT]: In the running example S* = 0.71 lies inside the band, so the judge decides.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (illustrative value 0.71)
4. [CONFIDENCE LEVEL]: High — Same illustrative number as sentence 97.


## D. Phase 4 – LLM Judge

**S110**
1. [STATEMENT]: Inside the band an LLM (gpt-oss-120b [20]) receives the complaint and the founding text of each candidate case and answers which case reports the same underlying problem, “none”, or “too vague to tell”.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:50-66 (PROMPT_GATED: case number, 0, specific flag)
4. [CONFIDENCE LEVEL]: High — The prompt returns {specific, case}; 'too vague' comes from specific=false.

**S111**
1. [STATEMENT]: A gate in the prompt asks for a specific shared symptom rather than a shared topic: the same feature and the same failure, so that one fix would solve both.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:51-52 'Same problem = same feature AND same concrete symptom, so that one fix would solve both'
4. [CONFIDENCE LEVEL]: High — Verbatim.

**S112**
1. [STATEMENT]: The judge runs at temperature 0 with a JSON answer, and every decision is cached.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:430 (temperature=0, response_format json_object); InsightDesk-dedup/experiments/dedup/results/llm_judge_cache_*.jsonl; InsightDesk-claude-review/backend/llm/provider.py:83-105 (app: temperature 0, NO JSON mode, no cache)
4. [CONFIDENCE LEVEL]: High — True in the experiments; the deployed app neither caches judge decisions nor uses JSON mode.

**S113**
1. [STATEMENT]: A chosen case is joined and its count rises by one; “none” opens a new case; “too vague” places the complaint in the unassigned pool of its product (Phase 8); an API error, timeout or malformed answer opens a new case, so a failure never merges.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:82,214 'Decision(None, "judge_failed", …)'
4. [CONFIDENCE LEVEL]: High — Routes match.

**S114**
1. [STATEMENT]: In the running example, “the OTP never arrives” matches the symptom of “OTP not received on login”, so the complaint joins that case; a complaint that “login is slow” would open a new one.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (illustrative)
4. [CONFIDENCE LEVEL]: Medium — Example outcome, not a logged decision.

**S115**
1. [STATEMENT]: The judge never acts alone.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Summary of 116
4. [CONFIDENCE LEVEL]: High — Rhetorical.

**S116**
1. [STATEMENT]: Retrieval decides which cases it may choose from (at most five, same product only), the thresholds settle clear matches and clear non-matches without it, a failed or uncertain answer never merges, re-joining limits each case to one merge per pass, and no escalation leaves the system without human approval.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:45-47,184,214; InsightDesk-claude-review/backend/services/rejoin.py:1-13; InsightDesk-claude-review/backend/services/escalation_policy.py
4. [CONFIDENCE LEVEL]: High — Each guard is in code (the same-product filter applies only when a product is given).

**S117**
1. [STATEMENT]: Each complaint receives at most one judge decision, never pairwise comparisons.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:104 (one generate_json call per complaint)
4. [CONFIDENCE LEVEL]: High — One call per complaint.

**S118**
1. [STATEMENT]: In our runs the band covered 66% of short reviews at the deployed setting and 90–96% of bug reports.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:97 'judged 66%'; InsightDesk-dedup/experiments/dedup/results/tlow_confirm_results.txt:2-3 (judged 96%, 90%)
4. [CONFIDENCE LEVEL]: High — Exact.

**S119**
1. [STATEMENT]: The judge answered “too vague to tell” for 20% of Play Store complaints and 7% of bug reports.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/review_stats.txt:1,3,5 (too vague 103/505 = 20.4%, 32/437 = 7.3%, 33/452 = 7.3%)
4. [CONFIDENCE LEVEL]: High — Computed from the counts; measured at t_low 0.26, not the deployed 0.40.

**S120**
1. [STATEMENT]: A decision takes 1.34 s at the median and costs about $0.24 per 1,000 judged complaints (Section VII-E).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/latency_cost.txt:2,4 'median 1.34 s', '$0.244 per 1,000 judged complaints'
4. [CONFIDENCE LEVEL]: High — Exact.


## E. Phase 5 – Case Re-joining

**S122**
1. [STATEMENT]: Online decisions split some problems across several cases.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/rejoin_ceiling.txt:2,8,14 ('problems split into >= 2 cases: 30')
4. [CONFIDENCE LEVEL]: High — Measured.

**S123**
1. [STATEMENT]: Every 6 hours a scheduler inside the API runs a re-joining pass.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/main.py:20 'REJOIN_INTERVAL_HOURS', "6"
4. [CONFIDENCE LEVEL]: High — Exact; it only runs when REJOIN_ENABLED=1.

**S124**
1. [STATEMENT]: For every case A it considers its three nearest same-product cases B whose case similarity reaches t_low:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rejoin.py:5-6,24,56-59 'TOP_K = 3', 'if s >= t_low'
4. [CONFIDENCE LEVEL]: High — Exact.

**S125**
1. [STATEMENT]: Candidate pairs are examined in decreasing σ.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rejoin.py:62 'sorted(pairs.items(), key=lambda kv: -kv[1])'
4. [CONFIDENCE LEVEL]: High — Exact.

**S126**
1. [STATEMENT]: An LLM case-pair judge sees up to three complaints per side and decides whether both cases describe one problem.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rejoin.py:25 'SHOW = 3'
4. [CONFIDENCE LEVEL]: High — Exact.

**S127**
1. [STATEMENT]: Each case takes part in at most one merge per pass, which keeps a single wrong decision from cascading.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rejoin.py:63-69 (done set)
4. [CONFIDENCE LEVEL]: High — Exact.

**S128**
1. [STATEMENT]: On a merge, counts are summed and the complaints, 6-hour windows and exemplar vectors of the absorbed case move to the kept case, which keeps its founding text; the absorbed case is hidden and is never offered to the judge again.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rejoin.py:65-67; InsightDesk-claude-review/reports/staging/seed_summary.txt:1 (kept/absorbed)
4. [CONFIDENCE LEVEL]: Medium — The merge logic is visible; window/vector moves are in dashboard/supabase code I did not open line by line.

**S129**
1. [STATEMENT]: On the Play Store held-out halves at the deployed setting, the judge approved 35 merges, of which 23 (66%) joined cases with the same majority problem; on Firefox and Thunderbird it approved 22 and 18 merges, of which 91% and 94% were correct.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:26 'merges 35 (23 correct)'; InsightDesk-dedup/experiments/dedup/results/review_stats.txt:4,6 '22 merges approved, 20 correct (91%)', '18 merges approved, 17 correct (94%)'
4. [CONFIDENCE LEVEL]: High — Exact.

**S130**
1. [STATEMENT]: Re-joining is thus reliable on bug reports and noisier on short reviews.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Derived from 129
4. [CONFIDENCE LEVEL]: High — Follows from the numbers.


## F. Phase 6 – Enrichment: Sentiment, Topics and Routing

**S132**
1. [STATEMENT]: Each case receives a sentiment label from RoBERTa [17] (cardiffnlp twitter-roberta-base-sentiment-latest) with three classes (negative, neutral, positive) and its confidence, computed once from the case’s founding complaint (its representative text), so later reports do not change it.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/sentiment/sentiment_service.py:29-60 (uses case['representative_text'])
4. [CONFIDENCE LEVEL]: High — It is recomputed on each merge, but from the same founding text, so the label is stable; 'computed once' is slightly inaccurate.

**S133**
1. [STATEMENT]: Evaluated on real Play Store reviews against star ratings (1–2 negative, 3 neutral, 4–5 positive), it reaches accuracy 0.707, with precision 0.81 and recall 0.85 on negative complaints; DistilBERT reached accuracy 0.713 but is binary, cannot say neutral, and is less precise on negatives (0.77).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sentiment_eval.txt:2-3 'accuracy 0.707 … negative-class P 0.806 R 0.847'; DistilBERT 'accuracy 0.713 … P 0.765'
4. [CONFIDENCE LEVEL]: High — Exact.

**S134**
1. [STATEMENT]: Topics come from BERTopic [16] over case texts: UMAP [27] with 12 neighbours, 5 components and cosine distance, then HDBSCAN [28] with minimum cluster size 3 and minimum samples 1, and keywords from a 1–2-gram c-TF-IDF (minimum document frequency 2).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/clustering_service.py:269-291 (ngram_range (1,2), min_df 2, n_neighbors 12, n_components 5, min_cluster_size 3, min_samples 1)
4. [CONFIDENCE LEVEL]: High — Exact constants.

**S135**
1. [STATEMENT]: Topics are recomputed on the first run, when the number of cases has grown by 20%, when outliers exceed 15%, or at a scheduled refresh; the 20% and 15% triggers are operating defaults chosen empirically, not tuned.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/clustering_service.py:32-33,119-124 'CLUSTER_GROWTH_THRESHOLD = 0.20', 'OUTLIER_THRESHOLD = 0.15'
4. [CONFIDENCE LEVEL]: High — Exact; the 'not tuned' wording is honest.

**S136**
1. [STATEMENT]: Departments come from a fixed rule table, not an LLM: five departments (Engineering, Authentication, Payments, Customer Success, Platform) each have a list of trigger words (for Authentication: login, password, otp, signin, verification, token), a topic goes to the department whose list matches most of its five top keywords, a topic with no match goes to General Support, and an operator can override the department in the dashboard.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/department_service.py:8-80 (5 departments, Authentication triggers), :128-131 'return "General"'; InsightDesk-claude-review/backend/department_mapping.py:48-53 (falls back to General Support email); InsightDesk-claude-review/web/src/api/types.ts (department_override)
4. [CONFIDENCE LEVEL]: High — The no-match label is 'General' (emailed via General Support). 'Five top keywords' is not visible in the function itself.

**S137**
1. [STATEMENT]: On the 306 cases of the test deployment BERTopic found 44 topics and left 41 cases (13%) as outliers.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Claude session scratchpad (outside the project): topics.json (306 cases, 44 topics, 41 outliers, recomputed)
4. [CONFIDENCE LEVEL]: Medium — Reproducible only from a temporary scratchpad snapshot; nothing is saved in the project.

**S138**
1. [STATEMENT]: Their c_v coherence is 0.49, against 0.38 for random five-word sets from the same texts, so the topics are moderately coherent; the largest are login and sign-in (19 cases), notifications (18), reinstalling or the app not working (16), support plans (15) and crashes after a new version (10).
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Claude session scratchpad (outside the project): topics.json + InsightDesk-claude-review/reports/paper/topic_coherence.py (c_v 0.489 vs random 0.383)
4. [CONFIDENCE LEVEL]: Medium — Reproduced, but from a non-project file. The list of largest topics skips 'Email' (11 cases), which is larger than 'crashes' (10).

**S139**
1. [STATEMENT]: The rule table routed only 19 of the 44 topics to a named department and sent 25 to General Support, so routing is the weakest step; a learned or LLM-based mapping is left to future work.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Claude session scratchpad (outside the project): topics.json: departments Authentication 1, Customer Success 9, Engineering 9, General 25
4. [CONFIDENCE LEVEL]: Medium — 19/25 reproduced from a scratchpad snapshot only.

**S140**
1. [STATEMENT]: In the running example the case is labelled negative and placed under an Authentication topic.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Illustrative
4. [CONFIDENCE LEVEL]: Low — Part of the running example.


## G. Phase 7 – Spike Detection

**S142**
1. [STATEMENT]: Complaints are counted per case u in 6-hour windows t, written c_ut, with zeros filled in for empty windows.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:3-5,26,100 (zero-filled 6-hour windows)
4. [CONFIDENCE LEVEL]: High — Exact.

**S143**
1. [STATEMENT]: A repeat complaint from the same user about the same case within 24 hours is attached to the case but not counted again.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/database/supabase.py:165-169 'hours: int = 24'; InsightDesk-claude-review/backend/services/duplicate_service.py:204-220 'Merged with recent report'
4. [CONFIDENCE LEVEL]: High — Exact.

**S144**
1. [STATEMENT]: The expected rate is a smoothed mean over the previous L = 28 windows (seven days), where n_ut is the number of past windows available:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:27-30,149 'BASELINE_WINDOWS = 28', 'PRIOR_COUNT = 0.5', 'PRIOR_WINDOWS = 7'
4. [CONFIDENCE LEVEL]: High — Exact.

**S145**
1. [STATEMENT]: A Poisson CUSUM [29] accumulates evidence that the count has risen by δ = 1 report per window above that rate, and raises a spike when the score reaches h (the score restarts at zero after each alarm):
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:35-36,150-154 'k = CUSUM_SHIFT / math.log((rate + CUSUM_SHIFT) / rate)', 'score = 0.0  # reset'
4. [CONFIDENCE LEVEL]: High — Exact.

**S146**
1. [STATEMENT]: The prior (a, b) keeps new and quiet cases from alerting on a single complaint.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:9-13
4. [CONFIDENCE LEVEL]: Medium — The rule's stated intent; not separately measured.

**S147**
1. [STATEMENT]: Because one problem can still be split across cases, similar same-product cases are summed into alert groups and tested the same way, while the cases themselves stay separate.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/alert_groups.py:1-14
4. [CONFIDENCE LEVEL]: High — Implemented (99th-percentile, average linkage).

**S148**
1. [STATEMENT]: In the running example, 5 OTP complaints in one window against a usual rate of 0.1 raise a spike.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Arithmetic: λ=0.1 → k=1/ln 11=0.417; S=5−0.417=4.58 ≥ 2
4. [CONFIDENCE LEVEL]: High — Correct by the formula in spike_detection.py, but illustrative (a usual rate of 0.1 is assumed).


## H. Phase 8 – Vague-Complaint Alarm

**S150**
1. [STATEMENT]: Vague complaints join no case, so no per-case detector can see them.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/vague_counter_confirm_results.txt:3-5 ('C: detected 0.00')
4. [CONFIDENCE LEVEL]: High — Measured.

**S151**
1. [STATEMENT]: They are counted per product p in the same windows, v_pt, with a baseline λ_pt computed as in Phase 7, and tested with a Poisson tail rule:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/unassigned_spikes.py:59; InsightDesk-claude-review/backend/services/spike_detection.py:59 (poisson_tail)
4. [CONFIDENCE LEVEL]: High — Implemented.

**S152**
1. [STATEMENT]: An alarm reports when the surge started and which cases were active in the same windows, so an outage reported only as “the app is not working” still reaches an operator.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/web/src/pages/admin/IncidentsPage.tsx:2 (useUnassignedSpikes)
4. [CONFIDENCE LEVEL]: Medium — The UI shows unassigned spikes; I did not verify the 'cases active in same windows' field.

**S153**
1. [STATEMENT]: The threshold was fixed before testing: among p ∈ {0.01, 0.001} and a minimum count m ∈ {2, 3, 4}, p < 0.001 with m = 2 was the loosest setting that kept false alerts at or below 2 per 100 windows on both tuning sets (p = 0.01 gave 3.35 on bug reports).
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:16-20 (grid m ∈ {2,3,4}, p ∈ {0.01,0.001}, false ≤ 2/100)
4. [CONFIDENCE LEVEL]: High — The grid and rule exist, but for the PER-CASE detector v2, not specifically the vague alarm; 'p = 0.01 gave 3.35 on bug reports' appears in NO file.

**S154**
1. [STATEMENT]: Confirmed unchanged on 588 reviews of unseen apps, the alarm detected every 10-complaint vague outage at a cost of 0.19 extra false alerts per 100 windows.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/vague_counter_confirm_results.txt:1,4 'n=10 … C+V: detected 1.00 … (vague counter adds 0.19)'
4. [CONFIDENCE LEVEL]: High — Exact.


## I. Phase 9 – Escalation and Root-Cause Explanation

**S156**
1. [STATEMENT]: A case is eligible for escalation when it is not vague and has at least three counted reports or an active spike of the case or its alert group:
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/escalation_policy.py:6-26 'MIN_REPORTS … 3'
4. [CONFIDENCE LEVEL]: High — Exact.

**S157**
1. [STATEMENT]: For an eligible case an LLM produces a grounded cause hypothesis as JSON with the fields cause, affected segment, action, severity, confidence and evidence, restricted to evidence in the case’s complaints and spike history.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/rca_service.py:24-29 (probable_cause, affected_segment, recommended_action, severity, confidence, source_evidence); InsightDesk-claude-review/reports/replay/rca_v3_rule.md:11-18
4. [CONFIDENCE LEVEL]: High — The fields match.

**S158**
1. [STATEMENT]: An operator reviews it in the dashboard, and an email reaches the department of the case’s topic only after the operator approves it.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/email_service.py; InsightDesk-claude-review/backend/routers/dashboard.py (escalate route)
4. [CONFIDENCE LEVEL]: Medium — The approval flow is in the dashboard; staging has email disabled.


## V. IMPLEMENTATION DETAILS


## A. Software Stack

**S161**
1. [STATEMENT]: The backend is a Python FastAPI service.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/main.py
4. [CONFIDENCE LEVEL]: High — FastAPI app.

**S162**
1. [STATEMENT]: Complaints, cases, 6-hour windows, alert history and root-cause reports are stored in Supabase (PostgreSQL), and case exemplar vectors in a Pinecone index.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/database/schema.sql:8-101 (topics, cases, complaints, complaint_windows, case_history, case_rca)
4. [CONFIDENCE LEVEL]: Medium — There is no alert-history table; spike state is stored on cases.

**S163**
1. [STATEMENT]: Embeddings come from sentence-transformers all-MiniLM-L6-v2.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/embedding_service.py (all-MiniLM-L6-v2)
4. [CONFIDENCE LEVEL]: High — Exact.

**S164**
1. [STATEMENT]: The LLM judge, the case-pair judge and the root-cause writer call gpt-oss-120b through the Groq API in JSON mode at temperature 0; a small local model can be configured instead.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/llm/provider.py:15 'DEFAULT_LOCAL_MODEL = "qwen3:1.7b"', :83-105 (Groq call with temperature 0, no response_format)
4. [CONFIDENCE LEVEL]: High — A local model is configurable; the app does NOT use Groq JSON mode (the experiments do).

**S165**
1. [STATEMENT]: Sentiment uses the Hugging Face transformers library, and topics use BERTopic with UMAP and HDBSCAN.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/sentiment/; InsightDesk-claude-review/backend/services/clustering_service.py:269-291
4. [CONFIDENCE LEVEL]: High — Exact.

**S166**
1. [STATEMENT]: A scheduler inside the API runs re-joining and topic upkeep every 6 hours.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/main.py:20-27
4. [CONFIDENCE LEVEL]: High — Exact.

**S167**
1. [STATEMENT]: The dashboard is a React and TypeScript application that shows cases, incidents, alert groups, the vague-complaint alarm and root causes, and approved escalations are sent by SMTP.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/web/src/pages/admin/*.tsx (Cases, Incidents, Topics, CaseDetail); InsightDesk-claude-review/backend/services/email_service.py:232-263 (SMTP)
4. [CONFIDENCE LEVEL]: High — Exact.

**S168**
1. [STATEMENT]: The pipeline is covered by unit tests and an end-to-end test of the API.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/tests/ (test_auth.py, test_dashboard_rca.py, …); InsightDesk-claude-review/test_e2e_local.py
4. [CONFIDENCE LEVEL]: High — The tests exist.


## B. Key Design Properties

**S170**
1. [STATEMENT]: • Bounded LLM use: the judge sees at most five same-product candidates, decides only inside the calibrated band, and makes one decision per complaint.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:45-47,104
4. [CONFIDENCE LEVEL]: High — Exact (same-product applies only when a product is given).

**S171**
1. [STATEMENT]: • Safe failure: a failed or uncertain judge answer opens a new case and never merges.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:214; InsightDesk-claude-review/backend/services/rejoin.py:13 'A judge failure never merges'
4. [CONFIDENCE LEVEL]: High — Exact.

**S172**
1. [STATEMENT]: • Stable online cases: membership does not depend on input order, so cases can carry counts, spike history and an escalation record.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_rule.md:34
4. [CONFIDENCE LEVEL]: Medium — Online decisions do depend on arrival order (RESULTS.md:41 measured shuffles). It is case IDs that stay stable, not membership regardless of order.

**S173**
1. [STATEMENT]: • Human approval: no escalation email leaves the system without an operator’s approval.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/routers/dashboard.py (escalate requires an admin action); InsightDesk-claude-review/run_test_backend.py (ADMIN_AUTH_REQUIRED)
4. [CONFIDENCE LEVEL]: Medium — Enforced by the UI flow; there is also a 'force' path that a person triggers.

**S174**
1. [STATEMENT]: • Reproducibility: every LLM decision is cached at temperature 0, so every reported run can be replayed.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/llm_judge_cache_*.jsonl; InsightDesk-claude-review/reports/replay/replay_llm_cache.jsonl
4. [CONFIDENCE LEVEL]: High — True for experiments and replays; the live app does not cache judge decisions.


## VI. DATASETS AND EVALUATION PROTOCOL


## A. Datasets

**S177**
1. [STATEMENT]: • Play Store reviews: 338 labelled reviews of six help-desk products (Zendesk, Freshdesk, Help Scout, Zoho Desk, LiveAgent, HappyFox), from a pool of 450 labelled by three team members.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/data/external/playstore_scored.csv (338 rows); playstore_all.csv (450); InsightDesk-claude-review/reports/topics/bertopic_eval.txt:1 (6 products)
4. [CONFIDENCE LEVEL]: High — Exact.

**S178**
1. [STATEMENT]: Labels follow a written codebook; inter-annotator agreement is Fleiss’ κ = 0.74.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Reproduced: InsightDesk-dedup/experiments/dedup/labelling_agreement.py --table team_labels_round2.csv → 'Fleiss kappa, exact code : 0.743 95% CI [0.630, 0.837]'
4. [CONFIDENCE LEVEL]: High — Correct only for the SECOND round; the first round (team_labels_v3_table.csv) gives 0.568. No file stores the printed result.

**S179**
1. [STATEMENT]: • Unseen products: 588 reviews of Intercom, Jira Service Management and ServiceNow, never used for tuning.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/new_apps_rule.md; InsightDesk-claude-review/reports/new_apps/replay_summary.txt:9-12 (179/200/209)
4. [CONFIDENCE LEVEL]: High — Exact.

**S180**
1. [STATEMENT]: • Bugzilla: Firefox (three samples) and Thunderbird reports, with the project’s own duplicate links as independent labels.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/data/external/firefox.csv, firefox2.csv, firefox3.csv, thunderbird.csv
4. [CONFIDENCE LEVEL]: High — The files exist.

**S181**
1. [STATEMENT]: • Retrieval at scale: 233,521 Firefox, Thunderbird and Eclipse reports with the public BugHub split.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/dbrd_benchmark_note.md:3-5 (115,814 + 32,551 + 85,156 = 233,521)
4. [CONFIDENCE LEVEL]: High — Exact sum.

**S182**
1. [STATEMENT]: • IT tickets: 1,000 Endava support tickets with category labels.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/endava/endava_results_FULL.txt:4 '1000 tickets, 127 category codes'
4. [CONFIDENCE LEVEL]: High — Exact.


## B. Credibility of the Labels

**S184**
1. [STATEMENT]: Each dataset’s ground truth comes from a different source, so no single labelling choice drives the results.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Summary of 185–204
4. [CONFIDENCE LEVEL]: Medium — Rhetorical summary.

**S185**
1. [STATEMENT]: • Bugzilla (independent, maintained by the projects).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labelling/mozilla_firefox.csv (RESOLVED,DUPLICATE rows)
4. [CONFIDENCE LEVEL]: High — In the data.

**S186**
1. [STATEMENT]: Duplicate links are created by Mozilla’s own triagers and developers during normal triage: a report is closed as RESOLVED DUPLICATE and linked to the report it repeats, after a person has compared the two.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labelling/mozilla_firefox.csv (Status RESOLVED, Resolution DUPLICATE, dup id column)
4. [CONFIDENCE LEVEL]: Medium — The data shows the links; 'after a person has compared' is assumed.

**S187**
1. [STATEMENT]: The labels predate this work, were made for engineering rather than research purposes, and the same Bugzilla histories are standard benchmarks for duplicate bug-report detection, including the public BugHub split used here.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/dbrd_benchmark_note.md:3-6 (logpai BugHub release)
4. [CONFIDENCE LEVEL]: High — Exact.

**S188**
1. [STATEMENT]: Because triagers link only the duplicates they notice, some true duplicates are unlinked; a correct merge of two unlinked duplicates is then scored as an error, so measured precision on Bugzilla is, if anything, conservative.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Reasoning
4. [CONFIDENCE LEVEL]: Medium — A logical argument; not measured (stated as such).

**S189**
1. [STATEMENT]: We did not measure how many duplicates are unlinked in our samples, so we make no claim about the size of this effect.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Self-description
4. [CONFIDENCE LEVEL]: High — Honest limitation.

**S190**
1. [STATEMENT]: [TODO: cite a published estimate of Bugzilla duplicate-link completeness, or keep this sentence as is.]
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: TODO placeholder
4. [CONFIDENCE LEVEL]: High — THIS IS A LEFT-OVER TODO IN THE PAPER: remove before submission.

**S191**
1. [STATEMENT]: • Play Store (human, three annotators).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labelling/team_labels_round2.csv (labeller column: Krisha, Krushnam, Sanyogita)
4. [CONFIDENCE LEVEL]: High — Exact.

**S192**
1. [STATEMENT]: Three team members labelled the reviews against a written codebook that defines a problem by its user-visible symptom (for example, “cannot log in” rather than “login”).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labels/playstore_codebook.csv
4. [CONFIDENCE LEVEL]: High — The codebook exists.

**S193**
1. [STATEMENT]: On a 50-review overlap labelled by all three, agreement is Fleiss’ κ = 0.74 (95% CI 0.63–0.84), conventionally read as substantial; disagreements were resolved by discussion, and a blind relabelling round checked consistency.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labelling_agreement.py output (0.743 [0.630,0.837], 50 of 50 rows); InsightDesk-dedup/experiments/dedup/build_recheck_sheet.py:2 (first round 0.568); InsightDesk-dedup/experiments/dedup/build_relabel_sheet.py:2-9 (blind relabel)
4. [CONFIDENCE LEVEL]: High — Numbers reproduced. The paper omits that 0.74 was reached after a re-check round that followed a failed first round (0.568 < 0.6).

**S194**
1. [STATEMENT]: As an external check, GPT, Claude and gpt-oss given the same codebook agree with the human key at κ = 0.68–0.70, about as well as the annotators agree with each other, which indicates the codebook is reproducible rather than idiosyncratic.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Recomputed from InsightDesk-dedup/experiments/dedup/results/llm_labels_playstore_vs_human.csv (0.696), _chatgpt_vs_human.csv (0.691), _sonnet55_vs_human.csv (0.676)
4. [CONFIDENCE LEVEL]: High — Reproduced at 0.68–0.70; no file prints these values.

**S195**
1. [STATEMENT]: The labels were fixed before any of the pipeline variants reported here was scored, and thresholds are always tuned and scored on disjoint halves.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/playstore_selection_rule.md:1 ('written … before Run 3'); InsightDesk-dedup/experiments/dedup/e5_three_way.py:862-866 (disjoint halves)
4. [CONFIDENCE LEVEL]: Medium — Disjoint halves are in code. But the deployed 0.8306/0.26 were calibrated on all 338 reviews, which includes the scoring halves (see 105).

**S196**
1. [STATEMENT]: • Unseen products.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Sub-heading bullet ('Unseen products.')
4. [CONFIDENCE LEVEL]: High — No claim.

**S197**
1. [STATEMENT]: Labels for Intercom, Jira Service Management and ServiceNow are the agreed key of two independent LLM labellers using the same codebook; we treat them as secondary evidence alongside the human and Bugzilla labels.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:2 (key X = Claude Sonnet 5.5, key Y = ChatGPT GPT-6); InsightDesk-dedup/experiments/dedup/results/tlow_short_text_rule.md:7 'agreed key of the two LLM labellers'
4. [CONFIDENCE LEVEL]: High — Exact.

**S198**
1. [STATEMENT]: The two labellers agree only moderately (pairwise κ = 0.38); the key keeps a pair as a duplicate only when both grouped it, so it is conservative but may still reflect shared LLM biases.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:4 'pair kappa 0.381'
4. [CONFIDENCE LEVEL]: High — Exact.

**S199**
1. [STATEMENT]: A human spot-check of 50 of these reviews is planned.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/spot_check/unseen_apps_spot_check.xlsx; InsightDesk-dedup/experiments/dedup/results/spot_check_hidden_key.csv
4. [CONFIDENCE LEVEL]: High — The sheet exists; the result is still pending.

**S200**
1. [STATEMENT]: [TODO: add its result.]
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: TODO placeholder
4. [CONFIDENCE LEVEL]: High — LEFT-OVER TODO IN THE PAPER: remove or fill.

**S201**
1. [STATEMENT]: • Endava IT tickets.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Sub-heading bullet ('Endava IT tickets.')
4. [CONFIDENCE LEVEL]: High — No claim.

**S202**
1. [STATEMENT]: Real IT service-desk tickets from a third domain: 1,000 tickets labelled only with one of 127 category codes.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/endava/endava_results_FULL.txt:4
4. [CONFIDENCE LEVEL]: High — Exact.

**S203**
1. [STATEMENT]: A category groups many different problems, so these labels test case purity, not duplicate detection, and are reported as a third-domain check only.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/endava/endava_rule.md
4. [CONFIDENCE LEVEL]: Medium — Reasonable reading of category labels.

**S204**
1. [STATEMENT]: • Synthetic complaints were used only to check that each component behaves as designed and are not part of any reported comparison.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/RESULTS.md:14 (488 synthetic complaints); InsightDesk-claude-review/reports/new_apps/replay_summary.txt:5
4. [CONFIDENCE LEVEL]: Medium — The synthetic set is used for component checks, but early experiments (RESULTS.md §1–5) were run on synthetic data.


## C. Protocol

**S206**
1. [STATEMENT]: Thresholds are tuned on one half of the problems and scored on the other half; we report the pooled scores of three held-out halves.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/e5_three_way.py:862-866 (seeds × halves); InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:2 'final halves s0A, s1A, s1B'
4. [CONFIDENCE LEVEL]: High — Exact.

**S207**
1. [STATEMENT]: Metrics are pairwise precision, recall and F1 over complaint pairs, B-cubed scores, and case precision (purity of each case).
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_corrected/new_apps_scores.txt (B3 P columns); InsightDesk-dedup/experiments/dedup/one_company_score.py:56-63 ('case P' = bcubed precision)
4. [CONFIDENCE LEVEL]: High — 'Case precision' in the code is B-cubed precision, not per-case purity as worded.

**S208**
1. [STATEMENT]: Every method has a threshold that trades precision against recall, so neither number alone can rank methods: any method reaches high precision by merging almost nothing, or high recall by merging almost everything.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Methodological statement
4. [CONFIDENCE LEVEL]: High — General reasoning.

**S209**
1. [STATEMENT]: We therefore compare methods in two ways.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Lead-in
4. [CONFIDENCE LEVEL]: High — No claim.

**S210**
1. [STATEMENT]: First, each baseline’s threshold is tuned for its best F1 on the tuning half, the setting most favourable to it.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_rule.md; InsightDesk-claude-review/reports/baselines/baselines_results.txt:3 (CLAP tuned eps per split)
4. [CONFIDENCE LEVEL]: High — Exact.

**S211**
1. [STATEMENT]: Second, because a wrong merge inflates counts and can trigger a false escalation while a missed duplicate only leaves two smaller cases, we also compare recall at equal precision, with every baseline threshold set to reach precision 0.80 on the tuning half.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_eqp.txt:1 'EQUAL PRECISION (tuning precision >= 0.8)'
4. [CONFIDENCE LEVEL]: High — Exact.

**S212**
1. [STATEMENT]: Confidence intervals come from a cluster bootstrap over problems in which pairs between two draws of the same problem are not counted; a simulation with known ground truth confirms 92–99% coverage for the nominal 95% intervals.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_correction_note.md:12-31 (pairs between copies not counted; coverage 92–99%)
4. [CONFIDENCE LEVEL]: High — Exact.

**S213**
1. [STATEMENT]: Every pipeline change was compared against the current version on identical data under a pass rule written before the run.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/*_rule.md (many pre-declared rules)
4. [CONFIDENCE LEVEL]: Medium — 'Every' change is a strong universal; many rules exist, but I could not verify all.


## D. Baselines

**S215**
1. [STATEMENT]: We compare against the methods other systems use for each step, run on identical data and scored with the same metric.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Lead-in
4. [CONFIDENCE LEVEL]: High — Summary.

**S216**
1. [STATEMENT]: For grouping: CLAP’s density clustering of app reviews, BERTopic topic grouping (the approach behind several commercial feedback tools), a single embedding-similarity threshold, a tuned cross-encoder threshold pipeline, and general-purpose LLMs used either as labellers or to group a whole batch in one call.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt; InsightDesk-dedup/experiments/dedup/results/external_ce_comparison.txt; InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_A.txt
4. [CONFIDENCE LEVEL]: High — Each baseline has a result file.

**S217**
1. [STATEMENT]: For spike detection: the z-score rule that commercial feedback-analytics tools apply per tag or theme, which alerts when a window’s count exceeds its mean by more than two standard deviations, applied to the same per-case counts.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/spike_detection.py:39-58 (compute_z_score); InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:3-6
4. [CONFIDENCE LEVEL]: High — Exact.

**S218**
1. [STATEMENT]: Topic models and clustering methods were not designed for problem-level grouping; we include them because commercial tools use them for this purpose, and score every method on the same task: placing reports of the same problem together and different problems apart.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:54
4. [CONFIDENCE LEVEL]: Medium — The justification is a generalisation.

**S219**
1. [STATEMENT]: Each method’s output is read as a partition (a topic, cluster or case per complaint) and scored pairwise against the same labels; each baseline is reported at the better of its published and tuned settings.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/baselines_rule.md
4. [CONFIDENCE LEVEL]: Medium — Scoring protocol.


## VII. RESULTS AND DISCUSSION


## A. Comparison with Published Methods and LLMs

**S222**
1. [STATEMENT]: TABLE II
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.

**S223**
1. [STATEMENT]: COMPETITORS EVALUATED ON OUR DATA
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.

**S224**
1. [STATEMENT]: InsightDesk has the highest F1 of all methods that keep stable online cases: 0.49 on Play Store, with precision 0.83 and recall 0.35.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:26; InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_A.txt:4 (batch F1 0.504 is higher)
4. [CONFIDENCE LEVEL]: High — True with the 'stable online cases' qualifier; the batch LLM has a higher F1.

**S225**
1. [STATEMENT]: Published duplicate finders given the same input, the same online procedure and their most favourable threshold reach F1 0.12–0.24; with their threshold chosen to reach precision 0.80 on the tuning half they recover about 1% of duplicate pairs on the held-out half, while InsightDesk recovers 35% at precision 0.83.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt:2-4 (F1 0.240/0.197/0.115); InsightDesk-dedup/experiments/dedup/results/published_baselines_eqp.txt:2-5 (R 0.008–0.010)
4. [CONFIDENCE LEVEL]: High — Exact. But the '35% at 0.83' comparison uses the t_low 0.40 run, while the baselines' file lists InsightDesk at 0.799/0.327.

**S226**
1. [STATEMENT]: Word and character overlap cannot separate different problems that share vocabulary, which is the case the LLM judge exists for.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt
4. [CONFIDENCE LEVEL]: Medium — Interpretation of the measured gap.

**S227**
1. [STATEMENT]: Fig. 4 places every method at its best-F1 setting.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/paper/img (Fig. 4)
4. [CONFIDENCE LEVEL]: High — Structural.

**S228**
1. [STATEMENT]: Topic models group by theme rather than by problem, and BERTopic’s precision of 0.16 shows how many unrelated complaints share a topic.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:7 'BERTopic topics (app) P 0.158'
4. [CONFIDENCE LEVEL]: High — Exact.

**S229**
1. [STATEMENT]: General-purpose LLMs given our own codebook label with precision 0.68–0.71, below InsightDesk without a codebook.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED in project files (only in Claude memory: memory/dedup-v2-experiments-state.md:229 'LLM labellers vs human labels pairwise P 0.68-0.71')
4. [CONFIDENCE LEVEL]: Medium — No result file in the project holds this; it may be true but is unbacked.

**S230**
1. [STATEMENT]: A single LLM call that groups a whole batch reaches a higher offline F1, but it is not stable: shuffling the input order leaves only 54% of its grouped pairs intact, which rules it out for counting and alerting.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED in project files. InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_A.txt:7 records the OPPOSITE test: 'identical prompts … 99.5% of review pairs grouped the same way'; the 54% shuffle figure exists only in memory/dedup-v2-experiments-state.md:229
4. [CONFIDENCE LEVEL]: High — The key argument against the batch LLM has no saved experiment; save the shuffle run or drop the number.

**S231**
1. [STATEMENT]: CLAP’s published setting reaches a similar precision (0.84) but finds only 2% of duplicate pairs.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:5 'CLAP eps 0.6 (published) P 0.839 … R 0.025'
4. [CONFIDENCE LEVEL]: High — Exact.

**S232**
1. [STATEMENT]: Re-joining recovers duplicates that online decisions split, on short reviews and long bug reports alike (Fig. 5).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:8-23
4. [CONFIDENCE LEVEL]: High — Exact.

**S233**
1. [STATEMENT]: On the Play Store held-out halves at the deployed setting it raises recall from 0.284 to 0.351 (+0.067, 95% CI +0.032 to +0.110) and F1 from 0.430 to 0.494 (+0.064, CI +0.025 to +0.112), at a cost in precision from 0.883 to 0.834 (CI −0.139 to +0.002).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:25-27 'RJ1 - R1: P -0.048 [-0.139,+0.002] R +0.067 [+0.032,+0.110] F1 +0.064 [+0.025,+0.112]'
4. [CONFIDENCE LEVEL]: High — Exact.

**S234**
1. [STATEMENT]: On bug reports precision is unchanged while recall rises by 11 points.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:11,23 (R 0.546→0.657, 0.609→0.721; P 0.963→0.961, 0.867→0.873)
4. [CONFIDENCE LEVEL]: High — +11 points each.

**S235**
1. [STATEMENT]: Without re-joining, the grouping step alone therefore reaches precision 0.88 on short reviews; the deployed system trades five points of it for a quarter more duplicates found.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:25-26 (0.883 → 0.834; 0.284 → 0.351 = +24%)
4. [CONFIDENCE LEVEL]: High — Derived arithmetic is correct.


## B. Generalisation

**S237**
1. [STATEMENT]: TABLE III
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.

**S238**
1. [STATEMENT]: RESULTS ON UNSEEN DATA (UPPER THRESHOLD FIXED)
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Table caption
4. [CONFIDENCE LEVEL]: High — Structural.

**S239**
1. [STATEMENT]: The same upper threshold transfers from short app reviews to long bug reports, and to products and a company never seen in tuning.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:24-49 ('calibrated on Play Store only'); InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt
4. [CONFIDENCE LEVEL]: High — Measured.

**S240**
1. [STATEMENT]: This transfer is also the main evidence that the rules of Section IV-C (the 0.97 precision target for t_high and the 20th percentile for t_low) give a robust operating point rather than one fitted to the tuning data.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Interpretation
4. [CONFIDENCE LEVEL]: Medium — Reasonable but an argument.

**S241**
1. [STATEMENT]: A sensitivity check supports this for t_high: around each half’s calibrated thresholds, lowering t_high by 0.03 or 0.08 keeps precision at 0.81–0.83 and F1 at 0.36–0.41 (calibrated setting: 0.81 and 0.39), while lowering it by 0.13 drops precision to 0.72.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:72-76 (P 0.831/0.808, F1 0.364/0.413; −0.13: P 0.722)
4. [CONFIDENCE LEVEL]: High — Exact.

**S242**
1. [STATEMENT]: A label-only check of the zone around t_high found that only 2 held-out Play Store reviews scored above it, both joined correctly, so short reviews almost never reach automatic joins and the judge does the deciding.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no file reports a label-only check with '2 reviews above t_high'; InsightDesk-dedup/experiments/dedup/results/review_stats.txt:1 shows 20 auto-joins ≥ t_high (4%) on Play Store)
4. [CONFIDENCE LEVEL]: Medium — Unsupported, and it seems to conflict with review_stats unless measured at 0.8306.

**S243**
1. [STATEMENT]: Raising t_low, measured with live judge calls, leaves recall unchanged (0.256–0.264) while precision rises to 0.87 at +0.09 and 0.91 at +0.14 and the share of complaints sent to the judge falls from 86% to 61%.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:90-94 (R 0.256–0.264; P 0.867, 0.906; judged 86% → 61%)
4. [CONFIDENCE LEVEL]: High — Exact.

**S244**
1. [STATEMENT]: The 20th-percentile rule is therefore conservative on short reviews.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Derived from 243
4. [CONFIDENCE LEVEL]: High — Follows.

**S245**
1. [STATEMENT]: Under a pre-declared confirmation on Firefox and Thunderbird, however, t_low = 0.40 left precision (0.912 vs 0.908) and recall (0.571 vs 0.578) essentially unchanged and reduced the judged share only from 96% to 90%, below the 10-point bar, because similarities of long bug reports mostly lie well above 0.40.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/tlow_confirm_results.txt:2-4; InsightDesk-dedup/experiments/dedup/results/tlow_confirm_rule.md:6-10
4. [CONFIDENCE LEVEL]: High — Exact; the 'because…' reason is inference.

**S246**
1. [STATEMENT]: A second pre-declared check on unseen short text, the 588 reviews of three unseen apps, met its bar: with t_low = 0.40 the judged share fell from 94% to 77%, precision rose from 0.608 to 0.635 and recall changed from 0.284 to 0.255, within the allowed 0.03.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/tlow_short_text_results.txt:2-4; InsightDesk-dedup/experiments/dedup/results/tlow_short_text_rule.md:8-11
4. [CONFIDENCE LEVEL]: High — Exact.

**S247**
1. [STATEMENT]: On the Play Store held-out halves, t_low = 0.40 gives precision 0.883, recall 0.284 and F1 0.430 before re-joining, against 0.810, 0.259 and 0.392, with 66% instead of 86% of complaints judged.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:91,97
4. [CONFIDENCE LEVEL]: High — Exact (with per-half t_high, not 0.8306).

**S248**
1. [STATEMENT]: InsightDesk therefore uses t_low = 0.40 for short-text channels (app reviews, chat) and keeps 0.26 for tickets, bug reports and its own complaint form; the unseen-app labels are LLM-made, so this setting is supported by secondary evidence.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/dedup_r1.py:30-31; InsightDesk-claude-review/tests/test_tlow_channel.py
4. [CONFIDENCE LEVEL]: Medium — Implemented per channel; 'its own complaint form' keeps 0.26 is visible in the test only by channel mapping.

**S249**
1. [STATEMENT]: Recall is higher on bug reports, whose descriptions are specific, than on 21-word reviews, where reports of one problem often share little wording.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED ('21-word reviews': measured mean is 26–28 words, see 21)
4. [CONFIDENCE LEVEL]: High — Same unsupported figure.

**S250**
1. [STATEMENT]: Complaint text varies by channel: a 21-word app review and a multi-paragraph bug report describe problems very differently.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED ('21-word app review')
4. [CONFIDENCE LEVEL]: High — Same unsupported figure; bug reports average 94 words (firefox3.csv).

**S251**
1. [STATEMENT]: When every method’s threshold is tuned on Play Store reviews and applied unchanged to Firefox reports, InsightDesk’s precision rises from 0.83 to 0.96, while surface-similarity methods break down: MinHash-LSH and SimHash merge almost every pair (precision 0.01–0.02), and BM25 falls to precision 0.56 (Fig. 3).
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_firefox3.txt:2-4 (BM25 0.560, MinHash 0.013, SimHash 0.021); InsightDesk 0.963 in InsightDesk-claude-review/reports/baselines/baselines_results.txt:11
4. [CONFIDENCE LEVEL]: High — Baselines are exact. '0.83 to 0.96' compares the deployed Play Store figure (with t_low 0.40 + re-joining) against Firefox R1 without re-joining.

**S252**
1. [STATEMENT]: Their scores depend on text length and shared vocabulary, so a cut tuned on short reviews admits nearly all pairs of long reports.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Explanation
4. [CONFIDENCE LEVEL]: Medium — A plausible mechanism, not tested.

**S253**
1. [STATEMENT]: InsightDesk’s thresholds act on length-insensitive embedding similarity and only settle clear cases; uncertain pairs are decided by an LLM that reads both texts.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Explanation
4. [CONFIDENCE LEVEL]: Medium — A design argument.

**S254**
1. [STATEMENT]: Baselines tuned on Firefox itself do better (CLAP F1 0.37, BERTopic 0.54) but remain below InsightDesk’s 0.78, and they require labelled data in each new format.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:12,14 (CLAP eps 0.6 F1 0.367; BERTopic 0.541)
4. [CONFIDENCE LEVEL]: High — The numbers match, but these are the PUBLISHED/default settings, not 'tuned on Firefox itself' as the sentence says.

**S255**
1. [STATEMENT]: In practice a new deployment can start from the shipped calibration with no labelled data in its own format.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Claim from transfer results
4. [CONFIDENCE LEVEL]: Medium — Supported in spirit by transfer (Table III); not separately tested.

**S256**
1. [STATEMENT]: Pairwise precision on unseen help-desk products (0.61–0.64) is lower than on the calibration data, so a small calibration set, or corrections that operators already make in the dashboard, would further improve a deployment.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/tlow_short_text_results.txt:2-3 (P 0.608, 0.635)
4. [CONFIDENCE LEVEL]: High — Exact.

**S257**
1. [STATEMENT]: On 1,000 Endava IT service tickets, with the same settings, 90% of InsightDesk’s cases fall within a single ticket category (case precision 0.904 [0.896, 0.947]), against 0.655 for the earlier cross-encoder pipeline, while it groups far fewer tickets, as category labels are coarser than problems.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/endava/endava_results_FULL.txt:5-6 'case P 0.904 [0.896,0.947]', main branch 'case P 0.655'
4. [CONFIDENCE LEVEL]: High — Exact. Pairwise F1 is LOWER for R1 (0.007 vs 0.037), and the paper softens this as 'groups far fewer tickets'.


## C. Incident Detection

**S259**
1. [STATEMENT]: Outbreaks were simulated by moving the real reviews of one problem into a short burst inside a 30-day stream of 6-hour windows.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:6 '120 six-hour windows each' (= 30 days)
4. [CONFIDENCE LEVEL]: High — Exact.

**S260**
1. [STATEMENT]: On unseen Firefox and Thunderbird streams, the CUSUM detects 76% of outbreaks per case and 91% per alert group, at 0.38 and 0.69 false alerts per 100 windows; on short Play Store reviews, where outbreaks split across more cases, it detects 42–43% at 0.06.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/cusum_confirm_results.txt:2-3; InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:15-16
4. [CONFIDENCE LEVEL]: High — Exact.

**S261**
1. [STATEMENT]: The z-score rule used by commercial feedback tools detects none on the same counts: with zero to two complaints per window a standard deviation gives no stable baseline.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:3-6 'detected 0% of simulated outbreaks'
4. [CONFIDENCE LEVEL]: High — Exact.

**S262**
1. [STATEMENT]: We compared the standard small-count alternatives on the same simulations.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Lead-in
4. [CONFIDENCE LEVEL]: High — No claim.

**S263**
1. [STATEMENT]: A raw count rule either over-alerts (at least 2 reports: 0.72–4.33 false alerts per 100 windows) or misses most outbreaks (at least 3: 25–49% detected), so a model of the baseline rate is needed.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:9,11,25,27 (0.72/4.33; 0.25/0.49)
4. [CONFIDENCE LEVEL]: High — Exact.

**S264**
1. [STATEMENT]: A Poisson tail test on each window (count ≥ 2, P < 0.001) detected 71% and 84% on the unseen streams at 1.20 and 1.75 false alerts, three times the CUSUM’s, which is why InsightDesk uses the CUSUM.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/cusum_confirm_results.txt:2-3 (v2 0.71/1.20, 0.84/1.75)
4. [CONFIDENCE LEVEL]: High — Exact; 'three times' = 1.20/0.38 = 3.2 and 1.75/0.69 = 2.5.

**S265**
1. [STATEMENT]: An EWMA chart on the same baseline (α 0.2–0.3, L 2–3) reached 86% detection on bug reports but at 3.2–3.6 false alerts per 100 windows, about nine times the CUSUM’s.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:45-51 (cases 0.86 / 3.19–3.56)
4. [CONFIDENCE LEVEL]: High — Exact; 3.19 rounds to 3.2.

**S266**
1. [STATEMENT]: Across h ∈ {1, 1.5, 2, 3, 4} and δ ∈ {0.5, 1, 2}, h = 2 with δ = 1 is the knee: h = 1.5 adds 10 points of detection for ten times the false alarms, and h = 3 loses a third of detections; h = 2 was chosen on Play Store and a first Firefox sample and confirmed unchanged on the unseen streams under a pre-declared rule.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:28-43; InsightDesk-dedup/experiments/dedup/results/cusum_confirm_rule.md:3-7 ('Play Store and Firefox sample 2')
4. [CONFIDENCE LEVEL]: High — The grid is exact. But h was chosen on Firefox SAMPLE 2, not 'a first Firefox sample'.

**S267**
1. [STATEMENT]: Real complaint counts are overdispersed: on 17,236 Firefox reports from the last two years, per-component variance-to-mean ratios have median 1.60 and pooled value 2.37 (95% CI 1.70–3.30).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:3-4 'median 1.60 … pooled 2.37 [95% CI 1.70, 3.30]'
4. [CONFIDENCE LEVEL]: High — Exact.

**S268**
1. [STATEMENT]: Nominal Poisson probabilities therefore understate false alarms (the tail test fires 0.61 times per 100 real windows against 0.10 nominal), so all rates above are empirical.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:5 '0.61 per 100 component-windows (nominal at p = 0.001: at most 0.10)'
4. [CONFIDENCE LEVEL]: High — Exact.

**S269**
1. [STATEMENT]: Because the CUSUM looks for a rise of one report per window, it is relatively more sensitive on very busy cases; this regime was rare in our streams.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Reasoning
4. [CONFIDENCE LEVEL]: Medium — Logical property of k; 'rare in our streams' is not quantified.

**S270**
1. [STATEMENT]: Two blind LLM raters preferred InsightDesk’s grounded cause-explanation prompt over an alternative prompt (12:0 and 17:2) and found fewer unsupported claims.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/replay/rca_v3_rule.md:35-39 (GPT-6 preferred 2/17/1; Claude 0/12/8; unsupported 12→9, 6→2)
4. [CONFIDENCE LEVEL]: High — Exact.


## D. Vague-Complaint Alarm

**S272**
1. [STATEMENT]: About one review in five is too vague to join any case (Phase 4), so an outage that customers describe only as “the app is not working” is invisible to every per-case detector: they detected none of the simulated vague-only outages.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/review_stats.txt:1 (103/505 too vague); InsightDesk-dedup/experiments/dedup/results/vague_area_spike_results.txt:6-8 ('C: detected 0.00')
4. [CONFIDENCE LEVEL]: High — Exact.

**S273**
1. [STATEMENT]: Counting these complaints per product and testing for a surge detected every vague-only outage of 10 or more complaints and 52% of those with 5, over 300 simulated outages per size, while false alerts rose from 0.20–0.24 to 0.35–0.39 per 100 windows.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_review_results.txt:20 'n=5 detected 0.52, n=10/20 detected 1.00; false alerts 0.35-0.39/100w … vs 0.20-0.24'
4. [CONFIDENCE LEVEL]: High — Exact.

**S274**
1. [STATEMENT]: The result held on a second dataset of unseen help-desk apps.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/vague_counter_confirm_results.txt:1-5
4. [CONFIDENCE LEVEL]: High — Exact.


## E. Limitations

**S276**
1. [STATEMENT]: • Recall on short reviews.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S277**
1. [STATEMENT]: Pairwise recall on Play Store is 0.35.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:26 'R 0.351'
4. [CONFIDENCE LEVEL]: High — Exact.

**S278**
1. [STATEMENT]: Short reviews of one problem often look no more alike than reviews of different problems, and human annotators themselves agree only at κ = 0.74.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/rejoin_ceiling.txt; labelling_agreement output 0.743
4. [CONFIDENCE LEVEL]: Medium — The kappa is reproduced; the first half is a qualitative claim.

**S279**
1. [STATEMENT]: Re-joining recovers 24% more duplicate pairs at a cost of five points of precision, and alert groups plus the vague-complaint alarm keep incidents visible when a problem is split.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:25-26 (0.284 → 0.351 = +23.6%; P −4.9 points)
4. [CONFIDENCE LEVEL]: High — Arithmetic correct.

**S280**
1. [STATEMENT]: • Reports, not people.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S281**
1. [STATEMENT]: App-store reviews carry no user identity, so counts are reports.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/user_level_rule.md
4. [CONFIDENCE LEVEL]: Medium — Play Store data has no user ids.

**S282**
1. [STATEMENT]: Where a company’s complaints carry a user ID, counts can be made per user.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/database/supabase.py:165-169 (user-level repeat rule)
4. [CONFIDENCE LEVEL]: High — Implemented for the app's own users.

**S283**
1. [STATEMENT]: • Label source.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S284**
1. [STATEMENT]: Play Store labels were made by our team; Bugzilla results rely on independent duplicate links, and the unseen-product labels were cross-checked by LLM labellers.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/labelling/team_labels_round2.csv; InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:2
4. [CONFIDENCE LEVEL]: High — 'Cross-checked by' is loose: the unseen-product labels ARE made by LLMs, not merely cross-checked.

**S285**
1. [STATEMENT]: • LLM dependence.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S286**
1. [STATEMENT]: The judge uses an open-weight model through a rate-limited API; all decisions were cached so every reported run is reproducible.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/llm_judge_cache_*.jsonl; InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:1-24 (key rate limits)
4. [CONFIDENCE LEVEL]: High — True for experiments.

**S287**
1. [STATEMENT]: Measured on 30 live calls with the deployed prompt and five candidates, a judge decision takes 1.34 s at the median (2.09 s at the 90th percentile), uses about 480 input and 270 output tokens, and costs about $0.00024 at list price, or $0.24 per 1,000 judged complaints; embedding a complaint takes 21 ms on a CPU.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/latency_cost.txt:1-5 (481/273 tokens, $0.000244, 20.6 ms)
4. [CONFIDENCE LEVEL]: High — Exact after rounding.

**S288**
1. [STATEMENT]: • Deployment without local calibration.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S289**
1. [STATEMENT]: Out of the box, about 90% of complaints land in the right case (case precision 0.89–0.92 on an unseen company and unseen products), while pairwise precision there (0.61–0.64) shows that errors gather in a few large mixed cases.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: LOPO B-cubed P 0.887 (recomputed); InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:12-13 (B3 P 0.928–0.940); InsightDesk-dedup/experiments/dedup/results/tlow_short_text_results.txt:2-3
4. [CONFIDENCE LEVEL]: Medium — 'About 90% of complaints land in the right case' reinterprets B-cubed precision, and LOPO pairwise precision is 0.589 (ci_bootstrap.txt:15), outside the quoted 0.61–0.64.

**S290**
1. [STATEMENT]: Because every escalation requires human approval and spikes require a burst of reports, such errors surface as a count or a suggestion a reviewer can reject, never as an automatic action.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/backend/services/escalation_policy.py
4. [CONFIDENCE LEVEL]: Medium — Design argument.

**S291**
1. [STATEMENT]: InsightDesk is therefore usable as decision support from the first day; for counts that are trusted without review, a short calibration on the company’s own complaints is recommended.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Recommendation
4. [CONFIDENCE LEVEL]: Medium — Opinion.

**S292**
1. [STATEMENT]: • A single judge model.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S293**
1. [STATEMENT]: The judge is one open-weight model (gpt-oss-120b) run at temperature 0 with every decision cached; we did not measure robustness across models or error rates per complaint category, and do not claim its decisions are optimal.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/cross_model_rule.md (not run)
4. [CONFIDENCE LEVEL]: Medium — Honest limitation.

**S294**
1. [STATEMENT]: One systematic error was observed in a usability test: a complaint describing two problems can join one case, become one of its exemplars and then attract complaints about the other problem.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/bridging_size_check.txt:1
4. [CONFIDENCE LEVEL]: Medium — The 'usability test' observation is not itself in a file; the follow-up check is.

**S295**
1. [STATEMENT]: Tracing every join shows this is a minor source of error: joins made through judge-approved exemplars were 85–90% correct and account for 6 of 24 wrong joins on Play Store and 16 of 32 on bug reports, so excluding such exemplars would cost more correct joins than it prevents.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/bridging_size_check.txt:2-7 (35/41 = 85%, 147/163 = 90%; 6 of 24, 16 of 32)
4. [CONFIDENCE LEVEL]: High — Exact.

**S296**
1. [STATEMENT]: • Assumptions not yet measured.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Heading bullet
4. [CONFIDENCE LEVEL]: High — No claim.

**S297**
1. [STATEMENT]: We did not measure how many Bugzilla duplicates are unlinked, so we assume only that the true precision is at least the measured one.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Self-description; consistent with 189
4. [CONFIDENCE LEVEL]: High — Honest.

**S298**
1. [STATEMENT]: We did not test the judge with other models, nor a Bayesian changepoint detector.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/cross_model_rule.md (planned)
4. [CONFIDENCE LEVEL]: Medium — Consistent with files.


## VIII. CONCLUSION

**S300**
1. [STATEMENT]: InsightDesk turns raw complaints into stable problem cases online and builds incident signals on top of them.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Summary
4. [CONFIDENCE LEVEL]: High — Restates the method.

**S301**
1. [STATEMENT]: A calibrated similarity band lets an LLM judge decide only the uncertain matches, and a re-joining pass merges cases that online decisions split.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Summary
4. [CONFIDENCE LEVEL]: High — Restates the method.

**S302**
1. [STATEMENT]: On human-labelled reviews it reaches precision 0.83, recall 0.35 and F1 0.49, more than doubling the precision of a tuned cross-encoder pipeline (0.38) and outperforming published grouping methods and topic models on the same data.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/headline_short_text.txt:26; InsightDesk-dedup/experiments/dedup/results/external_ce_comparison.txt:5 'CE pf P 0.377'
4. [CONFIDENCE LEVEL]: High — 0.83 vs 0.38 is 'more than doubling'.

**S303**
1. [STATEMENT]: A per-channel lower threshold made short-text grouping both more precise and cheaper, and the same upper threshold transfers without retuning to bug reports (F1 0.78), unseen products and an unseen company.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/sensitivity_results.txt:97; InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:11
4. [CONFIDENCE LEVEL]: High — Matches.

**S304**
1. [STATEMENT]: Small-count spike statistics and a vague-complaint alarm make incident detection work at the volumes support desks actually see, and every escalation is approved by a person before it reaches a department.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Summary
4. [CONFIDENCE LEVEL]: Medium — Restates results.


## IX. FUTURE SCOPE

**S306**
1. [STATEMENT]: InsightDesk can be packaged with Docker and deployed on a cloud platform, with an open-weight LLM hosted locally for full data privacy and personal details removed from complaints before any LLM call.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked slide11 (future scope)
4. [CONFIDENCE LEVEL]: High — A future-work statement.

**S307**
1. [STATEMENT]: Corrections that operators already make in the dashboard can be used to calibrate each company automatically.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Future work
4. [CONFIDENCE LEVEL]: High — Not a factual claim.

**S308**
1. [STATEMENT]: The judge can be tested across models, multi-problem complaints can be kept out of case exemplars, and a Bayesian changepoint detector can be compared with the CUSUM.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Future work
4. [CONFIDENCE LEVEL]: High — Not a factual claim.

**S309**
1. [STATEMENT]: Per-user submission limits, multilingual complaints and automatic Jira tickets for approved escalations are further extensions.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Future work
4. [CONFIDENCE LEVEL]: High — Not a factual claim.


## Acknowledgment

**S311**
1. [STATEMENT]: We thank Prof.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Acknowledgment
4. [CONFIDENCE LEVEL]: High — Not a claim.

**S312**
1. [STATEMENT]: Ganesh Wadmare for his guidance throughout this project, and the faculty of the Department of Artificial Intelligence & Data Science for their feedback.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: Acknowledgment
4. [CONFIDENCE LEVEL]: High — Not a claim.

**S313**
1. [STATEMENT]: We also thank Vision Helpdesk, whose support setting shaped the problem studied here.
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/ppt/unpacked slide3 (Vision Helpdesk named)
4. [CONFIDENCE LEVEL]: Medium — Acknowledgment; the relationship is not documented.


## REFERENCES

**S315**
1. [STATEMENT]: [1]  J. Dąbrowski, E. Letier, A. Perini and A. Susi, “Analysing app reviews for software engineering: a systematic literature review,” Empirical Software Engineering, vol. 27, 2022.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S316**
1. [STATEMENT]: [2]  C. Gao et al., “Emerging app issue identification via online joint sentiment-topic tracing,” IEEE Trans. Software Engineering, 2022.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S317**
1. [STATEMENT]: [3]  T. Zhang, D. Han, V. Vinayakarao, I. C. Irsan, B. Xu, F. Thung, D. Lo and L. Jiang, “Duplicate bug report detection: How far are we?,” ACM Trans. Software Engineering and Methodology, 2023.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S318**
1. [STATEMENT]: [4]  T. Zhang, I. C. Irsan, F. Thung and D. Lo, “Cupid: Leveraging ChatGPT for more accurate duplicate bug report detection,” arXiv:2308.10022, 2023.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S319**
1. [STATEMENT]: [5]  R. Peeters, A. Steiner and C. Bizer, “Entity matching using large language models,” in Proc. EDBT, 2025.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S320**
1. [STATEMENT]: [6]  L. Zheng et al., “Judging LLM-as-a-judge with MT-Bench and Chatbot Arena,” in Proc. NeurIPS (Datasets and Benchmarks), 2023.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S321**
1. [STATEMENT]: [7]  J. Gu et al., “A survey on LLM-as-a-judge,” arXiv:2411.15594, 2024.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S322**
1. [STATEMENT]: [8]  A. Abbas, K. Tirumala, D. Simig, S. Ganguli and A. S. Morcos, “SemDeDup: Data-efficient learning at web-scale through semantic deduplication,” arXiv:2303.09540, 2023.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S323**
1. [STATEMENT]: [9]  N. Muennighoff, N. Tazi, L. Magne and N. Reimers, “MTEB: Massive text embedding benchmark,” in Proc. EACL, 2023.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S324**
1. [STATEMENT]: [10]  “iPACK: Incident-aware duplicate ticket aggregation for cloud systems,” in Proc. ICSE, 2023 (arXiv:2302.09520).
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S325**
1. [STATEMENT]: [11]  F. Liu et al., “TickIt: Leveraging large language models for automated ticket escalation,” in Proc. FSE (industry), 2025.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S326**
1. [STATEMENT]: [12]  T. Ahmed, S. Ghosh, C. Bansal, T. Zimmermann, X. Zhang and S. Rajmohan, “Recommending root-cause and mitigation steps for cloud incidents using large language models,” in Proc. ICSE, 2023.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S327**
1. [STATEMENT]: [13]  Y. Chen et al., “Automatic root cause analysis via large language models for cloud incidents,” in Proc. EuroSys, 2024.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S328**
1. [STATEMENT]: [14]  SentiSum, “What is anomaly detection?,” product documentation, help.sentisum.com, 2025.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S329**
1. [STATEMENT]: [15]  P. Lewis et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in Proc. NeurIPS, 2020.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S330**
1. [STATEMENT]: [16]  M. Grootendorst, “BERTopic: Neural topic modeling with a class-based TF-IDF procedure,” arXiv:2203.05794, 2022.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S331**
1. [STATEMENT]: [17]  D. Loureiro, F. Barbieri, L. Neves, L. Espinosa Anke and J. Camacho-Collados, “TimeLMs: Diachronic language models from Twitter,” in Proc. ACL (demo), 2022.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S332**
1. [STATEMENT]: [18]  F. Barbieri, J. Camacho-Collados, L. Espinosa Anke and L. Neves, “TweetEval: Unified benchmark and comparative evaluation for tweet classification,” in Findings of EMNLP, 2020.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S333**
1. [STATEMENT]: [19]  W. Wang, F. Wei, L. Dong, H. Bao, N. Yang and M. Zhou, “MiniLM: Deep self-attention distillation for task-agnostic compression of pre-trained transformers,” in Proc. NeurIPS, 2020.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S334**
1. [STATEMENT]: [20]  OpenAI, “gpt-oss-120b and gpt-oss-20b model card,” 2025.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S335**
1. [STATEMENT]: [21]  L. Villarroel, G. Bavota, B. Russo, R. Oliveto and M. Di Penta, “Release planning of mobile apps based on user reviews,” in Proc. ICSE, 2016.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S336**
1. [STATEMENT]: [22]  C. Sun, D. Lo, S.-C. Khoo and J. Jiang, “Towards more accurate retrieval of duplicate bug reports,” in Proc. ASE, 2011.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S337**
1. [STATEMENT]: [23]  N. Reimers and I. Gurevych, “Sentence-BERT: Sentence embeddings using Siamese BERT-networks,” in Proc. EMNLP, 2019.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S338**
1. [STATEMENT]: [24]  J. Devlin, M.-W. Chang, K. Lee and K. Toutanova, “BERT: Pre-training of deep bidirectional transformers for language understanding,” in Proc. NAACL, 2019.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S339**
1. [STATEMENT]: [25]  G. S. Manku, A. Jain and A. Das Sarma, “Detecting near-duplicates for web crawling,” in Proc. WWW, 2007.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S340**
1. [STATEMENT]: [26]  A. Z. Broder, “On the resemblance and containment of documents,” in Proc. Compression and Complexity of Sequences, 1997.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S341**
1. [STATEMENT]: [27]  L. McInnes, J. Healy and J. Melville, “UMAP: Uniform manifold approximation and projection for dimension reduction,” arXiv:1802.03426, 2018.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S342**
1. [STATEMENT]: [28]  R. J. G. B. Campello, D. Moulavi and J. Sander, “Density-based clustering based on hierarchical density estimates,” in Proc. PAKDD, 2013.
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/ / InsightDesk-claude-review/reports/Raw complaint dedup literature review.md (reference discussed in the local literature notes)
4. [CONFIDENCE LEVEL]: Medium — The reference appears in the local literature notes; I did not re-check its bibliographic details.

**S343**
1. [STATEMENT]: [29]  E. S. Page, “Continuous inspection schemes,” Biometrika, vol. 41, pp. 100–115, 1954.
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED (no local file; external citation not verifiable from the project folder)
4. [CONFIDENCE LEVEL]: Low — Not found in any local note. It may be a real work, but nothing in the folder backs it.

**S344**
1. [STATEMENT]: [Table 0] [2] | MERIT (TSE, 2022) | Topic share per app version | Topics, not problems | Problem-level cases
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/academic_feedback_systems.md:28,148
4. [CONFIDENCE LEVEL]: High — Matches the notes.

**S345**
1. [STATEMENT]: [Table 0] [3] | Duplicate bug reports (TOSEM, 2023) | BM25F / deep retrieval, top-k | Ranking only, no cases | Online cases with counts
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/semantic_dedup_methods.md; InsightDesk-claude-review/reports/Raw complaint dedup literature review.md
4. [CONFIDENCE LEVEL]: Medium — TOSEM study in the notes.

**S346**
1. [STATEMENT]: [Table 0] [4] | Cupid (arXiv, 2023) | LLM summary + BM25F | No grouping decision | Calibrated band + LLM judge
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/Raw complaint dedup literature review.md:88
4. [CONFIDENCE LEVEL]: High — Matches.

**S347**
1. [STATEMENT]: [Table 0] [5] | LLM entity matching (EDBT, 2025) | Zero-shot prompt per pair | Pairwise, costly | One judge call per complaint
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/semantic_dedup_methods.md:73-84
4. [CONFIDENCE LEVEL]: High — Matches.

**S348**
1. [STATEMENT]: [Table 0] [8] | SemDeDup (arXiv, 2023) | ε = 0.00095–0.03 | Near-copies only | Paraphrase-level matching
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/Raw complaint dedup literature review.md:141 'ε = 0.00095–0.03'
4. [CONFIDENCE LEVEL]: High — Exact.

**S349**
1. [STATEMENT]: [Table 0] [10] | iPACK (ICSE, 2023) | Ticket–alert linking | Needs cloud alerts | Raw complaint text only
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:14
4. [CONFIDENCE LEVEL]: High — Exact.

**S350**
1. [STATEMENT]: [Table 0] [11] | TickIt (FSE, 2025) | Predefined categories | Cannot open new problems | Open-ended problem cases
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:46
4. [CONFIDENCE LEVEL]: Medium — Notes say category fine-tuning.

**S351**
1. [STATEMENT]: [Table 0] [13] | RCACopilot (EuroSys, 2024) | Telemetry + LLM | Needs telemetry | Root cause from complaints
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/aiops_llm_analytics.md:94
4. [CONFIDENCE LEVEL]: High — Matches.

**S352**
1. [STATEMENT]: [Table 0] [14] | SentiSum (2025) | z > 2 per tag | Fails at 0–2 per window | Poisson CUSUM + alert groups
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:57 (Z-score vs ~100-day baseline; sensitivity Low/Medium/High)
4. [CONFIDENCE LEVEL]: Medium — The notes do NOT state 'z > 2'; SentiSum's threshold is an ML sensitivity setting.

**S353**
1. [STATEMENT]: [Table 12] CLAP [21] | eps 0.6 / 0.75 | Shared words merge problems | LLM judge separates them
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:3,5
4. [CONFIDENCE LEVEL]: High — Exact.

**S354**
1. [STATEMENT]: [Table 12] BM25, REP [22] | k1 1.2, b 0.75, cut 0.15–0.20 | Misses paraphrases | Semantic retrieval
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt:2 'thresholds [0.2, 0.15, 0.15]'
4. [CONFIDENCE LEVEL]: Medium — The cut matches; k1/b are standard defaults, which I did not re-check in code.

**S355**
1. [STATEMENT]: [Table 12] MinHash-LSH [26] | 3-char shingles, J ≥ 0.15 | Near-copies only | Matches meaning
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt:3 '3-char shingles … thresholds [0.15…]'
4. [CONFIDENCE LEVEL]: High — Exact.

**S356**
1. [STATEMENT]: [Table 12] SimHash [25] | 36–42 of 64 bits | Near-copies only | Matches meaning
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/published_baselines_results.txt:4 'thresholds [42, 36, 42]'
4. [CONFIDENCE LEVEL]: High — Exact.

**S357**
1. [STATEMENT]: [Table 12] BERTopic [16] | Library defaults | Themes, not problems | Symptom-level cases
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/baselines/baselines_results.txt:7
4. [CONFIDENCE LEVEL]: Medium — BERTopic baseline 'topics (app)'.

**S358**
1. [STATEMENT]: [Table 12] Embedding cut [23] | One cosine threshold | Unsafe or too narrow | Two cuts + judge
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:6 (cosine only)
4. [CONFIDENCE LEVEL]: High — Exact.

**S359**
1. [STATEMENT]: [Table 12] Cross-encoder [24] | Score cut 0.4834 | Fails in a stream | Stream-calibrated band
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/external_ce_comparison.txt:1 'threshold 0.4834'
4. [CONFIDENCE LEVEL]: High — Exact.

**S360**
1. [STATEMENT]: [Table 12] LLM labellers | Full codebook | Offline, needs codebook | Online, no codebook
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: Memory note only (see 229)
4. [CONFIDENCE LEVEL]: Low — No result file holds the labeller pairwise precision.

**S361**
1. [STATEMENT]: [Table 12] LLM batch grouping | One prompt per batch | Order-sensitive | Stable cases
2. [CLASSIFICATION]: Hallucination
3. [EXACT FILE PATH & LINE]: NONE - FABRICATED in project files ('order-sensitive'); InsightDesk-dedup/experiments/dedup/results/llm_batch_baseline_A.txt:7 shows 99.5% same-prompt stability
4. [CONFIDENCE LEVEL]: High — No shuffle experiment saved.

**S362**
1. [STATEMENT]: [Table 12] z-score rule [14] | z > 2 per tag | Unstable at small counts | Poisson CUSUM
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/spike_detector_v2_rule.md:3-6; InsightDesk-claude-review/research_notes/Raw complaint dedup literature review/industry_feedback_systems.md:57
4. [CONFIDENCE LEVEL]: Medium — z > 2 is not in the notes.

**S363**
1. [STATEMENT]: [Table 13] Second domain | Firefox, 3 samples | 0.87–0.96 | F1 0.78 with re-joining
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/ci_corrected/ci_bootstrap.txt:26,35,44 (0.92/0.96/0.96); InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:11
4. [CONFIDENCE LEVEL]: High — Firefox precision is 0.92–0.96; the 0.87 is Thunderbird's, not Firefox's.

**S364**
1. [STATEMENT]: [Table 13] Second domain | Thunderbird | 0.87 | F1 0.79 with re-joining
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/rejoin_confirm_RJ1_with_thunderbird.txt:23 'P 0.867 … RJ1 P 0.873 … F1 0.790'
4. [CONFIDENCE LEVEL]: High — Exact.

**S365**
1. [STATEMENT]: [Table 13] Unseen products | Intercom, Jira SM, ServiceNow | case 0.92 | No tuning on them
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/new_apps_scores_all.txt:12-13 (B3 P 0.928/0.940)
4. [CONFIDENCE LEVEL]: Medium — 'Case 0.92' = B-cubed precision of the harness run; the app replay is 0.94.

**S366**
1. [STATEMENT]: [Table 13] Unseen company | Leave-one-company-out | case 0.89 | Other companies' thresholds
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: LOPO B-cubed P 0.887 recomputed from lopo assignments + data/external/playstore_scored.csv
4. [CONFIDENCE LEVEL]: Medium — No file prints 0.89.

**S367**
1. [STATEMENT]: [Table 13] No product field | 889 bug reports, one stream | 0.90 | vs 0.91 with product
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/one_company_no_product_results.txt:2-3 (P 0.908 vs 0.899)
4. [CONFIDENCE LEVEL]: High — Exact.

**S368**
1. [STATEMENT]: [Table 13] Retrieval at scale | 233,521 bug reports | RR@5 0.46–0.56 | BM25F 0.41–0.44
2. [CLASSIFICATION]: Inference
3. [EXACT FILE PATH & LINE]: InsightDesk-dedup/experiments/dedup/results/dbrd_benchmark_note.md:14-15 (MiniLM 0.551/0.560/0.456; BM25 0.406/0.443/0.402); InsightDesk-dedup/experiments/dedup/results/rep_baseline_results.txt (REP full 0.433–0.442)
4. [CONFIDENCE LEVEL]: High — 0.46–0.56 is exact. 'BM25F 0.41–0.44' matches neither BM25 (0.40–0.44) nor REP-full (0.43–0.44) exactly.

**S369**
1. [STATEMENT]: [Table 13] Third domain | 1,000 Endava tickets | case 0.90 | Cross-encoder 0.66
2. [CLASSIFICATION]: Fact
3. [EXACT FILE PATH & LINE]: InsightDesk-claude-review/reports/endava/endava_results_FULL.txt:5-6
4. [CONFIDENCE LEVEL]: High — Exact.
