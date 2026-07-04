#!/usr/bin/env python3
"""
T20 2026 Group Stage Scoring Script

Scoring rubric:
- 1 point if you named a team that finished in the top 2 of a group (either position)
- 1 bonus point if you got the exact rank correct (1st or 2nd)
- Maximum score: 16 points (4 groups × 2 slots × 2 points each)

Higher scores are better.

Usage:
    uv run python score_t20_group_stage.py [--generate-blog] [--config CONFIG_FILE]
"""

import pandas as pd
from datetime import datetime
import os
import json
import sys
import random


def load_config(config_file='contest_config.json'):
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'r') as f:
        return json.load(f)


def load_predictions(filepath):
    df = pd.read_csv(filepath)
    df = df.dropna(subset=['Name'])
    df['Name'] = df['Name'].str.strip()
    return df


# Map from abbreviations (results file) to full names (predictions file)
TEAM_ABBREV_TO_FULL = {
    'IND': 'India',
    'PAK': 'Pakistan',
    'SL': 'Sri Lanka',
    'AUS': 'Australia',
    'ENG': 'England',
    'WI': 'West Indies',
    'SA': 'South Africa',
    'NZ': 'New Zealand',
    'AFG': 'Afghanistan',
    'ZIM': 'Zimbabwe',
    'BAN': 'Bangladesh',
    'IRE': 'Ireland',
    'SCO': 'Scotland',
    'NAM': 'Namibia',
    'USA': 'USA',
    'NEP': 'Nepal',
    'NET': 'Netherlands',
    'UAE': 'UAE',
    'OMA': 'Oman',
    'CAN': 'Canada',
}

# Inverted map: full name -> abbreviation (for display in leaderboard)
TEAM_FULL_TO_ABBREV = {v: k for k, v in TEAM_ABBREV_TO_FULL.items()}


def load_results(filepath):
    """
    Load results CSV with columns: Team, Result
    Returns dict like: {'A1': 'India', 'A2': 'Pakistan', 'B1': 'Sri Lanka', ...}
    Values are normalized to full team names matching the predictions file.
    """
    df = pd.read_csv(filepath)
    results = {}
    for _, row in df.iterrows():
        slot = str(row['Team']).strip()
        team = str(row[' Result']).strip()
        if team and team != 'TBD':
            # Normalize abbreviation to full name
            team_normalized = TEAM_ABBREV_TO_FULL.get(team.upper(), team)
            results[slot] = team_normalized
    return results


def score_participant(row, results):
    """
    Score a single participant's predictions.

    For each group (A, B, C, D):
      - Check X1 prediction vs actual X1 and X2
      - Check X2 prediction vs actual X1 and X2

    Returns:
        total_score (int), breakdown dict {slot: points}
    """
    breakdown = {}
    total = 0

    groups = ['A', 'B', 'C', 'D']
    for g in groups:
        actual_1 = results.get(f'{g}1', '').strip().lower()
        actual_2 = results.get(f'{g}2', '').strip().lower()

        pred_1_raw = str(row.get(f'{g}1', '')).strip()
        pred_2_raw = str(row.get(f'{g}2', '')).strip()
        pred_1 = pred_1_raw.lower()
        pred_2 = pred_2_raw.lower()

        # Score for slot 1 prediction
        pts_1 = 0
        if actual_1 and pred_1 == actual_1:
            pts_1 = 2  # correct team + correct rank
        elif actual_2 and pred_1 == actual_2:
            pts_1 = 1  # correct team, wrong rank
        breakdown[f'{g}1'] = pts_1
        breakdown[f'{g}1_pick'] = TEAM_FULL_TO_ABBREV.get(pred_1_raw, pred_1_raw)
        total += pts_1

        # Score for slot 2 prediction
        pts_2 = 0
        if actual_2 and pred_2 == actual_2:
            pts_2 = 2  # correct team + correct rank
        elif actual_1 and pred_2 == actual_1:
            pts_2 = 1  # correct team, wrong rank
        breakdown[f'{g}2'] = pts_2
        breakdown[f'{g}2_pick'] = TEAM_FULL_TO_ABBREV.get(pred_2_raw, pred_2_raw)
        total += pts_2

    return total, breakdown


