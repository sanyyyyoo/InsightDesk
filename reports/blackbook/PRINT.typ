// ▶ Compile THIS file for the printed (hard-bound) version — wider binding margin.
#import "/template/utils.typ": blank-page

#include "template/covers/print.typ"
#pagebreak()
#blank-page
#pagebreak()
#blank-page
#pagebreak()

// 1. Set global page setup for normal pages
#set page(
  paper: "a4",
  margin: (left: 35mm, right: 25mm, top: 30mm, bottom: 25mm),
)

#include "template/front-matter/front-matter.typ"

// Set 20mm clearance for THIS format only
#state("chapter-top-space", 0mm).update(20mm)

#include "template/body.typ"


#set page(paper: "a4")
#pagebreak()
#blank-page
#pagebreak()
#blank-page
