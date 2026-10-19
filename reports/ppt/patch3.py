"""Third pass: formulation, calibration tables, datasets, sentiment/clustering, objectives."""
import re
from xml.sax.saxutils import escape

import build as b


def table(old_tbl, cols, head, rows, row_h, sz=900):
    tcpr = re.search(r"<a:tcPr .*?</a:tcPr>", old_tbl, re.S).group(0)
    pre = old_tbl[:old_tbl.find("<a:tblGrid>")]

    def cell(t, bold, s):
        return (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
                f'<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr>'
                f'<a:r><a:rPr{" b=\"1\"" if bold else ""} lang="en-US" sz="{s}">{b.FONT}</a:rPr><a:t>{escape(t)}</a:t></a:r></a:p></a:txBody>{tcpr}</a:tc>')
    out = pre + "<a:tblGrid>" + "".join(f'<a:gridCol w="{w}"/>' for w in cols) + "</a:tblGrid>"
    out += '<a:tr h="280000">' + "".join(cell(h, True, sz + 100) for h in head) + "</a:tr>"
    for r in rows:
        bold_row = r[0].endswith("(deployed)")
        out += f'<a:tr h="{row_h}">' + "".join(cell(c, bold_row, sz) for c in r) + "</a:tr>"
    return out + "</a:tbl>"


def table_slide(n, title, cols, head, rows, row_h, note=None, sz=900):
    s = b.rd(n)
    tbl = re.search(r"<a:tbl>.*?</a:tbl>", s, re.S).group(0)
    s = s.replace(tbl, table(tbl, cols, head, rows, row_h, sz))
    s = re.sub(r'(<p:graphicFrame>.*?<a:off x=")\d+(" y=")\d+("/><a:ext cx=")\d+(" cy=")\d+',
               rf'\g<1>497000\g<2>1500000\g<3>{sum(cols)}\g<4>{280000 + len(rows) * row_h}', s, count=1, flags=re.S)
    s = re.sub(r">LITERATURE SURVEY \(\d/3\)<", f">{escape(title)}<", s, count=1)
    s = s.replace('name="Results text 950"', 'name="old note"')
    s = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="950" name="old note".*?</p:sp>', "", s, flags=re.S)
    if note:
        y = 1500000 + 280000 + len(rows) * row_h + 60000
        s = s.replace("</p:spTree>", b.textbox(960, 497000, y, sum(cols), 4780000 - y, [b.plain(note, 1000, False, "l")]) + "</p:spTree>", 1)
    b.wr(n, s)


def body_slide(n, title, paras):
    s = b.rd(n)
    target = [nm for nm in re.findall(r'name="(Google Shape;\d+;p\d+)"', s)
              if "<a:buChar" in s[b.shape_block(s, nm)[0]:b.shape_block(s, nm)[1]]][0]
    s = b.set_paras(s, target, paras)
    s = re.sub(r">IMPLEMENTATION \(2/2\)<", f">{escape(title)}<", s, count=1)
    b.wr(n, s)


