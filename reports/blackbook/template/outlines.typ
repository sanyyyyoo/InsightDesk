#import "@preview/i-figured:0.2.4"
#import "@preview/alexandria:0.2.2":*

// --- OUTLINE FUNCTIONS ---
#let table-outline(title: upper[#text(size: 14pt, weight: "bold")[Contents]], depth: none) = context {
  let stroke = 0.5pt
  
  align(center, heading(numbering: none, outlined: false, title))
  
  table(
    columns: (2.8cm, 1fr, 2cm),
    align: (center + horizon, left + horizon, center + horizon),
    stroke: (x, y) => (
      x: stroke,
      top: if y == 0 { stroke } else { none },
      bottom: stroke,
    ),
    table.header(
      ..([Chapter No.], [Title], [Page No.]).map(strong).map(align.with(center))
    ),
    ..query(heading).map(h => {
      if depth != none and h.level > depth { return () }
      if not h.outlined { return () }
      
      let loc = h.location()
      let num = if h.numbering != none {
        numbering(h.numbering, ..counter(heading).at(loc))
      } else {
        []
      }
      let page-num = if loc.page-numbering() != none {
        numbering(loc.page-numbering(), ..counter(page).at(loc))
      } else { str(loc.page()) }
      
      (table.hline(stroke: stroke), num, h.body, page-num)
    }).flatten(),
    table.hline(stroke: stroke)
  )
}

#let figure-table-outline() = context {
  let stroke = .5pt
  let target-kind = i-figured._prefix + repr(image)
  let figures = query(figure.where(kind: target-kind))
  
  table(
    columns: (2.8cm, 1fr, 2cm),
    align: (center+horizon, left+horizon, center+horizon), 
    stroke: stroke, 
    table.header(..([Figure No], [Title], [Page No.]).map(strong).map(align.with(center))),
    
    ..figures.map(fig => {
      let loc = fig.location()
      let caption = if fig.caption != none { fig.caption.body } else { [] }
      
      let fig-counter = counter(figure.where(kind: target-kind)).at(loc)
      let fig-num = if fig-counter.len() > 0 { fig-counter.first() } else { 1 }
      
      let page = if loc.page-numbering() != none {
        numbering(loc.page-numbering(), ..counter(page).at(loc))
      } else { str(loc.page()) }
      
      (numbering(fig.numbering, fig-num), caption, page)
    }).flatten()
  )
}

#let table-table-outline() = context {
  let stroke = .5pt
  let target-kind = i-figured._prefix + repr(table)
  let figures = query(figure.where(kind: target-kind))
  
  table(
    columns: (2.8cm, 1fr, 2cm),
    align: (center+horizon, left+horizon, center+horizon), 
    stroke: stroke, 
    table.header(..([Table No.], [Title], [Page No.]).map(strong).map(align.with(center))),
    
    ..figures.map(fig => {
      let loc = fig.location()
      let caption = if fig.caption != none { fig.caption.body } else { [] }
      
      let fig-counter = counter(figure.where(kind: target-kind)).at(loc)
      let fig-num = if fig-counter.len() > 0 { fig-counter.first() } else { 1 }
      
      let page = if loc.page-numbering() != none {
        numbering(loc.page-numbering(), ..counter(page).at(loc))
      } else { str(loc.page()) }
      
      (numbering(fig.numbering, fig-num), caption, page)
    }).flatten()
  )
}
// --- ALIGNED SYMBOL LIST ---
// Lays out a `/ term: description` list as aligned columns:
//   symbol  –  description
// Each row is one paragraph, so symbols and descriptions share a baseline,
// and long descriptions wrap under the description column.
#let aligned-terms(it, separator: [–], gap: 0.8em) = context {
  let term-width = calc.max(..it.children.map(item => measure(item.term).width))
  let indent = term-width + 2 * gap + measure(separator).width
  set par(justify: false, first-line-indent: 0pt, hanging-indent: indent, spacing: 1.2em)
  for item in it.children {
    par[#box(width: term-width, item.term)#h(gap)#separator#h(gap)#item.description]
  }
}
