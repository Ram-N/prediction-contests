"""
Score FIFA 2026 Long-Range 4-2-1 predictions.

Reads predictions + results → applies strikethrough to eliminated teams →
generates 421-index.md with predictions table and leaderboard.

Input:
  - active-contest/data/predictions/LR-421-Predictions-Clean.csv (predictions)
  - active-contest/results/LR421-results.csv (eliminated/advancing teams)

Output:
  - active-contest/421-index.md (full page with predictions table + leaderboard)

Results CSV format:
  TEAM_ABBREV, RESULT
  where RESULT is:
    -1  = eliminated (red strikethrough in predictions)
    +1  = reached semifinals (1 pt for semifinalist pickers)
    +2  = reached final (2 pts for finalist pickers)
    +4  = won the World Cup (4 pts for winner pickers)

Usage:
  cd scripts
  uv run python score_fifa_lr421.py
"""

import csv
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "LR-421-Predictions-Clean.csv"
)
RESULTS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "results", "LR421-results.csv"
)
OUTPUT_MD = os.path.join(PROJECT_ROOT, "active-contest", "421-index.md")

# Normalize team abbreviations between results file and predictions
RESULTS_ABBREV_NORMALIZE = {
    "SPA": "Spain",
    "GER": "Germany",
    "NED": "Netherlands",
    "BRA": "Brazil",
    "FRA": "France",
    "ENG": "England",
    "ARG": "Argentina",
    "POR": "Portugal",
    "MEX": "Mexico",
    "USA": "USA",
    "COL": "Colombia",
    "MOR": "Morocco",
}

