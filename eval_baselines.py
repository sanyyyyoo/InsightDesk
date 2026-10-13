"""
Published-method baselines on our labelled data (rule: InsightDesk-dedup experiments/dedup/results/
baselines_rule.md). CLAP (as published, and with eps tuned on our tuning halves) and the app's own
BERTopic topics, scored with the same pairwise metric and corrected cluster bootstrap as R1. No LLM calls.

  python eval_baselines.py
"""

import os
import re
import sys
import types

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
stub = types.ModuleType("backend.database.supabase")
for _name in ("create_topic", "get_all_cases", "get_clustering_metadata", "get_clustering_statistics",
              "get_topic_by_slug", "update_case_topic", "update_clustering_metadata", "update_topic"):
    setattr(stub, _name, lambda *a, **k: None)
sys.modules["backend.database.supabase"] = stub

EXP = "D:/PBL/InsightDesk-dedup"
sys.path.insert(0, os.path.join(EXP, "experiments", "dedup"))
from ci_bootstrap import counts, prf  # noqa: E402
from spike_grouping import G, load  # noqa: E402

from nltk.stem import PorterStemmer  # noqa: E402
from sklearn.cluster import DBSCAN  # noqa: E402
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "baselines")
B, SEED = 2000, 11
_stem = PorterStemmer().stem


def clap_tokens(text):
    words = re.findall(r"[a-z]+", str(text).lower())
    return [_stem(w) for w in words if w not in ENGLISH_STOP_WORDS and len(w) > 1]


def clap(texts, eps):
    """CLAP: TF-IDF (stop words removed, Porter stemming), DBSCAN minPts 2 on 1 - cosine."""
    if len(texts) < 2:
        return np.arange(len(texts))
    X = TfidfVectorizer(tokenizer=clap_tokens, lowercase=False, token_pattern=None).fit_transform(texts)
    if X.shape[1] == 0:
        return np.arange(len(texts))
    lab = DBSCAN(eps=eps, min_samples=2, metric="cosine").fit_predict(X)
    nxt = lab.max() + 1
    out = lab.copy()
    for k in np.where(lab == -1)[0]:            # noise points = singletons
        out[k], nxt = nxt, nxt + 1
    return out


def bertopic(texts):
    import backend.services.clustering_service as cs
    from backend.services.preprocess import clean_text
    if len(texts) < 10:                         # too few for topic modelling: every review alone
        return np.arange(len(texts))
    docs = [clean_text(t) for t in texts]
    try:
        topics, _, _ = cs._run_bertopic(docs, cs.embedding_model.encode(docs, show_progress_bar=False))
    except Exception as e:                       # BERTopic can fail on tiny inputs
        print(f"    bertopic failed on {len(texts)} reviews ({str(e)[:60]}): singletons")
        return np.arange(len(texts))
    topics = np.asarray(topics)
    out, nxt = topics.copy(), topics.max() + 1
    for k in np.where(topics == -1)[0]:
        out[k], nxt = nxt, nxt + 1
    return out


def per_product(method, texts, products, **kw):
    lab = np.empty(len(texts), dtype=object)
    for p in pd.unique(products):
        idx = np.where(products == p)[0]
        lab[idx] = [f"{p}|{x}" for x in method([texts[i] for i in idx], **kw)]
    return lab


def pooled(parts, b=B):
    """parts: list of (issue labels, {method: case labels}); point + 95% corrected cluster bootstrap."""
    rng = np.random.default_rng(SEED)
    prep = []
    for issue, preds in parts:
        _, iss = np.unique(np.asarray(issue).astype(str), return_inverse=True)
        prep.append((iss, iss.max() + 1, {m: np.asarray(v).astype(str) for m, v in preds.items()}))
    names = list(parts[0][1])
    pt = {m: prf(*sum(np.array(counts(p[m], iss, np.ones(n))) for iss, n, p in prep)) for m in names}
    boot = {m: [] for m in names}
    for _ in range(b):
        tot = {m: np.zeros(3) for m in names}
        for iss, n, p in prep:
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            for m in names:
                tot[m] += np.array(counts(p[m], iss, w))
        for m in names:
            boot[m].append(prf(*tot[m]))
    out = []
    for m in names:
        lo, hi = np.percentile(np.array(boot[m]), [2.5, 97.5], axis=0)
        out.append(f"  {m:28s} P {pt[m][0]:.3f} [{lo[0]:.2f},{hi[0]:.2f}]  R {pt[m][1]:.3f} [{lo[1]:.2f},{hi[1]:.2f}]  "
                   f"F1 {pt[m][2]:.3f} [{lo[2]:.2f},{hi[2]:.2f}]")
    return out, pt


