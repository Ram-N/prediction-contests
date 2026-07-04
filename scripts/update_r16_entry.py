"""
Update r16-entry.js MATCHES array from r16-matches.csv.

Reads active-contest/data/matches/r16-matches.csv and rewrites the MATCHES array
in assets/js/r16-entry.js with full country names.

Usage:
  cd scripts
  uv run python update_r16_entry.py
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "active-contest", "data", "matches", "r16-matches.csv")
JS_PATH = os.path.join(PROJECT_ROOT, "assets", "js", "r16-entry.js")

# Abbreviation → full country name
ABBREV_TO_FULL = {
    "MEX": "Mexico", "RSA": "South Africa", "KOR": "Korea Republic",
    "CZE": "Czechia", "SUI": "Switzerland", "SWI": "Switzerland",
    "CAN": "Canada", "BIH": "Bosnia & Herzegovina",
    "QAT": "Qatar", "BRA": "Brazil", "MAR": "Morocco",
    "SCO": "Scotland", "HAI": "Haiti", "USA": "United States",
    "AUS": "Australia", "PAR": "Paraguay", "TUR": "Turkey",
    "GER": "Germany", "CIV": "Ivory Coast", "ECU": "Ecuador",
    "CUW": "Curacao", "CUR": "Curacao",
    "NED": "Netherlands", "JPN": "Japan", "TUN": "Tunisia",
    "SWE": "Sweden", "BEL": "Belgium", "IRN": "Iran",
    "EGY": "Egypt", "NZL": "New Zealand", "ESP": "Spain",
    "SPA": "Spain", "URU": "Uruguay", "KSA": "Saudi Arabia",
    "CPV": "Cape Verde", "FRA": "France", "NOR": "Norway",
    "SEN": "Senegal", "IRQ": "Iraq", "ARG": "Argentina",
    "AUT": "Austria", "ALG": "Algeria", "JOR": "Jordan",
    "POR": "Portugal", "COL": "Colombia", "UZB": "Uzbekistan",
    "COD": "DR Congo", "ENG": "England", "CRO": "Croatia",
    "GHA": "Ghana", "PAN": "Panama",
}


def resolve_team(abbrev):
    """Convert a CSV team abbreviation to a full name, or '?' if unknown."""
    abbrev = abbrev.strip()
    if not abbrev:
        return "?"
    upper = abbrev.upper()
    # Known abbreviation
    if upper in ABBREV_TO_FULL:
        return ABBREV_TO_FULL[upper]
    # Placeholder patterns (xxx, YYY, X12, etc.)
    if re.match(r'^[xXyY]+\d*$', abbrev):
        return "?"
    # Unknown abbreviation — return as-is
    print(f"  WARNING: Unknown abbreviation '{abbrev}' — using as-is")
    return abbrev


def read_matches(csv_path):
    """Read r16-matches.csv and return list of match dicts."""
    matches = []
    with open(csv_path, "r") as f:
        lines = f.read().strip().splitlines()

    # Skip header line
    for i, line in enumerate(lines[1:], start=1):
        line = line.strip()
        if not line:
            continue
        # Parse "TEAM1 vs TEAM2"
        parts = re.split(r'\s+vs\s+', line)
        if len(parts) != 2:
            print(f"  WARNING: Could not parse line {i}: '{line}' — skipping")
            continue
        abbrev1 = parts[0].strip()
        abbrev2 = parts[1].strip()
        team1 = resolve_team(abbrev1)
        team2 = resolve_team(abbrev2)
        # Column header: "CAN v MAR" for known teams, "Match N" for TBD
        if team1 != "?" and team2 != "?":
            col = f"{abbrev1.upper()} v {abbrev2.upper()}"
        else:
            col = f"Match {i}"
        matches.append({
            "num": i,
            "team1": team1,
            "team2": team2,
            "col": col,
        })
    return matches


def build_matches_js(matches):
    """Build the JS MATCHES array string."""
    lines = []
    for m in matches:
        t1 = m["team1"].replace("'", "\\'")
        t2 = m["team2"].replace("'", "\\'")
        col = m["col"].replace("'", "\\'")
        if t1 == "?" or t2 == "?":
            lines.append(
                f"    {{ num: {m['num']}, team1: '{t1}', team2: '{t2}', "
                f"slot1: 'TBD', slot2: 'TBD', col: '{col}' }}"
            )
        else:
            lines.append(
                f"    {{ num: {m['num']}, team1: '{t1}', team2: '{t2}', "
                f"col: '{col}' }}"
            )
    return "  var MATCHES = [\n" + ",\n".join(lines) + "\n  ];"


def update_js(js_path, matches_block):
    """Replace the MATCHES array in r16-entry.js."""
    with open(js_path, "r") as f:
        content = f.read()

    pattern = r"  var MATCHES = \[.*?\];"
    new_content, count = re.subn(pattern, matches_block, content, count=1, flags=re.DOTALL)
    if count == 0:
        print("ERROR: Could not find MATCHES array in r16-entry.js")
        return False

    with open(js_path, "w") as f:
        f.write(new_content)
    return True


def main():
    print(f"Reading {CSV_PATH}...")
    matches = read_matches(CSV_PATH)

    known = sum(1 for m in matches if m["team1"] != "?" and m["team2"] != "?")
    tbd = len(matches) - known

    print(f"  {len(matches)} matches: {known} ready, {tbd} TBD")
    print()

    for m in matches:
        t1 = m["team1"] if m["team1"] != "?" else "(TBD)"
        t2 = m["team2"] if m["team2"] != "?" else "(TBD)"
        status = "OK" if m["team1"] != "?" and m["team2"] != "?" else "TBD"
        print(f"  Match {m['num']}: {t1:25s} vs {t2:25s}  [{status}]")

    matches_block = build_matches_js(matches)

    print(f"\nUpdating {JS_PATH}...")
    if update_js(JS_PATH, matches_block):
        print("  Done")
    else:
        print("  FAILED")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
