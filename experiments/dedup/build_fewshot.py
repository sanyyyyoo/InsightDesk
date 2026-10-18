"""
Few-shot examples for the LLM judge, drawn ONLY from the tuning side of a split.

For split seed S, half H, the test reviews are one half of the problems; the
examples come from the other half, so no problem appears both as an example and
in the evaluation. Selection is automatic and seeded (no hand-picking):
  SAME       pairs of reviews with the same problem in the same product whose
             cosine falls inside the judge's band (where it actually decides)
  DIFFERENT  hard negatives: same product, different problem, highest cosine
             inside the band, at most one pair per problem
Texts are cut to MAX_CHARS to keep the prompt short.

Output: results/fewshot_examples_s{S}{H}.json

  python experiments/dedup/build_fewshot.py --seed 0 --half B
"""

import argparse
import itertools
import json
import os
import sys

import numpy as np

sys.path.append(os.path.dirname(__file__))

import e5_three_way as e5  # noqa: E402
from e5_three_way import band_thresholds_wide  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

N_SAME, N_DIFF, MAX_CHARS = 6, 6, 180
RES = os.path.join(os.path.dirname(__file__), "results")


def short(t):
    t = " ".join(str(t).split())
    return t if len(t) <= MAX_CHARS else t[:MAX_CHARS].rsplit(" ", 1)[0] + "..."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--half", default="B")
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    texts = df["complaint_text"].astype(str).tolist()
    ids = np.array(sorted(set(issues)))
    half = set(np.random.default_rng(args.seed).choice(ids, size=len(ids) // 2, replace=False))
    a = np.where(np.isin(issues, list(half)))[0]
    b = np.where(~np.isin(issues, list(half)))[0]
    tune, test = (a, b) if args.half == "B" else (b, a)
    t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])

    same, diff = [], []
    for i, j in itertools.combinations(tune, 2):
        if groups[i] != groups[j]:
            continue
        s = float(emb[i] @ emb[j])
        if not t_low <= s < t_high:
            continue
        (same if issues[i] == issues[j] else diff).append((s, int(i), int(j)))
    rng = np.random.default_rng(42)
    picked_same = [same[k] for k in rng.choice(len(same), size=min(N_SAME, len(same)), replace=False)]
    picked_diff, used = [], set()
    for s, i, j in sorted(diff, reverse=True):             # hardest negatives first
        if issues[i] in used or issues[j] in used:
            continue
        picked_diff.append((s, i, j))
        used |= {issues[i], issues[j]}
        if len(picked_diff) == N_DIFF:
            break
    examples = [{"a": short(texts[i]), "b": short(texts[j]), "same": True, "cos": round(s, 3)}
                for s, i, j in picked_same] + \
               [{"a": short(texts[i]), "b": short(texts[j]), "same": False, "cos": round(s, 3)}
                for s, i, j in picked_diff]
    order = np.random.default_rng(7).permutation(len(examples))
    examples = [examples[k] for k in order]
    assert not ({issues[i] for _, i, _ in picked_same + picked_diff} & set(issues[test])), "leak"
    out = os.path.join(RES, f"fewshot_examples_s{args.seed}{args.half}.json")
    json.dump(examples, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"band [{t_low:.2f},{t_high:.2f}) | candidate pairs: same {len(same)}, different {len(diff)}")
    for e in examples:
        print(("SAME " if e["same"] else "DIFF ") + f"{e['cos']:.2f} | {e['a'][:70]}  ||  {e['b'][:70]}")
    print("no test problem used | saved", out)


if __name__ == "__main__":
    main()
