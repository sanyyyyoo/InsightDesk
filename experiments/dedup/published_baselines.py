"""
Published duplicate finders on the Play Store held-out halves, same protocol as InsightDesk
(rule: results/published_baselines_rule.md).

Every method gets the raw review text and the product, nothing else; complaints arrive in time order;
each joins the case of its best-matching earlier complaint (same product) if the match passes the
method's threshold, else opens a new case. The threshold is tuned on the tuning half (best pairwise F1,
generous to the baselines) and scored on the held-out half. Pooled over the three halves R1 is scored on.

  python experiments/dedup/published_baselines.py
"""

import hashlib
import math
import os
import re
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ci_bootstrap import counts, prf  # noqa: E402
from normalize import DATA_PATHS  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as SW  # noqa: E402

df = load_ground_truth(path=DATA_PATHS["playstore"])
TXT = df["complaint_text"].astype(str).tolist()
ISS = np.array(df["issue_id"].astype(str).tolist())
GRP = np.array(df["department"].astype(str).tolist())
N = len(TXT)
TOK = [[w for w in re.findall(r"[a-z][a-z0-9']+", t.lower()) if w not in SW] for t in TXT]

# ---- similarity functions (each returns sim(i, j) in a comparable range) ----
DF = Counter(w for t in TOK for w in set(t))
AVG = np.mean([max(len(t), 1) for t in TOK])
IDF = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in DF.items()}


def bm25(q, j):
    tf, L = Counter(TOK[j]), len(TOK[j])
    return sum(IDF[w] * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * L / AVG)) for w in set(TOK[q]) if w in tf)


SELF = [bm25(i, i) or 1.0 for i in range(N)]


def bm25n(i, j):                       # normalised by the query's self-score so one threshold fits all
    return bm25(i, j) / SELF[i]


def shingles(t, k=3):
    t = re.sub(r"\s+", " ", t.lower())
    return {t[x:x + k] for x in range(max(len(t) - k + 1, 1))}


SH = [shingles(t) for t in TXT]


def jaccard(i, j):                     # MinHash-LSH estimates exactly this
    a, b = SH[i], SH[j]
    return len(a & b) / max(len(a | b), 1)


def simhash(tokens):
    v = np.zeros(64)
    for w, c in Counter(tokens).items():
        h = int(hashlib.md5(w.encode()).hexdigest()[:16], 16)
        v += c * np.array([1 if h >> b & 1 else -1 for b in range(64)])
    return sum(1 << b for b in range(64) if v[b] > 0)


SIM = [simhash(t) for t in TOK]


def simhash_sim(i, j):                 # 64 - Hamming distance
    return 64 - bin(SIM[i] ^ SIM[j]).count("1")


METHODS = {
    "BM25 (REP's text core)": (bm25n, np.round(np.arange(0.05, 1.0, 0.05), 2)),
    "Jaccard / MinHash-LSH (3-char shingles)": (jaccard, np.round(np.arange(0.05, 0.9, 0.05), 2)),
    "SimHash (64-bit)": (simhash_sim, np.arange(34, 64, 2)),
}


def online(idx, sim, th):
    """Time-ordered single pass: join the best earlier same-product complaint's case if sim >= th."""
    case = {}
    for n, i in enumerate(idx):
        best, bj = -1e9, None
        for j in idx[:n]:
            if GRP[j] == GRP[i]:
                s = sim(i, j)
                if s > best:
                    best, bj = s, j
        case[i] = case[bj] if bj is not None and best >= th else i
    return np.array([f"{GRP[i]}|{case[i]}" for i in idx])


def score(idx, labels):
    _, iss = np.unique(ISS[idx], return_inverse=True)
    return np.array(counts(labels, iss, np.ones(iss.max() + 1)))


def main():
    out = ["PUBLISHED DUPLICATE FINDERS on Play Store held-out halves (same splits and scoring as R1)"]
    ids = np.array(sorted(set(ISS)))
    for name, (sim, grid) in METHODS.items():
        tot, chosen = np.zeros(3), []
        for seed, half in ((0, "A"), (1, "B"), (1, "A")):
            rng = np.random.default_rng(seed)
            h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
            a, b = np.where(np.isin(ISS, list(h)))[0], np.where(~np.isin(ISS, list(h)))[0]
            tune, test = (a, b) if half == "B" else (b, a)
            th = max(grid, key=lambda t: prf(*score(tune, online(tune, sim, t)))[2])
            chosen.append(th)
            tot += score(test, online(test, sim, th))
        p, r, f = prf(*tot)[:3]
        out.append(f"  {name:42s} P {p:.3f}  R {r:.3f}  F1 {f:.3f}   thresholds {chosen}")
        print(out[-1], flush=True)
    out.append("  (InsightDesk on the same halves: R1 P 0.810 R 0.259 F1 0.392; with re-joining P 0.799 R 0.327 F1 0.464)")
    open(os.path.join(HERE, "results", "published_baselines_results.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
