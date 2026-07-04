import pandas as pd
from datetime import datetime

# Read the clean predictions
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Country code mapping
country_codes = {
    'India': 'IND',
    'Pakistan': 'PAK',
    'Australia': 'AUS',
    'Sri Lanka': 'SL',
    'England': 'ENG',
    'West Indies': 'WI',
    'South Africa': 'SA',
    'New Zealand': 'NZ',
    'Afghanistan': 'AFG',
    'Ireland': 'IRE',
    'Scotland': 'SCO',
    'USA': 'USA',
    'Netherlands': 'NED',
    'Zimbabwe': 'ZIM',
    'Nepal': 'NEP',
    'Namibia': 'NAM'
}

# Convert team names to codes
for col in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']:
    df[col] = df[col].map(country_codes)

# Separate humans and AI
human_df = df[df['AI'] == 0].copy()
ai_df = df[df['AI'] == 1].copy()

# Sort humans by AI_Similarity descending, then by Name
human_df = human_df.sort_values(['AI_Similarity', 'Name'], ascending=[False, True])

# Sort AI by Name
ai_df = ai_df.sort_values('Name')

# Combine: humans first, then AI
df = pd.concat([human_df, ai_df], ignore_index=True)

# Start building the markdown content
md_content = """---
layout: page
title: "Predictions - T20 2026"
description: "All submitted predictions"
background: '/img/bg_t20.webp'
permalink: "/t20-2026/predictions"
---

# T20 World Cup 2026 - Group Stage Predictions

{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Location | A1 | A2 | B1 | B2 | C1 | C2 | D1 | D2 | AI Similarity | AI |
|:-----|:---------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:-------------:|:--:|
"""

# Generate table rows
for idx, row in df.iterrows():
    name = row['Name']
    location = row['Location'] if pd.notna(row['Location']) else ''

    a1 = row['A1']
    a2 = row['A2']
    b1 = row['B1']
    b2 = row['B2']
    c1 = row['C1']
    c2 = row['C2']
    d1 = row['D1']
    d2 = row['D2']

    ai_sim = f"{row['AI_Similarity']:.3f}"
    ai_marker = "✓" if row['AI'] == 1 else ""

    md_content += f"| {name} | {location} | {a1} | {a2} | {b1} | {b2} | {c1} | {c2} | {d1} | {d2} | {ai_sim} | {ai_marker} |\n"

# Calculate statistics
human_df_stats = df[df['AI'] == 0]
ai_df_stats = df[df['AI'] == 1]

perfect_human_matches = len(human_df_stats[human_df_stats['AI_Similarity'] == 1.0])

# Find most contrarian (lowest similarity, excluding AI models)
most_contrarian = human_df_stats.nsmallest(1, 'AI_Similarity').iloc[0]
most_contrarian_name = most_contrarian['Name']
most_contrarian_score = most_contrarian['AI_Similarity']

# Find most popular picks for each group
def get_top_picks(df_data, col1, col2):
    teams = pd.concat([df_data[col1], df_data[col2]])
    top_teams = teams.value_counts().head(2)
    return ' & '.join(top_teams.index.tolist())

group_a_popular = get_top_picks(df, 'A1', 'A2')
group_b_popular = get_top_picks(df, 'B1', 'B2')
group_c_popular = get_top_picks(df, 'C1', 'C2')
group_d_popular = get_top_picks(df, 'D1', 'D2')

# Add descriptive text at the bottom
md_content += f"""
---

## About the Predictions

All submitted predictions are shown above. The deadline for group stage predictions has passed.

**Total Entries:** {len(df)} participants ({len(human_df_stats)} humans + {len(ai_df_stats)} AI models)

Each participant predicted the top 2 teams from each of the 4 groups (A, B, C, D).

**Scoring:**
- **4 points** if both teams qualify AND positions are correct
- **2 points** if both teams qualify but positions are swapped
- **1 point** if only one team qualifies
- **0 points** otherwise

**AI Similarity Score:** How closely each prediction matches the AI-canonical predictions (Claude/ChatGPT/Perplexity consensus). A score of 1.000 means identical to AI consensus, while lower scores indicate more divergent thinking.

---

## Notable Statistics

- **Perfect AI matches:** {perfect_human_matches} humans (plus 3 AI models)
- **Total participants:** {len(df)} ({len(human_df_stats)} humans + {len(ai_df_stats)} AI models)
- **Average AI similarity (all):** {df['AI_Similarity'].mean():.3f}
- **Average AI similarity (humans):** {human_df_stats['AI_Similarity'].mean():.3f}
- **Most contrarian:** {most_contrarian_name} ({most_contrarian_score:.3f})
- **Most popular Group A picks:** {group_a_popular}
- **Most popular Group B picks:** {group_b_popular}
- **Most popular Group C picks:** {group_c_popular}
- **Most popular Group D picks:** {group_d_popular}

### Key Observations

**AI Consensus:**
- Claude (Sonnet 4.5), ChatGPT, and Perplexity all made identical predictions
- Gemini (Thinking Mode) diverged with a similarity score of {ai_df_stats[ai_df_stats['Name'] == 'Gemini (Thinking Mode)']['AI_Similarity'].values[0]:.3f}
- The AI-canonical predictions: IND & PAK (A), AUS & SL (B), ENG & WI (C), SA & NZ (D)

**Human Patterns:**
- {perfect_human_matches} humans matched the AI consensus perfectly
- Average similarity score suggests strong consensus around conventional favorites
- Most divergent predictions came from participants who picked unexpected teams like Netherlands, Zimbabwe, USA, or Scotland

**Interesting Picks:**
- Several participants picked **USA** to qualify (a bold prediction!)
- **Ireland, Scotland, Nepal, Zimbabwe** received scattered support
- **Afghanistan** was the most popular dark horse pick

---

*Predictions will be scored as the tournament progresses. Check the [leaderboard](/prediction-contests/t20-2026/leaderboard) for live standings!*
"""

# Write to file
output_path = '/home/ram/projects/prediction-contests/active-contest/predictions.md'
with open(output_path, 'w') as f:
    f.write(md_content)

print(f"Generated predictions.md with {len(df)} entries")
print(f"Saved to: {output_path}")
print(f"\nStatistics:")
print(f"  Total: {len(df)} ({len(human_df_stats)} humans + {len(ai_df_stats)} AI)")
print(f"  Perfect matches: {perfect_human_matches} humans")
print(f"  Most contrarian: {most_contrarian_name} ({most_contrarian_score:.3f})")
print(f"\nLayout:")
print(f"  - Table at top")
print(f"  - Humans sorted by similarity (high to low)")
print(f"  - AI models at bottom")
print(f"  - Descriptive text moved to bottom")
