// The title page layout. Shared by the print cover, the digital cover and the
// first page of the front matter, so all three always stay identical.
#import "/config.typ": *

#let title-page(
  uni-logo: "/template/logos/UOM.svg",
  college-logo: "/template/logos/SV.svg",
  student-name: name => name,
) = [
#set align(center)

#set text(font: "Times New Roman")

#set text(size: 15pt, weight: "bold")

#image(uni-logo, width: 3.5cm)

#v(0.5fr)

#text(size: 22pt)[#Title]

#v(0.5fr)

L.Y. Project Report

#v(0.5fr)

Submitted in partial fulfillment of the requirements of the Degree of\ Bachelor of Technology in #underline[#Stream]

#v(0.5fr)

#text(weight: "regular")[by]

#align(center)[
  #block(width: auto)[
    #set align(left)
    #for (name, roll, division, seat) in dataset [
      #student-name(name) \
    ]
  ]
]

#v(1fr)

#Supervisor-1

#if Supervisor-2 != "" and Supervisor-2 != none [
  #text(weight: "bold")[#Supervisor-2]
]

#v(1fr)

#image(college-logo, width: 2.5cm)

#text(weight: "regular")[Department of #Stream]

#text(size: 14pt, weight: "regular")[#College-Name]

#College-Address

#Year
]
