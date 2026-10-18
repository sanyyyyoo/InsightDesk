"""Fill the template copy in unpacked/ with the final-pipeline content (string edits, no XML round-trip)."""
import os
import re
import shutil
from xml.sax.saxutils import escape

from PIL import Image

U = "unpacked/ppt"
EMU = 914400
FONT = ('<a:latin typeface="Times New Roman"/><a:ea typeface="Times New Roman"/>'
        '<a:cs typeface="Times New Roman"/><a:sym typeface="Times New Roman"/>')


def rd(n):
    return open(f"{U}/slides/slide{n}.xml", encoding="utf8").read()


def wr(n, s):
    open(f"{U}/slides/slide{n}.xml", "w", encoding="utf8").write(s)


def run(text, sz, bold=False):
    return (f'<a:r><a:rPr{" b=\"1\"" if bold else ""} lang="en-US" sz="{sz}"><a:solidFill><a:schemeClr val="dk1"/></a:solidFill>'
            f'{FONT}</a:rPr><a:t xml:space="preserve">{escape(text)}</a:t></a:r>')


def bullet(label, text, sz=1300, after=500):
    return (f'<a:p><a:pPr indent="-285750" lvl="0" marL="342900" rtl="0" algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="{after}"/></a:spcAft><a:buClr><a:schemeClr val="dk1"/></a:buClr><a:buSzPts val="{sz}"/>'
            f'<a:buFont typeface="Times New Roman"/><a:buChar char="●"/></a:pPr>'
            + (run(label, sz, True) if label else "") + run(text, sz) + '</a:p>')


def plain(text, sz=1300, bold=False, algn="just", after=0):
    return (f'<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="{algn}"><a:spcBef><a:spcPts val="0"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="{after}"/></a:spcAft><a:buNone/></a:pPr>{run(text, sz, bold)}</a:p>')


def shape_block(s, name):
    i = s.find(f'name="{name}"')
    a = s.rfind("<p:sp>", 0, i)
    return a, s.find("</p:sp>", i) + 7


def set_paras(s, name, paras):
    a, b = shape_block(s, name)
    blk = s[a:b]
    t0 = blk.find("<a:lstStyle/>") + len("<a:lstStyle/>")
    t1 = blk.find("</p:txBody>")
    return s[:a] + blk[:t0] + "".join(paras) + blk[t1:] + s[b:]


def set_title(s, old, new):
    assert s.count(f">{old}<") >= 1, old
    return s.replace(f">{old}<", f">{escape(new)}<", 1)


def textbox(sid, x, y, w, h, paras):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Results text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="t" bIns="45720" lIns="45720" '
            f'spcFirstLastPara="1" rIns="45720" wrap="square" tIns="45720"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            + "".join(paras) + '</p:txBody></p:sp>')


def place_picture(n, media_src, media_name, x, y, w):
    """Point the slide's content picture at a new image and size it to its aspect ratio."""
    shutil.copy(media_src, f"{U}/media/{media_name}")
    iw, ih = Image.open(media_src).size
    h = int(w * ih / iw)
    rels = f"{U}/slides/_rels/slide{n}.xml.rels"
    r = open(rels, encoding="utf8").read()
    s = rd(n)
    pics = re.findall(r"<p:pic>.*?</p:pic>", s, re.S)
    content = max(pics, key=lambda p: int(re.search(r'<a:off x="\d+" y="(\d+)"', p).group(1)))   # the lower picture, not the header logo
    rid = re.search(r'r:embed="(rId\d+)"', content).group(1)
    r = re.sub(rf'(Id="{rid}"[^>]*Target=")[^"]*(")', rf"\1../media/{media_name}\2", r)
    r = re.sub(rf'(Target=")[^"]*("[^>]*Id="{rid}")', rf"\1../media/{media_name}\2", r)
    open(rels, "w", encoding="utf8").write(r)
    new = re.sub(r'<a:off x="\d+" y="\d+"/><a:ext cx="\d+" cy="\d+"/>', f'<a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/>', content, count=1)
    wr(n, s.replace(content, new))
    return h


