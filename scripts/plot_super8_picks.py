#!/usr/bin/env python3
"""
Generate two plots for the Super 8 AI vs Humans blog post:
1. "How split are we?" - team advancement picks, Group 1 vs Group 2
2. "Humans vs AIs: Group 2 Leader picks"

Run with: uv run python plot_super8_picks.py
Output:   ../../img/cricket/t20-2026-super8-split.png
          ../../img/cricket/t20-2026-super8-g2-leader.png
"""

import csv
import os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "pii-data", "T20-2026", "T20 2026 Super8 Prediction Contest Responses.csv")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "..", "img", "cricket")

rows = []
with open(DATA_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

keys   = list(rows[0].keys())
g1_lead_col = keys[4]
g1_run_col  = keys[5]
g2_lead_col = keys[6]
g2_run_col  = keys[7]

AI_NAMES = {"Gemini (Deep Research)", "Claude Opus 4.6", "ChatGPT Deep Research", "Perplexity GPT-5.1"}
humans = [r for r in rows if r["Your Name"] not in AI_NAMES]
ais    = [r for r in rows if r["Your Name"] in AI_NAMES]

n_humans = len(humans)

# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------
g1_advance = Counter()
for r in humans:
    g1_advance[r[g1_lead_col]] += 1
    g1_advance[r[g1_run_col]]  += 1

g2_advance = Counter()
for r in humans:
    g2_advance[r[g2_lead_col]] += 1
    g2_advance[r[g2_run_col]]  += 1

g2_leader_humans = Counter(r[g2_lead_col] for r in humans)
g2_leader_ais    = Counter(r[g2_lead_col] for r in ais)

# ---------------------------------------------------------------------------
# Colour palette (consistent team colours, muted)
# ---------------------------------------------------------------------------
TEAM_COLORS = {
    "India":        "#1565C0",   # deep blue
    "South Africa": "#2E7D32",   # green
    "West Indies":  "#B71C1C",   # maroon
    "Zimbabwe":     "#E65100",   # orange

    "New Zealand":  "#000000",   # black
    "Sri Lanka":    "#283593",   # dark navy
    "England":      "#C62828",   # red
    "Pakistan":     "#1B5E20",   # dark green
}

HIGHLIGHT   = "#FFD600"   # gold accent for AI bar edges

# ---------------------------------------------------------------------------
# Plot 1: "How split are we?" — side-by-side Group 1 vs Group 2 advancement
# ---------------------------------------------------------------------------
G1_TEAMS = ["India", "South Africa", "West Indies", "Zimbabwe"]
G2_TEAMS = ["New Zealand", "Sri Lanka", "England", "Pakistan"]

g1_counts = [g1_advance[t] for t in G1_TEAMS]
g2_counts = [g2_advance[t] for t in G2_TEAMS]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor("#F5F5F5")

def make_bar_panel(ax, teams, counts, title, n_humans):
    colors = [TEAM_COLORS[t] for t in teams]
    bars = ax.barh(teams[::-1], counts[::-1], color=colors[::-1],
                   height=0.55, edgecolor="white", linewidth=0.8)

    # percentage labels
    for bar, cnt in zip(bars, counts[::-1]):
        pct = cnt / n_humans * 100
        ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
                f"{cnt}  ({pct:.0f}%)",
                va="center", ha="left", fontsize=11, color="#333333")

    ax.set_xlim(0, n_humans + 8)
    ax.set_xlabel("Number of humans who picked this team to advance", fontsize=10, color="#555555")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12, color="#222222")
    ax.set_facecolor("#F5F5F5")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", colors="#888888")
    ax.xaxis.grid(True, color="#DDDDDD", linewidth=0.7)
    ax.set_axisbelow(True)

make_bar_panel(axes[0], G1_TEAMS, g1_counts, "Group 1 — Near Unanimous", n_humans)
make_bar_panel(axes[1], G2_TEAMS, g2_counts, "Group 2 — Anyone's Guess", n_humans)

