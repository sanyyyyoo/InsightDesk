"""
Recall-Rate@k on the full Firefox duplicate-bug-report benchmark (rule: results/firefox_rrk_rule.md).

  python experiments/dedup/firefox_rrk.py [firefox | thunderbird | eclipse_platform]
"""

import os
import re
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_firefox_dbrd import clean  # noqa: E402

PROJECTS = {"firefox": ("labelling", "mozilla_firefox.csv"),
            "thunderbird": ("labelling/thunderbird", "mozilla_thunderbird.csv"),
            "eclipse_platform": ("labelling/eclipse_platform", "eclipse_platform.csv")}
PROJECT = sys.argv[1] if len(sys.argv) > 1 else "firefox"
SRC = os.path.join(HERE, PROJECTS[PROJECT][0])
REPORTS = PROJECTS[PROJECT][1]
CACHE = os.path.join(HERE, "results", "firefox_rrk_cache" if PROJECT == "firefox" else f"{PROJECT}_rrk_cache")
KS = (1, 5, 10, 20)
TOP = 400                       # reports kept per query before grouping into buckets


def load():
    m = pd.read_csv(os.path.join(SRC, REPORTS),
                    usecols=["Issue_id", "Title", "Description", "Created_time"])
    m["ts"] = pd.to_datetime(m.Created_time, utc=True, errors="coerce")
    m = m.dropna(subset=["ts"]).sort_values(["ts", "Issue_id"]).reset_index(drop=True)
    links = pd.concat([pd.read_csv(os.path.join(SRC, f)) for f in ("train.csv", "test.csv")])
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for r in links.itertuples():
        if isinstance(r.Duplicate, str):
            for d in r.Duplicate.split(";"):
                parent[find(int(r.Issue_id))] = find(int(d))
    m["bucket"] = [find(int(i)) if int(i) in parent else -int(i) for i in m.Issue_id]
    te = pd.read_csv(os.path.join(SRC, "test.csv"))
    dup_ids = set(te[te.Duplicate.notna()].Issue_id.astype(int))
    pos = {int(i): k for k, i in enumerate(m.Issue_id)}
    queries = []
    for i in dup_ids:
        if i not in pos:
            continue
        k = pos[i]
        b = m.at[k, "bucket"]
        if b < 0:
            continue
        if (m.bucket.values[:k] == b).any():          # the true group has an earlier member
            queries.append(k)
    return m, sorted(queries)


def rr_from_scores(scores_fn, m, queries, name):
    buckets = m.bucket.to_numpy()
    hits = Counter()
    t0 = time.time()
    for n, q in enumerate(queries):
        s = scores_fn(q)                               # scores for reports 0 .. q-1
        top = np.argpartition(-s, min(TOP, len(s) - 1))[:TOP] if len(s) > TOP else np.arange(len(s))
        top = top[np.argsort(-s[top])]
        seen, ranked = set(), []
        for j in top:
            b = buckets[j]
            if b not in seen:
                seen.add(b)
                ranked.append(b)
            if len(ranked) >= max(KS):
                break
        for k in KS:
            hits[k] += buckets[q] in ranked[:k]
        if (n + 1) % 1000 == 0:
            print(f"  {name}: {n + 1}/{len(queries)} queries ({time.time() - t0:.0f}s)", flush=True)
    return {k: hits[k] / len(queries) for k in KS}


def main():
    os.makedirs(CACHE, exist_ok=True)
    m, queries = load()
    print(f"reports {len(m)} | test duplicates with an earlier group member (queries): {len(queries)}")
    text = [clean(t, d) for t, d in zip(m.Title, m.Description)]
    titles = m.Title.fillna("").astype(str).tolist()
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    results = {}
    for name, docs in (("MiniLM, title + description", text), ("MiniLM, title only", titles)):
        f = os.path.join(CACHE, f"emb_{'full' if 'desc' in name else 'title'}.npy")
        if os.path.exists(f):
            E = np.load(f)
        else:
            t0 = time.time()
            E = enc.encode(docs, batch_size=128, normalize_embeddings=True, show_progress_bar=False).astype(np.float32)
            np.save(f, E)
            print(f"  embedded {len(docs)} reports for '{name}' in {time.time() - t0:.0f}s", flush=True)
        results[name] = rr_from_scores(lambda q, E=E: E[:q] @ E[q], m, queries, name)
        print(name, {f"RR@{k}": round(v, 3) for k, v in results[name].items()}, flush=True)
    # model C (trained bi-encoder, rule results/training_rule.md); only Thunderbird is unseen in its training
    bi_c = os.path.join(HERE, "..", "..", "data", "external", "training", "bi_C")
    if os.path.isdir(bi_c):
        name = "trained bi_C, title + description"
        f = os.path.join(CACHE, "emb_full_biC.npy")
        if os.path.exists(f):
            E = np.load(f)
        else:
            E = SentenceTransformer(bi_c).encode(text, batch_size=128, normalize_embeddings=True,
                                                 show_progress_bar=False).astype(np.float32)
            np.save(f, E)
        results[name] = rr_from_scores(lambda q, E=E: E[:q] @ E[q], m, queries, name)
        print(name, {f"RR@{k}": round(v, 3) for k, v in results[name].items()}, flush=True)
        del E
    # BM25 over the same cleaned text (sparse, all earlier reports)
    from sklearn.feature_extraction.text import CountVectorizer
    cv = CountVectorizer(lowercase=True, token_pattern=r"(?u)\b[a-z][a-z0-9_]{2,}\b", stop_words="english", min_df=2)
    X = cv.fit_transform(text).tocsc().astype(np.float32)
    N = X.shape[0]
    df_ = np.asarray((X > 0).sum(axis=0)).ravel()
    idf = np.log(1 + (N - df_ + 0.5) / (df_ + 0.5)).astype(np.float32)
    dl = np.asarray(X.sum(axis=1)).ravel()
    k1, b = 1.2, 0.75
    Xr = X.tocsr()
    Xr.data = Xr.data * (k1 + 1) / (Xr.data + np.repeat(k1 * (1 - b + b * dl / dl.mean()), np.diff(Xr.indptr)))
    W = Xr.multiply(idf).tocsr()
    Q = (X > 0).astype(np.float32).tocsr()

    def bm25(q):
        qv = Q[q]
        return np.asarray(W[:q] @ qv.T.toarray()).ravel()
    results["BM25, title + description"] = rr_from_scores(bm25, m, queries, "BM25")
    print("BM25, title + description", {f"RR@{k}": round(v, 3) for k, v in results["BM25, title + description"].items()})
    out = pd.DataFrame(results).T
    out.columns = [f"RR@{k}" for k in KS]
    out.to_csv(os.path.join(HERE, "results", f"{PROJECT}_rrk.csv"))
    print("\n" + out.round(3).to_string())


if __name__ == "__main__":
    main()
