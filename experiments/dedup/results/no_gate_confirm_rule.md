# "No hard gate" confirmation and combination with re-joining: pre-declared rule (2026-10-14, before any run)

Background (filtered_input_rule.md, evaluation only): on the Play Store final halves R1 without the hard
vague gate (judge prompt "strict": same feature AND same concrete symptom, answer 0 for complaints without
a concrete symptom, but those complaints' cases stay visible as candidates) gave P 0.797 R 0.350 F1 0.486
vs R1 0.810 / 0.259 / 0.392. Because those halves were the test halves, NG cannot be adopted on them; it
must be confirmed on data it was not chosen on.

Variant NG: R1 exactly as deployed (Play Store band, exemplar retrieval, top-5, founder view) with the
"strict" judge prompt instead of "gated". Confirmation data, untouched by this choice: Firefox sample 3,
Thunderbird sample (both benchmark labels) and the 588 new-app reviews (agreed LLM key, secondary).

1. NG adopted if ALL hold:
   - Firefox 3 precision >= 0.90 and Thunderbird precision >= R1's Thunderbird precision - 0.03 (0.837);
   - recall pooled over Firefox 3 + Thunderbird higher than R1 with the paired 95% interval (corrected
     cluster bootstrap) excluding 0;
   - new apps (agreed key): precision not below R1's by more than 0.05 (reported with interval).
2. NG + RJ1 (re-joining pass on NG's cases, unchanged RJ1) adopted over NG alone if NG is adopted AND, on
   Firefox 3 + Thunderbird pooled, precision >= 0.88 and recall higher than NG alone with the paired 95%
   interval excluding 0. Play Store final halves reported for both, not decisive.
Nothing is tuned; if NG fails, R1 + RJ1 stays the pipeline.
