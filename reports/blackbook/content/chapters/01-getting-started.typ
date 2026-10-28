// ============================================================================
//  SAMPLE CHAPTER 1 — Getting started with Typst (usage & formatting)
//
//  This chapter is a beginner's guide written with the template itself.
//  Read the compiled PDF side-by-side with this file to see how everything
//  is written. When you are ready, replace these sample chapters with your own
//  (see "Adding a new chapter" below).
// ============================================================================

// Loads the "YOU TYPE / YOU GET" boxes used in these sample chapters.
// Your own chapters don't need this line.
#import "/template/tutorial.typ": *

= Getting Started with Typst

== What is Typst?

Typst is a typesetting language. You write plain text with a few simple marks, like `*bold*` or `= Heading`, and Typst turns it into a properly formatted PDF. It does the same job as Microsoft Word or LaTeX, but you never format anything by hand.

This template already takes care of the margins, fonts, chapter titles, numbering, the contents page, the lists of figures and tables, and the page numbers. *You only write the content.*

This chapter and the next three are a guide to the template, written with the template itself. Most examples show the code you type in a grey box, and the result it produces below it. Open the file `content/chapters/01-getting-started.typ` next to this PDF to compare them line by line.

== Setting Up

=== Option 1: typst.app (easiest, nothing to install)

+ Create a free account at #link("https://typst.app")[typst.app].
+ Create a new empty project, then drag and drop *all* the files and folders of this template into the file panel on the left.
+ Open `PRINT.typ`. The preview on the right updates live as you type.
+ When you are done, click the download (export) button at the top right to get the PDF.

=== Option 2: VS Code on your own computer

+ Install #link("https://code.visualstudio.com")[VS Code] and the free extension *Tinymist Typst*.
+ Open the template folder in VS Code (_File → Open Folder_) and open `PRINT.typ`.
+ Click the preview button at the top right of the editor to see the PDF live.
+ Use the *Export PDF* link shown at the top of the file to produce the PDF.

=== Option 3: Command line

If you have installed the `typst` command, run this from the template folder:

#code(```bash
typst compile --font-path template/fonts PRINT.typ      # makes PRINT.pdf once
typst watch   --font-path template/fonts PRINT.typ      # re-makes it on every save
```)

== Where Everything Lives

#table(
  columns: (5.8cm, 1fr, 2cm),
  stroke: 0.5pt,
  align: (left + horizon, left + horizon, center + horizon),
  table.header([*File / folder*], [*What it is*], [*Edit it?*]),
  [`config.typ`], [Project title, student names, guides, HOD, college details and the list of chapters.], [Yes, first],
  [`content/chapters/`], [One file per chapter. This is where you write.], [Yes],
  [`content/abstract.typ` \ `content/acknowledgement.typ`], [The text of the abstract and acknowledgement pages.], [Yes],
  [`content/abbreviations.typ` \ `content/symbols.typ`], [The List of Abbreviations and List of Symbols.], [Yes],
  [`content/co-po-mapping.typ`], [The CO–PO mapping table to fill in.], [Yes],
  [`content/images/`], [Your figures, screenshots and diagrams.], [Yes],
  [`content/references/`], [Your references, as `.bib` files (see Chapter 4).], [Yes],
  [`PRINT.typ` \ `DIGITAL.typ`], [The files you compile, for the printed book and the soft copy.], [No],
  [`template/`], [All the formatting rules.], [No],
)

=== Adding a new chapter

+ Create a new file in `content/chapters/`, for example `05-methodology.typ`.
+ Write a chapter heading on the first line, followed by your text:
  #code(```typ
  = Methodology

  In this chapter we describe ...
  ```)
+ Open `config.typ` and add the file to the `chapters` list, in the order it should appear:
  #code(```typ
  #let chapters = (
    "/content/chapters/01-introduction.typ",
    "/content/chapters/02-literature-review.typ",
    "/content/chapters/05-methodology.typ",   // ← new line
  )
  ```)

The chapter then starts on a new page, is numbered automatically, and is added to the Contents.

== Writing Text

=== Paragraphs and line breaks

#example(```typ
This is the first paragraph. A single line break
in your file does nothing; the text just continues.

