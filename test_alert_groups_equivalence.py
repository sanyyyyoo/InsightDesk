"""
Equivalence check: backend/services/alert_groups.py must form exactly the same
alert groups as the tested experiment code (experiments/dedup/spike_grouping_v2.py,
q = 99), on the frozen R1 cases of the Play Store held-out halves and of the
three Firefox samples. Plus offline checks of the group spike rule (>= 3).

  python test_alert_groups_equivalence.py
"""

import os
import sys

import numpy as np
import pandas as pd

from test_r1_equivalence import EXP, G, RES, load_exp, prepare, same_partition

os.environ.setdefault("HF_HUB_OFFLINE", "1")


def main():
    from backend.services.alert_groups import group_cases
    cwd = os.getcwd()
    os.chdir(EXP)
    from spike_grouping_v2 import alert_groups as exp_groups
    results = []
    try:
        sets = [("playstore", None, [(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", 0, "A"),
                                     (f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", 1, "A"),
                                     (f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", 1, "B")])]
        for ff in ("firefox", "firefox2", "firefox3"):
            sets.append((ff, "playstore", [(f"{ff}_e5_assignments_llm_{G}_founder_gated_ext_playstore", "ext", ff)]))
        for data, cal, parts in sets:
            df, _, emb = prepare(data, cal)
            refs = df.complaint_ref.to_numpy()
            pos = {int(r): k for k, r in enumerate(refs)}
            dept = df.department.astype(str).to_numpy()
            for f, seed, half in parts:
                a = pd.Series(load_exp(f, "llm", seed, half))
                exp = exp_groups(a, pos, emb, dept, 99).to_dict()
                rows = [pos[int(r)] for r in a.index]
                app_case = group_cases(a.to_numpy(), dept[rows], emb[rows], 99)
                app = {int(r): app_case[int(c)] for r, c in a.items()}
                bad = same_partition(app, exp)
                n_groups = len(set(exp.values()))
                results.append((f"{data} {seed}{half if seed != 'ext' else ''}", len(a), n_groups, len(bad)))
    finally:
        os.chdir(cwd)
    ok = True
    for name, n, g, bad in results:
        ok &= bad == 0
        print(f"{'ok  ' if bad == 0 else 'FAIL'} {name}: {n} complaints, {g} alert groups, {bad} grouped differently")

    # group spike rule: >= 3 complaints (case alerts need >= 2)
    import types
    stub = types.ModuleType("backend.database.supabase")
    stub.get_case_history = stub.get_case_history_bulk = lambda *a: []
    sys.modules.setdefault("backend.database.supabase", stub)
    from datetime import datetime, timedelta, timezone

    from backend.services.spike_detection import detect_from_history, detect_group_from_history
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    w = lambda k, c: {"window_start": (t0 + timedelta(hours=6 * k)).isoformat(), "complaint_ct": c}
    case_a = [w(0, 1), w(20, 2)]                 # one complaint long ago, 2 now
    case_b = [w(5, 1), w(20, 1)]                 # one complaint long ago, 1 now
    for name, rows, fn, expect in [
            ("case A alone (2 now) -> no case alert", case_a, detect_from_history, False),
            ("case B alone (1 now) -> no case alert", case_b, detect_from_history, False),
            ("A + B as one alert group (3 now) -> group alert", case_a + case_b, detect_group_from_history, True),
            ("group with only 2 now -> no group alert (needs >= 3)", [w(0, 1), w(20, 1), w(5, 1), w(20, 1)],
             detect_group_from_history, False)]:
        got = fn(rows)["spike"]
        ok &= got == expect
        print(f"{'ok  ' if got == expect else 'FAIL'} {name}")
    print("ALL PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
