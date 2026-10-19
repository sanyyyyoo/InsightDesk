"""Fifth pass: calibration table with the adopted short-text setting (t_low = 0.40)."""
import re

import build as b
import patch3 as p3

s = b.rd(21)
s = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="960" name="Results text 960".*?</p:sp>', "", s, flags=re.S)
b.wr(21, s)
p3.table_slide(21, "THRESHOLD CALIBRATION & SENSITIVITY",
               [2450000, 1300000, 1350000, 850000, 750000, 650000, 750000],
               ["Setting", "t_low", "t_high", "Precision", "Recall", "F1", "LLM share"],
               [["Original calibration (long-text channels)", "20th pct. of duplicates", "precision ≥ 0.97", "0.810", "0.259", "0.392", "86%"],
                ["Short-text setting (deployed)", "0.40", "same", "0.883", "0.284", "0.430", "66%"],
                ["t_low raised by 0.04", "+ 0.04", "same", "0.803", "0.256", "0.388", "81%"],
                ["t_low raised by 0.14", "+ 0.14", "same", "0.906", "0.260", "0.404", "61%"],
                ["t_high lowered by 0.08", "same", "− 0.08", "0.808", "0.277", "0.413", "78%"],
                ["Unseen apps: 0.26 → 0.40", "0.26 → 0.40", "0.8306", "0.608 → 0.635", "0.284 → 0.255", "–", "94% → 77%"],
                ["Bug reports: 0.26 → 0.40", "0.26 → 0.40", "0.8306", "0.908 → 0.912", "0.578 → 0.571", "–", "96% → 90%"]],
               360000,
               "Play Store held-out halves pooled, live judge calls. t_low = 0.40 was confirmed on unseen short reviews "
               "under a rule written before the run and is used for app reviews and chat; it changed little on long bug "
               "reports, so tickets and bug reports keep 0.26. t_high 0.8306 transfers unchanged everywhere.")
print("ok")
