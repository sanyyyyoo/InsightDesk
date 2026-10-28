// ============================================================================
//  SAMPLE CHAPTER 2 — Figures, tables, code, diagrams and more
//  Read the compiled PDF side-by-side with this file.
// ============================================================================

#import "/template/tutorial.typ": *

= Figures, Tables and Other Elements

== How Figures and Tables Work

Every figure and table in a black book needs a caption. Wrap it in `#figure(...)` and the template does the rest:

- it is numbered by chapter: Figure 2.1, Figure 2.2, Table 2.1, …
- it is added to the *List of Figures* or *List of Tables* at the front of the book;
- you can refer to it in your text, and the number updates itself if you add or move figures later.

Never type figure or table numbers yourself.

== Images

=== Inserting an image

+ Copy your image into the `content/images/` folder. PNG, JPG and SVG files all work.
+ Insert it with `#figure`, giving the path to the file, a width, and a caption:

#example(```typ
#figure(
  image("/content/images/sample-figure.svg", width: 30%),
  caption: [The Somaiya Vidyavihar logo],
) <logo>
```)

The `width` is a percentage of the text width: `100%` fills the line and `50%` is half of it. You can also use fixed sizes like `8cm`.

#tip[For sharp prints, use SVG files, or PNGs that are at least 1500 pixels wide. Diagrams drawn in draw.io, Excalidraw or PowerPoint can be exported as SVG or PNG and inserted the same way.]

=== Referring to a figure

The `<logo>` written after the figure above is a *label*: a name you choose for the figure. To refer to it in your text, write `@fig:` followed by that name:

#example(```typ
The logo in @fig:logo shows a lamp.
```)

#tip(title: "Important:")[With this template, references to figures, tables, code and equations take a prefix: `@fig:name` for images, `@tbl:name` for tables, `@lst:name` for code listings, and `@eqt:name` for equations (see Chapter 3). The label itself is written without the prefix, as `<name>`. Label names can contain letters, numbers and `-`, but no spaces.]

=== Several images in one figure

Use a `grid` to place images side by side. A second row of the grid holds the sub-captions:

#example(```typ
#figure(
  grid(
    columns: 2,
    column-gutter: 1cm,
    row-gutter: 6pt,
    image("/content/images/sample-figure.svg", width: 3cm),
    image("/content/images/sample-figure.svg", width: 3cm),
    [(a) Original image], [(b) Processed image],
  ),
  caption: [Two images in one figure],
) <pipeline>
```)

== Tables

=== A simple table

#example(```typ
#figure(
  table(
    columns: 3,
    stroke: 0.5pt,
    table.header([*Model*], [*Accuracy*], [*Training time*]),
    [CNN],  [92.4%], [120 s],
    [LSTM], [89.1%], [340 s],
    [SVM],  [84.7%], [15 s],
  ),
  caption: [Comparison of models],
) <models>

@tbl:models shows that the CNN is the most accurate.
```)

How it works:
- `columns: 3` sets the number of columns.
- Each `[...]` is one cell. The cells fill in from left to right, row by row.
- `table.header(...)` marks the header row. If a long table continues onto the next page, the header is repeated there.
- `stroke: 0.5pt` sets the thickness of the lines.

=== Column widths and alignment

#example(```typ
#figure(
  table(
    columns: (3cm, 1fr, auto),
    align: (left, left, center),
    stroke: 0.5pt,
    table.header([*Module*], [*Description*], [*Status*]),
    [Data loader], [Reads the raw images and resizes them to 224 × 224 pixels.], [Done],
    [Trainer], [Trains the model and saves the best checkpoint.], [Done],
    [Dashboard], [Shows the predictions to the user in a web interface.], [Pending],
  ),
  caption: [Project modules],
)
```)

The column widths can be a fixed size like `3cm`, `auto` (just wide enough for the content), or `1fr` (all the remaining space). `align` sets how the text in each column is aligned.

=== Merging cells

Use `table.cell` with `colspan` to merge cells across columns, or `rowspan` to merge them down rows:

#example(```typ
#figure(
  table(
    columns: 4,
    stroke: 0.5pt,
    align: center + horizon,
    table.header(
      table.cell(rowspan: 2)[*Model*], table.cell(colspan: 3)[*Scores*],
      [*Precision*], [*Recall*], [*F1*],
    ),
    [CNN],  [0.91], [0.89], [0.90],
    [LSTM], [0.87], [0.90], [0.88],
  ),
  caption: [Table with merged header cells],
)
```)

=== A table from Excel or Google Sheets

Save your sheet as a CSV file (_File → Save As → CSV_ in Excel, or _File → Download → CSV_ in Google Sheets), put it in `content/data/`, and load it with `csv(...)`:

#example(```typ
#let results = csv("/content/data/results.csv")

#figure(
  table(
    columns: results.first().len(),
    stroke: 0.5pt,
    ..results.flatten(),
  ),
  caption: [Results loaded from a CSV file],
)
```)

== Code Listings

Put code between three backticks, followed by the name of the language for colour highlighting. To give it a number and a caption, wrap it in a `#figure`:

#example(````typ
#figure(
  ```python
  def accuracy(y_true, y_pred):
      correct = sum(t == p for t, p in zip(y_true, y_pred))
      return correct / len(y_true)
  ```,
  caption: [Computing accuracy in Python],
) <accuracy-code>

The function in @lst:accuracy-code returns a value between 0 and 1.
````)

For a short snippet that doesn't need a caption, leave out the `#figure` and write only the backtick block.

== Diagrams and Flowcharts

The simplest way is to draw the diagram in a tool like #link("https://app.diagrams.net")[draw.io], export it as SVG or PNG, and insert it as an image. You can also draw diagrams in code with the `fletcher` package:

#example(```typ
#import "@preview/fletcher:0.5.8": diagram, node, edge

#figure(
  diagram(
    node-stroke: 0.6pt,
    spacing: 3em,
    node((0, 0), [Raw Data]),
    edge("-|>"),
    node((1, 0), [Pre-processing]),
    edge("-|>"),
    node((2, 0), [Model]),
    edge("-|>"),
    node((3, 0), [Prediction]),
  ),
  caption: [System pipeline drawn with fletcher],
)
```)

== Footnotes, Links and Quotations

#example(```typ
Typst was first released in 2023.#footnote[See the official website, https://typst.app.]

Write a web address as it is, like https://github.com, or give it
your own text: #link("https://github.com")[our GitHub repository].

#quote(block: true, attribution: [Donald Knuth])[
  Premature optimization is the root of all evil.
]
```)

Footnotes are placed at the bottom of the page and numbered automatically.

== Referring to Chapters and Sections <sections>

Headings can have labels too. Write the label after the heading, then refer to it with `@` and the label name. No prefix is needed for headings. A heading reference prints only the number, so write the word "Section" or "Chapter" in front of it yourself:

#code(```typ
== Referring to Chapters and Sections <sections>
```)

#example(```typ
This is explained in Section @sections.
```)
