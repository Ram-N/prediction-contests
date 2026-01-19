#!/usr/bin/env python3
"""
Generic Contest Prediction Scoring Script

Calculates cross-entropy (log loss) penalties for contest predictions.
Generates leaderboard markdown and blog post for Jekyll site.

Configuration is read from contest_config.json.

Usage:
    python score_active_contest_predictions.py
"""

import pandas as pd
import math
from datetime import datetime
import os
import json


def load_config():
    """Load contest configuration from JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), 'contest_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def load_predictions(filepath):
    """Load predictions CSV into DataFrame."""
    df = pd.read_csv(filepath)
    # Remove any empty rows
    df = df.dropna(subset=['Name'])
    # Strip whitespace from names
    df['Name'] = df['Name'].str.strip()
    return df


def load_results(filepath, team_code_map):
    """
    Load results CSV and return dict {matchup: winner}.
    Skips games with TBD results.
    Normalizes team codes to match predictions.
    """
    df = pd.read_csv(filepath)
    results = {}

    for _, row in df.iterrows():
        matchup = str(row['Column']).strip()
        winner = str(row[' Winner']).strip()  # Note the space in column name

        if winner != 'TBD':
            # Normalize team codes
            winner = team_code_map.get(winner, winner)
            matchup_normalized = matchup
            for old, new in team_code_map.items():
                matchup_normalized = matchup_normalized.replace(old, new)

            results[matchup_normalized] = winner

    return results


def parse_matchup(matchup_str):
    """Parse 'BUF-DEN' into (team1, team2) tuple."""
    parts = matchup_str.split('-')
    if len(parts) != 2:
        raise ValueError(f"Invalid matchup format: {matchup_str}")
    return parts[0].strip(), parts[1].strip()


def calculate_penalty(score_team1, score_team2, winner, team1, team2):
    """
    Calculate cross-entropy penalty for a prediction.

    Formula: penalty = log2((score_team1 + score_team2) / score_winner)
    This is equivalent to: -log2(p_winner) where p_winner = score_winner / total

    Args:
        score_team1: Confidence score for team1
        score_team2: Confidence score for team2
        winner: The actual winning team code
        team1: First team code
        team2: Second team code

    Returns:
        (penalty, directionally_correct) tuple
        - penalty: float, rounded to 2 decimal places
        - directionally_correct: bool, True if higher score given to winner
    """
    total_score = score_team1 + score_team2

    if winner == team1:
        winner_score = score_team1
        loser_score = score_team2
    elif winner == team2:
        winner_score = score_team2
        loser_score = score_team1
    else:
        raise ValueError(f"Winner {winner} not in matchup {team1}-{team2}")

    # Avoid division by zero or log(0)
    if winner_score <= 0:
        winner_score = 0.01  # Minimum score to avoid infinity

    penalty = math.log2(total_score / winner_score)
    penalty = round(penalty, 2)

    # Check if directionally correct (winner score > loser score)
    directionally_correct = winner_score > loser_score

    return penalty, directionally_correct


def score_all_predictions(predictions_df, results_dict):
    """
    Score all predictions for completed games.

    Returns:
        DataFrame with columns:
        - Name
        - [Matchup columns with formatted penalties]
        - Total (sum across all games)
        Sorted by Total (lowest = best)
    """
    scored_data = []
    matchups = sorted(results_dict.keys())

    # Track best (lowest) penalty for each game
    best_penalties = {matchup: float('inf') for matchup in matchups}

    # First pass: calculate all penalties and find best per game
    temp_scores = []
    for _, row in predictions_df.iterrows():
        name = row['Name']
        game_penalties = {}

        for matchup in matchups:
            team1, team2 = parse_matchup(matchup)
            winner = results_dict[matchup]

            # Get scores from predictions
            score_team1 = float(row[team1])
            score_team2 = float(row[team2])

            penalty, directionally_correct = calculate_penalty(
                score_team1, score_team2, winner, team1, team2
            )

            game_penalties[matchup] = {
                'penalty': penalty,
                'directionally_correct': directionally_correct
            }

            # Track best penalty for this game
            if penalty < best_penalties[matchup]:
                best_penalties[matchup] = penalty

        temp_scores.append({
            'name': name,
            'penalties': game_penalties
        })

    # Second pass: format penalties with bold and underline
    for participant in temp_scores:
        row_data = {'Name': participant['name']}
        total_penalty = 0

        for matchup in matchups:
            penalty_info = participant['penalties'][matchup]
            penalty = penalty_info['penalty']
            directionally_correct = penalty_info['directionally_correct']
            is_best = (penalty == best_penalties[matchup])

            # Format penalty using HTML tags (markdown doesn't work well in kramdown tables)
            penalty_str = str(penalty)
            if directionally_correct and is_best:
                # Both bold and underlined
                penalty_str = f"<strong><u>{penalty_str}</u></strong>"
            elif directionally_correct:
                # Just bold
                penalty_str = f"<strong>{penalty_str}</strong>"
            elif is_best:
                # Just underlined
                penalty_str = f"<u>{penalty_str}</u>"

            row_data[matchup] = penalty_str
            total_penalty += penalty

        row_data['Total'] = round(total_penalty, 2)
        scored_data.append(row_data)

    # Create DataFrame and sort by Total
    scored_df = pd.DataFrame(scored_data)
    scored_df = scored_df.sort_values('Total')

    return scored_df


def calculate_ranks(scored_df):
    """
    Calculate ranks with tie handling.

    Args:
        scored_df: DataFrame sorted by Total score (ascending)

    Returns:
        List of rank strings (e.g., "1", "T-2", "T-2", "4")
    """
    ranks = []
    prev_score = None
    current_rank = 1
    tied_count = 0

    for idx, row in scored_df.iterrows():
        score = row['Total']

        if score == prev_score:
            # Tie with previous score
            tied_count += 1
            if tied_count == 1:
                # First tie - mark previous rank as tied
                ranks[-1] = f"T-{current_rank}"
            ranks.append(f"T-{current_rank}")
        else:
            # New score - update rank
            if tied_count > 0:
                # Skip ranks for tied entries
                current_rank += tied_count + 1
                tied_count = 0
            else:
                if len(ranks) > 0:
                    current_rank += 1

            ranks.append(str(current_rank))
            prev_score = score

    return ranks


def generate_leaderboard_table(scored_df):
    """
    Generate markdown table for leaderboard.

    Args:
        scored_df: Scored DataFrame with formatted penalties

    Returns:
        Markdown string for the table only
    """
    # Calculate ranks
    ranks = calculate_ranks(scored_df)

    # Get column names (exclude Name and Total)
    matchup_cols = [col for col in scored_df.columns if col not in ['Name', 'Total']]

    # Build table header with Rank as first column
    header_cols = ['Rank', 'Name', 'Total'] + matchup_cols

    table_md = "{:.thead-dark .table-striped .table-bordered .table-sm }\n"

    # Build table header row
    table_md += "| " + " | ".join(header_cols) + " |\n"

    # Build alignment row (Rank is centered, rest are right-aligned except Name)
    alignments = [":--------:", ":------------"] + ["---------:" for _ in range(len(header_cols) - 2)]
    table_md += "| " + " | ".join(alignments) + " |\n"

    # Build data rows
    for idx, (_, row) in enumerate(scored_df.iterrows()):
        row_values = [ranks[idx], str(row['Name']), str(row['Total'])] + [str(row[col]) for col in matchup_cols]
        table_md += "| " + " | ".join(row_values) + " |\n"

    return table_md


def generate_leaderboard_markdown(scored_df, games_scored, config):
    """
    Generate Jekyll markdown for leaderboard page.

    Args:
        scored_df: Scored DataFrame with formatted penalties
        games_scored: Number of completed games
        config: Contest configuration dictionary

    Returns:
        Markdown string for leaderboard file
    """
    total_games = config['total_games']
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']
    background_image = config['background_image']

    games_remaining = total_games - games_scored
    # Determine EST or EDT based on date
    import time
    is_dst = time.localtime().tm_isdst
    tz_name = "EDT" if is_dst else "EST"
    current_date = datetime.now().strftime(f"%B %d, %Y at %I:%M %p {tz_name}")

    markdown = f"""---
