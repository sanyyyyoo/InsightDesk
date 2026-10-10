"""
E9: published duplicate-bug-report baselines on the team-labelled Play Store
reviews, scored the way the TOSEM-DBRD benchmark scores them.

Reference: Zhang et al., "Duplicate Bug Report Detection: How Far Are We?",
TOSEM 2023 (github.com/soarsmu/TOSEM-DBRD). Their finding: the simple
retrieval method REP (BM25F) beats deep-learning DBRD methods by 22.3% RR@10
on average, and Mozilla's full-text search (FTS) beats some research tools.
Their code needs Bugzilla fields, a C++ build and MySQL, so the textual core
of both is re-implemented here (our reviews have one text field and no
product/component/version fields):

  FTS-OR    Bugzilla FULLTEXT_OR full-text search, approximated by BM25 over
            unstemmed words (stop words removed, words < 3 chars dropped,
            as MySQL InnoDB full-text search does)
  REP-text  REP's textual features only: BM25 on stemmed unigrams + BM25 on
            stemmed bigrams, combined with a weight; k1, b and the weight are
            tuned leave-one-product-out (REP learns them with RankNet)
  ours      MiniLM cosine (v2), SimCSE + synonyms, and a cosine + BM25 hybrid
  LLM       MiniLM on cached LLM issue statements (comparison only)

Protocol (TOSEM-DBRD, adapted to within-company dedup):
  - reviews in date order, within one product
  - test items: reviews that have an earlier duplicate in the same product
  - candidates: earlier reviews of that product, grouped into their buckets
    (cases); bucket score = max score over its members
  - RR@k = share of test items whose bucket is in the top k
  - tuned parameters are chosen on the other 5 products (LOPO)

  python experiments/dedup/e9_dbrd_baselines.py
"""

import math
import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
KS = (1, 3, 5, 10)
TUNE_K = 5
STEM = PorterStemmer()


def words(text, stem):
    toks = [t for t in re.findall(r"[a-z0-9]+", str(text).lower()) if len(t) >= 3 and t not in ENGLISH_STOP_WORDS]
    return [STEM.stem(t) for t in toks] if stem else toks


def bigrams(toks):
    return [a + "_" + b for a, b in zip(toks, toks[1:])]


def bm25_scores(query, docs, k1, b):
    """BM25 of one query against a list of token lists (IDF from those docs)."""
    n = len(docs)
    if n == 0:
        return np.zeros(0)
    df = Counter(t for d in docs for t in set(d))
    avg = max(np.mean([len(d) for d in docs]), 1e-9)
    q = set(query)
    out = np.zeros(n)
    for i, d in enumerate(docs):
        tf = Counter(d)
        s = 0.0
        for t in q:
            if tf[t]:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avg))
        out[i] = s
    return out


def test_items(df):
    """(query index, earlier same-product indices) for reviews with an earlier duplicate."""
    items = []
    prod, iss = df.department.values, df.issue_id.values
    for i in range(len(df)):
        prev = [j for j in range(i) if prod[j] == prod[i]]
        if any(iss[j] == iss[i] for j in prev):
            items.append((i, prev))
    return items


def rank_of_bucket(scores, prev, iss, target):
    """1-based rank of the true bucket after max-pooling member scores per bucket."""
    best = {}
    for s, j in zip(scores, prev):
        best[iss[j]] = max(best.get(iss[j], -np.inf), s)
    order = sorted(best, key=lambda k: -best[k])
    return order.index(target) + 1


def rr(ranks, k):
    return float(np.mean(np.asarray(ranks) <= k))


