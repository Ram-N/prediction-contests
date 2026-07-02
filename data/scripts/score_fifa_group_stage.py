"""
Score FIFA 2026 Group Stage predictions.

Reads predictions + results → scores → generates color-coded markdown → writes output files.

Input:
  - data/FIFA-2026/GroupStage-Predictions-Clean.csv (predictions)
  - active-contest/results/group-stage-results.csv (results)

Output:
  - active-contest/group-stage.md (full page with color-coded table)
  - active-contest/leaderboard.md (updates GS column and GS section)

Usage:
  cd data/scripts
  uv run python score_fifa_group_stage.py
"""

import csv
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

# Add scripts dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from process_group_stage_predictions import (
    GROUPS,
    TEAM_ABBREVS,
    abbreviate_single_team,
    calculate_herd_score,
    compute_wotc,
)

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "GroupStage-Predictions-Clean.csv"
)
RESULTS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "results", "group-stage-results.csv"
)
GROUP_STAGE_MD = os.path.join(PROJECT_ROOT, "active-contest", "group-stage.md")
LEADERBOARD_MD = os.path.join(PROJECT_ROOT, "active-contest", "leaderboard.md")
CANONICAL_LOCATIONS_CSV = os.path.join(
    PROJECT_ROOT, "data", "FIFA-2026", "canonical-locations.csv"
)

# Map results file abbreviations to prediction abbreviations where they differ
RESULTS_ABBREV_NORMALIZE = {
    "CUW": "CUR",
    "SPA": "ESP",
    "NZE": "NZL",
}

# Team abbreviation to emoji flag
TEAM_FLAGS = {
    "MEX": "\U0001f1f2\U0001f1fd",
    "RSA": "\U0001f1ff\U0001f1e6",
    "KOR": "\U0001f1f0\U0001f1f7",
    "CZE": "\U0001f1e8\U0001f1ff",
    "SUI": "\U0001f1e8\U0001f1ed",
    "CAN": "\U0001f1e8\U0001f1e6",
    "BIH": "\U0001f1e7\U0001f1e6",
    "QAT": "\U0001f1f6\U0001f1e6",
    "BRA": "\U0001f1e7\U0001f1f7",
    "MAR": "\U0001f1f2\U0001f1e6",
    "SCO": "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f",
    "HAI": "\U0001f1ed\U0001f1f9",
    "USA": "\U0001f1fa\U0001f1f8",
    "AUS": "\U0001f1e6\U0001f1fa",
    "PAR": "\U0001f1f5\U0001f1fe",
    "TUR": "\U0001f1f9\U0001f1f7",
    "GER": "\U0001f1e9\U0001f1ea",
    "CIV": "\U0001f1e8\U0001f1ee",
    "ECU": "\U0001f1ea\U0001f1e8",
    "CUR": "\U0001f1e8\U0001f1fc",
    "NED": "\U0001f1f3\U0001f1f1",
    "JPN": "\U0001f1ef\U0001f1f5",
    "TUN": "\U0001f1f9\U0001f1f3",
    "SWE": "\U0001f1f8\U0001f1ea",
    "BEL": "\U0001f1e7\U0001f1ea",
    "IRN": "\U0001f1ee\U0001f1f7",
    "EGY": "\U0001f1ea\U0001f1ec",
    "NZL": "\U0001f1f3\U0001f1ff",
    "ESP": "\U0001f1ea\U0001f1f8",
    "URU": "\U0001f1fa\U0001f1fe",
    "KSA": "\U0001f1f8\U0001f1e6",
    "CPV": "\U0001f1e8\U0001f1fb",
    "FRA": "\U0001f1eb\U0001f1f7",
    "NOR": "\U0001f1f3\U0001f1f4",
    "SEN": "\U0001f1f8\U0001f1f3",
    "IRQ": "\U0001f1ee\U0001f1f6",
    "ARG": "\U0001f1e6\U0001f1f7",
    "AUT": "\U0001f1e6\U0001f1f9",
    "ALG": "\U0001f1e9\U0001f1ff",
    "JOR": "\U0001f1ef\U0001f1f4",
    "POR": "\U0001f1f5\U0001f1f9",
    "COL": "\U0001f1e8\U0001f1f4",
    "UZB": "\U0001f1fa\U0001f1ff",
    "COD": "\U0001f1e8\U0001f1e9",
    "ENG": "\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f",
    "CRO": "\U0001f1ed\U0001f1f7",
    "GHA": "\U0001f1ec\U0001f1ed",
    "PAN": "\U0001f1f5\U0001f1e6",
}


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
    """Parse results CSV into dict: team_abbrev -> result_code (+1, -1, +3)."""
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
                team = RESULTS_ABBREV_NORMALIZE.get(team, team)
                results[team] = result
    return results


