#import "/config.typ": *
#import "/template/utils.typ": *

#set align(left)

#set text(font: "Times New Roman")

#set text(size: 12pt)
#set par(justify: true)

#set page(
  paper: "a4",
  header-ascent:0%-50pt,
  header: grid(
    columns: (1fr, 1fr),
    align: (left + bottom, right + bottom),
    inset: (bottom: 6pt),
    align(left+horizon)[#image("/template/logos/SV.svg", height: 2.6cm)],
    align(right+horizon)[#image("/template/logos/UOM.svg", height: 2.6cm)]
  )
)


#align(center+horizon)[#text(size: 14pt, weight: "bold")[CERTIFICATE]]
#v(4em)

#par(leading: 1.5em)[_This is to certify that the project entitled "#Title" is a bona fide work of #format-student-names(dataset), submitted to the University of Mumbai in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in #Stream._]

#v(4em)

#grid(
  columns: (1fr,1fr),
  row-gutter: 100pt,
  align: (center+horizon),
  
  [#if Supervisor-2 != "" and Supervisor-2 != none [
  #Supervisor-2
  ]\
  #if Supervisor-2-Designation != "" and Supervisor-2-Designation != none [
  #Supervisor-2-Designation
  ]\
  #if Supervisor-2-Dept != "" and Supervisor-2-Dept != none [
  #Supervisor-2-Dept
  ]],
  
  [#Supervisor-1\ #Supervisor-1-Designation\ Dept. of #Supervisor-1-Dept Engineering],
  
  [#box(width: 4cm, repeat[.])\(sign)

  #HOD-name

  Head of Department
  ],
  
  [#box(width: 4cm, repeat[.])\(sign)

  #Principal-name

  Principal
  ]
)

#v(1fr)
#align(center)[(College Seal)]

#align(left+bottom)[
  #set text(size: 12pt, weight: "regular")
  
  Place: 

  Date:
]

#pagebreak()