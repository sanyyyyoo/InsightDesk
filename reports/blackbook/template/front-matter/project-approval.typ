#import "/config.typ": *

#set text(font: "Times New Roman")

#set text(size: 12pt)

#align(center)[#text(size: 14pt, weight: "bold")[PROJECT APPROVAL FOR LAST YEAR]]

#v(2em)

This project report entitled _ #Title _ by
#align(center)[
  #block(width: auto)[
    #set align(left)
    #for (name, roll, division, seat) in dataset [
      #name #underline[#seat] (Exam Seat No.)
      
    ]
  ]
]

is approved for the Degree of Bachelor of Technology in #Stream.

#v(2em)

#grid(
  columns: (1fr,2fr),
  row-gutter: 100pt,
  
  grid.cell(rowspan: 2)[Examiners],
   
  [#h(1fr) #box()[1.\ (Internal Examiner Name and Sign)]],
  
  [#h(1fr) #box()[2.\ (External Examiner Name and Sign)]]
)

#align(left+bottom)[
  Date: 

  Place:
]

#pagebreak()