def assign_ranks(df, score_col='Score'):
    """
    Assign ranks with tie handling: tied participants get T-N notation.
    E.g. if 3 people tie for 4th, all get 'T-4', next person gets 7.
    """
    ranks = []
    sorted_scores = df[score_col].sort_values(ascending=False).values
    score_to_rank = {}
    current_rank = 1
    for score in sorted_scores:
        if score not in score_to_rank:
            score_to_rank[score] = current_rank
        current_rank += 1

    # Count how many people share each score
    score_counts = df[score_col].value_counts()

    for _, row in df.iterrows():
        score = row[score_col]
        rank = score_to_rank[score]
        if score_counts[score] > 1:
            ranks.append(f'T-{rank}')
        else:
            ranks.append(str(rank))

    return ranks


def generate_overall_leaderboard_markdown(scored_df, config):
    """Generate Jekyll markdown for the overall leaderboard (Group + Super8 + KO columns)."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']
    bg = config.get('background_images', {}).get('leaderboard', '/img/bg-post.jpg')

    col_headers = '| Rank | Name | Location | AI | Group Stage | Super 8 | KO & Finals | Total |'
    col_align = '| :---: | :--- | :--- | :---: | ---: | ---: | ---: | ---: |'

    rows = []
    for _, row in scored_df.iterrows():
        ai_flag = '✓' if str(row.get('AI', '0')).strip() == '1' else ''
        location = '' if pd.isna(row.get('Location')) else str(row.get('Location', '')).strip()
        name = str(row['Name']).strip()
        rank = str(row['Rank'])
        group_score = int(row['Score'])
        super8_score = '-'
        ko_score = '-'
        total = group_score  # running total of available scores only
        row_str = f'| {rank} | {name} | {location} | {ai_flag} | {group_score} | {super8_score} | {ko_score} | {total} |'
        rows.append(row_str)

    table = f'{col_headers}\n{col_align}\n' + '\n'.join(rows)

    md = f"""---
layout: page
title: Overall Leaderboard
description: {contest_name} - Overall Standings
background: '{bg}'
permalink: "/{contest_slug}/leaderboard"
---

*Last updated: {now}*

## Overall Leaderboard

Higher scores are better. Rounds not yet played show **-**.

{{:.thead-dark .table-striped .table-bordered .table-sm }}
{table}

---

