"""Eleventh pass: landscape architecture diagram, full width on its slide (the tall one was unreadable)."""
import re

import build as b

N = 25
s = b.rd(N)
s = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="990" name="Results text 990".*?</p:sp>', "", s, flags=re.S)
b.wr(N, s)
print(b.place_picture(N, "img_arch_wide.png", "arch_wide.png", 870000, 1450000, 7400000))
