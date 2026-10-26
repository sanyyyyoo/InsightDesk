"""
Case re-joining (RJ1): a pass over existing R1 cases that merges cases reporting the same problem.

R1 decides each complaint on arrival from one case's FIRST complaint, so one real problem often ends
up split over several cases. This pass compares each (non-vague) case with its 3 most similar cases
in the same product (similarity = highest cosine between any two members, >= T_LOW) and asks the LLM
judge, showing up to 3 complaints of each case, whether both report the same problem. Pairs are
processed from most to least similar; a case merges at most once per pass (no chains).

Adopted by pre-declared rule (experiments/dedup/results/rejoin_rule.md): Play Store held-out halves
recall 0.259 -> 0.327 at precision 0.810 -> 0.799 (difference not significant); Firefox 3 recall
0.546 -> 0.657 at precision 0.963 -> 0.961. plan() is the tested pass word for word
(test_rejoin_equivalence.py). A judge failure never merges. On by default; REJOIN_ENABLED=0 turns it off.
"""

import os
from collections import defaultdict

import numpy as np

from backend.services.dedup_r1 import T_LOW

TOP_K = 3
SHOW = 3

# Copied word for word from the tested pass (experiments/dedup/rejoin.py, REJOIN).
PROMPT_REJOIN = """Two groups of customer complaints about the same product were filed as separate problem cases.
Decide whether both cases report the SAME problem: the same feature AND the same failure, so that one
fix would solve both. Different wording or extra details do not matter. Being in the same general area
(e.g. both about login, or both about notifications) is NOT enough. If you are not sure, answer false.

Case A:
{a}

Case B:
{b}

Return JSON: {{"same": true or false}}"""


def enabled():
    return os.getenv("REJOIN_ENABLED", "1") == "1"


def plan(cases, emb, product_of, vague_cases, judge, t_low=None, arrival=None):
    """One pass. cases: {case_key: [member rows in arrival order]}; emb: unit vectors per row;
    product_of: {case_key: product}; vague_cases: case keys started by a vague complaint;
    judge(rows_a, rows_b) -> bool (same problem). Returns (merged cases dict, [(kept, absorbed)], pairs)."""
    t_low = T_LOW if t_low is None else t_low
    order = arrival if arrival is not None else {}
    live = {c: m for c, m in cases.items() if c not in vague_cases}
    by_prod = defaultdict(list)
    for c in live:
        by_prod[product_of[c]].append(c)
    pairs = {}
    for _, cs in by_prod.items():
        for a in cs:
            sims = sorted(((float((emb[live[a]] @ emb[live[b]].T).max()), b) for b in cs if b != a), reverse=True)
            for s, b in sims[:TOP_K]:
                if s >= t_low:
                    pairs[tuple(sorted((a, b)))] = s
    out = {c: list(m) for c, m in cases.items()}
    done, merges = set(), []
    for (a, b), _ in sorted(pairs.items(), key=lambda kv: -kv[1]):
        if a in done or b in done:
            continue
        if judge(out[a], out[b]):
            out[a] = sorted(out[a] + out[b], key=lambda i: order.get(i, i))
            del out[b]
            done |= {a, b}
            merges.append((a, b))
    return out, merges, len(pairs)


def llm_pair_judge(texts):
    """Judge for the app: the tested prompt; the case whose shown complaint ids sort first is Case A.
    Any failure answers False (no merge)."""
    from backend.llm.provider import generate_json

    def judge(rows_a, rows_b, ids=None):
        a, b = rows_a[:SHOW], rows_b[:SHOW]
        if ids is not None and [ids[i] for i in b] < [ids[i] for i in a]:
            a, b = b, a
        fmt = lambda rows: "\n".join(f"- {texts[i]}" for i in rows)
        try:
            return bool(generate_json(PROMPT_REJOIN.format(a=fmt(a), b=fmt(b)), cache=True).get("same", False))
        except Exception:
            return False
    return judge


def run_pass(db, embed, judge_factory=llm_pair_judge, move_vectors=None):
    """Run one pass on the live data. db: object with get_cases(), get_complaints(),
    reassign_case_complaints(from_id, to_id), move_case_windows(from_id, to_id),
    mark_case_merged(case_id, into_id), update_case(case_id, payload).
    embed(list of texts) -> unit vectors; move_vectors(from_id, to_id) moves the absorbed case's
    exemplar vectors (default: dedup_r1.move_case on Pinecone). Returns the merges made."""
    if move_vectors is None:
        from backend.services.dedup_r1 import move_case as move_vectors
    cases = {c["case_id"]: c for c in db.get_cases() if not c.get("merged_into")}
    rows = sorted((r for r in db.get_complaints() if r.get("case_id") in cases),
                  key=lambda r: (str(r.get("created_at")), r["complaint_id"]))
    if not rows:
        return []
    texts = [r.get("cleaned_text") or r["complaint_text"] for r in rows]
    shown = [r["complaint_text"] for r in rows]
    emb = np.asarray(embed(texts), dtype=float)
    emb = emb / np.maximum(np.linalg.norm(emb, axis=1, keepdims=True), 1e-12)
    members, product_of = defaultdict(list), {}
    for i, r in enumerate(rows):
        members[r["case_id"]].append(i)
        product_of.setdefault(r["case_id"], r.get("product") or "unknown")
    vague = {c for c, case in cases.items() if case.get("is_vague")}
    ids = [r["complaint_id"] for r in rows]
    j = judge_factory(shown)
    _, merges, _ = plan(dict(members), emb, product_of, vague, lambda a, b: j(a, b, ids))
    for keep, absorb in merges:
        db.reassign_case_complaints(absorb, keep)
        db.move_case_windows(absorb, keep)
        n = int(cases[keep].get("report_count") or 0) + int(cases[absorb].get("report_count") or 0)
        db.update_case(keep, {"report_count": n})
        db.mark_case_merged(absorb, keep)
        move_vectors(absorb, keep)
        cases[keep]["report_count"] = n
    return merges
