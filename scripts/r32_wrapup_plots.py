"""Generate plots for the R32 final wrap-up blog post (all 16 matches)."""
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
PREDICTIONS_CSV = os.path.join(PROJECT_ROOT, "active-contest", "data", "predictions", "FIFA-2026-R32-predictions.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "r32")

# All 16 R32 matches: (match_num, team1_full, team2_full, abbr1, abbr2, winner_full)
ALL_MATCHES = [
    (73, "South Africa", "Canada", "RSA", "CAN", "Canada"),
    (74, "Germany", "Paraguay", "GER", "PAR", "Paraguay"),
    (75, "Netherlands", "Morocco", "NED", "MAR", "Morocco"),
    (76, "Brazil", "Japan", "BRA", "JPN", "Brazil"),
    (77, "France", "Sweden", "FRA", "SWE", "France"),
    (78, "Ivory Coast", "Norway", "CIV", "NOR", "Norway"),
    (79, "Mexico", "Ecuador", "MEX", "ECU", "Mexico"),
    (80, "England", "DR Congo", "ENG", "DRC", "England"),
    (81, "United States", "Bosnia", "USA", "BIH", "United States"),
    (82, "Belgium", "Senegal", "BEL", "SEN", "Belgium"),
    (83, "Croatia", "Portugal", "CRO", "POR", "Portugal"),
    (84, "Spain", "Austria", "ESP", "AUT", "Spain"),
    (85, "Switzerland", "Algeria", "SUI", "ALG", "Switzerland"),
    (86, "Argentina", "Cabo Verde", "ARG", "CPV", "Argentina"),
    (87, "Ghana", "Colombia", "GHA", "COL", "Colombia"),
    (88, "Australia", "Egypt", "AUS", "EGY", "Egypt"),
]

AI_NAMES = {"ChatGPT", "Claude", "Gemini", "ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}
AI_DISPLAY = {"ChatGPT (AI)": "ChatGPT", "Claude (AI)": "Claude", "Gemini (AI)": "Gemini",
              "ChatGPT": "ChatGPT", "Claude": "Claude", "Gemini": "Gemini"}


def load_predictions():
    """Load predictions from clean CSV (no email). Exclude WOTC."""
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Deduplicate by name (keep latest)
    seen = {}
    for row in rows:
        name = row["Name"].strip()
        if name == "WOTC":
            continue
        seen[name] = row

    return list(seen.values())


def compute_r32_scores(entries):
    """Compute R32 scores for all 16 matches."""
    scores = []
    for entry in entries:
        name = entry["Name"].strip()
        correct = 0
        for match_num, t1, t2, a1, a2, winner in ALL_MATCHES:
            pick = entry[f"Match {match_num}"].strip()
            if pick == winner:
                correct += 1
        is_ai = name in AI_NAMES
        scores.append((name, correct * 2, is_ai))
    return scores


def plot_score_distribution(scores):
    """Histogram of final R32 scores, humans vs AI highlighted."""
    human_scores = [s for name, s, ai in scores if not ai]
    ai_scores = [(AI_DISPLAY.get(name, name), s) for name, s, ai in scores if ai]
    n_humans = len(human_scores)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    score_vals = sorted(set(human_scores))
    score_counts = Counter(human_scores)

    ax.bar(score_vals, [score_counts[v] for v in score_vals], width=1.4,
           color='#3498db', edgecolor='white', linewidth=1.2, alpha=0.85)

    for pos in score_vals:
        height = score_counts[pos]
        if height > 0:
            ax.text(pos, height + 0.3, str(height), ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#2c3e50')

    # Mark AI scores
    ai_colors = {'ChatGPT': '#10a37f', 'Claude': '#cc785c', 'Gemini': '#4285f4'}
    ai_annotations = sorted(ai_scores, key=lambda x: (x[1], x[0]))
    max_bar = max(score_counts.values())

    for i, (name, score) in enumerate(ai_annotations):
        color = ai_colors.get(name, '#888888')
        y_pos = max_bar * 0.5 + i * 2.0
        x_text = max(score_vals) + 1.2
        ax.annotate(f'{name} ({score})',
                    xy=(score, score_counts.get(score, 0) / 2),
                    xytext=(x_text, y_pos),
                    fontsize=10, fontweight='bold', color=color,
                    ha='left', va='center',
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

    ax.set_xlabel('R32 Score (16 matches, max 32)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Participants', fontsize=13, fontweight='bold')
    ax.set_title('R32 Final Score Distribution — Humans vs AI',
                 fontsize=15, fontweight='bold', pad=12)
    ax.set_xticks(score_vals)
    ax.set_xlim(min(score_vals) - 1.5, max(score_vals) + 5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    human_patch = mpatches.Patch(color='#3498db', alpha=0.85, label=f'Humans ({n_humans})')
    ax.legend(handles=[human_patch], fontsize=11, loc='upper left')

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r32_final_score_distribution.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved {outpath}")


def plot_consensus_vs_reality(entries):
    """Horizontal bar chart: for each match, show % who picked the winner."""
    match_data = []
    for match_num, t1, t2, a1, a2, winner in ALL_MATCHES:
        field = f"Match {match_num}"
        picks = [e[field].strip() for e in entries]
        total = len(picks)
        winner_count = sum(1 for p in picks if p == winner)
        pct = winner_count * 100 / total
        winner_abbr = a1 if winner == t1 else a2
        is_upset = pct < 50
        match_data.append((f"{a1} v {a2}", winner_abbr, pct, is_upset))

    # Reverse so first match is at top
    match_data = match_data[::-1]

    fig, ax = plt.subplots(figsize=(10, 8))

    labels = [m[0] for m in match_data]
    pcts = [m[2] for m in match_data]
    winners = [m[1] for m in match_data]
    upsets = [m[3] for m in match_data]

    colors = ['#e74c3c' if u else '#27ae60' for u in upsets]

    bars = ax.barh(range(len(labels)), pcts, color=colors, edgecolor='white',
                   linewidth=1.2, height=0.6)

    ax.axvline(x=50, color='#95a5a6', linestyle=':', linewidth=1.5, alpha=0.7)

    for i, (bar, pct, winner, upset) in enumerate(zip(bars, pcts, winners, upsets)):
        label = f"✓ {winner} — {pct:.0f}%"
        if pct > 30:
            ax.text(bar.get_width() - 2, bar.get_y() + bar.get_height() / 2,
                    label, ha='right', va='center', fontsize=10, fontweight='bold',
                    color='white')
        else:
            ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                    label, ha='left', va='center', fontsize=10, fontweight='bold',
                    color='#2c3e50')

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_xlabel('')
    ax.set_title('R32 Final Results: How Many Predicted Each Winner?',
                 fontsize=14, fontweight='bold', pad=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])

    green_patch = mpatches.Patch(color='#27ae60', label='Majority got it right')
    red_patch = mpatches.Patch(color='#e74c3c', label='Upset — majority got it wrong')
    ax.legend(handles=[green_patch, red_patch], fontsize=10, loc='lower right')

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r32_final_consensus_vs_reality.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved {outpath}")


def plot_top_scorers(scores):
    """Horizontal bar chart of top R32 scorers."""
    # Sort by score descending, take top 15
    sorted_scores = sorted(scores, key=lambda x: -x[1])[:15]
    sorted_scores = sorted_scores[::-1]  # reverse for plotting (highest at top)

    fig, ax = plt.subplots(figsize=(9, 6))

    names = [s[0] for s in sorted_scores]
    pts = [s[1] for s in sorted_scores]
    is_ai = [s[2] for s in sorted_scores]

    colors = ['#cc785c' if ai else '#3498db' for ai in is_ai]
    # Gold for the winner
    colors[-1] = '#f1c40f'  # top scorer

    bars = ax.barh(range(len(names)), pts, color=colors, edgecolor='white',
                   linewidth=1.2, height=0.65)

    for i, (bar, pt, name) in enumerate(zip(bars, pts, names)):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                str(pt), ha='left', va='center', fontsize=11, fontweight='bold',
                color='#2c3e50')

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel('R32 Points (max 32)', fontsize=12, fontweight='bold')
    ax.set_title('R32 Top Scorers', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlim(0, 34)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    human_patch = mpatches.Patch(color='#3498db', label='Human')
    ai_patch = mpatches.Patch(color='#cc785c', label='AI')
    gold_patch = mpatches.Patch(color='#f1c40f', label='R32 Winner')
    ax.legend(handles=[gold_patch, human_patch, ai_patch], fontsize=10, loc='lower right')

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r32_top_scorers.png")
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
    plot_top_scorers(scores)
    print("\nDone! Plots saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
