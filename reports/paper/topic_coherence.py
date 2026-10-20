import json, re, random, collections
from gensim.corpora import Dictionary
from gensim.models.coherencemodel import CoherenceModel


def main():
    d = json.load(open("topics.json", encoding="utf-8"))
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
    print(f"topics scored {len(tops)} of {len(d['topics'])}; c_v = {real:.3f}; random 5-word sets = {rand:.3f}")
    size = collections.Counter(c["topic_id"] for c in d["cases"] if c["topic_id"] is not None)
    print("departments:", dict(collections.Counter((t.get("department_override") or t["department"]) for t in d["topics"])))
    for t, w in sorted(tops, key=lambda tw: -size[tw[0]["topic_id"]])[:10]:
        print(f"  {t['topic_name']:<35} {size[t['topic_id']]:>3} cases -> {t.get('department_override') or t['department']}  [{t['description']}]")


if __name__ == "__main__":
    main()
