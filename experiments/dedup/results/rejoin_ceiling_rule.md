# Case re-joining ceiling: diagnostic, declared before running (2026-10-13)

Question: R1 splits one true problem into several cases (fragments). A second pass that re-joins
cases can only help if a fragment's sibling fragments are among its most similar cases. How often
are they, and how much recall could a PERFECT case-pair judge recover? (No method is adopted from
this; it decides whether a re-joining experiment is worth running.)

Data: R1's final assignments (no new runs): Play Store final halves s0A, s1A, s1B (human labels),
Firefox sample 3 (benchmark labels), Jira-only blind run (agreed Claude/ChatGPT key).
Case similarity = highest cosine between any two members (MiniLM on the cleaned text, as R1's
exemplar retrieval), within the same product only. Case label = majority true problem.

Reported, per dataset:
- fragments: cases whose true problem also has another case; problems split into >= 2 cases;
- sibling recall@k (k = 1, 3, 5): share of fragments with a sibling fragment among their k most
  similar cases;
- top-1 neighbour purity: share of cases (with >= 1 neighbour) whose most similar case has the same
  true problem - the base rate a case-pair judge must beat;
- ceiling: pairwise P / R / F1 after a perfect judge merges every fragment linked to a sibling within
  its top-k (k = 1, 3, 5), vs R1 as is.
