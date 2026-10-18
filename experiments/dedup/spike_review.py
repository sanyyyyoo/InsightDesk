"""
Spike-detection checks asked by the review (rule: results/spike_review_rule.md). No LLM calls.
A: v2 vs raw-count rules vs Poisson CUSUM on the simulated Play Store streams of spike_sim.py.
B: overdispersion and v2's alert rate on REAL Firefox Bugzilla timestamps (one stream per component).

  python experiments/dedup/spike_review.py
"""
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import spike_sim as ss  # noqa: E402
from spike_grouping import G, load  # noqa: E402
from spike_grouping_v2 import setup  # noqa: E402

L, A, B = 28, 0.5, 7


def baseline(counts, first, t):
    n_units = counts.shape[0]
    lo = np.maximum(first, t - L)
    n = np.maximum(t - lo, 0)
    cs = np.concatenate([np.zeros((n_units, 1)), np.cumsum(counts, axis=1)], axis=1)
    s = cs[np.arange(n_units), t] - cs[np.arange(n_units), np.minimum(lo, t)]
    return (s + A) / (n + B)


def raw_rule(m):
    def det(counts, first):
        t = np.arange(counts.shape[1])[None, :]
        return (counts >= m) & (first[:, None] <= t)
    return det


def cusum(h):
    def det(counts, first):
        n_units, n_w = counts.shape
        S = np.zeros(n_units)
        al = np.zeros_like(counts, dtype=bool)
        for t in range(n_w):
            l0 = baseline(counts, first, t)
            l1 = l0 + 1.0
            k = (l1 - l0) / np.log(l1 / l0)
            live = first <= t
            S = np.where(live, np.maximum(0.0, S + counts[:, t] - k), 0.0)
            fire = live & (S >= h)
            al[:, t] = fire
            S[fire] = 0.0
        return al
    return det


def run_sim(det, sets, seed=ss.SEED):
    ss.DETECTOR = det
    rng = np.random.default_rng(seed)
    out = {}
    for issues, methods in sets:
        r = ss.one_stream(issues, {k: methods[k] for k in ("R1 cases", "R1 alert groups (v2)")}, rng, ss.TRIALS // len(sets))
        for m, v in r.items():
            t = out.setdefault(m, [0, 0, 0])
            t[0] += v["det"]; t[1] += v["false"]; t[2] += ss.TRIALS // len(sets)
    return {m: (d / n, f / n / ss.W * 100) for m, (d, f, n) in out.items()}


def part_a(lines):
    ps = setup("playstore")
    llm = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    single = [load(f"playstore_e5_assignments_single_oracle_seeds0_{G}_halfA_merge", "single", 0, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "B")]
    sets = ss.methods_for(llm, single, *ps)
    lines.append(f"A. Simulated Play Store streams ({ss.TRIALS} trials, {ss.W} six-hour windows each); detection within 12 h | false alerts per 100 windows")
    res = {"v2 (deployed)": run_sim(ss.make_detector_v2(2, 0.001), sets)}
    for m in (2, 3, 4):
        res[f"raw count >= {m}"] = run_sim(raw_rule(m), sets)
    grid = {h: run_sim(cusum(h), sets) for h in np.arange(1.0, 8.01, 0.5)}
    for unit in ("R1 cases", "R1 alert groups (v2)"):
        v2fa = res["v2 (deployed)"][unit][1]
        ok = [h for h, r in grid.items() if r[unit][1] <= v2fa]
        hm = min(ok) if ok else max(grid)
        res.setdefault(f"Poisson CUSUM, h matched ({unit})", {})[unit] = grid[hm][unit] + (hm,)
    res["Poisson CUSUM, h = 4"] = grid[4.0]
    for name, r in res.items():
        for unit, v in r.items():
            extra = f"  (h = {v[2]})" if len(v) > 2 else ""
            lines.append(f"  {unit:22s} {name:40s} detected {v[0]:.2f} | false {v[1]:.2f}/100w{extra}")
    print("\n".join(lines), flush=True)


def part_b(lines):
    src = os.path.join(HERE, "labelling", "mozilla_firefox.csv")
    d = pd.read_csv(src, usecols=["Component", "Created_time"])
    d["ts"] = pd.to_datetime(d.Created_time, utc=True, errors="coerce")
    d = d.dropna(subset=["ts"])
    end = d.ts.max()
    d = d[d.ts > end - pd.Timedelta(days=730)]
    w = ((d.ts - (end - pd.Timedelta(days=730))) / pd.Timedelta(hours=6)).astype(int).clip(0, 4 * 730 - 1)
    comps = d.Component.astype(str)
    codes, u = np.unique(comps, return_inverse=True)
    counts = np.zeros((len(codes), 4 * 730))
    np.add.at(counts, (u, w.to_numpy()), 1)
    mean, var = counts.mean(axis=1), counts.var(axis=1, ddof=1)
    keep = mean >= 0.05
    vmr = var[keep] / mean[keep]
    rng = np.random.default_rng(0)
    idx = np.where(keep)[0]
    boots = [var[s].sum() / mean[s].sum() for s in (rng.choice(idx, len(idx)) for _ in range(2000))]
    lines.append(f"\nB. Real Firefox Bugzilla streams: {len(d)} reports, last 730 days, 6-hour windows, "
                 f"{keep.sum()} components with mean >= 0.05 per window")
    lines.append(f"  variance-to-mean per component: median {np.median(vmr):.2f}, IQR {np.percentile(vmr, 25):.2f}-{np.percentile(vmr, 75):.2f}; "
                 f"pooled {var[keep].sum() / mean[keep].sum():.2f} [95% CI {np.percentile(boots, 2.5):.2f}, {np.percentile(boots, 97.5):.2f}]")
    first = np.argmax(counts > 0, axis=1)
    al = ss.make_detector_v2(2, 0.001)(counts[keep], first[keep])
    live = (np.arange(counts.shape[1])[None, :] >= first[keep][:, None]).sum()
    lines.append(f"  detector v2 alert rate on these real streams (no injected outbreaks; includes real bursts): "
                 f"{al.sum() / live * 100:.2f} per 100 component-windows (nominal at p = 0.001: at most 0.10)")
    print("\n".join(lines[-3:]), flush=True)


def main():
    lines = ["SPIKE REVIEW CHECKS (rule: results/spike_review_rule.md)"]
    part_b(lines)
    part_a(lines)
    lines.append("\nC. Vague alarm (vague_area_spike_results.txt, 300 simulated vague-only outages per size, 150 per product):"
                 " n=5 detected 0.52, n=10/20 detected 1.00; false alerts 0.35-0.39/100w with the alarm vs 0.20-0.24 cases alone")
    open(os.path.join(HERE, "results", "spike_review_results.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
