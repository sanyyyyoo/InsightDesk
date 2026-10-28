// Shared helpers used by the template files.

#let gold-shine = gradient.linear(
  rgb("#AA771C"),
  rgb("#FFD700"),
  rgb("#FFF2A1"),
  rgb("#D4AF37"),
  angle: 45deg,
)

#let academic-year(start-month: 7) = {
  let today = datetime.today()
  let start-year = if today.month() >= start-month { today.year() } else { today.year() - 1 }
  let end-year-short = str(start-year + 1).slice(2)
  str(start-year) + "-" + end-year-short
}

// Helper function to format names with commas and an Oxford 'and'
#let format-student-names(students) = {
  let names = students.map(student => student.at(0))
  if names.len() == 0 { "" }
  else if names.len() == 1 { names.at(0) }
  else if names.len() == 2 { names.join(" and ") }
  else {
    names.slice(0, -1).join(", ") + ", and " + names.last()
  }
}

#let blank-page = align(center+horizon)[#text(fill: gray)[_This page is intentionally left blank_]]
