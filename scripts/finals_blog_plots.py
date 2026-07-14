"""Generate blog plots for the FIFA 2026 semifinals + final preview post.

Compares LR-421 (early June predictions) vs ST-421 (mid-July predictions) on:
- Finalist picks
- Winner picks
- SF breakdown in ST-421
- The France-Spain collision irony from LR-421
"""

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

ST421_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "ST-421-Predictions-Clean.csv"
)
LR421_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "LR-421-Predictions-Clean.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "finals")

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}

# Teams still alive after QFs
ALIVE = {"France", "Spain", "England", "Argentina"}

TEAM_COLORS = {
    "France":      "#003399",
    "Spain":       "#c60b1e",
    "England":     "#ffffff",
    "Argentina":   "#74acdf",
    "Norway":      "#ef2b2d",
    "Morocco":     "#c1272d",
    "Belgium":     "#222222",
    "Portugal":    "#006600",
    "Brazil":      "#009c3b",
    "Germany":     "#ffcc00",
    "Netherlands": "#ff6600",
    "Switzerland": "#ff0000",
}
# Text color overrides for light-background bars
TEAM_TEXT = {
    "England": "#333333",
    "Germany": "#333333",
}


def bar_style(team):
    """Return (facecolor, edgecolor, linewidth, hatch) for a team's bar."""
    color = TEAM_COLORS.get(team, "#888")
    eliminated = team not in ALIVE

    if team == "England":
        edge = "#333333"
        lw = 2.5
    elif color in ("#222222", "#000000"):
        edge = "#aaa"
        lw = 1.2
    else:
        edge = "white"
        lw = 1.0

    hatch = "///" if eliminated else None
    return color, edge, lw, hatch


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    seen = {}
    for row in rows:
        name = row["Name"].strip()
        if name:
            seen[name] = row
    return list(seen.values())


def humans(rows):
    return [r for r in rows if r["Name"].strip() not in AI_NAMES]


def add_eliminated_note(ax):
    """Add a small legend note explaining hatch = eliminated."""
    patch = mpatches.Patch(facecolor="#ccc", hatch="///", edgecolor="#888",
                           label="Team already eliminated")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [patch], labels=labels + ["Team already eliminated"],
              fontsize=9, loc="upper right")


