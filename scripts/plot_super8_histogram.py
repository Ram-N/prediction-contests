#!/usr/bin/env python3
"""
Generate a histogram of Super 8 scores (human participants),
with AI scores shown as hatched bars and median lines for both groups.

Run with: uv run python plot_super8_histogram.py
Output:   ../../img/cricket/t20-2026-super8-histogram.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "img", "cricket")

# ---------------------------------------------------------------------------
# Data: Super 8 scores from leaderboard.md (DNP treated as absent, excluded)
# ---------------------------------------------------------------------------

human_scores = [
    # (name, super8_score)  — only participants who played Super 8
    ("Aditya", 11),
    ("Keshav Venkatesh", 12),
    ("Ashish", 11),
    ("Sackett", 12),
    ("D. Sivakumar", 10),
    ("Chayan", 10),
    ("Ranga", 11),
    ("Sahana", 6),
    ("Niraj", 8),
    ("Mukund N.", 8),
    ("Krishnaveni Kumbaji", 10),
    ("Kshitij", 10),
    ("Ramesh Srinivasan", 10),
    ("Radhika Santhanam", 11),
    ("Sreenivas G", 9),
    ("Dhanush Ekollu", 9),
    ("Rankanathan.v.s", 7),
    ("Subbu Mahadevan", 6),
    ("Vivek J", 6),
    ("The Kasher", 6),
    ("Manoj S", 6),
    ("S. Parthasarathy", 6),
    ("bala", 8),
    ("Rupal", 8),
    ("Chink", 8),
    ("Dodo", 8),
    ("P.Amritha", 8),
    ("V CV C", 8),
    ("Shiv Iyer", 10),
    ("Ram", 7),
    ("Vivek", 7),
    ("Alok", 5),
    ("Keshav Narasimhan", 6),
    ("Abhinav S", 10),
    ("R Santhanam", 6),
    ("Bharathkirishnan S R", 6),
    ("Pradeep", 6),
    ("Rajesh", 6),
    ("Atul Agarwal", 5),
    ("S V Madhavan", 5),
    ("237 Narmada", 8),
    ("Shajman", 8),
    ("Aakarsh Ekollu", 7),
    ("Manish Bhatt", 6),
    ("Ishaan", 5),
    ("Siva Kantamneni", 4),
    ("Tees", 2),
    ("Goutham Ekollu", 3),
    ("Shriya Sateesh", 4),
    ("Sri Iyer", 2),
    ("Bharath Sridharan", 2),
    ("Hauroon", 1),
    ("Ramana Kadari", 11),
    ("Harsh", 1),
    ("Bhargavi", 10),
    ("Kausalya", 10),
    ("Alamuru Krishna", 8),
    ("vivek", 7),
    ("ALEX", 7),
    ("Rahul Santhanam", 6),
    ("Chandran Dharmarajan", 6),
    ("Harish Natarajan", 6),
    ("Rama", 6),
    ("Kaushik", 5),
    ("Nitin Khanna", 2),
]

ai_scores = [
    ("Perplexity 🤖", 9),
    ("Claude 🤖", 9),
    ("Gemini 🤖", 8),
    ("ChatGPT 🤖", 6),
]

human_vals = [s for _, s in human_scores]
ai_vals    = [s for _, s in ai_scores]

human_median = np.median(human_vals)
ai_median    = np.median(ai_vals)

print(f"Human scores: n={len(human_vals)}, median={human_median}, mean={np.mean(human_vals):.1f}")
print(f"AI scores:    n={len(ai_vals)},    median={ai_median},    mean={np.mean(ai_vals):.1f}")

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor("#F5F5F5")
ax.set_facecolor("#F5F5F5")

# Score range 0–12; bin edges at 0.5, 1.5, ... 12.5
bins = np.arange(-0.5, 13.5, 1)

# Human histogram (solid bars)
human_color = "#1565C0"
ax.hist(human_vals, bins=bins, color=human_color, alpha=0.80,
        edgecolor="white", linewidth=0.8, zorder=3, label=f"Humans (n={len(human_vals)})")

# AI scores as hatched bars (one bar per score value, stacked by count)
ai_color = "#E65100"
# Count AI scores per bin
from collections import Counter
ai_counts = Counter(ai_vals)
for score, count in ai_counts.items():
    ax.bar(score, count, width=1.0, bottom=0,
           color=ai_color, alpha=0.85,
           hatch="///", edgecolor="white", linewidth=1.0,
           zorder=4)

# Dummy patch for AI legend entry
ai_patch = mpatches.Patch(facecolor=ai_color, hatch="///", edgecolor="white",
                           alpha=0.85, label=f"AI models (n={len(ai_vals)})")

# Median lines
ax.axvline(human_median, color="#111111", linewidth=2.5, linestyle="--", zorder=5,
           label=f"Human median ({human_median:g})")
ax.axvline(ai_median,    color="#FF4500", linewidth=2.5, linestyle=":",  zorder=5,
           label=f"AI median ({ai_median:g})")

# Median annotations
ax.text(human_median + 0.15, 14.5, f"Human median\n({human_median:g})",
        color="#111111", fontsize=9, fontweight="bold", va="top", zorder=7)
ax.text(ai_median + 0.15, 14.5, f"AI median\n({ai_median:g})",
        color="#111111", fontsize=9, fontweight="bold", va="top", zorder=7)

# Axis labels and title
ax.set_xlabel("Super 8 Score (out of 12)", fontsize=12, color="#333333")
ax.set_ylabel("Number of participants", fontsize=12, color="#333333")
ax.set_title("Super 8 Scores — Humans vs. AI Models", fontsize=15, fontweight="bold",
             color="#111111", pad=14)

ax.set_xticks(range(0, 13))
ax.set_xlim(-0.5, 12.5)
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.7)
ax.set_axisbelow(True)

# Legend (combine manual AI patch with auto legend entries)
handles, labels = ax.get_legend_handles_labels()
# Insert ai_patch after the human bar entry
handles.insert(1, ai_patch)
labels.insert(1, ai_patch.get_label())
ax.legend(handles=handles, labels=labels, fontsize=11, framealpha=0.85, loc="upper left")

# Annotate perfect scorers with red box around the bar + label
perfect_count = human_vals.count(12)
if perfect_count:
    # Red rectangle around the score=12 bar
    rect = plt.Rectangle((11.5, 0), 1.0, perfect_count,
                          linewidth=2.5, edgecolor="#CC0000", facecolor="none",
                          zorder=6)
    ax.add_patch(rect)
    ax.annotate(f"{perfect_count} perfect\n(Keshav V, Sackett)",
                xy=(12, perfect_count), xytext=(12, perfect_count + 5.5),
                fontsize=9, color="#111111", fontweight="bold",
                ha="center", va="bottom",
                arrowprops=dict(arrowstyle="->", color="#CC0000", lw=1.2))

fig.tight_layout()
out_path = os.path.join(OUT_DIR, "t20-2026-super8-histogram.png")
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out_path}")
plt.close()
