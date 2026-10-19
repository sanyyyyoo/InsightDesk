"""
R1 duplicate detection (the pipeline tested offline in experiments/dedup).

For a new complaint, within its company (and product, when given):
  1. score every existing case by its best-matching exemplar (cosine);
  2. best >= T_HIGH -> merge into the top case, no LLM call;
     best <  T_LOW  -> new case, no LLM call;
     in between     -> the LLM judge sees the new complaint and the FIRST
                       complaint of up to TOP_K candidate cases ("gated"
                       prompt) and answers {"specific", "case"};
  3. judge says not specific -> vague: new case that is never offered to the
     judge as a candidate (it can still take near-identical complaints at
     >= T_HIGH, as in the tested pipeline);
  4. a merged complaint becomes an extra exemplar of its case if the case has
     < MAX_EXEMPLARS and it is not a near-copy (cosine < DIVERSE_SIM) of one.
If the judge fails (timeout, quota, bad JSON) the complaint gets a new case:
never a guessed merge.

Tested (frozen, no re-tuning): Play Store within-company precision 0.82,
Firefox 0.92 / 0.96 / 0.96 on three fresh samples. Thresholds below are the
band calibrated on the Play Store data, the one used for the Firefox tests.
"""

import json
import os
from dataclasses import dataclass, field

import numpy as np

T_HIGH = float(os.getenv("DEDUP_T_HIGH", "0.8306"))
T_LOW = float(os.getenv("DEDUP_T_LOW", "0.26"))
# Short-text channels (app reviews, chat) use a higher lower threshold: on unseen short reviews it cut LLM
# calls by 17 points at equal precision and recall within 0.03 (tlow_short_text_rule.md); on long tickets and
# bug reports it made no real difference, so they keep T_LOW (tlow_confirm_rule.md).
T_LOW_SHORT = float(os.getenv("DEDUP_T_LOW_SHORT", "0.40"))
SHORT_TEXT_SOURCES = {s.strip().lower() for s in os.getenv(
    "DEDUP_SHORT_TEXT_SOURCES", "google_play_store,play_store,app_review,chat").split(",") if s.strip()}


def t_low_for(source):
    """The lower threshold for a complaint's channel."""
    return T_LOW_SHORT if (source or "").strip().lower() in SHORT_TEXT_SOURCES else T_LOW
TOP_K = int(os.getenv("DEDUP_TOP_K", "5"))
REQUIRE_TOP1 = os.getenv("DEDUP_REQUIRE_TOP1", "false").lower() == "true"
MAX_EXEMPLARS = 5
DIVERSE_SIM = 0.85
QUERY_VECTORS = 60            # vectors fetched per query; enough to rank the top cases by best exemplar

# Copied word for word from the tested judge (experiments/dedup/e5_three_way.py, PROMPT_GATED).
PROMPT_GATED = """You decide whether a new customer complaint reports the SAME specific problem as an
existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.
Different wording does not matter. Same general area (e.g. both about login) is NOT enough.

First decide if the new complaint is SPECIFIC: it names a concrete symptom, error or behaviour
(e.g. "access token revoked", "macros won't apply", "crashes when opening settings").
It is NOT specific if it only says something like "can't login", "doesn't work", "bad app", "too slow".

If it is not specific, or no case is the same specific problem, or you are not sure, answer case 0.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"specific": true or false, "case": <case number that is the same problem, or 0 if none>}}"""


@dataclass
class Candidate:
    case_id: int
    score: float
    founder_id: object = None
    founder_text: str = ""
    vague: bool = False
    product: object = None


@dataclass
class Decision:
    case_id: object                 # existing case to merge into, or None for a new case
    route: str                      # auto_merge | judge_merge | new_empty | new_low | new_judge | vague | judge_failed
    score: float = 0.0
    vague: bool = False
    candidates: list = field(default_factory=list)
    target: object = None           # the chosen Candidate when merging


class JudgeError(Exception):
    pass


def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n else v


