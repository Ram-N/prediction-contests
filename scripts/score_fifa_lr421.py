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


def result_value(r):
    """Convert result string to numeric value."""
    return {"-1": -1, "+1": 1, "+2": 2, "+4": 4}.get(r, 0)


def parse_results(filepath):
    """Parse results CSV. Returns (current, peak) dicts mapping team_abbrev -> result.

    current[team] = last result string in file (may be -1 after a team is knocked out)
    peak[team]    = highest numeric value ever recorded for the team

    This distinction matters for teams like France that reached the semis (+1)
    but were later knocked out (-1): their semi picks should still score/display
    as correct even though their current result is -1.
    """
    current = {}
    peak = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                team = parts[0].strip()
                result = parts[1].strip()
                current[team] = result
                val = result_value(result)
                if team not in peak or val > peak[team]:
                    peak[team] = val
    return current, peak


def get_eliminated_teams(current):
    """Return set of team abbreviations whose current result is -1."""
    return {team for team, result in current.items() if result == "-1"}


def get_semi_eliminated(current, peak):
    """Teams confirmed to have NEVER reached the semis (current=-1 and peak < 1).

    Teams that reached the semis but then lost (e.g. SF losers) are NOT in this
    set — their semi picks were correct and should show as green, not strikethrough.
    """
    return {t for t, v in current.items() if v == "-1" and peak.get(t, -1) < 1}


def get_finalist_eliminated(current, peak):
    """Teams confirmed to not be in the final (current=-1 and peak < 2)."""
    return {t for t, v in current.items() if v == "-1" and peak.get(t, -1) < 2}


def get_winner_eliminated(current):
    """Teams confirmed out of the tournament (current=-1)."""
    return {t for t, v in current.items() if v == "-1"}


def get_semifinalists(peak):
    """Return set of teams that have reached (or surpassed) the semifinals."""
    return {team for team, val in peak.items() if val >= 1}


def get_finalists(peak):
    """Return set of teams that reached the final."""
    return {team for team, val in peak.items() if val >= 2}


def get_winner(peak):
    """Return the winning team, or None."""
    for team, val in peak.items():
        if val >= 4:
            return team
    return None


def team_to_abbrev(team_name):
    """Convert a full team name to its abbreviation."""
    return TEAM_NAME_TO_ABBREV.get(team_name, team_name)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_participant(row, peak):
    """Score a participant's predictions.

    Points are awarded only when a team actually reaches the milestone:
      - Correct semifinalist: +1 (when team reaches semis)
      - Correct finalist: +2 (when team reaches final)
      - Correct winner: +4 (when team wins)

    Uses peak results so that SF losers (who reached +1 then were knocked out)
    still award points for semi picks.

    Returns total points.
    """
    semifinalists = get_semifinalists(peak)
    finalists = get_finalists(peak)
    winner = get_winner(peak)

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


def style_team(team_name, eliminated_teams, confirmed=None):
    """Style a pick cell.

    - Eliminated → red strikethrough
    - In confirmed set (earned points for this slot) → green bold
    - Otherwise → plain text

    Pass the right confirmed set per column type:
      Semi cols:     confirmed = semifinalists
      Finalist cols: confirmed = finalists  (NOT semifinalists — reaching SF
                                             doesn't yet mean they're in the final)
    """
    if confirmed is None:
        confirmed = set()
    abbrev = team_to_abbrev(team_name)
    if abbrev in eliminated_teams:
        return f'<span style="color:red"><s>{team_name}</s></span>'
    if abbrev in confirmed:
        return f'<span style="color:green"><b>{team_name}</b></span>'
    return team_name


def style_winner(team_name, eliminated_teams, winner=None):
    """Style the winner column (bold always, green if correct, red/strikethrough if eliminated)."""
    abbrev = team_to_abbrev(team_name)
    if abbrev in eliminated_teams:
        return f'<span style="color:red"><s>**{team_name}**</s></span>'
    if winner and abbrev == winner:
        return f'<span style="color:green"><b>{team_name}</b></span>'
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


