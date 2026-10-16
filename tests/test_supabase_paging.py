"""
Collection reads page past Supabase's 1000-row limit.

No Supabase access: the client is replaced with a fake table that serves
rows the way PostgREST does (ordered, at most 1000 per request).
"""

from backend.database import supabase as db


class FakeQuery:
    def __init__(self, rows, log):
        self.rows, self.log = rows, log
        self.order_by = self.bounds = None

    def select(self, *_):
        return self

    def order(self, column):
        self.order_by = column
        return self

    def range(self, start, end):
        self.bounds = (start, end)
        return self

    def execute(self):
        self.log.append(self.bounds)
        rows = sorted(self.rows, key=lambda r: r[self.order_by])
        start, end = self.bounds if self.bounds else (0, len(rows) - 1)
        page = rows[start:min(end + 1, start + 1000)]
        return type("Response", (), {"data": page})()


class FakeClient:
    def __init__(self, rows):
        self.rows, self.log = rows, []

    def table(self, _name):
        return FakeQuery(self.rows, self.log)


def test_reads_all_rows_across_pages(monkeypatch):
    fake = FakeClient([{"complaint_id": i} for i in range(2500, 0, -1)])
    monkeypatch.setattr(db, "supabase", fake)
    rows = db.get_complaints()
    assert [r["complaint_id"] for r in rows] == list(range(1, 2501))
    assert fake.log == [(0, 999), (1000, 1999), (2000, 2999)]


def test_exact_page_multiple_needs_one_empty_page(monkeypatch):
    fake = FakeClient([{"case_id": i} for i in range(1, 2001)])
    monkeypatch.setattr(db, "supabase", fake)
    assert len(db.get_cases()) == 2000
    assert len(fake.log) == 3


def test_small_table_is_one_request(monkeypatch):
    fake = FakeClient([{"topic_id": i} for i in range(1, 6)])
    monkeypatch.setattr(db, "supabase", fake)
    assert len(db.get_topics()) == 5
    assert fake.log == [(0, 999)]


def test_case_original_texts_uses_first_complaint(monkeypatch):
    fake = FakeClient([
        {"complaint_id": 3, "case_id": 1, "complaint_text": "later report", "created_at": "2026-01-02T00:00:00"},
        {"complaint_id": 1, "case_id": 1, "complaint_text": "First report.", "created_at": "2026-01-01T00:00:00"},
        {"complaint_id": 2, "case_id": None, "complaint_text": "unassigned", "created_at": "2026-01-01T00:00:00"},
        {"complaint_id": 4, "case_id": 2, "complaint_text": "", "created_at": "2026-01-01T00:00:00"},
        {"complaint_id": 5, "case_id": 2, "complaint_text": "Second case.", "created_at": "2026-01-03T00:00:00"},
    ])
    monkeypatch.setattr(db, "supabase", fake)
    assert db.get_case_original_texts() == {1: "First report.", 2: "Second case."}