fig.suptitle(
    f"Who do humans think advances? ({n_humans} participants)",
    fontsize=15, fontweight="bold", y=1.02, color="#111111"
)
fig.tight_layout()

out1 = os.path.join(OUT_DIR, "t20-2026-super8-split.png")
fig.savefig(out1, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out1}")
plt.close()

# ---------------------------------------------------------------------------
# Plot 2: Group 2 Leader picks — humans (stacked) + AI markers
# ---------------------------------------------------------------------------
ALL_G2 = ["New Zealand", "Sri Lanka", "England", "Pakistan"]

h_counts = [g2_leader_humans[t] for t in ALL_G2]
ai_counts = [g2_leader_ais[t] for t in ALL_G2]

x = np.arange(len(ALL_G2))
bar_w = 0.5

fig2, ax2 = plt.subplots(figsize=(9, 5.5))
fig2.patch.set_facecolor("#F5F5F5")
ax2.set_facecolor("#F5F5F5")

bars2 = ax2.bar(x, h_counts, width=bar_w,
                color=[TEAM_COLORS[t] for t in ALL_G2],
                edgecolor="white", linewidth=0.8, zorder=3)

# human count labels — place below the AI marker zone to avoid overlap
for bar, cnt in zip(bars2, h_counts):
    if cnt > 0:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                 str(cnt), ha="center", va="center", fontsize=13, fontweight="bold", color="white")

# AI picks as gold diamond markers above the bars
AI_LABEL_MAP = {
    "ChatGPT Deep Research": "ChatGPT",
    "Claude Opus 4.6":       "Claude",
    "Gemini (Deep Research)":"Gemini",
    "Perplexity GPT-5.1":    "Perplexity",
}

# stack AI markers vertically per team so they don't overlap
ai_team_picks = {t: [] for t in ALL_G2}
for r in ais:
    team = r[g2_lead_col]
    label = AI_LABEL_MAP.get(r["Your Name"], r["Your Name"])
    ai_team_picks[team].append(label)

marker_size = 200
for i, team in enumerate(ALL_G2):
    labels = ai_team_picks[team]
    base_y = max(h_counts[i], 1) + 2.0
    for j, label in enumerate(labels):
        y_pos = base_y + j * 2.2
        ax2.scatter(i, y_pos, marker="D", s=marker_size,
                    color=HIGHLIGHT, edgecolors="#888800", linewidths=1.2, zorder=5)
        ax2.text(i, y_pos + 0.7, label,
                 ha="center", va="bottom", fontsize=9,
                 color="#444400", fontweight="bold")

ax2.set_xticks(x)
ax2.set_xticklabels(ALL_G2, fontsize=13)
ax2.set_ylabel("Number of humans picking this team as Group 2 leader", fontsize=10, color="#555555")
ax2.set_title(
    "Who wins Group 2?\nHuman picks (bars) vs AI picks (◆)",
    fontsize=14, fontweight="bold", color="#222222", pad=12
)
ai_stack_max = max(len(ai_team_picks[t]) for t in ALL_G2)
ax2.set_ylim(0, max(h_counts) + 4 + ai_stack_max * 2.2 + 3)
ax2.spines[["top", "right"]].set_visible(False)
ax2.tick_params(axis="x", bottom=False)
ax2.yaxis.grid(True, color="#DDDDDD", linewidth=0.7)
ax2.set_axisbelow(True)

# legend
human_patch = mpatches.Patch(color="#888888", label=f"Humans ({n_humans} total)")
ai_patch    = mpatches.Patch(facecolor=HIGHLIGHT, edgecolor="#888800", label="AI model pick")
ax2.legend(handles=[human_patch, ai_patch], loc="upper right", fontsize=10, framealpha=0.7)

fig2.tight_layout()
out2 = os.path.join(OUT_DIR, "t20-2026-super8-g2-leader.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight", facecolor=fig2.get_facecolor())
print(f"Saved: {out2}")
plt.close()
