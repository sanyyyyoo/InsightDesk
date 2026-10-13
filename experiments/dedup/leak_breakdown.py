"""
Where does R1 lose recall? Stage attribution (as stage_attribution.py) on Play Store final halves
and on the blind Jira-only run (agreed Claude/ChatGPT key). Cached judge answers only, no API calls.

A review whose correct case (same true problem) already existed when it arrived, but which did not
join it, is a recall leak; it is attributed to the stage that lost it. Reviews whose true problem
had no case yet are not leaks.

  python experiments/dedup/leak_breakdown.py
"""

import collections
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import e5_three_way as e5  # noqa: E402
from e5_three_way import band_thresholds_wide, by_group, three_way  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from stage_attribution import ReplayJudge  # noqa: E402

RES = os.path.join(os.path.dirname(__file__), "results")


class Judge(ReplayJudge):
    def __init__(self, refs, issues, cache):
        self.refs, self.issues, self.view, self.vague = refs, issues, "founder", set()
        self.cache = {}
        for line in open(cache, encoding="utf-8"):
            r = json.loads(line)
            self.cache[r["key"]] = r["answer"]
        self.log, self.misses = {}, 0


def attribute(emb, issues, groups, refs, test, t_high, t_low, cache):
    judge = Judge(refs, issues, cache)
    labels, _, _ = by_group(lambda r: three_way(emb, r, t_high, t_low, judge, True), test, groups)
    out = collections.Counter()
    cases = {}
    for k, i in enumerate(test):
        g, lab = groups[i], int(labels[k])
        existing = {key: m for key, m in cases.items() if key[0] == g}
        majors = {key: collections.Counter(issues[m]).most_common(1)[0][0] for key, m in existing.items()}
        available = issues[i] in majors.values()
        joined_right = (g, lab) in existing and majors[(g, lab)] == issues[i]
        if not available:
            stage = "no correct case yet (not a leak)"
        elif joined_right:
            stage = "joined the correct case"
        elif i in judge.log:
            d = judge.log[i]
            if d["answer"] == -1:
                stage = "LEAK judge: vague gate" if d["correct_shown"] else "LEAK retrieval"
            elif d["answer"] == 0:
                stage = "LEAK judge: said none" if d["correct_shown"] else "LEAK retrieval"
            else:
                stage = "LEAK judge: wrong pick" if d["correct_shown"] else "LEAK retrieval (wrong pick)"
        elif (g, lab) in existing:
            stage = "LEAK auto-merge into wrong case"
        else:
            stage = "LEAK below band"
        if stage.startswith("LEAK retrieval"):
            right = [key for key, mj in majors.items() if mj == issues[i]]
            if all(existing[key][0] in judge.vague for key in right):
                stage = "LEAK retrieval: correct case hidden (started by a vague complaint)"
            else:
                best = max(float(np.max(emb[existing[key]] @ emb[i])) for key in right
                           if existing[key][0] not in judge.vague)
                stage = ("LEAK below band" if best < t_low else "LEAK retrieval: correct case not in top-5")
        out[stage] += 1
        cases.setdefault((g, lab), []).append(i)
    return out, judge.misses


def report(name, tot, misses):
    leaks = {k: v for k, v in tot.items() if k.startswith("LEAK")}
    n_leak = sum(leaks.values())
    could = n_leak + tot["joined the correct case"]
    print(f"\n{name}: {sum(tot.values())} reviews | correct case existed for {could} | joined it {tot['joined the correct case']} "
          f"({tot['joined the correct case'] / max(1, could):.0%}) | leaked {n_leak} | cache misses {misses}")
    for k, v in sorted(leaks.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  {v / max(1, n_leak):5.1%} of leaks  {k}")


def main():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    e5.MAX_CANDIDATES = 5

    # Play Store final halves (frozen R1)
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    ids = np.array(sorted(set(issues)))
    tot, miss = collections.Counter(), 0
    for seed, h in [(0, "A"), (1, "B"), (1, "A")]:
        rng = np.random.default_rng(seed)
        half = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a, b = np.where(np.isin(issues, list(half)))[0], np.where(~np.isin(issues, list(half)))[0]
        tune, test = (a, b) if h == "B" else (b, a)
        t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])
        c, m = attribute(emb, issues, groups, refs, test, t_high, t_low,
                         os.path.join(RES, "llm_judge_cache_playstore_founder_gated.jsonl"))
        tot.update(c)
        miss += m
    report("PLAY STORE final halves (human labels)", tot, miss)

    # Jira-only blind run, agreed LLM key, band calibrated on Play Store (as in the run)
    cal = load_ground_truth(path=DATA_PATHS["playstore"])
    tgt = load_ground_truth(path=DATA_PATHS["jira_agreed"])
    tgt["complaint_ref"] = tgt["complaint_ref"] + e5.EXT_REF_OFFSET
    cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
    raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
    df = apply_text_mode(raw, "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    is_cal = df["_cal"].to_numpy(dtype=bool)
    t_high, t_low = band_thresholds_wide(emb[is_cal], issues[is_cal], groups[is_cal])
    c, m = attribute(emb, issues, groups, refs, np.where(~is_cal)[0], t_high, t_low,
                     os.path.join(RES, "llm_judge_cache_jira_new_ext_playstore_founder_gated.jsonl"))
    report("JIRA only, blind run (agreed Claude/ChatGPT key)", c, m)


if __name__ == "__main__":
    main()
