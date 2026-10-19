"""Tenth pass: system architecture slide after the flowchart (image from the paper's Fig. 2)."""
import re

import build as b

N = 25
h = b.place_picture(N, "img_arch.png", "arch.png", 420000, 1520000, 2950000)
s = b.rd(N)
s = re.sub(r">FLOW CHART\s*<", ">SYSTEM ARCHITECTURE<", s, count=1)
paras = [
    b.bullet("Two stores:", " Supabase (PostgreSQL) holds complaints, cases, 6-hour windows, the vague pool and root causes; Pinecone holds up to 5 exemplar vectors per case.", 1150, 300),
    b.bullet("Phases 1–4, on arrival:", " cleaning, MiniLM retrieval of the top-5 cases, the calibrated band (t_high 0.8306; t_low 0.40 short / 0.26 long), and the LLM judge for uncertain matches.", 1150, 300),
    b.bullet("Phases 5–6, every 6 h:", " LLM re-joining merges split cases and moves their vectors; RoBERTa sentiment and BERTopic topics map each case to a department.", 1150, 300),
    b.bullet("Phases 7–8, signals:", " Poisson CUSUM per case and alert group; a separate alarm for vague complaints per product.", 1150, 300),
    b.bullet("Phase 9, action:", " an eligible case gets an LLM root cause (JSON); email goes out only after human approval.", 1150, 300),
    b.bullet("Feedback loop:", " re-joining updates the exemplars that retrieval reads for every new complaint.", 1150, 300),
]
s = s.replace("</p:spTree>", b.textbox(990, 3800000, 1450000, 4950000, 3300000, paras) + "</p:spTree>", 1)
b.wr(N, s)
t = b.rd(2)
t = t.replace("<a:t>Flow Diagram</a:t>", "<a:t>Flow Diagram &amp; Architecture</a:t>", 1)
b.wr(2, t)
print("ok", h)
