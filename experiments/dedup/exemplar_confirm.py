"""EXA vs deployed R1, both with one re-joining pass (rule: results/exemplar_auto_rule.md)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import e5_three_way as e5
import rejoin as rj
from ci_bootstrap import counts, prf

def run(data, seed, half, cal, exa):
    e5.EXEMPLAR_AUTO_ONLY = exa
    r = rj.rebuild(data, seed, half, calibrate=cal)
    new, merges, _ = rj.run_variant(r, rj.PairJudge(r["texts"], r["refs"], "playstore" if data == "playstore" else data), 1)
    _, iss = np.unique(r["issues"][r["test"]], return_inverse=True)
    return np.array(counts(np.asarray(new).astype(str), iss, np.ones(iss.max() + 1))), len(merges), sum(a == b for a, b in merges), r["misses"]

out = ["EXEMPLAR FIX (EXA) vs R1, both + RJ1 (rule results/exemplar_auto_rule.md)"]
res = {}
for name, parts in {"playstore": [("playstore", s, h, False) for s, h in ((0, "A"), (1, "B"), (1, "A"))],
                    "bugzilla": [("firefox3", None, None, True), ("thunderbird", None, None, True)]}.items():
    for exa in (False, True):
        t, m, c, miss = np.zeros(3), 0, 0, 0
        for p in parts:
            a, mm, cc, ms = run(*p, exa); t += a; m += mm; c += cc; miss += ms
        p_, r_, f_ = prf(*t)[:3]
        res[(name, exa)] = (p_, r_, c / max(m, 1))
        out.append(f"  {name:9s} {'EXA' if exa else 'R1 '}+RJ1  P {p_:.3f} R {r_:.3f} F1 {f_:.3f} | rejoin merges {m}, correct {c} | new judge calls {miss}")
        print(out[-1], flush=True)
ok = (res[("playstore", True)][0] >= res[("playstore", False)][0] - 0.01 and res[("bugzilla", True)][0] >= res[("bugzilla", False)][0] - 0.01
      and res[("playstore", True)][1] >= res[("playstore", False)][1] - 0.03 and res[("bugzilla", True)][1] >= res[("bugzilla", False)][1] - 0.03
      and res[("playstore", True)][2] >= res[("playstore", False)][2] and res[("bugzilla", True)][2] >= res[("bugzilla", False)][2])
out.append(f"RULE: {'ADOPT EXA' if ok else 'keep R1 (EXA not adopted)'}")
print(out[-1]); open(os.path.join(HERE, "results", "exemplar_confirm.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
