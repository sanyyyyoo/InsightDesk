# Canonical rewrite: separation check, declared before running (2026-10-13)

Question: does rewriting each short review into a one-line problem statement make true duplicates
look more alike than unrelated reviews? Uses the existing cached rewrite (normalize.py llm_normalize,
results/llm_normalized_playstore.csv, all 338 scored Play Store reviews); no new calls.
Same MiniLM model, same pairs as before (all within-product pairs of the scored set).
Pass if: median similarity of true duplicate pairs >= 0.55 AND the 95th percentile of non-duplicate
pairs stays <= 0.45 (raw text: 0.43 and 0.42). If it fails, canonicalisation is not separating the
text and the idea stops here. Also reported (secondary): the same at user level
(labels/playstore_user_level_map.csv), and the share of true duplicate pairs above the non-duplicate
95th percentile.
