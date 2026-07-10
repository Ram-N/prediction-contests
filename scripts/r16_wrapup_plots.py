"""Generate score distribution plot for the R16 wrap-up blog post."""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "FIFA2026-r16-predictions.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "plots", "r16")

# Column name → winning team (full name as it appears in the CSV)
MATCH_WINNERS = {
    "CAN v MAR": "Morocco",
    "PAR v FRA": "France",
    "BRA v NOR": "Norway",
    "MEX v ENG": "England",
    "ESP v POR": "Spain",
    "USA v BEL": "Belgium",
    "EGY v ARG": "Argentina",
    "SUI v COL": "Switzerland",
}

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}
AI_DISPLAY = {
    "ChatGPT (AI)": "ChatGPT",
    "Claude (AI)": "Claude",
    "Gemini (AI)": "Gemini",
}
AI_COLORS = {"ChatGPT": "#10a37f", "Claude": "#cc785c", "Gemini": "#4285f4"}


def load_predictions():
    """Load R16 predictions, skip WOTC, deduplicate by name (keep last)."""
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    seen = {}
    for row in rows:
        name = row["Name"].strip()
        if name == "WOTC":
            continue
        seen[name] = row
    return list(seen.values())


def compute_scores(entries):
    """Return list of (name, pts, is_ai)."""
    results = []
    for entry in entries:
        name = entry["Name"].strip()
        correct = sum(
            1 for col, winner in MATCH_WINNERS.items()
            if entry.get(col, "").strip() == winner
        )
        results.append((name, correct * 4, name in AI_NAMES))
    return results


def plot_score_distribution(scores):
    human_scores = [s for _, s, ai in scores if not ai]
    ai_scores = [(AI_DISPLAY.get(n, n), s) for n, s, ai in scores if ai]
    n_humans = len(human_scores)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    score_vals = sorted(set(human_scores))
    score_counts = Counter(human_scores)

    ax.bar(score_vals, [score_counts[v] for v in score_vals], width=2.8,
           color="#3498db", edgecolor="white", linewidth=1.2, alpha=0.85)

    for pos in score_vals:
        height = score_counts[pos]
        if height > 0:
            ax.text(pos, height + 0.3, str(height), ha="center", va="bottom",
                    fontsize=11, fontweight="bold", color="#2c3e50")

    # Annotate AI scores
    max_bar = max(score_counts.values())
    ai_annotations = sorted(ai_scores, key=lambda x: (x[1], x[0]))
    for i, (name, score) in enumerate(ai_annotations):
        color = AI_COLORS.get(name, "#888888")
        y_pos = max_bar * 0.45 + i * 2.2
        x_text = max(score_vals) + 2
        ax.annotate(
            f"{name} ({score})",
            xy=(score, score_counts.get(score, 0) / 2),
            xytext=(x_text, y_pos),
            fontsize=10, fontweight="bold", color=color,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
        )

    ax.set_xlabel("R16 Score (8 matches × 4 pts, max 32)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Participants", fontsize=13, fontweight="bold")
    ax.set_title("R16 Final Score Distribution — Humans vs AI",
                 fontsize=15, fontweight="bold", pad=12)
    ax.set_xticks(score_vals)
    ax.set_xlim(min(score_vals) - 2, max(score_vals) + 8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    human_patch = mpatches.Patch(color="#3498db", alpha=0.85, label=f"Humans ({n_humans})")
    ax.legend(handles=[human_patch], fontsize=11, loc="upper left")

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, "r16_score_distribution.png")
    fig.savefig(outpath, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {outpath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    entries = load_predictions()
    print(f"Loaded {len(entries)} participants (excluding WOTC)")
    scores = compute_scores(entries)
    plot_score_distribution(scores)
    print("Done!")


if __name__ == "__main__":
    main()