# ---------------------------------------------------------------- literature survey (3 slides)
HEAD = ["System (venue, year)", "Method", "Parameters / thresholds", "Limitation", "Our improvement"]
ROWS = [
    ["CLAP [1] (ICSE 2016)", "Review features + DBSCAN clustering", "eps 0.6 as published; 0.75 tuned on our data", "Batch only; groups by shared words (F1 0.24 on our data)", "Online cases; LLM judge separates look-alike problems"],
    ["REP / BM25 [2] (ASE 2011)", "BM25F keyword retrieval + metadata", "k1 = 1.2, b = 0.75; top-k candidates", "Misses paraphrases (“can't log in” vs “sign-in fails”)", "Semantic retrieval + LLM verification"],
    ["Sentence-BERT [3] (EMNLP 2019)", "Bi-encoder cosine similarity", "One cosine threshold per task", "One cut cannot be both safe and inclusive (F1 ≈ 0.10)", "Two calibrated cuts: 0.26 and 0.8306"],
    ["BERT cross-encoder [4] (NAACL 2019)", "Fine-tuned pair classifier", "Score cut 0.4834, tuned on 110 labelled pairs", "Pair scores do not hold in a live stream (P 0.38)", "Band calibrated on the stream + LLM judge (P 0.80)"],
    ["SimHash [5] (WWW 2007)", "64-bit fingerprints, Hamming distance", "Hamming distance k = 3 bits", "Detects near-copies only (F1 0.12)", "Matches meaning, not wording"],
    ["MinHash-LSH [6] (1997)", "Jaccard over shingles + banding", "Similarity cut 0.75 / 0.80 / 0.85", "Detects near-copies only (F1 0.20)", "Matches meaning, not wording"],
    ["BERTopic [7] (2022)", "Embeddings + UMAP + HDBSCAN topics", "Library defaults (minimum topic size)", "Topics are themes, not problems (P 0.16)", "Problem-level cases; topics used only for routing"],
    ["IDEA / MERIT [8, 9] (ICSE 2018, TSE 2022)", "Online topic models per app version", "Change in topic share between versions", "Per version; no problem cases", "Per-case grouping as each complaint arrives"],
    ["SentiSum [10] (commercial)", "Anomaly detection per tag", "z-score > 2 per tag", "Fails at 0–2 complaints per window (0% detected)", "Poisson CUSUM, h = 2 (76–91% detected)"],
    ["iPACK [11] (ICSE 2023)", "Links tickets to cloud incidents", "Requires cloud monitoring alerts", "Depends on telemetry", "Works from complaint text alone"],
    ["TickIt [12] (2025)", "LLM ticket grouping and escalation", "Predefined ticket categories", "Fixed category set", "Open-ended cases + vague-complaint alarm"],
    ["LLM RCA from logs [13] (2024)", "Mistral / Mixtral on log data", "Trained on labelled log data", "Needs labelled data", "Grounded RCA, no training, human approval"],
]
COLS = [1600000, 1500000, 1700000, 1650000, 1700000]          # 8.15 M EMU wide


def table_xml(old_tbl, rows):
    tcpr = re.search(r"<a:tcPr .*?</a:tcPr>", old_tbl, re.S).group(0).replace('marT="91425" marB="91425" marR="91425" marL="91425"',
                                                                          'marT="45720" marB="45720" marR="45720" marL="45720"')
    head = old_tbl[:old_tbl.find("<a:tblGrid>")]

    def cell(t, bold, sz):
        return (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
                f'<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>'
                f'<a:r><a:rPr{" b=\"1\"" if bold else ""} lang="en-US" sz="{sz}">{FONT}</a:rPr><a:t>{escape(t)}</a:t></a:r></a:p></a:txBody>{tcpr}</a:tc>')
    out = head + "<a:tblGrid>" + "".join(f'<a:gridCol w="{w}"/>' for w in COLS) + "</a:tblGrid>"
    out += '<a:tr h="300000">' + "".join(cell(h, True, 1050) for h in HEAD) + "</a:tr>"
    for r in rows:
        out += '<a:tr h="700000">' + "".join(cell(c, i == 0, 950) for i, c in enumerate(r)) + "</a:tr>"
    return out + "</a:tbl>"


for k, n in enumerate((4, 16, 17)):
    s = rd(n)
    tbl = re.search(r"<a:tbl>.*?</a:tbl>", s, re.S).group(0)
    s = s.replace(tbl, table_xml(tbl, ROWS[4 * k:4 * k + 4]))
    s = re.sub(r'(<p:graphicFrame>.*?<a:off x=")\d+(" y=")\d+("/><a:ext cx=")\d+(" cy=")\d+', rf'\g<1>497000\g<2>1530000\g<3>{sum(COLS)}\g<4>3100000', s, count=1, flags=re.S)
    s = set_title(s, "LITERATURE SURVEY", f"LITERATURE SURVEY ({k + 1}/3)")
    wr(n, s)

