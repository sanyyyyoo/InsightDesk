"""
LLM labels with the humans' codebook, to compare LLM and human judgement.

Every review in labels/playstore_final_labels.csv (450, incl. the vague ones
the humans coded *_unspecified / other / not_a_problem) is labelled by the LLM
(gpt-oss-120b, temperature 0, 10 reviews per call) with the SAME codebook
and the SAME three rules the human labellers had. Output per review: code,
area, and whether the text itself names a concrete symptom (specific).

  python experiments/dedup/llm_labels.py            # label (cached, resumable)
  python experiments/dedup/llm_labels.py --compare  # compare with human labels

Frontier model done by hand (labelling/chatgpt_prompts.md, same prompt, blind):
  python experiments/dedup/llm_labels.py --import labelling/chatgpt_replies.txt --name chatgpt
  python experiments/dedup/llm_labels.py --compare --name chatgpt
"""

import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from e5_three_way import LLMJudge  # noqa: E402

HERE = os.path.dirname(__file__)
LABELS = os.path.join(HERE, "labels", "playstore_final_labels.csv")
CODEBOOK = os.path.join(HERE, "labels", "playstore_codebook.csv")
OUT = os.path.join(HERE, "results", "llm_labels_playstore.jsonl")
BATCH = 10

# exact labelling rules from the human sheet (labelling/playstore_labelling_sheet_v3.xlsx), same text ChatGPT gets
PROMPT = open(os.path.join(HERE, "labelling", "chatgpt_prompt_template.txt"), encoding="utf-8").read()


class Labeller:
    _call = LLMJudge._call
    _next_key = LLMJudge._next_key

    def __init__(self):
        from normalize import experiment_groq_clients
        self.clients = experiment_groq_clients()
        self.key_index, self.client = 0, self.clients[0]
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def label():
    d = pd.read_csv(LABELS)
    cb = pd.read_csv(CODEBOOK)
    book = "\n".join(f"{r.problem_code} | {r.area} | {r.definition}" for r in cb.itertuples())
    codes = set(cb.problem_code)
    done = {}
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            r = json.loads(line)
            done[r["row"]] = r
    todo = d[~d.row.isin(done)]
    print(f"{len(done)} labelled, {len(todo)} to go")
    lab = Labeller()
    for k in range(0, len(todo), BATCH):
        chunk = todo.iloc[k:k + BATCH]
        reviews = "\n".join(f'id {r.row} ({r.product}): "{r.review_text}"' for r in chunk.itertuples())
        reply = lab._call(PROMPT.format(codebook=book, reviews=reviews))
        items = reply if isinstance(reply, list) else (reply.get("labels") or next(
            (v for v in reply.values() if isinstance(v, list)), []))     # model sometimes returns a bare list
        got = {int(x["id"]): x for x in items if isinstance(x, dict) and str(x.get("id", "")).isdigit()}
        with open(OUT, "a", encoding="utf-8") as f:
            for r in chunk.itertuples():
                x = got.get(int(r.row))
                if x is None:
                    continue                      # missing -> retried on the next run
                code = x.get("code") if x.get("code") in codes else "other"
                f.write(json.dumps({"row": int(r.row), "code": code, "specific": bool(x.get("specific")),
                                    "raw_code": x.get("code")}) + "\n")
        print(f"  {min(k + BATCH, len(todo))}/{len(todo)}", flush=True)


