"""
Training data for the trained duplicate models (rule: results/training_rule.md).

Writes data/external/training/ (zipped for Colab):
  train_A.csv  text_a, text_b, label, source   (cross-encoder, variant A)
  train_B.csv  = A + Endava category pairs       (variant B)
  train_C.csv  anchor, positive, source          (bi-encoder, variant C)
Never used: the 338 scored Play Store reviews, Thunderbird, the Firefox groups of
our Firefox samples 1-3, the 1,000 Endava sample tickets.

  python experiments/dedup/build_training_data.py
"""

import itertools
import os
import random
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from build_firefox_dbrd import clean  # noqa: E402

OUT = os.path.join(ROOT, "data", "external", "training")
SEED = 7
PAIRS_PER_GROUP, MAX_BUG_POS = 6, 12000          # per project
MAX_SILVER_POS, MAX_ENDAVA_POS = 3000, 8000
rng = random.Random(SEED)


def union_find(links):
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
    return find, parent


def bug_pairs(folder, reports, excluded_rows, tag=None):
    tag = tag or folder
    m = pd.read_csv(os.path.join(HERE, "labelling", folder, reports),
                    usecols=["Issue_id", "Title", "Description", "Component"]).set_index("Issue_id")
    tr = pd.read_csv(os.path.join(HERE, "labelling", folder, "train.csv"))
    te = pd.read_csv(os.path.join(HERE, "labelling", folder, "test.csv"))
    find, parent = union_find(pd.concat([tr, te]))           # full graph, so no group straddles train/test
    test_ids = set(te.Issue_id.astype(int))
    banned = {find(int(x)) for x in excluded_rows if int(x) in parent}
    groups = {}
    for x in list(parent):
        if x in m.index and x not in test_ids:                 # TRAIN split reports only
            groups.setdefault(find(x), []).append(x)
    groups = {g: v for g, v in groups.items() if len(v) >= 2 and g not in banned}
    text = {}

    def t(i):
        if i not in text:
            text[i] = clean(m.at[i, "Title"], m.at[i, "Description"])
        return text[i]
    by_comp = m[~m.index.isin(test_ids)].groupby("Component").groups
    pos, neg = [], []
    for g, members in groups.items():
        prs = list(itertools.combinations(sorted(members), 2))
        for a, b in rng.sample(prs, min(PAIRS_PER_GROUP, len(prs))):
            pos.append((t(a), t(b), 1, tag))
            comp = m.at[a, "Component"]
            pool = by_comp.get(comp, m.index)
            for _ in range(5):                                 # hard negative: same component, other group
                c = pool[rng.randrange(len(pool))]
                if c not in members and c not in test_ids:
                    neg.append((t(a), t(c), 0, tag + "_hardneg"))
                    break
            c = m.index[rng.randrange(len(m))]                 # easy negative
            if c not in members and c not in test_ids:
                neg.append((t(a), t(c), 0, tag + "_neg"))
    pos = rng.sample(pos, min(MAX_BUG_POS, len(pos)))
    neg = rng.sample(neg, min(len(neg), len(pos) * 2))
    print(f"{tag}: {len(groups)} train duplicate groups (banned {len(banned)}) -> {len(pos)} pos, {len(neg)} neg")
    return pos, neg, groups, find


