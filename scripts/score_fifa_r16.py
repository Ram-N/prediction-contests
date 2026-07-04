"""
Score FIFA 2026 Round of 16 predictions.

Reads predictions + results → scores → generates color-coded markdown → writes output files.

Input:
  - active-contest/data/predictions/FIFA2026-r16-predictions.csv (predictions)
  - active-contest/results/r16-results.csv (results: one winner per line)

Output:
  - active-contest/predictions-r16-table.md (color-coded predictions table)
  - active-contest/leaderboard.md (updates R16 column, Total, and R16 detail section)
  - active-contest/round-of-16.md (Round of 16 page with scored table)

Usage:
  cd scripts
  uv run python score_fifa_r16.py
"""

import csv
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "pii-data", "FIFA-2026", "raw-predictions", "FIFA2026-r16-predictions - Sheet1.csv"
)
RESULTS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "results", "r16-results.csv"
)
LEADERBOARD_MD = os.path.join(PROJECT_ROOT, "active-contest", "leaderboard.md")
R16_TABLE_MD = os.path.join(PROJECT_ROOT, "active-contest", "predictions-r16-table.md")
R16_PAGE_MD = os.path.join(PROJECT_ROOT, "active-contest", "round-of-16.md")
CANONICAL_NAMES_CSV = os.path.join(
    PROJECT_ROOT, "pii-data", "FIFA-2026", "canonical-names.csv"
)
EMAIL_RECON_CSV = os.path.join(
    PROJECT_ROOT, "pii-data", "FIFA-2026", "email-reconciliation.csv"
)
CANONICAL_LOCATIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "canonical-locations.csv"
)

# R16 matches with team matchups (column headers from CSV)
MATCHES = [
    ("CAN v MAR", "CAN", "MAR"),
    ("PAR v FRA", "PAR", "FRA"),
    ("BRA v NOR", "BRA", "NOR"),
    ("MEX v ENG", "MEX", "ENG"),
    ("ESP v POR", "ESP", "POR"),
    ("USA v BEL", "USA", "BEL"),
    ("EGY v ARG", "EGY", "ARG"),
    ("SUI v COL", "SUI", "COL"),
]

# Full name -> 3-letter abbreviation
ABBREV = {
    "Canada": "CAN",
    "Morocco": "MAR",
    "Paraguay": "PAR",
    "France": "FRA",
    "Brazil": "BRA",
    "Norway": "NOR",
    "Mexico": "MEX",
    "England": "ENG",
    "Spain": "ESP",
    "Portugal": "POR",
    "United States": "USA",
    "Belgium": "BEL",
    "Egypt": "EGY",
    "Argentina": "ARG",
    "Switzerland": "SUI",
    "Colombia": "COL",
}

# AI entry names (share Ram's email but are separate entries)
AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}

# Known email variants that map to the same canonical email
EMAIL_ALIASES = {
    "goesfoinfinty@gmail.com": "goestoinfinity@gmail.com",
    "shnoong@gmail.com": "shnoong@yahoo.com",
    "subtees@hotmail.com": "subtees@gmail.com",
    "jrin2000@gmail.com": "jrin2000@gmsil.com",
    "keshavvenkatesh@gmail.com": "keshavvenkatesh211@gmail.com",
    "knarasim@terpmail.umd.edu": "keshavmp@gmail.com",
    "rupenderdahiya7@gmail.com": "rupenderdahiya5@gmail.com",
}

POINTS_PER_CORRECT = 4  # R16 correct pick is worth 4 points


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


def resolve_email(email):
    """Resolve email aliases to canonical email."""
    e = email.strip().lower()
    return EMAIL_ALIASES.get(e, e)


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
    """Parse r16-results.csv. Format: header line, then one winner abbreviation per line.

    Matches are NOT played in order, so the script looks up which match each
    winning team belongs to.

    Returns dict: match_label -> winner_abbrev
    """
    # Build reverse lookup: team_abbrev -> match_label
    team_to_match = {}
    for label, t1, t2 in MATCHES:
        team_to_match[t1] = label
        team_to_match[t2] = label

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
        match_label = team_to_match[winner]
        results[match_label] = winner

    return results


