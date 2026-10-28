// Long tables may continue on the next page (header row repeats).
#show figure: set block(breakable: true)

= Implementation

== Introduction

This chapter describes how InsightDesk was built: the hardware and software used, the backend modules that implement the nine phases, the data stores, the REST API, the web application, the scheduled maintenance, the safety measures for testing and the software tests.

== Hardware Used

The whole system was developed and tested on an ordinary laptop, described in @tbl:hardware. No GPU is needed: the sentence encoder, the sentiment model and topic modelling run on the CPU, and the large language model runs on the Groq cloud service.

#figure(
  table(
    columns: (4cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Component*], [*Specification of the development machine*]),
    [Processor], [Intel Core i5-1135G7 (11th generation), 4 cores, 2.40 GHz],
    [Memory], [8 GB RAM (7.7 GB usable)],
    [Graphics], [Intel Iris Xe and NVIDIA GeForce MX330 (not used by the pipeline)],
    [Operating system], [Microsoft Windows 10 Pro],
    [Network], [Internet connection for Supabase, Pinecone, Groq and SMTP],
  ),
  caption: [Hardware used for development and testing],
) <hardware>

Embedding one complaint takes about 21 ms on this CPU, and an LLM judge decision takes 1.34 s at the median (2.09 s at the 90th percentile), almost all of it spent waiting for the remote model.

== Software Used

@tbl:software lists the main software, libraries and services, with the versions used in the project.

#figure(
  table(
    columns: (3.6cm, 4.4cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Area*], [*Software (version)*], [*Used for*]),
    [Language], [Python 3.13; TypeScript 5.6], [Backend and experiments; web application],
    [Web API], [FastAPI 0.141, Uvicorn 0.53, Pydantic 2.13], [REST API and request validation],
    [Embeddings], [sentence-transformers 6.1 (all-MiniLM-L6-v2), PyTorch 2.14 (CPU)], [384-dimensional complaint embeddings],
    [Sentiment], [Hugging Face Transformers 5.17 (twitter-roberta-base-sentiment-latest)], [Case sentiment],
    [Topics], [BERTopic 0.17.4, UMAP 0.5.12, HDBSCAN 0.8.44, scikit-learn 1.9], [Topic discovery and keywords],
    [Language model], [gpt-oss-120b via the Groq API (groq 0.37); optional local model through Ollama], [LLM judge, case re-joining, root-cause explanation],
    [Assistant], [LangChain and LangGraph], [Dashboard assistant that answers questions from case data],
    [Database], [Supabase (PostgreSQL), supabase-py 2.31], [Complaints, cases, windows, topics, root causes, escalations],
    [Vector store], [Pinecone (client 10.0)], [Case exemplar vectors],
    [Authentication], [Supabase Auth, PyJWT 2.15], [Sign-in and role checks],
    [Email], [SMTP (Python smtplib)], [Escalation emails],
    [Front end], [React 19, Vite 6, React Router 7, Recharts 2, supabase-js 2], [Customer form and operator dashboard],
    [Data analysis], [pandas 3.0, NumPy 2.5], [Experiments and evaluation],
    [Testing], [pytest, Postman / Newman], [Unit, equivalence and API tests],
    [Tools], [Git and GitHub, VS Code, Node.js 24], [Version control and development],
  ),
  caption: [Software, libraries and services used],
) <software>

== Backend Modules

The backend is a Python FastAPI service. Each phase of the pipeline is implemented by one module, listed in @tbl:modules.

#figure(
  table(
    columns: (6.2cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Module (backend/)*], [*Responsibility*]),
    [`routers/complaints.py`], [Accepts a complaint from a signed-in customer (`POST /analyze`)],
    [`services/duplicate_service.py`], [Runs the intake pipeline for one complaint, end to end],
    [`services/boilerplate.py`], [Phase 1: boilerplate detection (every 6 h) and removal at intake],
    [`services/preprocess.py`], [Phase 1: lower-casing, punctuation and stop-word removal],
    [`services/embedding_service.py`], [Phase 2: MiniLM embeddings and the Pinecone index],
    [`services/dedup_r1.py`], [Phases 2–4: exemplar retrieval, decision band and LLM judge],
    [`services/rejoin.py`], [Phase 5: case re-joining pass],
    [`services/sentiment/`], [Phase 6: RoBERTa sentiment (DistilBERT kept as an alternative adapter)],
    [`services/clustering_service.py`], [Phase 6: BERTopic topics and re-clustering rules],
    [`services/department_service.py`], [Phase 6: department rule table],
    [`services/spike_detection.py`], [Phase 7: zero-filled windows and Poisson CUSUM],
    [`services/alert_groups.py`], [Phase 7: alert groups of related cases],
    [`services/unassigned_spikes.py`], [Phase 8: vague-complaint alarm per product],
    [`services/escalation_policy.py`], [Phase 9: escalation eligibility],
    [`services/rca_service.py`], [Phase 9: grounded root-cause explanation],
    [`services/email_service.py`], [Phase 9: escalation email and escalation record],
    [`llm/provider.py`], [LLM access (Groq or local), JSON mode, decision cache],
    [`chatbot/`], [Dashboard assistant with tools for cases, complaints, topics and root causes],
    [`database/supabase.py`], [All database reads and writes],
  ),
  caption: [Backend modules and their responsibilities],
) <modules>

