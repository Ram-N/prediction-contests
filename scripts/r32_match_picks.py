"""Generate bar plots for each R32 match showing pick percentages."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026", "raw-predictions", "FIFA-2026-R32-predictions.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "r32")

MATCHES = [
    (73, "South Africa", "Canada", "RSA", "CAN"),
    (74, "Germany", "Paraguay", "GER", "PAR"),
    (75, "Netherlands", "Morocco", "NED", "MAR"),
    (76, "Brazil", "Japan", "BRA", "JPN"),
    (77, "France", "Sweden", "FRA", "SWE"),
    (78, "Ivory Coast", "Norway", "CIV", "NOR"),
    (79, "Mexico", "Ecuador", "MEX", "ECU"),
    (80, "England", "DRC", "ENG", "DRC"),
    (81, "United States", "Bosnia & Herzegovina", "USA", "BIH"),
    (82, "Belgium", "Senegal", "BEL", "SEN"),
    (83, "Croatia", "Portugal", "CRO", "POR"),
    (84, "Spain", "Austria", "ESP", "AUT"),
    (85, "Switzerland", "Algeria", "SUI", "ALG"),
    (86, "Argentina", "Cape Verde", "ARG", "CPV"),
    (87, "Ghana", "Colombia", "GHA", "COL"),
    (88, "Australia", "Egypt", "AUS", "EGY"),
]

# National team colors
TEAM_COLORS = {
    "South Africa": "#007749",
    "Canada": "#FF0000",
    "Germany": "#000000",
    "Paraguay": "#D52B1E",
    "Netherlands": "#FF6600",
    "Morocco": "#C1272D",
    "Brazil": "#FFDF00",
    "Japan": "#BC002D",
    "France": "#002395",
    "Sweden": "#006AA7",
    "Ivory Coast": "#FF8200",
    "Norway": "#EF2B2D",
    "Mexico": "#006847",
    "Ecuador": "#FFD100",
    "England": "#CF081F",
    "DRC": "#007FFF",
    "United States": "#002868",
    "Bosnia & Herzegovina": "#002395",
    "Belgium": "#ED2939",
    "Senegal": "#00853F",
    "Croatia": "#FF0000",
    "Portugal": "#006600",
    "Spain": "#AA151B",
    "Austria": "#ED2939",
    "Switzerland": "#FF0000",
    "Algeria": "#006233",
    "Argentina": "#75AADB",
    "Cape Verde": "#003893",
    "Ghana": "#FCD116",
    "Colombia": "#FCD116",
    "Australia": "#00843D",
    "Egypt": "#CE1126",
}


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


def generate_match_plot(match_num, team1_full, team2_full, abbr1, abbr2, entries):
    """Generate a horizontal bar plot for a single R32 match."""
    field = f"Match {match_num}"
    picks = [e[field].strip() for e in entries]
    total = len(picks)

    counter = Counter(picks)
    count1 = counter.get(team1_full, 0)
    count2 = counter.get(team2_full, 0)
    pct1 = count1 * 100 / total
    pct2 = count2 * 100 / total

    teams = [team2_full, team1_full]  # bottom to top
    pcts = [pct2, pct1]
    counts = [count2, count1]
    colors = [TEAM_COLORS.get(team2_full, "#888888"), TEAM_COLORS.get(team1_full, "#888888")]

    # Handle edge case where both colors are very similar or dark
    fig, ax = plt.subplots(figsize=(8, 2.8))

    bars = ax.barh(range(len(teams)), pcts, color=colors, edgecolor="#333333", linewidth=0.8, height=0.6)

    # Add percentage + count labels
    for bar, pct, count, team in zip(bars, pcts, counts, teams):
        label = f"{pct:.0f}% ({count}/{total})"
        # Place label inside bar if wide enough, else outside
        if pct > 25:
            ax.text(bar.get_width() - 1.5, bar.get_y() + bar.get_height() / 2,
                    label, ha='right', va='center', fontsize=13, fontweight='bold', color='white')
        else:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    label, ha='left', va='center', fontsize=13, fontweight='bold', color='#333333')

    ax.set_yticks(range(len(teams)))
    ax.set_yticklabels([f"{t} ({a})" for t, a in zip(teams, [abbr2, abbr1])],
                       fontsize=13, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_xlabel("")
    ax.set_title(f"Match {match_num}: {team1_full} vs {team2_full}",
                 fontsize=14, fontweight='bold', pad=10)

    # Clean up
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()

    outpath = os.path.join(OUTPUT_DIR, f"r32_match_{match_num}.png")
    fig.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved {outpath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    entries = load_predictions()
    print(f"Loaded {len(entries)} participants (excluding WOTC)")

    for match_num, team1, team2, abbr1, abbr2 in MATCHES:
        generate_match_plot(match_num, team1, team2, abbr1, abbr2, entries)

    print(f"\nAll 16 plots saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
