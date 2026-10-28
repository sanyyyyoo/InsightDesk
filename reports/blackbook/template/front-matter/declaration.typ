#import "/config.typ": *

#set text(font: "Times New Roman")

#align(center)[#text(size: 14pt, weight: "bold")[DECLARATION]]

#v(2em)

#par(justify: true, leading: 22.5pt)[I declare that this written submission represents my ideas in my own words and where others' ideas or words have been included, I have adequately cited and referenced the original sources. I also declare that I have adhered to all principles of academic honesty and integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source in my submission. I understand that any violation of the above will be cause for disciplinary action by the Institute and can also evoke penal action from the sources which have thus not been properly cited or from whom proper permission has not been taken when needed.]

#v(4em)

#align(right)[
  #table(
    columns: (4cm, 5cm),
    row-gutter: 15pt,
    stroke: none,
    align: (left + horizon, center + bottom),
    ..dataset.map(row => (
      row.at(0),
      line(length: 80%, stroke: 0.5pt)
    )).flatten(),
    [], [(Signature)],
  )
]


#align(left+bottom)[
 Date:
]

#pagebreak()