layout: page
title: Leaderboard
description: {contest_name} Playoff Predictions - Live Scoring
background: '{background_image}'
permalink: "/{contest_slug}/leaderboard"
---

*Last updated: {current_date}*

## Contest Status

**{games_scored} of {total_games} games completed** ({games_remaining} remaining)

---

## Current Leaderboard

Lower scores are better! The scoring uses cross-entropy (log loss) to penalize incorrect predictions more heavily.

- **Bold numbers** indicate directionally correct predictions (you gave the winner a higher confidence score)
- <u>Underlined numbers</u> indicate the best (lowest penalty) prediction for that game

"""

    # Add the leaderboard table
    markdown += generate_leaderboard_table(scored_df)

    # Add scoring explanation
    markdown += """

---

## How Scoring Works

The penalty for each game is calculated using cross-entropy (log loss):

**Penalty = log₂((Team1_Score + Team2_Score) / Winner_Score)**

This is equivalent to: **-log₂(probability you assigned to the winner)**

### Examples:

- **Perfect prediction** (100-1): penalty = log₂(101/100) = **0.01**
- **Confident correct** (80-20): penalty = log₂(100/80) = **0.32**
- **Moderate correct** (60-40): penalty = log₂(100/60) = **0.74**
- **50-50 prediction**: penalty = log₂(100/50) = **1.0** (not directionally correct)
- **Wrong direction** (40-60, winner got 40): penalty = log₂(100/40) = **1.32**
- **Very wrong** (20-80, winner got 20): penalty = log₂(100/20) = **2.32**