# ---------------------------------------------------------------- flowchart
place_picture(6, "img_flow.png", "flow_final.png", 560000, 1560000, 8020000)

# ---------------------------------------------------------------- implementation, with one running example
EX = "Running example: a customer writes “Can't log in since the update, the OTP never arrives”."
impl1 = [plain(EX, 1250, True, "l", 600),
         bullet("Intake & Cleaning:", " the signed-in customer submits through the React app; filler such as “Hi team, please help” is removed, while negations like “can't” are kept."),
         bullet("Embedding & Retrieval:", " MiniLM turns the text into a vector; Pinecone returns the 5 most similar cases of the same product, e.g. “OTP not received on login” (similarity 0.71)."),
         bullet("Decision Band:", " similarity ≥ 0.8306 joins automatically, < 0.26 opens a new case; our 0.71 falls in between, so the LLM judge decides."),
         bullet("LLM Judge:", " gpt-oss-120b compares the symptom: “OTP never arrives” = same problem, so the complaint joins that case (count +1); “login is slow” would open a new case."),
         bullet("Same-User Rule:", " if the same customer repeats this complaint within 24 hours, it is attached to the case but not counted again.")]
impl2 = [bullet("Case Re-joining (every 6 h):", " the LLM merges cases that report one problem, e.g. “no dark mode” and “needs dark mode” become one case."),
         bullet("Sentiment & Topics:", " RoBERTa labels the case negative; BERTopic places it under an Authentication topic, which carries the responsible department."),
         bullet("Spike Detection:", " a Poisson CUSUM watches each case and group of similar cases; 5 OTP complaints in 6 hours against a usual 0.1 raises a spike."),
         bullet("Vague-Complaint Alarm:", " a surge of “app not working” complaints that fit no case still raises a product-level alarm."),
         bullet("Root Cause & Escalation:", " with 3+ reports or a spike the case is eligible; the LLM writes a grounded root cause (cause, severity, action, evidence) and an operator approves the email to the department.")]
for n, paras, t in ((7, impl1, "IMPLEMENTATION (1/2)"), (8, impl2, "IMPLEMENTATION (2/2)")):
    s = rd(n)
    body = re.findall(r'name="(Google Shape;\d+;p\d+)"', s)
    target = [nm for nm in body if "IMPLEMENTATION" not in s[shape_block(s, nm)[0]:shape_block(s, nm)[1]]
              and "<a:buChar" in s[shape_block(s, nm)[0]:shape_block(s, nm)[1]]][0]
    s = set_paras(s, target, paras)
    s = set_title(s, "IMPLEMENTATION", t)
    wr(n, s)

# ---------------------------------------------------------------- results (3 slides): chart left, findings right
RES = [
    (9, "img_f1.png", "res_f1.png", "RESULTS: GROUPING QUALITY", [
        bullet("Precision 0.80", " on human-labelled Play Store reviews.", 1200),
        bullet("F1 0.46", " vs at most 0.25 for every competitor on the same data.", 1200),
        bullet("Firefox bug reports:", " F1 0.78 with thresholds unchanged.", 1200),
        bullet("At equal precision (0.80):", " 33% of duplicates found vs about 1% for BM25, MinHash and SimHash.", 1200)]),
    (18, "img_pr.png", "res_pr.png", "RESULTS: PRECISION VS RECALL", [
        bullet("Only InsightDesk", " keeps precision high while finding useful recall.", 1200),
        bullet("Topic models", " group themes, not problems (BERTopic precision 0.16).", 1200),
        bullet("Generalises:", " unseen apps case precision 0.92, unseen company 0.89.", 1200),
        bullet("Duplicate retrieval (top-5):", " 0.46–0.56 vs REP 0.43–0.44 on 233K bug reports.", 1200)]),
    (19, "img_spike.png", "res_spike.png", "RESULTS: INCIDENT DETECTION", [
        bullet("CUSUM:", " 76–91% of outbreaks detected on bug-report streams, under 1 false alarm per 100 windows.", 1200),
        bullet("z-score", " (used by feedback tools): 0% detected.", 1200),
        bullet("Vague alarm:", " 100% of vague-only outages with 10+ complaints.", 1200),
        bullet("End to end:", " 94% of incidents escalation-eligible within 12 h, 0 false alarms.", 1200)]),
]
for n, src, name, title, paras in RES:
    place_picture(n, src, name, 380000, 1640000, 5350000)
    s = rd(n)
    s = set_title(s, "RESULT", title)
    s = s.replace("</p:spTree>", textbox(900 + n, 5850000, 1600000, 3050000, 3150000, paras) + "</p:spTree>", 1)
    wr(n, s)