def get_third_by_group(row):
    """Build a map of group letter -> abbreviated 3rd-place team for a row."""
    third_by_group = {}
    for i in range(1, 9):
        val = row.get(f"3rd_{i}", "")
        if val and str(val) != "nan":
            val = str(val).strip()
            if ":" in val:
                group_letter = val.split(":")[0].strip()
                team_name = val.split(":", 1)[1].strip()
                third_by_group[group_letter] = abbreviate_single_team(team_name)
    return third_by_group


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def style_team(team_abbrev, result, is_third_pick):
    """Apply color coding to a team abbreviation based on its result."""
    if is_third_pick:
        if result == "+3":
            return f'<span style="color:#2563EB"><b>{team_abbrev}</b></span>'
        elif result == "-1":
            return f'<span style="color:red"><s>{team_abbrev}</s></span>'
        elif result == "+1":
            # Picked as 3rd but finished top-2: right team, wrong slot
            return f'<span style="color:#D97706">{team_abbrev}</span>'
        else:
            return f'<span style="color:#2563EB">{team_abbrev}</span>'
    else:
        # Top-2 pick
        if result == "+1":
            return f'<span style="color:green"><b>{team_abbrev}</b></span>'
        elif result == "-1":
            return f'<span style="color:red"><s>{team_abbrev}</s></span>'
        elif result == "+3":
            # Picked as top-2 but finished 3rd: right team, wrong slot
            return f'<span style="color:#D97706">{team_abbrev}</span>'
        else:
            return team_abbrev


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_and_style_row(row, results):
    """Score a participant row and generate styled group cells.

    Returns (points, group_cells_list).
    """
    points = 0
    group_cells = []
    third_by_group = get_third_by_group(row)

    for g in GROUPS:
        # Top-2 picks
        r32_val = str(row[f"R32_{g}"])
        r32_teams = [
            t.strip()
            for t in r32_val.split(",")
            if t.strip() and t.strip() != "nan"
        ]
        r32_abbrs = [abbreviate_single_team(t) for t in r32_teams]

        styled_top2 = []
        for abbr in r32_abbrs:
            result = results.get(abbr)
            styled_top2.append(style_team(abbr, result, is_third_pick=False))
            if result == "+1":
                points += 1

        # 3rd-place pick
        third_team = third_by_group.get(g)
        if third_team:
            result = results.get(third_team)
            styled_third = style_team(third_team, result, is_third_pick=True)
            if result == "+3":
                points += 1
        else:
            styled_third = '<span style="color:#2563EB">---</span>'

        cell = "<br>".join(styled_top2 + [styled_third])
        group_cells.append(cell)

    return points, group_cells


def score_wotc_row(wotc, results):
    """Score and style the synthetic WOTC row."""
    points = 0
    group_cells = []

    for g in GROUPS:
        top2 = sorted(wotc["top2"][g])
        styled_top2 = []
        for team in top2:
            result = results.get(team)
            styled_top2.append(style_team(team, result, is_third_pick=False))
            if result == "+1":
                points += 1

        third = wotc["third"][g]
        if third:
            result = results.get(third)
            styled_third = style_team(third, result, is_third_pick=True)
            if result == "+3":
                points += 1
        else:
            styled_third = '<span style="color:#2563EB">---</span>'

        cell = "<br>".join(styled_top2 + [styled_third])
        group_cells.append(cell)

    return points, group_cells


# ---------------------------------------------------------------------------
# Summary & timestamp helpers
# ---------------------------------------------------------------------------


def get_timestamp():
    """Get current timestamp in EDT/EST format."""
    edt = ZoneInfo("America/New_York")
    now = datetime.now(edt)
    suffix = "EDT" if now.dst() else "EST"
    return now.strftime("%B %-d, %Y — %I:%M %p") + f" {suffix}"


