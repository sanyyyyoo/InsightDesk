"""
Spike-level grouping v2 (rule: results/spike_grouping_rule_v2.md).

Per-product label-free threshold (q-th percentile of the product's pairwise
similarities) and average linkage between alert groups, so no chaining.

  python experiments/dedup/spike_grouping_v2.py              # selection on seen data
  python experiments/dedup/spike_grouping_v2.py --confirm Q  # Firefox sample 2 + Play Store LOPO
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from spike_grouping import G, RES, embed, load, scores  # noqa: E402

QS = [99.5, 99, 98.5, 98, 97, 96, 95]
MIN_PURITY = 0.90


def product_tau(refs, pos, emb, dept, q):
    """refs of one partition -> {product: q-th percentile of its pairwise similarities}."""
    idx = np.array([pos[r] for r in refs])
    out = {}
    for p in np.unique(dept[idx]):
        e = emb[idx[dept[idx] == p]]
        s = e @ e.T
        out[p] = float(np.percentile(s[np.triu_indices(len(e), 1)], q)) if len(e) > 1 else 1.0
    return out


def alert_groups(a, pos, emb, dept, q):
    tau = product_tau(a.index, pos, emb, dept, q)
    groups = {}
    for c, g in a.groupby(a):
        groups[c] = [pos[r] for r in g.index]
    label = {c: c for c in groups}
    for p, t in tau.items():
        live = [c for c in groups if dept[groups[c][0]] == p]
        mem = {c: groups[c] for c in live}
        while len(mem) > 1:
            keys = list(mem)
            best, pair = -1.0, None
            for i, ci in enumerate(keys):
                for cj in keys[i + 1:]:
                    m = float((emb[mem[ci]] @ emb[mem[cj]].T).mean())
                    if m > best:
                        best, pair = m, (ci, cj)
            if best < t:
                break
            ci, cj = pair
            mem[ci] = mem[ci] + mem.pop(cj)
            for c in label:
                if label[c] == cj:
                    label[c] = ci
    return a.map(label)


def run(name, parts, df, pos, emb, dept, qs):
    base = scores(parts, df)
    print(f"\n{name}\n  cases only        capture={base[0]:.2f} capture(>=5)={base[1]:.2f} purity={base[2]:.3f} largest={base[3]}")
    out = {}
    for q in qs:
        r = scores([alert_groups(p, pos, emb, dept, q) for p in parts], df)
        out[q] = r
        print(f"  q={q:<5}  alert   capture={r[0]:.2f} capture(>=5)={r[1]:.2f} purity={r[2]:.3f} largest={r[3]}")
    return base, out


def setup(data, cal=None):
    df, pos, emb = embed(data, cal)
    return df, pos, emb, df.department.reindex(list(pos)).to_numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", type=float, default=None)
    args = ap.parse_args()
    if args.confirm is None:
        ps = setup("playstore")
        sel_ps = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
                  load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
                  load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
        _, a = run("SELECTION  Play Store within-company, R1", sel_ps, *ps, QS)
        ff = setup("firefox", "playstore")
        _, b = run("SELECTION  Firefox sample 1, R1",
                   [load(f"firefox_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox")], *ff, QS)
        ok = [q for q in QS if a[q][2] >= MIN_PURITY and b[q][2] >= MIN_PURITY]
        if not ok:
            print("\nno q keeps purity >= 0.90 on both: v2 rejected at selection")
            return
        q = max(ok, key=lambda q: (round((a[q][1] + b[q][1]) / 2, 4), q))
        print(f"\nselected q = {q} (mean capture(>=5) {(a[q][1] + b[q][1]) / 2:.3f})")
        return
    q = args.confirm
    ps = setup("playstore")
    f = f"playstore_e5_assignments_llm_{G}_founder_gated_lopo"
    halves = pd.read_csv(os.path.join(RES, f + ".csv")).held_out_half.unique()
    run("CONFIRM (secondary)  Play Store unseen company, R1", [load(f, "llm", "lopo", h) for h in halves], *ps, [q])
    ff2 = setup("firefox2", "playstore")
    base, r = run("CONFIRM  Firefox sample 2, R1",
                  [load(f"firefox2_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox2")], *ff2, [q])
    r = r[q]
    passed = r[2] >= MIN_PURITY and r[1] - base[1] >= 0.05
    print(f"\nPASS" if passed else "\nFAIL", f"(purity {r[2]:.3f}, capture(>=5) {base[1]:.2f} -> {r[1]:.2f})")


if __name__ == "__main__":
    main()
