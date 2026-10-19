"""Build the IEEE-style two-column Word version of the paper from the doc's XML (paper.xml).

Figures are the doc's own renders (img/fig*.png); equations are rendered with matplotlib mathtext.
  python build_docx.py   ->  InsightDesk_paper.docx
"""
import html
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

FONT = "Times New Roman"
COL_W = Inches(3.45)

FIGS = {"04f74690-b065": "img/fig1.png", "744a1564-8c9e": "img/fig2.png", "99700ab1-d770": "img/fig3.png",
        "20ff9b7c-e968": "img/fig4.png", "0e9a5709-bc0f": "img/fig5.png", "47fef0a8-e40a": "img/fig6.png"}

EQS = {
    "6d855770-35fa": r"$\max_{m' \in E_C}\, s(m, m') < 0.85, \qquad |E_C| \leq 5$",
    "cdd1f3c2-8d59": r"$S(x, C) = \max_{m \in E_C}\, s(x, m), \qquad \mathcal{C}_5(x) = \mathrm{top\text{-}5\ cases\ of\ product}(x)$",
    "cce56546-8ef6": [r"$d(x) = \mathrm{join}\ C^*$  if  $S^* \geq t_{high}$",
                      r"$d(x) = J(x, \mathcal{C}_5(x))$  if  $t_{low} \leq S^* < t_{high}$",
                      r"$d(x) = \mathrm{new\ case}$  if  $S^* < t_{low}$"],
    "6ea6c34b-d4df": [r"$\mathrm{Prec}(t) = \dfrac{|\{(i,j): s_{ij} \geq t,\ y_i = y_j\}|}{|\{(i,j): s_{ij} \geq t\}|}$",
                      r"$t_{high} = \min\{\, t : \mathrm{Prec}(t) \geq 0.97 \,\}$"],
    "11929ef3-3264": r"$t_{low} = Q_{0.20}\left(\{\, s_{ij} : y_i = y_j \,\}\right)$",
    "7e2cc8fd-fc63": [r"$t_{low}(x) = 0.40$  if channel$(x) \in$ {app review, chat}",
                      r"$t_{low}(x) = 0.26$  otherwise (tickets, bug reports, web form)"],
    "848a816a-2569": r"$\sigma(A, B) = \max_{a \in A,\ b \in B}\, s(a, b) \geq t_{low}$",
    "6946f64f-abf6": r"$\lambda_{u,t} = \dfrac{\sum_{\tau=t-L}^{t-1} c_{u,\tau} + a}{n_{u,t} + b}, \quad L = 28,\ a = 0.5,\ b = 7$",
    "855df979-22ad": [r"$S_{u,t} = \max(0,\ S_{u,t-1} + c_{u,t} - k_{u,t}), \quad k_{u,t} = \dfrac{\delta}{\ln((\lambda_{u,t} + \delta)/\lambda_{u,t})}$",
                      r"spike if $S_{u,t} \geq h, \quad \delta = 1,\ h = 2$"],
    "d24f008c-2910": r"$\mathrm{alarm}(p,t) \Leftrightarrow v_{p,t} \geq 2 \ \wedge\ P(X \geq v_{p,t}) < 0.001,\quad X \sim \mathrm{Poisson}(\lambda_{p,t})$",
    "37b683ec-8442": r"$\mathrm{eligible}(C) \Leftrightarrow \neg\mathrm{vague}(C) \wedge (n_C \geq 3 \vee \mathrm{alert}(C) \vee \mathrm{alert}(\mathrm{group}(C)))$",
}


def render_eq(ref, n):
    lines = EQS[ref] if isinstance(EQS[ref], list) else [EQS[ref]]
    plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
    fig = plt.figure(figsize=(6, 0.42 * len(lines) + (0.25 if any("dfrac" in l for l in lines) else 0)), dpi=300)
    for k, line in enumerate(lines):
        fig.text(0.02, 1 - (k + 0.5) / len(lines), line, fontsize=13, va="center")
    path = f"img/eq{n}.png"
    fig.savefig(path, bbox_inches="tight", pad_inches=0.04, transparent=False, facecolor="white")
    plt.close(fig)
    return path


def text_of(xml):
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def add_runs(par, xml, size=10, italic_all=False):
    """Paragraph XML -> runs with bold/italic."""
    for m in re.finditer(r"<text[^>]*>(.*?)</text>", xml, re.S):
        inner = m.group(1)
        bold, ital = "<bold>" in inner, "<italic>" in inner
        r = par.add_run(text_of(inner))
        r.bold, r.italic = bold, ital or italic_all
        r.font.size, r.font.name = Pt(size), FONT
    if not re.search(r"<text", xml):
        r = par.add_run(text_of(xml))
        r.font.size, r.font.name = Pt(size), FONT


def set_cols(section, n):
    cols = section._sectPr.xpath("./w:cols")
    c = cols[0] if cols else OxmlElement("w:cols")
    c.set(qn("w:num"), str(n))
    c.set(qn("w:space"), "360")
    if not cols:
        section._sectPr.append(c)


def new_section(doc, ncols):
    s = doc.add_section(WD_SECTION.CONTINUOUS)
    set_cols(s, ncols)
    return s