== Data Storage

=== Relational data in Supabase

@tbl:schema lists the database tables. Cases carry their report count, the users who reported them, sentiment, topic, a vague flag, and, after re-joining, the case they were merged into. Spike status is computed from the six-hour window counts, which form each case's spike history.

#figure(
  table(
    columns: (3.8cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Table*], [*Contents*]),
    [`complaints`], [Complaint text, cleaned text, user, product, source channel, rating, case, duplicate flag, time],
    [`cases`], [Founding (representative) text, report count, users, sentiment and confidence, topic, vague flag, merged-into case, spike status],
    [`complaint_windows`], [Counted complaints per case per six-hour window],
    [`case_history`], [Report count of a case over time],
    [`topics`], [Topic name, keywords, department, operator override of the department],
    [`clustering_metadata`], [When and why topics were last recomputed],
    [`case_rca`], [Root-cause reports: cause, affected segment, action, severity, confidence, evidence, model],
    [`case_escalations`], [Approved escalations: case, department, receiver, root-cause report, time],
  ),
  caption: [Database tables in Supabase],
) <schema>

=== Vectors in Pinecone

Each case has up to five exemplar vectors in a Pinecone index, with the identifiers `<case_id>` and `<case_id>:<k>`. Their metadata hold the case identifier, the founding complaint and its text, the vague flag and the product, so that a query can be filtered by product and the founding text can be shown to the LLM judge without a database lookup.

== REST API

The backend exposes the endpoints in @tbl:api. The complaint endpoint requires a signed-in user; dashboard endpoints require the administrator role when authentication is enforced.

#figure(
  table(
    columns: (5.6cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Endpoint*], [*Purpose*]),
    [`POST /analyze`], [Submit a complaint; returns its case and how it was decided],
    [`GET /dashboard/overview`], [Headline counts for the overview page],
    [`GET /dashboard/cases`], [Case list (merged cases hidden)],
    [`GET /dashboard/cases/{id}/intelligence`], [Case details, spike status and escalation eligibility],
    [`GET /dashboard/complaints`, `/case-texts`], [Complaints and case texts],
    [`GET /dashboard/topics`, `/clusters`], [Topics and clustering information],
    [`GET /dashboard/spikes`, `/group-spikes`], [Spikes of cases and of alert groups],
    [`GET /dashboard/vague-summary`, `/unassigned-spikes`], [Vague complaints per product and the vague-complaint alarm],
    [`POST /dashboard/rejoin`], [Run one re-joining pass on demand],
    [`GET /dashboard/rca/{id}`, `POST /dashboard/cases/{id}/rca`], [Read or generate a root-cause explanation],
    [`POST /dashboard/cases/{id}/escalate`], [Escalate a case after approval (refused with the reason if not eligible)],
    [`POST /chat`], [Ask the dashboard assistant a question],
  ),
  caption: [REST API endpoints],
) <api>

== Web Application

The React application has a complaint form for customers and a dashboard for operators. A customer signs in, writes a complaint and optionally names the product; the reply says whether the complaint opened a new case, joined an existing one or was recognised as a recent repeat of their own report. The operator dashboard has pages for an overview, cases, incident response, sentiment, topics and an assistant. @fig:ui-overview, @fig:ui-cases and @fig:ui-incidents show three of them, captured in the application's sample-data mode, which displays example data without contacting the backend.

#figure(
  image("/content/images/ui-overview.png", width: 100%),
  caption: [Overview page of the operator dashboard (sample-data mode)],
) <ui-overview>

#figure(
  image("/content/images/ui-cases.png", width: 100%),
  caption: [Cases page: each case groups the complaints about one problem (sample-data mode)],
) <ui-cases>

