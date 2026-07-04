"""
T20 2026 Final Wrap-up Visualizations
Generates charts for the contest wrap-up blog post.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(script_dir, '../../img/cricket')
os.makedirs(img_dir, exist_ok=True)

# ── Final overall scores (humans only, all 3 stages complete) ──────────────
# From leaderboard.md — Group Stage + Super 8 + KO & Finals
scores = {
    'Aditya': 37, 'Keshav Venkatesh': 36, 'Ramesh Srinivasan': 36,
    'Ashish': 35, 'Dhanush Ekollu': 35, 'Rankanathan v s': 35, 'Sackett': 35,
    'Shiv Iyer': 34,
    'Ranga': 33, 'Vivek': 33,
    'Kshitij': 32,
    'Aakarsh Ekollu': 30, 'Chink': 30, 'Goutham Ekollu': 30, 'Manoj S': 30,
    'Rupal': 30, 'S. Parthasarathy': 30, 'The Kasher': 30, 'Vivek J': 30,
    'Abhinav S': 29, 'Alok': 29, 'Ram': 29,
    'Bharathkirishnan': 28, 'Krishnaveni': 28, 'Pradeep': 28,
    'R Santhanam': 28, 'Sahana': 28,
    '237 Narmada': 27, 'S V Madhavan': 27, 'Shajman': 27,
    'D. Sivakumar': 26, 'Ishaan': 26, 'Manish Bhatt': 26, 'Siva Kantamneni': 26,
    'Mukund N.': 24, 'Niraj': 24, 'Radhika Santhanam': 24, 'Rajesh': 24, 'Sri Iyer': 24,
    'Harsh': 23,
    'P. Amritha': 22, 'Subbu Mahadevan': 22,
    'Chayan': 21, 'Keshav Narasimhan': 21,
    'Sreenivas G': 19,
    'bala': 18, 'Dodo': 18, 'Tees': 18,
    'Hauroon': 15,
    'Shriya': 13,
    'Bharath Sridharan': 12,
}

# AI scores
ai_scores = {
    'Perplexity 🤖': 33,
    'Gemini 🤖': 31,
    'ChatGPT 🤖': 30,
    'Claude 🤖': 25,
}

human_vals = sorted(scores.values())
all_human = np.array(human_vals)

# ── Chart 1: Final Score Distribution (humans vs AI) ──────────────────────
fig, ax = plt.subplots(figsize=(12, 6))

bins = range(10, 42, 2)
n_h, bins_h, patches_h = ax.hist(all_human, bins=bins, color='steelblue',
                                   edgecolor='white', linewidth=0.8, alpha=0.85,
                                   label=f'Humans ({len(all_human)})')

# Mark AI scores as vertical lines
ai_colors = {'Perplexity 🤖': '#e67e22', 'Gemini 🤖': '#2ecc71',
             'ChatGPT 🤖': '#9b59b6', 'Claude 🤖': '#e74c3c'}
for name, score in ai_scores.items():
    ax.axvline(score, color=ai_colors[name], linewidth=2.5,
               linestyle='--', label=f'{name}: {score}', alpha=0.9)

# Winner annotation
ax.axvline(37, color='gold', linewidth=3, linestyle='-', alpha=0.6)
ax.annotate('🏆 Aditya (37)', xy=(37, 0), xytext=(37.2, 8),
            fontsize=10, fontweight='bold', color='#b8860b',
            arrowprops=dict(arrowstyle='->', color='#b8860b'))

human_median = np.median(all_human)
ax.axvline(human_median, color='steelblue', linewidth=1.5, linestyle=':',
           alpha=0.7, label=f'Human median: {human_median:.0f}')

ax.set_title('T20 2026 — Final Score Distribution', fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel('Final Score (max 44)', fontsize=12)
ax.set_ylabel('Number of Participants', fontsize=12)
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(10, 42)
plt.tight_layout()
out = os.path.join(img_dir, 't20-2026-final-score-distribution.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'✓ Saved: {out}')
plt.close()

# ── Chart 2: Stage-by-stage AI vs Human average ───────────────────────────
stages = ['Group Stage', 'Super 8', 'KO & Finals', 'Total']
# Human averages (from leaderboard data)
h_group = np.mean([14,10,12,12,10,12,12,8,10,10,10,7,11,12,12,10,10,10,
                   12,12,12,7,10,11,10,10,12,10,12,10,11,7,7,12,10,8,10,
                   12,9,11,10,10,10,10,12,9,10,10,10,10,10,12,10,9,10])
h_s8  = np.mean([11,12,11,11,9,7,12,10,11,7,10,7,3,6,8,8,8,6,
                  8,12,9,7,8,10,8,8,6,5,8,6,6,8,8,6,10,6,4,
                  11,4,11,10,1,5,6,8,8,2,9,8,4,2,4,8,1,2])
h_ko  = np.mean([12,12,16,12,16,16,12,16,12,16,12,16,16,16,4,4,12,12,12,
                  12,12,16,12,8,12,12,8,12,12,4,12,4,12,12,8,8,12,4,4,4,
                  4,12,12,12,12,0,12,4,12,0,0,4,0,4,0,0])
h_total = h_group + h_s8 + h_ko

# AI averages
ai_g  = np.mean([12, 12, 11, 12])   # ChatGPT, Claude, Gemini, Perplexity
ai_s8 = np.mean([6, 9, 8, 9])
ai_ko = np.mean([12, 4, 12, 12])
ai_total = ai_g + ai_s8 + ai_ko

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(stages))
w = 0.35
bars_h = ax.bar(x - w/2, [h_group, h_s8, h_ko, h_total],
                w, label='Humans (avg)', color='steelblue', edgecolor='white')
bars_a = ax.bar(x + w/2, [ai_g, ai_s8, ai_ko, ai_total],
                w, label='AI models (avg)', color='#e67e22', edgecolor='white')

for bar in bars_h:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
for bar in bars_a:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)

# Shade the total bars differently
bars_h[-1].set_color('#1a5276')
bars_a[-1].set_color('#a04000')

ax.set_title('AI vs Humans — Average Score by Stage', fontsize=15, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=11)
ax.set_ylabel('Average Points', fontsize=11)
ax.legend(fontsize=11)
ax.set_ylim(0, 32)
ax.axvline(2.5, color='grey', linewidth=0.8, linestyle='--', alpha=0.5)
ax.text(2.55, 29, 'Full contest →', fontsize=8, color='grey')
plt.tight_layout()
out = os.path.join(img_dir, 't20-2026-ai-vs-humans-stages.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'✓ Saved: {out}')
plt.close()

# ── Chart 3: KO & Finals score distribution ───────────────────────────────
ko_scores_all = (
    [16]*11 +   # NZ✓ IND✓ IND✓
    [12]*37 +   # SA✗ IND✓ IND✓
    [8]*4  +    # mixed SF, wrong final
    [4]*12 +    # 4 pts
    [0]*9        # 0 pts
)
ko_human = ko_scores_all  # all from human predictions

fig, ax = plt.subplots(figsize=(9, 5))
ko_vals, ko_counts = np.unique(ko_human, return_counts=True)
colors = {0: '#e74c3c', 4: '#e67e22', 8: '#f1c40f', 12: '#2ecc71', 16: '#27ae60'}
bar_colors = [colors[v] for v in ko_vals]
bars = ax.bar(ko_vals, ko_counts, width=2.5, color=bar_colors, edgecolor='white', linewidth=1)
for bar, cnt in zip(bars, ko_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            str(cnt), ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_xticks([0, 4, 8, 12, 16])
ax.set_xticklabels(['0\n(0/3)', '4\n(1/3)', '8\n(2/3\nor Finals)', '12\n(2/3+Final)', '16\n(3/3 Perfect)'],
                    fontsize=10)
ax.set_title('KO & Finals Score Distribution\n(SF1: 4pts · SF2: 4pts · Final: 8pts)', fontsize=14, fontweight='bold')
ax.set_xlabel('KO & Finals Score', fontsize=11)
ax.set_ylabel('Number of Participants', fontsize=11)
ax.set_xlim(-3, 19)

# Annotate India pickers
ax.annotate('India backers\nclean up!', xy=(12, 37), xytext=(10, 32),
            fontsize=9, color='#1a6e1a', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#1a6e1a'))
plt.tight_layout()
out = os.path.join(img_dir, 't20-2026-ko-score-distribution.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'✓ Saved: {out}')
plt.close()

print('\nAll charts generated successfully!')