def load_predictions(filepath, canonical_names, canonical_locations):
    """Load and deduplicate R16 predictions. Returns list of dicts with
    canonical names and locations applied."""
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Deduplicate by email (keep latest), AI entries keyed by name
    seen = {}
    for row in rows:
        name = row["Name"].strip()
        email = row["Email"].strip()
        ts = row["Timestamp"].strip()

        if name in AI_NAMES:
            key = name
        else:
            key = resolve_email(email)

        if key not in seen or ts > seen[key]["Timestamp"]:
            seen[key] = row

    # Apply canonical names and locations
    entries = []
    for key, row in seen.items():
        entry = dict(row)
        if key in AI_NAMES:
            entry["Name"] = key
            entry["Location"] = "🤖 AI"
        else:
            resolved = resolve_email(entry["Email"].strip())
            if resolved in canonical_names:
                entry["Name"] = canonical_names[resolved]
            loc = canonical_locations.get(entry["Name"].strip())
            if loc:
                entry["Location"] = loc
        entries.append(entry)

    # Compute WOTC (majority pick for each match, humans only)
    from collections import Counter
    human_entries = [e for e in entries if e["Name"].strip() not in AI_NAMES]
    wotc_row = {"Name": "WOTC", "Location": "👥 Crowd", "Timestamp": ""}
    for label, t1, t2 in MATCHES:
        picks = [e[label].strip() for e in human_entries]
        counter = Counter(picks)
        wotc_row[label] = counter.most_common(1)[0][0]
    entries.append(wotc_row)

    # Sort: AI first, WOTC, then humans alphabetically
    def sort_key(r):
        name = r["Name"].strip()
        if "(AI)" in name:
            return (0, name.lower())
        if name == "WOTC":
            return (1, name.lower())
        return (2, name.lower())
    entries.sort(key=sort_key)

    return entries


def get_pick_abbrev(entry, match_label):
    """Get the 3-letter abbreviation for a participant's pick in a match."""
    val = entry[match_label].strip()
    return ABBREV.get(val, val[:3].upper())


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def style_pick(pick_abbrev, match_label, results):
    """Color-code a pick based on results."""
    if match_label not in results:
        return pick_abbrev  # No result yet

    winner = results[match_label]
    if pick_abbrev == winner:
        return f'<span style="color:green"><b>{pick_abbrev}</b></span>'
    else:
        return f'<span style="color:red"><s>{pick_abbrev}</s></span>'


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_entry(entry, results):
    """Score a participant. Returns (r16_points, list of styled picks)."""
    points = 0
    styled_picks = []

    for label, t1, t2 in MATCHES:
        pick = get_pick_abbrev(entry, label)
        styled = style_pick(pick, label, results)
        styled_picks.append(styled)

        if label in results and pick == results[label]:
            points += POINTS_PER_CORRECT

    return points, styled_picks


def get_timestamp():
    """Get current timestamp in EDT/EST format."""
    edt = ZoneInfo("America/New_York")
    now = datetime.now(edt)
    suffix = "EDT" if now.dst() else "EST"
    return now.strftime("%B %-d, %Y — %I:%M %p") + f" {suffix}"


# ---------------------------------------------------------------------------
# Generate predictions table (predictions-r16-table.md)
# ---------------------------------------------------------------------------


def generate_r16_table(entries, results):
    """Generate the color-coded R16 predictions table."""
    match_cols = [label for label, _, _ in MATCHES]

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
# Generate R16 page (round-of-16.md)
# ---------------------------------------------------------------------------


