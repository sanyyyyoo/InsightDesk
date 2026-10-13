"""
Case re-joining pass after R1 (rule: results/rejoin_rule.md).

R1's frozen cases are rebuilt from its cached judge answers (no new R1 calls); then case pairs
(each case with its 3 most similar cases in the product) go to a case-pair judge that sees up to
3 complaints per case. One merge per case per pass. RJ1 = one pass, RJ2 = two passes.

  python experiments/dedup/rejoin.py dev                 # selection on s0B (both variants)
  python experiments/dedup/rejoin.py confirm RJ1|RJ2     # one-shot: final halves + Firefox 3 (+ Jira, Thunderbird)
"""

import collections
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402
from e5_three_way import LLMJudge, band_thresholds_wide, by_group, three_way  # noqa: E402
from leak_breakdown import Judge  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RES = os.path.join(HERE, "results")
TOP_K, SHOW = 3, 3
B, SEED = 2000, 11

REJOIN = """Two groups of customer complaints about the same product were filed as separate problem cases.
Decide whether both cases report the SAME problem: the same feature AND the same failure, so that one
fix would solve both. Different wording or extra details do not matter. Being in the same general area
(e.g. both about login, or both about notifications) is NOT enough. If you are not sure, answer false.

Case A:
{a}

Case B:
{b}

Return JSON: {{"same": true or false}}"""


class PairJudge:
    def __init__(self, texts, refs, name):
        self.texts, self.refs = texts, refs
        self.llm = LLMJudge(texts, refs, "rejoin_" + name, "founder_latest", "v1")   # only its key rotation is used
        self.path = os.path.join(RES, "llm_rejoin_cache.jsonl")
        self.cache, self.calls = {}, 0
        if os.path.exists(self.path):
            for line in open(self.path, encoding="utf-8"):
                r = json.loads(line)
                self.cache[r["key"]] = r["same"]

    def same(self, a_rows, b_rows):
        a = [int(self.refs[m]) for m in a_rows[:SHOW]]
        b = [int(self.refs[m]) for m in b_rows[:SHOW]]
        key = json.dumps(sorted([a, b]))
        if key not in self.cache:
            fmt = lambda rows: "\n".join(f"- {self.texts[m]}" for m in rows[:SHOW])
            first, second = (a_rows, b_rows) if a <= b else (b_rows, a_rows)   # order fixed by key
            reply = self.llm._call(REJOIN.format(a=fmt(first), b=fmt(second)))
            self.cache[key] = bool(reply.get("same", False))
            self.calls += 1
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "same": self.cache[key]}) + "\n")
        return self.cache[key]


def rebuild(data, seed, half, calibrate=False):
    """R1's frozen cases for one partition, from the cached judge answers."""
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    e5.MAX_CANDIDATES = 5
    if calibrate:
        cal = load_ground_truth(path=DATA_PATHS["playstore"])
        tgt = load_ground_truth(path=DATA_PATHS[data])
        tgt["complaint_ref"] = tgt["complaint_ref"] + e5.EXT_REF_OFFSET
        cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
        raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
    else:
        raw = load_ground_truth(path=DATA_PATHS[data])
    df = apply_text_mode(raw, "boilerplate", enc)
    texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    if calibrate:
        is_cal = df["_cal"].to_numpy(dtype=bool)
        tune, test = np.where(is_cal)[0], np.where(~is_cal)[0]
        cache = {"firefox3": "firefox3_ext_playstore", "jira_agreed": "jira_new_ext_playstore",
                 "thunderbird": "thunderbird_ext_playstore"}[data]
    else:
        ids = np.array(sorted(set(issues)))
        rng = np.random.default_rng(seed)
        h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a, b = np.where(np.isin(issues, list(h)))[0], np.where(~np.isin(issues, list(h)))[0]
        tune, test = (a, b) if half == "B" else (b, a)
        cache = "playstore"
    t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])
    judge = Judge(refs, issues, os.path.join(RES, f"llm_judge_cache_{cache}_founder_gated.jsonl"))
    labels, _, _ = by_group(lambda r: three_way(emb, r, t_high, t_low, judge, True), test, groups)
    return dict(texts=texts, emb=emb, issues=issues, groups=groups, refs=refs, test=test,
                labels=np.asarray(labels), vague=set(judge.vague), t_low=t_low, misses=judge.misses)


