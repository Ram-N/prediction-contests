"""
Process FIFA 2026 Group Stage predictions from Excel into clean CSV and markdown table.

Input: pii-data/FIFA-2026/form-responses/FIFA Group Stage Responses.xlsx (two tabs)
  - Form Responses 1: Google Form wide format (12 entries)
  - Entries: Website compact format (42 entries)

Output:
  - active-contest/data/predictions/GroupStage-Predictions-Clean.csv (no emails)
  - pii-data/FIFA-2026/GroupStage-Contacts.csv (Name + Email)
  - active-contest/predictions-group-stage-table.md (markdown table)
"""

import pandas as pd
import os
import shutil
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
XLSX_PATH = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026", "form-responses", "FIFA Group Stage Responses.xlsx")
SUPPLEMENTAL_CSV = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026", "form-responses", "Group-stage-adds.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "active-contest", "data", "predictions")
ACTIVE_CONTEST_DIR = os.path.join(PROJECT_ROOT, "active-contest")

GROUPS = list("ABCDEFGHIJKL")

# Name normalization mapping
NAME_MAP = {
    "Narmada 237 Arvind": "Arvind Narayanan",
    "Arvind narayanan": "Arvind Narayanan",
}

# Entries to exclude by name
EXCLUDE_NAMES = {"Ram Test"}


def parse_form_responses(df):
    """Parse Form Responses 1 tab (wide format) into compact schema."""
    rows = []
    for _, row in df.iterrows():
        name = str(row["Your Name"]).strip()

        # Skip Ram N from Form Responses (has 10 third-place picks, use Entries version)
        if name == "Ram N":
            continue

        if name in EXCLUDE_NAMES:
            continue

        name = NAME_MAP.get(name, name)

        record = {
            "Timestamp": row["Timestamp"],
            "Name": name,
            "Email": str(row["Email Address"]).strip(),
            "Location": str(row.get("Location", "")).strip(),
        }

        # Parse R32 picks per group
        for g in GROUPS:
            r32_cols = [c for c in df.columns if f"Group {g} [" in c and "Pick the top two" in c]
            picked = []
            for c in r32_cols:
                val = row[c]
                if pd.notna(val) and "Advances" in str(val):
                    team = c.split("[")[1].rstrip("]")
                    picked.append(team)
            record[f"R32_{g}"] = ", ".join(picked)

        # Parse third-place picks
        third_cols = [c for c in df.columns if c.strip().startswith("[") and "-" in c]
        third_picks = []
        for c in third_cols:
            val = row[c]
            if pd.notna(val) and str(val).startswith("3rd"):
                col_name = c.strip().strip("[]")
                group_letter = col_name.split("-")[0]
                team_name = col_name.split("-", 1)[1]
                third_picks.append((val, f"{group_letter}: {team_name}"))

        # Sort by the "3rd Place-N" number
        third_picks.sort(key=lambda x: x[0])
        for i in range(8):
            if i < len(third_picks):
                record[f"3rd_{i+1}"] = third_picks[i][1]
            else:
                record[f"3rd_{i+1}"] = ""

        rows.append(record)
    return pd.DataFrame(rows)


def parse_entries(df):
    """Parse Entries tab (already compact format)."""
    rows = []
    for _, row in df.iterrows():
        name = str(row["Name"]).strip()

        if name in EXCLUDE_NAMES:
            continue

        name = NAME_MAP.get(name, name)

        email = str(row.get("Email", "")).strip()
        if email == "nan":
            email = ""

        record = {
            "Timestamp": row["Timestamp"],
            "Name": name,
            "Email": email,
            "Location": str(row.get("Location", "")).strip(),
        }

        for g in GROUPS:
            record[f"R32_{g}"] = str(row.get(f"R32_{g}", "")).strip()

        for i in range(1, 9):
            val = row.get(f"3rd_{i}", "")
            record[f"3rd_{i}"] = str(val).strip() if pd.notna(val) else ""

        rows.append(record)
    return pd.DataFrame(rows)