[Group Stage Details]({{{{ site.baseurl }}}}/{contest_slug}/group-stage) | [View All Predictions]({{{{ site.baseurl }}}}/{contest_slug}/predictions) | [Contest Rules]({{{{ site.baseurl }}}}/{contest_slug}/rules)
"""
    return md


def generate_group_stage_markdown(scored_df, results, config, games_scored):
    """Generate Jekyll markdown for the Group Stage detailed leaderboard page."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']
    bg = config.get('background_images', {}).get('leaderboard', '/img/bg-post.jpg')

    slots = [f'{g}{n}' for g in ['A', 'B', 'C', 'D'] for n in [1, 2]]

    col_headers = '| Rank | Name | Location | AI | Score |' + ' '.join(f' {s} |' for s in slots)
    col_align = '| :---: | :--- | :--- | :---: | ---: |' + ' :---: |' * len(slots)

    rows = []
    for _, row in scored_df.iterrows():
        ai_flag = '✓' if str(row.get('AI', '0')).strip() == '1' else ''
        location = '' if pd.isna(row.get('Location')) else str(row.get('Location', '')).strip()
        name = str(row['Name']).strip()
        rank = str(row['Rank'])
        score = int(row['Score'])

        cell_values = []
        for slot in slots:
            pts = int(row[slot])
            pick = str(row.get(slot + '_pick', '')).strip()
            if pts == 2:
                cell_values.append(f'**{pick} (2)**')
            elif pts == 1:
                cell_values.append(f'{pick} (1)')
            else:
                cell_values.append(pick)

        row_str = f'| {rank} | {name} | {location} | {ai_flag} | {score} | ' + ' | '.join(cell_values) + ' |'
        rows.append(row_str)

    table = f'{col_headers}\n{col_align}\n' + '\n'.join(rows)

    results_summary = ' | '.join(f'**{s}**: {results[s]}' for s in slots if s in results)

    md = f"""---
layout: page
title: Group Stage Leaderboard
description: {contest_name} - Group Stage Results
background: '{bg}'
permalink: "/{contest_slug}/group-stage"
---

*Last updated: {now}*

## Group Stage Leaderboard

Higher scores are better! Maximum possible score: **16 points**.

{{:.thead-dark .table-striped .table-bordered .table-sm }}
{table}

---

### Group Stage Results

{results_summary}

**Key:** **Team (2)** = correct team & rank | Team (1) = correct team, wrong rank | Team = incorrect (0 pts)

---

[Overall Leaderboard]({{{{ site.baseurl }}}}/{contest_slug}/leaderboard) | [View All Predictions]({{{{ site.baseurl }}}}/{contest_slug}/predictions) | [Contest Rules]({{{{ site.baseurl }}}}/{contest_slug}/rules)
"""
    return md


def generate_group_leaderboard_markdown(scored_df, group_name, results, config):
    """Generate Jekyll markdown for a group-specific leaderboard."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']
    bg = config.get('background_images', {}).get('leaderboard', '/img/bg-post.jpg')
    group_permalink = group_name.lower()

    slots = [f'{g}{n}' for g in ['A', 'B', 'C', 'D'] for n in [1, 2]]

    col_headers = '| Rank | Name | Location | AI | Score |' + ' '.join(f' {s} |' for s in slots)
    col_align = '| :---: | :--- | :--- | :---: | ---: |' + ' :---: |' * len(slots)

    rows = []
    for _, row in scored_df.iterrows():
        ai_flag = '✓' if str(row.get('AI', '0')).strip() == '1' else ''
        location = '' if pd.isna(row.get('Location')) else str(row.get('Location', '')).strip()
        name = str(row['Name']).strip()
        rank = str(row['Rank'])
        score = int(row['Score'])

        cell_values = []
        for slot in slots:
            pts = int(row[slot])
            pick = str(row.get(slot + '_pick', '')).strip()
            if pts == 2:
                cell_values.append(f'**{pick} (2)**')
            elif pts == 1:
                cell_values.append(f'{pick} (1)')
            else:
                cell_values.append(pick)

        row_str = f'| {rank} | {name} | {location} | {ai_flag} | {score} | ' + ' | '.join(cell_values) + ' |'
        rows.append(row_str)

    table = f'{col_headers}\n{col_align}\n' + '\n'.join(rows)

    results_summary = ' | '.join(f'**{s}**: {results[s]}' for s in slots if s in results)

    md = f"""---
layout: page
title: "Group Leaderboard - {group_name}"
description: {contest_name} - {group_name} Group Standings
background: '{bg}'
permalink: "/{contest_slug}/groups/{group_permalink}"
---

*Last updated: {now}*

## {group_name} Group Standings

Higher scores are better! Maximum possible score: **16 points**.

{{:.thead-dark .table-striped .table-bordered .table-sm }}
{table}

---

### Group Stage Results

{results_summary}

