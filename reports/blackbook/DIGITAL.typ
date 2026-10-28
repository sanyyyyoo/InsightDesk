// ▶ Compile THIS file for the digital (soft-copy) version — black & gold cover.
#import "/config.typ": Title, dataset
#import "/template/utils.typ": blank-page

// PDF properties (shown under File → Properties in PDF viewers and used by the digital library):
// title from config.typ, authors = every student in the dataset list, date = when the PDF is compiled.
#set document(
  title: Title,
  author: dataset.map(student => student.first()),
  date: auto,
)

#include "template/covers/digital.typ"
#pagebreak()
#blank-page
#pagebreak()
#blank-page
#pagebreak()

#set page(paper:"a4", margin: 25mm)

#include "template/front-matter/front-matter.typ"

#include "template/body.typ"

#pagebreak()
#blank-page
#pagebreak()
#blank-page