The more confident you were in the winner, the lower your penalty. Being confident in the loser results in high penalties!

---

"""
    # Add footer with liquid variables (can't use f-string escaping for this)
    markdown += "[View All Predictions]({{ site.baseurl }}/{{ site.contest.slug }}/predictions) | "
    markdown += "[Contest Rules]({{ site.baseurl }}/{{ site.contest.slug }}/rules)\n"

    return markdown


def generate_blog_post(scored_df, predictions_df, results_dict, games_scored, config):
    """
    Generate Jekyll blog post markdown with contest update.

    Args:
        scored_df: Scored DataFrame
        predictions_df: Original predictions DataFrame
        results_dict: Results dictionary {matchup: winner}
        games_scored: Number of completed games
        config: Contest configuration dictionary

    Returns:
        (filename, content) tuple
    """
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']
    background_image = config['background_image']
    round_names = config.get('round_names', {})

    current_date = datetime.now()
    date_str = current_date.strftime("%Y-%m-%d")
    date_with_tz = current_date.strftime("%Y-%m-%d %H:%M:%S -0500")

    # Determine round name based on games completed
    round_name = round_names.get(str(games_scored), f"{games_scored}-games")

    filename = f"{date_str}-{contest_slug}-after-{round_name}.md"

    # Get top 3 leaders
    top_3 = scored_df.head(3)
    leader_names = top_3['Name'].tolist()
    leader_scores = top_3['Total'].tolist()

    # Find who got all games right so far (all directionally correct)
    perfect_predictors = []
    for _, row in scored_df.iterrows():
        # Count bold predictions (directionally correct)
        bold_count = sum(1 for col in scored_df.columns
                        if col not in ['Name', 'Total'] and '**' in str(row[col]))
        if bold_count == games_scored:
            perfect_predictors.append(row['Name'])

    # Build game results section
    game_results = []
    for matchup in sorted(results_dict.keys()):
        team1, team2 = parse_matchup(matchup)
        winner = results_dict[matchup]
        loser = team2 if winner == team1 else team1
        game_results.append(f"- **{matchup}**: {winner} defeats {loser}")

    # Generate the leaderboard table
    table_md = generate_leaderboard_table(scored_df)

    content = f"""---
layout: post
title: "{leader_names[0]} leads with a penalty of {leader_scores[0]}"
subtitle: "Leaderboard Update: After {games_scored} Games"
date: {date_with_tz}
background: '{background_image}'
---

# {contest_name} - After {games_scored} Games

**Standings after {games_scored} games** (Lower scores are better!)

{table_md}

**Legend:**
- **Bold numbers** = Directionally correct predictions (you gave the winner a higher score)
- <u>Underlined numbers</u> = Best (lowest penalty) prediction for that game

---