**Key:** **Team (2)** = correct team & rank | Team (1) = correct team, wrong rank | Team = incorrect (0 pts)
"""
    return md


def generate_score_chart(scored_df, output_dir):
    """
    Generate score distribution histogram with a green→yellow→orange color gradient
    (green = high scores, orange = low scores). AI participants shown with hatching.
    Saves PNG, returns path for embedding in blog.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np

    human_df = scored_df[scored_df['AI'].astype(str).str.strip() != '1']
    ai_df = scored_df[scored_df['AI'].astype(str).str.strip() == '1']

    fig, ax = plt.subplots(figsize=(7, 4))

    score_range = range(0, 17)
    # Color gradient: scores 6 and below = orange, 13 and above = green, interpolated between
    cmap = mcolors.LinearSegmentedColormap.from_list('score_grad', ['#f4a300', '#ffe066', '#4caf50'])

    def score_to_color(score):
        low, high = 6, 13
        t = max(0.0, min(1.0, (score - low) / (high - low)))
        return cmap(t)

    # Draw one bar per score value for humans
    human_counts = human_df['Score'].value_counts()
    for score in score_range:
        count = human_counts.get(score, 0)
        ax.bar(score, count, width=0.8, color=score_to_color(score),
               edgecolor='white', linewidth=0.8)

    # Overlay AI counts with hatching
    if not ai_df.empty:
        ai_counts = ai_df['Score'].value_counts()
        for score in score_range:
            count = ai_counts.get(score, 0)
            if count:
                human_count = human_counts.get(score, 0)
                ax.bar(score, count, bottom=human_count, width=0.8,
                       color=score_to_color(score), edgecolor='white',
                       linewidth=0.8, hatch='//', alpha=0.6)

    median = human_df['Score'].median()
    ax.axvline(median, color='#c0392b', linestyle='--', linewidth=1.8,
               label=f'Human median: {median:.0f}')

    # Highlight score=14: rectangle around bar + annotation
    from matplotlib.patches import FancyBboxPatch
    human_count_14 = human_counts.get(14, 0)
    if human_count_14 > 0:
        rect = FancyBboxPatch((13.6, -0.3), 0.8, human_count_14 + 0.6,
                              boxstyle='round,pad=0.1', linewidth=2,
                              edgecolor='#c0392b', facecolor='none', zorder=5)
        ax.add_patch(rect)
        ax.annotate('Only humans\nbeating the AI!',
                    xy=(14, human_count_14), xytext=(14.8, human_count_14 + 2),
                    fontsize=8, color='#c0392b', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.5),
                    ha='left')

    # Legend proxies
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4caf50', edgecolor='white', label=f'Humans ({len(human_df)})'),
        Patch(facecolor='grey', edgecolor='white', hatch='//', alpha=0.6, label=f'AI ({len(ai_df)})'),
        plt.Line2D([0], [0], color='#c0392b', linestyle='--', linewidth=1.8, label=f'Human median: {median:.0f}'),
    ]
    ax.legend(handles=legend_elements, fontsize=9)

    ax.set_title('T20 2026 Group Stage — Score Distribution', fontsize=12, fontweight='bold')
    ax.set_xlabel('Score (out of 16)', fontsize=10)
    ax.set_ylabel('Participants', fontsize=10)
    ax.set_xticks(range(0, 17))
    ax.tick_params(labelsize=9)
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 't20-2026-score-distribution.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    return out_path


def find_brave_predictions(predictions_df, results):
    """
    Find participants who correctly picked upset teams (teams most people didn't pick).
    A 'brave' prediction is one where fewer than 25% of participants picked that team
    for that slot, but the result was correct.
    Returns list of (name, slot, team) tuples.
    """
    slots = [f'{g}{n}' for g in ['A', 'B', 'C', 'D'] for n in [1, 2]]
    total = len(predictions_df)
    brave = []

    for slot in slots:
        if slot not in results:
            continue
        actual_team = results[slot].strip().lower()
        if slot not in predictions_df.columns:
            continue

        # Count how many picked the actual winner for this slot
        picked = predictions_df[slot].str.strip().str.lower()
        count_correct = (picked == actual_team).sum()
        pct = count_correct / total if total > 0 else 1

        # "Brave" = fewer than 25% picked it, and it turned out correct
        if pct < 0.25:
            correct_pickers = predictions_df[picked == actual_team]['Name'].tolist()
            for name in correct_pickers:
                brave.append((name, slot, results[slot].strip(), round(pct * 100)))

    return brave