# Map full team names (as in predictions CSV) to abbreviations (as in results CSV)
TEAM_NAME_TO_ABBREV = {
    "Spain": "ESP",
    "France": "FRA",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "England": "ENG",
    "Germany": "GER",
    "Netherlands": "NED",
    "Portugal": "POR",
    "Mexico": "MEX",
    "USA": "USA",
    "Colombia": "COL",
    "Morocco": "MOR",
    "Belgium": "BEL",
    "Switzerland": "SUI",
    "Norway": "NOR",
    "Croatia": "CRO",
    "Australia": "AUS",
    "Egypt": "EGY",
    "Ivory Coast": "CIV",
    "Senegal": "SEN",
    "Ghana": "GHA",
    "Japan": "JPN",
    "South Korea": "KOR",
    "Uruguay": "URU",
    "Chile": "CHI",
    "Ecuador": "ECU",
    "Paraguay": "PAR",
    "Canada": "CAN",
    "Algeria": "ALG",
    "Saudi Arabia": "KSA",
    "Austria": "AUT",
    "Sweden": "SWE",
    "Tunisia": "TUN",
    "Iran": "IRN",
    "Qatar": "QAT",
    "South Africa": "RSA",
    "Czech Republic": "CZE",
    "Bosnia and Herzegovina": "BIH",
    "Iraq": "IRQ",
    "Jordan": "JOR",
    "Cape Verde": "CPV",
    "Curacao": "CUR",
    "New Zealand": "NZL",
    "Panama": "PAN",
    "Haiti": "HAI",
    "Scotland": "SCO",
    "DR Congo": "COD",
    "Uzbekistan": "UZB",
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_results(filepath):
    """Parse results CSV into dict: team_abbrev -> result_code.

    Result codes:
      -1 = eliminated
      +1 = reached semifinals
      +2 = reached final
      +4 = won World Cup
    """
    results = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                team = parts[0].strip()
                result = parts[1].strip()
                results[team] = result
    return results


def get_eliminated_teams(results):
    """Return set of team abbreviations that are eliminated."""
    return {team for team, result in results.items() if result == "-1"}


def get_semifinalists(results):
    """Return set of teams that reached semifinals."""
    return {team for team, result in results.items() if result in ("+1", "+2", "+4")}


def get_finalists(results):
    """Return set of teams that reached the final."""
    return {team for team, result in results.items() if result in ("+2", "+4")}


def get_winner(results):
    """Return the winning team, or None."""
    for team, result in results.items():
        if result == "+4":
            return team
    return None


def team_to_abbrev(team_name):
    """Convert a full team name to its abbreviation."""
    return TEAM_NAME_TO_ABBREV.get(team_name, team_name)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_participant(row, results):
    """Score a participant's predictions.

    Points are awarded only when a team actually reaches the milestone:
      - Correct semifinalist: +1 (when team reaches semis)
      - Correct finalist: +2 (when team reaches final)
      - Correct winner: +4 (when team wins)

    Returns total points.
    """
    semifinalists = get_semifinalists(results)
    finalists = get_finalists(results)
    winner = get_winner(results)

    points = 0

    # Check semifinalist picks (Semi_1 through Semi_4)
    for col in ["Semi_1", "Semi_2", "Semi_3", "Semi_4"]:
        team = team_to_abbrev(row[col])
        if team in semifinalists:
            points += 1

    # Check finalist picks
    for col in ["Finalist_1", "Finalist_2"]:
        team = team_to_abbrev(row[col])
        if team in finalists:
            points += 2

    # Check winner pick
    winner_pick = team_to_abbrev(row["Winner"])
    if winner and winner_pick == winner:
        points += 4

    return points


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def style_team(team_name, eliminated_teams):
    """Apply red strikethrough if team is eliminated, otherwise plain text."""
    abbrev = team_to_abbrev(team_name)
    if abbrev in eliminated_teams:
        return f'<span style="color:red"><s>{team_name}</s></span>'
    return team_name


def style_winner(team_name, eliminated_teams):
    """Style the winner column (bold + strikethrough if eliminated)."""
    abbrev = team_to_abbrev(team_name)
    if abbrev in eliminated_teams:
        return f'<span style="color:red"><s>**{team_name}**</s></span>'
    return f"**{team_name}**"


# ---------------------------------------------------------------------------
# Timestamp
# ---------------------------------------------------------------------------


def get_timestamp():
    """Get current timestamp in EDT/EST format."""
    edt = ZoneInfo("America/New_York")
    now = datetime.now(edt)
    suffix = "EDT" if now.dst() else "EST"
    return now.strftime("%B %-d, %Y — %I:%M %p") + f" {suffix}"


# ---------------------------------------------------------------------------
# Generate output
# ---------------------------------------------------------------------------


def count_eliminated_picks(row, eliminated_teams):
    """Count how many of a participant's 7 picks are eliminated."""
    count = 0
    for col in ["Semi_1", "Semi_2", "Semi_3", "Semi_4", "Finalist_1", "Finalist_2", "Winner"]:
        abbrev = team_to_abbrev(row[col])
        if abbrev in eliminated_teams:
            count += 1
    return count


def generate_421_page(predictions, results, timestamp):
    """Generate the full 421-index.md content."""
    eliminated = get_eliminated_teams(results)
    lines = []

    # Front matter
    lines.append("---")
    lines.append("layout: page")
    lines.append('title: "4-2-1 Long Range Predictions"')
    lines.append('description: "FIFA World Cup 2026 Long Range 4-2-1 Predictions"')
    lines.append("background: '/img/soccer/421-banner.png'")
    lines.append('permalink: "/fifa-2026/lr-421"')
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# FIFA World Cup 2026 — 4-2-1 Long Range")
    lines.append("")
    lines.append(f"*Last updated: {timestamp}*")
    lines.append("")
    lines.append("Predict the **4 Semifinalists**, **2 Finalists**, and the **World Cup Winner** before the tournament begins.")
    lines.append("")
    lines.append("**Scoring:** Correct Semifinalist = 1 pt, Correct Finalist = 2 pts, Correct Winner = 4 pts. **Max: 12 points.**")
    lines.append("")

    # Eliminated teams summary
    if eliminated:
        elim_list = ", ".join(sorted(eliminated))
        lines.append(f"**Eliminated teams:** {elim_list}")
        lines.append("")
        lines.append('Teams shown in <span style="color:red"><s>red strikethrough</s></span> have been eliminated from the tournament.')
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Combined predictions + leaderboard table ---
    # Score and sort participants
    scored = []
    for row in predictions:
        pts = score_participant(row, results)
        elim_count = count_eliminated_picks(row, eliminated)
        scored.append((pts, elim_count, row))

    # Sort by points desc, then more alive picks, then name
    scored.sort(key=lambda x: (-x[0], -(7 - x[1]), x[2]["Name"].lower()))

    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append("| Name | Location | Semi 1 | Semi 2 | Semi 3 | Semi 4 | Finalist 1 | Finalist 2 | Winner | Pts | Alive | Eliminated |")
    lines.append("|------|----------|--------|--------|--------|--------|------------|------------|--------|:---:|:---:|:---:|")

    for pts, elim_count, row in scored:
        name = row["Name"]
        loc = row["Location"]
        semi1 = style_team(row["Semi_1"], eliminated)
        semi2 = style_team(row["Semi_2"], eliminated)
        semi3 = style_team(row["Semi_3"], eliminated)
        semi4 = style_team(row["Semi_4"], eliminated)
        fin1 = style_team(row["Finalist_1"], eliminated)
        fin2 = style_team(row["Finalist_2"], eliminated)
        winner = style_winner(row["Winner"], eliminated)
        alive_count = 7 - elim_count
        alive_str = f"{alive_count}/7"
        elim_str = f"{elim_count}/7" if elim_count > 0 else "-"

        lines.append(f"| {name} | {loc} | {semi1} | {semi2} | {semi3} | {semi4} | {fin1} | {fin2} | {winner} | {pts} | {alive_str} | {elim_str} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("[Back to Contest Home](/prediction-contests/fifa-2026/) | [Leaderboard](/prediction-contests/fifa-2026/leaderboard) | [Rules](/prediction-contests/fifa-2026/rules)")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Reading LR-421 predictions...")
    predictions = []
    with open(PREDICTIONS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            predictions.append(row)
    print(f"  {len(predictions)} participants loaded")

    print("Reading results...")
    results = parse_results(RESULTS_CSV)
    eliminated = get_eliminated_teams(results)
    print(f"  {len(results)} results loaded")
    print(f"  Eliminated: {', '.join(sorted(eliminated)) if eliminated else 'none'}")

    semifinalists = get_semifinalists(results)
    if semifinalists:
        print(f"  Semifinalists: {', '.join(sorted(semifinalists))}")

    print("\nScoring participants...")
    timestamp = get_timestamp()

    scored = []
    for row in predictions:
        pts = score_participant(row, results)
        elim = count_eliminated_picks(row, eliminated)
        scored.append((pts, elim, row["Name"]))

    scored.sort(key=lambda x: (-x[0], x[1], x[2].lower()))
    print(f"\n{'Name':<25} {'Pts':>4}  {'Elim':>5}")
    print("-" * 40)
    for pts, elim, name in scored:
        print(f"  {name:<25} {pts:>3}  {elim:>3}/7")

    print(f"\nWriting {OUTPUT_MD}...")
    content = generate_421_page(predictions, results, timestamp)
    with open(OUTPUT_MD, "w") as f:
        f.write(content)
    print(f"  Done ({len(predictions)} rows)")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
