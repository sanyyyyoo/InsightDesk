"""
Department routing test (rule: reports/topics/routing_rule.md). No LLM calls.

  python eval_routing.py
"""

import json
import os
import sys
import types

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
stub = types.ModuleType("backend.database.supabase")
for _name in ("create_topic", "get_all_cases", "get_clustering_metadata", "get_clustering_statistics",
              "get_topic_by_slug", "update_case_topic", "update_clustering_metadata", "update_topic"):
    setattr(stub, _name, lambda *a, **k: None)
sys.modules["backend.database.supabase"] = stub

import backend.services.clustering_service as cs  # noqa: E402
from backend.services.department_service import assign_department  # noqa: E402
from backend.services.preprocess import clean_text  # noqa: E402

EXP = "D:/PBL/InsightDesk-dedup/experiments/dedup"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "topics")
AREA_DEPT = {"Login": "Authentication", "Account": "Authentication",
             **{a: "Engineering" for a in ("Stability", "Performance", "Install", "Notifications", "Text & editing",
                                           "Media", "Chat & calls", "Privacy")},
             **{a: "Product" for a in ("Tickets", "Macros & canned replies", "Layout", "Design", "Features", "Analytics")},
             "Not a problem": "General Support", "Other": "General Support"}
CODE_DEPT = {"support_no_response": "Customer Success", "billing_plan_complaint": "Billing & Accounts"}


def dept_of_code(code, cb):
    return CODE_DEPT.get(code) or AREA_DEPT.get(cb.get(code, "Other"), "General Support")


def main():
    lab = pd.read_csv(os.path.join(EXP, "labels", "playstore_final_labels.csv"))
    cbf = pd.read_csv(os.path.join(EXP, "labels", "playstore_codebook.csv"))
    cb = cbf.set_index("problem_code").area.to_dict()
    lab["ref"] = [dept_of_code(c, cb) for c in lab.problem_code]
    lab["text"] = lab.review_text.astype(str).map(clean_text)
    emb = cs.embedding_model.encode(lab.text.tolist(), show_progress_bar=False)
    unit = emb / np.linalg.norm(emb, axis=1, keepdims=True)

    # B: nearest codebook definition (no LLM)
    de = cs.embedding_model.encode(cbf.definition.astype(str).tolist(), show_progress_bar=False)
    de = de / np.linalg.norm(de, axis=1, keepdims=True)
    lab["B"] = [dept_of_code(cbf.problem_code.iloc[i], cb) for i in (unit @ de.T).argmax(axis=1)]

    # C: gpt-oss-120b codebook labels (already made, same model as the judge)
    llm = pd.DataFrame([json.loads(l) for l in open(os.path.join(EXP, "results", "llm_labels_playstore.jsonl"))])
    llm = llm.drop_duplicates("row", keep="last").set_index("row").code
    lab["C"] = [dept_of_code(llm.get(r, "other"), cb) for r in lab.row]

    rows = []
    for scope in ("Zendesk", "Freshdesk", "all 450"):
        d = lab if scope == "all 450" else lab[lab["product"] == scope]
        idx = d.index.to_numpy()
        topics, _, model = cs._run_bertopic(d.text.tolist(), emb[idx])
        dept_of_topic = {t: assign_department([w for w, _ in (model.get_topic(t) or [])][:6])
                         for t in set(topics) if t != -1}
        a = [dept_of_topic.get(t, "General Support") for t in topics]
        a = ["General Support" if x == "General" else x for x in a]
        lab.loc[idx, f"A_{scope}"] = a
        acc = {m: float((np.array(v) == d.ref.to_numpy()).mean()) for m, v in
               (("A current (BERTopic keywords)", a), ("B area, no LLM", d.B), ("C area from gpt-oss labels", d.C))}
        rows.append({"scope": scope, "reviews": len(d), **{k: round(v, 3) for k, v in acc.items()}})
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    print("\nreference departments:", lab.ref.value_counts().to_dict())
    for m in ("B", "C"):
        col = {"B": "B area, no LLM", "C": "C area from gpt-oss labels"}[m]
        better = all(res.set_index("scope").loc[s, col] >= res.set_index("scope").loc[s, "A current (BERTopic keywords)"] + 0.15
                     for s in ("Zendesk", "Freshdesk"))
        print(f"{col}: {'BETTER (>= +0.15 on both companies)' if better else 'not better by the rule'}")
    zd = lab[lab["product"] == "Zendesk"]
    print("\nZendesk: where the current routing sends each reference department (rows = reference):")
    print(pd.crosstab(zd.ref, zd["A_Zendesk"]).to_string())
    res.to_csv(os.path.join(OUT, "routing_results.csv"), index=False)


if __name__ == "__main__":
    main()
