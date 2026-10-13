"""
Real-review accuracy of the main-branch pipeline vs R1 on the 1,432-complaint set.

The 1,432 set (data/master_complaints_v2.csv = Krisha's main-branch Play Store
reviews + 488 synthetic) has team labels for part of its real reviews
(data/external/playstore_scored.csv, joined by exact review text). Each pipeline
processes the WHOLE stream in its own natural order; only pairs between labelled
real reviews are scored (same scoring as every Play Store result:
issue_id = product|problem_code; vague / other / not_a_problem / topic codes are
not in the scored set).

Pipelines:
  production (main branch): MiniLM top-5 + MS-MARCO cross-encoder, threshold -2.21
  v2 without LLM: boilerplate + online cosine 0.44
  R1 (in the app, real judge): reports/replay/replay_assignments.csv from the app repo

  python experiments/dedup/compare_1432_real.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from full_replay import load  # noqa: E402

R1_FILE = "D:/PBL/InsightDesk-claude-review/reports/replay/replay_assignments.csv"
R1_NOPROD = "D:/PBL/InsightDesk-claude-review/reports/replay/no_product_filter/replay_assignments.csv"
SAVED = os.path.join(os.path.dirname(__file__), "results", "full_replay_1432_assignments.csv")
B, SEED = 2000, 11


def c2(x):
    return x * (x - 1) / 2.0


from ci_bootstrap import counts  # noqa: E402  (corrected cluster-bootstrap counting)


def prf(tp, pred, true):
    p = tp / pred if pred else 0.0
    r = tp / true if true else 0.0
    return p, r, 2 * p * r / (p + r) if p + r else 0.0


def main():
    df = load()                                       # 1,432 rows in file (= production ingestion) order
    scored = pd.read_csv("data/external/playstore_scored.csv")
    lab = scored.drop_duplicates("complaint_text").set_index("complaint_text").issue_id
    df["issue"] = df.complaint_text.map(lab)
    labelled = df.issue.notna() & ~df.is_synthetic.astype(bool)
    print(f"labelled real reviews found in the 1,432 set: {int(labelled.sum())} of {len(scored)} scored")

    if os.path.exists(SAVED):                          # production / v2 replays are deterministic: reuse
        sv = pd.read_csv(SAVED)
        prod, v2 = sv["production"], sv["v2_cos044"]
    else:
        from replay_lab import Models, Replay
        from sentence_transformers import CrossEncoder, SentenceTransformer
        models = Models()
        models.cross_encoder, models._ce_cache = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2"), {}
        rep = Replay(df, models.embed(df["cleaned_text"]), models, "first", 5, -2.21).run()
        prod = pd.Series(rep.case_of_row).sort_index().reset_index(drop=True)

        from backend.services.preprocess import clean_text
        from compare_pipelines import online_cos
        from normalize import boilerplate_suppress
        enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        bp = pd.Series(boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)).map(clean_text)
        v2 = pd.Series(online_cos(enc.encode(bp.tolist(), normalize_embeddings=True, show_progress_bar=False), 0.44))
        pd.DataFrame({"row": df.index, "production": prod.values, "v2_cos044": v2.values}).to_csv(SAVED, index=False)

    r1a = pd.read_csv(R1_FILE).set_index("row").case_id     # row = index in master_complaints_v2.csv
    r1 = df.index.to_series().map(r1a)

    idx = np.where(labelled)[0]
    issue_codes, issue = np.unique(df.issue.values[idx].astype(str), return_inverse=True)
    methods = {"production (main branch): MS-MARCO -2.21": prod.values[idx],
               "v2 without LLM: cosine 0.44": v2.values[idx],
               "R1 (app, real judge), within product": r1.values[idx]}
    cases_all = {"production (main branch): MS-MARCO -2.21": prod, "v2 without LLM: cosine 0.44": v2,
                 "R1 (app, real judge), within product": r1}
    if os.path.exists(R1_NOPROD):
        r1n = df.index.to_series().map(pd.read_csv(R1_NOPROD).set_index("row").case_id)
        methods["R1 (app, real judge), NO product filter"] = r1n.values[idx]
        cases_all["R1 (app, real judge), NO product filter"] = r1n
    ones = np.ones(len(issue_codes))
    rng = np.random.default_rng(SEED)
    boot = {k: [] for k in methods}
    for _ in range(B):
        w = np.bincount(rng.integers(0, len(issue_codes), len(issue_codes)), minlength=len(issue_codes)).astype(float)
        for k, cases in methods.items():
            boot[k].append(prf(*counts(cases, issue, w)))
    true_pairs = counts(list(methods.values())[0], issue, ones)[2]
    print(f"\nreal labelled reviews: {len(idx)}, true duplicate pairs: {int(true_pairs)} (95% intervals, cluster bootstrap)")
    print(f"  {'pipeline':42s} {'precision':>22s} {'recall':>22s} {'F1':>22s}")
    for k, cases in methods.items():
        pt = prf(*counts(cases, issue, ones))
        lo, hi = np.percentile(np.array(boot[k]), [2.5, 97.5], axis=0)
        print(f"  {k:42s} " + " ".join(f"{pt[j]:.3f} [{lo[j]:.3f},{hi[j]:.3f}]".rjust(22) for j in range(3)))
    base = "production (main branch): MS-MARCO -2.21"
    for k in methods:
        if k == base:
            continue
        d = np.array(boot[k]) - np.array(boot[base])
        pk, pb = prf(*counts(methods[k], issue, ones)), prf(*counts(methods[base], issue, ones))
        for j, n in ((0, "precision"), (2, "F1")):
            lo, hi = np.percentile(d[:, j], [2.5, 97.5])
            print(f"  {k} minus main branch: {n} {pk[j] - pb[j]:+.3f} [{lo:+.3f},{hi:+.3f}], ahead in {(d[:, j] > 0).mean():.0%}")
    print("\nwhole stream: cases, and cases mixing products (cross-company merges):")
    for k, s in cases_all.items():
        mix = df.groupby(s.values)["product"].nunique()
        print(f"  {k:42s} cases {s.nunique():4d} | multi-product cases {int((mix > 1).sum())}")


if __name__ == "__main__":
    main()
