// ▶ Compile THIS file for the text strip printed on the book's spine.
#import "/config.typ": *
#import "/template/utils.typ": academic-year

#set page(width: auto, margin: 10pt, flipped: true)

#set text(font: "Times New Roman")

// Left end of the strip = top of the spine: the project title.
// Right end = bottom of the spine: stream, academic year and group (coordinator's format).
// The title keeps the normal text size, and shrinks only as much as needed to stay on one line.
#layout(size => {
  let info = [#Stream-Short #academic-year()/Group-#Group-Number]
  let gap = 2em
  let room = size.width - measure(info).width - gap.to-absolute()
  let title-width = measure(Title).width
  let title-size = if title-width <= room { 1em } else { 1em * (room / title-width) * 0.99 }
  grid(
    columns: (1fr, auto),
    column-gutter: gap,
    align: (left + horizon, right + horizon),
    text(size: title-size, Title),
    info,
  )
})
