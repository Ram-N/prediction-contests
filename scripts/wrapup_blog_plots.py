"""Generate wrap-up blog plots for FIFA 2026 World Cup prediction contest.

Plots:
1. wrapup_top15_stacked.png  — Top finishers stacked bar (GS / R32 / R16 / ST-421)
2. wrapup_lr421_scores.png   — LR-421 final scores: top performers, AI vs humans
3. wrapup_ai_comparison.png  — AI vs human best/avg per round

Usage:
    cd scripts
    uv run python wrapup_blog_plots.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "wrapup")

# ---------------------------------------------------------------------------
# Data — extracted from the final leaderboard
# ---------------------------------------------------------------------------

# (name, gs, r32, r16, st421, is_ai)
OVERALL = [
    ("Subbu",            25, 26, 24, 28, False),
    ("bala varadarajan", 22, 26, 20, 28, False),
    ("Tees",             24, 26, 28, 16, False),
    ("ChatGPT",          24, 24, 24, 20, True),
    ("Claude",           20, 28, 24, 20, True),
    ("Aarush",           26, 28, 20, 16, False),
    ("Keshav V.",        21, 28, 20, 20, False),
    ("Rahul S.",         25, 24, 20, 20, False),
    ("Shaji",            21, 28, 20, 20, False),
    ("Alex",             27, 24, 20, 16, False),
    ("Gokul",            23, 28, 16, 20, False),
    ("Ranga Setlur",     21, 30, 20, 16, False),
    ("Gemini",           21, 28, 16, 20, True),
    ("Daniel",           24, 26, 24, 12, False),
    ("Goutham E.",       20, 26, 24, 16, False),
]

# LR-421 top scorers (name, pts, is_ai)
LR421 = [
    ("Guru Bhat",   12, False),
    ("Shaj",        12, False),
    ("Kunal Soni",  11, False),
    ("Manish B.",   11, False),
    ("Subbu",       11, False),
    ("Tees",        11, False),
    ("Vishal G.",   11, False),
    ("Claude",      10, True),
    ("Gemini",      10, True),
    ("Keshav N.",   10, False),
    ("Rupal",       10, False),
    ("Sri Iyer",    10, False),
    ("Rajesh",      10, False),
    ("ChatGPT",      9, True),
]

# AI per-round scores and human comparison (best human, avg human)
AI_ROUNDS = {
    # (chatgpt, claude, gemini, human_best, human_avg)
    "Group\nStage":  (24, 20, 21, 27, 20.5),
    "Round\nof 32":  (24, 28, 28, 30, 22.3),
    "Round\nof 16":  (24, 24, 16, 28, 18.5),
    "ST-421":        (20, 20, 20, 28, 16.8),
    "LR-421":        ( 9, 10, 10, 12,  7.4),
}

# Max possible per round
MAX_SCORES = {
    "Group\nStage": 32,
    "Round\nof 32": 32,
    "Round\nof 16": 32,
    "ST-421":       32,
    "LR-421":       12,
}

ROUND_COLORS = {
    "GS":    "#2196f3",
    "R32":   "#4caf50",
    "R16":   "#ff9800",
    "ST421": "#e91e63",
}

AI_COLORS = {
    "ChatGPT": "#10a37f",
    "Claude":  "#cc785c",
    "Gemini":  "#4285f4",
}


# ---------------------------------------------------------------------------
# Plot 1: Top 15 stacked bar
# ---------------------------------------------------------------------------
def plot_top15_stacked():
    names   = [p[0] for p in OVERALL]
    gs      = [p[1] for p in OVERALL]
    r32     = [p[2] for p in OVERALL]
    r16     = [p[3] for p in OVERALL]
    st421   = [p[4] for p in OVERALL]
    is_ai   = [p[5] for p in OVERALL]
    totals  = [a+b+c+d for a,b,c,d in zip(gs,r32,r16,st421)]

    x = np.arange(len(names))
    width = 0.62

    fig, ax = plt.subplots(figsize=(15, 6.5))

    b1 = ax.bar(x, gs,    width, label="Group Stage (max 32)", color=ROUND_COLORS["GS"])
    b2 = ax.bar(x, r32,   width, bottom=gs,                   label="Round of 32 (max 32)", color=ROUND_COLORS["R32"])
    b3 = ax.bar(x, r16,   width, bottom=[a+b for a,b in zip(gs,r32)],     label="Round of 16 (max 32)", color=ROUND_COLORS["R16"])
    b4 = ax.bar(x, st421, width, bottom=[a+b+c for a,b,c in zip(gs,r32,r16)], label="ST-421 (max 32)", color=ROUND_COLORS["ST421"])

    # Edge highlight for AIs
    for i, ai in enumerate(is_ai):
        if ai:
            ax.bar(i, totals[i], width, fill=False, edgecolor="black", linewidth=2.2, linestyle="--")

    # Total labels above bars
    for i, total in enumerate(totals):
        ax.text(i, total + 0.8, str(total), ha="center", va="bottom",
                fontsize=9, fontweight="bold",
                color="#111" if not is_ai[i] else "#555")

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=10, fontweight="bold", rotation=30, ha="right")
    ax.set_ylabel("Total Points", fontsize=11)
    ax.set_title("FIFA 2026 WC — Overall Top Finishers (by round contribution)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, 115)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend_items = [
        mpatches.Patch(color=ROUND_COLORS["GS"],    label="Group Stage (max 32)"),
        mpatches.Patch(color=ROUND_COLORS["R32"],   label="Round of 32 (max 32)"),
        mpatches.Patch(color=ROUND_COLORS["R16"],   label="Round of 16 (max 32)"),
        mpatches.Patch(color=ROUND_COLORS["ST421"], label="ST-421 (max 32)"),
        mpatches.Patch(facecolor="white", edgecolor="black", linewidth=2,
                       linestyle="--", label="AI model (dashed border)"),
    ]
    ax.legend(handles=legend_items, fontsize=9, loc="upper right", ncol=2)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "wrapup_top15_stacked.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 2: LR-421 final scores — horizontal bar
# ---------------------------------------------------------------------------
def plot_lr421_scores():
    names   = [e[0] for e in LR421]
    scores  = [e[1] for e in LR421]
    is_ai   = [e[2] for e in LR421]

    y = np.arange(len(names))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (name, score, ai) in enumerate(LR421):
        if score == 12:
            color = "#1a7a1a"   # perfect score — dark green
            edge  = "white"
        elif ai:
            color = AI_COLORS.get(name, "#888")
            edge  = "white"
        else:
            color = "#5b8dd9"   # normal human
            edge  = "white"

        ax.barh(i, score, color=color, edgecolor=edge, linewidth=1, height=0.65)

        # Score label inside
        label_x = score - 0.15 if score >= 10 else score + 0.1
        ha = "right" if score >= 10 else "left"
        ax.text(label_x, i, str(score), ha=ha, va="center",
                fontsize=11, fontweight="bold",
                color="white" if score >= 10 else "#333")

        # AI tag
        if ai:
            ax.text(score + 0.2, i, "[AI]", ha="left", va="center",
                    fontsize=9, color="#555", style="italic")

        # Perfect tag
        if score == 12:
            ax.text(score + 0.35, i, "PERFECT!", ha="left", va="center",
                    fontsize=9, fontweight="bold", color="#1a7a1a")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 14.5)
    ax.set_xlabel("Points (max 12)", fontsize=11)
    ax.set_title("LR-421 Final Scores — Long Range contest\n"
                 "Pick 4 SFs (1 pt each), 2 Finalists (2 pts each), Winner (4 pts)",
                 fontsize=13, fontweight="bold", pad=10)
    ax.axvline(x=12, color="#1a7a1a", linestyle="--", linewidth=1.2, alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "wrapup_lr421_scores.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Plot 3: AI performance comparison across all rounds
# ---------------------------------------------------------------------------
def plot_ai_comparison():
    rounds = list(AI_ROUNDS.keys())
    chatgpt_vals = [AI_ROUNDS[r][0] for r in rounds]
    claude_vals  = [AI_ROUNDS[r][1] for r in rounds]
    gemini_vals  = [AI_ROUNDS[r][2] for r in rounds]
    best_vals    = [AI_ROUNDS[r][3] for r in rounds]
    avg_vals     = [AI_ROUNDS[r][4] for r in rounds]
    max_vals     = [MAX_SCORES[r]  for r in rounds]

    # Normalize to % of max for comparability
    def pct(vals, maxes):
        return [100 * v / m for v, m in zip(vals, maxes)]

    cg_pct  = pct(chatgpt_vals, max_vals)
    cl_pct  = pct(claude_vals,  max_vals)
    ge_pct  = pct(gemini_vals,  max_vals)
    best_pct= pct(best_vals,    max_vals)
    avg_pct = pct(avg_vals,     max_vals)

    x = np.arange(len(rounds))
    width = 0.22

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(x - width,     cg_pct, width, label="ChatGPT", color=AI_COLORS["ChatGPT"], zorder=3)
    ax.bar(x,             cl_pct, width, label="Claude",  color=AI_COLORS["Claude"],  zorder=3)
    ax.bar(x + width,     ge_pct, width, label="Gemini",  color=AI_COLORS["Gemini"],  zorder=3)

    # Lines for human best and human average
    ax.plot(x, best_pct, "o--", color="#222", linewidth=1.8, markersize=7,
            label="Human best", zorder=4)
    ax.plot(x, avg_pct,  "s:",  color="#888", linewidth=1.5, markersize=6,
            label="Human average", zorder=4)

    # Value labels on bars
    for i, (cg, cl, ge) in enumerate(zip(cg_pct, cl_pct, ge_pct)):
        for offset, val, col in [(-width, cg, AI_COLORS["ChatGPT"]),
                                  (0,      cl, AI_COLORS["Claude"]),
                                  (+width, ge, AI_COLORS["Gemini"])]:
            ax.text(i + offset, val + 1.5, f"{val:.0f}%", ha="center",
                    va="bottom", fontsize=8, fontweight="bold", color="#222")

    ax.set_xticks(x)
    ax.set_xticklabels(rounds, fontsize=12, fontweight="bold")
    ax.set_ylabel("Score as % of maximum", fontsize=11)
    ax.set_title("AI models vs. humans — performance across all scoring rounds",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, 105)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.legend(fontsize=10, loc="lower right")

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "wrapup_ai_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {out}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_top15_stacked()
    plot_lr421_scores()
    plot_ai_comparison()
    print("All done!")


if __name__ == "__main__":
    main()
