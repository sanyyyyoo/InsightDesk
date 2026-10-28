// ============================================================================
//  CONFIG — fill in YOUR project details here.
//  Every cover, certificate, approval page and the spine read from this file.
// ============================================================================

// --- Project -----------------------------------------------------------------
#let Title = "InsightDesk: Intelligent Complaint Triage System"
#let Stream = "Artificial Intelligence & Data Science"
#let Stream-Short = "AI-DS"  // printed on the spine, e.g. AI-DS 2026-27/Group-3

#let Group-Number = "10"

// --- Students ----------------------------------------------------------------
// One line per student: (Name, Roll Number, Division, Exam Seat Number)
// [TO FILL] Division and Exam Seat No. for each student.
#let dataset = (
  ("Krushnam Sadrani", 40, "L.Y. - [DIV]", "[SEAT NO.]"),
  ("Sanyogita Shinde", 60, "L.Y. - [DIV]", "[SEAT NO.]"),
  ("Krisha Sinnarkar", 61, "L.Y. - [DIV]", "[SEAT NO.]"),
)

// --- Guides ------------------------------------------------------------------
#let Supervisor-1 = "Prof. Ganesh Wadmare"
#let Supervisor-1-Designation = "[DESIGNATION]"  // [TO FILL] e.g. Assistant Professor
#let Supervisor-1-Dept = "AI&DS"

#let Supervisor-2 = ""  // No co-guide assigned. Set a name here if there is one.
#let Supervisor-2-Designation = ""
#let Supervisor-2-Dept = ""

// --- Signatories -------------------------------------------------------------
#let HOD-name = "[HOD NAME]"  // [TO FILL]

#let Principal-name = "[PRINCIPAL NAME]"  // [TO FILL]

// --- College (printed at the bottom of the covers) ---------------------------
#let College-Name = "K.J. Somaiya Institute of Technology"
#let College-Address = "Sion Ayurvihar Complex, Eastern Express Highway, Everard Nagar, Sion East, Mumbai-400022"
#let Year = "2026"

// --- Chapters ----------------------------------------------------------------
// Listed in the order they appear in the book.
// To add a chapter: create a file in content/chapters/ and add its path here.
#let chapters = (
  "/content/chapters/01-introduction.typ",
  "/content/chapters/02-literature-survey.typ",
  "/content/chapters/03-proposed-system.typ",
  "/content/chapters/04-methodology.typ",
  "/content/chapters/05-implementation.typ",
  "/content/chapters/06-datasets-and-evaluation.typ",
  "/content/chapters/07-results-and-discussion.typ",
  "/content/chapters/08-conclusion.typ",
)
