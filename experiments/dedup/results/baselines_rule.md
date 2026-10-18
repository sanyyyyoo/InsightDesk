# Published-method baselines on our data: pre-declared rule (2026-10-13, before any run)

Purpose: no published system reports pairwise P/R on raw app reviews, so the closest published
methods are re-implemented and run on our labelled data with our protocol. No LLM calls.

1. CLAP (Villarroel et al., ICSE 2016), as published: preprocessing = lowercase, stop-word removal,
   Porter stemming, no synonym merging; TF-IDF vector space, cosine; DBSCAN with minPts = 2,
   distance = 1 - cosine, eps = 0.6 (their published value, tuned by them on another app).
   Deviation (recorded in advance): CLAP first sorts reviews into bug report / feature request /
   other with its own classifier, which is not available; here it clusters within each product
   only. Variant CLAP-tuned: eps chosen on the tuning half of each Play Store split (grid
   0.3-0.9 step 0.05, best pairwise F1), then applied to the held-out half; for Firefox / new apps
   the eps tuned on all Play Store tuning halves pooled.
2. Topic grouping (BERTopic as configured in the app, eval_bertopic.py config 8): each topic = one
   group; outlier topic -1 = singletons. Scored on the same reviews.
Data / scoring: Play Store final halves s0A, s1A, s1B (fine-level human labels; batch clustering of
each half per product), Firefox sample 3, new apps 588 (agreed LLM key). Pairwise P/R/F1 with the
corrected cluster bootstrap, next to R1 and R1 + RJ1 on the same reviews. Reported as measured.
Note in the paper: CLAP and BERTopic are batch methods that see all reviews at once; R1 is online
(each complaint decided on arrival), which is harder.
