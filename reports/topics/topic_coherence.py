"""Topic statistics and c_v coherence of the staging BERTopic run.

Input: staging_topics_snapshot.json (topics and cases exported from the staging TEST project on 2026-10-20).
  python reports/topics/topic_coherence.py   ->  reports/topics/topic_coherence_results.txt
"""
import collections
import json
import os
import random
import re
import sys

from gensim.corpora import Dictionary
from gensim.models.coherencemodel import CoherenceModel

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "staging_topics_snapshot.json")


def main():
    d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else SNAP, encoding="utf-8"))
    tok = lambda s: re.findall(r"[a-z0-9]+", (s or "").lower())
    docs = [tok(c["representative_text"]) for c in d["cases"]]
    dic = Dictionary(docs)
    tops = []
    for t in d["topics"]:
        words = []
        for kw in (t["description"] or "").split(","):
            for w in tok(kw):
                if w in dic.token2id and w not in words:
                    words.append(w)
        if len(words) >= 2:
            tops.append((t, words[:5]))
    cv = lambda ws: CoherenceModel(topics=ws, texts=docs, dictionary=dic, coherence="c_v", topn=5, processes=1).get_coherence()
    real = cv([w for _, w in tops])
    random.seed(0)
    vocab = [w for w, c in collections.Counter(x for doc in docs for x in doc).items() if c >= 2]
    rand = sum(cv([random.sample(vocab, 5) for _ in tops]) for _ in range(5)) / 5
    outliers = sum(1 for c in d["cases"] if c["topic_id"] is None)
    out = [f"cases {len(d['cases'])}, topics {len(d['topics'])}, outliers {outliers} ({outliers / len(d['cases']):.0%})",
           f"topics scored {len(tops)} of {len(d['topics'])}; c_v = {real:.3f}; random 5-word sets = {rand:.3f}",
           "departments: " + str(dict(collections.Counter((t.get("department_override") or t["department"]) for t in d["topics"])))]
    size = collections.Counter(c["topic_id"] for c in d["cases"] if c["topic_id"] is not None)
    for t, w in sorted(tops, key=lambda tw: -size[tw[0]["topic_id"]])[:10]:
        out.append(f"  {t['topic_name']:<40} {size[t['topic_id']]:>3} cases -> {t.get('department_override') or t['department']}  [{t['description']}]")
    text = "\n".join(out)
    print(text)
    open(os.path.join(HERE, "topic_coherence_results.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
