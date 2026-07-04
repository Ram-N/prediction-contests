import pandas as pd
from datetime import datetime

# Read the clean predictions
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Sort by AI_Similarity descending, then by Name
df = df.sort_values(['AI_Similarity', 'Name'], ascending=[False, True])

# Start building the markdown content
md_content = """---
layout: page
title: "Predictions - T20 2026"
description: "All submitted predictions"
background: '/img/bg_t20.webp'
permalink: "/t20-2026/predictions"
---

# T20 World Cup 2026 - Group Stage Predictions

All submitted predictions are shown below. The deadline for group stage predictions has passed.

**Total Entries:** {} participants ({} humans + {} AI models)

## About the Predictions

Each participant predicted the top 2 teams from each of the 4 groups (A, B, C, D).

**Scoring:**
- **4 points** if both teams qualify AND positions are correct
- **2 points** if both teams qualify but positions are swapped
- **1 point** if only one team qualifies
- **0 points** otherwise

**AI Similarity Score:** How closely each prediction matches the AI-canonical predictions (Claude/ChatGPT/Perplexity consensus). A score of 1.000 means identical to AI consensus, while lower scores indicate more divergent thinking.

---

## All Predictions

{{:.thead-dark .table-striped .table-bordered .table-sm }}
| Name | Location | Group A | Group B | Group C | Group D | AI Similarity | AI |
|:-----|:---------|:--------|:--------|:--------|:--------|:-------------:|:--:|
""".format(
    len(df),
    len(df[df['AI'] == 0]),
    len(df[df['AI'] == 1])
)

# Generate table rows
for idx, row in df.iterrows():
    name = row['Name']
    location = row['Location'] if pd.notna(row['Location']) else ''

    group_a = f"{row['A1']}, {row['A2']}"
    group_b = f"{row['B1']}, {row['B2']}"
    group_c = f"{row['C1']}, {row['C2']}"
    group_d = f"{row['D1']}, {row['D2']}"

    ai_sim = f"{row['AI_Similarity']:.3f}"
    ai_marker = "✓" if row['AI'] == 1 else ""

    md_content += f"| {name} | {location} | {group_a} | {group_b} | {group_c} | {group_d} | {ai_sim} | {ai_marker} |\n"

# Calculate statistics
human_df = df[df['AI'] == 0]
ai_df = df[df['AI'] == 1]

perfect_matches = len(df[df['AI_Similarity'] == 1.0])
perfect_human_matches = len(human_df[human_df['AI_Similarity'] == 1.0])

# Find most contrarian (lowest similarity, excluding AI models)
most_contrarian = human_df.nsmallest(1, 'AI_Similarity').iloc[0]
most_contrarian_name = most_contrarian['Name']
most_contrarian_score = most_contrarian['AI_Similarity']

# Find most popular picks for each group
def get_top_picks(df, col1, col2):
    teams = pd.concat([df[col1], df[col2]])
    top_teams = teams.value_counts().head(2)
    return ' & '.join(top_teams.index.tolist())

group_a_popular = get_top_picks(df, 'A1', 'A2')
group_b_popular = get_top_picks(df, 'B1', 'B2')
group_c_popular = get_top_picks(df, 'C1', 'C2')
group_d_popular = get_top_picks(df, 'D1', 'D2')

# Add statistics section
md_content += f"""
---

## Notable Statistics

- **Perfect AI matches:** {perfect_human_matches} humans (plus 3 AI models)
- **Total participants:** {len(df)} ({len(human_df)} humans + {len(ai_df)} AI models)
- **Average AI similarity (all):** {df['AI_Similarity'].mean():.3f}
- **Average AI similarity (humans):** {human_df['AI_Similarity'].mean():.3f}
- **Most contrarian:** {most_contrarian_name} ({most_contrarian_score:.3f})
- **Most popular Group A picks:** {group_a_popular}
- **Most popular Group B picks:** {group_b_popular}
- **Most popular Group C picks:** {group_c_popular}
- **Most popular Group D picks:** {group_d_popular}

### Key Observations

**AI Consensus:**
- Claude (Sonnet 4.5), ChatGPT, and Perplexity all made identical predictions
- Gemini (Thinking Mode) diverged with a similarity score of {ai_df[ai_df['Name'] == 'Gemini (Thinking Mode)']['AI_Similarity'].values[0]:.3f}
- The AI-canonical predictions: India & Pakistan (A), Australia & Sri Lanka (B), England & West Indies (C), South Africa & New Zealand (D)

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
print(f"  Total: {len(df)} ({len(human_df)} humans + {len(ai_df)} AI)")
print(f"  Perfect matches: {perfect_human_matches} humans")
print(f"  Most contrarian: {most_contrarian_name} ({most_contrarian_score:.3f})")
