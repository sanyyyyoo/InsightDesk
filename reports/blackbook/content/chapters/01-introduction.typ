= Introduction

== Introduction

Software-as-a-service companies support their customers through help-desk platforms such as Vision Helpdesk, Zendesk, Freshdesk, Intercom and ServiceNow. Complaints reach these platforms from many channels: app-store reviews, support tickets, live chat and web forms. A support desk that serves thousands of customers receives a steady stream of such complaints, and a large share of them describe the same few underlying problems in different words. One customer writes "I never get the OTP when I log in", another "the verification code doesn't arrive", and a third "can't sign in, no SMS". To a human reader these are one problem; to most support software they are three unrelated tickets.

The operational questions a support team must answer are about problems, not tickets: how many customers are affected by the same issue, whether it is suddenly growing, what is likely causing it, and which department must act. Answering them requires a step that most tools skip or hide: deciding, as each complaint arrives, whether it reports a problem that is already known or a new one. This project, *InsightDesk*, builds that step and the incident signals that depend on it.

InsightDesk groups raw complaints into *problem cases* as they arrive. A case is a set of complaints that report the same specific problem, such as "the OTP never arrives", rather than a broad theme such as "login". On top of the cases, the system counts reports per case over time, detects sudden spikes, raises an alarm when vaguely worded complaints surge, labels each case with sentiment, topic and department, writes an evidence-grounded explanation of the likely cause, and escalates the case to the responsible department only after a person approves it.

== Background and Context

=== The support-desk setting

Help-desk software sits between a company and its customers. When a release breaks a feature, complaints arrive within hours, but they arrive one at a time, through different channels and in the customers' own words. Each agent sees only the tickets assigned to them, so the same problem is triaged again and again, and the size of the problem becomes visible only when it is already large. Commercial voice-of-customer tools add dashboards and alerts, but they group feedback by tag or theme and detect anomalies with statistics designed for large counts @sentisum2025.

=== Why grouping complaints is hard

Three properties of complaint text make the grouping step difficult:

- *Complaints are short and noisy.* On the Google Play reviews used in this project the median review has 21 words. Two reports of one problem often share almost no vocabulary, while reports of different problems in the same feature share many words ("login fails after update" and "login is slow").
- *Decisions must be online and stable.* Complaints arrive continuously, and each must be placed when it arrives. A case that changed its members whenever the input order changed could not carry counts, a spike history or an escalation record.
- *A wrong merge is costly.* Merging two different problems inflates a case, hides the second problem and can send a false escalation to the wrong department, while a missed duplicate only leaves two smaller cases.

=== Societal, safety and sustainability context

Customer-facing software now carries everyday activities such as banking, payments, travel, education, healthcare portals and government services. When such software fails, the people affected are often those least able to work around it, and the first signal of the failure is usually a rising number of complaints. Grouping complaints by problem and detecting spikes early shortens the time between the first reports and a fix, which reduces the harm a silent outage causes to users who depend on the service.

The design of InsightDesk also reflects ethical and safety considerations. No escalation leaves the system without a person approving it, so an automated mistake cannot reach a department on its own. Root-cause explanations are restricted to evidence found in the customers' own complaints and list the complaints they rely on, so a reviewer can check every claim. Complaint text is personal data; the language model used is open-weight and can be hosted privately by a company, and removing personal details before any model call is listed as future work (Chapter 8).

From a sustainability point of view, the pipeline is designed to use large language models sparingly. Cheap similarity checks settle every clear case, and the language model is consulted only for uncertain complaints, at most once per complaint; every decision is cached so it is never recomputed. Embedding a complaint takes about 21 ms on an ordinary laptop CPU, and the whole pipeline runs without a GPU. Grouping duplicates also reduces repeated manual triage work for support agents.

== Motivation

The project was motivated by the support setting of Vision Helpdesk, a help-desk software company, and by a gap visible in existing tools. Topic models and keyword rules mix different problems that share vocabulary, a single similarity threshold either merges unrelated complaints or misses paraphrases, and per-tag z-score alerts cannot detect a new problem that grows from zero or one complaint per window. Large language models can judge whether two complaints describe the same problem, but calling one on every pair of complaints is slow, costly and hard to audit. The motivation was to combine cheap, calibrated similarity with a bounded language-model decision, and to build incident detection on top of the resulting cases.

== Problem Statement

Help-desk and customer-support platforms, and the companies that use them, receive complaints from app reviews, support tickets, chat and web forms. The same problem is reported many times in different words, so agents triage it again and again, and no one sees how many customers a single problem affects. Existing tools group complaints by theme ("login") rather than by problem ("the OTP never arrives"): keyword rules and topic models mix different problems, and a single similarity threshold either merges unrelated complaints or misses paraphrases. Feedback tools flag spikes with z-scores on whole categories, which miss a new problem growing from a low base.

There is a need for a system that groups raw complaints into problem-level cases as they arrive with high precision, tracks each case's volume to raise incidents early, adds sentiment, topic and root cause, and routes each incident to the responsible department after a person approves it.

== Objectives

The objectives of the project are:

+ To group duplicate complaints into problem-level cases as they arrive, using similarity retrieval and a large-language-model judge only for uncertain matches.
+ To measure the sentiment of each case using a RoBERTa sentiment model.
+ To discover complaint topics automatically with BERTopic and route each topic to the responsible department.
+ To detect sudden spikes in complaint volume with a Poisson CUSUM, and to raise an alarm on surges of vague complaints that fit no case.
+ To explain the likely root cause of an incident with a language model grounded in the complaints, with a person approving every escalation.
+ To evaluate every component against human labels and independent benchmarks, with rules for each test written before the test was run.

== Scope of the Project

InsightDesk targets English-language customer complaints about software products, received as free text through a web form, app reviews, chat or tickets. It works from the complaint text alone and does not require system logs or monitoring data. The product field is optional: when a complaint names a product, it is compared only with cases of that product.

The system covers intake, grouping, case upkeep, sentiment, topics, department routing, spike detection, the vague-complaint alarm, root-cause explanation and human-approved email escalation, together with a web dashboard for operators and a complaint form for customers. Multilingual complaints, automatic ticket creation in external tools and learning from operator corrections are outside the current scope and are discussed as future work.

== Organisation of the Report

The rest of this report is organised as follows. Chapter 2 reviews related work and identifies the research gaps. Chapter 3 presents the proposed system and its architecture. Chapter 4 describes each of the nine phases of the pipeline in detail, with the rules and equations it uses. Chapter 5 describes the implementation: the hardware and software used, the modules, the data stores, the dashboard and the testing. Chapter 6 describes the datasets, the credibility of their labels and the evaluation protocol. Chapter 7 presents and discusses the results, and Chapter 8 concludes the report and outlines future work.