def generate_r16_page(entries, results, timestamp):
    """Generate the Round of 16 page content."""
    ai_count = sum(1 for e in entries if "(AI)" in e["Name"])
    wotc_count = sum(1 for e in entries if e["Name"].strip() == "WOTC")
    human_count = len(entries) - ai_count - wotc_count

    num_decided = len(results)

    lines = []
    lines.append("---")
    lines.append("layout: page")
    lines.append('title: "Round of 16 Predictions"')
    lines.append('description: "All R16 predictions — entries are now closed"')
    lines.append("background: '/img/soccer/bg_fifa.webp'")
    lines.append('permalink: "/fifa-2026/round-of-16"')
    lines.append("---")
    lines.append("")
    lines.append("## FIFA World Cup 2026 — Round of 16 Predictions")
    lines.append("")
    lines.append(f"*Last updated: {timestamp}*")
    lines.append("")
    lines.append(f"**{len(entries)} participants** ({human_count} humans + {ai_count} AI models + WOTC) picked the winner of each of the 8 knockout matches. Each correct pick is worth **{POINTS_PER_CORRECT} points**.")
    lines.append("")

    if num_decided > 0:
        lines.append(f"**{num_decided} of 8 matches decided.** ")
        winner_strs = []
        for label, t1, t2 in MATCHES:
            if label in results:
                winner = results[label]
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
    lines.append("{% include_relative predictions-r16-table.md %}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Update leaderboard.md
# ---------------------------------------------------------------------------


def update_leaderboard(leaderboard_path, r16_scores, entries, results, timestamp, location_map=None):
    """Update leaderboard.md: overall table R16/Total + R16 detail section."""
    if location_map is None:
        location_map = {}
    with open(leaderboard_path, "r") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []
    updated_top_timestamp = False
    in_r16_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Update the top-level timestamp
        if line.startswith("*Last updated:") and not updated_top_timestamp:
            new_lines.append(f"*Last updated: {timestamp}*")
            updated_top_timestamp = True
            i += 1
            continue

        # Update R16 status row
        if "| R16 |" in line and "Round of 16" in line:
            num_decided = len(results)
            if num_decided == 8:
                status = "✅ Complete"
            elif num_decided > 0:
                status = f"✅ In progress ({num_decided}/8)"
            else:
                status = "⏳ Starts July 4"
            new_lines.append(
                f"| R16 | [Round of 16 (pick winners) ↓](#round-of-16-leaderboard) | {status} |"
            )
            i += 1
            continue

        # Detect overall leaderboard table header
        if "| Name |" in line and "| GS |" in line and "| R16 |" in line:
            new_lines.append(line)
            i += 1
            if i < len(lines) and lines[i].startswith("|") and "---" in lines[i]:
                new_lines.append(lines[i])
                i += 1
            table_rows = []
            while i < len(lines) and lines[i].startswith("|"):
                table_rows.append(lines[i])
                i += 1
            new_lines.extend(rebuild_overall_table(table_rows, r16_scores, location_map))
            continue

        # Replace or insert R16 section
        if "## Round of 16 Leaderboard" in line:
            in_r16_section = True
            new_lines.append(build_r16_leaderboard_section(entries, results, timestamp))
            i += 1
            # Skip old R16 section until next ## or end
            while i < len(lines):
                if lines[i].startswith("## ") and "Round of 16" not in lines[i]:
                    break
                i += 1
            continue

        # Insert R16 section before R32 section if not already present
        if "## Round of 32 Leaderboard" in line and not in_r16_section:
            new_lines.append(build_r16_leaderboard_section(entries, results, timestamp))
            new_lines.append("")

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def rebuild_overall_table(table_rows, r16_scores, location_map=None):
    """Parse overall table rows, update R16/Total, re-sort by Total desc."""
    if location_map is None:
        location_map = {}

    parsed = []
    seen_names = set()
    for row in table_rows:
        cells = [c.strip() for c in row.split("|")]
        # cells: ['', 'Name', 'Location', 'GS', 'R32', 'R16', 'ST-421', 'Total', '']
        if len(cells) < 8:
            continue
        name = cells[1]
        location = cells[2]
        gs = cells[3]
        r32 = cells[4]
        r16_cell = cells[5]
        st421 = cells[6]

        # Update location from canonical map
        location = location_map.get(name, location)

        # Update R16 from computed scores
        if name in r16_scores:
            r16 = str(r16_scores[name])
        else:
            r16 = r16_cell  # Keep existing

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

    # Add R16-only participants not already in the table
    for name, r16_pts in r16_scores.items():
        if name not in seen_names:
            r16 = str(r16_pts)
            total = r16_pts
            location = location_map.get(name, "")
            parsed.append((name, location, "-", "-", r16, "-", str(total), total))
            seen_names.add(name)

    # Filter to participants who entered all active rounds
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


def build_r16_leaderboard_section(entries, results, timestamp):
    """Build the R16 detail section for leaderboard.md."""
    num_decided = len(results)

    lines = []
    lines.append("## Round of 16 Leaderboard")
    lines.append("")
    lines.append(f"**{num_decided} of 8 matches decided.** Each correct pick = {POINTS_PER_CORRECT} points. Max possible so far: {num_decided * POINTS_PER_CORRECT}.")
    lines.append("")

    if num_decided > 0:
        winner_strs = []
        for label, t1, t2 in MATCHES:
            if label in results:
                winner = results[label]
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

    # Build R16 leaderboard table
    match_cols = [label for label, _, _ in MATCHES]
    scored = []
    for entry in entries:
        name = entry["Name"].strip()
        location = entry["Location"].strip()
        points, styled_picks = score_entry(entry, results)
        scored.append((points, name, location, styled_picks))

    scored.sort(key=lambda x: (-x[0], x[1].lower()))

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
    print("Loading canonical data...")
    canonical_names = load_canonical_names()
    canonical_locations = load_canonical_locations()
    email_recon = load_email_recon()
    print(f"  {len(canonical_names)} canonical names, {len(canonical_locations)} locations")

    print("Reading R16 predictions...")
    entries = load_predictions(PREDICTIONS_CSV, canonical_names, canonical_locations)
    ai_count = sum(1 for e in entries if "(AI)" in e["Name"])
    wotc_count = sum(1 for e in entries if e["Name"].strip() == "WOTC")
    human_count = len(entries) - ai_count - wotc_count
    print(f"  {len(entries)} participants ({human_count} humans + {ai_count} AI + WOTC)")

    print("Reading R16 results...")
    results = parse_results(RESULTS_CSV)
    print(f"  {len(results)} match results loaded")
    for label, t1, t2 in MATCHES:
        if label in results:
            winner = results[label]
            loser = t2 if winner == t1 else t1
            print(f"    {label}: {winner} beat {loser}")

    print("\nScoring all participants...")
    timestamp = get_timestamp()

    # Build name -> R16 score map
    r16_scores = {}
    for entry in entries:
        name = entry["Name"].strip()
        points, _ = score_entry(entry, results)
        r16_scores[name] = points

    # Print scores summary
    scored_list = sorted(r16_scores.items(), key=lambda x: (-x[1], x[0].lower()))
    print(f"\n{'Name':<30} {'R16 Pts':>7}")
    print("-" * 40)
    for name, pts in scored_list[:10]:
        print(f"  {name:<30} {pts:>5}")
    if len(scored_list) > 10:
        print(f"  ... and {len(scored_list) - 10} more")

    # Generate predictions table
    print(f"\nWriting {R16_TABLE_MD}...")
    table_content = generate_r16_table(entries, results)
    with open(R16_TABLE_MD, "w") as f:
        f.write(table_content)
    print("  Done")

    # Generate R16 page
    print(f"Writing {R16_PAGE_MD}...")
    page_content = generate_r16_page(entries, results, timestamp)
    with open(R16_PAGE_MD, "w") as f:
        f.write(page_content)
    print("  Done")

    # Update leaderboard
    print(f"Updating {LEADERBOARD_MD}...")
    lb_content = update_leaderboard(
        LEADERBOARD_MD, r16_scores, entries, results, timestamp, canonical_locations
    )
    with open(LEADERBOARD_MD, "w") as f:
        f.write(lb_content)
    print("  Done")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