A blank line starts a new paragraph. The template
indents it and justifies it automatically.\
A backslash at the end of a line forces a line break.
```)

=== Comments

Anything after `//` on a line, or between `/*` and `*/`, is a note to yourself and is not printed.

#example(```typ
This sentence is printed. // This note is not.
/* Neither is this
   longer note. */
```)

== Headings

Headings are written with `=` signs. The number of `=` signs sets the level:

#code(```typ
= Chapter Title        // level 1: once, at the top of each chapter file
== Section             // level 2: numbered 1.1, 1.2, ...
=== Sub-section        // level 3: numbered 1.1.1, ...
==== Paragraph Heading // level 4: numbered 1.1.1.1, ...
```)

Never type the numbers yourself. The template numbers the headings, styles them and adds them to the Contents. The headings of this chapter are examples of levels 1, 2 and 3.

#tip[Begin every chapter with a `==` section heading (for example `== Introduction`) straight after the chapter title. This keeps the spacing below the chapter title consistent.]

== Text Formatting

#example(```typ
*Bold text*, _italic text_ and *_both together_*. \
#underline[Underlined text] and #strike[struck-through text]. \
`Monospace text` for file names, commands and short code. \
H#sub[2]O and x#super[2] for subscripts and superscripts. \
#text(size: 14pt)[Larger text] and #text(fill: blue)[coloured text]. \
#highlight[Highlighted text] and #smallcaps[Small Capitals].
```)

#tip[A black book is a formal document, so use bold and italics sparingly, and don't use colours in the printed copy.]

== Lists

#example(```typ
- A bullet point
- Another bullet point
  - Indent by two spaces to nest a list

+ A numbered item
+ The numbers are added automatically
  + Nested items are numbered too

/ Term: A description list, used for definitions.
/ CNN: Convolutional Neural Network
```)

== Special Characters

Some characters have a special meaning in Typst: #raw("* _ # $ @ < ` \\"). To print one of them as it is, put a backslash `\` in front of it.

#example(```typ
Cost: \$500 · Email: name\@gmail.com · C\# · \*not bold\* \
Ranges use an en dash: pages 10--20 or 2023--24. \
An em dash marks a break---like this. \
"Quotes" become curly automatically, and ... becomes an ellipsis.
```)

== Spacing, Alignment and Page Breaks

#example(```typ
Some text.
#v(1cm)
Text one centimetre lower.

#align(center)[Centred text]
#align(right)[Right-aligned text]
```)

To start a new page, write `#pagebreak()`. You rarely need it, because every chapter already starts on a new page.

== Abbreviations and Symbols

The List of Abbreviations and List of Symbols at the front of the book are filled in from `content/abbreviations.typ` and `content/symbols.typ`. Each entry uses the description-list syntax from the Lists section:

#code(```typ
/ CNN: Convolutional Neural Network
/ LSTM: Long Short-Term Memory
/ ROC: Receiver Operating Characteristic
```)

Keep the abbreviations in alphabetical order. In the List of Symbols, the college requires Greek symbols first, then English letters (lower case before upper case), each group in alphabetical order. If you don't need one of these lists, delete everything below the `// --- CONTENT ---` line in its file, and the page disappears from the book.

== When Something Goes Wrong

If Typst can't compile your file, it shows an error with the file name and line number. In typst.app and VS Code, the problem is also underlined in red. These are the most common errors:

#table(
  columns: (4.2cm, 1fr),
  stroke: 0.5pt,
  align: left + horizon,
  table.header([*Error message*], [*Usual cause and fix*]),
  [`unknown variable: xy`], [Inside maths, letters written next to each other are read as one word. Write `x y` with a space (see Chapter 3).],
  [`label <...> does not exist`], [A reference like `@fig:abc` doesn't match any label: check the spelling. In normal text, an email address needs `\@`.],
  [`file not found`], [Wrong image path. Paths start with `/content/images/` and must match the file name exactly, including capitals and the extension.],
  [`unclosed delimiter`], [A missing `]`, `)` or `}`. Check the brackets on the line shown.],
  [Text suddenly turns bold or italic], [A `*` or `_` was left unclosed. Close it, or write `\*` or `\_` to print the character itself.],
)