def kappa(a, b):
    a, b = pd.Series(a).astype(str).values, pd.Series(b).astype(str).values
    po = (a == b).mean()
    cats = set(a) | set(b)
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def import_replies(path, name):
    """Parse pasted JSON replies; keep only codebook codes (anything else -> other)."""
    import re
    codes = set(pd.read_csv(CODEBOOK).problem_code)
    rows = set(pd.read_csv(LABELS).row)
    txt = open(path, encoding="utf-8").read()
    got = {}
    for block in re.split(r"=== reply \d+ ===", txt)[1:]:
        m = re.search(r"\{.*\}", block, re.S)
        if not m:
            continue
        try:
            for x in json.loads(m.group(0)).get("labels", []):
                if int(x["id"]) in rows:
                    got[int(x["id"])] = x
        except (ValueError, KeyError, TypeError):
            print("could not parse one reply block; check it")
    out = OUT.replace(".jsonl", f"_{name}.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for r, x in got.items():
            code = x.get("code") if x.get("code") in codes else "other"
            f.write(json.dumps({"row": r, "code": code, "specific": x.get("specific"), "confidence": x.get("confidence"),
                                "raw_code": x.get("code")}) + "\n")
    print(f"imported {len(got)} of {len(rows)} reviews -> {out}")


def import_sheet(path, name):
    """Completed chatgpt_label_sheet.xlsx (or .csv) -> labels file; unknown codes -> other."""
    codes = set(pd.read_csv(CODEBOOK).problem_code)
    x = pd.read_excel(path, sheet_name=0) if path.endswith(".xlsx") else pd.read_csv(path)
    x = x.dropna(subset=["id"])
    out = OUT.replace(".jsonl", f"_{name}.jsonl")
    bad = 0
    with open(out, "w", encoding="utf-8") as f:
        for r in x.itertuples():
            raw = str(r.problem_code).strip() if isinstance(r.problem_code, str) else None
            bad += raw is not None and raw not in codes
            if raw is None:
                continue
            f.write(json.dumps({"row": int(r.id), "code": raw if raw in codes else "other", "raw_code": raw,
                                "confidence": getattr(r, "confidence", None) if isinstance(getattr(r, "confidence", None), str) else None,
                                "notes": r.notes if isinstance(getattr(r, "notes", None), str) else None}) + chr(10))
    n = sum(1 for _ in open(out, encoding="utf-8"))
    print(f"imported {n} of {len(x)} rows ({bad} codes not in the codebook -> other) -> {out}")


def compare(name=None):
    global OUT
    if name:
        OUT = OUT.replace(".jsonl", f"_{name}.jsonl")
    d = pd.read_csv(LABELS)
    cb = pd.read_csv(CODEBOOK).set_index("problem_code")
    llm = pd.DataFrame([json.loads(l) for l in open(OUT, encoding="utf-8")]).drop_duplicates("row", keep="last")
    m = d.merge(llm, on="row")
    m["h_area"], m["l_area"] = m.problem_code.map(cb.area), m.code.map(cb.area)
    vague = m.problem_code.astype(str).str.contains("unspecified|^other$|not_a_problem")
    m["h_vague"] = vague
    m["l_vague"] = m.code.astype(str).str.contains("unspecified|^other$|not_a_problem")
    if "specific" not in m or m.specific.isna().all():      # exact-instruction prompt: no separate flag
        m["specific"] = ~m.l_vague
    m["specific"] = m.specific.fillna(~m.l_vague).astype(bool)
    print(f"reviews compared: {len(m)} of {len(d)}")
    print(f"exact code:  agreement {(m.problem_code == m.code).mean():.2f}, kappa {kappa(m.problem_code, m.code):.3f}")
    print(f"area:        agreement {(m.h_area == m.l_area).mean():.2f}, kappa {kappa(m.h_area, m.l_area):.3f}")
    print(f"vague-vs-specific code: agreement {(m.h_vague == m.l_vague).mean():.2f}")
    print("\nhuman specific code, but LLM says the text names no symptom:",
          int((~m.h_vague & ~m.specific).sum()), "of", int((~m.h_vague).sum()))
    print("  ... of those, LLM still picks the same AREA:",
          int((~m.h_vague & ~m.specific & (m.h_area == m.l_area)).sum()))
    if "confidence" in m:
        print("LLM 'unsure' on:", int((m.confidence == "unsure").sum()), "reviews")
    print("human vague code, but LLM gives a specific code:", int((m.h_vague & ~m.l_vague).sum()), "of", int(m.h_vague.sum()))
    rel = os.path.join(HERE, "labelling", "relabel_majority.csv")
    if os.path.exists(rel):                       # LLM vs each human, on the blind 3-person relabel set
        r = pd.read_csv(rel)
        sc = pd.read_csv("data/external/playstore_scored.csv")[["complaint_ref", "row"]]
        r = r.merge(sc, on="complaint_ref").merge(llm, on="row")
        votes = r.votes.str.split("|", expand=True)
        print(f"\nblind relabel set ({len(r)} reviews), Cohen kappa on exact code:")
        for i, j in [(0, 1), (0, 2), (1, 2)]:
            print(f"  human {i + 1} vs human {j + 1}: {kappa(votes[i], votes[j]):.3f}")
        for i in range(3):
            print(f"  LLM vs human {i + 1}:     {kappa(r.code, votes[i]):.3f}")
        print(f"  LLM vs majority:     {kappa(r.code, r.majority):.3f}")
    m.to_csv(OUT.replace(".jsonl", "_vs_human.csv"), index=False)
    print("saved", OUT.replace(".jsonl", "_vs_human.csv"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--import", dest="imp", default=None)
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    if a.imp and a.imp.endswith((".xlsx", ".csv")):
        import_sheet(a.imp, a.name or "chatgpt")
    elif a.imp:
        import_replies(a.imp, a.name or "chatgpt")
    elif a.compare:
        compare(a.name)
    else:
        label()
