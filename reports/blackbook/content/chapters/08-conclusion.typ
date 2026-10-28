= Conclusion and Future Scope

== Conclusion

This project built InsightDesk, a system that turns raw customer complaints into stable problem cases as they arrive and builds incident signals on top of them. Retrieval over diverse case exemplars narrows each complaint to at most five candidate cases, two thresholds calibrated from labelled pairs settle the clear matches and clear non-matches, and an open-weight language model decides only the uncertain complaints, once each, with a failure never merging two complaints. A re-joining pass every six hours merges cases that the online decisions split.

On 338 human-labelled reviews of six help-desk products, InsightDesk reaches pairwise precision 0.83, recall 0.35 and F1 0.49, the highest of every method tested on the same data: it more than doubles the precision of the project's earlier cross-encoder pipeline (0.38) and outperforms published grouping methods and topic models, whose F1 is at most 0.25. A lower threshold for short-text channels made grouping both more precise and cheaper, and the same upper threshold transfers without retuning to Bugzilla bug reports (F1 0.78), unseen products (case precision 0.92), an unseen company (0.89) and IT tickets (0.90).

Small-count statistics make incident detection work at the volumes a support desk actually sees: a Poisson CUSUM detects 76–91% of simulated outbreaks on bug-report streams at under one false alarm per 100 windows, where the z-score rule of feedback tools detects none, and a separate alarm detects every outage of ten or more complaints that customers describe only vaguely. Each case carries sentiment, a topic and a department, and every escalation is explained from the customers' own words and approved by a person before it reaches a department.

The objectives set in Chapter 1 were met: complaints are grouped into problem cases online with a bounded LLM judge; sentiment and topics are computed and topics are routed to departments; spikes and vague-complaint surges are detected; root causes are explained with human-approved escalation; and every component was evaluated against human and independent labels under rules written before each test. The main limitation is recall on very short reviews, and department routing by keyword rules is the weakest step.

== Future Scope

The work can be extended in several directions:

- *Deployment.* Package the application with Docker and deploy it on a cloud platform such as Google Cloud or Microsoft Azure.
- *Privacy.* Host the open-weight language model locally, so that no complaint leaves the company, and remove personal details from complaints before any model call.
- *Learning from operators.* Use the corrections operators already make in the dashboard, such as overriding a department or rejecting a suggested escalation, to calibrate the thresholds for each company automatically.
- *Better routing.* Replace the keyword rule table with a learned or LLM-based mapping from topics to departments.
- *Robustness of the judge.* Test the judge with other models, and keep complaints that describe two problems out of case exemplars.
- *Statistics.* Compare the CUSUM with a Bayesian changepoint detector, and model the burstiness of real complaint counts explicitly.
- *Wider use.* Add per-user submission limits, support multilingual complaints, and create tickets automatically in tools such as Jira for approved escalations.
