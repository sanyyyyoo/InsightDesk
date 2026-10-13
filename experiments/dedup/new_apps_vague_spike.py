"""
Vague counter confirmation on the new help-desk apps (rule: results/vague_counter_confirm_rule.md).
No LLM calls; uses R1's real app decisions from the new-apps replay.

  python experiments/dedup/new_apps_vague_spike.py
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from spike_sim import SEED, TRIALS, W  # noqa: E402
from vague_area_spike_sim import alerts_for  # noqa: E402

REPLAY = "D:/PBL/InsightDesk-claude-review/reports/new_apps/replay_assignments.csv"


def trial(d, n, rng):
    base = d.copy()
    base["win"] = rng.integers(0, W, len(base))
    base["out"] = False
    b = int(rng.integers(60, 111))
    if n:
        src = base[base.vague]
        cp = src.iloc[rng.integers(0, len(src), n)].copy()
        cp["win"] = rng.integers(b, b + 2, n)
        cp["out"] = True
        cp["case"] = ["inj_%d" % k for k in range(n)]             # each copy a new singleton case
        stream = pd.concat([base, cp], ignore_index=True)
    else:
        stream = base
    w, o = stream.win.to_numpy(), stream.out.to_numpy()
    hc, fc = alerts_for(stream.case.to_numpy(), w, o)
    vk = np.where(stream.vague, "vague", "_specific")
    hv, fv = alerts_for(vk, w, o, valid=lambda c: c == "vague")
    hit_c = bool(hc[:, b:min(b + 3, W)].any())
    hit_v = bool(hv[:, b:min(b + 3, W)].any())
    return hit_c, hit_c or hit_v, fc, fv


def main():
    a = pd.read_csv(REPLAY)
    a["vague"] = a.route.eq("vague")
    a["case"] = a["product"].astype(str) + "|" + a.case_id.astype(str)
    apps = a["product"].unique()
    print("streams: " + ", ".join(f"{p}: {int((a['product'] == p).sum())} reviews, "
                                  f"{int(a[a['product'] == p].vague.sum())} vague" for p in apps))
    per = TRIALS // len(apps)
    res = {}
    for n in (0, 5, 10, 20):
        rng = np.random.default_rng(SEED)
        det_c = det_cv = f_c = f_v = 0
        for p in apps:
            dp = a[a["product"] == p]
            for _ in range(per):
                hc, hcv, fc, fv = trial(dp, n, rng)
                det_c += hc
                det_cv += hcv
                f_c += fc
                f_v += fv
        t = per * len(apps)
        res[n] = (det_c / t, det_cv / t, f_c / t / W * 100, (f_c + f_v) / t / W * 100, f_v / t / W * 100)
        name = "null stream (no outbreak)" if n == 0 else f"vague outage n={n}"
        print(f"  {name:26s} C: detected {res[n][0]:.2f}, false {res[n][2]:.2f}/100w | "
              f"C+V: detected {res[n][1]:.2f}, false {res[n][3]:.2f}/100w (vague counter adds {res[n][4]:.2f})")
    ok = res[10][1] >= 0.80 and res[0][3] <= 1.0 and res[0][4] <= 0.5
    print(f"\nRULE: vague counter {'ADOPT' if ok else 'not adopted'} (n=10 detection {res[10][1]:.2f} >= 0.80? "
          f"null false {res[0][3]:.2f} <= 1.0? added {res[0][4]:.2f} <= 0.5?)")


if __name__ == "__main__":
    main()