def build_summary_line(results):
    """Build the summary line showing qualified, 3rd place, and eliminated teams."""
    qualified = []
    third_place = []
    eliminated = []

    for team, result in results.items():
        if result == "+1":
            qualified.append(team)
        elif result == "+3":
            third_place.append(team)
        elif result == "-1":
            eliminated.append(team)

    total = len(results)

    parts = []
    if qualified:
        team_strs = [f"{t} {TEAM_FLAGS.get(t, '')}" for t in qualified]
        parts.append(", ".join(team_strs) + " qualified")
    if third_place:
        team_strs = [f"{t} {TEAM_FLAGS.get(t, '')}" for t in third_place]
        parts.append(", ".join(team_strs) + " 3rd place")
    if eliminated:
        team_strs = [f"{t} {TEAM_FLAGS.get(t, '')}" for t in eliminated]
        parts.append(", ".join(team_strs) + " eliminated")

    return (
        f"**{total} of 48 group stage results decided** — "
        + "; ".join(parts)
        + "."
    )


def build_scoring_line(results):
    """Build the scoring explanation line with current max possible."""
    num_qualified = sum(1 for r in results.values() if r == "+1")
    num_third = sum(1 for r in results.values() if r == "+3")
    max_possible = num_qualified + num_third
    return (
        f"**Scoring:** +1 point for each correct top-2 pick, "
        f"+1 for each correct 3rd-place pick. "
        f"Max possible so far: {max_possible}."
    )


# ---------------------------------------------------------------------------
# Generate group-stage.md
# ---------------------------------------------------------------------------


def score_all_participants(df, results, wotc):
    """Score all participants and WOTC. Returns sorted list of tuples:
    (points, name, location, group_cells, herd_score_str)
    """
    scored_rows = []
    for _, row in df.iterrows():
        points, group_cells = score_and_style_row(row, results)
        name = row["Name"]
        loc = str(row["Location"]) if str(row["Location"]) != "nan" else ""
        herd = calculate_herd_score(row, wotc)
        scored_rows.append((points, name, loc, group_cells, f"{herd}/32"))

    # WOTC row
    wotc_points, wotc_cells = score_wotc_row(wotc, results)
    scored_rows.append((wotc_points, "WOTC", "Crowd", wotc_cells, "32/32"))

    # Sort by points desc, then name asc (case-insensitive)
    scored_rows.sort(key=lambda x: (-x[0], x[1].lower()))
    return scored_rows