### Current Leader

**{leader_names[0]}** is in first place with a total penalty of **{leader_scores[0]}**, followed by {leader_names[1]} ({leader_scores[1]}) and {leader_names[2]} ({leader_scores[2]}).

### Game Results

{"\n".join(game_results)}

{f"### Perfect Predictions So Far\n\nThese participants got **all {games_scored} games directionally correct**:\n\n" + "\n".join([f"- {name}" for name in perfect_predictors]) if perfect_predictors else "### No Perfect Predictors Yet\n\nNo one has gotten all games directionally correct so far. The competition is wide open!"}

---

## How Cross-Entropy Scoring Works

Our scoring system penalizes confident wrong predictions more heavily than tentative ones:

**Formula:** Penalty = log₂((Team1_Score + Team2_Score) / Winner_Score)

**Examples:**
- Confidently picked the winner (80-20): low penalty (~0.32)
- No strong opinion (50-50): penalty of 1.0
- Confidently picked the loser (20-80): high penalty (~2.32)

This rewards participants who correctly identified strong winners with high confidence!

---

"""
    # Add footer with liquid variables (can't use f-string escaping for this)
    content += "[See All Predictions]({{ site.baseurl }}/{{ site.contest.slug }}/predictions) | "
    content += "[Contest Rules]({{ site.baseurl }}/{{ site.contest.slug }}/rules) | "
    content += "[Leaderboard Page]({{ site.baseurl }}/{{ site.contest.slug }}/leaderboard)\n"

    return filename, content


def main():
    """Main execution function."""
    print("Contest Prediction Scoring")
    print("=" * 50)

    # Load configuration
    print("\nLoading configuration...")
    config = load_config()
    contest_name = config['contest_name']
    print(f"  ✓ Contest: {contest_name}")

    # Load data
    predictions_file = config['predictions_file']
    results_file = config['results_file']
    team_code_map = config.get('team_code_map', {})

    print(f"\nLoading predictions from: {predictions_file}")
    predictions_df = load_predictions(predictions_file)
    print(f"  ✓ Loaded {len(predictions_df)} participants")

    print(f"\nLoading results from: {results_file}")
    results_dict = load_results(results_file, team_code_map)
    games_scored = len(results_dict)
    print(f"  ✓ Loaded {games_scored} completed games")

    if games_scored == 0:
        print("\n⚠ No completed games yet. Skipping scoring.")
        return

    print("\nCompleted games:")
    for matchup, winner in sorted(results_dict.items()):
        print(f"  - {matchup}: {winner}")

    # Score predictions
    print("\nCalculating penalties...")
    scored_df = score_all_predictions(predictions_df, results_dict)
    print(f"  ✓ Scored all participants")

    # Display top 5
    print("\nTop 5 Current Leaders:")
    for i, row in scored_df.head(5).iterrows():
        print(f"  {i+1}. {row['Name']}: {row['Total']}")

    # Generate leaderboard
    print(f"\nGenerating leaderboard markdown...")
    leaderboard_md = generate_leaderboard_markdown(scored_df, games_scored, config)

    # Write leaderboard file
    leaderboard_path = os.path.join(os.path.dirname(__file__), config['leaderboard_file'])
    with open(leaderboard_path, 'w') as f:
        f.write(leaderboard_md)
    print(f"  ✓ Written to: {leaderboard_path}")

    # Generate blog post
    print(f"\nGenerating blog post...")
    blog_filename, blog_content = generate_blog_post(
        scored_df, predictions_df, results_dict, games_scored, config
    )

    # Write blog post file
    blog_post_path = os.path.join(os.path.dirname(__file__), config['blog_post_dir'], blog_filename)
    with open(blog_post_path, 'w') as f:
        f.write(blog_content)
    print(f"  ✓ Written to: {blog_post_path}")

    print("\n" + "=" * 50)
    print("✓ Scoring complete!")
    print("\nNext steps:")
    print("  1. Review the generated files")
    print("  2. Test locally: bundle exec jekyll serve")
    print("  3. Commit and push to GitHub")
    print("\nFiles updated:")
    print(f"  - {leaderboard_path}")
    print(f"  - {blog_post_path}")


if __name__ == "__main__":
    main()