def generate_blog_post(scored_df, predictions_df, results, config, games_scored, chart_path=None):
    """Generate a blog post announcing group stage results."""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
    contest_name = config['contest_name']
    contest_slug = config['contest_slug']

    bg_images = config.get('background_images', {}).get('blog_posts', ['/img/bg-post.jpg'])
    bg = random.choice(bg_images) if bg_images else '/img/bg-post.jpg'

    # Find the leader(s)
    top_score = scored_df['Score'].max()
    # Exclude AI participants from the headline leader
    human_leaders = scored_df[(scored_df['Score'] == top_score) & (scored_df['AI'].astype(str).str.strip() != '1')]['Name'].tolist()
    all_leaders = scored_df[scored_df['Score'] == top_score]['Name'].tolist()
    headline_leaders = human_leaders if human_leaders else all_leaders

    if len(headline_leaders) == 1:
        leader_str = headline_leaders[0]
        title = f"{leader_str} wins the {contest_name} Group Stage!"
    else:
        leader_str = ' & '.join(headline_leaders)
        title = f"{leader_str} share the lead after the {contest_name} Group Stage!"

    # Top of leaderboard for blog summary: take up to 5 rows, then extend to
    # include everyone who shares the score of the last row shown (no partial ties).
    top5 = scored_df.head(5)
    cutoff_score = top5.iloc[-1]['Score']
    top_df = scored_df[scored_df['Score'] >= cutoff_score]
    top5_lines = []
    for _, row in top_df.iterrows():
        ai_note = ' (AI)' if str(row.get('AI', '0')).strip() == '1' else ''
        top5_lines.append(f"- **{row['Rank']}. {row['Name']}**{ai_note} — {int(row['Score'])} pts")
    top5_md = '\n'.join(top5_lines)

    slots = [f'{g}{n}' for g in ['A', 'B', 'C', 'D'] for n in [1, 2]]
    results_lines = [f'- **Group {slot[0]} {"Winner" if slot[1]=="1" else "Runner-up"}**: {results[slot]}' for slot in slots if slot in results]
    results_md = '\n'.join(results_lines)

    # Brave predictions callout
    brave = find_brave_predictions(predictions_df, results)

    # Find ZIM pickers specifically for special callout
    zim_pickers = []
    if any(results.get(slot, '').strip().lower() == 'zimbabwe' for slot in ['B1', 'B2']):
        for slot in ['B1', 'B2']:
            picked = predictions_df[slot].str.strip().str.lower()
            zim_pickers += predictions_df[picked == 'zimbabwe']['Name'].tolist()

    brave_section = ''
    if brave:
        brave_lines = []
        for name, slot, team, pct in brave:
            group_label = f"Group {slot[0]} {'winner' if slot[1] == '1' else 'runner-up'}"
            brave_lines.append(f"- **{name}** correctly called **{team}** as {group_label} (only {pct}% of participants picked this!)")

        zim_section = ''
        if zim_pickers:
            names = ', '.join(f'**{n}**' for n in zim_pickers)
            zim_section = f"""
### 🦁 Special Mention: The Zimbabwe Believers

Zimbabwe making the Super 8 was arguably the hardest pick of the entire group stage. Only {names} had the courage to pick them — hats off!
"""

        brave_section = f"""
{zim_section}
### Brave Predictions 🎯

A shout-out to those who dared to predict the upsets:

{''.join(chr(10) + line for line in brave_lines)}"""

    chart_section = ''
    if chart_path:
        chart_section = """
### Score Distribution

![Score Distribution](/prediction-contests/img/cricket/t20-2026-score-distribution.png)
"""

    filename = f'{date_str}-t20-2026-group-stage-results.md'
    total_games = config.get('total_group_stage_games', games_scored)

    md = f"""---
layout: post
title: "{title}"
subtitle: "Group Stage complete — {total_games} matches played"
date: {datetime_str}
background: '{bg}'
---

The group stage of the {contest_name} is complete after {total_games} thrilling matches!

### Top of the Leaderboard

{top5_md}
{brave_section}{chart_section}
### Group Stage Results

{results_md}

[See the full leaderboard]({{{{ site.baseurl }}}}/{contest_slug}/leaderboard)
"""
    return md, filename