def rejoin_pass(r, cases, pj):
    """cases: {case_id: [rows in arrival order]} -> merged copy, merges made."""
    emb, groups, vague = r["emb"], r["groups"], r["vague"]
    live = {c: m for c, m in cases.items() if m[0] not in vague}
    pairs = {}
    by_prod = collections.defaultdict(list)
    for c, m in live.items():
        by_prod[groups[m[0]]].append(c)
    for p, cs in by_prod.items():
        for a in cs:
            sims = sorted(((float((emb[live[a]] @ emb[live[b]].T).max()), b) for b in cs if b != a), reverse=True)
            for s, b in sims[:TOP_K]:
                if s >= r["t_low"]:
                    pairs[tuple(sorted((a, b)))] = s
    out = {c: list(m) for c, m in cases.items()}
    done, merges = set(), []
    for (a, b), s in sorted(pairs.items(), key=lambda kv: -kv[1]):
        if a in done or b in done:
            continue
        if pj.same(out[a], out[b]):
            out[a] = sorted(out[a] + out[b], key=lambda i: list(r["test"]).index(i))
            del out[b]
            done |= {a, b}
            merges.append((a, b))
    return out, merges, len(pairs)


def run_variant(r, pj, passes):
    cases = collections.defaultdict(list)
    for i, lab in zip(r["test"], r["labels"]):
        cases[f"{r['groups'][i]}|{lab}"].append(i)
    cases = dict(cases)
    issues = r["issues"]
    major = lambda m: collections.Counter(issues[m]).most_common(1)[0][0]
    all_merges, n_pairs = [], 0
    for _ in range(passes):
        before = {c: list(m) for c, m in cases.items()}
        cases, merges, np_ = rejoin_pass(r, cases, pj)
        n_pairs += np_
        all_merges += [(major(before[a]), major(before[b])) for a, b in merges]
    lab = {i: c for c, m in cases.items() for i in m}
    return np.array([lab[i] for i in r["test"]]), all_merges, n_pairs


def score(r, case_labels):
    _, iss = np.unique(r["issues"][r["test"]], return_inverse=True)
    return prf(*counts(np.asarray(case_labels).astype(str), iss, np.ones(iss.max() + 1)))


def dev():
    r = rebuild("playstore", 0, "B")
    pj = PairJudge(r["texts"], r["refs"], "playstore")
    base_labels = np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])
    b = score(r, base_labels)
    print(f"dev s0B (R1 rebuilt, cache misses {r['misses']}): R1 P {b[0]:.3f} R {b[1]:.3f} F1 {b[2]:.3f}")
    res = {}
    for name, passes in (("RJ1", 1), ("RJ2", 2)):
        lab, merges, n_pairs = run_variant(r, pj, passes)
        s = score(r, lab)
        right = sum(x == y for x, y in merges)
        ok = s[0] >= 0.75 and s[2] >= 0.615
        res[name] = (s, ok)
        print(f"  {name}: P {s[0]:.3f} R {s[1]:.3f} F1 {s[2]:.3f} | candidate pairs {n_pairs}, merges {len(merges)} "
              f"({right} correct) | {'QUALIFIES' if ok else 'does not qualify'}")
    print(f"  new judge calls: {pj.calls}")
    good = [k for k, (s, ok) in res.items() if ok]
    print("SELECTED: " + (max(good, key=lambda k: res[k][0][2]) if good else "none (tried, not adopted)"))