def tune_eps(splits):
    """Best pooled pairwise F1 of CLAP over eps, on tuning halves (texts, products, issues)."""
    best = None
    for eps in np.round(np.arange(0.30, 0.91, 0.05), 2):
        tot = np.zeros(3)
        for texts, prods, iss in splits:
            lab = per_product(clap, texts, prods, eps=eps)
            _, ii = np.unique(iss, return_inverse=True)
            tot += np.array(counts(lab.astype(str), ii, np.ones(ii.max() + 1)))
        f = prf(*tot)[2]
        if best is None or f > best[1]:
            best = (eps, f)
    return best[0]


def main():
    os.makedirs(OUT, exist_ok=True)
    lines = ["Published-method baselines (rule: experiments/dedup/results/baselines_rule.md)"]
    s = pd.read_csv(os.path.join(EXP, "data", "external", "playstore_scored.csv")).set_index("complaint_ref")
    halves = {"s0A": load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
              "s1B": load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B"),
              "s1A": load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A")}
    allrefs = set(s.index)
    parts, eps_used = [], []
    for name, r1 in halves.items():
        test = list(r1.index)
        tune = sorted(allrefs - set(test))
        t_texts = s.complaint_text.reindex(tune).astype(str).tolist()
        eps = tune_eps([(t_texts, s.department.reindex(tune).to_numpy(), s.issue_id.reindex(tune).astype(str).to_numpy())])
        eps_used.append(eps)
        texts = s.complaint_text.reindex(test).astype(str).tolist()
        prods = s.department.reindex(test).to_numpy()
        preds = {"R1 (InsightDesk, online)": r1.reindex(test).astype(str).to_numpy(),
                 "CLAP eps 0.6 (published)": per_product(clap, texts, prods, eps=0.6),
                 f"CLAP eps tuned": per_product(clap, texts, prods, eps=eps),
                 "BERTopic topics (app)": per_product(bertopic, texts, prods)}
        parts.append((s.issue_id.reindex(test).astype(str).to_numpy(), preds))
        print(f"{name}: tuned eps {eps}", flush=True)
    res, _ = pooled(parts)
    lines += [f"\nPLAY STORE, held-out halves s0A, s1B, s1A pooled (CLAP tuned eps per split: {eps_used})"] + res
    lines.append("  (R1 + re-joining RJ1 on the same halves: P 0.799 R 0.327 F1 0.464 - rejoin_confirm_RJ1.txt)")
    eps_all = float(np.round(np.median(eps_used), 2))

    # Firefox sample 3 and the new apps: CLAP eps from Play Store tuning (median), BERTopic as is
    from replay_lab import load_ground_truth  # noqa: E402
    import e5_three_way as e5  # noqa: E402
    ff = load_ground_truth(path=os.path.join(EXP, "data", "external", "firefox3.csv"))
    r1 = load(f"firefox3_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox3")
    ff = ff.set_index(ff.complaint_ref + e5.EXT_REF_OFFSET).reindex(r1.index)
    texts, prods = ff.complaint_text.astype(str).tolist(), ff.department.astype(str).to_numpy()
    res, _ = pooled([(ff.issue_id.astype(str).to_numpy(),
                      {"R1 (InsightDesk, online)": r1.astype(str).to_numpy(),
                       "CLAP eps 0.6 (published)": per_product(clap, texts, prods, eps=0.6),
                       f"CLAP eps {eps_all} (Play Store)": per_product(clap, texts, prods, eps=eps_all),
                       "BERTopic topics (app)": per_product(bertopic, texts, prods)})])
    lines += ["\nFIREFOX sample 3"] + res + ["  (R1 + RJ1: P 0.961 R 0.657 F1 0.780)"]

    from new_apps_score import agreed, key, app_replay  # noqa: E402
    import glob
    NA = os.path.join(EXP, "data", "external", "new_apps")
    t = pd.read_csv(os.path.join(NA, "new_apps_test588.csv"))
    kx, _ = key(sorted(glob.glob(os.path.join(NA, "sheetX_*.xlsx")))[0])
    ky, _ = key(sorted(glob.glob(os.path.join(NA, "sheetY_*.xlsx")))[0])
    ka = agreed(kx, ky)
    texts, prods = t.complaint_text.astype(str).tolist(), t["product"].astype(str).to_numpy()
    res, _ = pooled([(ka.reindex(t.index).astype(str).to_numpy(),
                      {"R1 (InsightDesk, app)": app_replay("new_apps", t.index.to_numpy()).reindex(t.index).astype(str).to_numpy(),
                       "CLAP eps 0.6 (published)": per_product(clap, texts, prods, eps=0.6),
                       f"CLAP eps {eps_all} (Play Store)": per_product(clap, texts, prods, eps=eps_all),
                       "BERTopic topics (app)": per_product(bertopic, texts, prods)})])
    lines += ["\nNEW HELP-DESK APPS (588, agreed Claude/ChatGPT key)"] + res
    text = "\n".join(lines)
    print(text)
    open(os.path.join(OUT, "baselines_results.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
