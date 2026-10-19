"""Result charts for the deck (deployed setting: short-text t_low 0.40 on Play Store, 0.26 on bug reports).

  python charts.py <play_store_P> <play_store_R> <play_store_F1>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, GREY, INK, MUTED = "#2b7bd6", "#c4c4b8", "#111111", "#555555"
plt.rcParams.update({"font.family": "Arial", "font.size": 13, "axes.edgecolor": "#999999"})

P, R, F1 = map(float, sys.argv[1:4])

# ---------------------------------------------------------------- F1 bars (competitor numbers unchanged)
rows = [("InsightDesk", F1, 0.78), ("BERTopic", 0.25, 0.54), ("CLAP (best setting)", 0.24, 0.37),
        ("BM25 (REP text model)", 0.24, 0.47), ("MinHash-LSH", 0.20, 0.03), ("Cross-encoder threshold", 0.14, None),
        ("Embedding threshold", 0.10, 0.07), ("SimHash", 0.12, 0.04)]
fig, axes = plt.subplots(1, 2, figsize=(13.44, 8.08), dpi=100, sharey=True)
fig.subplots_adjust(left=0.3, right=0.97, top=0.78, bottom=0.08, wspace=0.25)
y = list(range(len(rows)))[::-1]
for k, (ax, title) in enumerate(zip(axes, ("Play Store F1", "Firefox F1"))):
    for yi, row in zip(y, rows):
        v = row[1 + k]
        col = BLUE if row[0] == "InsightDesk" else GREY
        if v is None:
            ax.text(0.01, yi, "not run", va="center", color=MUTED)
            continue
        ax.barh(yi, v, color=col, height=0.55)
        ax.text(v + 0.015, yi, f"{v:.2f}", va="center", color=INK if col == BLUE else MUTED,
                fontweight="bold" if col == BLUE else "normal")
    ax.set_xlim(0, 0.95)
    ax.set_title(title, loc="left", fontweight="bold", fontsize=14)
    ax.axvline(0, color="#999999", lw=1)
    ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(left=False)
axes[0].set_yticks(y)
axes[0].set_yticklabels([r[0] for r in rows])
axes[0].get_yticklabels()[0].set_fontweight("bold")
fig.text(0.03, 0.93, "InsightDesk has the highest F1 on both datasets", fontsize=19, fontweight="bold")
fig.text(0.03, 0.885, "Pairwise F1 on identical data; deployed settings (Play Store: short-text t_low 0.40; Firefox: 0.26), "
         "with re-joining", fontsize=12.5, color=MUTED)
fig.savefig("img_f1.png")

# ---------------------------------------------------------------- precision vs recall
pts = [("CLAP (published)", 0.025, 0.84), ("Cross-encoder pipeline", 0.082, 0.378), ("BM25 (REP text)", 0.196, 0.305),
       ("CLAP (tuned)", 0.22, 0.252), ("MinHash-LSH", 0.241, 0.167), ("SimHash", 0.289, 0.073), ("BERTopic", 0.648, 0.159)]
fig, ax = plt.subplots(figsize=(13.44, 7.92), dpi=100)
fig.subplots_adjust(left=0.1, right=0.96, top=0.82, bottom=0.12)
for name, r, p in pts:
    ax.scatter(r, p, s=110, color=GREY, zorder=3)
    ax.annotate(name, (r, p), xytext=(10, -2 if name != "MinHash-LSH" else -16), textcoords="offset points", color=MUTED, va="center")
ax.scatter(0.327, 0.80, s=110, facecolor="white", edgecolor=BLUE, lw=2, zorder=3)
ax.annotate("previous setting (t_low 0.26)", (0.327, 0.80), xytext=(12, -14), textcoords="offset points", color=MUTED, va="center")
ax.annotate("", xy=(R, P), xytext=(0.327, 0.80), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5), zorder=2)
ax.scatter(R, P, s=260, color=BLUE, zorder=4)
ax.annotate(f"InsightDesk (deployed)  P {P:.2f}, R {R:.2f}", (R, P), xytext=(14, 10), textcoords="offset points",
            fontweight="bold", color=INK)
ax.set_xlim(0, 0.7)
ax.set_ylim(0, 1.0)
ax.set_xlabel("recall (share of true duplicate pairs found)", color=MUTED)
ax.set_ylabel("precision", color=MUTED)
ax.grid(axis="y", color="#e5e5e5")
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
fig.text(0.03, 0.93, "Only InsightDesk combines high precision with useful recall", fontsize=19, fontweight="bold")
fig.text(0.03, 0.885, "Pairwise precision and recall, Play Store held-out halves, same input and protocol for every method",
         fontsize=12.5, color=MUTED)
fig.savefig("img_pr.png")
print("charts written")
