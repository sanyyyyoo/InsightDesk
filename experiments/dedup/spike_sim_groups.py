"""
Alert-group spikes on top of case alerts (rule: results/spike_groups_rule.md).

  python experiments/dedup/spike_sim_groups.py              # selection on seen data
  python experiments/dedup/spike_sim_groups.py --confirm M P # Firefox sample 3
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from spike_grouping import G, load  # noqa: E402
from spike_grouping_v2 import alert_groups, setup  # noqa: E402
from spike_sim import SEED, TRIALS, W, make_detector_v2  # noqa: E402

Q = 99
CASE_DET = make_detector_v2(2, 0.001)


def unit_matrix(unit, win, is_p):
    codes, u = np.unique(unit, return_inverse=True)
    counts = np.zeros((len(codes), W))
    np.add.at(counts, (u, win), 1)
    pc = np.zeros((len(codes), W))
    np.add.at(pc, (u[is_p], win[is_p]), 1)
    first = np.full(len(codes), W)
    np.minimum.at(first, u, win)
    return codes, counts, pc, first


def one_stream(issues, cases, groups, group_det, rng, trials):
    multi = pd.Series(cases).groupby(groups).nunique()            # cases per group
    multi_groups = set(multi[multi >= 2].index)
    sizes = pd.Series(issues).value_counts()
    pool = [p for p, n in sizes.items() if n >= 5 and not str(p).startswith("lone")]
    out = {"cases only": [0, 0], "cases + group alerts": [0, 0]}
    for _ in range(trials):
        p = pool[rng.integers(len(pool))]
        b = int(rng.integers(60, 111))
        win = rng.integers(0, W, size=len(issues))
        idx = np.where(issues == p)[0]
        idx = idx[rng.permutation(len(idx))]
        nb = math.ceil(0.3 * len(idx))
        win[idx[:nb]] = rng.integers(0, b, size=nb)
        win[idx[nb:]] = rng.integers(b, b + 2, size=len(idx) - nb)
        is_p = issues == p
        _, cc, cp, cf = unit_matrix(cases, win, is_p)
        ca = CASE_DET(cc, cf)
        case_hit = any((ca[:, t] & (cp[:, t] > 0)).any() for t in range(b, min(b + 3, W)))
        case_false = int((ca & (cp == 0)).sum())
        gcodes, gc, gp, gf = unit_matrix(groups, win, is_p)
        keep = np.array([g in multi_groups for g in gcodes])
        ga = group_det(gc, gf) & keep[:, None]
        group_hit = any((ga[:, t] & (gp[:, t] > 0)).any() for t in range(b, min(b + 3, W)))
        group_false = int((ga & (gp == 0)).sum())
        out["cases only"][0] += case_hit
        out["cases only"][1] += case_false
        out["cases + group alerts"][0] += case_hit or group_hit
        out["cases + group alerts"][1] += case_false + group_false
    return out


def run(name, sets, group_det, verbose=True):
    rng = np.random.default_rng(SEED)
    per = TRIALS // len(sets)
    tot = {"cases only": [0, 0], "cases + group alerts": [0, 0]}
    for s in sets:
        r = one_stream(*s, group_det, rng, per)
        for k in tot:
            tot[k][0] += r[k][0]
            tot[k][1] += r[k][1]
    n = per * len(sets)
    res = {k: (v[0] / n, v[1] / n / W * 100) for k, v in tot.items()}
    if verbose:
        print(f"  {name}")
        for k, (d, f) in res.items():
            print(f"    {k:22s} detected={d:.2f}  false alerts/100 windows={f:.2f}")
    return res


def streams(parts, df, pos, emb, dept):
    return [(df.issue_id.reindex(a.index).astype(str).to_numpy(), a.astype(str).to_numpy(),
             alert_groups(a, pos, emb, dept, Q).astype(str).to_numpy()) for a in parts]


def seen_sets():
    ps = setup("playstore")
    ff1 = setup("firefox", "playstore")
    ff2 = setup("firefox2", "playstore")
    return {
        "Play Store": streams([load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
                               load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
                               load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")], *ps),
        "Firefox 1": streams([load(f"firefox_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox")], *ff1),
        "Firefox 2": streams([load(f"firefox2_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox2")], *ff2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", nargs=2, default=None)
    args = ap.parse_args()
    if args.confirm:
        m, p = int(args.confirm[0]), float(args.confirm[1])
        ff3 = setup("firefox3", "playstore")
        s = streams([load(f"firefox3_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox3")], *ff3)
        print(f"CONFIRM  Firefox sample 3, group alerts m_g={m} p_g={p}")
        r = run("Firefox 3", s, make_detector_v2(m, p))
        (dc, fc), (ds, fs) = r["cases only"], r["cases + group alerts"]
        print(f"cases-only detector v2: {'meets' if dc >= 0.70 and fc <= 2 else 'misses'} its bar "
              f"(detected {dc:.2f}, false {fc:.2f})")
        ok = ds >= dc + 0.05 and fs <= 1.25 * fc
        print("PASS" if ok else "FAIL", f"(detection {dc:.2f} -> {ds:.2f}, false {fc:.2f} -> {fs:.2f}, "
                                        f"ceiling {1.25 * fc:.2f})")
        return
    sets = seen_sets()
    rows = []
    for m in (2, 3, 4, 5):
        for p in (0.001, 0.0001):
            det = make_detector_v2(m, p)
            print(f"m_g={m} p_g={p}")
            res = {k: run(k, v, det) for k, v in sets.items()}
            ok = all(r["cases + group alerts"][1] <= 1.25 * r["cases only"][1] for r in res.values())
            gain = np.mean([r["cases + group alerts"][0] - r["cases only"][0] for r in res.values()])
            rows.append((m, p, gain, ok))
    print("\nm_g p_g mean_gain within_false_limit")
    for r in rows:
        print(f"{r[0]} {r[1]:<7} {r[2]:+.3f} {r[3]}")
    good = [r for r in rows if r[3]]
    if good:
        best = max(good, key=lambda r: (round(r[2], 4), r[0], -r[1]))
        print(f"\nselected: m_g={best[0]} p_g={best[1]}")
    else:
        print("\nno setting stays within the false-alert limit on every seen set: rejected at selection")


if __name__ == "__main__":
    main()
