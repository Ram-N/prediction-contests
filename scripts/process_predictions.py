#!/usr/bin/env python3
"""
Process NFL 2025 Playoff Predictions
Converts Google Forms CSV to clean markdown table for Jekyll site
"""

import pandas as pd

# Configuration
INPUT_FILE = '../NFL-2025-Predictions.csv'
OUTPUT_FILE = '../NFL-2025-Predictions-Clean.csv'

# Team abbreviation mapping (extract team names from verbose column headers)
TEAM_ABBREV = {
    'AFC   Buffalo Bills- (Enter  a Confidence Score   from 1 to 100)  High number = high confidence of winning': 'BUF',
    'AFC   Denver Broncos - (Enter a Confidence Score from 1 to 100)  High number = high confidence of winning': 'DEN',
    'AFC   Houston Texans (Enter  a Confidence Score  from 1 to 100)  High number = high confidence of winning': 'HOU',
    'AFC   NE Patriots (Enter  a Confidence Score   from 1 to 100)  High number = high confidence of winning': 'NE',
    'NFC  San Francisco 49ers  (Enter an integer from 1 to 100)  High number = high confidence of winning': 'SF',
    'NFC  Seattle Seahawks  (Enter  a Confidence Score   from 1 to 100)  High number = high confidence of winning': 'SEA',
    'NFC  Los Angeles Rams (Enter  a Confidence Score from 1 to 100)  High number = high confidence of winning': 'LAR',
    'NFC  Chicago Bears  (Enter  a Confidence Score from 1 to 100)  High number = high confidence of winning': 'CHI'
}

def process_predictions():
    """Load and process predictions CSV"""

    # Read CSV
    df = pd.read_csv(INPUT_FILE)

    # Drop Email Address column (privacy)
    df = df.drop('Email Address', axis=1)

    # Rename team columns to abbreviations
    df = df.rename(columns=TEAM_ABBREV)

    # Convert prediction columns to numeric
    team_cols = list(TEAM_ABBREV.values())
    for col in team_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Keep only Name and team predictions (drop Timestamp for cleaner display)
    cols_to_keep = ['Your Name'] + team_cols
    df_clean = df[cols_to_keep]

    # Rename 'Your Name' to just 'Name'
    df_clean = df_clean.rename(columns={'Your Name': 'Name'})

    return df_clean


def generate_markdown_table(df):
    """Generate Bootstrap-styled markdown table for Jekyll"""

    # Bootstrap table styling (matches existing leaderboard style)
    table_style = "{:.thead-dark .table-striped .table-bordered .table-sm }"

    # Generate markdown with pandas
    md_table = df.to_markdown(index=False)

    # Combine with styling
    output = f"{table_style}\n{md_table}"

    return output


def main():
    """Main processing pipeline"""

    print("Processing NFL 2025 Predictions...")

    # Load and clean data
    df = process_predictions()

    print(f"\nProcessed {len(df)} predictions")
    print(f"\nTeams: {', '.join(df.columns[1:])}")

    # Save clean CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nClean CSV saved to: {OUTPUT_FILE}")

    # Generate markdown table
    md_table = generate_markdown_table(df)

    print("\n" + "="*60)
    print("MARKDOWN TABLE FOR predictions.md")
    print("="*60)
    print(md_table)
    print("="*60)

    # Save markdown to file
    md_file = '../NFL-2025-Predictions-Table.md'
    with open(md_file, 'w') as f:
        f.write(md_table)
    print(f"\nMarkdown table saved to: {md_file}")


if __name__ == "__main__":
    main()
