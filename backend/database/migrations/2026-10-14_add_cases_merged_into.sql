-- Case re-joining (backend/services/rejoin.py): an absorbed case keeps its row for the audit trail
-- and points to the case it was merged into; get_cases() hides such rows.
alter table cases add column if not exists merged_into bigint references cases(case_id) on delete set null;
create index if not exists cases_merged_into_idx on cases (merged_into);