def para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    return p


def blocks(xml):
    body = xml[xml.find(">") + 1:xml.rfind("</doc>")]
    depth, start, out = 0, 0, []
    for m in re.finditer(r"<(/?)([a-zA-Z]+)([^>]*?)(/?)>", body):
        close, tag, attrs, selfc = m.groups()
        if close:
            depth -= 1
        elif not selfc:
            depth += 1
        if depth == 0:
            out.append(body[start:m.end()])
            start = m.end()
    return out


def main():
    xml = open("paper.xml", encoding="utf-8").read()
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(0.7)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1)
    set_cols(sec, 1)

    bl = blocks(xml)
    eq_n, in_body = 0, False
    i = 0
    while i < len(bl):
        b = bl[i]
        tag = re.match(r"<(\w+)", b).group(1)
        head = re.search(r"heading='(\d)'", b[:120])
        t = text_of(b).strip()
        if t.startswith("Editor notes"):
            break
        if tag == "paragraph" and head and head.group(1) == "1":           # title
            p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 2)
            r = p.add_run(t)
            r.bold, r.font.size = True, Pt(20)
        elif not in_body and tag == "paragraph" and not head and not t.startswith(("Abstract", "Keywords")):
            p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 1)
            if t.startswith("Department"):
                dept, guide = t.split(" Under the guidance")
                r = p.add_run(dept.rstrip(". ")); r.italic = True; r.font.size = Pt(11)
                p2 = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 1)
                r = p2.add_run("Under the guidance" + guide.rstrip(".")); r.italic = True; r.font.size = Pt(10)
            else:
                add_runs(p, b, 11 if "Krushnam" in t else 10)
                for r in p.runs:
                    r.bold = False
            if t.startswith("Academic"):
                new_section(doc, 2)
                in_body = True
        elif t.startswith(("Abstract", "Keywords")):
            p = para(doc, after=6)
            add_runs(p, b, 9)
            for r in p.runs:
                r.bold = r.text.strip() in ("Abstract", "Keywords", "—")
                r.italic = True
        elif tag == "paragraph" and head and head.group(1) == "2":
            p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 4)
            p.paragraph_format.space_before = Pt(8)
            r = p.add_run(t if t.isupper() else t.upper())
            r.font.size = Pt(10)
            if t in ("REFERENCES",):
                pass
        elif tag == "paragraph" and head:                                     # subsection
            p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, 3)
            p.paragraph_format.space_before = Pt(4)
            r = p.add_run(t); r.italic = True; r.font.size = Pt(10)
        elif tag == "paragraph" and re.fullmatch(r"TABLE [IVX]+", t):         # table caption + table, full width
            cap = text_of(bl[i + 1]).strip()
            tbl = bl[i + 2]
            new_section(doc, 1)
            for line in (t, cap):
                p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 1)
                r = p.add_run(line); r.font.size = Pt(8)
            rows = re.findall(r"<row.*?</row>", tbl, re.S)
            cells = [re.findall(r"<cell.*?</cell>", r, re.S) for r in rows]
            table = doc.add_table(rows=len(rows), cols=len(cells[0]))
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, row in enumerate(cells):
                for ci, c in enumerate(row):
                    cp = table.cell(ri, ci).paragraphs[0]
                    r = cp.add_run(text_of(c).strip())
                    r.font.size, r.font.name, r.bold = Pt(7.5), FONT, ri == 0
            para(doc, after=2)
            new_section(doc, 2)
            i += 3
            continue
        elif tag == "list":
            ordered = "kind='ordered'" in b[:200]
            for k, li in enumerate(re.findall(r"<listItem.*?</listItem>", b, re.S), 1):
                p = para(doc, after=2)
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.first_line_indent = Inches(-0.2)
                pre = p.add_run(f"[{k}] " if ordered else "• ")
                pre.font.size = Pt(8 if ordered else 10)
                add_runs(p, li, 8 if ordered else 10)
        elif tag == "embed":
            ref = re.search(r"ref='node/([^']+)'", b).group(1)
            if ref in FIGS:
                p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, 6)
                p.add_run().add_picture(FIGS[ref], width=COL_W)
            elif ref in EQS:
                eq_n += 1
                tab = doc.add_table(rows=1, cols=2)
                tab.autofit = False
                c0, c1 = tab.rows[0].cells
                c0.width, c1.width = Inches(3.0), Inches(0.45)
                p0 = c0.paragraphs[0]
                p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
                img = render_eq(ref, eq_n)
                from PIL import Image
                wpx = Image.open(img).size[0]
                p0.add_run().add_picture(img, width=Inches(min(2.9, wpx / 300 * 0.85)))
                p1 = c1.paragraphs[0]
                p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                r = p1.add_run(f"({eq_n})"); r.font.size = Pt(10)
        elif tag == "paragraph" and t:
            p = para(doc)
            p.paragraph_format.first_line_indent = Inches(0.15)
            add_runs(p, b, 10)
        i += 1
    doc.save("InsightDesk_paper.docx")
    print("saved InsightDesk_paper.docx,", eq_n, "equations")


if __name__ == "__main__":
    main()
