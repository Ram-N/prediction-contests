#!/usr/bin/env python3
"""
Merge and process LR 4-2-1 predictions from two Google Form tabs,
deduplicate, add AI predictions, and output clean CSV + markdown table.

Usage:
    uv run --with openpyxl --with pandas python scripts/process_lr421_predictions.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PII_DIR = PROJECT_ROOT / "pii-data" / "FIFA-2026"
EXCEL_FILE = PII_DIR / "form-responses" / "LR 4-2-1 FIFA WC 2026.xlsx"
SUPPLEMENTAL_CSV = PII_DIR / "form-responses" / "LR 4-2-1-adds.csv"
OUTPUT_CSV = PROJECT_ROOT / "active-contest" / "data" / "predictions" / "LR-421-Predictions-Clean.csv"
CONTACTS_CSV = PII_DIR / "LR-421-Contacts.csv"
TABLE_MD = PROJECT_ROOT / "active-contest" / "data" / "predictions" / "LR-421-Predictions-Table.md"
ACTIVE_CONTEST_TABLE = PROJECT_ROOT / "active-contest" / "predictions-lr421-table.md"

# Standard column names
COLS = [
    "Timestamp", "Name", "Email", "Location",
    "Semi_1", "Semi_2", "Semi_3", "Semi_4",
    "Finalist_1", "Finalist_2", "Winner",
]


# Name normalization: map short/alternate names to canonical forms
NAME_MAP = {
    "RN": "Ram N",
}

# Email aliases: map alternate emails to a canonical email (for dedup)
EMAIL_ALIASES = {}


def read_sheet1(path: Path) -> pd.DataFrame:
    """Read Sheet1 (original Google Form) and normalize columns."""
    df = pd.read_excel(path, sheet_name="Sheet1")
    df.columns = COLS[:2] + ["Email"] + COLS[3:]  # Email is col 1 in Sheet1
    # Sheet1 has columns: Timestamp, Email Address, Name, Location, ...
    # Re-read with proper mapping
    df = pd.read_excel(path, sheet_name="Sheet1")
    df.columns = [
        "Timestamp", "Email", "Name", "Location",
        "Semi_1", "Semi_2", "Semi_3", "Semi_4",
        "Finalist_1", "Finalist_2", "Winner",
    ]
    # Reorder to standard
    df = df[COLS]
    return df


def read_entries(path: Path) -> pd.DataFrame:
    """Read Entries tab (website form) — already has standard column names."""
    df = pd.read_excel(path, sheet_name="Entries")
    df.columns = COLS
    return df


def normalize_names(df: pd.DataFrame) -> pd.DataFrame:
    """Apply name mapping and strip whitespace."""
    df["Name"] = df["Name"].str.strip()
    df["Location"] = df["Location"].str.strip()
    df["Name"] = df["Name"].replace(NAME_MAP)
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep latest entry per person. Uses Email as primary key to identify
    the same person across tabs (handles name variations like RN/Ram N).
    Falls back to Name only when email is missing."""
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
    df = df.sort_values("Timestamp", ascending=False)

    df["_email_lower"] = df["Email"].astype(str).str.strip().str.lower()
    df["_email_lower"] = df["_email_lower"].replace(EMAIL_ALIASES)

    # Deduplicate by email (same email = same person, keep latest)
    before = len(df)
    df = df.drop_duplicates(subset="_email_lower", keep="first")
    after = len(df)
    print(f"Deduplicated: {before} → {after} (removed {before - after} duplicates)")

    # For the kept rows, use the latest entry's name (already sorted desc)
    df = df.drop(columns=["_email_lower"])
    return df


def add_ai_predictions() -> pd.DataFrame:
    """Create AI prediction rows from markdown files."""
    ai_entries = []

    # Claude
    ai_entries.append({
        "Timestamp": "2026-06-10",
        "Name": "Claude (AI)",
        "Email": "",
        "Location": "AI",
        "Semi_1": "Spain",
        "Semi_2": "France",
        "Semi_3": "England",
        "Semi_4": "Argentina",
        "Finalist_1": "Spain",
        "Finalist_2": "England",
        "Winner": "Spain",
    })

    # ChatGPT
    ai_entries.append({
        "Timestamp": "2026-06-10",
        "Name": "ChatGPT (AI)",
        "Email": "",
        "Location": "AI",
        "Semi_1": "Spain",
        "Semi_2": "France",
        "Semi_3": "Brazil",
        "Semi_4": "Argentina",
        "Finalist_1": "Spain",
        "Finalist_2": "France",
        "Winner": "Spain",
    })

    # Gemini
    ai_entries.append({
        "Timestamp": "2026-06-10",
        "Name": "Gemini (AI)",
        "Email": "",
        "Location": "AI",
        "Semi_1": "Spain",
        "Semi_2": "France",
        "Semi_3": "England",
        "Semi_4": "Argentina",
        "Finalist_1": "Spain",
        "Finalist_2": "France",
        "Winner": "Spain",
    })

    return pd.DataFrame(ai_entries)