def main():
    # ------------------------------------------------ mathematical formulation
    body_slide(20, "MATHEMATICAL FORMULATION", [
        b.bullet("Retrieval:", " e(x) = MiniLM(x) ∈ ℝ³⁸⁴ with ‖e‖ = 1;  S(x, C) = max over exemplars m ∈ E_C of e(x)·e(m);  keep the top 5 cases of the same product.", 1200, 350),
        b.bullet("Decision band:", " join automatically if S* ≥ t_high; open a new case if S* < t_low; otherwise the LLM judge decides.", 1200, 350),
        b.bullet("Upper threshold:", " t_high = min{ t : Prec(t) ≥ 0.97 }, Prec(t) = share of true duplicates among tuning pairs with similarity ≥ t  →  0.8306.", 1200, 350),
        b.bullet("Lower threshold:", " t_low = 20th percentile of similarities of true duplicate pairs  →  0.26 (80% of duplicates stay reachable).", 1200, 350),
        b.bullet("Spike CUSUM:", " λ = (Σ last 28 windows + 0.5) / (n + 7);  k = 1 / ln((λ + 1)/λ);  S = max(0, S + c − k);  alert when S ≥ 2.", 1200, 350),
        b.bullet("Vague alarm:", " alert when v ≥ 2 and P(X ≥ v) < 0.001 with X ~ Poisson(λ).", 1200, 350),
    ])

    # ------------------------------------------------ threshold calibration and sensitivity
    table_slide(21, "THRESHOLD CALIBRATION & SENSITIVITY",
                [2350000, 1450000, 1450000, 850000, 750000, 650000, 650000],
                ["Setting", "t_low", "t_high", "Precision", "Recall", "F1", "Note"],
                [["Calibrated on tuning half (deployed)", "20th percentile of duplicates", "precision ≥ 0.97", "0.810", "0.259", "0.392", "exact"],
                 ["t_high lowered by 0.03", "same", "− 0.03", "0.831", "0.233", "0.364", "robust"],
                 ["t_high lowered by 0.08", "same", "− 0.08", "0.808", "0.277", "0.413", "robust"],
                 ["t_high lowered by 0.13", "same", "− 0.13", "0.722", "0.246", "0.367", "P falls"],
                 ["Single cosine threshold, no judge", "one cut", "one cut", "–", "–", "≈ 0.10", "fails"],
                 ["BM25 / MinHash forced to precision 0.80", "–", "–", "≈ 0.80", "0.01", "–", "fails"]],
                420000,
                "Play Store held-out halves pooled. Final values calibrated on all Play Store data (t_low 0.26, t_high 0.8306) are reused "
                "unchanged on Firefox, Thunderbird and unseen apps (precision 0.87–0.96). Raising t_low changes which complaints reach "
                "the judge, so those cells need new LLM calls and are not shown.")

    # ------------------------------------------------ spike detector calibration
    table_slide(22, "SPIKE DETECTOR CALIBRATION",
                [2000000, 1450000, 1150000, 1150000, 1200000, 1200000],
                ["Detector", "Setting", "Play Store detected", "Play Store false / 100 windows", "Bug reports detected", "Bug reports false / 100 windows"],
                [["Poisson CUSUM (deployed)", "δ = 1, h = 2", "42%", "0.06", "76%", "0.38"],
                 ["Poisson CUSUM", "δ = 1, h = 1.5", "56%", "0.78", "86%", "3.81"],
                 ["Poisson CUSUM", "δ = 1, h = 3", "25%", "0.00", "50%", "0.01"],
                 ["Poisson CUSUM", "δ = 0.5, h = 2", "45%", "0.22", "78%", "1.04"],
                 ["Poisson CUSUM", "δ = 2, h = 2", "33%", "0.02", "67%", "0.10"],
                 ["EWMA", "α = 0.2, L = 3", "55%", "0.67", "86%", "3.19"],
                 ["Poisson tail test", "c ≥ 2, p < 0.001", "43%", "0.27", "71%", "1.20"],
                 ["z-score (feedback tools)", "z > 2", "0%", "–", "0%", "–"]],
                330000,
                "300 simulated outbreaks per dataset, case level. h = 2 is the knee: lower h buys little detection for many more false "
                "alarms. EWMA reaches CUSUM's detection only at about 9× its false alarms on bug reports.")

    # ------------------------------------------------ datasets and credibility
    table_slide(23, "TEST DATASETS & LABEL CREDIBILITY",
                [1800000, 1100000, 1600000, 2150000, 1500000],
                ["Dataset", "Size", "Ground truth", "Credibility", "Used for"],
                [["Play Store reviews (6 help-desk apps)", "338 labelled of 450", "3 team annotators, written codebook", "Fleiss κ = 0.74 across all 3; LLM labellers agree with humans at κ 0.68–0.70", "Tuning and held-out evaluation"],
                 ["Firefox and Thunderbird (Bugzilla)", "437 + 452 reports", "Mozilla triagers' duplicate links", "Independent of us; some duplicates unlinked, so precision is conservative", "Transfer test"],
                 ["BugHub split: Firefox, Thunderbird, Eclipse", "233,521 reports", "Public duplicate links", "Standard public benchmark", "Duplicate retrieval (top-5)"],
                 ["Unseen apps: Intercom, Jira SM, ServiceNow", "588 reviews", "Agreed key of 2 LLM labellers", "κ 0.38 between LLMs; 50-pair human check pending", "Secondary transfer test"],
                 ["Endava IT tickets", "1,000 tickets", "Ticket categories", "Case precision 0.90 vs 0.66 (cross-encoder); F1 tied", "Third domain"],
                 ["Synthetic complaints", "488", "Generator ground truth", "Sanity check only", "Never a headline result"]],
                450000, None, 880)

    # ------------------------------------------------ sentiment and clustering
    body_slide(24, "SENTIMENT & TOPIC CLUSTERING", [
        b.bullet("Sentiment model:", " RoBERTa (cardiffnlp twitter-roberta-base-sentiment-latest), 3 classes (negative, neutral, positive) with a confidence per case.", 1200, 350),
        b.bullet("How it was evaluated:", " on real Play Store reviews against star ratings (1–2 negative, 3 neutral, 4–5 positive): accuracy 0.707; negative complaints precision 0.81, recall 0.85.", 1200, 350),
        b.bullet("Why RoBERTa:", " DistilBERT reached accuracy 0.713 but is binary and cannot say neutral; RoBERTa is more precise on negatives (0.81 vs 0.77).", 1200, 350),
        b.bullet("Topic clustering:", " BERTopic over case texts: UMAP (12 neighbours, 5 dimensions, cosine), then HDBSCAN (minimum cluster size 3, minimum samples 1), keywords from 1–2-word c-TF-IDF.", 1200, 350),
        b.bullet("Result:", " 319 staging cases formed 49 topics with 11.9% outliers; each topic's keywords map to a department (Authentication, Engineering, Customer Success) that receives escalations.", 1200, 350),
        b.bullet("Upkeep:", " re-clustered automatically every 6 hours when cases grow by 20% or outliers exceed 15%.", 1200, 350),
    ])

    # ------------------------------------------------ objectives updated to the final pipeline
    s = b.rd(5)
    old = re.findall(r"<a:t>([^<]*)</a:t>", s)
    objs = [t for t in old if len(t) > 30]
    new = ["Group duplicate complaints into problem-level cases as they arrive, using similarity retrieval and an LLM judge for uncertain matches.",
           "Measure customer sentiment using the RoBERTa model.",
           "Find complaint topics automatically with BERTopic and route each to the responsible department.",
           "Detect sudden spikes with a Poisson CUSUM and raise an alarm on surges of vague complaints.",
           "Explain the root cause with an LLM, with a human approving every escalation."]
    assert len(objs) == 5, objs
    for o, n_ in zip(objs, new):
        s = s.replace(f"<a:t>{o}</a:t>", f"<a:t>{escape(n_)}</a:t>", 1)
    b.wr(5, s)
    print("patched")


if __name__ == "__main__":
    main()
