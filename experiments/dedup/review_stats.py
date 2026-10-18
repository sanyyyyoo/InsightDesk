"""
Reviewer-requested counts from the cached runs (no new LLM calls expected):
 1. routes per complaint: auto-join (>= t_high), judged in the band (-> joined / new / vague), auto-new (< t_low)
 2. re-joining pass: candidate case pairs, pairs judged, merges approved, merges correct (same majority problem)
 5. "too vague" rate of the judge

  python experiments/dedup/review_stats.py
"""
import collections
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rejoin as rj  # noqa: E402
from leak_breakdown import Judge  # noqa: E402

STATS = collections.Counter()
_choose = Judge.choose


def counting_choose(self, i, cases, shown=None):
    pick = _choose(self, i, cases, shown)
    STATS["judged"] += 1
    STATS["judge_join" if pick >= 0 else "judge_no"] += 1
    return pick


Judge.choose = counting_choose
_same = rj.PairJudge.same


def counting_same(self, a, b):
    out = _same(self, a, b)
    STATS["rj_judged"] += 1
    STATS["rj_approved"] += bool(out)
    return out


rj.PairJudge.same = counting_same


def one(data, seed, half, calibrate):
    STATS.clear()
    r = rj.rebuild(data, seed, half, calibrate=calibrate)
    n = len(r["test"])
    labs = r["labels"]
    joined = n - len(set(f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], labs)))   # complaints that joined a case
    route = dict(n=n, banded=STATS["judged"], judge_join=STATS["judge_join"], judge_no=STATS["judge_no"],
                 vague=len(r["vague"]), auto_join=joined - STATS["judge_join"])
    route["auto_new"] = n - route["banded"] - route["auto_join"]
    STATS.clear()
    _, merges, n_pairs = rj.run_variant(r, rj.PairJudge(r["texts"], r["refs"], "playstore" if data == "playstore" else data), 1)
    rjs = dict(candidates=n_pairs, judged=STATS["rj_judged"], approved=STATS["rj_approved"],
               correct=sum(a == b for a, b in merges))
    return route, rjs


def main():
    out = []
    runs = {"playstore": [("playstore", s, h, False) for s, h in ((0, "A"), (1, "B"), (1, "A"))],
            "firefox3": [("firefox3", None, None, True)], "thunderbird": [("thunderbird", None, None, True)]}
    for name, parts in runs.items():
        tot_r, tot_j = collections.Counter(), collections.Counter()
        for p in parts:
            a, b = one(*p)
            tot_r.update(a)
            tot_j.update(b)
        n = tot_r["n"]
        pct = lambda k: f"{tot_r[k]} ({tot_r[k] / n:.0%})"
        out.append(f"{name}: {n} complaints | auto-join >= t_high {pct('auto_join')} | auto-new < t_low or first "
                   f"{pct('auto_new')} | judged in band {pct('banded')} -> joined {tot_r['judge_join']}, "
                   f"not joined {tot_r['judge_no']} (of which too vague {tot_r['vague']})")
        out.append(f"   re-joining: {tot_j['candidates']} candidate case pairs, {tot_j['judged']} judged, "
                   f"{tot_j['approved']} merges approved, {tot_j['correct']} correct "
                   f"({tot_j['correct'] / max(tot_j['approved'], 1):.0%})")
        print("\n".join(out[-2:]), flush=True)
    open(os.path.join(HERE, "results", "review_stats.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
