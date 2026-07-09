"""Generate bar plots for each ST-421 QF match showing pick percentages."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(PROJECT_ROOT, "active-contest", "data", "predictions",
                               "ST-421-Predictions-Clean.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "st421")

# (match_label, team1_full, team2_full, abbr1, abbr2)
QF_MATCHES = [
    ("FRA v MAR", "France", "Morocco", "FRA", "MAR"),
    ("ESP v BEL", "Spain", "Belgium", "ESP", "BEL"),
    ("ENG v NOR", "England", "Norway", "ENG", "NOR"),
    ("ARG v SUI", "Argentina", "Switzerland", "ARG", "SUI"),
]

TEAM_COLORS = {
    "France": "#002395",
    "Morocco": "#C1272D",
    "Spain": "#AA151B",
    "Belgium": "#ED2939",
    "England": "#CF081F",
    "Norway": "#EF2B2D",
    "Argentina": "#75AADB",
    "Switzerland": "#FF0000",
}

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}


def load_predictions():
    """Load clean predictions CSV (no email column, already deduplicated)."""
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_match_plot(match_label, team1_full, team2_full, abbr1, abbr2, entries):
    """Generate a horizontal bar plot for a single QF match."""
    # Exclude AI entries from percentages (match R16 script behavior)
    human_entries = [e for e in entries if e["Name"] not in AI_NAMES]
    picks = [e[match_label].strip() for e in human_entries]
    total = len(picks)

    counter = Counter(picks)
    count1 = counter.get(team1_full, 0)
    count2 = counter.get(team2_full, 0)
    pct1 = count1 * 100 / total
    pct2 = count2 * 100 / total

    teams = [team2_full, team1_full]  # bottom to top
    pcts = [pct2, pct1]
    counts = [count2, count1]
    colors = [TEAM_COLORS.get(team2_full, "#888888"),
              TEAM_COLORS.get(team1_full, "#888888")]
    abbrs = [abbr2, abbr1]

    fig, ax = plt.subplots(figsize=(8, 2.8))

    bars = ax.barh(range(len(teams)), pcts, color=colors,
                   edgecolor="#333333", linewidth=0.8, height=0.6)

    for bar, pct, count, team in zip(bars, pcts, counts, teams):
        label = f"{pct:.0f}% ({count}/{total})"
        if pct > 25:
            ax.text(bar.get_width() - 1.5, bar.get_y() + bar.get_height() / 2,
                    label, ha='right', va='center', fontsize=13,
                    fontweight='bold', color='white')
        else:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    label, ha='left', va='center', fontsize=13,
                    fontweight='bold', color='#333333')

    ax.set_yticks(range(len(teams)))
    ax.set_yticklabels([f"{t} ({a})" for t, a in zip(teams, abbrs)],
                       fontsize=13, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_xlabel("")
    ax.set_title(f"QF: {team1_full} vs {team2_full}",
                 fontsize=14, fontweight='bold', pad=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()

    safe_label = match_label.replace(" ", "_")
    outpath = os.path.join(OUTPUT_DIR, f"st421_{safe_label}.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved {outpath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    entries = load_predictions()
    human_count = sum(1 for e in entries if e["Name"] not in AI_NAMES)
    print(f"Loaded {len(entries)} entries ({human_count} humans)")

    for match_label, team1, team2, abbr1, abbr2 in QF_MATCHES:
        generate_match_plot(match_label, team1, team2, abbr1, abbr2, entries)

    print(f"\nAll {len(QF_MATCHES)} QF plots saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