def silver_support():
    """R1 replay decisions on NON-test real reviews of the 1,432 stream (distillation)."""
    norm = lambda x: " ".join(str(x).lower().split())
    test = {norm(x) for x in pd.read_csv(os.path.join(ROOT, "data", "external", "playstore_scored.csv")).complaint_text}
    a = pd.read_csv("D:/PBL/InsightDesk-claude-review/reports/replay/replay_assignments.csv")
    a = a[~a.is_synthetic & ~a.complaint_text.map(norm).isin(test)].reset_index(drop=True)
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    e = enc.encode(a.complaint_text.astype(str).tolist(), normalize_embeddings=True, show_progress_bar=False)
    pos, neg = [], []
    for _, g in a.groupby("case_id"):
        for i, j in itertools.combinations(g.index, 2):
            pos.append((a.complaint_text[i], a.complaint_text[j], 1, "support_silver"))
    for prod, g in a.groupby("product"):
        idx = g.index.to_numpy()
        s = e[idx] @ e[idx].T
        for x, y in zip(*np.triu_indices(len(idx), 1)):
            i, j = idx[x], idx[y]
            if a.case_id[i] != a.case_id[j] and 0.26 <= s[x, y] < 0.83:
                neg.append((a.complaint_text[i], a.complaint_text[j], 0, "support_silver_neg"))
    pos = rng.sample(pos, min(MAX_SILVER_POS, len(pos)))
    neg = rng.sample(neg, min(len(neg), len(pos) * 2))
    print(f"support silver (non-test reviews: {len(a)}): {len(pos)} pos, {len(neg)} neg")
    return pos, neg


def endava_pairs():
    d = pd.read_csv(os.path.join(ROOT, "data", "all_tickets.csv"))
    sample = set(pd.read_csv(os.path.join(ROOT, "data", "external", "endava", "endava_sample1000.csv")).complaint_text)
    d["text"] = (d.title.fillna("").astype(str) + ". " + d.body.fillna("").astype(str)).str.strip(". ").str.strip()
    d = d[~d.text.isin(sample)].reset_index(drop=True)
    d["label"] = d.category.astype(str) + "-" + d.sub_category1.astype(str) + "-" + d.sub_category2.astype(str)
    groups = d.groupby("label").groups
    labels = [l for l, ix in groups.items() if len(ix) >= 2]
    pos, neg = [], []
    for _ in range(MAX_ENDAVA_POS):
        l = rng.choice(labels)
        i, j = rng.sample(list(groups[l]), 2)
        pos.append((d.text[i], d.text[j], 1, "endava"))
        k = rng.randrange(len(d))
        if d.label[k] != l:
            neg.append((d.text[i], d.text[k], 0, "endava_neg"))
    print(f"endava (excluding the 1,000 test sample): {len(pos)} pos, {len(neg)} neg")
    return pos, neg


def main():
    os.makedirs(OUT, exist_ok=True)
    ff_rows = set()
    for f in ("firefox", "firefox2", "firefox3"):
        ff_rows |= set(pd.read_csv(os.path.join(ROOT, "data", "external", f + ".csv")).row)
    fp, fn, _, _ = bug_pairs_firefox(ff_rows)
    ep, en, eg, _ = bug_pairs("eclipse_platform", "eclipse_platform.csv", set())
    sp, sn = silver_support()
    A = fp + fn + ep + en + sp + sn
    rng.shuffle(A)
    pd.DataFrame(A, columns=["text_a", "text_b", "label", "source"]).to_csv(os.path.join(OUT, "train_A.csv"), index=False)
    dp, dn = endava_pairs()
    B = A + dp + dn
    rng.shuffle(B)
    pd.DataFrame(B, columns=["text_a", "text_b", "label", "source"]).to_csv(os.path.join(OUT, "train_B.csv"), index=False)
    C = [(a, b, s) for a, b, _, s in fp + ep + dp]
    rng.shuffle(C)
    pd.DataFrame(C, columns=["anchor", "positive", "source"]).to_csv(os.path.join(OUT, "train_C.csv"), index=False)
    for name in ("A", "B", "C"):
        df = pd.read_csv(os.path.join(OUT, f"train_{name}.csv"))
        print(f"train_{name}: {len(df)} rows | " + str(df.source.value_counts().to_dict()))
    with zipfile.ZipFile(os.path.join(OUT, "training_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("A", "B", "C"):
            z.write(os.path.join(OUT, f"train_{name}.csv"), f"train_{name}.csv")
    print("zip:", round(os.path.getsize(os.path.join(OUT, "training_data.zip")) / 1e6, 1), "MB")


def bug_pairs_firefox(ff_rows):
    """Firefox files sit directly in labelling/ (not a sub-folder)."""
    return bug_pairs("", "mozilla_firefox.csv", ff_rows, tag="firefox")


if __name__ == "__main__":
    main()
