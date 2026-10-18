# InsightDesk – React frontend

Customer complaint portal + operator dashboard for the InsightDesk FastAPI
backend. Same colour theme as the earlier Streamlit dashboard.

## Run

Requires Node 20+ (team setup: `D:\tools\node`).

```bash
cd web
npm install
cp .env.example .env.local      # fill in VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
npm run dev                      # http://localhost:5173 (backend on http://127.0.0.1:8000)
```

Sample-data mode (no backend, no Supabase, fake admin session):

```bash
npm run dev:mock
```

Checks: `npm run typecheck`, `npm test`, `npm run build`.

## Configuration (`web/.env.local`)

| Variable | Meaning |
|---|---|
| `VITE_API_URL` | FastAPI base URL (default `http://127.0.0.1:8000`) |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | Supabase project URL and **anon** key (never the service-role key) |
| `VITE_REQUIRE_ADMIN_ROLE` | `true`: admin portal needs `app_metadata.role = "admin"`; `false`: any signed-in user (local dev only) |
| `VITE_USE_MOCKS` | `true`: built-in sample data |

Backend side: the API allows `http://localhost:5173` via `CORS_ORIGINS`. Set
`ADMIN_AUTH_REQUIRED=true` in the backend `.env` to enforce the admin role on
`/dashboard` and `/chat` server-side as well (the browser check alone is not a
security boundary).

Make a user an admin (Supabase SQL editor):

```sql
update auth.users set raw_app_meta_data = raw_app_meta_data || '{"role":"admin"}' where email = 'operator@example.com';
```

## Pages

| Route | Who | What |
|---|---|---|
| `/login` | everyone | sign in / create account (Supabase email + password) |
| `/submit` | signed-in customers | report a problem (`POST /analyze`); shows whether it joined an existing case |
| `/admin` | admins | overview: KPIs, daily volume, spiking cases, sentiment-model benchmarks |
| `/admin/cases` | admins | searchable, filterable, sortable case list (filters kept in the URL) |
| `/admin/cases/:id` | admins | complaints, spike status, RCA, confirmed escalation (`POST /dashboard/cases/{id}/escalate`) |
| `/admin/incidents` | admins | spiking cases by z-score (spike > 2, critical > 3) |
| `/admin/sentiment` | admins | sentiment computed from live case data (the Streamlit page used mock data) |
| `/admin/topics` | admins | BERTopic topics, departments, representative cases |
| `/admin/assistant` | admins | chat with the LangGraph assistant (`POST /chat`) |

## Robustness

- Typed API client: timeouts, bearer token, FastAPI `detail` messages surfaced, network errors mapped to a clear message.
- React Query: caching, de-duplicated requests, retries only for network/timeout/5xx (max 2).
- Every view has loading, empty and error states (with Retry); an error boundary contains render errors per page.
- Irreversible actions (escalation email) need confirmation and show the backend's reason on failure.
- Admin pages and the charts library are code-split, so the customer portal loads less code.

## Known backend gaps (not frontend bugs)

- No endpoint to *generate* an RCA – only to read one. Escalation needs an RCA, so cases without one cannot be escalated from the UI yet.
- Case sentiment comes from the case's first complaint only.
- No endpoint for a customer's own past complaints – the portal shows this session's reports.
