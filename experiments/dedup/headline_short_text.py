"""Headline for the deployed short-text setting: R1 with t_low = 0.40 (short-text channels), then RJ1
re-joining exactly as deployed (case pairs with similarity >= 0.26, backend/services/rejoin.py T_LOW).
Play Store, 3 held-out halves pooled; t_high per half as calibrated. Report-only, no tuning.

  python experiments/dedup/headline_short_text.py dry    # count uncached judge answers, no API calls
  python experiments/dedup/headline_short_text.py run
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rejoin as rj  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402

T_LOW_SHORT, T_LOW_REJOIN = 0.40, 0.26
_orig = rj.band_thresholds_wide
rj.band_thresholds_wide = lambda *a, **k: (_orig(*a, **k)[0], T_LOW_SHORT)


class DryPairJudge(rj.PairJudge):
    def same(self, a_rows, b_rows):
        import json
        a = [int(self.refs[m]) for m in a_rows[:rj.SHOW]]
        b = [int(self.refs[m]) for m in b_rows[:rj.SHOW]]
        key = json.dumps(sorted([a, b]))
        if key not in self.cache:
            self.calls += 1
            return False
        return self.cache[key]


def main(dry):
    tb, tn, parts, misses, calls, merges_all = np.zeros(3), np.zeros(3), [], 0, 0, []
    for seed, h in ((0, "A"), (1, "B"), (1, "A")):
        r = rj.rebuild("playstore", seed, h)
        misses += r["misses"]
        r["t_low"] = T_LOW_REJOIN
        pj = (DryPairJudge if dry else rj.PairJudge)(r["texts"], r["refs"], "playstore")
        base = np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])
        new, merges, _ = rj.run_variant(r, pj, 1)
        calls += pj.calls
        merges_all += merges
        _, ii = np.unique(r["issues"][r["test"]], return_inverse=True)
        tb += counts(base, ii, np.ones(ii.max() + 1))
        tn += counts(new.astype(str), ii, np.ones(ii.max() + 1))
        parts.append((r["issues"][r["test"]], base, new))
    pb, pn = prf(*tb), prf(*tn)
    print(f"{'DRY ' if dry else ''}R1 decision cache misses {misses} | rejoin pairs not cached {calls}")
    print(f"R1 (t_low 0.40)        P {pb[0]:.3f} R {pb[1]:.3f} F1 {pb[2]:.3f}")
    print(f"R1 + RJ1 (deployed)    P {pn[0]:.3f} R {pn[1]:.3f} F1 {pn[2]:.3f} | merges {len(merges_all)} "
          f"({sum(x == y for x, y in merges_all)} correct)")
    if not dry:
        lo, hi = rj.boot_diff(parts)
        print(f"  RJ1 - R1: P {pn[0]-pb[0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}] R {pn[1]-pb[1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}] "
              f"F1 {pn[2]-pb[2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")


if __name__ == "__main__":
    main(sys.argv[1] == "dry")
