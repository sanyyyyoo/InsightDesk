// ============================================================================
//  CO-PO MAPPING
//  Fill in the mapping levels (1 / 2 / 3 / -) in the empty [ ] cells of the
//  first table. The PSO table at the bottom is department-specific — update it
//  if you are not from AI&DS. Everything else is the college's standard text.
// ============================================================================

#set text(font: "Times New Roman")

#align(center)[#text(size: 14pt, weight: "bold")[CO-PO MAPPING]]
#v(2em)

#text(size: 14pt, weight: "bold")[CO-PO Mapping:]\
Map COs with POs, POs satisfied by respective COs are mentioned in the above table.\
In the table given below, you have to map COs with POs in either of the three levels. Write levels against every COs. Write “-“ if CO not mapping with PO.\
“1”: For less mapping #h(1fr)		“2”: Moderate mapping	#h(1fr)	“3”: Strong mapping\
*(PSO1, PSO2, and PSO3 mapping with COs based on the Project development task. PSO2 will be mapped only if your project design task includes VLSI Design technology)*

#align(center)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: center + horizon,
    stroke: 0.5pt + black,

    // Header Row
    [*COs*], [*PO1*], [*PO2*], [*PO3*], [*PO4*], [*PO5*], [*PO6*], 
    [*PO7*], [*PO8*], [*PO9*], [*PO10*], [*PO11*], [*PO12*], 
    [*PSO1*], [*PSO2*], [*PSO3*],

    [*CO1*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ],
    [*CO2*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ],
    [*CO3*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ],
    [*CO4*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ],
    [*CO5*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ],
    [*CO6*], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ], [ ]
  )
]

#align(center)[
#show table.cell.where(x: 1): set par(justify: true)
#table(
  columns: (2cm, 1fr),
  align: (center + horizon, left + horizon),
  stroke: 0.5pt + black,

  // Header Row
  [*CO/PO\ mapping*], align(center)[*Proof required*],

  // Data Rows
  [CO1], [Literature review chapter, detailed problem statement based on research knowledge, discussion on results],
  [CO2], [Hardware and software used for project],
  [CO3], [Include a chapter on the Introduction and Context of the project (Context related to *public health, safety, societal, environmental issues*, and sustainable development)],
  [CO4], [Project Report writing and presentation],
  [CO5], [Plagiarism check certificate, proper citations in the report, acknowledgment of figures, data, observations in rubrics],
  [CO6], [Timely completion- marks awarded in rubrics, Budget documentation- Logbook maintenance]
)]

#pagebreak()

#text(size: 14pt, weight: "bold")[Explanation of PO satisfied by LY Project]
#text(size:11pt)[
// Line spacing matched to the coordinator's Word document:
// first column "single" (12.65 pt), second column "exactly 12.45 pt", justified.
#set par(leading: 0.488em)
#align(center)[
  #table(
  columns: (5cm, 1fr),
  stroke: 0.5pt + black,
  align: (left + horizon, left + horizon),

  // Data Rows
  [*PO1*\ Engineering Knowledge (EK)], par(justify: true, leading: 5.17pt)[Apply knowledge of mathematics, natural science, computing, engineering fundamentals and an engineering specialization as specified in WK1 to WK4 respectively to develop to the solution of complex engineering problems.],
  [*PO2*\ Problem Analysis (PA)], par(justify: true, leading: 5.17pt)[Identify, formulate, review research literature and analyze complex engineering problems reaching substantiated conclusions with consideration for sustainable development. (WK1 to WK4)],
  [*PO3*\ Design/Development of Solutions (DS)], par(justify: true, leading: 5.17pt)[Design creative solutions for complex engineering problems and design/develop systems/components/processes to meet identified needs with consideration for the public health and safety, whole-life cost, net zero carbon, culture, society and environment as required. (WK5)],
  [*PO4*\ Conduct Investigations of Complex Problems (IP)], par(justify: true, leading: 5.17pt)[Conduct investigations of complex engineering problems using research-based knowledge including design of experiments, modelling, analysis & interpretation of data to provide valid conclusions. (WK8).],
  [*PO5*\ Engineering Tool Usage (ETU)], par(justify: true, leading: 5.17pt)[Create, select and apply appropriate techniques, resources and modern engineering & IT tools, including prediction and modelling recognizing their limitations to solve complex engineering problems. (WK2 and WK6)],
  [*PO6*\ The Engineer and The World (EW)], par(justify: true, leading: 5.17pt)[Analyze and evaluate societal and environmental aspects while solving complex engineering problems for its impact on sustainability with reference to economy, health, safety, legal framework, culture and environment. (WK1, WK5, and WK7).],
  [*PO7*\ Ethics (Eth)], par(justify: true, leading: 5.17pt)[Apply ethical principles and commit to professional ethics, human values, diversity and inclusion; adhere to national & international laws. (WK9)],
  [*PO8*\ Individual and Collaborative Team work (ICTw)], par(justify: true, leading: 5.17pt)[Function effectively as an individual, and as a member or leader in diverse/multi-disciplinary teams.],
  [*PO9*\ Communication (Cm)], par(justify: true, leading: 5.17pt)[Communicate effectively and inclusively within the engineering community and society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations considering cultural, language, and learning differences],
  [*PO10*\ Project Management and Finance (PM)], par(justify: true, leading: 5.17pt)[Apply knowledge and understanding of engineering management principles and economic decision-making and apply these to one's own work, as a member and leader in a team, and to manage projects and in multidisciplinary environments.],
  [*PO11*\ Life-long Learning (LL)], par(justify: true, leading: 5.17pt)[Recognize the need for, and have the preparation and ability for: \ i) Independent and life-long learning \ ii) Adaptability to new and emerging technologies and \ iii) Critical thinking in the broadest context of technological change. (WK8)]
)
]]

#pagebreak()

#text(size: 14pt, weight: "bold")[PROGRAM SPECIFIC OUTCOMES (PSOs)]\
Students of the program will:
#text(size:11pt)[
#table(
  columns: (1.7cm, 1fr),
  stroke: 0.5pt + black,
  align: (center + horizon, left + horizon),

  // Data Rows
  [*PSO I*], [Exhibit proficiency in the field of *Artificial Intelligence* by *developing intelligent systems*],
  [*PSO II*], [Be accomplished in the field of *data analytics, statistical programming languages and Machine learning*]
)]

#pagebreak()