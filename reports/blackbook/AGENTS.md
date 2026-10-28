# AGENTS.md

Instructions for AI coding agents (and the humans driving them) working on this project.
Read this whole file before making any change.

## What this project is

A [Typst](https://typst.app) template for the **L.Y. major project report ("black book")** at
K.J. Somaiya Institute of Technology (University of Mumbai). It reproduces the project
coordinator's official black-book format, which was originally supplied as a Word document.

Students fill in `config.typ` and the files in `content/`; everything else is automatic.
The four sample chapters are a beginner's tutorial for Typst, written with the template itself.

**Who you are working for:** usually a student who may never have used Typst or written code.
Explain what you did in plain language, and tell them which page of the PDF to look at.

## Golden rules

1. **Don't change the formatting.** Everything in `template/`, and the page setup in
   `PRINT.typ` / `DIGITAL.typ` / `PRINT-SPINE.typ`, implements the college's rules. Only
   change it when the user explicitly asks. When they do:
   - say which college rule the change affects (see the table below);
   - render the affected page before and after, and show both;
   - change only what was asked.
2. **Personal and college details live only in `config.typ`.** Never hard-code a name, stream,
   year or college detail into `template/`.
3. **Student writing lives only in `content/`.** Keep its input formats simple; the template
   does the layout (for example, abbreviations are typed as `/ CNN: Convolutional Neural Network`).
4. **Respect the deliberate decisions** listed below. They differ from the coordinator's
   document on purpose; don't "fix" them unless asked.
5. **Never fabricate academic content.** Don't invent results, data, measurements, quotations,
   citations or BibTeX entries. Use only sources and numbers the student gives you, and mark
   anything left to fill in as an obvious placeholder. The report goes through a plagiarism check.
6. **Compile after every change** (all three outputs, see below) and fix every error and warning
   before reporting back.
7. **Ask before deleting** the student's files or text.

## Project map

```
PRINT.typ            ▶ printed, hard-bound book (35 mm binding margin, 50 mm top on chapter pages)
DIGITAL.typ          ▶ soft copy for the digital library (black & gold cover, 25 mm margins)
PRINT-SPINE.typ      ▶ spine strip: project title at the top end, "AI-DS 2026-27/Group-3" at the bottom end
config.typ           ✏️  ALL details: title, stream, students, guides, HOD, principal, college, chapter list
README.md, readme.typ   guides for humans (readme.typ is for typst.app users)
AGENTS.md            this file

content/             ✏️  what the student writes
  abstract.typ, acknowledgement.typ       body text only (headings and names are added by the template)
  co-po-mapping.typ                       CO-PO / PO / PSO pages (PSO table is AI&DS-specific)
  abbreviations.typ, symbols.typ          "/ term: meaning" lists; page skipped if empty below the CONTENT marker
  chapters/NN-name.typ                    one chapter per file; must also be listed in config.typ
  appendix.typ                            each "= Title" is one appendix (A1, A2, ...); optional
  publications.typ
  images/, data/                          figures; CSV files for tables
  references/books.bib, journals.bib      BibTeX; EVERY entry is printed in the Bibliography

template/            🔒 formatting rules
  body.typ                text style, headings, page numbers, header, equation/figure numbering,
                          contents & lists, chapters loop, bibliography, appendices
  outlines.typ            Contents / List of Figures / List of Tables tables; aligned-terms layout
  covers/                 title-page.typ (shared layout), print.typ, digital.typ
  front-matter/           title page, certificate, project approval, declaration, acknowledgement,
                          abstract wrappers; front-matter.typ sets their order
  utils.typ               gold gradient, academic-year(), student-name formatting, blank page
  ieee.csl                IEEE citation style ("et al." after the first author when 3+ authors)
  tutorial.typ            "YOU TYPE / YOU GET" boxes used only by the sample chapters
  fonts/                  Times New Roman: NOT in Git (licence); pass with --font-path when present
  logos/                  university and college logos (normal and gold)
```

### Order of the book (PRINT.typ)

Cover → 2 blank pages → front matter (title page, Certificate, Project Approval, Declaration,
Acknowledgement, Abstract, CO-PO mapping) → Contents, List of Abbreviations, List of Symbols,
List of Figures, List of Tables (roman page numbers from Contents = i) → chapters (arabic page
numbers, Chapter 1 = 1) → Bibliography → Appendices → Publications and Certificates → 2 blank pages.

## Build and verify

Tested with **Typst 0.15.1**. Packages (downloaded automatically on the first compile, needs
internet): `i-figured 0.2.4`, `alexandria 0.2.2`, and `fletcher 0.5.8` (used only by the tutorial).

Install the Typst CLI if it's missing: `winget install --id Typst.Typst` (Windows),
`brew install typst` (macOS), or `cargo install --locked typst-cli`. The Tinymist extension
for VS Code-based editors also previews and exports without the CLI.

Run every command **from the project root**. Paths that start with `/` (for example
`/content/images/x.png`) are resolved from the project root.

```bash
typst compile --font-path template/fonts PRINT.typ
typst compile --font-path template/fonts DIGITAL.typ
typst compile --font-path template/fonts PRINT-SPINE.typ
typst compile readme.typ                                  # stand-alone guide, built-in fonts
typst watch   --font-path template/fonts PRINT.typ        # recompile on every save
```

Always pass `--font-path template/fonts`: without it, machines without Times New Roman fall back to
another font and the layout changes.

The Times New Roman `.ttf` files are **not in the Git repository** (Microsoft/Monotype licence) and are
ignored in `.gitignore`. Never commit or download font files. Windows and macOS have the font
installed; elsewhere the user copies their own files into `template/fonts/` (see "Fonts" in
README.md). If the font is missing, Typst warns `unknown font family: times new roman`: tell the
user rather than switching fonts.

**A change is done when** all four commands above finish with no errors and no warnings.

Useful checks:

```bash
# Check images go in a folder NEXT TO the project, never inside it
mkdir -p ../bb-check/before ../bb-check/after

# Which page does each chapter start on?
typst eval 'query(heading.where(level: 1)).map(hd => (repr(hd.body), hd.location().page()))' --in PRINT.typ --font-path template/fonts

# Render one page to an image to look at it (page 19 here)
typst compile --font-path template/fonts PRINT.typ ../bb-check/page-{0p}.png --pages 19 --ppi 110

# Refactor without visible change: render every page before and after, then compare.
# Typst's PNG output is deterministic, so identical pages give identical files.
typst compile --font-path template/fonts PRINT.typ ../bb-check/before/p-{0p}.png --ppi 60
# ...make the change...
typst compile --font-path template/fonts PRINT.typ ../bb-check/after/p-{0p}.png --ppi 60
for f in ../bb-check/before/*.png; do cmp -s "$f" "../bb-check/after/$(basename "$f")" || echo "differs: $f"; done
```

`typst query` is deprecated in 0.15; use `typst eval '<expression>' --in FILE` instead.
Delete `../bb-check` when you are done.

## College formatting rules and where they live

| Rule                                         | Value                                                                                                                                                                              | Where                                                                             |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Paper                                        | A4, single column, printed on one side                                                                                                                                             | `PRINT.typ`, `DIGITAL.typ`                                                        |
| Margins (print)                              | left 35 mm, right 25 mm, top 30 mm, bottom 25 mm                                                                                                                                   | `PRINT.typ`                                                                       |
| Top margin on a chapter's first page (print) | 50 mm (30 mm + 20 mm `chapter-top-space`)                                                                                                                                          | `PRINT.typ` sets it; `body.typ` applies it to chapters only, not appendices       |
| Margins (digital)                            | 25 mm all round, no extra chapter space                                                                                                                                            | `DIGITAL.typ`                                                                     |
| Font                                         | Times New Roman everywhere                                                                                                                                                         | every file sets it; `.ttf` files in `template/fonts/` (not in Git)                |
| Body text                                    | 12 pt, justified, first-line indent 1 em in chapters                                                                                                                               | `body.typ`                                                                        |
| Line spacing                                 | Word "1.5 lines" → `leading: 1.063em`; paragraphs `spacing: 1.563em` (+6 pt)                                                                                                       | `body.typ`                                                                        |
| Display equations                            | Word "double" spacing around them → block `above`/`below: 1.638em`                                                                                                                 | `body.typ`                                                                        |
| Code blocks                                  | single-spaced (`leading: 0.65em`)                                                                                                                                                  | `body.typ`                                                                        |
| Chapter title                                | new page; "CHAPTER N" above the title; 14 pt bold capitals; centred                                                                                                                | `body.typ`, level-1 show rule                                                     |
| Section (`==`)                               | 12 pt bold CAPITALS, left; 2 em space above and below                                                                                                                              | `body.typ`                                                                        |
| Subsection (`===`)                           | 12 pt regular, sentence case                                                                                                                                                       | `body.typ`                                                                        |
| Paragraph heading (`====`)                   | 12 pt bold, sentence case                                                                                                                                                          | `body.typ`                                                                        |
| Page numbers                                 | bottom centre; roman from Contents (i); arabic from Chapter 1; Chapter 1's first page unnumbered                                                                                   | `body.typ`                                                                        |
| Page header                                  | from the 2nd page of each chapter: *Chapter N \| Title*, italic 10 pt, right-aligned, thin rule; none on a chapter's first page or in the front matter                             | `body.typ`, main-matter `set page(header: ...)`                                   |
| Figures                                      | numbered per chapter, caption below: "Figure 2.1: …"                                                                                                                               | `i-figured` in `body.typ`                                                         |
| Tables                                       | numbered per chapter, caption above: "Table 2.1: …"                                                                                                                                | `i-figured` in `body.typ`                                                         |
| Equations                                    | every display equation numbered per chapter, (3.1); references print "Eqn.(3.1)"                                                                                                   | `body.typ` (`show math.equation`, `show ref`)                                     |
| Appendices                                   | "APPENDIX A1" + title; sections A1.1; figures/tables A1.1; equations (A1.1); normal top margin                                                                                     | `body.typ`                                                                        |
| Contents                                     | ruled table: Chapter No. / Title / Page No., showing the printed page numbers                                                                                                      | `outlines.typ`                                                                    |
| List of Figures / Tables                     | Figure No / Title / Page No.; Table No. / Title / Page No.; only shown if there are figures/tables                                                                                 | `outlines.typ`, `body.typ`                                                        |
| Abbreviations / Symbols                      | aligned columns: term – meaning; symbols ordered Greek, then lower case, then upper case                                                                                           | `aligned-terms` in `outlines.typ`; applied in `body.typ`                          |
| Citations                                    | IEEE numbers [1] in the text                                                                                                                                                       | `body.typ`                                                                        |
| Bibliography                                 | headings "Books," and "Journal Papers,"; IEEE; first author + *et al.* when 3+ authors                                                                                             | `body.typ`, `template/ieee.csl` (`et-al-min="3"`)                                 |
| Blank sheets                                 | 2 after the cover and 2 at the end                                                                                                                                                 | `PRINT.typ`, `DIGITAL.typ`                                                        |
| Covers                                       | logos; title 22 pt; students one per line in 15 pt bold; digital cover black with gold lettering                                                                                   | `template/covers/` (shared layout in `title-page.typ`)                            |
| Certificate                                  | students separated by commas and "and"; guides side by side; HOD and Principal signatures                                                                                          | `template/front-matter/certificate.typ`                                           |
| Spine                                        | `Title` left-aligned (= top of the spine), auto-shrunk below 11 pt only if it wouldn't fit on one line; `Stream-Short academic-year/Group-N` right-aligned (= bottom of the spine) | `PRINT-SPINE.typ`; the year comes from the compile date (new year starts in July) |
| PDF properties (digital copy)                | title = `Title`; authors = all students in `dataset`, comma-separated; date = when the PDF is compiled                                                                             | `DIGITAL.typ`, `set document(...)`                                                |
| Abstract / Acknowledgement                   | 11 pt, justified; the student's text at Word "1.5 lines" (`leading: 1.063em`, `spacing: 1.563em`)                                                                                  | `front-matter/abstract.typ`, `acknowledgement.typ`                                |
| CO-PO tables                                 | 11 pt; PO table: 1st column Word single (`leading: 0.488em`), 2nd column exactly 12.45 pt (`leading: 5.17pt`), justified; Proof-required table: 2nd column justified               | `content/co-po-mapping.typ`                                                       |

### Deliberate decisions: don't change unless the user asks

- Captions stay "Figure 2.1: …" and "Table 2.1: …" (the coordinator's document prefers
  "Fig. 2.1 …" and no colon; the user chose to keep the current style).
- The Bibliography is grouped into Books and Journal Papers, numbered in that order, not in
  order of first citation.
- The Abstract, Acknowledgement and Declaration pages stay 11 pt (not the chapters' 12 pt).
  The Abstract and Acknowledgement text is justified with Word "1.5 lines" spacing; the
  Declaration keeps its own `leading: 22.5pt`.
- Justified text is hyphenated (Typst's default); the user chose to keep it.
- The sample Appendix A2 in `content/appendix.typ` starts directly with a table, on purpose
  (the user chose not to add a section). Appendices may do this; the fallback gap handles it.
- Contents and lists keep ruled table borders.
- The inner title page lists student names only (no roll numbers).

## Common tasks

**Fill in details:** edit `config.typ` only. `dataset` rows are `(Name, Roll No., Division, Exam Seat No.)`.
Set `Supervisor-2` to `""` when there is only one guide.

**Add a chapter:** create `content/chapters/05-name.typ`, starting with `= Title` and then
immediately a `== Section` (for example `== Introduction`). Add `"/content/chapters/05-name.typ"`
to `chapters` in `config.typ`, in reading order.

> ⚠️ **Never put text, a figure or a table directly under a chapter title.** Every chapter must
> begin with a `== Section`, as in the coordinator's sample ("1.1 Introduction"). If a student's
> chapter starts with a paragraph, move it under a new first section such as `== Introduction`
> and tell the student why. Don't add `#v(...)` spacing to fix the gap by hand.
>
> Safety net: if it happens anyway, the level-1 heading rule in `template/body.typ` detects that
> no `== Section` follows the title and adds the gap a section would have had (38 pt from the
> title, the same as a normal chapter), so the page still looks right. The numbering still
> skips the "N.1" introduction, which is why the rule above matters.

**Replace the tutorial:** remove the four sample chapters from `chapters` in `config.typ` (and
delete their files if the user agrees). Also replace the sample entries in `content/references/*.bib`
(every entry is printed), `abbreviations.typ`, `symbols.typ`, `appendix.typ`, `publications.typ`,
`abstract.typ` and `acknowledgement.typ`. `content/images/sample-figure.svg` and
`content/data/results.csv` are only used by the tutorial. `template/tutorial.typ` can stay.

**Figure:**
```typ
#figure(image("/content/images/arch.png", width: 80%), caption: [System architecture]) <arch>
As shown in @fig:arch, ...
```

**Table** (caption goes above automatically; a CSV can be loaded with `csv("/content/data/x.csv")`):
```typ
#figure(
  table(columns: 3, stroke: 0.5pt,
    table.header([*Model*], [*Accuracy*], [*Time*]),
    [CNN], [92.4%], [120 s],
  ),
  caption: [Comparison of models],
) <model-comparison>
See @tbl:model-comparison.
```

**Equation:** `$ E = m c^2 $ <energy>` then `@eqt:energy` (prints "Eqn.(3.1)"). Label `<->` to leave
one unnumbered.

**Code listing:** a fenced code block inside `#figure(..., caption: [...]) <name>`; cite with `@lst:name`.

**Citation:** add the BibTeX entry to `books.bib` (books) or `journals.bib` (everything else), then
write `@key` in the text.

**Abbreviation / symbol:** one line each in `content/abbreviations.typ` / `content/symbols.typ`:
`/ CNN: Convolutional Neural Network` or `/ $V_"pp"$: Voltage corresponding to peak power`.
Don't type a separator; the template adds the dash.

**Appendix:** each `= Title` in `content/appendix.typ` starts a new appendix (A1, A2, …).

**Student from another department:** set `Stream` and `Stream-Short` in `config.typ`, and replace the
PSO table at the end of `content/co-po-mapping.typ`.

**Diagrams in code:** import a package at the top of the chapter that uses it, e.g.
`#import "@preview/fletcher:0.5.8": diagram, node, edge`.

## Typst pitfalls in this project

- **A line starting with `= ` is a heading, even inside a list item** (for example `/ q: = charge`).
  A chapter heading in the wrong place then fails with "pagebreaks are not allowed inside of
  containers" or warns "pagebreak may not occur inside of a paragraph". Escape it as `\=`.
- **Labels need the i-figured prefix.** The template renames figure labels: `<x>` on an image is cited
  as `@fig:x`, on a table `@tbl:x`, on code `@lst:x`, on an equation `@eqt:x`. A plain `@x` fails
  with "label does not exist". Headings are cited without a prefix, and only print the number,
  so write "Section @x".
- **Chapters must start with a `== Section`.** Text, figures or tables placed directly under
  `= Title` break the college's numbering scheme (1.1, 1.2 …). The template's fallback gap
  keeps the spacing right, but see the warning under "Add a chapter". Keep the fallback in the
  level-1 heading rule: a chapter that starts with a section must stay pixel-identical.
- **Labels must be unique across the whole book.** While the tutorial chapters are still listed in
  `config.typ`, these labels are taken: `logo`, `models`, `pipeline`, `accuracy-code`, `sections`,
  `sigmoid`. A duplicate fails with "label `<…>` occurs multiple times in the document".
- **Don't shadow built-in functions** with variable names such as `v`, `h`, `text`, `table`
  (error: "expected function, found …").
- **The level-1 heading show rule replaces the heading element**, so a global
  `show heading: i-figured.reset-counters` never sees chapter headings. The counter reset is called
  inside that rule; keep it there, or figure/table/equation numbers stop restarting per chapter.
- **Maths:** letters written together are one name (`$xy$` → "unknown variable"; write `$x y$`);
  `*` prints an asterisk (use `dot` or `times`); in Typst 0.15 the intersection symbol is `inter`
  (not `sect`); use `overline(x)` for x̄.
- **Set and show rules inside an included file only affect that file.** Book-wide style belongs in
  `template/body.typ`; the front-matter pages are styled by their own files in `template/front-matter/`.
- **The tutorial's `example()` box evaluates its code for real**, so figures and equations inside it
  are numbered and listed like any other.
- **`#v(...)` and `#pagebreak()` are rarely needed:** chapters, appendices and the back matter
  start new pages on their own.

## Line spacing calibration (only if the font or size changes)

The spacing values were measured against Microsoft Word's own output for Times New Roman 12 pt:
Word's line pitch is 13.80 pt single, 20.70 pt at "1.5 lines", 27.60 pt double (1.15×, 1.725× and
2.3× the font size). Typst's line pitch is `leading` + the font's cap height (0.662 em for Times New
Roman). Therefore:

- 1.5 lines: `leading = 1.725em − 0.662em = 1.063em`
- double:   `leading = 2.3em − 0.662em = 1.638em`

With a different font, re-measure the cap height before changing these values.

## Working with the user

- They may not know Typst: explain changes simply and point to the page of the PDF that changed.
- For any visible formatting change: show before/after renders and get confirmation first.
- Before a large change, copy the whole project folder as a backup.
- Report which files you changed, and confirm that all outputs compile without warnings.