def boot_diff(parts):
    """Paired cluster bootstrap over true problems, pooled over partitions. parts: (issue, base, new)."""
    rng = np.random.default_rng(SEED)
    prep = []
    for issue, base, new in parts:
        _, iss = np.unique(issue, return_inverse=True)
        prep.append((iss, iss.max() + 1, base.astype(str), new.astype(str)))
    d = []
    for _ in range(B):
        tb, tn = np.zeros(3), np.zeros(3)
        for iss, n, base, new in prep:
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            tb += counts(base, iss, w)
            tn += counts(new, iss, w)
        d.append(np.array(prf(*tn)) - np.array(prf(*tb)))
    return np.percentile(np.array(d), [2.5, 97.5], axis=0)


def confirm(variant):
    passes = {"RJ1": 1, "RJ2": 2}[variant]
    parts, tot_b, tot_n = [], np.zeros(3), np.zeros(3)
    print(f"CONFIRM {variant} (one shot)")
    for seed, h in ((0, "A"), (1, "B"), (1, "A")):
        r = rebuild("playstore", seed, h)
        pj = PairJudge(r["texts"], r["refs"], "playstore")
        base = np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])
        new, merges, _ = run_variant(r, pj, passes)
        iss = r["issues"][r["test"]]
        _, ii = np.unique(iss, return_inverse=True)
        tot_b += counts(base, ii, np.ones(ii.max() + 1))
        tot_n += counts(new.astype(str), ii, np.ones(ii.max() + 1))
        parts.append((iss, base, new))
        print(f"  s{seed}{h}: R1 {np.round(score(r, base), 3)} -> {variant} {np.round(score(r, new), 3)} | "
              f"merges {len(merges)} ({sum(x == y for x, y in merges)} correct), cache misses {r['misses']}")
    pb, pn = prf(*tot_b), prf(*tot_n)
    lo, hi = boot_diff(parts)
    print(f"PLAY STORE pooled: R1 P {pb[0]:.3f} R {pb[1]:.3f} F1 {pb[2]:.3f} -> {variant} P {pn[0]:.3f} R {pn[1]:.3f} F1 {pn[2]:.3f}")
    print(f"  difference: P {pn[0] - pb[0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}], R {pn[1] - pb[1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}], "
          f"F1 {pn[2] - pb[2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    ext = {}
    for data in ("firefox3", "jira_agreed", "thunderbird"):
        f = os.path.join(RES, f"llm_judge_cache_{'jira_new' if data == 'jira_agreed' else data}_ext_playstore_founder_gated.jsonl")
        if not os.path.exists(f):
            print(f"  {data}: R1 cache not available, skipped")
            continue
        r = rebuild(data, None, None, calibrate=True)
        if r["misses"]:                                   # R1 run on this dataset not complete
            print(f"  {data}: R1 run incomplete ({r['misses']} uncached decisions), skipped")
            continue
        pj = PairJudge(r["texts"], r["refs"], data)
        base = np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])
        new, merges, _ = run_variant(r, pj, passes)
        sb, sn = score(r, base), score(r, new)
        ext[data] = sn
        print(f"  {data}: R1 P {sb[0]:.3f} R {sb[1]:.3f} F1 {sb[2]:.3f} -> {variant} P {sn[0]:.3f} R {sn[1]:.3f} F1 {sn[2]:.3f} | "
              f"merges {len(merges)} ({sum(x == y for x, y in merges)} correct), cache misses {r['misses']}")
    ok = pn[0] >= 0.78 and lo[1] > 0 and ext.get("firefox3", [0])[0] >= 0.90
    print(f"\nRULE: {'ADOPT' if ok else 'not adopted'} (P {pn[0]:.3f} >= 0.78? recall CI low {lo[1]:+.3f} > 0? "
          f"Firefox 3 P {ext.get('firefox3', [float('nan')])[0]:.3f} >= 0.90?)")


if __name__ == "__main__":
    {"dev": lambda: dev(), "confirm": lambda: confirm(sys.argv[2])}[sys.argv[1]]()
