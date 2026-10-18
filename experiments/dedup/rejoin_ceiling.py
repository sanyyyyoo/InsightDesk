"""
Case re-joining ceiling (diagnostic; results/rejoin_ceiling_rule.md). No API calls.

  python experiments/dedup/rejoin_ceiling.py
"""

import collections
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from spike_grouping import G, load  # noqa: E402

RES = os.path.join(HERE, "results")
KS = (1, 3, 5)


def analyse(name, refs, case, issue, product, emb):
    """refs/case/issue/product/emb aligned arrays for the reviews of one evaluated partition set."""
    df = pd.DataFrame({"case": case, "issue": issue, "product": product})
    df["case"] = df["product"] + "|" + df["case"].astype(str)
    major = df.groupby("case").issue.agg(lambda s: collections.Counter(s).most_common(1)[0][0])
    cases = list(major.index)
    members = df.groupby("case").groups
    prod_of = df.groupby("case")["product"].first()
    # case-case similarity: max member cosine, same product only
    neigh = {}
    for p in df["product"].unique():
        cp = [c for c in cases if prod_of[c] == p]
        idx = [np.asarray(members[c]) for c in cp]
        for a, ia in enumerate(idx):
            sims = []
            for b, ib in enumerate(idx):
                if a != b:
                    sims.append((float((emb[ia] @ emb[ib].T).max()), cp[b]))
            neigh[cp[a]] = [c for _, c in sorted(sims, reverse=True)]
    by_issue = collections.defaultdict(list)
    for c in cases:
        by_issue[major[c]].append(c)
    frag = [c for c in cases if len(by_issue[major[c]]) >= 2]
    split = sum(1 for v in by_issue.values() if len(v) >= 2)
    has_n = [c for c in cases if neigh[c]]
    purity = np.mean([major[neigh[c][0]] == major[c] for c in has_n]) if has_n else float("nan")
    lines = [f"\n{name}: {len(df)} reviews, {len(cases)} cases | problems split into >= 2 cases: {split} | "
             f"fragments: {len(frag)} | top-1 neighbour purity: {purity:.2f}"]
    issue_codes, iss = np.unique(df.issue.astype(str), return_inverse=True)
    ones = np.ones(len(issue_codes))
    base = prf(*counts(df.case.to_numpy(), iss, ones))
    lines.append(f"  R1 as is: P {base[0]:.3f} R {base[1]:.3f} F1 {base[2]:.3f}")
    for k in KS:
        rec = np.mean([any(major[n] == major[c] for n in neigh[c][:k]) for c in frag]) if frag else float("nan")
        parent = {c: c for c in cases}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for c in frag:                                  # perfect judge: merge siblings within top-k
            for n in neigh[c][:k]:
                if major[n] == major[c]:
                    parent[find(c)] = find(n)
        merged = df.case.map(lambda c: find(c)).to_numpy()
        p, r, f = prf(*counts(merged, iss, ones))
        lines.append(f"  k={k}: sibling recall@{k} {rec:.2f} | perfect re-join ceiling P {p:.3f} R {r:.3f} F1 {f:.3f} "
                     f"(recall {r - base[1]:+.3f})")
    return lines


def main():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    out = []
    # Play Store final halves
    d = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(d["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    pos = {int(r): k for k, r in enumerate(d.complaint_ref)}
    halves = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
              load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B"),
              load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A")]
    for n, s in zip(("s0A", "s1B", "s1A"), halves):
        rows = [pos[int(r)] for r in s.index]
        out += analyse(f"PLAY STORE {n}", s.index.to_numpy(), s.to_numpy(), d.issue_id.astype(str).to_numpy()[rows],
                       d.department.astype(str).to_numpy()[rows], emb[rows])
    # Firefox 3 and Jira (external refs are offset in the assignment files)
    for data, f, key, title in (
            ("firefox3", f"firefox3_e5_assignments_llm_{G}_founder_gated_ext_playstore", "firefox3", "FIREFOX 3"),
            ("jira_agreed", f"jira_new_e5_assignments_llm_{G}_founder_gated_ext_playstore", "jira_new",
             "JIRA blind run (agreed key)")):
        d = apply_text_mode(load_ground_truth(path=DATA_PATHS[data]), "boilerplate", enc)
        emb = enc.encode(d["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        s = load(f, "llm", "ext", key)
        pos = {int(r) + e5.EXT_REF_OFFSET: k for k, r in enumerate(d.complaint_ref)}
        rows = [pos[int(r)] for r in s.index]
        out += analyse(title, s.index.to_numpy(), s.to_numpy(), d.issue_id.astype(str).to_numpy()[rows],
                       d.department.astype(str).to_numpy()[rows], emb[rows])
    text = "\n".join(out)
    print(text)
    open(os.path.join(RES, "rejoin_ceiling.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