#figure(
  image("/content/images/ui-incidents.png", width: 100%),
  caption: [Incident response page: case spikes, alert groups and the vague-complaint alarm (sample-data mode)],
) <ui-incidents>

The assistant page answers questions such as "what is the root cause of case 12?" by calling tools that read cases, complaints, topics and root-cause reports. Its instructions forbid it from stating facts that the retrieved data do not support.

== Scheduled Maintenance

A scheduler inside the API runs every six hours without operator action. It refreshes the boilerplate list from the most recent complaints, runs one re-joining pass, and re-clusters topics when its own rule says so (first run, 20% more cases, more than 15% outliers, or a scheduled refresh). A failure is logged and retried at the next interval. The only manual step in the pipeline, by design, is approving an escalation.

== Configuration and Safety

All settings come from environment variables, so the same code runs in development, testing and production. The main switches are the LLM provider and model, the decision thresholds, re-joining, the vague-complaint alarm, the decision cache and the boilerplate settings; re-joining and the vague alarm are on by default.

A separate test environment, with its own Supabase project and Pinecone index, holds 393 real Play Store reviews grouped by the final pipeline. Its launcher refuses to start if it is pointed at the production project, and email is disabled in it, so demonstrations and API tests can never write to production data or send a real escalation. A demonstration script sends a burst of six differently worded reports of one problem and shows them land in one case, trigger a CUSUM spike and become eligible for escalation.

== Handling of Edge Cases

@tbl:edge-cases lists how the system handles the situations met in testing and the limits that remain.

#figure(
  table(
    columns: (4.4cm, 1fr, 2.2cm),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Situation*], [*What InsightDesk does*], [*Status*]),
    [Same user repeats a problem within 24 h], [Attached to the case but not counted again], [Built],
    [Same user repeats after 24 h], [Counted again: still affected a day later], [Built],
    [Very vague complaint ("app is useless")], [Joins no case; counted by the vague-complaint alarm], [Built],
    [Too short, or empty after cleaning], [Rejected with a clear message (minimum 10 characters)], [Built and tested],
    [Longer than 5,000 characters], [Truncated to 5,000 characters], [Built and tested],
    [LLM service down or slow], [Never merges on failure; opens its own case; re-joining can merge it later], [Built],
    [No product given], [All complaints treated as one stream], [Tested],
    [Problem split across two cases], [Re-joining merges them; alert groups catch the burst meanwhile], [Built and tested],
    [Brand-new problem with a sudden burst], [Judged against a low prior rate, so it alerts on the first day], [Built and tested],
    [One complaint mentions two problems], [Joins the closer problem; can occasionally link two cases], [Known limit],
    [Very busy case rising slightly], [CUSUM looks for +1 report per window, so busy cases are relatively sensitive], [Known limit],
    [Many accounts posting the same text], [Sign-in required; a per-user limit is not built yet], [Open],
    [Non-English complaints], [Not evaluated], [Open],
  ),
  caption: [Handling of edge cases],
) <edge-cases>

== Testing

The software was tested at three levels.

- *Unit tests (pytest).* 46 automated tests cover authentication and roles, request validation (including truncation of long complaints), the dashboard's root-cause endpoints, paging of database reads, the channel-specific lower threshold, boilerplate suppression and the LLM decision cache.
- *Equivalence tests.* Separate scripts replay the experiments' saved decisions through the application's own code, without network or LLM calls, and require identical results: the grouping code builds exactly the same cases as the tested pipeline on the Play Store halves and a Firefox sample (0 complaints assigned differently), the re-joining code makes the same merges, the alert groups and the vague-complaint alarm behave as tested, and the boilerplate module cleans all 488 synthetic complaints exactly as the tested method.
- *API tests (Postman).* A Postman collection of 21 requests with 60 assertions, in six folders, checks the running API against the test environment: health, complaint intake, cases and dashboard, spikes and alerts, re-joining, and escalation with root causes. A forced escalation is deliberately excluded because it would send a real email.

An end-to-end acceptance test replayed 32 incidents built from real Firefox reports through the whole pipeline with re-joining: 94% of them became eligible for escalation within 12 hours, with no false alarms on streams without an incident.

== Summary

InsightDesk is implemented as a FastAPI backend with one module per phase, a Supabase database and a Pinecone vector index, an LLM accessed through Groq, and a React web application. It runs on a CPU-only laptop, separates test data from production, and is covered by unit, equivalence and API tests.
