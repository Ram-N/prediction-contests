"""Generate bar plots for each R16 match showing pick percentages."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026",
                               "raw-predictions", "FIFA2026-r16-predictions - Sheet1.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "r16")

# (match_label, team1_full, team2_full, abbr1, abbr2)
# team1 is listed first in the CSV column header "X v Y"
MATCHES = [
    ("CAN v MAR", "Canada", "Morocco", "CAN", "MAR"),
    ("PAR v FRA", "Paraguay", "France", "PAR", "FRA"),
    ("BRA v NOR", "Brazil", "Norway", "BRA", "NOR"),
    ("MEX v ENG", "Mexico", "England", "MEX", "ENG"),
    ("ESP v POR", "Spain", "Portugal", "ESP", "POR"),
    ("USA v BEL", "United States", "Belgium", "USA", "BEL"),
    ("EGY v ARG", "Egypt", "Argentina", "EGY", "ARG"),
    ("SUI v COL", "Switzerland", "Colombia", "SUI", "COL"),
]

# National team colors
TEAM_COLORS = {
    "Canada": "#FF0000",
    "Morocco": "#C1272D",
    "Paraguay": "#D52B1E",
    "France": "#002395",
    "Brazil": "#FFDF00",
    "Norway": "#EF2B2D",
    "Mexico": "#006847",
    "England": "#CF081F",
    "Spain": "#AA151B",
    "Portugal": "#006600",
    "United States": "#002868",
    "Belgium": "#ED2939",
    "Egypt": "#CE1126",
    "Argentina": "#75AADB",
    "Switzerland": "#FF0000",
    "Colombia": "#FCD116",
}

# AI entry names (share Ram's email but are separate entries)
AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}


def load_predictions():
    """Load and deduplicate predictions (by email, keep latest).

    AI entries (name contains '(AI)') are keyed by name, not email,
    so they don't overwrite each other or Ram's entry.
    """
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    seen = {}
    for row in rows:
        name = row["Name"].strip()
        email = row["Email"].strip().lower()
        ts = row["Timestamp"].strip()

        if name in AI_NAMES:
            key = name
        else:
            key = email

        if key not in seen or ts > seen[key]["Timestamp"]:
            seen[key] = row

    return list(seen.values())


def generate_match_plot(match_label, team1_full, team2_full, abbr1, abbr2, entries):
    """Generate a horizontal bar plot for a single R16 match."""
    picks = [e[match_label].strip() for e in entries]
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

    fig, ax = plt.subplots(figsize=(8, 2.8))

    bars = ax.barh(range(len(teams)), pcts, color=colors,
                   edgecolor="#333333", linewidth=0.8, height=0.6)

    # Add percentage + count labels
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
    ax.set_yticklabels([f"{t} ({a})" for t, a in
                        zip(teams, [abbr2, abbr1])],
                       fontsize=13, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_xlabel("")
    ax.set_title(f"R16: {team1_full} vs {team2_full}",
                 fontsize=14, fontweight='bold', pad=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()

    # Filename: r16_CAN_v_MAR.png
    safe_label = match_label.replace(" ", "_")
    outpath = os.path.join(OUTPUT_DIR, f"r16_{safe_label}.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved {outpath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    entries = load_predictions()
    print(f"Loaded {len(entries)} participants")

    for match_label, team1, team2, abbr1, abbr2 in MATCHES:
        generate_match_plot(match_label, team1, team2, abbr1, abbr2, entries)

    print(f"\nAll {len(MATCHES)} plots saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