def count_eliminated_picks(row, current, peak):
    """Count how many of a participant's 7 picks are eliminated for their slot.

    Uses slot-specific elimination so that SF losers don't count as eliminated
    in semi slots (they reached the semis — those picks were correct).
    """
    semi_elim = get_semi_eliminated(current, peak)
    finalist_elim = get_finalist_eliminated(current, peak)
    winner_elim = get_winner_eliminated(current)

    count = 0
    for col in ["Semi_1", "Semi_2", "Semi_3", "Semi_4"]:
        if team_to_abbrev(row[col]) in semi_elim:
            count += 1
    for col in ["Finalist_1", "Finalist_2"]:
        if team_to_abbrev(row[col]) in finalist_elim:
            count += 1
    if team_to_abbrev(row["Winner"]) in winner_elim:
        count += 1
    return count


def generate_421_page(predictions, current, peak, timestamp):
    """Generate the full 421-index.md content."""
    eliminated = get_eliminated_teams(current)
    semi_elim = get_semi_eliminated(current, peak)
    finalist_elim = get_finalist_eliminated(current, peak)
    winner_elim = get_winner_eliminated(current)
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
        lines.append('Teams shown in <span style="color:red"><s>red strikethrough</s></span> have been eliminated. <span style="color:green"><b>Green bold</b></span> = confirmed semifinalist (points awarded).')
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Combined predictions + leaderboard table ---
    # Score and sort participants
    semifinalists = get_semifinalists(peak)
    finalists = get_finalists(peak)
    winner_team = get_winner(peak)

    scored = []
    for row in predictions:
        pts = score_participant(row, peak)
        elim_count = count_eliminated_picks(row, current, peak)
        scored.append((pts, elim_count, row))

    # Sort by points desc, then more alive picks, then name
    scored.sort(key=lambda x: (-x[0], -(7 - x[1]), x[2]["Name"].lower()))

    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append("| Name | Location | Semi 1 | Semi 2 | Semi 3 | Semi 4 | Finalist 1 | Finalist 2 | Winner | Pts | Alive | Eliminated |")
    lines.append("|------|----------|--------|--------|--------|--------|------------|------------|--------|:---:|:---:|:---:|")

    for pts, elim_count, row in scored:
        name = row["Name"]
        loc = row["Location"]
        semi1 = style_team(row["Semi_1"], semi_elim, semifinalists)
        semi2 = style_team(row["Semi_2"], semi_elim, semifinalists)
        semi3 = style_team(row["Semi_3"], semi_elim, semifinalists)
        semi4 = style_team(row["Semi_4"], semi_elim, semifinalists)
        fin1 = style_team(row["Finalist_1"], finalist_elim, finalists)
        fin2 = style_team(row["Finalist_2"], finalist_elim, finalists)
        winner = style_winner(row["Winner"], winner_elim, winner_team)
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
    current, peak = parse_results(RESULTS_CSV)
    eliminated = get_eliminated_teams(current)
    print(f"  {len(current)} results loaded")
    print(f"  Eliminated: {', '.join(sorted(eliminated)) if eliminated else 'none'}")

    semifinalists = get_semifinalists(peak)
    if semifinalists:
        print(f"  Semifinalists: {', '.join(sorted(semifinalists))}")

    print("\nScoring participants...")
    timestamp = get_timestamp()

    scored = []
    for row in predictions:
        pts = score_participant(row, peak)
        elim = count_eliminated_picks(row, current, peak)
        scored.append((pts, elim, row["Name"]))

    scored.sort(key=lambda x: (-x[0], x[1], x[2].lower()))
    print(f"\n{'Name':<25} {'Pts':>4}  {'Elim':>5}")
    print("-" * 40)
    for pts, elim, name in scored:
        print(f"  {name:<25} {pts:>3}  {elim:>3}/7")

    print(f"\nWriting {OUTPUT_MD}...")
    content = generate_421_page(predictions, current, peak, timestamp)
    with open(OUTPUT_MD, "w") as f:
        f.write(content)
    print(f"  Done ({len(predictions)} rows)")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
