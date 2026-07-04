"""
Visualize Group Stage predictions for any FIFA 2026 group.

Usage:
    uv run --with openpyxl --with pandas --with matplotlib --with seaborn \
        python scripts/viz_group_predictions.py B

    uv run --with openpyxl --with pandas --with matplotlib --with seaborn \
        python scripts/viz_group_predictions.py A
"""

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CSV_PATH = PROJECT_ROOT / "active-contest" / "data" / "predictions" / "GroupStage-Predictions-Clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "active-contest" / "data" / "plots"

# Group compositions
GROUPS = {
    "A": ["Mexico", "South Africa", "Korea Republic", "Czechia"],
    "B": ["Canada", "Switzerland", "Qatar", "Bosnia & Herz."],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Ecuador", "Côte d'Ivoire", "Curaçao"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "IR Iran", "New Zealand"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cabo Verde"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Colombia", "Congo DR", "Uzbekistan"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Team colors (primary national colors)
TEAM_COLORS = {
    # Group A
    "Mexico": "#006847", "South Africa": "#007749",
    "Korea Republic": "#CD2E3A", "Czechia": "#11457E",
    # Group B
    "Canada": "#FF0000", "Switzerland": "#D52B1E",
    "Qatar": "#8D1B3D", "Bosnia & Herz.": "#002395",
    # Group C
    "Brazil": "#FFDF00", "Morocco": "#C1272D",
    "Haiti": "#00209F", "Scotland": "#003078",
    # Group D
    "USA": "#002868", "Paraguay": "#D52B1E",
    "Australia": "#00843D", "Türkiye": "#E30A17",
    # Group E
    "Germany": "#000000", "Ecuador": "#FFD100",
    "Côte d'Ivoire": "#FF8200", "Curaçao": "#002B7F",
    # Group F
    "Netherlands": "#FF6600", "Japan": "#BC002D",
    "Sweden": "#006AA7", "Tunisia": "#E70013",
    # Group G
    "Belgium": "#ED2939", "Egypt": "#CE1126",
    "IR Iran": "#239F40", "New Zealand": "#000000",
    # Group H
    "Spain": "#AA151B", "Uruguay": "#5CBFEB",
    "Saudi Arabia": "#006C35", "Cabo Verde": "#003893",
    # Group I
    "France": "#002395", "Senegal": "#00853F",
    "Iraq": "#CE1126", "Norway": "#EF2B2D",
    # Group J
    "Argentina": "#74ACDF", "Algeria": "#006233",
    "Austria": "#ED2939", "Jordan": "#007A3D",
    # Group K
    "Portugal": "#006600", "Colombia": "#FCD116",
    "Congo DR": "#007FFF", "Uzbekistan": "#1EB53A",
    # Group L
    "England": "#FFFFFF", "Croatia": "#FF0000",
    "Ghana": "#006B3F", "Panama": "#D21034",
}

# Lighter versions for 3rd place bars
def lighten(hex_color, factor=0.5):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


# Normalize team names from various CSV spellings
TEAM_ALIASES = {
    "Bosnia and Herzegovina": "Bosnia & Herz.",
    "Bosnia": "Bosnia & Herz.",
    "South Korea": "Korea Republic",
    "Korea": "Korea Republic",
    "Turkey": "Türkiye",
    "Turkiye": "Türkiye",
    "Iran": "IR Iran",
    "Cape Verde": "Cabo Verde",
    "DR Congo": "Congo DR",
    "Ivory Coast": "Côte d'Ivoire",
    "United States": "USA",
}


def normalize(team):
    team = team.strip()
    return TEAM_ALIASES.get(team, team)


def get_color(team):
    c = TEAM_COLORS.get(team, "#888888")
    # Some colors are too light/dark for bars — adjust
    if c in ("#FFFFFF", "#000000", "#FFDF00", "#FCD116", "#FFD100"):
        # Use a darker/more visible variant
        fallbacks = {"#FFFFFF": "#4A7CC9", "#000000": "#333333",
                     "#FFDF00": "#C8A600", "#FCD116": "#C8A600", "#FFD100": "#C8A600"}
        c = fallbacks.get(c, c)
    return c


def analyze_group(df, group_letter):
    teams = GROUPS[group_letter]
    n = len(df)

    top2_counts = Counter()
    third_counts = Counter()
    combos = Counter()
    has_third = 0

    for _, row in df.iterrows():
        # Parse R32 picks
        r32 = [normalize(t) for t in str(row[f"R32_{group_letter}"]).split(",")]
        for t in r32:
            top2_counts[t] += 1
        combo = tuple(sorted(r32))
        combos[combo] += 1

        # Parse 3rd place picks
        found_third = False
        for i in range(1, 9):
            val = row.get(f"3rd_{i}", "")
            if pd.notna(val) and str(val).startswith(f"{group_letter}:"):
                team = normalize(str(val).split(":", 1)[1])
                third_counts[team] += 1
                found_third = True
        if found_third:
            has_third += 1

    not_advancing = {t: n - top2_counts[t] - third_counts[t] for t in teams}

    return {
        "teams": teams,
        "n": n,
        "top2": top2_counts,
        "third": third_counts,
        "not_advancing": not_advancing,
        "combos": combos,
        "has_third": has_third,
    }


def _plot_fate(ax, data, group_letter):
    """Plot 1: Stacked horizontal bar — fate of each team."""
    teams = data["teams"]
    n = data["n"]
    y_pos = np.arange(len(teams))
    top2 = [data["top2"][t] for t in teams]
    third = [data["third"][t] for t in teams]
    out = [data["not_advancing"][t] for t in teams]

    ax.barh(y_pos, top2, color=[get_color(t) for t in teams],
            edgecolor="white", height=0.6)
    ax.barh(y_pos, third, left=top2,
            color=[lighten(get_color(t)) for t in teams],
            edgecolor="white", height=0.6)
    ax.barh(y_pos, out, left=[a + b for a, b in zip(top2, third)],
            color="#E0E0E0", edgecolor="white", height=0.6)

    for i, team in enumerate(teams):
        if top2[i] > 3:
            ax.text(top2[i] / 2, i, str(top2[i]),
                    ha="center", va="center", fontweight="bold", color="white", fontsize=12)
        if third[i] > 2:
            ax.text(top2[i] + third[i] / 2, i, str(third[i]),
                    ha="center", va="center", fontweight="bold", fontsize=11)
        if out[i] > 3:
            ax.text(top2[i] + third[i] + out[i] / 2, i, str(out[i]),
                    ha="center", va="center", color="#666", fontsize=11)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(teams, fontsize=12, fontweight="bold")
    ax.set_xlabel(f"Number of Predictors (out of {n})", fontsize=11)
    ax.set_title("Predicted Fate of Each Team", fontsize=14, fontweight="bold", pad=12)
    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, fc="#666"),
            plt.Rectangle((0, 0), 1, 1, fc="#AAA"),
            plt.Rectangle((0, 0), 1, 1, fc="#E0E0E0"),
        ],
        labels=["Top 2", "3rd Place", "Not Advancing"],
        loc="lower right", fontsize=9,
    )
    ax.set_xlim(0, n + 2)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _plot_combos(ax, data, group_letter):
    """Plot 2: Top 2 pair combinations."""
    sorted_combos = sorted(data["combos"].items(), key=lambda x: -x[1])
    combo_labels = [f"{c[0]}\n+ {c[1]}" for c, _ in sorted_combos]
    combo_counts = [cnt for _, cnt in sorted_combos]

    palette = plt.cm.Set2(np.linspace(0, 1, len(combo_labels)))
    ax.barh(range(len(combo_labels)), combo_counts,
            color=palette, edgecolor="white", height=0.6)
    for i, count in enumerate(combo_counts):
        ax.text(count + 0.5, i, str(count), va="center", fontweight="bold", fontsize=12)

    ax.set_yticks(range(len(combo_labels)))
    ax.set_yticklabels(combo_labels, fontsize=10, fontweight="bold")
    ax.set_xlabel("Number of Predictors", fontsize=11)
    ax.set_title("Most Popular Top 2 Combinations", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlim(0, max(combo_counts) + 5)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _plot_third_pie(ax, data, group_letter):
    """Plot 3: Pie — does this group produce a 3rd place qualifier?"""
    n = data["n"]
    has = data["has_third"]
    no = n - has
    wedges, texts, autotexts = ax.pie(
        [has, no],
        labels=[f"Yes\n({has})", f"No\n({no})"],
        colors=["#2E86AB", "#E0E0E0"],
        explode=(0.05, 0),
        autopct="%1.0f%%", startangle=90,
        textprops={"fontsize": 13, "fontweight": "bold"},
        pctdistance=0.55,
    )
    for at in autotexts:
        at.set_fontsize(14)
        at.set_fontweight("bold")
    ax.set_title(
        f"Will a Group {group_letter} Team Qualify\nas Best 3rd Place?",
        fontsize=14, fontweight="bold", pad=12,
    )


def _plot_third_bar(ax, data, group_letter):
    """Plot 4: Which team is the 3rd place pick?"""
    teams = data["teams"]
    n = data["n"]
    has = data["has_third"]
    third_teams = sorted(
        [(t, data["third"].get(t, 0)) for t in teams],
        key=lambda x: -x[1],
    )
    t_labels = [t[0] for t in third_teams]
    t_counts = [t[1] for t in third_teams]
    t_colors = [get_color(t) for t in t_labels]

    ax.bar(range(len(t_labels)), t_counts, color=t_colors, edgecolor="white", width=0.6)
    for i, count in enumerate(t_counts):
        if count > 0:
            ax.text(i, count + 0.3, str(count), ha="center", fontweight="bold", fontsize=13)

    ax.set_xticks(range(len(t_labels)))
    ax.set_xticklabels(t_labels, fontsize=11, fontweight="bold")
    ax.set_ylabel("Number of Predictors", fontsize=11)
    ax.set_title(
        f"If 3rd Place From Group {group_letter},\nWhich Team?",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_ylim(0, max(t_counts) + 3 if max(t_counts) > 0 else 5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.text(
        0.95, 0.95,
        f"{has} of {n} predictors\nexpect a Group {group_letter} team\nto qualify as 3rd place",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color="#555", fontstyle="italic",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0f0f0", edgecolor="#ccc"),
    )


def _save_individual(plot_fn, data, group_letter, suffix, figsize=(8, 6)):
    """Save a single chart as its own PNG."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(
        f"Group {group_letter}: {'  •  '.join(data['teams'])}",
        fontsize=12, fontweight="bold", color="#555", y=0.98,
    )
    plot_fn(ax, data, group_letter)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = OUTPUT_DIR / f"group_{group_letter.lower()}_{suffix}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"  Saved {out_path.name}")
    plt.close()


def plot_group(data, group_letter):
    teams = data["teams"]
    n = data["n"]

    # ── Combined 2x2 figure ───────────────────────────────────
    fig = plt.figure(figsize=(16, 14))
    fig.suptitle(
        f"FIFA 2026 Group {group_letter} — How Did {n} Predictors See It?",
        fontsize=20, fontweight="bold", y=0.97,
    )
    fig.text(
        0.5, 0.94,
        "  •  ".join(teams),
        ha="center", fontsize=13, color="#555",
    )

    _plot_fate(fig.add_subplot(2, 2, 1), data, group_letter)
    _plot_combos(fig.add_subplot(2, 2, 2), data, group_letter)
    _plot_third_pie(fig.add_subplot(2, 2, 3), data, group_letter)
    _plot_third_bar(fig.add_subplot(2, 2, 4), data, group_letter)

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    out_path = OUTPUT_DIR / f"group_{group_letter.lower()}_predictions.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved {out_path}")
    plt.close()

    # ── Individual PNGs ───────────────────────────────────────
    _save_individual(_plot_fate, data, group_letter, "fate", figsize=(9, 5))
    _save_individual(_plot_combos, data, group_letter, "combos", figsize=(8, 5))
    _save_individual(_plot_third_pie, data, group_letter, "third_pie", figsize=(7, 6))
    _save_individual(_plot_third_bar, data, group_letter, "third_bar", figsize=(8, 5))


def main():
    if len(sys.argv) < 2:
        print("Usage: python viz_group_predictions.py <GROUP_LETTER>")
        print("  e.g. python viz_group_predictions.py B")
        print("  or   python viz_group_predictions.py ALL")
        sys.exit(1)

    arg = sys.argv[1].upper()
    df = pd.read_csv(CSV_PATH)

    if arg == "ALL":
        for letter in GROUPS:
            data = analyze_group(df, letter)
            plot_group(data, letter)
    else:
        if arg not in GROUPS:
            print(f"Unknown group: {arg}. Must be A–L or ALL.")
            sys.exit(1)
        data = analyze_group(df, arg)
        plot_group(data, arg)


if __name__ == "__main__":
    main()