def generate_group_stage_md(scored_rows, results, timestamp):
    """Generate the full group-stage.md content."""
    lines = []

    # Front matter
    lines.append("---")
    lines.append("layout: page")
    lines.append('title: "Group Stage - FIFA 2026"')
    lines.append(
        'description: "FIFA World Cup 2026 Group Stage results and predictions leaderboard"'
    )
    lines.append("background: '/img/soccer/bg_fifa.webp'")
    lines.append('permalink: "/fifa-2026/group-stage"')
    lines.append("")
    lines.append("---")
    lines.append("")

    # Live standings box
    lines.append("# FIFA World Cup 2026 — Group Stage")
    lines.append("")
    lines.append("## Live Standings")
    lines.append("")
    lines.append(
        '<div style="background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px; '
        'padding:20px; margin:20px 0; text-align:center;">'
    )
    lines.append(
        '  <p style="font-size:1.1em; margin-bottom:15px;">'
        "<strong>Official Group Stage Tables (Groups A\u2013L)</strong></p>"
    )
    lines.append("  <p>")
    lines.append(
        '    <a href="https://www.fifa.com/en/tournaments/mens/worldcup/'
        'canadamexicousa2026/standings" target="_blank" '
        'style="display:inline-block; background:#326295; color:white; '
        "padding:10px 20px; border-radius:5px; text-decoration:none; "
        'margin:5px;">FIFA.com Standings \u2197</a>'
    )
    lines.append(
        '    <a href="https://en.wikipedia.org/wiki/2026_FIFA_World_Cup#Group_stage" '
        'target="_blank" style="display:inline-block; background:#36c; '
        "color:white; padding:10px 20px; border-radius:5px; "
        'text-decoration:none; margin:5px;">Wikipedia Group Tables \u2197</a>'
    )
    lines.append("  </p>")
    lines.append(
        '  <p style="font-size:0.85em; color:#666; margin-top:10px;">'
        "Tables update live as matches are played</p>"
    )
    lines.append("</div>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Prediction leaderboard
    lines.append("## Prediction Leaderboard")
    lines.append("")
    lines.append(f"*Last updated: {timestamp}*")
    lines.append("")
    lines.append(build_summary_line(results))
    lines.append("")
    lines.append("**Color coding:**")
    lines.append(
        '- <span style="color:green"><b>Green/Bold</b></span> = '
        "Correct top-2 pick (team qualified \u2713)"
    )
    lines.append(
        '- <span style="color:#2563EB"><b>Blue/Bold</b></span> = '
        "Correct 3rd place pick \u2713"
    )
    lines.append(
        '- <span style="color:#D97706">Orange</span> = '
        "Team advanced, but in wrong slot (e.g., picked top-2 but finished 3rd)"
    )
    lines.append(
        '- <span style="color:red"><s>Red/Strikethrough</s></span> = '
        "Wrong pick (team eliminated \u2717)"
    )
    lines.append("- Plain text = Result pending")
    lines.append("")
    lines.append(build_scoring_line(results))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table
    lines.append(build_gs_table(scored_rows))

    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def build_gs_table(scored_rows):
    """Build the group stage markdown table from scored rows."""
    table_lines = []
    table_lines.append(
        "{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }"
    )
    table_lines.append(
        "| Name | Location | Pts | A | B | C | D | E | F | G | H | I | J | K | L | WOTC% |"
    )
    table_lines.append(
        "|------|----------|---|---|---|---|---|---|---|---|---|---|---|---|---|-------|"
    )

    for points, name, loc, group_cells, herd_str in scored_rows:
        cells = [name, loc, str(points)] + group_cells + [herd_str]
        table_lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(table_lines)


# ---------------------------------------------------------------------------
# Update leaderboard.md
# ---------------------------------------------------------------------------


def update_overall_leaderboard(leaderboard_path, gs_scores, scored_rows, results, timestamp, location_map=None):
    """Update leaderboard.md: overall table GS/Total + GS detail section."""
    if location_map is None:
        location_map = {}
    with open(leaderboard_path, "r") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []
    updated_top_timestamp = False
    in_overall_table = False
    overall_table_rows = []
    overall_header_lines = []  # The header + separator lines of the table
    skip_gs_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Update the top-level timestamp (first one in the file)
        if line.startswith("*Last updated:") and not updated_top_timestamp:
            new_lines.append(f"*Last updated: {timestamp}*")
            updated_top_timestamp = True
            i += 1
            continue

        # Detect overall leaderboard table header (with or without Location column)
        if "| Name |" in line and "| GS |" in line and "| R32 |" in line:
            in_overall_table = True
            has_location = "| Location |" in line
            # Write new header with Location column
            new_lines.append("| Name | Location | GS | R32 | R16 | ST-421 | Total |")
            i += 1
            # Next line is separator
            if i < len(lines) and lines[i].startswith("|") and "---" in lines[i]:
                new_lines.append("|------|----------|:---:|:---:|:---:|:---:|:---:|")
                i += 1
            # Collect table rows
            while i < len(lines) and lines[i].startswith("|"):
                overall_table_rows.append(lines[i])
                i += 1
            # Process and re-sort the overall table
            new_lines.extend(
                rebuild_overall_table(overall_table_rows, gs_scores, location_map=location_map, has_location=has_location)
            )
            in_overall_table = False
            continue

        # Replace GS section entirely
        if "## Group Stage Leaderboard" in line:
            skip_gs_section = True
            # Write the new GS section
            new_lines.append("")
            new_lines.append("## Group Stage Leaderboard")
            new_lines.append("")
            new_lines.append(build_summary_line(results))
            new_lines.append("")
            new_lines.append("**Color coding:**")
            new_lines.append(
                '- <span style="color:green"><b>Green/Bold</b></span> = '
                "Correct top-2 pick (team qualified \u2713)"
            )
            new_lines.append(
                '- <span style="color:#2563EB"><b>Blue/Bold</b></span> = '
                "Correct 3rd place pick \u2713"
            )
            new_lines.append(
                '- <span style="color:#D97706">Orange</span> = '
                "Team advanced, but in wrong slot (e.g., picked top-2 but finished 3rd)"
            )
            new_lines.append(
                '- <span style="color:red"><s>Red/Strikethrough</s></span> = '
                "Wrong pick (team eliminated \u2717)"
            )
            new_lines.append("- Plain text = Result pending")
            new_lines.append("")
            new_lines.append(build_scoring_line(results))
            new_lines.append("")
            new_lines.append("---")
            new_lines.append("")
            new_lines.append(build_gs_table(scored_rows))
            new_lines.append("")
            new_lines.append("---")
            new_lines.append("")
            # Skip remaining lines (GS section goes to end of file)
            break

        if not skip_gs_section:
            new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def rebuild_overall_table(table_rows, gs_scores, rename_map=None, location_map=None, has_location=False):
    """Parse overall table rows, update GS/Total, re-sort by Total desc.

    - Renames participants whose canonical name changed (via rename_map)
    - Adds GS participants not already in the table
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
            gs_cell = cells[3]
            r32 = cells[4]
            r16 = cells[5]
            st421 = cells[6]
        else:
            # cells: ['', 'Name', 'GS', 'R32', 'R16', 'ST-421', 'Total', '']
            if len(cells) < 7:
                continue
            name = cells[1]
            location = ""
            gs_cell = cells[2]
            r32 = cells[3]
            r16 = cells[4]
            st421 = cells[5]

        # Apply name rename if needed
        name = rename_map.get(name, name)

        # Skip if we already have this name (duplicate from rename)
        if name in seen_names:
            continue

        # Look up location from canonical map (prefer it over existing)
        location = location_map.get(name, location)

        # Update GS from computed scores
        gs = gs_scores.get(name, gs_cell)
        gs_str = str(gs)

        # Compute total
        total = 0
        for val in [gs_str, r32, r16, st421]:
            if val != "-" and val.strip():
                try:
                    total += int(val)
                except ValueError:
                    pass

        parsed.append((name, location, gs_str, r32, r16, st421, str(total), total))
        seen_names.add(name)

    # Add GS participants not already in the table
    for name, gs_pts in gs_scores.items():
        if name not in seen_names:
            gs_str = str(gs_pts)
            total = gs_pts
            location = location_map.get(name, "")
            parsed.append((name, location, gs_str, "-", "-", "-", str(total), total))
            seen_names.add(name)

    # Sort by total desc, then name asc
    parsed.sort(key=lambda x: (-x[7], x[0].lower()))

    result_lines = []
    for name, location, gs, r32, r16, st421, total_str, _ in parsed:
        result_lines.append(
            f"| {name} | {location} | {gs} | {r32} | {r16} | {st421} | {total_str} |"
        )
    return result_lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading canonical locations...")
    location_map = load_canonical_locations()
    print(f"  {len(location_map)} locations loaded")

    print("Reading predictions...")
    df = pd.read_csv(PREDICTIONS_CSV)
    print(f"  {len(df)} participants loaded")

    print("Reading results...")
    results = parse_results(RESULTS_CSV)
    print(f"  {len(results)} team results loaded")
    for team, result in results.items():
        label = {"1": "qualified", "+1": "qualified", "+3": "3rd place", "-1": "eliminated"}.get(
            result, result
        )
        print(f"    {team}: {label}")

    print("\nComputing WOTC...")
    wotc = compute_wotc(df)
    for g in GROUPS:
        top2 = ", ".join(sorted(wotc["top2"][g]))
        third = wotc["third"][g] or "---"
        print(f"  Group {g}: Top-2: {{{top2}}}  3rd: {third}")

    print("\nScoring all participants...")
    timestamp = get_timestamp()
    scored_rows = score_all_participants(df, results, wotc)

    # Build name -> GS score map for leaderboard update
    gs_scores = {name: pts for pts, name, _, _, _ in scored_rows}

    # Print scores
    print(f"\n{'Name':<25} {'Pts':>4}  {'WOTC':>6}")
    print("-" * 40)
    for pts, name, _, _, herd in scored_rows:
        print(f"  {name:<25} {pts:>3}  {herd:>6}")

    # Generate group-stage.md
    print(f"\nWriting {GROUP_STAGE_MD}...")
    gs_content = generate_group_stage_md(scored_rows, results, timestamp)
    with open(GROUP_STAGE_MD, "w") as f:
        f.write(gs_content)
    print(f"  Done ({len(scored_rows)} rows)")

    # Update leaderboard.md
    print(f"\nUpdating {LEADERBOARD_MD}...")
    lb_content = update_overall_leaderboard(
        LEADERBOARD_MD, gs_scores, scored_rows, results, timestamp, location_map
    )
    with open(LEADERBOARD_MD, "w") as f:
        f.write(lb_content)
    print("  Done")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
