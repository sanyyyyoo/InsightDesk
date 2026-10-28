// ============================================================================
//  READ ME, for typst.app users. Click this file to read it in the preview.
//  It is a stand-alone guide: nothing here changes the black book itself.
// ============================================================================

#set document(title: "Black Book Template: Read Me")
#set page(paper: "a4", margin: (x: 20mm, y: 18mm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)

#let accent = rgb("#1f4e8c")
#show heading.where(level: 1): set text(size: 22pt, fill: accent)
#show heading.where(level: 2): it => {
  v(0.6em)
  text(fill: accent, it)
  v(0.2em)
}
#show raw.where(block: true): block.with(fill: luma(244), inset: 9pt, radius: 3pt, width: 100%, breakable: false)
#show raw.where(block: false): box.with(fill: luma(238), inset: (x: 3pt), outset: (y: 3pt), radius: 2pt)
#show link: underline

#let note(title: "Note:", body) = block(
  width: 100%,
  fill: rgb("#eef4fb"),
  stroke: (left: 3pt + accent),
  inset: (x: 11pt, y: 9pt),
  [*#title* #body],
)

#let simple-table(..cells) = table(
  columns: (auto, 1fr),
  stroke: 0.5pt + luma(170),
  inset: 6pt,
  ..cells,
)

= Black Book Template

A ready-made Typst template for the L.Y. major project report (black book). You fill in *your details* and *your content*; the template already follows the college's formatting rules (margins, fonts, 1.5 line spacing, numbering, contents page, lists of figures and tables, page numbers and headers).

#note(title: "New to Typst?")[Compile `PRINT.typ` and read *Chapters 1–4* of the PDF. They are a step-by-step tutorial written with the template itself: every example shows the code you type and the result it produces. Keep the matching file from `content/chapters/` open next to the preview.]

#note(title: "Prefer an AI code editor?")[Cursor, VS Code with GitHub Copilot, Claude Code, Codex and similar tools can edit and compile this project for you. The included `AGENTS.md` tells them the rules. See section 9.]

== 1. Put the template on typst.app

+ Sign in at #link("https://typst.app")[typst.app] and create a new *empty* project.
+ Drag *all* the files and folders of this template into the *Files* panel on the left (or use its upload button). Keep the folders exactly as they are.
+ Make `PRINT.typ` the project's *main file* (from the menu next to it in the Files panel). The preview on the right always shows the main file.
+ Edit, and the preview updates as you type. When you are done, use the *download* button above the preview to export the PDF.

You don't need to install anything. The Times New Roman font files in `template/fonts/` are picked up automatically, and the Typst packages the template uses are downloaded for you. (If you start from the GitHub repo instead, the font files aren't included because of their licence: upload `times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf` from a Windows PC's `C:\Windows\Fonts` into the project.)

== 2. The three files you compile

#simple-table(
  [`PRINT.typ`], [The *hard-bound* copy: white cover page, 35 mm binding margin on the left, extra space above each chapter title.],
  [`DIGITAL.typ`], [The *soft copy* for the department's digital library: black and gold cover, 25 mm margins.],
  [`PRINT-SPINE.typ`], [The text strip for the book's *spine*: your project title at the top (shrunk automatically if it is too long for one line) and, for example, `AI-DS 2026-27/Group-3` at the bottom.],
)

To export the digital copy or the spine, make that file the main file instead, then download.

== 3. Fill in your details: `config.typ`

Everything printed on the covers, certificate, approval page and spine comes from this one file:

#simple-table(
  [`Title`], [Project title.],
  [`Stream`, `Stream-Short`], [Your branch in full, and its short form for the spine (e.g. `AI-DS`).],
  [`Group-Number`], [Your project group number.],
  [`dataset`], [One line per student: name, roll number, division, exam seat number.],
  [`Supervisor-1`, `Supervisor-2`], [Guide names, designations and departments. Set `Supervisor-2` to `""` if you have only one guide.],
  [`HOD-name`, `Principal-name`], [Names for the certificate signatures.],
  [`College-Name`, `College-Address`, `Year`], [Printed at the bottom of the covers.],
  [`chapters`], [The list of your chapter files, in order (see section 5).],
)

