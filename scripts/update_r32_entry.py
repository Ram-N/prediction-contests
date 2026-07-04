"""
Update r32-entry.js MATCHES array from r32-matches.csv.

Reads active-contest/data/matches/r32-matches.csv and rewrites the MATCHES array
in assets/js/r32-entry.js with full country names.

Usage:
  cd scripts
  uv run python update_r32_entry.py
"""

import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "active-contest", "data", "matches", "r32-matches.csv")
JS_PATH = os.path.join(PROJECT_ROOT, "assets", "js", "r32-entry.js")

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
    """Convert a CSV team value to a full name, or '?' if unknown."""
    if not abbrev:
        return "?"
    abbrev = abbrev.strip()
    if not abbrev or abbrev == "XXX":
        return "?"
    # If it's a known abbreviation, return full name
    if abbrev.upper() in ABBREV_TO_FULL:
        return ABBREV_TO_FULL[abbrev.upper()]
    # If it looks like a placeholder (contains spaces, "3rd", "RU", etc.)
    if " " in abbrev or abbrev.startswith("3rd") or abbrev.startswith("RU"):
        return "?"
    # Unknown abbreviation — return as-is (user can fix the CSV)
    print(f"  WARNING: Unknown abbreviation '{abbrev}' — using as-is")
    return abbrev


def shorten_slot(slot):
    """Shorten bracket slot description for display."""
    # "Best 3rd place Group A/B/C/D/F" → "Best 3rd A/B/C/D/F"
    slot = slot.replace("Best 3rd place Group ", "Best 3rd ")
    return slot


def read_matches(csv_path):
    """Read r32-matches.csv and return list of match dicts."""
    matches = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            num = int(row["match_num"].strip())
            slot1 = row["bracket_slot_1"].strip()
            slot2 = row["bracket_slot_2"].strip()
            team1 = resolve_team(row.get("team1", ""))
            team2 = resolve_team(row.get("team2", ""))
            matches.append({
                "num": num,
                "team1": team1,
                "team2": team2,
                "slot1": shorten_slot(slot1),
                "slot2": shorten_slot(slot2),
            })
    return matches


def build_matches_js(matches):
    """Build the JS MATCHES array string."""
    lines = []
    for m in matches:
        t1 = m["team1"].replace("'", "\\'")
        t2 = m["team2"].replace("'", "\\'")
        s1 = m["slot1"].replace("'", "\\'")
        s2 = m["slot2"].replace("'", "\\'")
        lines.append(
            f"    {{ num: {m['num']}, team1: '{t1}', team2: '{t2}', "
            f"slot1: '{s1}', slot2: '{s2}' }}"
        )
    return "  var MATCHES = [\n" + ",\n".join(lines) + "\n  ];"


def update_js(js_path, matches_block):
    """Replace the MATCHES array in r32-entry.js."""
    with open(js_path, "r") as f:
        content = f.read()

    # Match from "  var MATCHES = [" to the closing "];"
    pattern = r"  var MATCHES = \[.*?\];"
    replacement = matches_block

    new_content, count = re.subn(pattern, replacement, content, count=1, flags=re.DOTALL)
    if count == 0:
        print("ERROR: Could not find MATCHES array in r32-entry.js")
        return False

    with open(js_path, "w") as f:
        f.write(new_content)
    return True


def main():
    print(f"Reading {CSV_PATH}...")
    matches = read_matches(CSV_PATH)

    known = sum(1 for m in matches if m["team1"] != "?" and m["team2"] != "?")
    partial = sum(1 for m in matches if (m["team1"] != "?") != (m["team2"] != "?"))
    tbd = sum(1 for m in matches if m["team1"] == "?" and m["team2"] == "?")

    print(f"  {len(matches)} matches: {known} ready, {partial} partial, {tbd} TBD")
    print()

    for m in matches:
        t1 = m["team1"] if m["team1"] != "?" else f"({m['slot1']})"
        t2 = m["team2"] if m["team2"] != "?" else f"({m['slot2']})"
        status = "OK" if m["team1"] != "?" and m["team2"] != "?" else "TBD" if m["team1"] == "?" and m["team2"] == "?" else "partial"
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
