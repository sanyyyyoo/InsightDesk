"""
Re-joining (backend/services/rejoin.py): equivalence with the tested pass and the database steps.
No Supabase, no Pinecone, no new LLM calls (cached judge answers only).

  python test_rejoin.py
"""

import json
import os
import sys
import types

os.environ.setdefault("HF_HUB_OFFLINE", "1")


class _Stub(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return lambda *a, **k: []


sys.modules.setdefault("backend.database.supabase", _Stub("backend.database.supabase"))

import numpy as np  # noqa: E402

from backend.services import rejoin  # noqa: E402

EXP = "D:/PBL/InsightDesk-dedup/experiments/dedup"
results = []


def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")


# ---------------------------------------------------------------- 1. equivalence with the experiment
def equivalence():
    sys.path.insert(0, EXP)
    os.chdir("D:/PBL/InsightDesk-dedup")          # the experiment reads data/ relative to its repo
    import rejoin as exp                                   # experiments/dedup/rejoin.py
    cache = {}
    for line in open(os.path.join(EXP, "results", "llm_rejoin_cache.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        cache[r["key"]] = r["same"]
    total_misses = 0
    parts = [("playstore", 0, "B", False), ("playstore", 0, "A", False), ("playstore", 1, "B", False),
             ("playstore", 1, "A", False), ("firefox3", None, None, True), ("jira_agreed", None, None, True)]
    for data, seed, half, cal in parts:
        r = exp.rebuild(data, seed, half, calibrate=cal)
        misses = [0]

        def cached(rows_a, rows_b):
            a = [int(r["refs"][m]) for m in rows_a[:exp.SHOW]]
            b = [int(r["refs"][m]) for m in rows_b[:exp.SHOW]]
            key = json.dumps(sorted([a, b]))
            if key not in cache:
                misses[0] += 1
                return False
            return cache[key]

        class FakePJ:
            def same(self, a, b):
                return cached(a, b)

        cases = {}
        for i, lab in zip(r["test"], r["labels"]):
            cases.setdefault(f"{r['groups'][i]}|{lab}", []).append(i)
        exp_out, exp_merges, exp_pairs = exp.rejoin_pass(r, {c: list(m) for c, m in cases.items()}, FakePJ())
        product_of = {c: r["groups"][m[0]] for c, m in cases.items()}
        vague_cases = {c for c, m in cases.items() if m[0] in r["vague"]}
        arrival = {i: k for k, i in enumerate(r["test"])}
        app_out, app_merges, app_pairs = rejoin.plan({c: list(m) for c, m in cases.items()}, r["emb"], product_of,
                                                     vague_cases, cached, t_low=r["t_low"], arrival=arrival)
        same = (exp_merges == app_merges and exp_pairs == app_pairs
                and {c: list(m) for c, m in exp_out.items()} == app_out)
        total_misses += misses[0] + r["misses"]
        check(f"same merges as the tested pass: {data} {seed if seed is not None else ''}{half or ''}", same,
              f"({len(app_merges)} merges, {app_pairs} pairs, cache misses {misses[0]}, R1 cache misses {r['misses']})")
    check("no uncached judge answers needed", total_misses == 0, f"({total_misses})")


# ---------------------------------------------------------------- 2. database steps with a fake db
class FakeDB:
    def __init__(self, cases, complaints):
        self.cases = {c["case_id"]: dict(c) for c in cases}
        self.complaints = [dict(c) for c in complaints]
        self.windows = {(c["case_id"], "w1"): c.get("report_count", 1) for c in cases}
        self.calls = []

    def get_cases(self):
        return [c for c in self.cases.values() if not c.get("merged_into")]

    def get_complaints(self):
        return self.complaints

    def reassign_case_complaints(self, a, b):
        self.calls.append(("reassign", a, b))
        for c in self.complaints:
            if c["case_id"] == a:
                c["case_id"] = b

    def move_case_windows(self, a, b):
        self.calls.append(("windows", a, b))
        for (case, w), n in list(self.windows.items()):
            if case == a:
                self.windows[(b, w)] = self.windows.get((b, w), 0) + n
                del self.windows[(case, w)]

    def mark_case_merged(self, a, b):
        self.calls.append(("merged", a, b))
        self.cases[a]["merged_into"] = b

    def update_case(self, cid, payload):
        self.cases[cid].update(payload)


def db_steps():
    # product P: cases 1 and 2 are the same problem (similar vectors), 3 is different, 4 is vague
    vec = {"login a": [1, 0, 0], "login b": [0.95, 0.31, 0], "crash": [0, 1, 0], "useless": [0.9, 0.1, 0.4],
           "login c": [0.97, 0.2, 0]}
    cases = [{"case_id": 1, "report_count": 2}, {"case_id": 2, "report_count": 1},
             {"case_id": 3, "report_count": 1}, {"case_id": 4, "report_count": 1, "is_vague": True}]
    comps = [{"complaint_id": 10, "case_id": 1, "complaint_text": "login a", "product": "P", "created_at": "1"},
             {"complaint_id": 11, "case_id": 1, "complaint_text": "login c", "product": "P", "created_at": "2"},
             {"complaint_id": 12, "case_id": 2, "complaint_text": "login b", "product": "P", "created_at": "3"},
             {"complaint_id": 13, "case_id": 3, "complaint_text": "crash", "product": "P", "created_at": "4"},
             {"complaint_id": 14, "case_id": 4, "complaint_text": "useless", "product": "P", "created_at": "5"}]
    embed = lambda texts: np.array([vec[t] for t in texts], dtype=float)
    moved = []
    judge_login = lambda shown: (lambda a, b, ids: all("login" in shown[i] for i in a + b))
    db = FakeDB(cases, comps)
    merges = rejoin.run_pass(db, embed, judge_factory=judge_login, move_vectors=lambda a, b: moved.append((a, b)))
    check("same-problem cases merged (older case kept)", merges == [(1, 2)], f"{merges}")
    check("complaints, windows, count and vectors moved",
          db.calls == [("reassign", 2, 1), ("windows", 2, 1), ("merged", 2, 1)] and moved == [(2, 1)]
          and db.cases[1]["report_count"] == 3 and db.windows.get((1, "w1")) == 3
          and all(c["case_id"] == 1 for c in db.complaints if c["complaint_id"] in (10, 11, 12)))
    check("absorbed case hidden from case lists", 2 not in [c["case_id"] for c in db.get_cases()])
    check("vague case never merged", all(4 not in m for m in merges))
    db2 = FakeDB(cases, comps)
    fail = lambda shown: (lambda a, b, ids: (_ for _ in ()).throw(RuntimeError("quota")))
    try:
        m2 = rejoin.run_pass(db2, embed, judge_factory=lambda s: rejoin_safe(fail(s)), move_vectors=lambda a, b: None)
    except RuntimeError:
        m2 = None
    check("judge failure -> no merge", m2 == [] and db2.calls == [], f"{m2}")
    db3 = FakeDB(cases, comps)
    always = lambda shown: (lambda a, b, ids: True)
    m3 = rejoin.run_pass(db3, embed, judge_factory=always, move_vectors=lambda a, b: None)
    involved = [c for m in m3 for c in m]
    check("a case merges at most once per pass (no chains)", len(involved) == len(set(involved)), f"{m3}")
    os.environ.pop("REJOIN_ENABLED", None)
    check("off by default", not rejoin.enabled())


def rejoin_safe(j):
    """What llm_pair_judge does on any error: answer False."""
    def judge(a, b, ids):
        try:
            return j(a, b, ids)
        except Exception:
            return False
    return judge


if __name__ == "__main__":
    db_steps()
    if "--quick" not in sys.argv:
        equivalence()
    print("\nALL PASSED" if all(results) else f"\n{results.count(False)} FAILED")
    sys.exit(0 if all(results) else 1)
