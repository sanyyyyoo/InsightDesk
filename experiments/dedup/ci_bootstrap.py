"""
Bootstrap confidence intervals for the frozen dedup results (no LLM calls).

Cluster bootstrap: resample whole true problem groups (issue_id) with
replacement, 2000 times, inside each evaluated partition; a review copied k
times keeps its prediction; pairs between copies of the SAME review are not
counted. Pairwise precision / recall / F1 are pooled over the partitions of a
setting. Differences between methods use the same resamples (paired).

  python experiments/dedup/ci_bootstrap.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from spike_grouping import G, RES  # noqa: E402

B, SEED = 2000, 11


def c2(x):
    return x * (x - 1) / 2.0


def load(f, judge, seed, half):
    a = pd.read_csv(os.path.join(RES, f + ".csv"))
    a = a[(a.judge == judge) & (a.split_seed.astype(str) == str(seed)) & (a.held_out_half == half)]
    return a.drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case


def counts(case, issue, w_issue):
    """TP, predicted pairs, true pairs when true group g is drawn w_g times (cluster bootstrap).

    Each draw of a group is its own copy: pairs INSIDE a group count once per copy (weight w_g),
    pairs ACROSS groups count over all copies (w_g * w_h), pairs between two copies of the same
    group are not counted. Both kinds then have expected weight 1, so the resampled precision is
    not biased. (The earlier version, counts_v1, gave within-group pairs weight w_g^2, about 2 in
    expectation, which pushed precision intervals upward.) With w = 1 both equal the point estimate.
    """
    case = np.asarray(case)
    issue = np.asarray(issue)
    _, cidx = np.unique(case.astype(str), return_inverse=True)
    cells, n_cell = np.unique(np.stack([cidx, issue]), axis=1, return_counts=True)
    cc, ci, n = cells[0], cells[1], n_cell.astype(float)
    wi = np.asarray(w_issue, dtype=float)[ci]
    within = wi * c2(n)                                  # same case, same group: once per copy
    tp = float(within.sum())
    N = n * wi
    cross = (np.bincount(cc, weights=N) ** 2 - np.bincount(cc, weights=N ** 2)) / 2.0
    pred = tp + float(cross.sum())
    n_iss = np.bincount(issue, minlength=len(w_issue)).astype(float)
    true = float((np.asarray(w_issue, dtype=float) * c2(n_iss)).sum())
    return tp, pred, true


def bcubed(case, issue, w_issue):
    """B-cubed P, R, F1 with the same copy rule (a review's case-mates = its own copy's group members
    in the case + all copies of other groups in the case)."""
    case = np.asarray(case)
    issue = np.asarray(issue)
    _, cidx = np.unique(case.astype(str), return_inverse=True)
    cells, inv, n_cell = np.unique(np.stack([cidx, issue]), axis=1, return_inverse=True, return_counts=True)
    inv = np.asarray(inv).ravel()
    cc, ci, n = cells[0], cells[1], n_cell.astype(float)
    w = np.asarray(w_issue, dtype=float)
    N = n * w[ci]
    other = np.bincount(cc, weights=N)[cc] - N            # all copies of OTHER groups in the case
    p_cell = n / (n + other)
    n_iss = np.bincount(issue, minlength=len(w)).astype(float)
    r_cell = n / n_iss[ci]
    wr = w[issue]
    P = float((wr * p_cell[inv]).sum() / wr.sum())
    R = float((wr * r_cell[inv]).sum() / wr.sum())
    return P, R, (2 * P * R / (P + R) if P + R else 0.0)


def counts_v1(case, issue, w_issue):
    """Superseded (kept to document the correction): within-group pairs weighted w_g^2."""
    w = w_issue[issue]                       # weight of every review
    self_pairs = c2(w)
    df = pd.DataFrame({"case": case, "issue": issue, "w": w, "s": self_pairs})
    cell = df.groupby(["case", "issue"]).agg(N=("w", "sum"), S=("s", "sum"))
    tp = float((c2(cell.N) - cell.S).sum())
    byc = df.groupby("case").agg(N=("w", "sum"), S=("s", "sum"))
    pred = float((c2(byc.N) - byc.S).sum())
    byi = df.groupby("issue").agg(N=("w", "sum"), S=("s", "sum"))
    true = float((c2(byi.N) - byi.S).sum())
    return tp, pred, true


def prf(tp, pred, true):
    p = tp / pred if pred else 0.0
    r = tp / true if true else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def run(name, methods, label_of):
    """methods: {method: [Series ref->case per partition]}; same partitions for every method."""
    rng = np.random.default_rng(SEED)
    parts = list(zip(*methods.values()))
    names = list(methods)
    prepared = []
    for per_method in parts:
        refs = per_method[0].index
        issue_codes, issue = np.unique(label_of.reindex(refs).astype(str).to_numpy(), return_inverse=True)
        cases = [m.reindex(refs).to_numpy() for m in per_method]
        prepared.append((issue, len(issue_codes), cases))
    point = {}
    for k, n in enumerate(names):
        tot = np.zeros(3)
        for issue, n_iss, cases in prepared:
            tot += counts(cases[k], issue, np.ones(n_iss))
        point[n] = prf(*tot)
    boot = {n: [] for n in names}
    for _ in range(B):
        tot = {n: np.zeros(3) for n in names}
        for issue, n_iss, cases in prepared:
            w = np.bincount(rng.integers(0, n_iss, n_iss), minlength=n_iss).astype(float)
            for k, n in enumerate(names):
                tot[n] += counts(cases[k], issue, w)
        for n in names:
            boot[n].append(prf(*tot[n]))
    true_pairs = sum(counts(cases[0], issue, np.ones(n_iss))[2] for issue, n_iss, cases in prepared)
    print(f"\n{name}  ({int(true_pairs)} true duplicate pairs, {sum(len(i) for i, _, _ in prepared)} reviews)")
    print(f"  {'method':16s} {'precision':>22s} {'recall':>22s} {'F1':>22s}")
    arr = {n: np.array(boot[n]) for n in names}
    for n in names:
        lo, hi = np.percentile(arr[n], [2.5, 97.5], axis=0)
        cells = [f"{point[n][j]:.3f} [{lo[j]:.3f},{hi[j]:.3f}]" for j in range(3)]
        print(f"  {n:16s} {cells[0]:>22s} {cells[1]:>22s} {cells[2]:>22s}")
    if "R1" in arr:
        for n in names:
            if n == "R1":
                continue
            d = arr[n] - arr["R1"]
            lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
            print(f"  {n} minus R1: precision {point[n][0] - point['R1'][0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}], "
                  f"F1 {point[n][2] - point['R1'][2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    p_r1 = arr.get("R1")
    if p_r1 is not None:
        print(f"  share of resamples with R1 precision >= 0.85: {(p_r1[:, 0] >= 0.85).mean():.1%}")


def main():
    ps = pd.read_csv("data/external/playstore_scored.csv").set_index("complaint_ref").issue_id
    H = [(0, "A"), (1, "A"), (1, "B")]
    llm = lambda tag: [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA{tag}_founder_gated" if s == 0
                            else f"playstore_e5_assignments_llm_seeds1_{G}{tag}_founder_gated", "llm", s, h) for s, h in H]
    so = lambda j: [load(f"playstore_e5_assignments_single_oracle_seeds0_{G}_halfA_merge" if s == 0
                         else f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", j, s, h) for s, h in H]
    run("PLAY STORE, within company (final halves s0A, s1A, s1B)",
        {"R1": llm(""), "R1 + agreement": llm("_top1agree"), "cosine only": so("single"), "oracle": so("oracle")}, ps)

    def lopo(f, j):
        a = pd.read_csv(os.path.join(RES, f + ".csv"))
        return [load(f, j, "lopo", h) for h in sorted(a.held_out_half.unique())]
    run("PLAY STORE, unseen company (leave one company out)",
        {"R1": lopo(f"playstore_e5_assignments_llm_{G}_founder_gated_lopo", "llm"),
         "R1 + agreement": lopo(f"playstore_e5_assignments_llm_{G}_top1agree_founder_gated_lopo", "llm"),
         "cosine only": lopo(f"playstore_e5_assignments_single_oracle_{G}_lopo", "single"),
         "oracle": lopo(f"playstore_e5_assignments_single_oracle_{G}_lopo", "oracle")}, ps)

    for ff in ("firefox", "firefox2", "firefox3"):
        d = pd.read_csv(f"data/external/{ff}.csv")
        lab = pd.Series(d.issue_id.to_numpy(), index=d.complaint_ref + 1_000_000)
        f = f"{ff}_e5_assignments_{{}}_{G}{{}}_ext_playstore"
        run(f"FIREFOX sample {ff[-1] if ff[-1].isdigit() else '1'} (calibrated on Play Store only)",
            {"R1": [load(f.format("llm", "_founder_gated"), "llm", "ext", ff)],
             "cosine only": [load(f.format("single_oracle", ""), "single", "ext", ff)],
             "oracle": [load(f.format("single_oracle", ""), "oracle", "ext", ff)]}, lab)


if __name__ == "__main__":
    main()
