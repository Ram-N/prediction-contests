"""
Score FIFA 2026 Round of 32 predictions.

Reads predictions + results → scores → generates color-coded markdown → writes output files.

Input:
  - data/FIFA-2026/FIFA-2026-R32-predictions.csv (predictions)
  - active-contest/results/r32-results.csv (results: one winner per line)

Output:
  - active-contest/predictions-r32-table.md (color-coded predictions table)
  - active-contest/leaderboard.md (updates R32 column, Total, and R32 detail section)
  - active-contest/r32-entry.md (Round of 32 page with scored table)

Usage:
  cd data/scripts
  uv run python score_fifa_r32.py
"""

import csv
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "FIFA-2026-R32-predictions.csv"
)
RESULTS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "results", "r32-results.csv"
)
LEADERBOARD_MD = os.path.join(PROJECT_ROOT, "active-contest", "leaderboard.md")
R32_TABLE_MD = os.path.join(PROJECT_ROOT, "active-contest", "predictions-r32-table.md")
R32_PAGE_MD = os.path.join(PROJECT_ROOT, "active-contest", "r32-entry.md")
CANONICAL_NAMES_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "canonical-names.csv"
)
EMAIL_RECON_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "email-reconciliation.csv"
)
CANONICAL_LOCATIONS_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "canonical-locations.csv"
)

# R32 matches (73-88) with team matchups
MATCHES = [
    (73, "RSA", "CAN"),
    (74, "GER", "PAR"),
    (75, "NED", "MAR"),
    (76, "BRA", "JPN"),
    (77, "FRA", "SWE"),
    (78, "CIV", "NOR"),
    (79, "MEX", "ECU"),
    (80, "ENG", "DRC"),
    (81, "USA", "BIH"),
    (82, "BEL", "SEN"),
    (83, "CRO", "POR"),
    (84, "ESP", "AUT"),
    (85, "SUI", "ALG"),
    (86, "ARG", "CPV"),
    (87, "GHA", "COL"),
    (88, "AUS", "EGY"),
]

# Map match number -> (team1_abbr, team2_abbr)
MATCH_TEAMS = {m: (t1, t2) for m, t1, t2 in MATCHES}

# Full name -> 3-letter abbreviation
ABBREV = {
    "South Africa": "RSA",
    "Canada": "CAN",
    "Germany": "GER",
    "Paraguay": "PAR",
    "Netherlands": "NED",
    "Morocco": "MAR",
    "Brazil": "BRA",
    "Japan": "JPN",
    "France": "FRA",
    "Sweden": "SWE",
    "Ivory Coast": "CIV",
    "Norway": "NOR",
    "Mexico": "MEX",
    "Ecuador": "ECU",
    "England": "ENG",
    "DRC": "DRC",
    "United States": "USA",
    "Bosnia & Herzegovina": "BIH",
    "Belgium": "BEL",
    "Senegal": "SEN",
    "Croatia": "CRO",
    "Portugal": "POR",
    "Spain": "ESP",
    "Austria": "AUT",
    "Switzerland": "SUI",
    "Algeria": "ALG",
    "Argentina": "ARG",
    "Cape Verde": "CPV",
    "Ghana": "GHA",
    "Colombia": "COL",
    "Australia": "AUS",
    "Egypt": "EGY",
}


# ---------------------------------------------------------------------------
# Canonical names
# ---------------------------------------------------------------------------


