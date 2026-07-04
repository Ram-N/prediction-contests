"""Generate plots for the R32 halftime blog post."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026", "raw-predictions", "FIFA-2026-R32-predictions.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "r32")

# 7 decided matches: (match_num, team1_full, team2_full, abbr1, abbr2, winner_full)
DECIDED = [
    (73, "South Africa", "Canada", "RSA", "CAN", "Canada"),
    (74, "Germany", "Paraguay", "GER", "PAR", "Paraguay"),
    (75, "Netherlands", "Morocco", "NED", "MAR", "Morocco"),
    (76, "Brazil", "Japan", "BRA", "JPN", "Brazil"),
    (77, "France", "Sweden", "FRA", "SWE", "France"),
    (78, "Ivory Coast", "Norway", "CIV", "NOR", "Norway"),
    (79, "Mexico", "Ecuador", "MEX", "ECU", "Mexico"),
]

AI_NAMES = {"ChatGPT", "Claude", "Gemini", "ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}
AI_DISPLAY = {"ChatGPT (AI)": "ChatGPT", "Claude (AI)": "Claude", "Gemini (AI)": "Gemini",
              "ChatGPT": "ChatGPT", "Claude": "Claude", "Gemini": "Gemini"}


def load_predictions():
    """Load and deduplicate predictions (by email, keep latest). Exclude WOTC."""
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    seen = {}
    for row in rows:
        name = row["Name"].strip()
        if name == "WOTC":
            continue
        email = row["Email"].strip().lower()
        if not email:
            email = f"__ai__{name}"
        seen[email] = row

    return list(seen.values())


def compute_r32_scores(entries):
    """Compute R32 scores for the 7 decided matches."""
    scores = []
    for entry in entries:
        name = entry["Name"].strip()
        correct = 0
        for match_num, t1, t2, a1, a2, winner in DECIDED:
            pick = entry[f"Match {match_num}"].strip()
            if pick == winner:
                correct += 1
        is_ai = name in AI_NAMES
        scores.append((name, correct * 2, is_ai))
    return scores


def plot_score_distribution(scores):
    """Histogram of R32 scores, humans vs AI highlighted."""
    human_scores = [s for name, s, ai in scores if not ai]
    ai_scores = [(AI_DISPLAY.get(name, name), s) for name, s, ai in scores if ai]
    n_humans = len(human_scores)

    fig, ax = plt.subplots(figsize=(9, 5))

    # Use explicit score values as categories
    score_vals = sorted(set(human_scores))
    score_counts = Counter(human_scores)

    bar_positions = score_vals
    bar_heights = [score_counts[v] for v in score_vals]

    ax.bar(bar_positions, bar_heights, width=1.4, color='#3498db',
           edgecolor='white', linewidth=1.2, alpha=0.85)

    # Label bars with count
    for pos, height in zip(bar_positions, bar_heights):
        if height > 0:
            ax.text(pos, height + 0.3, str(height), ha='center', va='bottom',
                    fontsize=12, fontweight='bold', color='#2c3e50')

    # Mark AI scores with arrows pointing to their bars
    ai_colors = {'ChatGPT': '#10a37f', 'Claude': '#cc785c', 'Gemini': '#4285f4'}
    # Place annotations to the right side to avoid title overlap
    ai_annotations = []
    for name, score in ai_scores:
        ai_annotations.append((name, score))
    # Sort by score so we can space them
    ai_annotations.sort(key=lambda x: (x[1], x[0]))

    max_bar = max(bar_heights)
    # Place all AI labels to the right of the chart
    for i, (name, score) in enumerate(ai_annotations):
        color = ai_colors.get(name, '#888888')
        # Stagger vertically on the right side
        y_pos = max_bar * 0.45 + i * 2.5
        x_text = max(score_vals) + 0.8
        ax.annotate(f'{name} ({score})',
                    xy=(score, score_counts.get(score, 0) / 2),
                    xytext=(x_text, y_pos),
                    fontsize=10, fontweight='bold', color=color,
                    ha='left', va='center',
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

    ax.set_xlabel('R32 Score (7 of 16 matches)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Participants', fontsize=13, fontweight='bold')
    ax.set_title('R32 Score Distribution — Humans vs AI', fontsize=15, fontweight='bold', pad=12)
    ax.set_xticks(score_vals)
    ax.set_xlim(min(score_vals) - 1.5, max(score_vals) + 4.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    human_patch = mpatches.Patch(color='#3498db', alpha=0.85, label=f'Humans ({n_humans})')
    ax.legend(handles=[human_patch], fontsize=11, loc='upper left')

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r32_score_distribution.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved {outpath}")


def plot_consensus_vs_reality(entries):
    """Horizontal bar chart: for each decided match, show % who picked the winner."""
    match_data = []
    for match_num, t1, t2, a1, a2, winner in DECIDED:
        field = f"Match {match_num}"
        picks = [e[field].strip() for e in entries]
        total = len(picks)
        winner_count = sum(1 for p in picks if p == winner)
        pct = winner_count * 100 / total
        loser = t1 if winner == t2 else t2
        loser_abbr = a1 if winner == t2 else a2
        winner_abbr = a1 if winner == t1 else a2
        is_upset = pct < 50
        match_data.append((f"{a1} v {a2}", winner_abbr, pct, is_upset))

    # Reverse so first match is at top
    match_data = match_data[::-1]

    fig, ax = plt.subplots(figsize=(10, 5))

    labels = [m[0] for m in match_data]
    pcts = [m[2] for m in match_data]
    winners = [m[1] for m in match_data]
    upsets = [m[3] for m in match_data]

    colors = ['#e74c3c' if u else '#27ae60' for u in upsets]

    bars = ax.barh(range(len(labels)), pcts, color=colors, edgecolor='white',
                   linewidth=1.2, height=0.6)

    # 50% reference line
    ax.axvline(x=50, color='#95a5a6', linestyle=':', linewidth=1.5, alpha=0.7)

    for i, (bar, pct, winner, upset) in enumerate(zip(bars, pcts, winners, upsets)):
        # Winner label inside or outside bar
        label = f"✓ {winner} — {pct:.0f}% picked"
        if pct > 30:
            ax.text(bar.get_width() - 2, bar.get_y() + bar.get_height() / 2,
                    label, ha='right', va='center', fontsize=11, fontweight='bold',
                    color='white')
        else:
            ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                    label, ha='left', va='center', fontsize=11, fontweight='bold',
                    color='#2c3e50')

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=12, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_xlabel('')
    ax.set_title('R32 Results: How Many Predicted the Winner?',
                 fontsize=15, fontweight='bold', pad=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])

    # Legend
    green_patch = mpatches.Patch(color='#27ae60', label='Majority got it right')
    red_patch = mpatches.Patch(color='#e74c3c', label='Upset — majority got it wrong')
    ax.legend(handles=[green_patch, red_patch], fontsize=10, loc='lower left',
              bbox_to_anchor=(0.55, 0.0))

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r32_consensus_vs_reality.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved {outpath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    entries = load_predictions()
    print(f"Loaded {len(entries)} participants (excluding WOTC)")

    scores = compute_r32_scores(entries)
    plot_score_distribution(scores)
    plot_consensus_vs_reality(entries)
    print("\nDone!")


if __name__ == "__main__":
    main()
