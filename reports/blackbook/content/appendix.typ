// ============================================================================
//  APPENDICES
//  Each = heading starts a new appendix, numbered automatically (A1, A2, ...).
// ============================================================================

= Source Code of Key Functions

== Decision Band and LLM Judge

@lst:decide shows how the backend decides, for one complaint, whether it joins a case automatically, opens a new case, or goes to the LLM judge (Phases 3 and 4). It is taken from `backend/services/dedup_r1.py`.

#figure(
  ```python
  def decide(new_id, embedding, text, product=None, store=None, judge=llm_judge,
             t_high=None, t_low=None, top_k=None, require_top1=None):
      store = store or default_store()
      t_high = T_HIGH if t_high is None else t_high
      t_low = T_LOW if t_low is None else t_low
      top_k = TOP_K if top_k is None else top_k
      require_top1 = REQUIRE_TOP1 if require_top1 is None else require_top1
      order = candidates_for(unit(embedding), store, product)
      if not order:
          return Decision(None, "new_empty")
      best = order[0]
      if best.score >= t_high:
          return Decision(best.case_id, "auto_merge", best.score, target=best)
      if best.score < t_low:
          return Decision(None, "new_low", best.score)
      cands = [c for c in order if c.score >= t_low and not c.vague][:top_k]
      try:
          specific, pick = judge(new_id, text, cands)
      except JudgeError:
          return Decision(None, "judge_failed", best.score, candidates=cands)
      if not specific:
          return Decision(None, "vague", best.score, vague=True, candidates=cands)
      if 1 <= pick <= len(cands):
          chosen = cands[pick - 1]
          if require_top1 and chosen is not cands[0]:
              return Decision(None, "new_judge", best.score, candidates=cands)
          return Decision(chosen.case_id, "judge_merge", chosen.score, candidates=cands, target=chosen)
      return Decision(None, "new_judge", best.score, candidates=cands)
  ```,
  caption: [Decision band and LLM judge (backend/services/dedup_r1.py)],
) <decide>

== Exemplar Update

@lst:add-member stores a joined complaint as a new exemplar of its case only when the case has room and the complaint is worded differently from every existing exemplar (@eqt:exemplar-rule).

#figure(
  ```python
  def add_member(target, embedding, store=None):
      """Keep a merged complaint as an exemplar of its case (target: the chosen
      Candidate) if the case has room and it is not a near-copy of an exemplar."""
      store = store or default_store()
      vec = unit(embedding)
      ex = store.exemplars(target.case_id)
      if len(ex) < MAX_EXEMPLARS and (not ex or float(max(unit(e) @ vec for e in ex)) < DIVERSE_SIM):
          store.add(target.case_id, len(ex), vec, {"founder_id": target.founder_id, "founder_text": target.founder_text,
                                                   "vague": target.vague, "product": target.product})
          return True
      return False
  ```,
  caption: [Exemplar update (backend/services/dedup_r1.py)],
) <add-member>

== Poisson CUSUM

@lst:cusum computes the spike signal of one case from its zero-filled six-hour counts (Phase 7). It is taken from `backend/services/spike_detection.py`.

#figure(
  ```python
  BASELINE_WINDOWS = 28          # 7 days of 6-hour windows
  PRIOR_COUNT = 0.5              # prior: about one complaint every 14 windows (3.5 days)
  PRIOR_WINDOWS = 7
  CUSUM_SHIFT = 1.0             # rise of interest: one more report per window than usual
  CUSUM_H = 2.0                 # alarm level (cusum_confirm_rule.md)
  
  def evaluate_cusum(counts):
      """Poisson CUSUM on zero-filled counts (last entry = current window), plus the tail-test figures for display."""
  
      score, fire = 0.0, False
      for t, count in enumerate(counts):
          previous = counts[max(0, t - BASELINE_WINDOWS):t]
          rate = (sum(previous) + PRIOR_COUNT) / (len(previous) + PRIOR_WINDOWS)
          k = CUSUM_SHIFT / math.log((rate + CUSUM_SHIFT) / rate)
          score = max(0.0, score + count - k)
          fire = score >= CUSUM_H
          if fire and t < len(counts) - 1:
              score = 0.0                                   # reset after an earlier alarm
      ...
  ```,
  caption: [Poisson CUSUM spike detection (backend/services/spike_detection.py; constants and the scoring loop)],
) <cusum>

= Prompts

== Case Re-joining Prompt

@lst:rejoin-prompt is the prompt of the case-pair judge used by the re-joining pass (Phase 5), from `backend/services/rejoin.py`. The prompt of the complaint judge (Phase 4) is shown in Chapter 4.

#figure(
  ```text
  Two groups of customer complaints about the same product were filed as
  separate problem cases. Decide whether both cases report the SAME problem:
  the same feature AND the same failure, so that one fix would solve both.
  Different wording or extra details do not matter. Being in the same general
  area (e.g. both about login, or both about notifications) is NOT enough.
  If you are not sure, answer false.

  Case A:
  {a}

  Case B:
  {b}

  Return JSON: {"same": true or false}
  ```,
  caption: [Prompt of the case re-joining judge (backend/services/rejoin.py)],
) <rejoin-prompt>