def llm_judge(new_id, new_text, candidates):
    """The LLM call. Returns (specific, case number 1..len or 0)."""
    from backend.llm.provider import generate_json
    cases = "\n".join(f"Case {n + 1}: {c.founder_text}" for n, c in enumerate(candidates))
    try:
        reply = generate_json(PROMPT_GATED.format(new=new_text, cases=cases))
        return bool(reply.get("specific", True)), int(reply.get("case", 0) or 0)
    except Exception as exc:
        raise JudgeError(str(exc)) from exc


class PineconeStore:
    """Exemplar vectors in the existing Pinecone index: id '<case_id>:<k>', metadata
    case_id, founder_id, founder_text, vague, product. Older cases with one vector
    (id '<case_id>') still work: that vector counts as their first exemplar."""

    def __init__(self):
        from backend.services.embedding_service import index
        self.index = index

    def query(self, vec, top_k, product=None):
        kw = {"filter": {"product": product}} if product else {}
        res = self.index.query(vector=list(map(float, vec)), top_k=top_k, include_metadata=True, **kw)
        matches = res.get("matches", []) if isinstance(res, dict) else res.matches
        out = []
        for m in matches:
            md = m["metadata"] if isinstance(m, dict) else m.metadata
            sc = m["score"] if isinstance(m, dict) else m.score
            out.append((int(md["case_id"]), float(sc), dict(md)))
        return out

    def exemplars(self, case_id):
        ids = [str(case_id)] + [f"{case_id}:{k}" for k in range(MAX_EXEMPLARS)]
        res = self.index.fetch(ids=ids)
        vecs = res.get("vectors", {}) if isinstance(res, dict) else res.vectors
        out = []
        for v in vecs.values():
            out.append(np.asarray(v["values"] if isinstance(v, dict) else v.values, dtype=float))
        return out

    def add(self, case_id, k, vec, metadata):
        md = {key: val for key, val in metadata.items() if val is not None}
        md["case_id"] = int(case_id)
        self.index.upsert(vectors=[{"id": f"{case_id}:{k}", "values": list(map(float, vec)), "metadata": md}])

    def first_metadata(self, case_id):
        res = self.index.fetch(ids=[f"{case_id}:0", str(case_id)])
        vecs = res.get("vectors", {}) if isinstance(res, dict) else res.vectors
        for v in vecs.values():
            return dict(v["metadata"] if isinstance(v, dict) else v.metadata)
        return {}

    def delete_case(self, case_id):
        self.index.delete(ids=[str(case_id)] + [f"{case_id}:{k}" for k in range(MAX_EXEMPLARS)])


def move_case(from_case, to_case, store=None):
    """Re-joining: the absorbed case's exemplars become exemplars of the kept case (if room and not
    near-copies, with the kept case's founder text), then the absorbed case leaves the index so the
    judge is never offered it again."""
    store = store or default_store()
    md = store.first_metadata(to_case)
    kept = store.exemplars(to_case)
    for vec in store.exemplars(from_case):
        v = unit(vec)
        if len(kept) < MAX_EXEMPLARS and (not kept or float(max(unit(e) @ v for e in kept)) < DIVERSE_SIM):
            store.add(to_case, len(kept), v, {"founder_id": md.get("founder_id"), "founder_text": md.get("founder_text"),
                                              "vague": bool(md.get("vague", False)), "product": md.get("product")})
            kept.append(v)
    store.delete_case(from_case)


_default_store = None


def default_store():
    global _default_store
    if _default_store is None:
        _default_store = PineconeStore()
    return _default_store


def candidates_for(vec, store, product=None):
    """Existing cases ranked by their best-matching exemplar."""
    best = {}
    for case_id, score, md in store.query(vec, QUERY_VECTORS, product):
        c = best.get(case_id)
        if c is None:
            best[case_id] = Candidate(case_id, score, md.get("founder_id"),
                                      md.get("founder_text") or md.get("representative_text", ""),
                                      bool(md.get("vague", False)), md.get("product"))
        elif score > c.score:
            c.score = score
    return sorted(best.values(), key=lambda c: (-c.score, c.case_id))


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


def start_case(case_id, embedding, complaint_id, text, product=None, vague=False, store=None):
    """First exemplar of a new case; it carries the founder text the judge will see."""
    store = store or default_store()
    store.add(case_id, 0, unit(embedding), {"founder_id": complaint_id, "founder_text": text,
                                            "vague": bool(vague), "product": product})


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