# ---------------------------------------------------------------- future scope, conclusion
s = rd(11)
fs = [nm for nm in re.findall(r'name="(Google Shape;\d+;p\d+)"', s) if "Docker" in s[shape_block(s, nm)[0]:shape_block(s, nm)[1]]][0]
s = set_paras(s, fs, [
    bullet("", "Package the app with Docker and deploy it on GCP or Azure (free tier).", 1500, 900),
    bullet("", "Host the open-weight LLM locally for full data privacy.", 1500, 900),
    bullet("", "Remove personal details from complaints before any LLM call.", 1500, 900),
    bullet("", "Learn from operator corrections to calibrate each company automatically.", 1500, 900),
    bullet("", "Per-user submission limits, multilingual complaints and automatic Jira tickets.", 1500, 900)])
wr(11, s)

s = rd(12)
cs = [nm for nm in re.findall(r'name="(Google Shape;\d+;p\d+)"', s) if "intelligent complaint" in s[shape_block(s, nm)[0]:shape_block(s, nm)[1]]][0]
s = set_paras(s, cs, [plain(
    "InsightDesk turns raw customer complaints into problem cases as they arrive. Similarity retrieval narrows each complaint to a few "
    "candidate cases, calibrated thresholds settle the clear ones, and an LLM judge decides the rest; a re-joining pass merges split cases. "
    "On real reviews it reaches precision 0.80 and the highest F1 of every method tested, and it transfers unchanged to bug reports. "
    "A Poisson CUSUM and a vague-complaint alarm detect incidents that the usual z-score misses, and every escalation is approved by a "
    "person before an email reaches the department.", 1500)])
wr(12, s)

# ---------------------------------------------------------------- references (2 slides)
REFS = [
    "[1] L. Villarroel, G. Bavota, B. Russo, R. Oliveto, M. Di Penta, “Release planning of mobile apps based on user reviews,” ICSE, 2016.",
    "[2] C. Sun, D. Lo, S.-C. Khoo, J. Jiang, “Towards more accurate retrieval of duplicate bug reports,” ASE, 2011.",
    "[3] N. Reimers, I. Gurevych, “Sentence-BERT: Sentence embeddings using Siamese BERT-networks,” EMNLP, 2019.",
    "[4] J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, “BERT: Pre-training of deep bidirectional transformers,” NAACL, 2019.",
    "[5] G. S. Manku, A. Jain, A. Das Sarma, “Detecting near-duplicates for web crawling,” WWW, 2007.",
    "[6] A. Z. Broder, “On the resemblance and containment of documents,” Compression and Complexity of Sequences, 1997.",
    "[7] M. Grootendorst, “BERTopic: Neural topic modeling with a class-based TF-IDF procedure,” arXiv:2203.05794, 2022.",
    "[8] C. Gao et al., “Online app review analysis for identifying emerging issues,” ICSE, 2018.",
    "[9] C. Gao et al., “Emerging app issue identification via online joint sentiment-topic tracing,” IEEE TSE, 2022.",
    "[10] SentiSum, “What is anomaly detection?,” product documentation, help.sentisum.com, 2025.",
    "[11] “iPACK: Incident-aware duplicate ticket aggregation for cloud systems,” ICSE, 2023.",
    "[12] “TickIt: Leveraging large language models for automated ticket escalation,” arXiv:2504.08475, 2025.",
    "[13] “Root cause prediction from log data using large language models,” Diva-Portal research report, 2024.",
    "[14] S. Lee, S. Lee, “Duplicate bug report detection by using sentence embedding and Faiss,” CEUR-WS vol. 3655, 2023.",
]
for n, part in ((13, REFS[:7]), (14, REFS[7:])):
    s = rd(n)
    shp = [nm for nm in re.findall(r'name="(Google Shape;\d+;p\d+)"', s)
           if re.search(r"\[\d\]|Author", s[shape_block(s, nm)[0]:shape_block(s, nm)[1]])][0]
    s = set_paras(s, shp, [plain(r, 1100, False, "l", 500) for r in part])
    s = s.replace(">[6] <", "><").replace(">[6]<", "><")
    wr(n, s)
print("done")