def load_canonical_names():
    """Load canonical names CSV. Returns dict: canonical_email -> canonical_name."""
    mapping = {}
    if os.path.exists(CANONICAL_NAMES_CSV):
        with open(CANONICAL_NAMES_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                email = row["canonical_email"].strip().lower()
                name = row["canonical_name"].strip()
                if email:
                    mapping[email] = name
    return mapping


def load_email_recon():
    """Load email reconciliation. Returns dict: alternate_email -> canonical_email."""
    mapping = {}
    if os.path.exists(EMAIL_RECON_CSV):
        with open(EMAIL_RECON_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                alt = row["alternate_email"].strip().lower()
                canon = row["canonical_email"].strip().lower()
                mapping[alt] = canon
    return mapping


def build_name_rename_map(canonical_names, email_recon, predictions_csv):
    """Build old_name -> canonical_name mapping for participants whose names
    changed between contest rounds.

    Scans the GS contacts and R32 predictions to find all names used per email,
    then maps any non-canonical name to the canonical one.
    """
    # Collect all names ever used per canonical email
    email_to_names = {}
    gs_contacts_csv = os.path.join(
        PROJECT_ROOT, "data", "FIFA-2026", "GroupStage-Contacts.csv"
    )
    if os.path.exists(gs_contacts_csv):
        with open(gs_contacts_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                email = row["Email"].strip().lower()
                name = row["Name"].strip()
                if email:
                    resolved = email_recon.get(email, email)
                    email_to_names.setdefault(resolved, set()).add(name)

    rename_map = {}
    for email, names in email_to_names.items():
        canon = canonical_names.get(email)
        if canon:
            for name in names:
                if name != canon:
                    rename_map[name] = canon

    return rename_map


def load_canonical_locations():
    """Load canonical locations CSV. Returns dict: name -> location."""
    mapping = {}
    if os.path.exists(CANONICAL_LOCATIONS_CSV):
        with open(CANONICAL_LOCATIONS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row["Name"].strip()
                location = row["Location"].strip()
                if name:
                    mapping[name] = location
    return mapping


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_results(filepath):
    """Parse r32-results.csv. Format: one winner abbreviation per line.

    Matches are NOT played in numerical order, so the script looks up which
    match each winning team belongs to (each team appears in exactly one R32 match).

    Returns dict: match_number -> winner_abbrev
    """
    # Build reverse lookup: team_abbrev -> match_number
    team_to_match = {}
    for match_num, t1, t2 in MATCHES:
        team_to_match[t1] = match_num
        team_to_match[t2] = match_num

    results = {}
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Skip header line
    for line in lines[1:]:
        winner = line.strip()
        if not winner:
            continue
        if winner not in team_to_match:
            print(f"  WARNING: Unknown team '{winner}' in results — skipping")
            continue
        match_num = team_to_match[winner]
        results[match_num] = winner

    return results


def load_predictions(filepath):
    """Load and deduplicate R32 predictions. Returns list of dicts."""
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Deduplicate by email (keep latest — rows are in timestamp order)
    seen = {}
    for row in rows:
        email = row["Email"].strip().lower()
        if not email:
            email = f"__ai__{row['Name'].strip()}"
        seen[email] = row

    entries = list(seen.values())
    # Sort AI entries first, then WOTC, then humans alphabetically
    def sort_key(r):
        name = r["Name"].strip()
        if "(AI)" in name:
            return (0, name.lower())
        if name == "WOTC":
            return (1, name.lower())
        return (2, name.lower())
    entries.sort(key=sort_key)
    return entries


def get_pick_abbrev(entry, match_num):
    """Get the 3-letter abbreviation for a participant's pick in a match."""
    field = f"Match {match_num}"
    val = entry[field].strip()
    return ABBREV.get(val, val[:3].upper())


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def style_pick(pick_abbrev, match_num, results):
    """Color-code a pick based on results.

    Green bold = correct, Red strikethrough = wrong, plain = pending.
    """
    if match_num not in results:
        return pick_abbrev  # No result yet

    winner = results[match_num]
    if pick_abbrev == winner:
        return f'<span style="color:green"><b>{pick_abbrev}</b></span>'
    else:
        return f'<span style="color:red"><s>{pick_abbrev}</s></span>'


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_entry(entry, results):
    """Score a participant. Returns (r32_points, list of styled picks)."""
    points = 0
    styled_picks = []

    for match_num, t1, t2 in MATCHES:
        pick = get_pick_abbrev(entry, match_num)
        styled = style_pick(pick, match_num, results)
        styled_picks.append(styled)

        if match_num in results and pick == results[match_num]:
            points += 2

    return points, styled_picks


def get_timestamp():
    """Get current timestamp in EDT/EST format."""
    edt = ZoneInfo("America/New_York")
    now = datetime.now(edt)
    suffix = "EDT" if now.dst() else "EST"
    return now.strftime("%B %-d, %Y — %I:%M %p") + f" {suffix}"


# ---------------------------------------------------------------------------
# Generate predictions table (predictions-r32-table.md)
# ---------------------------------------------------------------------------


def generate_r32_table(entries, results):
    """Generate the color-coded R32 predictions table."""
    match_cols = [f"{t1} v {t2}" for _, t1, t2 in MATCHES]

    lines = []
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    header = "| Name | Location | " + " | ".join(match_cols) + " |"
    sep = "|------|----------|" + "|".join(["---"] * len(match_cols)) + "|"
    lines.append(header)
    lines.append(sep)

    for entry in entries:
        name = entry["Name"].strip()
        location = entry["Location"].strip()
        _, styled_picks = score_entry(entry, results)
        row_str = f"| {name} | {location} | " + " | ".join(styled_picks) + " |"
        lines.append(row_str)

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generate R32 page (r32-entry.md)
# ---------------------------------------------------------------------------


def generate_r32_page(entries, results, timestamp):
    """Generate the Round of 32 page content."""
    ai_count = sum(1 for e in entries if "(AI)" in e["Name"])
    human_count = len(entries) - ai_count

    num_decided = len(results)
    num_remaining = 16 - num_decided

    lines = []
    lines.append("---")
    lines.append("layout: page")
    lines.append('title: "Round of 32 Predictions"')
    lines.append('description: "All R32 predictions — entries are now closed"')
    lines.append("background: '/img/soccer/bg_fifa.webp'")
    lines.append('permalink: "/fifa-2026/round-of-32"')
    lines.append("---")
    lines.append("")
    lines.append('<div class="alert alert-warning" style="font-size: 1.15rem; padding: 1.5rem; margin-top: 1.5rem; border-radius: 8px;">')
    lines.append("  <strong>Entries are now closed.</strong><br>")
    lines.append("  The Round of 32 matches have begun — predictions are no longer being accepted.<br><br>")
    lines.append('  Check the <a href="{{ \'/fifa-2026/leaderboard\' | relative_url }}">leaderboard</a> to follow the action!')
    lines.append("</div>")
    lines.append("")
    lines.append("## All R32 Predictions")
    lines.append("")
    lines.append(f"*Last updated: {timestamp}*")
    lines.append("")
    lines.append(f"**{len(entries)} participants** ({human_count} humans + {ai_count} AI models) picked the winner of each of the 16 knockout matches. Each correct pick is worth **2 points**.")
    lines.append("")

    if num_decided > 0:
        lines.append(f"**{num_decided} of 16 matches decided.** ")
        winner_strs = []
        for match_num, t1, t2 in MATCHES:
            if match_num in results:
                winner = results[match_num]
                loser = t2 if winner == t1 else t1
                winner_strs.append(f"**{winner}** beat {loser}")
        lines.append(", ".join(winner_strs) + ".")
        lines.append("")

    lines.append("**Color coding:**")
    lines.append('- <span style="color:green"><b>Green/Bold</b></span> = Correct pick (winner guessed right)')
    lines.append('- <span style="color:red"><s>Red/Strikethrough</s></span> = Wrong pick')
    lines.append("- Plain text = Result pending")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("{% include_relative predictions-r32-table.md %}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Update leaderboard.md
# ---------------------------------------------------------------------------


def update_leaderboard(leaderboard_path, r32_scores, entries, results, timestamp, rename_map=None, location_map=None):
    """Update leaderboard.md: overall table R32/Total + R32 detail section."""
    if location_map is None:
        location_map = {}
    with open(leaderboard_path, "r") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []
    updated_top_timestamp = False
    in_r32_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Update the top-level timestamp
        if line.startswith("*Last updated:") and not updated_top_timestamp:
            new_lines.append(f"*Last updated: {timestamp}*")
            updated_top_timestamp = True
            i += 1
            continue

        # Update R32 status row in the round status table (not the overall leaderboard)
        if "| R32 |" in line and "| Name |" not in line and "pick winners" in line:
            num_decided = len(results)
            if num_decided == 16:
                status = "✅ Complete"
            else:
                status = f"✅ In progress ({num_decided}/16)"
            new_lines.append(
                f"| R32 | [Round of 32 (pick winners) ↓](#round-of-32-leaderboard) | {status} |"
            )
            i += 1
            continue

        # Detect overall leaderboard table header (with or without Location column)
        if "| Name |" in line and "| GS |" in line and "| R32 |" in line:
            has_location = "| Location |" in line
            # Write new header with Location column
            new_lines.append("| Name | Location | GS | R32 | R16 | ST-421 | Total |")
            i += 1
            if i < len(lines) and lines[i].startswith("|") and "---" in lines[i]:
                new_lines.append("|------|----------|:---:|:---:|:---:|:---:|:---:|")
                i += 1
            table_rows = []
            while i < len(lines) and lines[i].startswith("|"):
                table_rows.append(lines[i])
                i += 1
            new_lines.extend(rebuild_overall_table(table_rows, r32_scores, rename_map, location_map=location_map, has_location=has_location))
            continue

        # Replace or insert R32 section
        if "## Round of 32 Leaderboard" in line:
            in_r32_section = True
            new_lines.append(build_r32_leaderboard_section(entries, results, timestamp))
            i += 1
            # Skip old R32 section until next ## or end
            while i < len(lines):
                if lines[i].startswith("## ") and "Round of 32" not in lines[i]:
                    break
                i += 1
            continue

        # Insert R32 section before GS section if not already present
        if "## Group Stage Leaderboard" in line and not in_r32_section:
            new_lines.append(build_r32_leaderboard_section(entries, results, timestamp))
            new_lines.append("")

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def rebuild_overall_table(table_rows, r32_scores, rename_map=None, location_map=None, has_location=False):
    """Parse overall table rows, update R32/Total, re-sort by Total desc.

    - Renames participants whose canonical name changed (via rename_map)
    - Adds R32-only participants not already in the table
    - Includes Location column from location_map
    """
    if rename_map is None:
        rename_map = {}
    if location_map is None:
        location_map = {}

    parsed = []
    seen_names = set()
    for row in table_rows:
        cells = [c.strip() for c in row.split("|")]
        if has_location:
            # cells: ['', 'Name', 'Location', 'GS', 'R32', 'R16', 'ST-421', 'Total', '']
            if len(cells) < 8:
                continue
            name = cells[1]
            location = cells[2]
            gs = cells[3]
            r32_cell = cells[4]
            r16 = cells[5]
            st421 = cells[6]
        else:
            # cells: ['', 'Name', 'GS', 'R32', 'R16', 'ST-421', 'Total', '']
            if len(cells) < 7:
                continue
            name = cells[1]
            location = ""
            gs = cells[2]
            r32_cell = cells[3]
            r16 = cells[4]
            st421 = cells[5]

        # Apply name rename if needed
        name = rename_map.get(name, name)

        # Look up location from canonical map (prefer it over existing)
        location = location_map.get(name, location)

        # Update R32 from computed scores
        if name in r32_scores:
            r32 = str(r32_scores[name])
        else:
            r32 = r32_cell  # Keep existing (might be '-')

        # Compute total
        total = 0
        for val in [gs, r32, r16, st421]:
            if val != "-" and val.strip():
                try:
                    total += int(val)
                except ValueError:
                    pass

        parsed.append((name, location, gs, r32, r16, st421, str(total), total))
        seen_names.add(name)

    # Add R32-only participants not already in the table
    for name, r32_pts in r32_scores.items():
        if name not in seen_names:
            r32 = str(r32_pts)
            total = r32_pts
            location = location_map.get(name, "")
            parsed.append((name, location, "-", r32, "-", "-", str(total), total))
            seen_names.add(name)

    # Filter to participants who entered all active rounds.
    # A round is "active" if any participant has a non-"-" value for it.
    round_indices = {"GS": 2, "R32": 3, "R16": 4, "ST-421": 5}
    active_rounds = []
    for label, idx in round_indices.items():
        if any(row[idx] != "-" for row in parsed):
            active_rounds.append(idx)

    parsed = [
        row for row in parsed
        if all(row[idx] != "-" for idx in active_rounds)
    ]

    # Sort by total desc, then name asc
    parsed.sort(key=lambda x: (-x[7], x[0].lower()))

    result_lines = []
    for name, location, gs, r32, r16, st421, total_str, _ in parsed:
        result_lines.append(
            f"| {name} | {location} | {gs} | {r32} | {r16} | {st421} | {total_str} |"
        )
    return result_lines


def build_r32_leaderboard_section(entries, results, timestamp):
    """Build the R32 detail section for leaderboard.md."""
    num_decided = len(results)

    lines = []
    lines.append("## Round of 32 Leaderboard")
    lines.append("")
    lines.append(f"**{num_decided} of 16 matches decided.** Each correct pick = 2 points. Max possible so far: {num_decided * 2}.")
    lines.append("")

    if num_decided > 0:
        winner_strs = []
        for match_num, t1, t2 in MATCHES:
            if match_num in results:
                winner = results[match_num]
                loser = t2 if winner == t1 else t1
                winner_strs.append(f"**{winner}** beat {loser}")
        lines.append("Results: " + ", ".join(winner_strs) + ".")
        lines.append("")

    lines.append("**Color coding:**")
    lines.append('- <span style="color:green"><b>Green/Bold</b></span> = Correct pick')
    lines.append('- <span style="color:red"><s>Red/Strikethrough</s></span> = Wrong pick')
    lines.append("- Plain text = Result pending")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Build R32 leaderboard table
    scored = []
    for entry in entries:
        name = entry["Name"].strip()
        location = entry["Location"].strip()
        points, styled_picks = score_entry(entry, results)
        scored.append((points, name, location, styled_picks))

    scored.sort(key=lambda x: (-x[0], x[1].lower()))

    match_cols = [f"{t1} v {t2}" for _, t1, t2 in MATCHES]
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append("| Name | Location | Pts | " + " | ".join(match_cols) + " |")
    lines.append("|------|----------|:---:|" + "|".join(["---"] * len(match_cols)) + "|")

    for points, name, location, styled_picks in scored:
        row = f"| {name} | {location} | {points} | " + " | ".join(styled_picks) + " |"
        lines.append(row)

    lines.append("")
    lines.append("---")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    # Load canonical location mappings
    print("Loading canonical locations...")
    location_map = load_canonical_locations()
    print(f"  {len(location_map)} locations loaded")

    # Load canonical name mappings
    print("Loading canonical names...")
    canonical_names = load_canonical_names()
    email_recon = load_email_recon()
    rename_map = build_name_rename_map(canonical_names, email_recon, PREDICTIONS_CSV)
    if rename_map:
        print(f"  Name renames: {rename_map}")
    else:
        print("  No renames needed")

    print("Reading R32 predictions...")
    entries = load_predictions(PREDICTIONS_CSV)
    ai_count = sum(1 for e in entries if "(AI)" in e["Name"])
    human_count = len(entries) - ai_count
    print(f"  {len(entries)} participants ({human_count} humans + {ai_count} AI)")

    print("Reading R32 results...")
    results = parse_results(RESULTS_CSV)
    print(f"  {len(results)} match results loaded")
    for match_num, winner in results.items():
        t1, t2 = MATCH_TEAMS[match_num]
        loser = t2 if winner == t1 else t1
        print(f"    Match {match_num} ({t1} v {t2}): {winner} beat {loser}")

    print("\nScoring all participants...")
    timestamp = get_timestamp()

    # Build name -> R32 score map
    r32_scores = {}
    for entry in entries:
        name = entry["Name"].strip()
        points, _ = score_entry(entry, results)
        r32_scores[name] = points

    # Print scores summary
    scored_list = sorted(r32_scores.items(), key=lambda x: (-x[1], x[0].lower()))
    print(f"\n{'Name':<30} {'R32 Pts':>7}")
    print("-" * 40)
    for name, pts in scored_list[:10]:
        print(f"  {name:<30} {pts:>5}")
    print(f"  ... and {len(scored_list) - 10} more")

    # Generate predictions table
    print(f"\nWriting {R32_TABLE_MD}...")
    table_content = generate_r32_table(entries, results)
    with open(R32_TABLE_MD, "w") as f:
        f.write(table_content)
    print("  Done")

    # Generate R32 page
    print(f"Writing {R32_PAGE_MD}...")
    page_content = generate_r32_page(entries, results, timestamp)
    with open(R32_PAGE_MD, "w") as f:
        f.write(page_content)
    print("  Done")

    # Update leaderboard
    print(f"Updating {LEADERBOARD_MD}...")
    lb_content = update_leaderboard(
        LEADERBOARD_MD, r32_scores, entries, results, timestamp, rename_map, location_map
    )
    with open(LEADERBOARD_MD, "w") as f:
        f.write(lb_content)
    print("  Done")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
