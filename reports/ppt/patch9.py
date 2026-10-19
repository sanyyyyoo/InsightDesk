"""Ninth pass: TOC row 6 formatting, problem statement examples, conclusion wording (F1 is the 'highest' claim,
precision is not: CLAP's published setting has 0.84 at 2% recall)."""
import re

import build as b

# TOC: row 6 had its own line spacing and left-aligned number; rebuild it from row 7
s = b.rd(2)
rows = re.findall(r"<a:tr .*?</a:tr>", s, re.S)
r6 = rows[7].replace("<a:t>7.</a:t>", "<a:t>6.</a:t>").replace("<a:t>Results</a:t>", "<a:t>Datasets &amp; Calibration</a:t>")
assert "6." in r6 and "Datasets" in r6
s = s.replace(rows[6], r6, 1)
b.wr(2, s)

EDITS = {
    3: [("Help-desk software companies such as Vision Helpdesk receive complaints from app reviews, support tickets, chat and "
         "web forms.",
         "Help-desk and customer-support platforms such as Vision Helpdesk, Zendesk, Freshdesk, Intercom and ServiceNow, and the "
         "companies that use them, receive complaints from app reviews, support tickets, chat and web forms.")],
    12: [("On real reviews it reaches precision 0.83, recall 0.35 and F1 0.49, the highest of every method tested;",
          "On real reviews it reaches precision 0.83 and recall 0.35, an F1 of 0.49 that is the highest of every method tested;")],
}
for n, pairs in EDITS.items():
    s = b.rd(n)
    for old, new in pairs:
        assert s.count(old) == 1, (n, old)
        s = s.replace(old, new)
    b.wr(n, s)
print("ok")
