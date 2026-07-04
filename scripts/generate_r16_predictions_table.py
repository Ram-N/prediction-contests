#!/usr/bin/env python3
"""Generate R16 predictions table from CSV submissions."""

import csv
import io
from collections import Counter
from datetime import datetime

# --- Config ---
CSV_PATH = "pii-data/FIFA-2026/raw-predictions/FIFA2026-r16-predictions - Sheet1.csv"
CANONICAL_NAMES_PATH = "pii-data/FIFA-2026/canonical-names.csv"
CANONICAL_LOCATIONS_PATH = "active-contest/data/canonical-locations.csv"
OUTPUT_TABLE_PATH = "active-contest/predictions-r16-table.md"

MATCHES = [
    "CAN v MAR", "PAR v FRA", "BRA v NOR", "MEX v ENG",
    "ESP v POR", "USA v BEL", "EGY v ARG", "SUI v COL",
]

# Map full country name -> 3-letter abbreviation
COUNTRY_ABBREV = {
    "Canada": "CAN", "Morocco": "MAR",
    "Paraguay": "PAR", "France": "FRA",
    "Brazil": "BRA", "Norway": "NOR",
    "Mexico": "MEX", "England": "ENG",
    "Spain": "ESP", "Portugal": "POR",
    "United States": "USA", "Belgium": "BEL",
    "Egypt": "EGY", "Argentina": "ARG",
    "Switzerland": "SUI", "Colombia": "COL",
}

# Known email variants that map to the same person
EMAIL_ALIASES = {
    "goesfoinfinty@gmail.com": "goestoinfinity@gmail.com",  # typo
    "shnoong@gmail.com": "shnoong@yahoo.com",  # different domain
    "subtees@hotmail.com": "subtees@gmail.com",  # different domain
    "jrin2000@gmail.com": "jrin2000@gmsil.com",  # typo in canonical
    "keshavvenkatesh@gmail.com": "keshavvenkatesh211@gmail.com",  # variant
    "knarasim@terpmail.umd.edu": "keshavmp@gmail.com",  # different email
    "rupenderdahiya7@gmail.com": "rupenderdahiya5@gmail.com",  # variant
}

# AI entry names (these share Ram's email but are separate entries)
AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}


def load_canonical_names(path):
    """Load canonical name mapping: email -> canonical_name."""
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["canonical_email"].strip().lower()
            if email:
                mapping[email] = row["canonical_name"].strip()
    return mapping


def load_canonical_locations(path):
    """Load canonical location mapping: name -> location."""
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["Name"].strip()] = row["Location"].strip()
    return mapping


def resolve_email(email):
    """Resolve email aliases to canonical email."""
    e = email.strip().lower()
    return EMAIL_ALIASES.get(e, e)


def parse_entries(path):
    """Parse CSV, deduplicate by email (latest wins), AI entries kept separate."""
    entries = {}  # key: (resolved_email or ai_name) -> entry dict

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Name"].strip()
            email = row["Email"].strip()
            timestamp = row["Timestamp"].strip()

            # AI entries keyed by name, not email
            if name in AI_NAMES:
                key = name
            else:
                key = resolve_email(email)

            # Keep latest entry per key
            if key in entries:
                if timestamp > entries[key]["timestamp"]:
                    entries[key] = {
                        "timestamp": timestamp,
                        "name": name,
                        "email": email,
                        "location": row["Location"].strip(),
                        "picks": {
                            "CAN v MAR": row["CAN v MAR"].strip(),
                            "PAR v FRA": row["PAR v FRA"].strip(),
                            "BRA v NOR": row["BRA v NOR"].strip(),
                            "MEX v ENG": row["MEX v ENG"].strip(),
                            "ESP v POR": row["ESP v POR"].strip(),
                            "USA v BEL": row["USA v BEL"].strip(),
                            "EGY v ARG": row["EGY v ARG"].strip(),
                            "SUI v COL": row["SUI v COL"].strip(),
                        },
                    }
            else:
                entries[key] = {
                    "timestamp": timestamp,
                    "name": name,
                    "email": email,
                    "location": row["Location"].strip(),
                    "picks": {
                        "CAN v MAR": row["CAN v MAR"].strip(),
                        "PAR v FRA": row["PAR v FRA"].strip(),
                        "BRA v NOR": row["BRA v NOR"].strip(),
                        "MEX v ENG": row["MEX v ENG"].strip(),
                        "ESP v POR": row["ESP v POR"].strip(),
                        "USA v BEL": row["USA v BEL"].strip(),
                        "EGY v ARG": row["EGY v ARG"].strip(),
                        "SUI v COL": row["SUI v COL"].strip(),
                    },
                }

    return entries


