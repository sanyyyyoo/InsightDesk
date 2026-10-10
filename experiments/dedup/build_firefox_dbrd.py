"""
Firefox duplicate-bug benchmark (local files) -> the pipeline's ingestion format.

Inputs (experiments/dedup/labelling/, provided by the user):
  mozilla_firefox.csv   all reports: Issue_id, Title, Description, Resolution, Created_time, ...
  test.csv              Issue_id -> Duplicate (';'-separated ids of its duplicate group)
  train.csv             unused (nothing is trained or tuned on Firefox)

Sample (fixed before any pipeline run, seed 7; same recipe as GitBugs):
  - duplicate groups from test.csv links (union-find), members with text only;
    N_GROUPS random groups with >= 3 usable reports, at most MAX_PER_GROUP
    random reports each
  - N_LONE lone reports: test issues with no duplicate, resolved FIXED
Text = title + description: the description's ';' separators become line
breaks; User-Agent / Build Identifier lines, HTML tags, URLs and crash/log lines
are removed; template headings (Steps to Reproduce, Actual/Expected Results)
are kept for the frozen pipeline's boilerplate step. Cut to MAX_CHARS.

Output: data/external/firefox.csv
  complaint_ref (arrival order by Created_time), department ("Firefox"),
  issue_id ("ff_<group root>" or "lone_<id>"), complaint_text, created_at,
  row (Issue_id), problem_code (group root or "lone"), scored

  python experiments/dedup/build_firefox_dbrd.py

Fresh second sample (spike-grouping v2 confirmation): groups from train.csv
links, none sharing a report or a group with the first sample:
  python experiments/dedup/build_firefox_dbrd.py --split train --seed 11       --exclude data/external/firefox.csv --out data/external/firefox2.csv
"""

import argparse
import collections
import os
import random
import re

import pandas as pd

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "labelling")
OUT = "data/external/firefox.csv"
SEED = 7
N_GROUPS = 70
MAX_PER_GROUP = 10
MIN_PER_GROUP = 3
N_LONE = 100
MAX_CHARS = 1000
MIN_CHARS = 40

HTML = re.compile(r"<[^>]+>")
URL = re.compile(r"https?://\S+|www\.\S+")
DROP_LINE = re.compile(
    r"^\s*(user[- ]agent:|build identifier:|mozilla/5\.0|crash (report|id)|signature:|#\d+\s+0x|\[@|"
    r"at\s+\S+:\d+|\S+\.(js|cpp|h|rs|jsm|xul|py):\d+|\w*(error|exception):\s|0x[0-9a-f]{6,}|"
    r"\d{4}-\d\d-\d\d[ t]\d\d:\d\d)", re.I)
# pieces of a User-Agent string (the dataset's ';' separators split it into fragments)
UA_PIECE = re.compile(
    r"gecko/\d|rv:\d|^\s*[uin]\s*$|windows nt|wow64|win64|macintosh|intel mac os|ppc mac|x11|"
    r"linux (i686|x86_64)|^\s*[a-z]{2}-[a-z]{2}\s*$|firefox/\d[\d.]*\s*$|seamonkey/\d|applewebkit|khtml", re.I)


def clean(title, desc):
    desc = HTML.sub(" ", str(desc) if isinstance(desc, str) else "")
    lines = [URL.sub("", ln).strip() for ln in re.split(r";\s*|\n", desc)]
    lines = [ln for ln in lines if ln and not DROP_LINE.search(ln) and not UA_PIECE.search(ln)]
    return (str(title).strip() + ". " + "\n".join(lines)).strip()[:MAX_CHARS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["test", "train"])
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--exclude", nargs="*", default=None, help="earlier samples: no shared report or group")
    args = ap.parse_args()
    m = pd.read_csv(os.path.join(SRC, "mozilla_firefox.csv"),
                    usecols=["Issue_id", "Title", "Description", "Resolution", "Created_time"]).set_index("Issue_id")
    te = pd.read_csv(os.path.join(SRC, f"{args.split}.csv"))
    links = pd.concat([pd.read_csv(os.path.join(SRC, f)) for f in ("test.csv", "train.csv")]) if args.exclude else te
    excluded = set().union(*(set(pd.read_csv(f).row) for f in args.exclude)) if args.exclude else set()
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in links.itertuples():          # with --exclude: full link graph, so groups cannot straddle samples
        if isinstance(r.Duplicate, str):
            for d in r.Duplicate.split(";"):
                a, b = find(int(r.Issue_id)), find(int(d))
                parent[a] = b
    groups, touched = collections.defaultdict(list), set()
    for x in list(parent):
        if x in excluded:
            touched.add(find(x))
        if x in m.index and isinstance(m.at[x, "Title"], str):
            groups[find(x)].append(x)
    rng = random.Random(args.seed)
    roots = sorted(k for k, v in groups.items() if len(v) >= MIN_PER_GROUP and k not in touched)
    rng.shuffle(roots)
    rows = []
    for root in roots:
        members = sorted(groups[root])
        if len(members) > MAX_PER_GROUP:
            members = sorted(rng.sample(members, MAX_PER_GROUP))
        texts = [(i, clean(m.at[i, "Title"], m.at[i, "Description"])) for i in members]
        texts = [(i, t) for i, t in texts if len(t) >= MIN_CHARS]
        if len(texts) < MIN_PER_GROUP:
            continue
        rows += [{"row": i, "issue_id": f"ff_{root}", "problem_code": str(root), "complaint_text": t,
                  "created_at": m.at[i, "Created_time"]} for i, t in texts]
        if len({r["issue_id"] for r in rows}) == N_GROUPS:
            break
    lone_pool = te[te.Duplicate.isna()].Issue_id.tolist()
    lone_pool = sorted(i for i in lone_pool if i in m.index and m.at[i, "Resolution"] == "FIXED"
                       and i not in parent and i not in excluded)
    rng.shuffle(lone_pool)
    n_lone = 0
    for i in lone_pool:
        t = clean(m.at[i, "Title"], m.at[i, "Description"])
        if len(t) >= MIN_CHARS:
            rows.append({"row": i, "issue_id": f"lone_{i}", "problem_code": "lone", "complaint_text": t,
                         "created_at": m.at[i, "Created_time"]})
            n_lone += 1
            if n_lone == N_LONE:
                break
    d = pd.DataFrame(rows)
    d["ts"] = pd.to_datetime(d.created_at, utc=True)
    d = d.sort_values(["ts", "row"]).drop(columns="ts").reset_index(drop=True)
    d["complaint_ref"] = range(1, len(d) + 1)
    d["department"] = "Firefox"
    d["scored"] = True
    d = d[["complaint_ref", "department", "issue_id", "complaint_text", "created_at", "row", "problem_code", "scored"]]
    assert d.row.is_unique
    os.makedirs("data/external", exist_ok=True)
    assert not (set(d.row) & excluded)
    d.to_csv(args.out, index=False)
    g = d.issue_id.value_counts()
    print(f"reports {len(d)} | duplicate groups {int((g > 1).sum())} ({int(g[g > 1].sum())} reports, "
          f"{int((g * (g - 1) // 2).sum())} pairs, sizes {g[g > 1].min()}-{g[g > 1].max()}) | lone {int((g == 1).sum())}")
    print("example:", d.complaint_text.iloc[5][:400].replace("\n", " / "))
    print("saved", args.out)


if __name__ == "__main__":
    main()
