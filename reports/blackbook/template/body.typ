#import "@preview/i-figured:0.2.4"
#import "@preview/alexandria:0.2.2"

#import "outlines.typ": *
#import "/config.typ": chapters

#set par(justify: true)

#set text(font: "Times New Roman")

// Body of thesis: 12pt, 1.5 line spacing, double spacing for equations.
// Leading values are calibrated against MS Word's output for Times New Roman 12pt:
//   Word "1.5 lines" = 20.70pt line pitch -> leading 1.063em
//   Word "Double"    = 27.60pt line pitch -> leading 1.638em
// The paragraph spacing adds 6pt between paragraphs (like Word's "6pt after").
#set text(size: 12pt)
#set par(leading: 1.063em, spacing: 1.563em)
#show math.equation.where(block: true): set block(above: 1.638em, below: 1.638em)
// Code blocks stay single-spaced.
#show raw.where(block: true): set par(leading: 0.65em)

#show figure: i-figured.show-figure

// Every displayed equation is numbered by chapter, e.g. (3.1), and referred to
// in the text as Eqn.(3.1). Label an equation <-> to leave it unnumbered.
#show math.equation: i-figured.show-equation
#show ref: it => {
  let el = it.element
  if el != none and el.func() == math.equation and el.numbering != none {
    link(el.location(), [Eqn.#numbering(el.numbering, ..counter(math.equation).at(el.location()))])
  } else {
    it
  }
}

#let heading-style = state("default", "chapter")

// Appendices are numbered A1, A2, ... (sections A1.1, figures A1.1, ...)
#let appendix-numbering(..nums) = "A" + nums.pos().map(str).join(".")

// Define state variable (defaults to 0mm so other formats remain unchanged)
#let chapter-top-space = state("chapter-top-space", 0mm)

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  // Restart figure, table and equation numbers for every chapter / appendix.
  // (The reset must happen here: this rule replaces the heading element.)
  i-figured.reset-counters(it, return-orig-heading: false)
  
  let style = heading-style.get()
  if style == "chapter" or style == "appendix" {
    let label = if style == "chapter" [CHAPTER] else [APPENDIX]
    stack(
      dir: ttb,
      spacing: 0.3cm,
      v(if style == "chapter" { chapter-top-space.get() } else { 0mm }), // Extra top clearance for chapters only (set by the active format)
      align(center)[#text(size: 14pt)[#label #counter(heading).display()]],
      align(center)[#text(size: 14pt)[#upper[#it.body]]]
    )
    // Chapters should start with a `== Section` (see AGENTS.md). If something else comes
    // first (a paragraph, figure, table...), add the gap a section would have had.
    context {
      let title-end = here().position()
      let nxt = query(selector(heading).after(here())).at(0, default: none)
      let section-first = (
        nxt != none and nxt.level == 2
          and nxt.location().page() == title-end.page
          and nxt.location().position().y - title-end.y < 1pt
      )
      if not section-first { v(29.6pt) }  // = normal title-to-section gap (38 pt) minus the title-to-text gap (8.4 pt)
    }
  } else {
    align(center)[#text(size: 14pt)[#upper[#it.body]]]
    v(2em)
  }
}

#show heading.where(level: 2): it => {
    set text(size: 12pt, weight: "bold")
    v(2em); upper(it); v(2em)
  }

#show heading.where(level: 3): it => {
    set text(size: 12pt, weight: "regular")
    it; v(2em)
  }

#show heading.where(level: 4): it => {
    set text(size: 12pt)
    it;
  }

//PUT ALL ALEXENDARIA SHOW RULES HERE FOR EACH BIB TEXT
#show: alexandria(prefix: "x:", read: path => read(path))
  
// Cover Page
#counter(page).update(1)
#set page(numbering: "i", number-align: center)

#heading-style.update("default")

#table-outline()

#pagebreak()


// indexs
#set heading(numbering: none, supplement: none)

#{
  let raw = read("/content/abbreviations.typ")
  let parts = raw.split("// --- CONTENT ---")
  
  // Check if marker exists and text after it is non-empty
  let has_body = parts.len() > 1 and parts.last().trim().len() > 0
  
  if has_body {
    show terms: aligned-terms
    include "/content/abbreviations.typ"
    pagebreak()
  }
}

#{
  let raw = read("/content/symbols.typ")
  let parts = raw.split("// --- CONTENT ---")
  
  // Check if marker exists and text after it is non-empty
  let has_body = parts.len() > 1 and parts.last().trim().len() > 0
  
  if has_body {
    show terms: aligned-terms
    include "/content/symbols.typ"
    pagebreak()
  }
}

#context {
  let figures = query(figure.where(kind: image))
  
  if figures.len() > 0 [
    = List of Figures

    #figure-table-outline()

    #pagebreak()
  ]
}

#context {
  let tables = query(figure.where(kind: table))
  
  if tables.len() > 0 [
    = List of Tables

    #table-table-outline()

    #pagebreak()
  ]
}

// Main stuff
#counter(page).update(1)
#set page(numbering: "1", number-align: center, header: context {
    // Chapter name as header from the 2nd page of each chapter (none on the
    // page where the chapter begins), right-aligned for one-sided printing.
    let this-page = here().page()
    let started = query(heading.where(level: 1)).filter(hd => hd.location().page() <= this-page)
    if started.len() > 0 and started.last().location().page() != this-page {
      let chapter = started.last()
      set text(size: 10pt, style: "italic")
      align(right, if chapter.numbering != none {
        let label = if chapter.supplement == [Appendix] [Appendix] else [Chapter]
        [#label #numbering(chapter.numbering, ..counter(heading).at(chapter.location())) #h(0.5em)|#h(0.5em) #chapter.body]
      } else {
        chapter.body
      })
      v(-0.6em)
      line(length: 100%, stroke: 0.4pt)
    }
  }, footer: context {
    let current_page = counter(page).get().first()
    if current_page > 1 {
      align(center, counter(page).display())
    }
  })
#set heading(numbering: "1.1")
#counter(heading).update(0)
#heading-style.update("chapter")

#set par(first-line-indent: 1em)

// Chapters (the list lives in config.typ)
#for chapter in chapters {
  include chapter
}

// Back Matter
#set heading(numbering: none, supplement: none)
#heading-style.update("default")

= Bibliography

#align(center)[#text(14pt)[*Books,*]]
#bibliography("/content/references/books.bib", full: true, title: none, style: "/template/ieee.csl")

#align(center)[#text(14pt)[*Journal Papers,*]]
#bibliography("/content/references/journals.bib", full: true, title: none, style: "/template/ieee.csl")

// Appendices (each = heading in content/appendix.typ is one appendix)
#{
  set heading(numbering: appendix-numbering, supplement: [Appendix])
  show figure: i-figured.show-figure.with(numbering: appendix-numbering)
  show math.equation: i-figured.show-equation.with(numbering: (..n) => "(" + appendix-numbering(..n) + ")")
  counter(heading).update(0)
  heading-style.update("appendix")
  include "/content/appendix.typ"
}
#heading-style.update("default")

#include "/content/publications.typ"
