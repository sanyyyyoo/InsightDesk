"""
Area check as a merge guard (rule: results/area_check_rule.md). No LLM calls.

  python experiments/dedup/area_check.py            # selection on the dev half
  python experiments/dedup/area_check.py --confirm MU
"""

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from e5_three_way import EMBED_MODEL  # noqa: E402
from spike_grouping import G, load  # noqa: E402
from spike_grouping import embed  # noqa: E402

HERE = os.path.dirname(__file__)
MUS = [0.0, 0.02, 0.05, 0.10]
NEVER_BLOCK = {"Not a problem", "Other"}


def areas(df, pos, emb):
    from sentence_transformers import SentenceTransformer
    cb = pd.read_csv(os.path.join(HERE, "labels", "playstore_codebook.csv"))
    enc = SentenceTransformer(EMBED_MODEL)
    de = enc.encode(cb.definition.astype(str).tolist(), normalize_embeddings=True, show_progress_bar=False)
    sims = emb @ de.T
    code_area = cb.area.to_numpy()
    best = sims.argmax(axis=1)
    area = code_area[best]
    top = sims.max(axis=1)
    other = np.array([sims[i, code_area != area[i]].max() for i in range(len(sims))])
    refs = list(pos)
    return pd.Series(area, index=refs), pd.Series(top - other, index=refs)


def guarded(a, area, margin, mu):
    """a: ref -> case (R1). Returns new assignment and (blocked right, blocked wrong)."""
    out, right, wrong, nxt = a.copy(), 0, 0, 10 ** 6
    for case, g in a.groupby(a):
        refs = sorted(g.index)
        founder = refs[0]
        for r in refs[1:]:
            fa, ra = area[founder], area[r]
            if (fa != ra and fa not in NEVER_BLOCK and ra not in NEVER_BLOCK
                    and margin[founder] >= mu and margin[r] >= mu):
                out[r] = nxt
                nxt += 1
                right += ISSUE[r] == ISSUE[founder]
                wrong += ISSUE[r] != ISSUE[founder]
    return out, right, wrong


def pairs(parts):
    tp = fp = tr = 0
    for a in parts:
        for x, y in itertools.combinations(a.index, 2):
            same, pred = ISSUE[x] == ISSUE[y], a[x] == a[y]
            tp += same and pred
            fp += pred and not same
            tr += same
    return tp, fp, tr


def report(name, parts, area, margin, mus):
    tp0, fp0, tr0 = pairs(parts)
    print(f"\n{name}\n  R1            P={tp0 / (tp0 + fp0):.3f} R={tp0 / tr0:.3f}")
    res = {}
    for mu in mus:
        new, br, bw = [], 0, 0
        for a in parts:
            g, r_, w_ = guarded(a, area, margin, mu)
            new.append(g)
            br += r_
            bw += w_
        tp, fp, tr = pairs(new)
        res[mu] = (tp / (tp + fp), tp / tr, tp / tp0)
        print(f"  mu={mu:.2f}  P={res[mu][0]:.3f} R={res[mu][1]:.3f} kept correct pairs={res[mu][2]:.0%} "
              f"| blocked merges: {bw} wrong, {br} right")
    return tp0 / tr0, res


def main():
    global ISSUE
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", type=float, default=None)
    args = ap.parse_args()
    df, pos, emb = embed("playstore")
    ISSUE = df.issue_id.astype(str)
    area, margin = areas(df, pos, emb)
    if args.confirm is None:
        dev = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfB_founder_gated", "llm", 0, "B")]
        _, res = report("SELECTION  dev half s0B", dev, area, margin, MUS)
        ok = [m for m in MUS if res[m][2] >= 0.90]
        if not ok:
            print("\nno mu keeps >= 90% of correct pairs: rejected at selection")
            return
        mu = max(ok, key=lambda m: (round(res[m][0], 4), m))
        print(f"\nselected mu = {mu}")
        return
    mu = args.confirm
    final = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
             load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
             load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    r0, res = report("CONFIRM  final halves s0A, s1A, s1B (pooled)", final, area, margin, [mu])
    p, r, _ = res[mu]
    print("\nPASS" if p >= 0.85 and r >= 0.90 * r0 else "\nFAIL", f"(P {p:.3f}, R {r:.3f} vs floor {0.90 * r0:.3f})")


if __name__ == "__main__":
    main()