# ---------------------------------------------------------------------------
# Plot 1: Finalist picks — LR-421 vs ST-421 grouped bar
# ST-421 finalists = SF1 + SF2 winners predicted
# LR-421 finalists = Finalist_1 + Finalist_2 columns
# ---------------------------------------------------------------------------
def plot_finalist_comparison(st_rows, lr_rows):
    st_humans = humans(st_rows)
    lr_humans = humans(lr_rows)
    n_st = len(st_humans)
    n_lr = len(lr_humans)

    # ST-421: each person predicts 2 finalists (SF1 + SF2)
    st_picks = []
    for r in st_humans:
        st_picks += [r["SF1"].strip(), r["SF2"].strip()]
    st_counts = Counter(st_picks)

    # LR-421: Finalist_1 and Finalist_2
    lr_picks = []
    for r in lr_humans:
        lr_picks += [r["Finalist_1"].strip(), r["Finalist_2"].strip()]
    lr_counts = Counter(lr_picks)

    # Union sorted by ST-421 count desc
    all_teams = set(st_counts) | set(lr_counts)
    ordered = sorted(all_teams, key=lambda t: (-st_counts.get(t, 0), -lr_counts.get(t, 0)))

    x = np.arange(len(ordered))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 5.5))

    lr_vals = [lr_counts.get(t, 0) for t in ordered]
    st_vals = [st_counts.get(t, 0) for t in ordered]

    # Draw LR-421 bars (hatched/faded = "early picks")
    for i, (team, val) in enumerate(zip(ordered, lr_vals)):
        color, edge, lw, hatch = bar_style(team)
        # LR-421 always gets additional cross-hatch for "early" feel; if eliminated, combine
        lr_hatch = "///" if team not in ALIVE else ".."
        ax.bar(x[i] - width / 2, val, width,
               color=color, alpha=0.45, edgecolor=edge if team == "England" else "#888",
               linewidth=lw, hatch=lr_hatch)
        if val > 0:
            ax.text(x[i] - width / 2, val + 0.3, f"{val}",
                    ha="center", va="bottom", fontsize=8.5, color="#555")

    # Draw ST-421 bars (solid = latest picks)
    for i, (team, val) in enumerate(zip(ordered, st_vals)):
        color, edge, lw, hatch = bar_style(team)
        ax.bar(x[i] + width / 2, val, width,
               color=color, edgecolor=edge, linewidth=lw,
               hatch=hatch if hatch else None)
        if val > 0:
            txt_col = TEAM_TEXT.get(team, "white") if color == "#ffffff" else "#222"
            ax.text(x[i] + width / 2, val + 0.3, f"{val}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#222")

    ax.set_xticks(x)
    ax.set_xticklabels(ordered, fontsize=11, fontweight="bold")
    ax.set_ylabel("Times picked as a finalist", fontsize=11)
    ax.set_title("Who reaches the Final? — early (LR-421) vs late (ST-421) predictions",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, max(max(st_vals), max(lr_vals)) + 8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    lr_patch = mpatches.Patch(facecolor="#aaa", alpha=0.5, hatch="..",
                               label=f"LR-421 early picks (n={n_lr} humans, 2×picks each)")
    st_patch = mpatches.Patch(facecolor="#aaa", label=f"ST-421 late picks (n={n_st} humans, SF1+SF2 picks)")
    elim_patch = mpatches.Patch(facecolor="#ccc", hatch="///", edgecolor="#888",
                                 label="Team already eliminated (hatched bars)")
    ax.legend(handles=[lr_patch, st_patch, elim_patch], fontsize=9, loc="upper right")

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_finalist_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 2: Winner picks — LR-421 vs ST-421 grouped bar chart
# ---------------------------------------------------------------------------
def plot_winner_comparison(st_rows, lr_rows):
    st_humans = humans(st_rows)
    lr_humans = humans(lr_rows)

    st_winners = Counter(r["Winner"].strip() for r in st_humans)
    lr_winners = Counter(r["Winner"].strip() for r in lr_humans)

    all_teams = set(st_winners) | set(lr_winners)
    ordered = sorted(all_teams, key=lambda t: (-st_winners.get(t, 0), -lr_winners.get(t, 0)))

    n_st = len(st_humans)
    n_lr = len(lr_humans)

    x = np.arange(len(ordered))
    width = 0.38

    fig, ax = plt.subplots(figsize=(13, 5.5))

    lr_vals = [lr_winners.get(t, 0) for t in ordered]
    st_vals = [st_winners.get(t, 0) for t in ordered]

    # LR-421 bars (faded, with hatch for eliminated teams)
    for i, (team, val) in enumerate(zip(ordered, lr_vals)):
        color, edge, lw, hatch = bar_style(team)
        lr_hatch = "///" if team not in ALIVE else ".."
        ax.bar(x[i] - width / 2, val, width,
               color=color, alpha=0.45,
               edgecolor=edge if team == "England" else "#888",
               linewidth=lw, hatch=lr_hatch)
        if val > 0:
            ax.text(x[i] - width / 2, val + 0.2,
                    f"{val}\n({val*100//n_lr}%)",
                    ha="center", va="bottom", fontsize=8, color="#555")

    # ST-421 bars (solid, with hatch for eliminated teams)
    for i, (team, val) in enumerate(zip(ordered, st_vals)):
        color, edge, lw, hatch = bar_style(team)
        ax.bar(x[i] + width / 2, val, width,
               color=color, edgecolor=edge, linewidth=lw,
               hatch=hatch if hatch else None)
        if val > 0:
            ax.text(x[i] + width / 2, val + 0.2,
                    f"{val}\n({val*100//n_st}%)",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#222")

    ax.set_xticks(x)
    ax.set_xticklabels(ordered, fontsize=11, fontweight="bold")
    ax.set_ylabel("Number of winner picks (humans)", fontsize=11)
    ax.set_title("Who wins the World Cup? — early (LR-421) vs late (ST-421) predictions",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, max(max(st_vals), max(lr_vals)) + 9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    lr_patch = mpatches.Patch(facecolor="#aaa", alpha=0.5, hatch="..",
                               label=f"LR-421 early picks  (n={n_lr} humans)")
    st_patch = mpatches.Patch(facecolor="#aaa",
                               label=f"ST-421 late picks  (n={n_st} humans)")
    elim_patch = mpatches.Patch(facecolor="#ccc", hatch="///", edgecolor="#888",
                                 label="Team already eliminated")
    ax.legend(handles=[lr_patch, st_patch, elim_patch], fontsize=9, loc="upper right")

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_winner_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 3: ST-421 Semi-final breakdown — two panels, SF1 and SF2
# ---------------------------------------------------------------------------
def plot_sf_breakdown(st_rows):
    st_humans = humans(st_rows)
    n_h = len(st_humans)

    sf1_counts = Counter(r["SF1"].strip() for r in st_humans)
    sf2_counts = Counter(r["SF2"].strip() for r in st_humans)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    fig.suptitle("ST-421: Who wins each semifinal?", fontsize=15, fontweight="bold", y=1.02)

    def draw_panel(ax, counts, title, n):
        ordered = sorted(counts.items(), key=lambda x: -x[1])
        teams = [t for t, _ in ordered]
        vals  = [v for _, v in ordered]

        for i, (team, val) in enumerate(zip(teams, vals)):
            color, edge, lw, hatch = bar_style(team)
            bar = ax.barh(i, val, color=color, edgecolor=edge, linewidth=lw,
                          height=0.55, hatch=hatch if hatch else None)
            txt_color = TEAM_TEXT.get(team, "white")
            pct = val * 100 // n
            label = f"  {team}  {val} ({pct}%)"
            if val >= max(vals) * 0.3:
                ax.text(val - 0.4, i, label.strip(),
                        ha="right", va="center", fontsize=11, fontweight="bold", color=txt_color)
            else:
                ax.text(val + 0.3, i, label.strip(),
                        ha="left", va="center", fontsize=11, fontweight="bold", color="#333")

        ax.set_yticks([])
        ax.set_xlim(0, max(vals) + 16)
        ax.set_title(title, fontsize=13, fontweight="bold", pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xticks([])

        # Eliminated note
        elim_patch = mpatches.Patch(facecolor="#ccc", hatch="///", edgecolor="#888",
                                     label="Already eliminated")
        ax.legend(handles=[elim_patch], fontsize=8.5, loc="lower right")

    draw_panel(ax1, sf1_counts, "SF1  (France half vs Spain half)", n_h)
    draw_panel(ax2, sf2_counts, "SF2  (England half vs Argentina half)", n_h)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_sf_breakdown.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 4: The France-Spain collision — LR-421 finalist pair analysis
# ---------------------------------------------------------------------------
def plot_france_spain_collision(lr_rows):
    lr_humans = humans(lr_rows)
    n_h = len(lr_humans)

    categories = []
    for r in lr_humans:
        f1 = r["Finalist_1"].strip()
        f2 = r["Finalist_2"].strip()
        pair = {f1, f2}
        has_fra = "France" in pair
        has_esp = "Spain" in pair

        if has_fra and has_esp:
            categories.append("France & Spain\n(same semi — final impossible!)")
        elif has_esp:
            categories.append("Spain + other\n(not France)")
        elif has_fra:
            categories.append("France + other\n(not Spain)")
        else:
            categories.append("Neither France\nnor Spain")

    cat_counts = Counter(categories)
    label_order = [
        "France & Spain\n(same semi — final impossible!)",
        "Spain + other\n(not France)",
        "France + other\n(not Spain)",
        "Neither France\nnor Spain",
    ]
    colors_map = {
        "France & Spain\n(same semi — final impossible!)": "#e74c3c",
        "Spain + other\n(not France)":                    "#c60b1e",
        "France + other\n(not Spain)":                    "#003399",
        "Neither France\nnor Spain":                       "#95a5a6",
    }

    vals   = [cat_counts.get(lbl, 0) for lbl in label_order]
    colors = [colors_map[lbl] for lbl in label_order]

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for i, (lbl, val, col) in enumerate(zip(label_order, vals, colors)):
        ax.barh(i, val, color=col, edgecolor="white", linewidth=1.2, height=0.6)
        if val > 0:
            pct = val * 100 // n_h
            ax.text(val + 0.3, i, f"{val} people  ({pct}%)",
                    ha="left", va="center", fontsize=11, fontweight="bold", color="#333")

    ax.set_yticks(range(len(label_order)))
    ax.set_yticklabels(label_order, fontsize=11)
    ax.set_xlim(0, max(vals) + 18)
    ax.set_title("LR-421: How many predicted a France vs Spain Final?\n"
                 "(Spoiler: they're in the same semifinal bracket)",
                 fontsize=13, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_fra_esp_collision.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 5: Dream final tracker — top final matchup combos in ST-421
# ---------------------------------------------------------------------------
def plot_dream_finals(st_rows):
    st_humans = humans(st_rows)
    n_h = len(st_humans)

    final_pairs = []
    for r in st_humans:
        f1 = r["SF1"].strip()
        f2 = r["SF2"].strip()
        pair = tuple(sorted([f1, f2]))
        final_pairs.append(pair)

    pair_counts = Counter(final_pairs)
    ordered = sorted(pair_counts.items(), key=lambda x: -x[1])
    top = ordered[:8]

    labels = [f"{t[0][0]} vs {t[0][1]}" for t in top]
    vals   = [t[1] for t in top]

    # Color by the "headlining" team (first alphabetically)
    bar_colors = [TEAM_COLORS.get(pair[0], "#3498db") for pair, _ in top]
    bar_edges  = ["#333" if c == "#ffffff" else "white" for c in bar_colors]
    bar_lws    = [2.5 if c == "#ffffff" else 1.0 for c in bar_colors]

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, (val, col, edge, lw) in enumerate(zip(vals, bar_colors, bar_edges, bar_lws)):
        ax.barh(i, val, color=col, edgecolor=edge, linewidth=lw, height=0.6)
        pct = val * 100 // n_h
        txt_color = TEAM_TEXT.get(top[i][0][0], "white")
        ax.text(val - 0.3, i, f"{val} ({pct}%)",
                ha="right", va="center", fontsize=10.5, fontweight="bold", color=txt_color)

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=12, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, max(vals) + 5)
    ax.set_title("ST-421: What Final are people predicting?",
                 fontsize=14, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_dream_final.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 6: Simple 4-bar chart — ST-421 winner picks, alive teams only
# ---------------------------------------------------------------------------
def plot_st421_winner_simple(st_rows):
    st_humans = humans(st_rows)
    n_h = len(st_humans)

    all_rows = st_rows  # includes AIs
    ai_winner_picks = {
        r["Name"].strip(): r["Winner"].strip()
        for r in all_rows if r["Name"].strip() in AI_NAMES
    }
    # Display name + brand color for each AI
    AI_DISPLAY = {
        "ChatGPT (AI)": ("ChatGPT", "#10a37f"),
        "Claude (AI)":  ("Claude",  "#cc785c"),
        "Gemini (AI)":  ("Gemini",  "#4285f4"),
    }

    winner_counts = Counter(r["Winner"].strip() for r in st_humans)

    # Only the 4 teams still in the tournament, sorted by count
    alive_order = sorted(ALIVE, key=lambda t: -winner_counts.get(t, 0))
    vals = [winner_counts.get(t, 0) for t in alive_order]

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, (team, val) in enumerate(zip(alive_order, vals)):
        color, edge, lw, _ = bar_style(team)
        ax.bar(i, val, color=color, edgecolor=edge, linewidth=lw, width=0.55)
        pct = val * 100 // n_h
        txt_col = TEAM_TEXT.get(team, "white")
        if val >= 8:
            ax.text(i, val / 2, f"{val}\n({pct}%)",
                    ha="center", va="center", fontsize=14, fontweight="bold", color=txt_col)
        else:
            ax.text(i, val + 0.4, f"{val}\n({pct}%)",
                    ha="center", va="bottom", fontsize=12, fontweight="bold", color="#222")

    # Annotate AI picks below the x-axis, stacked per bar
    # Build a mapping: team -> list of (display_name, color)
    ai_by_team = {t: [] for t in alive_order}
    for ai_name, pick in ai_winner_picks.items():
        if pick in ai_by_team:
            disp, col = AI_DISPLAY[ai_name]
            ai_by_team[pick].append((disp, col))

    y_base = -1.8   # starting y below axis (in data coords)
    y_step = -1.4

    for i, team in enumerate(alive_order):
        for j, (disp, col) in enumerate(ai_by_team[team]):
            ax.text(i, y_base + j * y_step, f"[AI] {disp}",
                    ha="center", va="top", fontsize=9, fontweight="bold",
                    color=col, clip_on=False, transform=ax.transData)

    ax.set_xticks(range(len(alive_order)))
    ax.set_xticklabels(alive_order, fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of picks (humans)", fontsize=11)
    ax.set_title(f"ST-421: Who do {n_h} participants think will win the World Cup?",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, max(vals) + 6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "finals_st421_winner_simple.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    st_rows = load_csv(ST421_CSV)
    lr_rows = load_csv(LR421_CSV)
    print(f"ST-421: {len(st_rows)} participants ({len(humans(st_rows))} humans)")
    print(f"LR-421: {len(lr_rows)} participants ({len(humans(lr_rows))} humans)")

    plot_st421_winner_simple(st_rows)
    plot_finalist_comparison(st_rows, lr_rows)
    plot_winner_comparison(st_rows, lr_rows)
    plot_sf_breakdown(st_rows)
    plot_france_spain_collision(lr_rows)
    plot_dream_finals(st_rows)
    print("All done!")


if __name__ == "__main__":
    main()
