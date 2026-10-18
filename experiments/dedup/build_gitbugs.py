"""
Build the GitBugs VS Code real-duplicate test set (local only).

Source: GitBugs (Patil 2025, CC-BY-4.0), github.com/av9ash/gitbugs,
ms_vscode_bugs/vscode_bugs.csv + vscode_bugs-combined.csv, saved in
data/external/ (git-excluded).

Groups: each original issue plus its maintainer-marked duplicates; groups
that share an issue are merged (union-find). Sample:
  - every duplicate group with >= 3 usable reports (capped at 10 random
    reports each), then random duplicate PAIRS until ~400 reports.
    Deviation from the planned 60-80 groups: only 2,006 of the 11,451
    duplicate-group issue ids have text in vscode_bugs.csv, so only 70
    groups have >= 3 usable reports (276 reports); pairs fill the rest.
  - ~100 lone reports: closed as "completed" and not in any duplicate
    group (GitHub has no "fixed" state; "completed" is the closest)

Two text versions of every report (same rows, same labels):
  user      title + body with the issue template, HTML comments, code
            blocks, <details> dumps, stack traces, version lines and URLs
            removed
  template  title + body with only code blocks, <details> dumps, stack
            traces and URLs removed (template text kept) - input for the
            boilerplate detector

Output: data/external/gitbugs_user.csv, data/external/gitbugs_template.csv
(schema of synthetic_ground_truth.csv: complaint_ref, department,
issue_id, complaint_text; complaint_ref = arrival order by creation time).

  python experiments/dedup/build_gitbugs.py
"""

import ast
import os
import random
import re

import pandas as pd

EXT = "data/external"
SEED = 7
TARGET_REPORTS = 400
MAX_PER_GROUP = 10
MIN_PER_GROUP = 3
N_SINGLETONS = 100
# Manual label check (gitbugs_label_check.py -> results/gitbugs_top30_crossgroup.csv):
# of the 30 most similar cross-group pairs, 2 were the same bug (both linking
# these two groups), 9 unsure (kept as labelled), 19 different.
MANUAL_MERGES = {"dup_164485": "dup_205471"}
MAX_CHARS = 1000
MIN_USER_CHARS = 40

CODE_FENCE = re.compile(r"```.*?(```|$)", re.S)
DETAILS = re.compile(r"<details>.*?(</details>|$)", re.S | re.I)
HTML_COMMENT = re.compile(r"<!--.*?(-->|$)", re.S)
URL = re.compile(r"!?\[[^\]]*\]\([^)]*\)|https?://\S+")
STACK_LINE = re.compile(r"^\s*(at\s+\S+.*\(|at\s+[\w.$<>]+\s*$|\S+\.(js|ts):\d+|Error:\s|\w*Exception\b)", re.I)
TEMPLATE_LINE = re.compile(
    r"^\s*[-*]?\s*(vs ?code version|os version|version|commit|date|electron|electronbuildid|"
    r"chromium|node\.?js|v8|os|sandboxed|type|does this issue occur when all extensions are disabled|"
    r"steps to reproduce|expected|actual)\s*[:?]",
    re.I,
)
TEMPLATE_MARKERS = re.compile(
    r"do not delete this|bug_report_template|please search existing issues|issue type:|"
    r"we have written the needed data into your clipboard|because it was too large to send|"
    r"^\s*(ple)?ase paste\.?\s*$|^\s*restricted mode|^\s*modes?:|remote os version|extension version \(available",
    re.I)
HTML_TAG = re.compile(r"<[^>]+>")


def _strip_common(text):
    text = CODE_FENCE.sub(" ", text)
    text = DETAILS.sub(" ", text)
    text = URL.sub(" ", text)
    lines = [l for l in text.splitlines() if not STACK_LINE.search(l)]
    return lines


def user_text(title, body):
    body = HTML_COMMENT.sub(" ", str(body or ""))
    lines = _strip_common(body)
    kept = []
    for l in lines:
        if TEMPLATE_LINE.search(l) or TEMPLATE_MARKERS.search(l):
            continue
        l = HTML_TAG.sub(" ", l)
        l = re.sub(r"^[\s>#*\-\d.]+", "", l).strip()   # markdown bullets / headings / numbering
        if l and not re.fullmatch(r"[|:\- ]+", l):
            kept.append(l)
    return _join(title, kept)


