"""
Offline unit checks for backend/services/dedup_r1.py (no Pinecone, no LLM).

Boundary values of every rule (BVA) plus the failure paths (error guessing).

  python test_dedup_r1.py
"""

import sys

import numpy as np

from backend.services import dedup_r1 as r1
from test_r1_equivalence import MemoryStore

T_HIGH, T_LOW = 0.83, 0.26
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"{'ok  ' if ok else 'FAIL'} {name}{(': ' + detail) if detail else ''}")


def vec_at(sim, base):
    """Unit vector with cosine `sim` to unit vector `base`."""
    other = np.zeros_like(base)
    other[1 if base[0] else 0] = 1.0
    other = other - (other @ base) * base
    other /= np.linalg.norm(other)
    return sim * base + np.sqrt(max(0.0, 1 - sim ** 2)) * other


def store_with_case(vague=False, product="Zendesk"):
    s = MemoryStore()
    base = np.zeros(8)
    base[0] = 1.0
    r1.start_case(1, base, 101, "founder text", product=product, vague=vague, store=s)
    return s, base


def judge_returning(specific=True, case=1, calls=None):
    def j(new_id, text, cands):
        if calls is not None:
            calls.append(len(cands))
        return specific, case
    return j


def failing_judge(new_id, text, cands):
    raise r1.JudgeError("timeout")


def run(sim, judge=None, vague=False, product="Zendesk", query_product="Zendesk", require_top1=False):
    s, base = store_with_case(vague, product)
    calls = []
    d = r1.decide(2, vec_at(sim, base), "new", product=query_product, store=s,
                  judge=judge or judge_returning(calls=calls), t_high=T_HIGH, t_low=T_LOW,
                  require_top1=require_top1)
    return d, calls


def main():
    # empty store
    d = r1.decide(1, np.ones(8), "first", store=MemoryStore(), judge=failing_judge, t_high=T_HIGH, t_low=T_LOW)
    check("first complaint ever -> new case, no LLM call", d.case_id is None and d.route == "new_empty")

    # BVA on T_HIGH
    for sim, route in [(0.8299, "judge_merge"), (0.83, "auto_merge"), (0.8301, "auto_merge")]:
        d, calls = run(sim)
        check(f"similarity {sim} -> {route}", d.route == route, f"got {d.route}, judge calls {len(calls)}")
    # BVA on T_LOW
    for sim, route in [(0.2599, "new_low"), (0.26, "judge_merge"), (0.2601, "judge_merge")]:
        d, calls = run(sim)
        check(f"similarity {sim} -> {route}", d.route == route, f"got {d.route}")

    # judge outcomes
    d, _ = run(0.5, judge_returning(specific=False, case=1))
    check("judge: not specific -> vague new case", d.case_id is None and d.vague and d.route == "vague")
    d, _ = run(0.5, judge_returning(case=0))
    check("judge: case 0 -> new case", d.case_id is None and d.route == "new_judge")
    d, _ = run(0.5, judge_returning(case=7))
    check("judge: case number out of range -> new case (no guessed merge)", d.case_id is None)
    d, _ = run(0.5, failing_judge)
    check("judge failure (timeout/quota/bad JSON) -> new case", d.case_id is None and d.route == "judge_failed")

    # vague cases are never judge candidates, but still take near-identical complaints
    d, calls = run(0.5, vague=True)
    check("vague case is not offered to the judge", calls == [0], f"candidates shown {calls}")
    d, _ = run(0.9, vague=True)
    check("vague case still takes a near-identical complaint (>= T_HIGH)", d.route == "auto_merge")

    # product isolation
    d, _ = run(0.95, product="Freshdesk", query_product="Zendesk")
    check("other product's case is never matched", d.case_id is None and d.route == "new_empty")
    d, _ = run(0.95, product="Zendesk", query_product=None)
    check("no product given -> whole company is searched", d.route == "auto_merge")

    # agreement rule: new complaint q; case 1 at cosine 0.6 (cosine top-1), case 2 at 0.5; judge picks case 2
    e = np.eye(8)
    for req, expect in [(True, None), (False, 2)]:
        s = MemoryStore()
        r1.start_case(1, 0.6 * e[0] + 0.8 * e[1], 101, "case one", product="Zendesk", store=s)
        r1.start_case(2, 0.5 * e[0] + np.sqrt(0.75) * e[2], 102, "case two", product="Zendesk", store=s)
        d = r1.decide(3, e[0], "new", product="Zendesk", store=s, judge=judge_returning(case=2),
                      t_high=T_HIGH, t_low=T_LOW, require_top1=req)
        check(f"agreement rule {'on' if req else 'off'}: judge picks the 2nd-ranked case -> "
              f"{'no merge' if expect is None else 'merge'}", d.case_id == expect,
              f"cosine order {[c.case_id for c in d.candidates]}, decision {d.case_id}")

    # exemplars: diversity boundary and the 5-exemplar cap
    s, base = store_with_case()
    tgt = r1.candidates_for(base, s)[0]
    check("near-copy (cosine 0.85) is not added as exemplar", not r1.add_member(tgt, vec_at(0.85, base), store=s))
    check("cosine 0.8499 is added as exemplar", r1.add_member(tgt, vec_at(0.8499, base), store=s))
    rng = np.random.default_rng(0)
    added = sum(r1.add_member(tgt, rng.normal(size=8), store=s) for _ in range(10))
    check("a case keeps at most 5 exemplars", len(s.exemplars(1)) == 5, f"{len(s.exemplars(1))} kept")
    meta = [md for _, md in s.vecs.values() if md["case_id"] == 1]
    check("every exemplar carries the founder text the judge sees",
          all(m.get("founder_text") == "founder text" and m.get("founder_id") == 101 for m in meta))

    # input edge cases (error guessing)
    d = r1.decide(9, np.zeros(8), "", store=store_with_case()[0], judge=failing_judge, t_high=T_HIGH, t_low=T_LOW)
    check("all-zero embedding (empty text) -> new case, no crash", d.case_id is None)

    print("ALL PASSED" if all(CHECKS) else "SOME CHECKS FAILED")
    return 0 if all(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
