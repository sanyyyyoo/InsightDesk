# InsightDesk API tests (Postman)

`InsightDesk.postman_collection.json`: 21 requests, 60 test assertions, in 6 folders.

| Folder | What it checks |
|---|---|
| 1. Health | API is up, responds within 5 s |
| 2. Ingest (`/analyze`) | A complaint creates or joins a case; an identical complaint is marked duplicate and joins the same case; a complaint longer than 512 tokens does not crash (regression test); missing or wrong-typed fields return 422 |
| 3. Cases and dashboard | Overview, case list (merged cases hidden), case intelligence, complaint list, topics; unknown case returns 404 |
| 4. Spikes and alerts | Case spikes, alert-group spikes, vague summary, unassigned-complaint (outage) alarm with its hedged message |
| 5. Re-joining | Pass reports its feature flag; when disabled it merges nothing |
| 6. Escalation and RCA | A non-eligible case returns 409 with the policy; unknown case and unknown RCA return 404 |

## Run it

Only against a LOCAL backend connected to a TEST Supabase project and Pinecone index: the ingest
requests write complaints and cases. Never point it at production.

1. Start the backend with the test project's `.env`: `python -m uvicorn backend.main:app --port 8000`.
2. Postman: Import -> `InsightDesk.postman_collection.json` -> Run collection (keep the folder order:
   later requests use the case created in folder 2).
   Command line: `npx newman run postman/InsightDesk.postman_collection.json`.
3. Change `baseUrl` (collection variables) if the backend runs elsewhere.

Not included on purpose: a forced escalation (`force=true`) sends a real email.
Rebuild the file after editing tests: `python postman/build_collection.py`.
