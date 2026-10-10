"""
Firefox (Mozilla Bugzilla) real-duplicate test set, in the pipeline's ingestion format.

Source: bugzilla.mozilla.org public REST API, product Firefox, reports filed
2024-01-01 .. 2025-12-31. Labels are Bugzilla's own: a triager closed a
report as DUPLICATE of another bug (dupe_of). Nothing here is labelled by us.

Groups: each master bug plus every report closed as its duplicate (dupe_of
chains followed to the final master). Sample (seed fixed, decided before any
pipeline run):
  - groups with >= 3 usable reports, capped at MAX_PER_GROUP random reports,
    until ~TARGET_GROUPED reports
  - N_LONE lone reports from the user's query (product Firefox, resolution
    still open), not in any duplicate group. Caveat: an open bug can still
    have an undetected duplicate, so a few "lone" pairs may be wrong labels.
Text = summary + first comment (the report itself), with code blocks, stack
traces, crash/log lines, URLs and the user-agent line removed; the template
headings (Steps to reproduce / Actual results / Expected results) are kept,
because the frozen pipeline's boilerplate detector is part of the test.

Output: data/external/firefox.csv with the Play Store test set's columns:
  complaint_ref (arrival order by creation time), department ("Firefox"),
  issue_id ("ff_<master>" or "lone_<id>"), complaint_text, created_at, row
  (bug id), problem_code (master id), scored

  python experiments/dedup/build_firefox.py
"""

import os
import random
import re
import time

import pandas as pd
import requests

B = "https://bugzilla.mozilla.org/rest"
FROM, TO = "2024-01-01", "2025-12-31"
SEED = 7
MAX_PER_GROUP = 10
MIN_PER_GROUP = 3
TARGET_GROUPED = 320
N_LONE = 100
MAX_CHARS = 1000
MIN_CHARS = 40
OUT = "data/external/firefox.csv"

CODE_FENCE = re.compile(r"```.*?(```|$)", re.S)
URL = re.compile(r"https?://\S+")
DROP_LINE = re.compile(
    r"^\s*(user agent:|mozilla/5\.0|crash report|signature:|#\d+\s+0x|\[@|at\s+\S+:\d+|"
    r"\S+\.(js|cpp|h|rs|jsm|mjs|py):\d+|\w*(error|exception):\s|\[(parent|child|gfx)|"
    r"\d{4}-\d\d-\d\d[ t]\d\d:\d\d|0x[0-9a-f]{6,})", re.I)


def get(path, **params):
    for attempt in range(6):
        try:
            r = requests.get(f"{B}/{path}", params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Bugzilla request failed: {path}")


def fetch_list(**query):
    out, offset = [], 0
    while True:
        j = get("bug", product="Firefox", creation_time=FROM, limit=1000, offset=offset,
                include_fields="id,summary,dupe_of,creation_time,resolution,product", **query)
        bugs = j.get("bugs", [])
        out += [b for b in bugs if b["creation_time"][:10] <= TO]
        if len(bugs) < 1000:
            return out
        offset += 1000
        time.sleep(1)


def first_comments(ids):
    texts = {}
    ids = list(ids)
    for k in range(0, len(ids), 40):
        chunk = ids[k:k + 40]
        j = get(f"bug/{chunk[0]}/comment", ids=chunk[1:])
        for bid, v in j.get("bugs", {}).items():
            comments = v.get("comments", [])
            texts[int(bid)] = comments[0]["text"] if comments else ""
        time.sleep(0.5)
    return texts


def clean(summary, body):
    body = CODE_FENCE.sub(" ", body or "")
    lines = [URL.sub("", ln).rstrip() for ln in body.splitlines()]
    lines = [ln for ln in lines if ln.strip() and not DROP_LINE.search(ln)]
    text = (summary.strip() + ". " + "\n".join(lines)).strip()
    return text[:MAX_CHARS]


def main():
    rng = random.Random(SEED)
    dups = fetch_list(resolution="DUPLICATE")
    print("DUPLICATE reports fetched:", len(dups))
    by_id = {b["id"]: b for b in dups}
    master = {}
    for b in dups:
        m, seen = b["dupe_of"], set()
        while m in by_id and by_id[m].get("dupe_of") and m not in seen:   # follow chains
            seen.add(m)
            m = by_id[m]["dupe_of"]
        master[b["id"]] = m
    groups = {}
    for bid, m in master.items():
        groups.setdefault(m, set()).add(bid)
    masters = [m for m in groups if m not in by_id]
    meta = {}
    for k in range(0, len(masters), 300):
        j = get("bug", id=",".join(map(str, masters[k:k + 300])),
                include_fields="id,summary,creation_time,product,resolution")
        meta.update({b["id"]: b for b in j.get("bugs", [])})
    for m in groups:                                   # the master is a report too, if it is Firefox
        if m in meta and meta[m]["product"] == "Firefox":
            groups[m].add(m)
    by_id.update(meta)

    big = [m for m, g in groups.items() if len(g) >= MIN_PER_GROUP]
    rng.shuffle(big)
    picked, n = {}, 0
    for m in big:
        members = sorted(groups[m])
        if len(members) > MAX_PER_GROUP:
            members = sorted(rng.sample(members, MAX_PER_GROUP))
        picked[m] = members
        n += len(members)
        if n >= TARGET_GROUPED:
            break
    in_groups = set(master) | set(groups)
    open_bugs = [b for b in fetch_list(resolution="---") if b["id"] not in in_groups]
    lone = rng.sample(open_bugs, min(N_LONE * 2, len(open_bugs)))
    by_id.update({b["id"]: b for b in lone})

    want = [b for ms in picked.values() for b in ms] + [b["id"] for b in lone]
    texts = first_comments(want)
    rows = []
    for m, members in picked.items():
        for b in members:
            t = clean(by_id[b]["summary"], texts.get(b, ""))
            if len(t) >= MIN_CHARS:
                rows.append({"row": b, "issue_id": f"ff_{m}", "problem_code": str(m), "complaint_text": t,
                             "created_at": by_id[b]["creation_time"]})
    lone_rows = []
    for b in lone:
        t = clean(b["summary"], texts.get(b["id"], ""))
        if len(t) >= MIN_CHARS and len(lone_rows) < N_LONE:
            lone_rows.append({"row": b["id"], "issue_id": f"lone_{b['id']}", "problem_code": "lone",
                              "complaint_text": t, "created_at": b["creation_time"]})
    d = pd.DataFrame(rows + lone_rows)
    g = d.issue_id.value_counts()
    d = d[~d.issue_id.str.startswith("ff_") | d.issue_id.map(g).ge(2)]      # a group needs >= 2 usable reports
    d = d.sort_values(["created_at", "row"]).reset_index(drop=True)
    d["complaint_ref"] = range(1, len(d) + 1)
    d["department"] = "Firefox"
    d["scored"] = True
    d = d[["complaint_ref", "department", "issue_id", "complaint_text", "created_at", "row", "problem_code", "scored"]]
    os.makedirs("data/external", exist_ok=True)
    d.to_csv(OUT, index=False)
    g = d.issue_id.value_counts()
    print(f"reports {len(d)} | duplicate groups {int((g > 1).sum())} ({int(g[g > 1].sum())} reports, "
          f"{int((g * (g - 1) // 2).sum())} pairs) | lone {int((g == 1).sum())} | saved {OUT}")


if __name__ == "__main__":
    main()
