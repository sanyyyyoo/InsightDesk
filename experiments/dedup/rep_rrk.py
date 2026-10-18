"""
REP-style duplicate-bug-report baseline on the BugHub split (rule: results/rep_baseline_rule.md).

  python experiments/dedup/rep_rrk.py [firefox | thunderbird | eclipse_platform]

BM25F (title, description) retrieves the top 400 earlier reports; a linear REP-style score re-ranks them
with bigram BM25F and component / version / priority features. Weights are grid-searched on training-split
queries and scored once on the test-split queries that firefox_rrk.py uses.
"""

import itertools
import os
import sys
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

import firefox_rrk as fr  # reads sys.argv[1] for the project

K1, B, TOP, KS = 1.2, 0.75, 400, (1, 5, 10, 20)
N_TUNE = 2000


def queries_from(m, split_file):
    pos = {int(i): k for k, i in enumerate(m.Issue_id)}
    sp = pd.read_csv(os.path.join(fr.SRC, split_file))
    out = []
    for i in set(sp[sp.Duplicate.notna()].Issue_id.astype(int)):
        k = pos.get(i)
        if k is None or m.at[k, "bucket"] < 0:
            continue
        if (m.bucket.values[:k] == m.at[k, "bucket"]).any():
            out.append(k)
    return sorted(out)


def build(m):
    title = m.Title.fillna("").astype(str).tolist()
    desc = m.Description.fillna("").astype(str).tolist()
    mats = {}
    for ng in (1, 2):
        cv = CountVectorizer(lowercase=True, token_pattern=r"(?u)\b[a-z][a-z0-9_]{2,}\b", stop_words="english",
                             min_df=2, ngram_range=(ng, ng), dtype=np.float32)
        cv.fit([t + " " + d for t, d in zip(title, desc)])
        T, D = cv.transform(title).tocsr(), cv.transform(desc).tocsr()
        N = T.shape[0]
        df_ = np.asarray(((T + D) > 0).sum(axis=0)).ravel()
        idf = np.log(1 + (N - df_ + 0.5) / (df_ + 0.5)).astype(np.float32)
        for X in (T, D):                       # per-field length normalisation (BM25F)
            ln = np.asarray(X.sum(axis=1)).ravel()
            X.data /= np.repeat(1 - B + B * ln / max(ln.mean(), 1e-9), np.diff(X.indptr))
        mats[ng] = (T, D, idf, ((T + D) > 0).astype(np.float32).tocsr())
    return mats


def bm25f(mats, ng, wt, q, cand):
    T, D, idf, Q = mats[ng]
    qv = Q[q]
    cols = qv.indices
    if len(cols) == 0:
        return np.zeros(len(cand), np.float32)
    tf = (wt * T[cand][:, cols] + D[cand][:, cols]).toarray()
    return (tf / (K1 + tf)) @ idf[cols]


def run(m, mats, queries, w, feats):
    wt, a, c, v, p = w
    buckets = m.bucket.to_numpy()
    hits = np.zeros(len(KS))
    for q in queries:
        cand = np.arange(q)
        s1 = bm25f(mats, 1, wt, q, cand)
        top = np.argpartition(-s1, min(TOP, q - 1))[:TOP] if q > TOP else cand
        s = s1[top] + a * bm25f(mats, 2, wt, q, top)
        comp, ver, pri = feats
        s = s + c * (comp[top] == comp[q]) + v * (ver[top] == ver[q]) + p / (1 + np.abs(pri[top] - pri[q]))
        seen, ranked = set(), []
        for j in top[np.argsort(-s)]:
            if buckets[j] not in seen:
                seen.add(buckets[j])
                ranked.append(buckets[j])
            if len(ranked) >= max(KS):
                break
        hits += [buckets[q] in ranked[:k] for k in KS]
    return hits / len(queries)


def main():
    m, test_q = fr.load()
    extra = pd.read_csv(os.path.join(fr.SRC, fr.REPORTS), usecols=["Issue_id", "Priority", "Component", "Version"])
    extra = extra.drop_duplicates("Issue_id").set_index("Issue_id").reindex(m.Issue_id)
    pri = pd.to_numeric(extra.Priority.astype(str).str.extract(r"(\d)")[0], errors="coerce").fillna(3).to_numpy()
    feats = (extra.Component.astype(str).to_numpy(), extra.Version.astype(str).to_numpy(), pri)
    t0 = time.time()
    mats = build(m)
    print(f"{fr.PROJECT}: {len(m)} reports, {len(test_q)} test queries, matrices {time.time() - t0:.0f}s", flush=True)
    tune_q = queries_from(m, "train.csv")
    rng = np.random.default_rng(0)
    tune_q = sorted(rng.choice(tune_q, min(N_TUNE, len(tune_q)), replace=False))
    best, best_w = -1, None
    for wt in (1, 2, 3):                                   # stage 1: field weight + bigrams
        for a in (0, 0.5, 1):
            r5 = run(m, mats, tune_q, (wt, a, 0, 0, 0), feats)[1]
            print(f"  tune wt={wt} a={a}: RR@5 {r5:.3f}", flush=True)
            if r5 > best:
                best, best_w = r5, (wt, a, 0, 0, 0)
    wt, a = best_w[:2]
    text_w = best_w                                       # text only: the same input InsightDesk gets
    res_t = run(m, mats, test_q, text_w, feats)
    line_t = f"{fr.PROJECT}: REP-style TEXT ONLY test " + " ".join(f"RR@{k} {r:.3f}" for k, r in zip(KS, res_t)) + f" | weights {text_w}"
    print(line_t, flush=True)
    with open(os.path.join(fr.HERE, "results", "rep_baseline_results.txt"), "a", encoding="utf-8") as f:
        f.write(line_t + "\n")
    for c, v, p in itertools.product((0, 0.5, 1, 2), (0, 0.5, 1), (0, 0.5)):   # stage 2: metadata
        r5 = run(m, mats, tune_q, (wt, a, c, v, p), feats)[1]
        if r5 > best:
            best, best_w = r5, (wt, a, c, v, p)
    print(f"chosen weights (wt, a, c, v, p) = {best_w}, train RR@5 {best:.3f}", flush=True)
    res = run(m, mats, test_q, best_w, feats)
    line = f"{fr.PROJECT}: REP-style FULL (with metadata) test " + " ".join(f"RR@{k} {r:.3f}" for k, r in zip(KS, res)) + f" | weights {best_w}"
    print(line, flush=True)
    with open(os.path.join(fr.HERE, "results", "rep_baseline_results.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    main()