def deduplicate(df):
    """Deduplicate by email (latest timestamp wins). Handle Ram (no email) by name."""
    # Special handling: Ram with no email gets ramnarasimhan@gmail.com
    ram_mask = (df["Name"] == "Ram") & (df["Email"] == "")
    df.loc[ram_mask, "Name"] = "Ram N"
    df.loc[ram_mask, "Email"] = "ramnarasimhan@gmail.com"

    # Sort by timestamp descending so latest entry comes first
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
    df = df.sort_values("Timestamp", ascending=False)

    # For entries with email, deduplicate by email (latest wins)
    has_email = df["Email"] != ""
    deduped_email = df[has_email].drop_duplicates(subset="Email", keep="first")

    # For entries without email (shouldn't be any after Ram fix), deduplicate by name
    no_email = df[~has_email].drop_duplicates(subset="Name", keep="first")

    result = pd.concat([deduped_email, no_email], ignore_index=True)
    # Sort AI entries first, then humans alphabetically
    result["_is_ai"] = result["Name"].str.contains(r"\(AI\)", regex=True).map({True: 0, False: 1})
    result = result.sort_values(["_is_ai", "Name"], key=lambda s: s.str.lower() if s.name == "Name" else s).reset_index(drop=True)
    result = result.drop(columns=["_is_ai"])
    return result


def _get_third_by_group(row):
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


def _get_top2_set(row, group):
    """Get the top-2 picks for a group as a set of abbreviations."""
    r32_val = row[f"R32_{group}"]
    teams = [abbreviate_single_team(t.strip()) for t in str(r32_val).split(",")
             if t.strip() and t.strip() != "nan"]
    return set(teams)


def compute_wotc(df):
    """Compute Wisdom of the Crowd (WOTC) picks from participant data.

    Returns a dict with:
      - 'top2': {group_letter: set of 2 abbreviated team names}
      - 'third': {group_letter: abbreviated team name or None}
    """
    wotc = {"top2": {}, "third": {}}

    # Top-2 per group: pool all top-2 picks (position-agnostic), take 2 most common
    for g in GROUPS:
        all_picks = []
        for _, row in df.iterrows():
            r32_val = str(row[f"R32_{g}"])
            teams = [t.strip() for t in r32_val.split(",") if t.strip() and t.strip() != "nan"]
            for t in teams[:2]:
                all_picks.append(abbreviate_single_team(t))
        top_two = Counter(all_picks).most_common(2)
        wotc["top2"][g] = {t for t, _ in top_two}

    # Third-place: count how often each group is picked, take top 8
    group_counts = Counter()
    group_team_counts = {g: Counter() for g in GROUPS}
    for _, row in df.iterrows():
        third_by_group = _get_third_by_group(row)
        for g, team in third_by_group.items():
            group_counts[g] += 1
            group_team_counts[g][team] += 1

    top_8_groups = [g for g, _ in group_counts.most_common(8)]
    for g in GROUPS:
        if g in top_8_groups and group_team_counts[g]:
            wotc["third"][g] = group_team_counts[g].most_common(1)[0][0]
        else:
            wotc["third"][g] = None

    return wotc


def calculate_herd_score(row, wotc):
    """Calculate how closely a participant's picks match the WOTC.

    Compares 24 top-2 slots (unordered set, 2 per group) and
    8 third-place slots (only groups where WOTC has a pick).
    Returns (matches, 32).
    """
    matches = 0

    for g in GROUPS:
        # Top-2: unordered set intersection
        participant_top2 = _get_top2_set(row, g)
        wotc_top2 = wotc["top2"][g]
        matches += len(participant_top2 & wotc_top2)

    # Third-place: only compare groups where WOTC has a pick
    participant_third = _get_third_by_group(row)
    for g in GROUPS:
        wotc_third = wotc["third"][g]
        if wotc_third is None:
            continue  # WOTC has no consensus for this group, skip
        participant_team = participant_third.get(g)
        if participant_team == wotc_third:
            matches += 1

    return matches


