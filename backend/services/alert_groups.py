"""
Alert groups for spike detection (the spike branch tested offline).

Cases stay exactly as dedup built them (RCA always reads cases). For counting
only, related cases of one product are joined into alert groups:
  - threshold per product, no labels: the 99th percentile of all pairwise
    cosine similarities among that product's complaints;
  - average linkage: repeatedly join the two groups with the highest MEAN
    similarity over all their complaint pairs while it is >= the threshold
    (no chaining through one similar pair).
A group that joins >= 2 cases gets its own spike check (spike_detection,
GROUP_MIN_COUNT complaints). Tested (experiments/dedup/spike_sim_groups.py):
on a fresh Firefox sample, case + group alerts caught 75% of simulated
outbreaks vs 68% for case alerts alone, with 1.1 false alerts per 100 windows.
"""

import numpy as np

PERCENTILE = 99.0
_EMB_CACHE = {}


def _embed(complaints):
    """Unit embeddings of the complaints' cleaned text (cached by complaint id)."""
    from backend.services.embedding_service import generate_embedding
    out = []
    for c in complaints:
        cid = c["complaint_id"]
        if cid not in _EMB_CACHE:
            v = np.asarray(generate_embedding(c.get("cleaned_text") or c.get("complaint_text") or ""), dtype=float)
            n = np.linalg.norm(v)
            _EMB_CACHE[cid] = v / n if n else v
        out.append(_EMB_CACHE[cid])
    return np.array(out)


def group_cases(case_ids, products, emb, percentile=PERCENTILE):
    """case_ids / products / emb: one entry per complaint. Returns {case_id: group label}."""
    case_ids = np.asarray(case_ids)
    products = np.array([p if p is not None else "" for p in products], dtype=object)
    label = {int(c): int(c) for c in case_ids}
    for p in sorted(set(products)):
        idx = np.where(products == p)[0]
        if len(idx) < 2:
            continue
        e = emb[idx]
        sims = e @ e.T
        tau = float(np.percentile(sims[np.triu_indices(len(idx), 1)], percentile))
        cases = sorted({int(c) for c in case_ids[idx]})
        pos = {c: k for k, c in enumerate(cases)}
        onehot = np.zeros((len(idx), len(cases)))
        onehot[np.arange(len(idx)), [pos[int(c)] for c in case_ids[idx]]] = 1
        S = onehot.T @ sims @ onehot              # summed similarity between every pair of groups
        size = onehot.sum(axis=0)
        alive = np.ones(len(cases), dtype=bool)
        owner = np.arange(len(cases))              # case position -> position of its group
        rows_of = {k: list(np.where(onehot[:, k] == 1)[0]) for k in range(len(cases))}
        while alive.sum() > 1:
            mask = np.outer(alive, alive)
            np.fill_diagonal(mask, False)
            mean = np.where(mask, S / np.outer(size, size), -np.inf)
            i, j = np.unravel_index(int(np.argmax(mean)), mean.shape)   # first max = lowest (i, j)
            i, j = min(i, j), max(i, j)
            # threshold check on the exact block mean (as tested), not the running sums:
            # a pair can sit exactly on the percentile, where rounding would flip it
            if float((e[rows_of[i]] @ e[rows_of[j]].T).mean()) < tau:
                break
            S[i, :] += S[j, :]
            S[:, i] += S[:, j]
            size[i] += size[j]
            alive[j] = False
            owner[owner == j] = i
            rows_of[i] = rows_of[i] + rows_of.pop(j)
        for c, k in pos.items():
            label[c] = cases[owner[k]]
    return label


def build_groups(complaints, percentile=PERCENTILE):
    """complaints: rows with complaint_id, case_id, product, cleaned_text. Returns {case_id: group id}."""
    rows = [c for c in complaints if c.get("case_id") is not None]
    if not rows:
        return {}
    emb = _embed(rows)
    return group_cases([r["case_id"] for r in rows], [r.get("product") for r in rows], emb, percentile)