== 4. Write your content: `content/`

```
content/
├── abstract.typ          one page, around 500 words
├── acknowledgement.typ
├── co-po-mapping.typ     fill in the mapping levels
├── abbreviations.typ     page disappears if left empty
├── symbols.typ           page disappears if left empty
├── chapters/             one file per chapter (the 4 samples are the tutorial)
├── appendix.typ          optional
├── publications.typ
├── images/               your figures and screenshots
├── data/                 CSV files for tables (optional)
└── references/           books.bib and journals.bib
```

*Don't edit `template/`.* It holds the formatting rules, so changing it can break the college format.

== 5. Quick reference

The tutorial chapters explain all of these in detail.

=== Add a chapter

Create a file in `content/chapters/`, start it with the chapter title and a first section, then add its path to `chapters` in `config.typ`:

```typ
= Results and Discussion

== Introduction

Your text ...
```

```typ
#let chapters = (
  "/content/chapters/01-introduction.typ",
  "/content/chapters/02-results.typ",
)
```

Chapter numbers, the "CHAPTER N" title, the new page, the page header and the Contents entry are all automatic.

=== Figures and tables

Upload the image into `content/images/`, then:

```typ
#figure(
  image("/content/images/architecture.png", width: 80%),
  caption: [System architecture],
) <arch>

As shown in @fig:arch, ...
```

Figures and tables are numbered by chapter (Figure 2.1, Table 2.1) and listed at the front of the book automatically. References need a prefix: `@fig:` for images, `@tbl:` for tables, `@lst:` for code and `@eqt:` for equations. The label itself is written without the prefix.

=== Equations

Every display equation is numbered by chapter, like (3.1), and a reference prints as "Eqn.(3.1)":

```typ
$ sigma(z) = 1 / (1 + e^(-z)) $ <activation>

The sigmoid in @eqt:activation ...
```

Label an equation `<->` to leave it unnumbered.

=== Citations

Copy the BibTeX of a paper or book (Google Scholar → *Cite* → *BibTeX*) into `content/references/journals.bib` or `books.bib`, then cite it with `@key`, which prints as [1]. Entries with 3 or more authors show the first author followed by _et al._ (see section 8).

=== Abbreviations and symbols

One entry per line; the template lines them up and adds the dash:

```typ
/ CNN: Convolutional Neural Network
/ $V_"pp"$: Voltage corresponding to peak power
```

List symbols with Greek letters first, then English letters (lower case before upper case), each group in alphabetical order.

=== Appendices

Each `= Title` in `content/appendix.typ` starts a new appendix, numbered A1, A2, … (sections A1.1, figures A1.1, equations (A1.1)). Delete everything in that file if you don't need appendices.

== 6. Not from AI&DS?

- In `config.typ`, set `Stream` and `Stream-Short` to your branch.
- In `content/co-po-mapping.typ`, the *PSO table* at the bottom is written for AI&DS, so replace it with your department's PSOs.

== 7. If something goes wrong

Typst shows the error, and the line it is on, under the editor. The most common ones:

#simple-table(
  [`unknown variable`], [In maths, letters written together are read as one name. Write `x y` with a space, or put words in quotes: `"loss"`.],
  [`label does not exist`], [A reference like `@fig:abc` doesn't match any label. Check the spelling and the prefix. In normal text, write an email address as `name\@gmail.com`.],
  [`file not found`], [Wrong image path. Paths start with `/content/images/` and must match the file name exactly, including capital letters and the extension.],
  [`unclosed delimiter`], [A missing `]`, `)` or `}` on the line shown.],
  [Text suddenly bold or italic], [An unclosed `*` or `_`. Close it, or write `\*` / `\_` to print the character itself.],
)

