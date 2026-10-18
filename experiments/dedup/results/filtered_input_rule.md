# R1 on filtered (non-vague) input: evaluation note, declared before running (2026-10-13)

Question (user): how does the pipeline do on real reviews with vague ones removed upstream?
This is an evaluation, not a candidate change; nothing is adopted from it.

1. Play Store: the scored test set already excludes reviews people labelled vague / other /
   not a problem (338 of 450). On this filtered input R1's gate still drops ~24% of specific
   reviews. Run the same pipeline WITHOUT the gate (judge prompt "strict": same feature and same
   concrete symptom, no specificity step; e5 --judge-view founder --judge-prompt strict), on the
   final halves s0A, s1A, s1B, and report pairwise P/R/F1 (corrected intervals) next to R1 and the
   oracle. Interpretation: dedup quality if an upstream filter removed vague reviews perfectly.
2. New apps: R1's existing 588-review output, scored only on reviews that BOTH LLM keys code with a
   specific problem (not vague / other); no new runs.
