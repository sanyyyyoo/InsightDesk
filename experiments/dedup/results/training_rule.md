# Trained duplicate models: pre-declared rule (2026-10-12, before any training)

Question: can a small trained neural model (MiniLM, ~22M parameters) make the
"same problem?" decision instead of the LLM judge, and does Endava category data help?

Models (trained on Colab GPU from the notebook train_dedup_models.ipynb; seed 7;
one fixed configuration each, no tuning on any test set):
A. cross-encoder (pair classifier), from cross-encoder/ms-marco-MiniLM-L6-v2,
   trained on: Firefox + Eclipse Platform duplicate pairs (train splits; Firefox
   groups used in our Firefox samples 1-3 removed) with hard negatives (other
   reports of the same Component), plus silver pairs from the R1 replay of the
   1,432 stream on NON-test reviews (same R1 case = positive; different case
   with cosine 0.26-0.83 = negative). The 338 scored Play Store reviews and
   Thunderbird are never used for training.
B. = A + Endava category pairs (same category code = positive, different = negative).
C. bi-encoder (embeddings), from all-MiniLM-L6-v2, contrastive training on the
   Firefox + Eclipse duplicate pairs + Endava same-category pairs; for retrieval only.

Tests (untouched by training):
1. Play Store held-out halves s0A, s1A, s1B: A and B replace the LLM judge in the
   same pipeline (same band, exemplar retrieval, top-5 cases, founder text);
   merge into the candidate with the highest probability if >= 0.5, else new case.
   Pairwise P/R/F1 with 95% intervals vs R1 (LLM) and cosine-only.
2. Firefox sample 3 and a NEW Thunderbird sample (built like the Firefox samples,
   seed 7, before any model exists): same pipeline, A and B vs cosine-only and
   oracle; R1 (LLM) on Thunderbird added when Groq quota allows.
3. C: Recall-Rate@k on the full Thunderbird history vs base MiniLM, and
   Recall@5 of the true case on the Play Store held-out halves.
A model "replaces the LLM" if on Play Store its precision >= 0.80 AND F1 >= R1's
F1 - 0.05 (0.342), and on Firefox 3 its precision >= 0.90. Otherwise reported as
not sufficient on its own (a hybrid with the LLM is a separate, later test).

## Outcome (2026-10-12)
- A, B as judge: FAIL. Play Store s0A P 0.486 / 0.390; Firefox 3 P 0.510 / 0.453 (R1 0.963); Thunderbird P 0.382 / 0.410.
- C retrieval, Recall-Rate@k (firefox_rrk.py on Colab GPU, results/*_rrk.csv), base MiniLM -> bi_C:
  Thunderbird (never in training, 1,585 queries) RR@1 0.316 -> 0.381, RR@5 0.560 -> 0.616, RR@10 0.655 -> 0.701, RR@20 0.731 -> 0.774;
  Eclipse (train split was in training, 2,327 test queries) RR@5 0.456 -> 0.523; Firefox (same, 4,236) RR@5 0.551 -> 0.593.
  BM25 below MiniLM everywhere (Thunderbird RR@5 0.443). C helps retrieval; whether it helps R1 on support reviews = V4 in new_apps_rule.md.
