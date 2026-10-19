"""Second pass: paper titles + recent work in the survey, research finding, objective 2, references."""
import re
from xml.sax.saxutils import escape

import build as b   # reuses helpers; build.py's top-level edits are guarded below

HEAD = ["Paper (venue, year)", "Method", "Parameters / thresholds", "Limitation", "Our improvement"]
ROWS = [
    ["“Release Planning of Mobile Apps Based on User Reviews” (CLAP) [1], ICSE 2016", "Review features + DBSCAN clustering", "eps 0.6 published; 0.75 tuned on our data", "Batch only; groups by shared words (F1 0.24 on our data)", "Online cases; LLM judge separates look-alike problems"],
    ["“Towards More Accurate Retrieval of Duplicate Bug Reports” (REP) [2], ASE 2011", "BM25F keyword retrieval + metadata", "k1 = 1.2, b = 0.75; top-k candidates", "Misses paraphrases; top-5 hit 0.43–0.44 vs our 0.46–0.56", "Semantic retrieval + LLM verification"],
    ["“Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” [3], EMNLP 2019", "Bi-encoder cosine similarity", "One cosine threshold per task", "One cut cannot be safe and inclusive (F1 ≈ 0.10)", "Two calibrated cuts: 0.26 and 0.8306"],
    ["“BERTopic: Neural Topic Modeling with a Class-Based TF-IDF Procedure” [4], 2022", "Embeddings + UMAP + HDBSCAN topics", "Library defaults (minimum topic size)", "Topics are themes, not problems (precision 0.16)", "Problem-level cases; topics only for routing"],
    ["“Cupid: Leveraging ChatGPT for More Accurate Duplicate Bug Report Detection” [5], 2023", "ChatGPT extracts essentials, then REP retrieval", "LLM on 40–60% of reports; Recall-Rate@10 0.60–0.65", "Ranking only; no cases, spikes or escalation", "Online cases with spike alerts and RCA"],
    ["“Entity Matching using Large Language Models” [6], EDBT 2025", "Zero-shot GPT-4 pair judge", "Prompt only; F1 89.6–98.4 on record pairs", "Judges every pair: cost grows with pairs", "Judge only in the calibrated band, at most 5 candidates"],
    ["“GPTrace: Effective Crash Deduplication Using LLM Embeddings” [7], ICSE 2026", "LLM embeddings + HDBSCAN clustering", "Density clustering over 300K crash reports", "Batch; stack traces only", "Online grouping of free-text complaints"],
    ["“Dial-In LLM: Human-Aligned LLM-in-the-loop Intent Clustering for Customer Service Dialogues” [8], EMNLP 2025", "LLM-in-the-loop intent clustering", "100k calls, 1,507 clusters; >95% agreement with humans", "Intents, not problems; batch", "Problem cases decided as complaints arrive"],
    ["“LLM-Guided Lifecycle-Aware Clustering of Multi-Turn Customer Support Conversations” [9], AACL 2025", "Incremental clustering; LLM splits degraded clusters", "Silhouette / Davies-Bouldin quality triggers", "No spike detection, RCA or escalation", "Full pipeline: spikes, RCA, approval"],
    ["“TickIt: Leveraging Large Language Models for Automated Ticket Escalation” [10], FSE 2025 (ByteDance)", "LLM escalation with category fine-tuning", "Predefined ticket categories", "Fixed category set; no spike detection", "Open-ended cases + CUSUM + vague alarm"],
    ["“Incident-aware Duplicate Ticket Aggregation for Cloud Systems” (iPACK) [11], ICSE 2023 (Microsoft)", "Links tickets to cloud incident alerts", "Requires monitoring alerts; F1 0.87–0.94", "Depends on telemetry", "Works from complaint text alone"],
    ["SentiSum anomaly detection [12], commercial, 2025", "Anomaly detection per tag", "z-score > 2 per tag", "Fails at 0–2 complaints per window (0% detected)", "Poisson CUSUM, h = 2 (76–91% detected)"],
]
b.COLS = [2050000, 1400000, 1600000, 1500000, 1600000]
b.HEAD = HEAD


def table_xml(old_tbl, rows, row_h):
    tcpr = re.search(r"<a:tcPr .*?</a:tcPr>", old_tbl, re.S).group(0)
    head = old_tbl[:old_tbl.find("<a:tblGrid>")]

    def cell(t, bold, sz):
        return (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
                f'<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>'
                f'<a:r><a:rPr{" b=\"1\"" if bold else ""} lang="en-US" sz="{sz}">{b.FONT}</a:rPr><a:t>{escape(t)}</a:t></a:r></a:p></a:txBody>{tcpr}</a:tc>')
    out = head + "<a:tblGrid>" + "".join(f'<a:gridCol w="{w}"/>' for w in b.COLS) + "</a:tblGrid>"
    out += '<a:tr h="280000">' + "".join(cell(h, True, 1000) for h in HEAD) + "</a:tr>"
    for r in rows:
        out += f'<a:tr h="{row_h}">' + "".join(cell(c, False, 900) for c in r) + "</a:tr>"
    return out + "</a:tbl>"


