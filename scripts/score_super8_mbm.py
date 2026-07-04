#!/usr/bin/env python3
"""
T20 2026 Super 8 Match-by-Match Leaderboard Generator

Reads match-by-match predictions and results, generates updated super-8.md.

Scoring:
- Washout (Tie result): everyone gets 1 point
- Correct prediction: 1 point
- Incorrect: 0 points

Usage:
    uv run python score_super8_mbm.py
"""

import pandas as pd
import re
import os

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_FILE = os.path.join(SCRIPT_DIR, "../Match by Match T20 2026 Super8 Predictions.csv")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "../T20-2026-Super8-match-by-match-results.csv")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "../../active-contest/super-8.md")


def load_results(filepath):
    """Load results CSV. Returns dict {match_num: winner} and list of matches in order."""
    df = pd.read_csv(filepath)
    results = {}
    match_order = []
    for _, row in df.iterrows():
        match_num = int(row['Match'])
        winner = row['Winner'].strip()
        results[match_num] = winner
        match_order.append(match_num)
    return results, match_order, df


def load_predictions(filepath):
    """
    Load predictions CSV.
    Returns DataFrame with Name, Location, and one column per match.
    Column names are normalized to match number (int).
    """
    df = pd.read_csv(filepath)
    df = df.dropna(subset=['Your Name'])

    # Rename columns
    df = df.rename(columns={
        'Your Name': 'Name',
        'City/Country where you live': 'Location',
    })

    # Parse match columns: "43 - IND vs SA" -> match_num=43, matchup="INDvSA"
    match_cols = {}
    for col in df.columns:
        m = re.match(r'^(\d+)\s*-\s*(.+)$', col)
        if m:
            match_num = int(m.group(1))
            teams_raw = m.group(2).strip()
            # Normalize: "IND vs SA" -> "INDvSA", "NZ vs PAK" -> "NZvPAK"
            teams = teams_raw.replace(' vs ', 'v').replace(' ', '')
            match_cols[col] = match_num

    # Rename match columns to match numbers
    df = df.rename(columns=match_cols)

    # Keep only relevant columns
    keep_cols = ['Name', 'Location'] + list(match_cols.values())
    df = df[keep_cols]

    # Clean up name/location
    df['Name'] = df['Name'].str.strip()
    df['Location'] = df['Location'].str.strip().str.rstrip('/')

    return df


def score_predictions(pred_df, results, match_order):
    """
    Calculate scores for each participant.
    Returns pred_df with added 'total' column and per-match scoring info.
    """
    completed = [m for m in match_order if results.get(m, 'TBD') != 'TBD']
    n_completed = len(completed)

    def score_match(row, match_num):
        winner = results.get(match_num, 'TBD')
        if winner == 'TBD':
            return None
        if winner == 'Tie':
            return 1  # Washout: everyone gets 1
        pick = str(row[match_num]).strip() if match_num in row.index else ''
        return 1 if pick == winner else 0

    # Add score columns
    for m in match_order:
        score_col = f'score_{m}'
        pred_df[score_col] = pred_df.apply(lambda row: score_match(row, m), axis=1)

    # Total = sum of completed match scores
    score_cols = [f'score_{m}' for m in completed]
    pred_df['total'] = pred_df[score_cols].sum(axis=1)

    return pred_df, completed, n_completed


def assign_ranks(pred_df):
    """Assign tied ranks (T-1, T-2, etc.) sorted by total descending."""
    sorted_df = pred_df.sort_values('total', ascending=False).reset_index(drop=True)

    ranks = []
    prev_score = None
    prev_rank = None
    for i, row in sorted_df.iterrows():
        score = row['total']
        if score != prev_score:
            prev_rank = i + 1
            prev_score = score
        ranks.append(f'T-{prev_rank}')

    sorted_df['rank'] = ranks
    return sorted_df


def get_match_header_label(match_num, results_df):
    """Get the display label for a match column header."""
    row = results_df[results_df['Match'] == match_num].iloc[0]
    matchup = row['Matchup']
    winner = row['Winner']
    if winner == 'TBD':
        return matchup, ''
    elif winner == 'Tie':
        return matchup, 'Washout'
    else:
        return matchup, f'✓ {winner}'


def build_crowd_picks_section(pred_df, results, match_order, completed):
    """
    Build the 'Against the Crowd' section.
    Lists correct picks made by fewer than 25% of participants.
    """
    n_participants = len(pred_df)
    threshold = 0.25 * n_participants
    lines = []

    for match_num in completed:
        winner = results.get(match_num)
        if winner == 'TBD' or winner == 'Tie':
            continue

        row = None
        # Find matchup label
        matchup = None
        for col in pred_df.columns:
            if col == match_num:
                matchup = match_num
                break

        # Count who picked correctly
        correct_pickers = pred_df[pred_df[match_num] == winner]['Name'].tolist()
        n_correct = len(correct_pickers)

        if n_correct <= threshold:
            matchup_label = f'M{match_num}'
            # Get matchup name from original results
            pct = int(round(100 * n_correct / n_participants))
            names_bold = ', '.join(f'**{name}**' for name in correct_pickers)
            lines.append(
                f'- **{matchup_label} {winner} win** — '
                f'picked by only {n_correct} of {n_participants} ({pct}%): {names_bold}'
            )

    return lines


