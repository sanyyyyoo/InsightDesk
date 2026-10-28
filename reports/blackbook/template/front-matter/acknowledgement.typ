#import "/config.typ": *

#set text(font: "Times New Roman")
#set par(justify: true)  // college rule: full justification of all text

#align(center)[#text(size: 16pt, weight: "bold")[ACKNOWLEDGEMENT]]

#v(2em)

#{
  // Word "1.5 lines" (same values as the chapters in template/body.typ; em-based, so it also fits 11pt)
  set par(leading: 1.063em, spacing: 1.563em)
  include "/content/acknowledgement.typ"
}


#align(right+bottom)[
  #block(width: auto)[
    #set align(left)
    #for (name, roll, division, seat) in dataset [
      *#name*

    ]
  ]
]

#pagebreak()
