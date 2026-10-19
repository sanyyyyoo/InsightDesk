"""Eighth pass: layout. Drop empty leftover tables (Google Slides export artefacts), move the conclusion text
below its title, and give table slides a gap under the title."""
import glob
import re

import build as b

for f in glob.glob(f"{b.U}/slides/slide*.xml"):
    n = int(re.search(r"slide(\d+)\.xml", f).group(1))
    s = b.rd(n)
    gfs = re.findall(r"<p:graphicFrame>.*?</p:graphicFrame>", s, re.S)
    for g in gfs:
        if "drawingml/2006/table" in g and not re.search(r"<a:t>[^<]+</a:t>", g):
            s = s.replace(g, "", 1)
    if n in (21, 22, 23):     # table under the title, not touching it
        s = s.replace('<a:off x="497000" y="1500000"/>', '<a:off x="497000" y="1580000"/>', 1)
        s = re.sub(r'(name="Results text 9\d0".*?<a:off x="\d+" y=")(\d+)', lambda m: m.group(1) + str(int(m.group(2)) + 80000), s, count=1, flags=re.S)
    if n == 12:               # conclusion body below the title
        s = s.replace('<a:off x="686435" y="1648460"/><a:ext cx="7764780" cy="2457450"/>',
                      '<a:off x="686435" y="1960000"/><a:ext cx="7764780" cy="2700000"/>', 1)
    b.wr(n, s)
print("ok")

# spike table: shorter rows so the note clears the footer band (applied once, 2026-10-19)
