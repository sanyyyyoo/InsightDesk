"""Builds InsightDesk.postman_collection.json (Postman v2.1) next to this file.

  python postman/build_collection.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def req(name, method, path, tests, body=None, desc=""):
    url = {"raw": "{{baseUrl}}" + path, "host": ["{{baseUrl}}"],
           "path": [p for p in path.split("?")[0].split("/") if p]}
    r = {"name": name,
         "request": {"method": method,
                     "header": [{"key": "Content-Type", "value": "application/json"}] if body is not None else [],
                     "url": url, "description": desc},
         "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests.strip().split("\n")}}]}
    if body is not None:
        r["request"]["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2), "options": {"raw": {"language": "json"}}}
    return r


OK = 'pm.test("status 200", () => pm.response.to.have.status(200));\npm.test("JSON body", () => pm.response.to.be.json);'
FAST = '\npm.test("responds within 5 s", () => pm.expect(pm.response.responseTime).to.be.below(5000));'
LONG = ("The app keeps crashing when I open the ticket view after the last update. " * 60).strip()

ANALYZE_OK = OK + """
const r = pm.response.json();
pm.test("has complaint_id, case_id, dedup_route, is_duplicate", () => {
  ["complaint_id", "case_id", "dedup_route", "is_duplicate"].forEach(k => pm.expect(r).to.have.property(k));
});
pm.test("dedup_route is a known route", () =>
  pm.expect(["auto_merge", "judge_merge", "new_empty", "new_low", "new_judge", "vague", "judge_failed"]).to.include(r.dedup_route));
pm.collectionVariables.set("caseId", r.case_id);"""

DUPLICATE = OK + """
const r = pm.response.json();
pm.test("marked as duplicate", () => pm.expect(r.is_duplicate).to.eql(true));
pm.test("same case as the first complaint", () => pm.expect(String(r.case_id)).to.eql(String(pm.collectionVariables.get("caseId"))));"""

CASES = OK + """
const cases = pm.response.json();
pm.test("is an array", () => pm.expect(cases).to.be.an("array"));
pm.test("every case has case_id and report_count", () => cases.forEach(c => {
  pm.expect(c).to.have.property("case_id"); pm.expect(c).to.have.property("report_count"); }));