def generate_markdown_table(df: pd.DataFrame) -> str:
    """Generate a Bootstrap-styled markdown table for the predictions page."""
    lines = []
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(
        "| # | Name | Location | Semi 1 | Semi 2 | Semi 3 | Semi 4 "
        "| Finalist 1 | Finalist 2 | Winner |"
    )
    lines.append(
        "|---|------|----------|--------|--------|--------|--------"
        "|------------|------------|--------|"
    )

    # Split AI and human entries
    display_df = df.sort_values("Name", key=lambda s: s.str.lower())
    ai_df = display_df[display_df["Name"].str.contains("(AI)", regex=False)]
    human_df = display_df[~display_df["Name"].str.contains("(AI)", regex=False)]

    # AI entries first with robot emoji
    for _, row in ai_df.iterrows():
        lines.append(
            f"| 🤖 | {row['Name']} | {row['Location']} "
            f"| {row['Semi_1']} | {row['Semi_2']} | {row['Semi_3']} | {row['Semi_4']} "
            f"| {row['Finalist_1']} | {row['Finalist_2']} | **{row['Winner']}** |"
        )

    # Human entries numbered sequentially
    for i, (_, row) in enumerate(human_df.iterrows(), 1):
        lines.append(
            f"| {i} | {row['Name']} | {row['Location']} "
            f"| {row['Semi_1']} | {row['Semi_2']} | {row['Semi_3']} | {row['Semi_4']} "
            f"| {row['Finalist_1']} | {row['Finalist_2']} | **{row['Winner']}** |"
        )

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("LR 4-2-1 Predictions — Merge & Process")
    print("=" * 60)

    # Read both tabs
    sheet1 = read_sheet1(EXCEL_FILE)
    entries = read_entries(EXCEL_FILE)
    print(f"\nSheet1: {len(sheet1)} entries")
    print(f"Entries: {len(entries)} entries")
    print(f"Combined: {len(sheet1) + len(entries)} entries")

    # Read supplemental CSV if it exists
    supplements = []
    if SUPPLEMENTAL_CSV.exists():
        df_supp = pd.read_csv(SUPPLEMENTAL_CSV)
        df_supp.columns = COLS
        print(f"Supplemental CSV: {len(df_supp)} entries")
        supplements.append(df_supp)

    # Combine
    combined = pd.concat([sheet1, entries] + supplements, ignore_index=True)

    # Normalize names
    combined = normalize_names(combined)

    # Deduplicate
    combined = deduplicate(combined)

    # Add AI predictions
    ai_df = add_ai_predictions()
    final = pd.concat([combined, ai_df], ignore_index=True)
    print(f"After adding 3 AI entries: {len(final)} total participants")

    # Sort by name for output
    final = final.sort_values("Name", key=lambda s: s.str.lower())
    final = final.reset_index(drop=True)

    # Output clean CSV (no emails)
    clean = final.drop(columns=["Email", "Timestamp"])
    clean.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote clean CSV: {OUTPUT_CSV}")

    # Output contacts CSV
    contacts = final[final["Email"].astype(str).str.contains("@", na=False)][
        ["Name", "Email"]
    ].drop_duplicates()
    contacts.to_csv(CONTACTS_CSV, index=False)
    print(f"Wrote contacts CSV: {CONTACTS_CSV}")

    # Generate markdown table
    table_md = generate_markdown_table(clean)
    TABLE_MD.write_text(table_md)
    ACTIVE_CONTEST_TABLE.write_text(table_md)
    print(f"Wrote markdown table: {TABLE_MD}")
    print(f"Copied to active-contest: {ACTIVE_CONTEST_TABLE}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Final participant count: {len(final)}")
    vivek_count = len(final[final["Name"].str.contains("Vivek", case=False)])
    print(f"Vivek entries: {vivek_count} (should be 2 — different people)")
    ai_count = len(final[final["Name"].str.contains("(AI)", regex=False)])
    print(f"AI entries: {ai_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
