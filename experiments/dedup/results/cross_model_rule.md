# Cross-model judge (written 2026-10-19, before running). Report-only; the deployed judge is not changed by it.
Same pipeline, data, splits, per-half calibrated thresholds, prompt ("gated") and view ("founder") as the published
Play Store result; only the judge model changes: llama-3.3-70b-versatile (Groq) instead of openai/gpt-oss-120b.
Own answer cache (data tag playstore_llama), live calls. Reported: pooled pairwise P, R, F1 of R1 for both judges.
Reading: similar P/F1 (within the gpt-oss CI) = the design is not tied to one model; a large drop = the judge model
matters and must be re-validated per model (already stated as a limitation).
