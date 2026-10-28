# Black Book — Typst Template

A ready-made Typst template for the L.Y. major project report (black book).
You only fill in **your details** and **your content**. The formatting is already done.

> **New to Typst?** Compile `PRINT.typ` (see below) and read **Chapters 1–4** of the PDF.
> The sample chapters are a step-by-step tutorial written with the template itself. Each
> example shows the code you type and the result it produces:
>
> 1. **Getting Started**: setup, folders, paragraphs, headings, bold/italic, lists, special characters, common errors
> 2. **Figures and Tables**: images, side-by-side figures, tables, merged cells, CSV/Excel tables, code listings, diagrams, footnotes, cross-references
> 3. **Mathematics**: inline and display equations, symbols, fractions, matrices, cases, multi-line and numbered equations, common mistakes
> 4. **Citing References**: getting BibTeX from Google Scholar, citing papers, books and websites
>
> Keep the matching `.typ` file open next to the PDF to see exactly how each page is written.

> **On typst.app?** Click `readme.typ` in the Files panel for a formatted version of this guide, with steps for the web app.

> **Using an AI code editor?** Cursor, VS Code + GitHub Copilot, Claude Code, Codex and similar tools can edit and compile this project for you. `AGENTS.md` tells them the rules; see [Editing with an AI code editor](#editing-with-an-ai-code-editor).

## Folder layout

```
BLACK BOOK/
│
├── PRINT.typ            ▶ compile → hard-bound print version (wider binding margin)
├── DIGITAL.typ          ▶ compile → soft-copy version (black & gold cover)
├── PRINT-SPINE.typ      ▶ compile → spine strip: title (auto-sized to one line) + AI-DS 2026-27/Group-3
├── readme.typ           📖 this guide as a Typst document (open it on typst.app)
├── AGENTS.md            🤖 briefing for AI coding assistants (rules, build steps, recipes)
│
├── config.typ           ✏️  STEP 1 — title, students, guides, HOD, college, chapter list
│
├── content/             ✏️  STEP 2 — everything you write goes here
│   ├── abstract.typ
│   ├── acknowledgement.typ
│   ├── co-po-mapping.typ      fill in the mapping levels
│   ├── abbreviations.typ      page skipped automatically if left empty
│   ├── symbols.typ            page skipped automatically if left empty
│   ├── chapters/              one file per chapter (the 4 samples are the tutorial)
│   │   ├── 01-getting-started.typ
│   │   ├── 02-figures-and-tables.typ
│   │   ├── 03-mathematics.typ
│   │   └── 04-citing-references.typ
│   ├── appendix.typ
│   ├── publications.typ
│   ├── images/                put your figures/screenshots here
│   ├── data/                  CSV files for tables (optional)
│   └── references/            your .bib files
│       ├── books.bib
│       └── journals.bib
│
└── template/            🔒 the formatting rules — you don't need to touch this
    ├── covers/                print + digital cover, shared title-page layout
    ├── front-matter/          title page, certificate, approval, declaration, …
    ├── body.typ               contents page, lists, page numbering, chapter style
    ├── outlines.typ           table-style Contents / Figures / Tables lists
    ├── utils.typ              small shared helpers
    ├── ieee.csl               IEEE reference style ("et al." after the first author when 3+ authors)
    ├── tutorial.typ           "YOU TYPE / YOU GET" boxes used by the sample chapters
    ├── logos/
    └── fonts/                 Times New Roman (not in the Git repo, see Fonts below)
```

## Quick start

1. **`config.typ`**: put in your project title, stream (and its short form for the spine, e.g. `AI-DS`), group number, students, guides and so on.
2. **`content/`**: write your abstract, acknowledgement and chapters. Read the sample chapters first, then replace them with your own (and update the `chapters` list in `config.typ`).
3. **Compile** `PRINT.typ` (for printing) and/or `DIGITAL.typ` (for the soft copy).

### Compiling

**typst.app (easiest):** upload the whole folder as a project, open `PRINT.typ` or `DIGITAL.typ`, and download the PDF.

**VS Code:** install the *Tinymist Typst* extension, open `PRINT.typ`, and click *Preview* / *Export PDF*.

**AI code editor:** let an AI assistant edit and compile it for you; see [below](#editing-with-an-ai-code-editor).

**Command line:**

```bash
typst compile --font-path template/fonts PRINT.typ
```

```bash
typst compile --font-path template/fonts DIGITAL.typ
```

```bash
typst compile --font-path template/fonts PRINT-SPINE.typ
```

The packages (`i-figured`, `alexandria`, and `fletcher` for the sample diagram) are downloaded automatically the first time you compile.

### Fonts

The Times New Roman font files are **not included in the Git repository**: their licence doesn't allow redistributing them. The template still works:

- **Windows and macOS:** Times New Roman is already installed, so there is nothing to do.
- **Linux, typst.app, or anywhere else without it:** copy `times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf` from a Windows PC (`C:\Windows\Fonts`) into `template/fonts/` (on typst.app, upload them into the project). On Ubuntu/Debian, `sudo apt install ttf-mscorefonts-installer` also works.

If Times New Roman is missing, Typst warns `unknown font family: times new roman` and the book comes out in a different font.

## Editing with an AI code editor

You can let an AI coding assistant do the typing. Cursor, Windsurf, VS Code with GitHub Copilot, Claude Code, OpenAI Codex, Gemini CLI and similar tools can all edit and compile this project.

1. Get the project folder onto your computer (clone the Git repo, download it from typst.app, or copy the folder you were given). A Git clone has no font files; see [Fonts](#fonts).
2. Open the folder in your editor.
3. So the assistant can compile and check its work, install the Typst command-line tool: `winget install --id Typst.Typst` on Windows, `brew install typst` on macOS. In VS Code-based editors, the *Tinymist Typst* extension adds a live preview.
4. Ask for what you want in plain English.

**`AGENTS.md`** is a briefing written for AI assistants. It tells them:

- what this project is, and that they may be helping someone new to Typst;
- the rules: don't change the college formatting, keep personal details in `config.typ` and writing in `content/`, and never invent results, data or references;
- how to compile and check the book, and when a change counts as done (all outputs compile with no errors or warnings);
- every college formatting rule and the file that implements it, plus the decisions made on purpose, so they don't "fix" them;
- step-by-step recipes (chapters, figures, tables, equations, citations, abbreviations, appendices) and the Typst pitfalls met while building this template.

Most AI coding tools read `AGENTS.md` automatically. If yours doesn't, start with: *"Read AGENTS.md first."*

Example requests:

- "Add a chapter called Methodology after chapter 2, with sections Dataset, Model and Training."
- "Turn `content/data/results.csv` into a table in chapter 4 with the caption 'Model results'."
- "Here is the BibTeX for three papers. Add them and cite them in the literature review."
- "Remove the tutorial chapters and set up my five chapters."
- "The book doesn't compile. Find and fix the error."

Always read the PDF yourself before submitting. Assistants make mistakes, and you are responsible for what your report says.

## Quick reference

The tutorial chapters explain all of this in detail. These are the most common tasks:

### …add a chapter?

1. Create a file in `content/chapters/`, e.g. `04-results.typ`.
2. Start it with a level-1 heading, then a first section: `= Results and Discussion` and `== Introduction`
3. Add its path to the `chapters` list in `config.typ`:
   ```typ
   #let chapters = (
     ...
     "/content/chapters/04-results.typ",
   )
   ```

Chapter numbers, the "CHAPTER N" title, page breaks and the Contents entry are all automatic.

### …add a figure?

Put the image in `content/images/`, then:

```typ
#figure(image("/content/images/architecture.png", width: 80%), caption: [System Architecture]) <arch>

As shown in @fig:arch, ...
```

It is numbered per chapter (Figure 2.1, 2.2 …) and added to the **List of Figures** automatically.
Numbers restart in every chapter.
Tables wrapped in `#figure(table(...), caption: [...])` go into the **List of Tables** the same way.

**References need a prefix:** `@fig:name` for images, `@tbl:name` for tables, `@lst:name` for code and `@eqt:name` for equations. The label itself is written without the prefix, as `<name>`.

### …write an equation?

Every display equation (`$ ... $` on its own line, with spaces inside the dollar signs) is numbered by chapter, e.g. (3.1), as the college rules require:

```typ
$ sigma(z) = 1 / (1 + e^(-z)) $ <activation>

The sigmoid in @eqt:activation ...  // prints "Eqn.(3.1)"
```

Label an equation `<->` to leave it unnumbered. See Chapter 3 of the tutorial for everything else.

### …add an appendix?

Each `= Title` in `content/appendix.typ` starts a new appendix, numbered **A1, A2, …** (sections A1.1, figures/tables A1.1, equations (A1.1)). Delete everything in that file if you don't need appendices.

### …cite a paper or book?

Add the BibTeX entry to `content/references/books.bib` or `journals.bib`, then write `@key` in your text.
See `content/chapters/04-citing-references.typ` for an example. In the Bibliography, entries with 3 or more authors show the first author followed by *et al.* (see [How the "et al." rule works](#how-the-et-al-rule-works)).

### …use other Typst packages (diagrams, etc.)?

Import them at the top of the chapter file that uses them, e.g.

```typ
#import "@preview/cetz:0.4.1"
```

### …fill the List of Abbreviations / Symbols?

One entry per line, `/ CNN: Convolutional Neural Network` or `/ $V_"pp"$: Voltage corresponding to peak power`. The template lines them up in columns and adds the dash. Symbols go Greek first, then English lower case, then upper case, each group alphabetical.

To remove either page, delete everything below `// --- CONTENT ---` in `content/abbreviations.typ` or `content/symbols.typ`.
The List of Figures and List of Tables also disappear on their own if you have no figures or tables.

## Not from AI&DS?

A few department-specific things are worth checking:

- `config.typ`: set `Stream` (printed on the covers, certificate and approval page) and `Stream-Short` (printed on the spine).
- `content/co-po-mapping.typ`: the **PSO table** at the bottom is written for AI&DS.

## How the "et al." rule works

College rule: with more than 2 authors, list the first author followed by "et al."

| Authors | Typst's built-in IEEE style                               | This template            |
|---------|-----------------------------------------------------------|--------------------------|
| 4       | T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein | T. H. Cormen *et al.*    |
| 3       | Y. LeCun, Y. Bengio, and G. Hinton                        | Y. LeCun *et al.*        |
| 2       | S. Russell and P. Norvig                                  | S. Russell and P. Norvig |

- **Why a separate style file:** Typst's built-in `ieee` style lists up to 6 authors and only switches to "et al." at 7. It is stored inside the Typst program and can't be edited, so the template ships its own copy, `template/ieee.csl`.
- **Where it came from:** the official `ieee.csl` from the Citation Style Language project (https://github.com/citation-style-language/styles), the same style collection Zotero and Mendeley use. Before editing, it was checked against Typst's built-in `ieee` style: both rendered the Bibliography **pixel-identical**.
- **The one change:** in the author list (and, for consistency, the director list), `et-al-min="7"` became `et-al-min="3"`:

  ```xml
  <name and="text" et-al-min="3" et-al-use-first="1" initialize-with=". "/>
  ```

  `et-al-min` is the number of authors at which the list switches to "et al." (3 = more than 2); `et-al-use-first` is how many authors are shown before it (1 = first author only). Nothing else in the file changed; a comment at the top of `ieee.csl` records the edit.
- **Where it is used:** both bibliographies in `template/body.typ` (Books and Journal Papers) use `style: "/template/ieee.csl"`.
- **To change it:** edit the two `et-al-min` values in `template/ieee.csl`, or set both `style:` values in `template/body.typ` back to `"ieee"` to return to Typst's default.
