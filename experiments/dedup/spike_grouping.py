"""
Spike-level grouping, offline (rule: results/spike_grouping_rule.md).

Cases from a finished run stay unchanged; for alerting only, cases of one
product are linked when their most similar members have cosine >= tau, and
linked cases count as one alert group. Tau is chosen on Play Store
within-company R1 and then applied unchanged to Firefox and Play Store LOPO.

  python experiments/dedup/spike_grouping.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from e5_three_way import EMBED_MODEL, EXT_REF_OFFSET  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RES = os.path.join(os.path.dirname(__file__), "results")
TAUS = [round(0.50 + 0.05 * k, 2) for k in range(9)]
MIN_PURITY = 0.90
G = "perproduct_wideband_exemplars_top5"


def embed(data, calibrate_on=None):
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(EMBED_MODEL)
    cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
    if calibrate_on:          # same corpus as the run, so boilerplate suppression matches
        cal = load_ground_truth(path=DATA_PATHS[calibrate_on])
        tgt = load_ground_truth(path=DATA_PATHS[data])
        tgt["complaint_ref"] = tgt["complaint_ref"] + EXT_REF_OFFSET
        raw = pd.concat([cal[cols], tgt[cols]], ignore_index=True)
    else:
        raw = load_ground_truth(path=DATA_PATHS[data])
    df = apply_text_mode(raw, "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    df = df[cols].reset_index(drop=True)
    return df.set_index("complaint_ref"), {r: i for i, r in enumerate(df.complaint_ref)}, emb


def alert_groups(a, pos, emb, dept, tau):
    """a: complaint_ref -> case for one partition; returns complaint_ref -> alert group."""
    cases = {c: [pos[r] for r in g.index] for c, g in a.groupby(a)}
    parent = {c: c for c in cases}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    keys = list(cases)
    for i, ci in enumerate(keys):
        for cj in keys[i + 1:]:
            if dept[cases[ci][0]] != dept[cases[cj][0]]:
                continue
            if float((emb[cases[ci]] @ emb[cases[cj]].T).max()) >= tau:
                parent[find(ci)] = find(cj)
    return a.map(lambda c: find(c))


def scores(parts, df):
    """parts: list of Series complaint_ref -> group. Capture, purity (B-cubed P), largest group."""
    caps, caps5, pur, n, biggest = [], [], 0.0, 0, 0
    for s in parts:
        t = pd.DataFrame({"grp": s.astype(str)}).join(df[["issue_id"]])
        sz = t.grp.value_counts()
        biggest = max(biggest, int(sz.iloc[0]))
        both = t.groupby(["grp", "issue_id"]).size()
        pur += sum(both[(g, i)] / sz[g] for g, i in zip(t.grp, t.issue_id))
        n += len(t)
        for iid, g in t.groupby("issue_id"):
            if len(g) < 2 or iid.startswith("lone"):
                continue
            c = g.grp.value_counts().iloc[0] / len(g)
            caps.append(c)
            if len(g) >= 5:
                caps5.append(c)
    return np.mean(caps), np.mean(caps5), pur / n, biggest


def load(f, judge, seed, half):
    a = pd.read_csv(os.path.join(RES, f + ".csv"))
    a = a[(a.judge == judge) & (a.split_seed.astype(str) == str(seed)) & (a.held_out_half == half)]
    return a.drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case


def evaluate(name, parts, df, pos, emb, dept, taus):
    base = scores(parts, df)
    print(f"\n{name}\n  cases only          capture={base[0]:.2f} capture(>=5)={base[1]:.2f} purity={base[2]:.3f} largest={base[3]}")
    out = []
    for tau in taus:
        r = scores([alert_groups(p, pos, emb, dept, tau) for p in parts], df)
        out.append((tau, *r))
        print(f"  tau={tau:.2f}  alert groups  capture={r[0]:.2f} capture(>=5)={r[1]:.2f} purity={r[2]:.3f} largest={r[3]}")
    return out


def main():
    # selection set: Play Store within-company R1
    df, pos, emb = embed("playstore")
    dept = df.department.reindex(list(pos)).to_numpy()
    sel = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    grid = evaluate("SELECTION  Play Store within-company, R1", sel, df, pos, emb, dept, TAUS)
    ok = [g for g in grid if g[3] >= MIN_PURITY]
    tau = max(ok, key=lambda g: (round(g[2], 4), g[0]))[0] if ok else None
    print(f"\nselected tau = {tau} (highest capture(>=5) with purity >= {MIN_PURITY})")
    if tau is None:
        return

    f = f"playstore_e5_assignments_llm_{G}_founder_gated_lopo"
    halves = pd.read_csv(os.path.join(RES, f + ".csv")).held_out_half.unique()
    evaluate("CONFIRM (secondary)  Play Store unseen company, R1", [load(f, "llm", "lopo", h) for h in halves],
             df, pos, emb, dept, [tau])

    df, pos, emb = embed("firefox", calibrate_on="playstore")
    dept = df.department.reindex(list(pos)).to_numpy()
    evaluate("CONFIRM  Firefox, R1", [load(f"firefox_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox")],
             df, pos, emb, dept, [tau])


if __name__ == "__main__":
    main()