def template_text(title, body):
    lines = _strip_common(str(body or ""))
    kept = [l.strip() for l in lines if l.strip() and not re.fullmatch(r"[|:\- ]+", l.strip())]
    return _join(title, kept)


def _join(title, lines):
    title = str(title).strip().rstrip(".")
    text = title + ". " + "\n".join(lines)
    return re.sub(r"[ \t]+", " ", text).strip()[:MAX_CHARS]


def load_groups():
    comb = pd.read_csv(os.path.join(EXT, "vscode_bugs-combined.csv"))
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in comb.itertuples(index=False):
        master = int(r[0])
        for d in ast.literal_eval(r[1]):
            parent[find(int(d))] = find(master)
    groups = {}
    for x in list(parent):
        groups.setdefault(find(x), set()).add(x)
    return groups


def main():
    bugs = pd.read_csv(os.path.join(EXT, "vscode_bugs.csv"))
    bugs["Issue id"] = bugs["Issue id"].astype(int)
    bugs = bugs.drop_duplicates("Issue id").set_index("Issue id")
    bugs["user"] = [user_text(t, b) for t, b in zip(bugs["Summary"], bugs["Description"])]
    bugs["template"] = [template_text(t, b) for t, b in zip(bugs["Summary"], bugs["Description"])]
    usable = bugs[bugs["user"].str.len() >= MIN_USER_CHARS]

    groups = load_groups()
    in_any_group = set().union(*groups.values())
    big, pairs = [], []
    for gid, members in sorted(groups.items()):
        present = sorted(m for m in members if m in usable.index)
        if len(present) >= MIN_PER_GROUP:
            big.append((gid, present))
        elif len(present) == 2:
            pairs.append((gid, present))

    rng = random.Random(SEED)
    chosen = [(gid, rng.sample(p, min(MAX_PER_GROUP, len(p)))) for gid, p in big]
    total = sum(len(t) for _, t in chosen)
    rng.shuffle(pairs)
    for gid, p in pairs:
        if total >= TARGET_REPORTS:
            break
        chosen.append((gid, p))
        total += 2
    candidates = big

    lone_pool = usable[(usable["Resolution"] == "completed") & ~usable.index.isin(in_any_group)]
    lone = rng.sample(sorted(lone_pool.index), N_SINGLETONS)

    rows = [(i, f"dup_{gid}") for gid, take in chosen for i in take] + [(i, f"lone_{i}") for i in lone]
    df = pd.DataFrame(rows, columns=["issue_number", "issue_id"])
    df["issue_id"] = df["issue_id"].replace(MANUAL_MERGES)
    df["created"] = df["issue_number"].map(bugs["Created"])
    df = df.sort_values(["created", "issue_number"]).reset_index(drop=True)
    df["complaint_ref"] = range(1, len(df) + 1)
    df["department"] = "vscode"

    for version in ("user", "template"):
        out = df.assign(complaint_text=df["issue_number"].map(bugs[version]))
        out[["complaint_ref", "department", "issue_id", "complaint_text", "issue_number", "created"]] \
            .to_csv(os.path.join(EXT, f"gitbugs_{version}.csv"), index=False)

    sizes = df[df.issue_id.str.startswith("dup_")].groupby("issue_id").size()
    print(f"duplicate groups: {len(sizes)}, reports in them: {sizes.sum()}, "
          f"size min/median/max: {sizes.min()}/{int(sizes.median())}/{sizes.max()}")
    print(f"lone reports: {len(lone)}; total reports: {len(df)}; "
          f"candidate groups available (>= {MIN_PER_GROUP} usable): {len(candidates)}")
    u = df["issue_number"].map(bugs["user"]).str.len()
    t = df["issue_number"].map(bugs["template"]).str.len()
    print(f"mean chars: user {u.mean():.0f}, template {t.mean():.0f}")


if __name__ == "__main__":
    main()
