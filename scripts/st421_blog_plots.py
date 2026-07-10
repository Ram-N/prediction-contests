"""Generate blog plots for the ST-421 predictions analysis post."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "ST-421-Predictions-Clean.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "st421")

QF_MATCHES = [
    ("FRA v MAR", "France", "Morocco", "FRA", "MAR"),
    ("ESP v BEL", "Spain",  "Belgium", "ESP", "BEL"),
    ("ENG v NOR", "England","Norway",  "ENG", "NOR"),
    ("ARG v SUI", "Argentina","Switzerland","ARG","SUI"),
]
# Ordered by contestedness (most lopsided first, for the overview chart)
QF_ORDER_LOPSIDED = ["ARG v SUI", "FRA v MAR", "ESP v BEL", "ENG v NOR"]

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}
COLOR_FAV  = "#2ecc71"   # green  – heavy favourite
COLOR_CONT = "#f39c12"   # orange – contested
COLOR_EDGE = "#e74c3c"   # red    – real upset territory
COLOR_GREY = "#bdc3c7"

# Consistent team colours
TEAM_COLORS = {
    "France":      "#003399",
    "Morocco":     "#c1272d",
    "Spain":       "#c60b1e",
    "Belgium":     "#000000",
    "England":     "#ffffff",
    "Norway":      "#ef2b2d",
    "Argentina":   "#74acdf",
    "Switzerland": "#ff0000",
}
TEAM_TEXT = {
    "England": "#333333",   # white bar needs dark label
}


def load_predictions():
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    seen = {}
    for row in rows:
        seen[row["Name"].strip()] = row
    return list(seen.values())


# ---------------------------------------------------------------------------
# Plot 1: QF overview — horizontal stacked bar, one row per match
# ---------------------------------------------------------------------------
def plot_qf_overview(rows):
    total = len(rows)
    humans = [r for r in rows if r["Name"].strip() not in AI_NAMES]
    n_h = len(humans)

    # Compute counts: {col: {team_abbr: count_human, count_all}}
    data = []
    for col, t1_full, t2_full, a1, a2 in QF_MATCHES:
        h_picks = [r[col].strip() for r in humans]
        all_picks = [r[col].strip() for r in rows]
        h_t1 = sum(1 for p in h_picks if p == t1_full)
        h_t2 = sum(1 for p in h_picks if p == t2_full)
        pct_t1 = h_t1 * 100 / n_h
        pct_t2 = h_t2 * 100 / n_h
        data.append((col, a1, a2, pct_t1, pct_t2, h_t1, h_t2))

    # Sort: most lopsided first (largest leading %)
    data.sort(key=lambda x: -max(x[3], x[4]))

    fig, ax = plt.subplots(figsize=(11, 4.5))
    y_positions = range(len(data))
    bar_height = 0.55

    for i, (col, a1, a2, pct1, pct2, n1, n2) in enumerate(data):
        y = i
        # Left bar (favourite / team 1)
        c1 = TEAM_COLORS.get(
            next((t for c, t, *_ in QF_MATCHES if c == col), a1), "#3498db"
        )
        ax.barh(y, pct1, height=bar_height, color=c1, edgecolor="white", linewidth=0.8)
        # Right bar (underdog / team 2)
        col_info = next((m for m in QF_MATCHES if m[0] == col), None)
        c2 = TEAM_COLORS.get(col_info[2] if col_info else a2, "#e74c3c")
        ax.barh(y, pct2, left=pct1, height=bar_height, color=c2,
                edgecolor="white", linewidth=0.8, alpha=0.85)

        # Labels inside bars
        txt1_color = TEAM_TEXT.get(col_info[1] if col_info else a1, "white")
        txt2_color = TEAM_TEXT.get(col_info[2] if col_info else a2, "white")
        if pct1 > 8:
            ax.text(pct1 / 2, y, f"{a1}  {pct1:.0f}%", ha="center", va="center",
                    fontsize=11, fontweight="bold", color=txt1_color)
        if pct2 > 8:
            ax.text(pct1 + pct2 / 2, y, f"{pct2:.0f}%  {a2}", ha="center", va="center",
                    fontsize=11, fontweight="bold", color=txt2_color)

        # 50% reference
        ax.axvline(50, color="#7f8c8d", linestyle="--", linewidth=1, alpha=0.5)

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels([d[0] for d in data], fontsize=12, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of participants (humans only)", fontsize=11)
    ax.set_title("ST-421 Quarterfinal Picks — Human Field at a Glance",
                 fontsize=14, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "st421_qf_overview.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 2: Winner picks distribution
# ---------------------------------------------------------------------------
def plot_winner_picks(rows):
    humans = [r for r in rows if r["Name"].strip() not in AI_NAMES]
    ai     = [r for r in rows if r["Name"].strip() in AI_NAMES]

    h_counts = Counter(r["Winner"].strip() for r in humans)
    ai_picks = {r["Name"].strip(): r["Winner"].strip() for r in ai}

    ordered = sorted(h_counts.items(), key=lambda x: -x[1])
    teams   = [t for t, _ in ordered]
    counts  = [c for _, c in ordered]
    n_h     = len(humans)

    bar_colors = [TEAM_COLORS.get(t, "#3498db") for t in teams]
    edge_colors = ["#333333" if TEAM_COLORS.get(t, "#3498db") in ("#ffffff", "#000000")
                   else "white" for t in teams]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(teams)), counts, color=bar_colors, edgecolor=edge_colors,
                  linewidth=1.2, width=0.65)

    for i, (bar, cnt) in enumerate(zip(bars, counts)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{cnt}\n({cnt*100//n_h}%)", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#2c3e50")

    # Annotate AI picks below x-axis
    ai_label_colors = {"ChatGPT (AI)": "#10a37f", "Claude (AI)": "#cc785c",
                       "Gemini (AI)": "#4285f4"}
    ai_short = {"ChatGPT (AI)": "ChatGPT", "Claude (AI)": "Claude",
                "Gemini (AI)": "Gemini"}
    for ai_name, pick in ai_picks.items():
        if pick in teams:
            xi = teams.index(pick)
            color = ai_label_colors[ai_name]
            ax.annotate(
                f"[AI] {ai_short[ai_name]}",
                xy=(xi, 0), xytext=(xi, -2.8 - list(ai_picks.keys()).index(ai_name) * 1.4),
                ha="center", fontsize=8.5, fontweight="bold", color=color,
                annotation_clip=False,
            )

    ax.set_xticks(range(len(teams)))
    ax.set_xticklabels(teams, fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of picks (humans)", fontsize=11)
    ax.set_title("ST-421 — Who do people think will win the tournament?",
                 fontsize=14, fontweight="bold", pad=10)
    ax.set_ylim(0, max(counts) + 7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "st421_winner_picks.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 3: SF1 and SF2 picks side by side
# ---------------------------------------------------------------------------
def plot_sf_picks(rows):
    humans = [r for r in rows if r["Name"].strip() not in AI_NAMES]
    n_h = len(humans)

    sf1_counts = Counter(r["SF1"].strip() for r in humans)
    sf2_counts = Counter(r["SF2"].strip() for r in humans)

    sf1_order = sorted(sf1_counts.items(), key=lambda x: -x[1])
    sf2_order = sorted(sf2_counts.items(), key=lambda x: -x[1])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    def draw_sf(ax, counts_order, title, n):
        teams = [t for t, _ in counts_order]
        vals  = [c for _, c in counts_order]
        colors = [TEAM_COLORS.get(t, "#3498db") for t in teams]
        bars = ax.barh(range(len(teams)), vals, color=colors, edgecolor="white",
                       linewidth=1, height=0.55)
        for bar, cnt, team in zip(bars, vals, teams):
            txt_color = TEAM_TEXT.get(team, "white")
            label = f"{team}  —  {cnt} ({cnt*100//n}%)"
            if cnt > 3:
                ax.text(cnt - 0.5, bar.get_y() + bar.get_height() / 2,
                        label, ha="right", va="center",
                        fontsize=10, fontweight="bold", color=txt_color)
            else:
                ax.text(cnt + 0.3, bar.get_y() + bar.get_height() / 2,
                        label, ha="left", va="center",
                        fontsize=10, fontweight="bold", color="#2c3e50")
        ax.set_yticks([])
        ax.set_xlim(0, max(vals) + 12)
        ax.set_title(title, fontsize=13, fontweight="bold", pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xticks([])

    draw_sf(ax1, sf1_order, "SF1 Picks\n(FRA/MAR vs ESP/BEL half)", n_h)
    draw_sf(ax2, sf2_order, "SF2 Picks\n(ENG/NOR vs ARG/SUI half)", n_h)

    fig.suptitle("Who reaches the semifinals?", fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "st421_sf_picks.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = load_predictions()
    print(f"Loaded {len(rows)} participants")
    plot_qf_overview(rows)
    plot_winner_picks(rows)
    plot_sf_picks(rows)
    print("Done!")


if __name__ == "__main__":
    main()
