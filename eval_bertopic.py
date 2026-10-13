"""
BERTopic topic-quality evaluation (rule: reports/topics/bertopic_eval_rule.md).

Runs the app's own _run_bertopic (Config 8) on the 450 team-labelled Play Store
reviews, per company, and compares topics with the codebook AREAS. No LLM calls,
no Supabase / Pinecone (the database module is stubbed before import).

  python eval_bertopic.py
"""

import os
import sys
import types
from collections import Counter

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
stub = types.ModuleType("backend.database.supabase")
for _name in ("create_topic", "get_all_cases", "get_clustering_metadata", "get_clustering_statistics",
              "get_topic_by_slug", "update_case_topic", "update_clustering_metadata", "update_topic"):
    setattr(stub, _name, lambda *a, **k: None)                   # the DB helpers clustering_service imports
sys.modules["backend.database.supabase"] = stub

from sklearn.metrics import adjusted_rand_score, homogeneity_completeness_v_measure  # noqa: E402

import backend.services.clustering_service as cs  # noqa: E402
from backend.services.department_service import assign_department  # noqa: E402
from backend.services.preprocess import clean_text  # noqa: E402

EXP = "D:/PBL/InsightDesk-dedup/experiments/dedup"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "topics")


def evaluate(name, d, lines, rows):
    docs = d.review_text.astype(str).map(clean_text).tolist()
    emb = cs.embedding_model.encode(docs, show_progress_bar=False)
    topics, _, model = cs._run_bertopic(docs, emb)
    topics = np.asarray(topics)
    area = d.area.to_numpy()
    n_topics = len(set(topics) - {-1})
    out_share = float((topics == -1).mean())
    h, c, v = homogeneity_completeness_v_measure(area, topics)
    ari = adjusted_rand_score(area, topics)
    keep = topics != -1
    h2, c2, v2 = homogeneity_completeness_v_measure(area[keep], topics[keep]) if keep.sum() > 1 else (0, 0, 0)
    ari2 = adjusted_rand_score(area[keep], topics[keep]) if keep.sum() > 1 else 0
    lines.append(f"\n{name}: {len(d)} reviews, {n_topics} topics, outliers {out_share:.0%}")
    lines.append(f"  all reviews : homogeneity {h:.2f} completeness {c:.2f} V-measure {v:.2f} ARI {ari:.2f}")
    lines.append(f"  non-outliers: homogeneity {h2:.2f} completeness {c2:.2f} V-measure {v2:.2f} ARI {ari2:.2f}")
    for t in sorted(set(topics) - {-1}):
        members = area[topics == t]
        top_area, top_n = Counter(members).most_common(1)[0]
        words = [w for w, _ in (model.get_topic(t) or [])][:6]
        dept = assign_department(words)
        rows.append({"scope": name, "topic": int(t), "size": int(len(members)), "keywords": ", ".join(words),
                     "majority_area": top_area, "area_purity": round(top_n / len(members), 2),
                     "areas": dict(Counter(members).most_common(4)), "department_assigned": dept})
    return {"scope": name, "reviews": len(d), "topics": n_topics, "outlier_share": round(out_share, 2),
            "homogeneity": round(h, 2), "completeness": round(c, 2), "v_measure": round(v, 2), "ari": round(ari, 2),
            "v_measure_non_outliers": round(v2, 2), "ari_non_outliers": round(ari2, 2)}


def main():
    os.makedirs(OUT, exist_ok=True)
    lab = pd.read_csv(os.path.join(EXP, "labels", "playstore_final_labels.csv"))
    cb = pd.read_csv(os.path.join(EXP, "labels", "playstore_codebook.csv")).set_index("problem_code").area
    lab["area"] = lab.problem_code.map(cb).fillna("Other")
    lines, rows, summary = [], [], []
    lines.append("Company sizes: " + str(lab["product"].value_counts().to_dict()))
    for comp in ("Zendesk", "Freshdesk"):
        summary.append(evaluate(comp, lab[lab["product"] == comp].reset_index(drop=True), lines, rows))
    summary.append(evaluate("all 450 pooled (diagnostic)", lab.reset_index(drop=True), lines, rows))
    pd.DataFrame(summary).to_csv(os.path.join(OUT, "bertopic_vs_areas_summary.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "bertopic_topics_detail.csv"), index=False)
    detail = pd.DataFrame(rows)
    for comp in ("Zendesk", "Freshdesk"):
        dd = detail[detail.scope == comp]
        lines.append(f"\n{comp} topics (size, purity, majority area -> department assigned):")
        for r in dd.itertuples():
            lines.append(f"  t{r.topic:<3} n={r.size:<3} purity {r.area_purity:.2f} {r.majority_area:22s} -> "
                         f"{r.department_assigned:22s} [{r.keywords}]")
    text = "\n".join(lines)
    open(os.path.join(OUT, "bertopic_eval.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
