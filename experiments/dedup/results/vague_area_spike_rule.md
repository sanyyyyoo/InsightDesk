# Vague and area counters for spike detection: pre-declared rule (2026-10-13, before any run)

Question (lever 4): R1 puts every vague complaint in its own one-complaint case, so a burst of
vague complaints ("app not working!!") - typical of an outage - can never trigger a case alert.
Do extra counters recover that signal without too many false alerts?

Stream: the labelled real Play Store reviews of Zendesk (243) and Freshdesk (124) (the only
products with >= 100 labelled reviews), with R1's real decisions from the 1,432-review app replay
(reports/replay/replay_assignments.csv: case_id, route = vague or not). Same simulation protocol
as spike_sim.py: 120 six-hour windows (30 days), every review placed in a random window, 300
trials per outbreak type, seed 5. Detector = deployed detector v2 (m 2, p 0.001) on every counter.

Counters compared:
- C   cases only (deployed);
- C+V cases + one vague counter per product (all complaints R1 routed "vague");
- C+V+A cases + vague counter + one counter per product area (a complaint's area = codebook area
  of its label). Two area sources: human labels (upper bound) and gpt-oss-120b labels
  (results/llm_labels_playstore.jsonl; an LLM area, the realistic case).

Outbreak types (injected copies of real reviews of the product, in windows b..b+1, b random in 60-110):
- S specific: an existing protocol outbreak (a true problem with >= 5 reviews: 30% spread before b,
  70% in b..b+1) - checks that the extra counters do not hurt.
- V vague outage: n = 10 copies of the product's R1-vague reviews (also n = 5, 20 reported).
  Copies get new singleton cases (as R1 would give them).
- A area outage: n = 10 copies of reviews of one area with >= 5 reviews (specific and vague mixed as
  they occur); a specific copy joins its original's case, a vague copy gets a new singleton case.
Detected = an alert in windows b..b+2 on a counter that contains outbreak complaints.
False alerts = alerts on counters with no outbreak complaint in that window, per 100 windows.

Adoption:
- vague counter: V detection (n 10) >= 0.80 AND false alerts of C+V <= 1.25 x those of C;
- area counters (gpt-oss areas): A detection gain over C+V >= 0.10 AND false alerts <= 1.25 x C+V.
Human-label areas are reported only as an upper bound. Nothing is tuned.
Limitation: areas come from a codebook here; in the app they would come from the judge's
free-text area (vague_second_look_rule.md), not tested here.
