#!/usr/bin/env python3
"""Generate ST-421 predictions table and clean CSV from raw submissions."""

import csv
from collections import Counter

# --- Config ---
CSV_PATH = "active-contest/data/predictions/FIFA-2026-ST-421-Predictions.csv"
CANONICAL_LOCATIONS_PATH = "active-contest/data/canonical-locations.csv"
CLEAN_CSV_PATH = "active-contest/data/predictions/ST-421-Predictions-Clean.csv"
OUTPUT_TABLE_PATH = "active-contest/predictions-st421-table.md"

QF_MATCHES = ["FRA v MAR", "ESP v BEL", "ENG v NOR", "ARG v SUI"]
FINALIST_COLS = ["SF1", "SF2"]
ALL_PICKS = QF_MATCHES + FINALIST_COLS + ["Winner"]

COUNTRY_ABBREV = {
    "France": "FRA", "Morocco": "MAR",
    "Spain": "ESP", "Belgium": "BEL",
    "England": "ENG", "Norway": "NOR",
    "Argentina": "ARG", "Switzerland": "SUI",
}

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}


def load_canonical_locations(path):
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["Name"].strip()] = row["Location"].strip()
    return mapping


def parse_entries(path):
    """Parse CSV, deduplicate by email (latest wins), AI entries kept separate."""
    entries = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Name"].strip()
            email = row.get("Email", "").strip()
            timestamp = row["Timestamp"].strip()

            key = name if name in AI_NAMES else email.lower()

            picks = {col: row[col].strip() for col in ALL_PICKS}
            entry = {
                "timestamp": timestamp,
                "name": name,
                "email": email,
                "location": row["Location"].strip(),
                "picks": picks,
            }

            if key not in entries or timestamp > entries[key]["timestamp"]:
                entries[key] = entry

    return entries


def write_clean_csv(entries, path):
    """Write clean CSV with email stripped, sorted alphabetically."""
    ai_rows = sorted(
        [e for e in entries.values() if e["name"] in AI_NAMES],
        key=lambda x: x["name"]
    )
    human_rows = sorted(
        [e for e in entries.values() if e["name"] not in AI_NAMES],
        key=lambda x: x["name"].lower()
    )

    fieldnames = ["Name", "Location"] + ALL_PICKS
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in ai_rows + human_rows:
            row = {"Name": entry["name"], "Location": entry["location"]}
            row.update(entry["picks"])
            writer.writerow(row)

    print(f"Written clean CSV: {path} ({len(ai_rows)} AI + {len(human_rows)} humans)")


def compute_wotc(entries):
    human_entries = [e for e in entries.values() if e["name"] not in AI_NAMES]
    wotc = {}
    for col in ALL_PICKS:
        picks = [e["picks"][col] for e in human_entries]
        counter = Counter(picks)
        wotc[col] = counter.most_common(1)[0][0]
    return wotc


def generate_table(entries, canonical_locations):
    lines = []

    col_headers = ["Name", "Location", "FRA v MAR", "ESP v BEL", "ENG v NOR", "ARG v SUI", "Finalist 1", "Finalist 2", "Winner"]
    header = "| " + " | ".join(col_headers) + " |"
    sep = "|" + "|".join(["---"] * len(col_headers)) + "|"
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    # Build processed list
    processed = []
    for key, entry in entries.items():
        name = entry["name"]
        if name in AI_NAMES:
            location = "🤖 AI"
            canon_name = name
        else:
            canon_name = name
            location = canonical_locations.get(name, entry["location"])

        processed.append({
            "name": canon_name,
            "location": location,
            "picks": entry["picks"],
            "is_ai": name in AI_NAMES,
            "is_wotc": False,
        })

    # WOTC entry
    wotc_picks_raw = compute_wotc(entries)
    processed.append({
        "name": "WOTC",
        "location": "👥 Crowd",
        "picks": wotc_picks_raw,
        "is_ai": False,
        "is_wotc": True,
    })

    ai_entries = sorted([p for p in processed if p["is_ai"]], key=lambda x: x["name"])
    wotc_entries = [p for p in processed if p["is_wotc"]]
    human_entries = sorted(
        [p for p in processed if not p["is_ai"] and not p["is_wotc"]],
        key=lambda x: x["name"].lower()
    )

    all_sorted = ai_entries + wotc_entries + human_entries

    for entry in all_sorted:
        p = entry["picks"]
        cells = [
            COUNTRY_ABBREV.get(p["FRA v MAR"], p["FRA v MAR"]),
            COUNTRY_ABBREV.get(p["ESP v BEL"], p["ESP v BEL"]),
            COUNTRY_ABBREV.get(p["ENG v NOR"], p["ENG v NOR"]),
            COUNTRY_ABBREV.get(p["ARG v SUI"], p["ARG v SUI"]),
            COUNTRY_ABBREV.get(p["SF1"], p["SF1"]),
            COUNTRY_ABBREV.get(p["SF2"], p["SF2"]),
            f"**{COUNTRY_ABBREV.get(p['Winner'], p['Winner'])}**",
        ]
        row = f"| {entry['name']} | {entry['location']} | " + " | ".join(cells) + " |"
        lines.append(row)

    return "\n".join(lines), len(human_entries), len(ai_entries)


def main():
    canonical_locations = load_canonical_locations(CANONICAL_LOCATIONS_PATH)
    entries = parse_entries(CSV_PATH)

    write_clean_csv(entries, CLEAN_CSV_PATH)

    table, num_humans, num_ai = generate_table(entries, canonical_locations)

    with open(OUTPUT_TABLE_PATH, "w", encoding="utf-8") as f:
        f.write(table + "\n")

    print(f"Generated {OUTPUT_TABLE_PATH}")
    print(f"Total: {num_humans} humans + {num_ai} AI + 1 WOTC = {num_humans + num_ai + 1} rows")

    # Print WOTC summary
    wotc = compute_wotc(entries)
    print("\nWOTC picks:")
    for col in ALL_PICKS:
        print(f"  {col}: {COUNTRY_ABBREV.get(wotc[col], wotc[col])}")

    # Print deduped entries
    print(f"\nDeduped entries ({len(entries)}):")
    for e in sorted(entries.values(), key=lambda x: x["name"].lower()):
        print(f"  {e['name']} ({e['location']})")


if __name__ == "__main__":
    main()
