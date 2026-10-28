= Proposed System

== Introduction

This chapter gives an overview of InsightDesk: the stages a complaint passes through, the system architecture, the data each stage reads and writes, and the design principles that keep the language model's role bounded and auditable. Chapter 4 then describes each phase in detail.

== System Overview

InsightDesk runs nine phases organised in four stages. @fig:flowchart shows the path of one complaint through them.

#figure(
  image("/content/images/flowchart.png", width: 78%),
  caption: [Flowchart of the InsightDesk pipeline ($t_"low"$ = 0.40 for app reviews and chat, 0.26 for tickets and bug reports)],
) <flowchart>

+ *Intake and grouping (phases 1–4).* Each complaint is cleaned and embedded, and its closest existing cases are retrieved. Its best similarity score decides whether it joins a case automatically, opens a new case, or goes to the LLM judge, which joins it to a candidate, opens a new case, or marks it as too vague to place.
+ *Case upkeep (phases 5–6).* Every six hours a re-joining pass merges cases that describe one problem. Each case receives a sentiment label, a topic and the department responsible for that topic.
+ *Incident signals (phases 7–8).* Complaint counts per case in six-hour windows feed a Poisson CUSUM spike detector, for each case and for groups of related cases. Complaints too vague to join any case feed a separate alarm per product.
+ *Action (phase 9).* A case with at least three reports or an active spike becomes eligible for escalation. An LLM writes a root-cause explanation grounded in the case's complaints, and an email reaches the department only after an operator approves it.

@tbl:stages summarises when each part of the pipeline runs and what triggers it.

#figure(
  table(
    columns: (3cm, 1fr, 3cm),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*When*], [*What runs*], [*Trigger*]),
    [Each complaint], [Cleaning, retrieval, decision band, LLM judge, sentiment of a new case, window count], [Customer submits],
    [Each dashboard view], [Spike detection (cases and alert groups), vague-complaint alarm, escalation policy], [Page load],
    [Every 6 hours], [Boilerplate list refresh, re-joining pass, topic re-clustering when needed], [Automatic scheduler],
    [On request], [Root-cause explanation, escalation email], [Operator action],
  ),
  caption: [When each part of the pipeline runs],
) <stages>

== System Architecture

@fig:architecture shows the architecture of the nine phases and the two stores they share. Supabase (a hosted PostgreSQL database) holds complaints, cases with their counts, users, topics and departments, the six-hour window counts per case, the vague pool per product, root-cause reports and approved escalations. Pinecone (a vector database) holds up to five exemplar vectors per case, which the retrieval phase searches and the re-joining phase moves when two cases merge.

#figure(
  image("/content/images/architecture.png", width: 100%),
  caption: [System architecture: nine phases over two stores],
) <architecture>

The deployed application has three parts. A React web application provides the customer complaint form and the operator dashboard. A FastAPI backend runs the pipeline and exposes it through a REST API. External services provide storage (Supabase, Pinecone), the language model (gpt-oss-120b through the Groq API) and email (SMTP). Sign-in uses Supabase authentication; dashboard pages need an administrator role that users cannot give themselves.

== Methodology Overview

@fig:methodology expands the architecture into the methodology: the input and output types of each phase, the rule it applies, and how each decision updates the stored state.

#figure(
  image("/content/images/methodology.png", width: 100%),
  caption: [Methodology: rules, data flows and state updates of the nine phases],
) <methodology>

Three outcomes of the grouping stage update the state differently. A *join* increases the case's report count and its count in the current six-hour window, and stores the complaint as a new exemplar if it is worded differently from the existing ones. A *new case* starts with one report and the complaint as its only exemplar. A *vague* complaint is added to its product's vague pool and is never grouped. Sentiment and topic labels are attached to cases for the dashboard and routing; they are never used in grouping decisions.

== Running Example

Throughout this report a running example follows the complaint "Can't log in since the update, the OTP never arrives". After cleaning, it is embedded and compared with existing cases; suppose the closest case is "OTP not received on login" with a similarity of 0.71, an illustrative value. Because 0.71 lies between the two thresholds, the LLM judge decides: the new complaint names the same feature and the same failure, so it joins that case. A complaint saying "login is slow" would share the topic but not the symptom, and would open a new case. If five such OTP complaints arrive in one six-hour window against a usual rate of about 0.1 per window, the spike detector raises an alarm and the case becomes eligible for escalation.

== Design Principles

The design keeps the language model's role small, checkable and safe:

- *Bounded LLM use.* The judge sees at most five candidate cases, decides only inside the calibrated similarity band, and makes at most one decision per complaint, never pairwise comparisons.
- *Safe failure.* A failed, timed-out or malformed judge answer opens a new case and never merges two complaints.
- *Stable online cases.* A decision, once made, is changed only by a recorded re-joining merge, so case identifiers persist and cases can carry counts, spike history and an escalation record.
- *Human approval.* No escalation email leaves the system without an operator's approval.
- *Reproducibility.* Every judge decision is made at temperature 0 and cached, so a replay of the same complaints gives the same decisions.

== Summary

InsightDesk turns each arriving complaint into a decision about which problem it reports, keeps the resulting cases up to date, and builds spike, vague-complaint and escalation signals on top of them. The next chapter describes each of the nine phases, with the exact rules, thresholds and equations they use.