def generate_leaderboard_md(sorted_df, results, match_order, completed, results_df):
    """Generate the full super-8.md markdown content."""
    n_completed = len(completed)
    n_total = len(match_order)

    # Build match column headers
    header_cols = ['Rank', 'Name', 'Location', f'Total / {n_completed}']
    subheader_cols = ['', '', '', '']

    for match_num in match_order:
        matchup, note = get_match_header_label(match_num, results_df)
        header_cols.append(matchup)
        subheader_cols.append(note)

    # Build header row HTML
    th_cells = ''
    for col, note in zip(header_cols, subheader_cols):
        if note:
            th_cells += f'\n      <th>{col}<br><small>{note}</small></th>'
        else:
            th_cells += f'\n      <th>{col}</th>'

    # Build data rows
    rows_html = ''
    for _, row in sorted_df.iterrows():
        total = int(row['total'])
        cells = (
            f'      <td>{row["rank"]}</td>\n'
            f'      <td>{row["Name"]}</td>\n'
            f'      <td>{row["Location"]}</td>\n'
            f'      <td><strong>{total}/{n_completed}</strong></td>\n'
        )
        for match_num in match_order:
            pick = str(row[match_num]).strip() if match_num in row.index else '?'
            winner = results.get(match_num, 'TBD')
            is_correct = (
                winner != 'TBD' and (
                    winner == 'Tie' or pick == winner
                )
            )
            if winner == 'TBD':
                cells += f'      <td>{pick}</td>\n'
            elif is_correct:
                cells += f'      <td><strong>{pick}</strong></td>\n'
            else:
                cells += f'      <td>{pick}</td>\n'

        rows_html += f'    <tr>\n{cells}    </tr>\n'

    # Build crowd picks section
    crowd_lines = build_crowd_picks_section(sorted_df, results, match_order, completed)
    crowd_section = '\n'.join(crowd_lines) if crowd_lines else '*No crowd-busting picks yet.*'

    # Build washout note
    washouts = [results_df[results_df['Match'] == m].iloc[0]['Matchup']
                for m in completed if results.get(m) == 'Tie']
    washout_note = ''
    if washouts:
        washout_str = ', '.join(f'{m} (washout)' for m in washouts)
        washout_note = f' {washout_str}: all participants receive 1 point.'

    note_text = (
        f'*{n_completed} of {n_total} matches played. '
        f'Correct predictions are **bolded**.'
        f'{washout_note}*'
    )

    md = f"""---
layout: page
title: Super 8 Leaderboard
description: T20 2026 - Super 8 Results
background: '/img/cricket/bg_cricket.jpg'
permalink: "/t20-2026/super-8"
---

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap4.min.css">
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap4.min.js"></script>

<style>
  .table td, .table th {{
    white-space: nowrap;
    padding: 0.4rem 0.6rem;
    font-size: 0.85rem;
  }}
  .table th small {{
    font-weight: normal;
    color: #ccc;
  }}
</style>

## Contents
{{:.no_toc}}

* TOC
{{:toc}}

---

## Match by Match Leaderboard

{note_text}

<table id="super8MBMTable" class="table table-striped table-bordered table-sm table-hover">
  <thead class="thead-dark">
    <tr>{th_cells}
    </tr>
  </thead>
  <tbody>
{rows_html}  </tbody>
</table>

<script>
$(document).ready(function() {{
    $('#super8MBMTable').DataTable({{
        "paging": false,
        "searching": true,
        "info": false,
        "order": [[3, "desc"]]
    }});
}});
</script>

---

## Against the Crowd

*Correct picks made by fewer than 25% of participants ({int(0.25 * len(sorted_df))} or fewer of {len(sorted_df)}).*

{crowd_section}

---

[Overall Leaderboard]({{{{ site.baseurl }}}}/t20-2026/leaderboard) | [Group Stage]({{{{ site.baseurl }}}}/t20-2026/group-stage)
"""
    return md


def main():
    print("Loading predictions...")
    pred_df = load_predictions(PREDICTIONS_FILE)
    print(f"  {len(pred_df)} participants loaded")

    print("Loading results...")
    results, match_order, results_df = load_results(RESULTS_FILE)
    completed = [m for m in match_order if results.get(m, 'TBD') != 'TBD']
    print(f"  {len(completed)} of {len(match_order)} matches completed: {completed}")

    print("Scoring predictions...")
    pred_df, completed, n_completed = score_predictions(pred_df, results, match_order)

    print("Assigning ranks...")
    sorted_df = assign_ranks(pred_df)

    print("Generating leaderboard markdown...")
    md = generate_leaderboard_md(sorted_df, results, match_order, completed, results_df)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(md)

    print(f"\nDone! Written to: {OUTPUT_FILE}")
    print(f"\nTop 5:")
    for _, row in sorted_df.head(5).iterrows():
        print(f"  {row['rank']:5s} {row['Name']:25s} {int(row['total'])}/{n_completed}")


if __name__ == '__main__':
    main()
