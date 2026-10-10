-- R1 dedup marks complaints with no concrete symptom ("app is useless") as vague.
-- They keep their own case, stay out of RCA/escalation, and are counted on
-- /dashboard/vague-summary. Run once on every existing company database.
alter table cases add column if not exists is_vague boolean not null default false;