def generate_markdown_table(df, wotc=None):
    """Generate markdown table for predictions.

    Each group column shows the two R32 picks, then a <br> and the
    3rd-place pick (abbreviated) if the participant chose a team from
    that group, or '---' if not.
    """
    lines = []
    if wotc:
        header = "| Name | Location | A | B | C | D | E | F | G | H | I | J | K | L | WOTC% |"
        sep = "|------|----------|---|---|---|---|---|---|---|---|---|---|---|---|-------|"
    else:
        header = "| Name | Location | A | B | C | D | E | F | G | H | I | J | K | L |"
        sep = "|------|----------|---|---|---|---|---|---|---|---|---|---|---|---|"
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    for idx, row in df.iterrows():
        num = idx + 1
        name = row["Name"]
        loc = row["Location"] if row["Location"] != "nan" else ""

        # Build a map of group letter -> 3rd place team name
        third_by_group = {}
        for i in range(1, 9):
            val = row.get(f"3rd_{i}", "")
            if val and str(val) != "nan":
                val = str(val).strip()
                # Format is "X: Team Name" where X is the group letter
                if ":" in val:
                    group_letter = val.split(":")[0].strip()
                    team_name = val.split(":", 1)[1].strip()
                    third_by_group[group_letter] = team_name

        group_cells = []
        for g in GROUPS:
            r32_val = row[f"R32_{g}"]
            r32_teams = [t.strip() for t in str(r32_val).split(",") if t.strip() and t.strip() != "nan"]
            r32_abbrs = [abbreviate_single_team(t) for t in r32_teams]
            third_team = third_by_group.get(g, "")
            if third_team:
                third_abbr = f'<span style="color:#2563EB">{abbreviate_single_team(third_team)}</span>'
            else:
                third_abbr = '<span style="color:#2563EB">---</span>'
            group_cells.append("<br>".join(r32_abbrs + [third_abbr]))

        cells = [name, loc] + group_cells
        if wotc:
            herd = calculate_herd_score(row, wotc)
            cells.append(f"{herd}/32")
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


TEAM_ABBREVS = {
    "Mexico": "MEX",
    "South Africa": "RSA",
    "Korea Republic": "KOR",
    "South Korea": "KOR",
    "Czechia": "CZE",
    "Canada": "CAN",
    "Bosnia and Herzegovina": "BIH",
    "Bosnia & Herz.": "BIH",
    "Bosnia": "BIH",
    "Qatar": "QAT",
    "Switzerland": "SUI",
    "Brazil": "BRA",
    "Morocco": "MAR",
    "Scotland": "SCO",
    "Haiti": "HAI",
    "United States": "USA",
    "USA": "USA",
    "Australia": "AUS",
    "Paraguay": "PAR",
    "Turkey": "TUR",
    "Türkiye": "TUR",
    "Germany": "GER",
    "Ecuador": "ECU",
    "Côte d'Ivoire": "CIV",
    "Ivory Coast": "CIV",
    "Curaçao": "CUR",
    "Netherlands": "NED",
    "Japan": "JPN",
    "Tunisia": "TUN",
    "Sweden": "SWE",
    "Belgium": "BEL",
    "Iran": "IRN",
    "IR Iran": "IRN",
    "Egypt": "EGY",
    "New Zealand": "NZL",
    "Spain": "ESP",
    "Uruguay": "URU",
    "Saudi Arabia": "KSA",
    "Cabo Verde": "CPV",
    "Cape Verde": "CPV",
    "France": "FRA",
    "Norway": "NOR",
    "Senegal": "SEN",
    "Iraq": "IRQ",
    "Argentina": "ARG",
    "Austria": "AUT",
    "Algeria": "ALG",
    "Jordan": "JOR",
    "Portugal": "POR",
    "Colombia": "COL",
    "Uzbekistan": "UZB",
    "DR Congo": "COD",
    "Congo DR": "COD",
    "England": "ENG",
    "Croatia": "CRO",
    "Ghana": "GHA",
    "Panama": "PAN",
}


def abbreviate_single_team(team_name):
    """Abbreviate a single team name."""
    return TEAM_ABBREVS.get(team_name.strip(), team_name.strip())


def abbreviate_teams(team_str):
    """Abbreviate comma-separated team names for compact table display."""
    if not team_str or team_str == "nan":
        return ""
    teams = [t.strip() for t in team_str.split(",")]
    abbreviated = [TEAM_ABBREVS.get(t, t) for t in teams]
    return ", ".join(abbreviated)


