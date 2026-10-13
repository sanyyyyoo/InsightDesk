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