== 8. How the "et al." rule works

College rule: with more than 2 authors, list the first author followed by "et al."

#table(
  columns: (auto, 1fr, auto),
  stroke: 0.5pt + luma(170),
  inset: 6pt,
  table.header([*Authors*], [*Typst's built-in IEEE style*], [*This template*]),
  [4], [T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein], [T. H. Cormen _et al._],
  [3], [Y. LeCun, Y. Bengio, and G. Hinton], [Y. LeCun _et al._],
  [2], [S. Russell and P. Norvig], [S. Russell and P. Norvig],
)

- *Why a separate style file:* Typst's built-in `ieee` style lists up to 6 authors and only switches to "et al." at 7. It is stored inside the Typst program and can't be edited, so the template ships its own copy, `template/ieee.csl`.
- *Where it came from:* the official `ieee.csl` from the Citation Style Language project (#link("https://github.com/citation-style-language/styles")[github.com/citation-style-language/styles]), the same style collection Zotero and Mendeley use. Before editing, it was checked against Typst's built-in `ieee` style: both rendered the Bibliography *pixel-identical*.
- *The one change:* in the author list (and, for consistency, the director list), `et-al-min="7"` became `et-al-min="3"`:
  ```xml
  <name and="text" et-al-min="3" et-al-use-first="1" initialize-with=". "/>
  ```
  `et-al-min` is the number of authors at which the list switches to "et al." (3 = more than 2); `et-al-use-first` is how many authors are shown before it (1 = first author only). Nothing else in the file changed; a comment at the top of `ieee.csl` records the edit.
- *Where it is used:* both bibliographies in `template/body.typ` (Books and Journal Papers) use `style: "/template/ieee.csl"`.
- *To change it:* edit the two `et-al-min` values in `template/ieee.csl`, or set both `style:` values in `template/body.typ` back to `"ieee"` to return to Typst's default.

== 9. Editing with an AI code editor

You can let an AI coding assistant do the typing. Cursor, Windsurf, VS Code with GitHub Copilot, Claude Code, OpenAI Codex, Gemini CLI and similar tools can all edit and compile this project.

+ Get the project folder onto your computer (clone the Git repo, download it from typst.app, or copy the folder you were given). Windows and macOS already have Times New Roman; elsewhere, copy the four `times*.ttf` files into `template/fonts/`.
+ Open the folder in your editor.
+ So the assistant can compile and check its work, install the Typst command-line tool: `winget install --id Typst.Typst` on Windows, `brew install typst` on macOS. In VS Code-based editors, the *Tinymist Typst* extension adds a live preview.
+ Ask for what you want in plain English.

*`AGENTS.md`* is a briefing written for AI assistants. It tells them:

- what this project is, and that they may be helping someone new to Typst;
- the rules: don't change the college formatting, keep personal details in `config.typ` and writing in `content/`, and never invent results, data or references;
- how to compile and check the book, and when a change counts as done (all outputs compile with no errors or warnings);
- every college formatting rule and the file that implements it, plus the decisions made on purpose, so they don't "fix" them;
- step-by-step recipes (chapters, figures, tables, equations, citations, abbreviations, appendices) and the Typst pitfalls met while building this template.

Most AI coding tools read `AGENTS.md` automatically. If yours doesn't, start with: _"Read AGENTS.md first."_

Example requests:

- "Add a chapter called Methodology after chapter 2, with sections Dataset, Model and Training."
- "Turn `content/data/results.csv` into a table in chapter 4 with the caption 'Model results'."
- "Here is the BibTeX for three papers. Add them and cite them in the literature review."
- "Remove the tutorial chapters and set up my five chapters."
- "The book doesn't compile. Find and fix the error."

#note(title: "Remember:")[Always read the PDF yourself before submitting. Assistants make mistakes, and you are responsible for what your report says.]