pm.test("merged (absorbed) cases are hidden", () => cases.forEach(c => pm.expect(c.merged_into || null).to.eql(null)));
pm.test("our case is listed", () => pm.expect(cases.map(c => String(c.case_id))).to.include(String(pm.collectionVariables.get("caseId"))));""" + FAST

INTEL = OK + """
const r = pm.response.json();
pm.test("has case, escalation and rca_recommended", () => ["case", "escalation", "rca_recommended"].forEach(k => pm.expect(r).to.have.property(k)));
pm.test("report_count is at least 2 after the duplicate", () => pm.expect(r.case.report_count).to.be.at.least(2));"""

UNASSIGNED = OK + """
const r = pm.response.json();
pm.test("reports whether the feature flag is on", () => pm.expect(r.enabled).to.be.a("boolean"));
pm.test("products is an array", () => pm.expect(r.products).to.be.an("array"));
pm.test("an alert carries a hedged message", () => r.products.filter(p => p.spike).forEach(p => pm.expect(p.message).to.include("Possible outage")));"""

REJOIN = OK + """
const r = pm.response.json();
pm.test("reports enabled flag and merges", () => { pm.expect(r.enabled).to.be.a("boolean"); pm.expect(r.merges).to.be.an("array"); });
pm.test("when disabled, nothing is merged", () => { if (!r.enabled) pm.expect(r.merges).to.have.length(0); });"""

ESCALATE_409 = """
// a fresh case with 2 reports and no spike does not meet the policy (>= 3 reports or a spike)
pm.test("status 409", () => pm.response.to.have.status(409));
pm.test("detail explains eligibility", () => {
  const d = pm.response.json().detail; pm.expect(d.eligible).to.eql(false); pm.expect(d.message).to.include("force=true"); });"""

S404 = 'pm.test("status 404", () => pm.response.to.have.status(404));'
S422 = 'pm.test("status 422", () => pm.response.to.have.status(422));'

items = [
    {"name": "1. Health", "item": [
        req("API is running", "GET", "/", OK + '\npm.test("running message", () => pm.expect(pm.response.json().message).to.include("running"));' + FAST)]},
    {"name": "2. Ingest complaints (/analyze)", "item": [
        req("New complaint creates or joins a case", "POST", "/analyze", ANALYZE_OK,
            {"complaint_text": "{{complaintText}}", "user_id": "{{userId}}", "rating": 1, "source": "postman", "product": "{{product}}"},
            "Ingests one complaint; stores the returned case_id for the next requests."),
        req("Same complaint again joins the same case (duplicate)", "POST", "/analyze", DUPLICATE,
            {"complaint_text": "{{complaintText}}", "user_id": "{{userId2}}", "rating": 1, "source": "postman", "product": "{{product}}"},
            "An identical complaint from another user must be merged (above the auto-merge threshold)."),
        req("Very long complaint (> 512 tokens) does not crash", "POST", "/analyze",
            OK + '\npm.test("processed despite length (regression: sentiment truncation)", () => pm.expect(pm.response.json()).to.have.property("case_id"));',
            {"complaint_text": LONG, "user_id": "{{userId}}", "product": "{{product}}"},
            "Regression test for the crash fixed in commit 03f85c8 (index 514 out of bounds)."),
        req("Missing complaint_text is rejected (422)", "POST", "/analyze",
            S422 + '\npm.test("error names the missing field", () => pm.expect(JSON.stringify(pm.response.json().detail)).to.include("complaint_text"));',
            {"user_id": "{{userId}}"}),
        req("Wrong type for rating is rejected (422)", "POST", "/analyze", S422,
            {"complaint_text": "Login fails", "user_id": "{{userId}}", "rating": "five stars"}),
        req("Missing user_id is rejected (422)", "POST", "/analyze", S422, {"complaint_text": "Login fails"})]},
    {"name": "3. Cases and dashboard", "item": [
        req("Overview", "GET", "/dashboard/overview", OK + FAST),
        req("Case list", "GET", "/dashboard/cases", CASES),
        req("Case intelligence", "GET", "/dashboard/cases/{{caseId}}/intelligence", INTEL),
        req("Unknown case -> 404", "GET", "/dashboard/cases/999999999/intelligence", S404),
        req("Complaint list", "GET", "/dashboard/complaints", OK + '\npm.test("is an array", () => pm.expect(pm.response.json()).to.be.an("array"));'),
        req("Topics", "GET", "/dashboard/topics", OK)]},
    {"name": "4. Spikes and alerts", "item": [
        req("Case spikes", "GET", "/dashboard/spikes", OK),
        req("Alert-group spikes", "GET", "/dashboard/group-spikes",
            OK + '\npm.test("is an array of groups with case_ids", () => { const g = pm.response.json(); pm.expect(g).to.be.an("array"); g.forEach(x => pm.expect(x).to.have.property("case_ids")); });'),
        req("Vague-complaint summary", "GET", "/dashboard/vague-summary",
            OK + '\npm.test("has vague_cases and by_product", () => { const r = pm.response.json(); pm.expect(r).to.have.property("vague_cases"); pm.expect(r.by_product).to.be.an("array"); });'),
        req("Unassigned-complaint (outage) alarm", "GET", "/dashboard/unassigned-spikes", UNASSIGNED)]},
    {"name": "5. Re-joining", "item": [
        req("Re-joining pass (off unless REJOIN_ENABLED=1)", "POST", "/dashboard/rejoin", REJOIN,
            desc="With REJOIN_ENABLED=1 this merges cases in the database: run it only against a test database.")]},
    {"name": "6. Escalation and RCA", "item": [
        req("Escalating a non-eligible case -> 409 with the policy", "POST", "/dashboard/cases/{{caseId}}/escalate", ESCALATE_409,
            desc="Never sends an email: the case is not eligible. A forced escalation (force=true) is deliberately NOT included because it sends a real email."),
        req("Escalating an unknown case -> 404", "POST", "/dashboard/cases/999999999/escalate", S404),
        req("RCA for an unknown case -> 404", "GET", "/dashboard/rca/999999999", S404)]},
]

collection = {
    "info": {"name": "InsightDesk API tests",
             "description": ("Functional API tests for the InsightDesk backend (FastAPI). Run against a LOCAL backend "
                             "connected to a TEST Supabase project and Pinecone index - never production. Run the folders "
                             "in order: later requests use the case created in folder 2."),
             "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
    "variable": [{"key": "baseUrl", "value": "http://127.0.0.1:8000"},
                 {"key": "userId", "value": "postman-user-1"},
                 {"key": "userId2", "value": "postman-user-2"},
                 {"key": "product", "value": "PostmanTestApp"},
                 {"key": "complaintText", "value": "Postman test: the app shows invalid credentials when I log in with the correct password"},
                 {"key": "caseId", "value": ""}],
    "item": items,
}

out = os.path.join(HERE, "InsightDesk.postman_collection.json")
json.dump(collection, open(out, "w", encoding="utf-8"), indent=2)
print("written", out, "| requests:", sum(len(f["item"]) for f in items),
      "| tests:", sum(r["event"][0]["script"]["exec"].__len__() and sum(l.count("pm.test(") for l in r["event"][0]["script"]["exec"]) for f in items for r in f["item"]))