def compute_wotc(entries):
    """Compute Wisdom of the Crowd - majority pick for each match."""
    # Only count human entries (exclude AI)
    human_entries = {k: v for k, v in entries.items() if k not in AI_NAMES}

    wotc = {}
    for match in MATCHES:
        picks = [e["picks"][match] for e in human_entries.values()]
        counter = Counter(picks)
        wotc[match] = counter.most_common(1)[0][0]
    return wotc


def generate_table(entries, canonical_names, canonical_locations):
    """Generate markdown predictions table."""
    lines = []

    # Header
    header = "| Name | Location | " + " | ".join(MATCHES) + " |"
    sep = "|------|----------|" + "|".join(["---"] * len(MATCHES)) + "|"
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    # Resolve canonical names and locations
    processed = []
    for key, entry in entries.items():
        if key in AI_NAMES:
            canon_name = key
            location = "🤖 AI"
        else:
            resolved_email = resolve_email(entry["email"])
            canon_name = canonical_names.get(resolved_email, entry["name"])
            # Use canonical location if available
            location = canonical_locations.get(canon_name, entry["location"])

        processed.append({
            "name": canon_name,
            "location": location,
            "picks": entry["picks"],
            "is_ai": key in AI_NAMES,
            "is_wotc": False,
        })

    # Compute WOTC
    wotc_picks = compute_wotc(entries)
    processed.append({
        "name": "WOTC",
        "location": "👥 Crowd",
        "picks": wotc_picks,
        "is_ai": False,
        "is_wotc": True,
    })

    # Sort: AI first, then WOTC, then humans alphabetically
    ai_entries = sorted([p for p in processed if p["is_ai"]], key=lambda x: x["name"])
    wotc_entries = [p for p in processed if p["is_wotc"]]
    human_entries = sorted(
        [p for p in processed if not p["is_ai"] and not p["is_wotc"]],
        key=lambda x: x["name"].lower()
    )

    all_sorted = ai_entries + wotc_entries + human_entries

    # Count humans
    num_humans = len(human_entries)
    num_ai = len(ai_entries)

    for entry in all_sorted:
        picks_cells = []
        for match in MATCHES:
            country = entry["picks"][match]
            abbrev = COUNTRY_ABBREV.get(country, country)
            picks_cells.append(abbrev)

        row = f"| {entry['name']} | {entry['location']} | " + " | ".join(picks_cells) + " |"
        lines.append(row)

    return "\n".join(lines), num_humans, num_ai


def main():
    canonical_names = load_canonical_names(CANONICAL_NAMES_PATH)
    canonical_locations = load_canonical_locations(CANONICAL_LOCATIONS_PATH)
    entries = parse_entries(CSV_PATH)

    table, num_humans, num_ai = generate_table(entries, canonical_names, canonical_locations)

    # Write table file
    with open(OUTPUT_TABLE_PATH, "w", encoding="utf-8") as f:
        f.write(table + "\n")

    print(f"Generated {OUTPUT_TABLE_PATH}")
    print(f"Total entries: {num_humans} humans + {num_ai} AI = {num_humans + num_ai + 1} (incl. WOTC)")

    # Print WOTC picks
    wotc = compute_wotc(entries)
    print("\nWOTC (Wisdom of the Crowd) picks:")
    for match in MATCHES:
        print(f"  {match}: {COUNTRY_ABBREV.get(wotc[match], wotc[match])}")

    # Print entries sorted by name for verification
    print(f"\nDeduped entries ({len(entries)}):")
    for key in sorted(entries.keys(), key=str.lower):
        e = entries[key]
        resolved = resolve_email(e["email"])
        canon = canonical_names.get(resolved, e["name"])
        print(f"  {canon} ({e['email']})")


if __name__ == "__main__":
    main()