for k, n in enumerate((4, 16, 17)):
    s = b.rd(n)
    tbl = re.search(r"<a:tbl>.*?</a:tbl>", s, re.S).group(0)
    row_h = 640000 if k < 2 else 580000
    s = s.replace(tbl, table_xml(tbl, ROWS[4 * k:4 * k + 4], row_h))
    s = re.sub(r'(<p:graphicFrame>.*?<a:off x=")\d+(" y=")\d+("/><a:ext cx=")\d+(" cy=")\d+',
               rf'\g<1>497000\g<2>1500000\g<3>{sum(b.COLS)}\g<4>{280000 + 4 * row_h}', s, count=1, flags=re.S)
    if k == 2:
        finding = b.textbox(950, 497000, 4170000, sum(b.COLS), 620000, [b.plain(
            "Research finding: several systems group duplicate reports (CLAP, TickIt, iPACK, Dial-In LLM), but none we found in "
            "academic papers, industry blogs, products or patents combines online problem-level case merging of raw complaint text "
            "with per-case spike detection, root-cause explanation and human-approved escalation.", 1000, True, "l")])
        s = s.replace("</p:spTree>", finding + "</p:spTree>", 1)
    b.wr(n, s)

# objective 2
s = b.rd(5)
assert "Measure customer sentiment with two AI models." in s
s = s.replace("Measure customer sentiment with two AI models.", "Measure customer sentiment using the RoBERTa model.")
b.wr(5, s)

REFS = [
    "[1] L. Villarroel, G. Bavota, B. Russo, R. Oliveto, M. Di Penta, “Release planning of mobile apps based on user reviews,” ICSE, 2016.",
    "[2] C. Sun, D. Lo, S.-C. Khoo, J. Jiang, “Towards more accurate retrieval of duplicate bug reports,” ASE, 2011.",
    "[3] N. Reimers, I. Gurevych, “Sentence-BERT: Sentence embeddings using Siamese BERT-networks,” EMNLP, 2019.",
    "[4] M. Grootendorst, “BERTopic: Neural topic modeling with a class-based TF-IDF procedure,” arXiv:2203.05794, 2022.",
    "[5] T. Zhang, I. C. Irsan, F. Thung, D. Lo, “Cupid: Leveraging ChatGPT for more accurate duplicate bug report detection,” arXiv:2308.10022, 2023.",
    "[6] R. Peeters, A. Steiner, C. Bizer, “Entity matching using large language models,” EDBT, 2025.",
    "[7] “GPTrace: Effective crash deduplication using LLM embeddings,” ICSE, 2026 (arXiv:2512.01609).",
    "[8] M. Hong et al., “Dial-In LLM: Human-aligned LLM-in-the-loop intent clustering for customer service dialogues,” EMNLP, 2025.",
    "[9] P. Pattnayak et al., “LLM-guided lifecycle-aware clustering of multi-turn customer support conversations,” AACL, 2025.",
    "[10] F. Liu et al., “TickIt: Leveraging large language models for automated ticket escalation,” FSE, 2025.",
    "[11] “Incident-aware duplicate ticket aggregation for cloud systems (iPACK),” ICSE, 2023 (arXiv:2302.09520).",
    "[12] SentiSum, “What is anomaly detection?,” product documentation, help.sentisum.com, 2025.",
    "[13] G. S. Manku, A. Jain, A. Das Sarma, “Detecting near-duplicates for web crawling,” WWW, 2007.",
    "[14] A. Z. Broder, “On the resemblance and containment of documents,” Compression and Complexity of Sequences, 1997.",
    "[15] E. S. Page, “Continuous inspection schemes,” Biometrika, vol. 41, 1954 (CUSUM).",
]
for n, part in ((13, REFS[:8]), (14, REFS[8:])):
    s = b.rd(n)
    shp = [nm for nm in re.findall(r'name="([^"]+)"', s) if re.search(r"\[\d+\]", s[b.shape_block(s, nm)[0]:b.shape_block(s, nm)[1]])][0]
    s = b.set_paras(s, shp, [b.plain(r, 1050, False, "l", 400) for r in part])
    b.wr(n, s)
print("patched")