def get_group_columns(predictions_df):
    """Return list of group column names (columns starting with grp_)."""
    return [col for col in predictions_df.columns if col.startswith('grp_')]


def get_group_name(col):
    """Strip grp_ prefix to get display name."""
    return col[4:]  # removes 'grp_'


def format_group_filename(group_name):
    """Convert group name to filename."""
    if len(group_name) <= 3 and group_name.isupper():
        return f'{group_name}.md'
    return f'{group_name.title()}.md'


def main():
    generate_blog = '--generate-blog' in sys.argv
    config_file = 'contest_config.json'
    for i, arg in enumerate(sys.argv):
        if arg == '--config' and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config(config_file)

    # Load data
    predictions_path = os.path.join(script_dir, config['predictions_file'])
    results_path = os.path.join(script_dir, config['results_file'])

    print(f"Loading predictions from: {predictions_path}")
    print(f"Loading results from: {results_path}")

    predictions_df = load_predictions(predictions_path)
    results = load_results(results_path)

    print(f"\nResults loaded: {results}")
    print(f"Participants: {len(predictions_df)}")

    games_scored = len(results)

    # Score each participant
    scored_rows = []
    slots = [f'{g}{n}' for g in ['A', 'B', 'C', 'D'] for n in [1, 2]]

    for _, row in predictions_df.iterrows():
        total, breakdown = score_participant(row, results)
        entry = {
            'Name': row['Name'],
            'Location': row.get('Location', ''),
            'AI': row.get('AI', 0),
            'Score': total,
        }
        entry.update(breakdown)

        # Preserve group membership columns
        for col in predictions_df.columns:
            if col.startswith('grp_'):
                entry[col] = row.get(col, '')

        scored_rows.append(entry)

    scored_df = pd.DataFrame(scored_rows)
    scored_df = scored_df.sort_values('Score', ascending=False).reset_index(drop=True)
    scored_df['Rank'] = assign_ranks(scored_df)

    # Reorder columns: Rank, Name, Location, AI, Score, slots, grp_*
    pick_cols = [f'{s}_pick' for s in slots]
    grp_cols = [c for c in scored_df.columns if c.startswith('grp_')]
    col_order = ['Rank', 'Name', 'Location', 'AI', 'Score'] + slots + pick_cols + grp_cols
    scored_df = scored_df[col_order]

    print(f"\nTop 5:")
    for _, row in scored_df.head(5).iterrows():
        print(f"  {row['Rank']}. {row['Name']} — {int(row['Score'])} pts")

    # Write overall leaderboard
    leaderboard_path = os.path.join(script_dir, config['leaderboard_file'])
    os.makedirs(os.path.dirname(leaderboard_path), exist_ok=True)
    with open(leaderboard_path, 'w') as f:
        f.write(generate_overall_leaderboard_markdown(scored_df, config))
    print(f"\nOverall leaderboard written to: {leaderboard_path}")

    # Write group stage detailed leaderboard
    group_stage_path = leaderboard_path.replace('leaderboard.md', 'group-stage.md')
    with open(group_stage_path, 'w') as f:
        f.write(generate_group_stage_markdown(scored_df, results, config, games_scored))
    print(f"Group stage leaderboard written to: {group_stage_path}")

    # Write Super 8 placeholder
    super8_path = leaderboard_path.replace('leaderboard.md', 'super-8.md')
    if not os.path.exists(super8_path):
        contest_name = config['contest_name']
        contest_slug = config['contest_slug']
        bg = config.get('background_images', {}).get('leaderboard', '/img/bg-post.jpg')
        with open(super8_path, 'w') as f:
            f.write(f"""---
layout: page
title: Super 8 Leaderboard
description: {contest_name} - Super 8 Results
background: '{bg}'
permalink: "/{contest_slug}/super-8"
---

## Super 8 Leaderboard

*Coming soon — Super 8 round not yet complete.*

[Overall Leaderboard]({{{{ site.baseurl }}}}/{contest_slug}/leaderboard) | [Group Stage]({{{{ site.baseurl }}}}/{contest_slug}/group-stage)
""")
        print(f"Super 8 placeholder written to: {super8_path}")
    else:
        print(f"Super 8 page already exists, skipping: {super8_path}")

    # Write KO & Finals placeholder
    ko_path = leaderboard_path.replace('leaderboard.md', 'ko-finals.md')
    if not os.path.exists(ko_path):
        contest_name = config['contest_name']
        contest_slug = config['contest_slug']
        bg = config.get('background_images', {}).get('leaderboard', '/img/bg-post.jpg')
        with open(ko_path, 'w') as f:
            f.write(f"""---
layout: page
title: KO & Finals Leaderboard
description: {contest_name} - Knockout & Finals Results
background: '{bg}'
permalink: "/{contest_slug}/ko-finals"
---

## KO & Finals Leaderboard

*Coming soon — Knockout stage not yet complete.*

[Overall Leaderboard]({{{{ site.baseurl }}}}/{contest_slug}/leaderboard) | [Group Stage]({{{{ site.baseurl }}}}/{contest_slug}/group-stage)
""")
        print(f"KO & Finals placeholder written to: {ko_path}")
    else:
        print(f"KO & Finals page already exists, skipping: {ko_path}")

    # Write group leaderboards
    if 'groups_dir' in config:
        groups_dir = os.path.join(script_dir, config['groups_dir'])
        os.makedirs(groups_dir, exist_ok=True)

        group_cols = get_group_columns(predictions_df)
        for col in group_cols:
            group_name = get_group_name(col)
            # Filter to members (value == 1, 1.0, or '1')
            mask = scored_df[col].notna() & (pd.to_numeric(scored_df[col], errors='coerce') == 1)
            group_df = scored_df[mask].copy()

            if group_df.empty:
                print(f"  No members found for group: {group_name}")
                continue

            # Re-rank within group
            group_df = group_df.sort_values('Score', ascending=False).reset_index(drop=True)
            group_df['Rank'] = assign_ranks(group_df)

            group_md = generate_group_leaderboard_markdown(group_df, group_name, results, config)
            filename = format_group_filename(group_name)
            group_path = os.path.join(groups_dir, filename)
            with open(group_path, 'w') as f:
                f.write(group_md)
            print(f"  Group leaderboard written: {group_path} ({len(group_df)} members)")

    # Write blog post
    if generate_blog:
        chart_output_dir = os.path.join(script_dir, '../../img/cricket')
        chart_path = generate_score_chart(scored_df, chart_output_dir)
        print(f"\nScore chart written to: {chart_path}")
        blog_md, filename = generate_blog_post(scored_df, predictions_df, results, config, games_scored, chart_path=chart_path)
        blog_dir = os.path.join(script_dir, config['blog_post_dir'])
        os.makedirs(blog_dir, exist_ok=True)
        blog_path = os.path.join(blog_dir, filename)
        with open(blog_path, 'w') as f:
            f.write(blog_md)
        print(f"\nBlog post written to: {blog_path}")

    print("\nDone!")


if __name__ == '__main__':
    main()