def main():
    print("Reading Excel file...")
    df_form = pd.read_excel(XLSX_PATH, sheet_name="Form Responses 1")
    df_entries = pd.read_excel(XLSX_PATH, sheet_name="Entries")

    print(f"Form Responses 1: {len(df_form)} rows")
    print(f"Entries: {len(df_entries)} rows")

    # Parse both tabs
    parsed_form = parse_form_responses(df_form)
    parsed_entries = parse_entries(df_entries)

    print(f"Parsed from Form Responses 1: {len(parsed_form)} rows (after exclusions)")
    print(f"Parsed from Entries: {len(parsed_entries)} rows (after exclusions)")

    # Read supplemental CSV if it exists
    supplements = []
    if os.path.exists(SUPPLEMENTAL_CSV):
        df_supp = pd.read_csv(SUPPLEMENTAL_CSV)
        parsed_supp = parse_entries(df_supp)
        print(f"Supplemental CSV: {len(df_supp)} rows → {len(parsed_supp)} after exclusions")
        supplements.append(parsed_supp)

    # Combine
    combined = pd.concat([parsed_form, parsed_entries] + supplements, ignore_index=True)
    print(f"Combined: {len(combined)} rows")

    # Deduplicate
    deduped = deduplicate(combined)
    print(f"After dedup: {len(deduped)} rows")

    # Show who was deduplicated
    all_names = combined["Name"].value_counts()
    dupes = all_names[all_names > 1]
    if len(dupes) > 0:
        print(f"\nDuplicate names resolved (latest entry kept):")
        for name, count in dupes.items():
            print(f"  {name}: {count} entries → 1")

    # Check for email-based deduplication
    combined_with_email = combined.copy()
    combined_with_email.loc[
        (combined_with_email["Name"] == "Ram") & (combined_with_email["Email"] == ""),
        "Email"
    ] = "ramnarasimhan@gmail.com"
    combined_with_email.loc[
        (combined_with_email["Name"] == "Ram") & (combined_with_email["Email"] == "ramnarasimhan@gmail.com"),
        "Name"
    ] = "Ram N"
    email_dupes = combined_with_email[combined_with_email["Email"] != ""]["Email"].value_counts()
    email_dupes = email_dupes[email_dupes > 1]
    if len(email_dupes) > 0:
        print(f"\nEmail-based deduplication:")
        for email, count in email_dupes.items():
            names = combined_with_email[combined_with_email["Email"] == email]["Name"].tolist()
            print(f"  {email} ({', '.join(names)}): {count} → 1")

    # Generate outputs
    target_cols = ["Timestamp", "Name", "Location"] + \
                  [f"R32_{g}" for g in GROUPS] + \
                  [f"3rd_{i}" for i in range(1, 9)]
    clean_df = deduped[target_cols].copy()

    contacts_df = deduped[["Name", "Email"]].copy()

    # Write clean CSV (no emails)
    clean_path = os.path.join(OUT_DIR, "GroupStage-Predictions-Clean.csv")
    clean_df.to_csv(clean_path, index=False)
    print(f"\nWrote {clean_path} ({len(clean_df)} rows)")

    # Write contacts CSV (to pii-data)
    contacts_dir = os.path.join(PROJECT_ROOT, "pii-data", "FIFA-2026")
    contacts_path = os.path.join(contacts_dir, "GroupStage-Contacts.csv")
    contacts_df.to_csv(contacts_path, index=False)
    print(f"Wrote {contacts_path}")

    # Compute WOTC from human participant data
    wotc = compute_wotc(clean_df)

    print(f"\n=== WOTC (Wisdom of the Crowd) ===")
    for g in GROUPS:
        top2 = ", ".join(sorted(wotc["top2"][g]))
        third = wotc["third"][g] or "---"
        print(f"  Group {g}: Top-2: {{{top2}}}  3rd: {third}")

    # Generate and write markdown table
    table_md = generate_markdown_table(clean_df, wotc=wotc)

    # Write markdown table directly to active-contest
    active_table_path = os.path.join(ACTIVE_CONTEST_DIR, "predictions-group-stage-table.md")
    with open(active_table_path, "w") as f:
        f.write(table_md)
    print(f"\nWrote {active_table_path}")

    # Summary
    print(f"\n=== Summary ===")
    print(f"Total unique entries: {len(deduped)}")
    print(f"Names: {', '.join(sorted(deduped['Name'].tolist(), key=str.lower))}")

    # Print herd score summary (sorted by score descending)
    print(f"\n=== Herd Scores ===")
    scores = []
    for _, row in clean_df.iterrows():
        scores.append((row["Name"], calculate_herd_score(row, wotc)))
    scores.sort(key=lambda x: -x[1])
    for name, score in scores:
        print(f"  {name}: {score}/32")


if __name__ == "__main__":
    main()
