"""Fourth pass: drop duplicate notes; calibration table with the live t_low rows."""
import re
import build as b
import patch3 as p3


def drop_notes(n):
    s = b.rd(n)
    s = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="960" name="Results text 960".*?</p:sp>', "", s, flags=re.S)
    b.wr(n, s)


drop_notes(21)
drop_notes(22)
p3.table_slide(21, "THRESHOLD CALIBRATION & SENSITIVITY",
               [2350000, 1450000, 1450000, 850000, 750000, 650000, 650000],
               ["Setting", "t_low", "t_high", "Precision", "Recall", "F1", "LLM share"],
               [["Calibrated on tuning half (deployed)", "20th pct. of duplicates", "precision \u2265 0.97", "0.810", "0.259", "0.392", "86%"],
                ["t_low raised by 0.04", "+ 0.04", "same", "0.803", "0.256", "0.388", "81%"],
                ["t_low raised by 0.09", "+ 0.09", "same", "0.867", "0.264", "0.404", "71%"],
                ["t_low raised by 0.14", "+ 0.14", "same", "0.906", "0.260", "0.404", "61%"],
                ["t_high lowered by 0.08", "same", "\u2212 0.08", "0.808", "0.277", "0.413", "78%"],
                ["t_high lowered by 0.13", "same", "\u2212 0.13", "0.722", "0.246", "0.367", "68%"],
                ["Single cosine threshold, no judge", "one cut", "one cut", "\u2013", "\u2013", "\u2248 0.10", "0%"]],
               360000,
               "Play Store held-out halves pooled, live judge calls. Recall is stable across settings; a higher t_low raises "
               "precision and cuts LLM calls, so the 20th-percentile rule is conservative. Final values (t_low 0.26, t_high 0.8306) "
               "transfer unchanged to Firefox, Thunderbird and unseen apps (precision 0.87\u20130.96).")
p3.table_slide(22, "SPIKE DETECTOR CALIBRATION",
               [2000000, 1450000, 1150000, 1150000, 1200000, 1200000],
               ["Detector", "Setting", "Play Store detected", "Play Store false / 100 windows", "Bug reports detected", "Bug reports false / 100 windows"],
               [["Poisson CUSUM (deployed)", "\u03b4 = 1, h = 2", "42%", "0.06", "76%", "0.38"],
                ["Poisson CUSUM", "\u03b4 = 1, h = 1.5", "56%", "0.78", "86%", "3.81"],
                ["Poisson CUSUM", "\u03b4 = 1, h = 3", "25%", "0.00", "50%", "0.01"],
                ["Poisson CUSUM", "\u03b4 = 0.5, h = 2", "45%", "0.22", "78%", "1.04"],
                ["Poisson CUSUM", "\u03b4 = 2, h = 2", "33%", "0.02", "67%", "0.10"],
                ["EWMA", "\u03b1 = 0.2, L = 3", "55%", "0.67", "86%", "3.19"],
                ["Poisson tail test", "c \u2265 2, p < 0.001", "43%", "0.27", "71%", "1.20"],
                ["z-score (feedback tools)", "z > 2", "0%", "\u2013", "0%", "\u2013"]],
               330000,
               "300 simulated outbreaks per dataset, case level. h = 2 is the knee: lower h buys little detection for many more false "
               "alarms. EWMA reaches CUSUM's detection only at about 9\u00d7 its false alarms on bug reports.")
for n in (21, 22):
    print(n, b.rd(n).count('name="Results text 960"'))
