# "One LLM does everything" baseline: pre-declared rule (written 2026-10-13, run 2026-10-14)

Reviewer question: why not give all complaints to one LLM and ask it to group them?

A. Same model as R1's judge, batch mode (no retrieval, no thresholds, no online decisions):
   gpt-oss-120b gets ALL reviews of one product in one held-out half in a single prompt (ids + text)
   and returns groups of reviews reporting the same problem, using R1's definition (same feature AND
   same concrete symptom; same area is not enough; a review with no concrete problem stays alone).
   One call per (half, product); temperature 0; JSON output; a review missing from the output is a
   singleton. Play Store final halves s0A, s1A, s1B (primary), fine-level human labels.
   New apps (588) per app only if one request fits the provider's per-minute token limit; otherwise
   reported as "not run (request too large for one call)" - itself part of the answer.
B. Frontier chat LLMs, already available, no new calls: the blind user-level label sheets made by
   ChatGPT (GPT-6) and Claude (Sonnet 5.5) for the 450 Play Store reviews are themselves batch
   groupings by one LLM. Scored as systems against the approved user-level mapping, on the same
   final halves as R1 (user-level stream). Caveat recorded: these were produced over many manual
   chat turns ("continue"), offline, with no time order.
Scoring: pairwise P / R / F1 with the corrected cluster bootstrap, next to R1 and R1 + RJ1 on the
same reviews. Also reported: calls and tokens per review, and whether group ids are stable when the
same prompt is run twice on s0A (fraction of review pairs grouped the same in both runs).
Interpretation fixed in advance: if a batch LLM matches or beats R1 on these offline batches, the
paper says so and argues R1's value from streaming, stable case ids, counting / spike detection and
cost; it does not hide the result.

## Outcome (2026-10-14 ~14:30)
A. gpt-oss-120b batch, one prompt per (held-out half, product), fine-level human labels, final halves pooled:
   R1 P 0.810 R 0.259 F1 0.392; R1+RJ1 0.799 / 0.327 / 0.464; batch 0.858 [0.74,0.95] / 0.357 / 0.504.
   18 calls, ~22k prompt tokens (~44 per review); identical prompts rerun on s0A: 99.5% of pairs grouped the same.
B. Blind user-level sheets vs the approved mapping (dev s0B): R1 0.736 / 0.209 / 0.325; ChatGPT 0.378 / 0.410 / 0.393;
   Claude 0.780 / 0.647 / 0.707 (other halves: Claude F1 0.71-0.83, ChatGPT 0.43-0.73). Caveat: the mapping and the
   user-level prompt share one author's definition; ChatGPT, with the same prompt, grouped far more broadly.
Interpretation (as fixed in advance): on small offline batches (~60-110 reviews per product) an LLM that sees all
reviews at once groups better than R1's online, one-complaint-at-a-time decisions - with the SAME model (gpt-oss).
R1's remaining advantages are the streaming ones (arrival-time decisions, stable case ids, counting, unbounded
history); the batch result points to periodic batch consolidation as the next design to test.
