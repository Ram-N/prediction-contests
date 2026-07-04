#!/usr/bin/env python3
"""Generate the R32 predictions table for predictions.md"""

import csv
from collections import OrderedDict

CSV_PATH = "pii-data/FIFA-2026/raw-predictions/FIFA-2026-R32-predictions.csv"
OUTPUT_PATH = "active-contest/predictions-r32-table.md"

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


def main():
    # Read CSV
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Deduplicate by email (keep latest — rows are in timestamp order)
    seen = {}
    for row in rows:
        email = row["Email"].strip().lower()
        # AI entries have empty/space emails — use Name as key
        if not email:
            email = f"__ai__{row['Name'].strip()}"
        seen[email] = row

    entries = list(seen.values())
    # Sort by name alphabetically
    entries.sort(key=lambda r: r["Name"].strip().lower())

    # Count humans vs AI
    ai_count = sum(1 for e in entries if "(AI)" in e["Name"])
    human_count = len(entries) - ai_count

    # Build match column headers
    match_cols = [f"{t1} v {t2}" for _, t1, t2 in MATCHES]
    match_fields = [f"Match {m}" for m, _, _ in MATCHES]

    # Build table
    lines = []
    # Header
    header = "| Name | Location | " + " | ".join(match_cols) + " |"
    sep = "|------|----------|" + "|".join(["---"] * len(match_cols)) + "|"
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    for entry in entries:
        name = entry["Name"].strip()
        location = entry["Location"].strip()
        picks = []
        for field in match_fields:
            val = entry[field].strip()
            abbr = ABBREV.get(val, val[:3].upper())
            picks.append(abbr)
        row_str = f"| {name} | {location} | " + " | ".join(picks) + " |"
        lines.append(row_str)

    table_text = "\n".join(lines) + "\n"

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(table_text)

    print(f"Generated R32 predictions table: {len(entries)} entries ({human_count} humans + {ai_count} AI)")
    print(f"Deduplicated from {len(rows)} raw rows")
    print(f"Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
