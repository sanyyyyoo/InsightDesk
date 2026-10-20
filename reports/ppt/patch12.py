"""Twelfth pass: slide 9 becomes a methodology diagram (rules and formulas in each phase, data types on the
arrows, state updates), replacing the plain architecture picture."""
import re

import build as b

N = 25
print(b.place_picture(N, "img_method.png", "methodology.png", 1620000, 1600000, 5900000))
s = b.rd(N)
s = re.sub(r"<a:srcRect[^>]*/>", "<a:srcRect/>", s)
s = s.replace(">SYSTEM ARCHITECTURE<", ">SYSTEM ARCHITECTURE &amp; METHODOLOGY<", 1)
b.wr(N, s)
