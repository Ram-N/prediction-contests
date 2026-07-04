#!/usr/bin/env python3
"""Generate charts for the FIFA 2026 Group Stage blog post."""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')

# Group Stage scores (GS column only, excluding those with "-")
human_scores = [
    27,  # Alex
    26,  # Aarush
    25, 25,  # Rahul Santhanam, Subbu
    25,  # Amit Baranwal
    24, 24, 24,  # Daniel, Keshav Narasimhan, Tees
    23, 23,  # Gokul Krishnan, Ishaan
    23,  # Joydeep Dey
    23,  # Sri Iyer
    22, 22, 22, 22,  # bala, Chayan, Cheen, S Mahesh
    22,  # Vikram
    21, 21, 21, 21, 21, 21, 21, 21,  # Aravind, Keshav V, Kunal, Manoj, Neeraj, Rajesh, Ranga, Rupal
    21,  # Shaji
    20, 20,  # Goutham, MK (assuming from score)
    19, 19,  # Bharathkirishnan, Sackett
    18, 18, 18, 18, 18,  # Ashish Naik, Harsh, Ashish Kumar, Prasad R, Radhika
    17, 17, 17,  # D. Sivakumar, R. Santhanam, Ram N, Vishal Goyal
    16, 16,  # Guru Bhat, vivek
    15,  # Chandran
    13,  # Shriya
]

ai_scores = {
    'ChatGPT': 24,
    'Gemini': 21,
    'Claude': 20,
}

wotc_score = 22

# ---- Chart 1: Score Distribution with AI markers ----
fig, ax = plt.subplots(figsize=(10, 6))

bins = range(12, 29)
human_mean = np.mean(human_scores)
human_median = np.median(human_scores)

ax.hist(human_scores, bins=bins, color='#4A90D9', edgecolor='white', alpha=0.85, label='Human participants', align='left')

# Mark AI scores
colors = {'ChatGPT': '#10A37F', 'Gemini': '#4285F4', 'Claude': '#D97706'}
y_offsets = {'ChatGPT': 8.5, 'Gemini': 7, 'Claude': 5.5}

for name, score in ai_scores.items():
    ax.axvline(x=score, color=colors[name], linestyle='--', linewidth=2, alpha=0.8)
    ax.annotate(f'{name} ({score})', xy=(score, y_offsets[name]),
                fontsize=10, fontweight='bold', color=colors[name],
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=colors[name], alpha=0.9))

# Mark WOTC
ax.axvline(x=wotc_score, color='#888', linestyle=':', linewidth=2, alpha=0.7)
ax.annotate(f'WOTC ({wotc_score})', xy=(wotc_score, 10),
            fontsize=10, fontweight='bold', color='#555',
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', edgecolor='#888', alpha=0.9))

# Mark human median
ax.axvline(x=human_median, color='#E74C3C', linestyle='-', linewidth=1.5, alpha=0.6)
ax.annotate(f'Human median ({human_median:.0f})', xy=(human_median - 0.3, 11.5),
            fontsize=9, color='#E74C3C', ha='right', va='bottom')

ax.set_xlabel('Group Stage Score', fontsize=13)
ax.set_ylabel('Number of Participants', fontsize=13)
ax.set_title('FIFA 2026 Group Stage — Score Distribution', fontsize=15, fontweight='bold')
ax.set_xticks(range(13, 28))
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ram/projects/prediction-contests/img/soccer/gs_score_distribution.png', dpi=150)
print("Saved gs_score_distribution.png")

# ---- Chart 2: Common traps - teams everyone got wrong ----
# Let's show what % of people picked certain teams and whether they were right
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Traps: teams widely picked but eliminated, and surprises that qualified
traps = {
    'Korea Rep.\n(eliminated)': {'picked_pct': 70, 'correct': False},
    'Turkey\n(eliminated)': {'picked_pct': 45, 'correct': False},
    'Uruguay\n(eliminated)': {'picked_pct': 96, 'correct': False},
    'Ecuador\n(3rd, not top-2)': {'picked_pct': 66, 'correct': False},
    'Australia\n(qualified!)': {'picked_pct': 16, 'correct': True},
    'Cabo Verde\n(qualified!)': {'picked_pct': 2, 'correct': True},
    'Norway\n(qualified!)': {'picked_pct': 47, 'correct': True},
    'Croatia\n(qualified!)': {'picked_pct': 86, 'correct': True},
}

labels = list(traps.keys())
pcts = [v['picked_pct'] for v in traps.values()]
bar_colors = ['#E74C3C' if not v['correct'] else '#2ECC71' for v in traps.values()]

bars = ax2.bar(labels, pcts, color=bar_colors, edgecolor='white', width=0.7)
ax2.set_ylabel('% of Participants Who Picked', fontsize=12)
ax2.set_title('FIFA 2026 Group Stage — The Biggest Traps & Surprises', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 105)
ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar, pct in zip(bars, pcts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{pct}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#E74C3C', label='Widely picked but failed'),
    Patch(facecolor='#2ECC71', label='Qualified (correctly or as surprise)')
]
ax2.legend(handles=legend_elements, fontsize=10, loc='upper right')

plt.xticks(fontsize=9)
plt.tight_layout()
plt.savefig('/home/ram/projects/prediction-contests/img/soccer/gs_traps_surprises.png', dpi=150)
print("Saved gs_traps_surprises.png")

plt.close('all')
print("Done!")
