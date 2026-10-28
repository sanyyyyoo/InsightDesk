// Helpers used ONLY by the sample tutorial chapters in content/chapters/.
// Once you replace those chapters with your own, nothing uses this file.

#let _label(body) = text(size: 9pt, fill: luma(110), weight: "bold", body)

// A grey box showing code exactly as you would type it.
#let code(source) = block(
  width: 100%,
  fill: luma(244),
  stroke: 0.5pt + luma(200),
  radius: 2pt,
  inset: 8pt,
  {
    set text(size: 9.5pt)
    set par(justify: false)
    source
  },
)

// Shows the code you type, then the result it produces in the book.
// The result is real: figures, tables and equations made here are numbered
// and listed exactly like your own will be.
#let example(source) = {
  block(breakable: false, below: 0.6em)[
    #_label[YOU TYPE]
    #code(source)
  ]
  block(breakable: false, below: 1.4em)[
    #_label[YOU GET]
    #block(
      width: 100%,
      stroke: 0.5pt + luma(200),
      radius: 2pt,
      inset: 10pt,
      eval(source.text, mode: "markup"),
    )
  ]
}

// A highlighted tip / warning box.
#let tip(title: "Tip:", body) = block(
  width: 100%,
  fill: rgb("#eef4fb"),
  stroke: (left: 2.5pt + rgb("#4a7ab8")),
  inset: (x: 10pt, y: 8pt),
  {
    set par(first-line-indent: 0em)
    [*#title* #body]
  },
)
