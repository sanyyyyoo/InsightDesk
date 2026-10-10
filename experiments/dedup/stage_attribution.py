"""
Stage-by-stage error attribution for the final LLM-judge pipeline (no API calls).

Replays the frozen R1 configuration on the final held-out halves using only the
cached judge answers, and records for every review which stage decided its fate:

  first-in-product      no case existed yet in its product
  below band            best cosine < t_low  -> new case
  auto-merge            best cosine >= t_high -> merged without the judge
  judge                 t_low <= best < t_high -> LLM picked a case / none / vague

"Correct case available" = at arrival time some existing case's majority problem
equals the review's problem. Each review is then classified as correct or as an
error attributed to one stage:

  retrieval miss        correct case existed but was not among the top-5 shown
                        (or was hidden because its first complaint was gated vague)
  band miss             correct case existed but best cosine < t_low
  judge: none/vague     correct case was shown, judge said none or vague
  judge: wrong pick     judge picked a case with a different problem
  auto-merge wrong      merged above t_high into a different problem's case

  python experiments/dedup/stage_attribution.py
"""

import collections
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))

import e5_three_way as e5  # noqa: E402
from e5_three_way import LLMJudge, band_thresholds_wide, by_group, three_way  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RES = os.path.join(os.path.dirname(__file__), "results")
CACHE = os.path.join(RES, "llm_judge_cache_playstore_founder_gated.jsonl")
SPLITS = [(0, "A"), (1, "B"), (1, "A")]


class ReplayJudge(LLMJudge):
    """Answers only from the cache of the final run; records every decision."""

    def __init__(self, refs, issues):
        self.refs, self.issues, self.view, self.vague = refs, issues, "founder", set()
        self.cache = {}
        for line in open(CACHE, encoding="utf-8"):
            r = json.loads(line)
            self.cache[r["key"]] = r["answer"]
        self.log, self.misses = {}, 0

    def choose(self, i, candidates, shown=None):
        shown = [[c[0]] for c in candidates]
        key = json.dumps([int(self.refs[i]), [[int(self.refs[m]) for m in s] for s in shown]])
        if key not in self.cache:
            self.misses += 1
            answer = 0
        else:
            answer = self.cache[key]
        if answer == -1:
            self.vague.add(i)
        majors = [collections.Counter(self.issues[c]).most_common(1)[0][0] for c in candidates]
        self.last_shown = set(c[0] for c in candidates)
        self.log[i] = {"answer": answer, "correct_shown": self.issues[i] in majors,
                       "picked_major": majors[answer - 1] if 1 <= answer <= len(candidates) else None}
        return answer - 1 if 1 <= answer <= len(candidates) else -1


def main():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    issue_ids = np.array(sorted(set(issues)))
    e5.MAX_CANDIDATES = 5

    totals = collections.Counter()
    for seed, h in SPLITS:
        rng = np.random.default_rng(seed)
        half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
        a = np.where(np.isin(issues, list(half)))[0]
        b = np.where(~np.isin(issues, list(half)))[0]
        tune, test = (a, b) if h == "B" else (b, a)
        t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])
        judge = ReplayJudge(refs, issues)
        labels, _, _ = by_group(lambda r: three_way(emb, r, t_high, t_low, judge, True), test, groups)

        counts = collections.Counter()
        cases = {}                                   # (product, label) -> member rows so far
        for k, i in enumerate(test):                 # test rows are in arrival order
            g, lab = groups[i], int(labels[k])
            existing = {key: m for key, m in cases.items() if key[0] == g}
            majors = {key: collections.Counter(issues[m]).most_common(1)[0][0] for key, m in existing.items()}
            available = issues[i] in majors.values()
            joined = (g, lab) in existing
            if i in judge.log:
                d = judge.log[i]
                if d["answer"] == -1:
                    stage = "judge: vague gate (correct case shown)" if d["correct_shown"] else (
                        "retrieval miss" if available else "correct: vague, no case existed")
                elif d["answer"] == 0:
                    stage = "judge: said none (correct case shown)" if d["correct_shown"] else (
                        "retrieval miss" if available else "correct: new case")
                elif d["picked_major"] == issues[i]:
                    stage = "correct: judge merged"
                else:
                    stage = "judge: wrong pick"
            elif joined:
                stage = "correct: auto-merge" if majors[(g, lab)] == issues[i] else "auto-merge wrong"
            elif not existing:
                stage = "correct: first in product" if not available else "band miss"
            else:
                stage = "band miss" if available else "correct: new case"
            if stage == "retrieval miss":
                right = [key for key, mj in majors.items() if mj == issues[i]]
                if all(existing[key][0] in judge.vague for key in right):
                    stage = "retrieval miss: correct case hidden (its first complaint was gated vague)"
                else:
                    best = max(float(np.max(emb[existing[key]] @ emb[i])) for key in right
                               if existing[key][0] not in judge.vague)
                    stage = ("retrieval miss: correct case below t_low" if best < t_low
                             else "retrieval miss: correct case ranked below top-5")
            counts[stage] += 1
            cases.setdefault((g, lab), []).append(i)
        totals.update(counts)
        print(f"seed {seed}{h}: band [{t_low:.2f},{t_high:.2f}) cache misses {judge.misses} | "
              + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))

    n = sum(totals.values())
    print(f"\nall 3 final halves ({n} reviews):")
    for k, v in sorted(totals.items(), key=lambda kv: (kv[0].startswith("correct"), -kv[1])):
        print(f"  {v:4d}  {v / n:5.1%}  {k}")


if __name__ == "__main__":
    main()