def main():
    from sentence_transformers import SentenceTransformer
    df = load_ground_truth(path=DATA_PATHS["playstore"])
    df["issue_id"] = df.issue_id.astype(str)
    df["department"] = df.department.astype(str)
    iss, prod = df.issue_id.values, df.department.values
    items = test_items(df)
    products = sorted(set(prod[i] for i, _ in items))
    print(f"test items: {len(items)} | per product: {Counter(prod[i] for i, _ in items)}")

    minilm = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    simcse = SentenceTransformer(os.path.join(os.path.dirname(__file__), "models", "minilm-simcse"))
    syn = apply_text_mode(df, "boilerplate+synonyms", minilm, data="playstore")
    llm = apply_text_mode(df, "llm", minilm, data="playstore")
    emb = {
        "v2 MiniLM cosine": minilm.encode(df.cleaned_text.tolist(), normalize_embeddings=True),
        "SimCSE + synonyms cosine": simcse.encode(syn.cleaned_text.tolist(), normalize_embeddings=True),
        "LLM statement cosine (comparison)": minilm.encode(llm.cleaned_text.tolist(), normalize_embeddings=True),
    }
    raw = df.complaint_text.astype(str).tolist()
    plain = [words(t, stem=False) for t in raw]
    stemmed = [words(t, stem=True) for t in raw]
    stemmed_bi = [bigrams(t) for t in stemmed]

    # ---- per-item score vectors for every configuration -----------------
    configs = {}                                   # name -> list of score arrays (one per item)

    def add(name, fn):
        configs[name] = [fn(i, prev) for i, prev in items]

    for name, e in emb.items():
        add(name, lambda i, prev, e=e: e[prev] @ e[i])
    add("FTS-OR (BM25, unstemmed)", lambda i, prev: bm25_scores(plain[i], [plain[j] for j in prev], 1.2, 0.75))
    rep_grid = [(k1, b) for k1 in (0.8, 1.2, 2.0) for b in (0.5, 0.75, 1.0)]
    for k1, b in rep_grid:
        add(f"_uni_{k1}_{b}", lambda i, prev, k1=k1, b=b: bm25_scores(stemmed[i], [stemmed[j] for j in prev], k1, b))
        add(f"_bi_{k1}_{b}", lambda i, prev, k1=k1, b=b: bm25_scores(stemmed_bi[i], [stemmed_bi[j] for j in prev], k1, b))

    def norm(s):
        return s / s.max() if len(s) and s.max() > 0 else s

    # ---- parameterised methods, tuned leave-one-product-out --------------
    weights = np.round(np.arange(0.0, 1.01, 0.1), 2)
    families = {
        "REP-text (BM25 uni+bi, tuned)": [
            (f"k1={k1} b={b} w={w}", [w * u + (1 - w) * v for u, v in zip(configs[f"_uni_{k1}_{b}"], configs[f"_bi_{k1}_{b}"])])
            for k1, b in rep_grid for w in weights],
        "Hybrid SimCSE cosine + BM25 (ours, tuned)": [
            (f"a={a}", [c + a * norm(f) for c, f in zip(configs["SimCSE + synonyms cosine"], configs["FTS-OR (BM25, unstemmed)"])])
            for a in np.round(np.arange(0.0, 1.01, 0.1), 2)],
    }

    def ranks_of(scores_list):
        return np.array([rank_of_bucket(s, prev, iss, iss[i]) for s, (i, prev) in zip(scores_list, items)])

    item_prod = np.array([prod[i] for i, _ in items])
    final = {}
    for name in [n for n in configs if not n.startswith("_")]:
        final[name] = (ranks_of(configs[name]), "-")
    for fam, options in families.items():
        opt_ranks = [(label, ranks_of(sc)) for label, sc in options]
        r = np.empty(len(items), dtype=int)
        chosen = {}
        for p in products:
            held = item_prod == p
            label, best = max(opt_ranks, key=lambda o: rr(o[1][~held], TUNE_K))
            r[held] = best[held]
            chosen[p] = label
        final[fam] = (r, "; ".join(f"{p}: {c}" for p, c in chosen.items()))

    # random baseline: buckets in random order (expected value by simulation)
    rng = np.random.default_rng(0)
    sims = [ranks_of([rng.random(len(prev)) for _, prev in items]) for _ in range(200)]
    final["Random"] = (np.concatenate(sims), "-")

    rows = []
    for name, (r, chosen) in final.items():
        row = {"method": name, **{f"RR@{k}": rr(r, k) for k in KS}}
        if name != "Random":
            for p in products:
                row[f"RR@5 {p}"] = rr(r[item_prod == p], 5)
        row["tuned (LOPO)"] = chosen
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "e9_dbrd_baselines.csv"), index=False)

    # paired bootstrap over test items: each method vs the plain v2 cosine
    ref = final["v2 MiniLM cosine"][0]
    ci = []
    for name, (r, _) in final.items():
        if name in ("Random", "v2 MiniLM cosine"):
            continue
        d = []
        for _ in range(2000):
            s = rng.integers(0, len(items), len(items))
            d.append(rr(r[s], 5) - rr(ref[s], 5))
        ci.append({"method": name, "RR@5 minus v2": rr(r, 5) - rr(ref, 5),
                   "CI low": np.percentile(d, 2.5), "CI high": np.percentile(d, 97.5)})
    pd.set_option("display.width", 250)
    print(out.drop(columns=["tuned (LOPO)"]).round(3).to_string(index=False))
    print("\nLOPO-chosen settings:")
    for name, (_, chosen) in final.items():
        if chosen != "-":
            print(f"  {name}: {chosen}")
    print("\nPaired bootstrap, RR@5 difference vs v2 MiniLM cosine (95% CI):")
    print(pd.DataFrame(ci).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
