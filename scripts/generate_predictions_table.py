import pandas as pd

# Load data
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Sort by AI_Similarity descending (most similar first)
df_sorted = df.sort_values('AI_Similarity', ascending=False)

# Count entries
num_total = len(df)
num_humans = len(df[df['AI'] == 0])
num_ai = len(df[df['AI'] == 1])

# Generate markdown table
table_lines = []

# Header
header = "| Name | Location | Group A | Group B | Group C | Group D | AI Similarity | AI |"
separator = "|:-----|:---------|:--------|:--------|:--------|:--------|:-------------:|:--:|"

table_lines.append(header)
table_lines.append(separator)

# Data rows
for _, row in df_sorted.iterrows():
    name = row['Name']
    location = row['Location'] if pd.notna(row['Location']) else ''
    group_a = f"{row['A1']}, {row['A2']}"
    group_b = f"{row['B1']}, {row['B2']}"
    group_c = f"{row['C1']}, {row['C2']}"
    group_d = f"{row['D1']}, {row['D2']}"
    ai_sim = f"{row['AI_Similarity']:.3f}"
    is_ai = "✓" if row['AI'] == 1 else ""

    line = f"| {name} | {location} | {group_a} | {group_b} | {group_c} | {group_d} | {ai_sim} | {is_ai} |"
    table_lines.append(line)

# Create the full markdown content
markdown_content = f"""---
layout: page
title: "Predictions - T20 2026"
description: "All submitted predictions"
background: '/img/bg_t20.webp'
permalink: "/t20-2026/predictions"
---

# T20 World Cup 2026 - Group Stage Predictions

All submitted predictions are shown below. The deadline for group stage predictions has passed.

**Total Entries:** {num_total} participants ({num_humans} humans + {num_ai} AI models)

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
{chr(10).join(table_lines)}

---

## Notable Statistics

- **Perfect AI matches:** {len(df[df['AI_Similarity'] == 1.0])} participants
- **Average AI similarity (humans):** {df[df['AI'] == 0]['AI_Similarity'].mean():.3f}
- **Most contrarian:** {df_sorted.iloc[-1]['Name']} ({df_sorted.iloc[-1]['AI_Similarity']:.3f})
- **Most popular Group A picks:** India & Pakistan
- **Most popular Group B picks:** Australia & Sri Lanka
- **Most popular Group C picks:** England & West Indies
- **Most popular Group D picks:** South Africa & New Zealand

---

*Predictions will be scored as the tournament progresses. Check the [leaderboard](/prediction-contests/t20-2026/leaderboard) for live standings!*
"""

# Save the file
output_file = '/home/ram/projects/prediction-contests/active-contest/predictions.md'
with open(output_file, 'w') as f:
    f.write(markdown_content)

print(f"Updated predictions.md")
print(f"\nStats:")
print(f"- Total participants: {num_total}")
print(f"- Humans: {num_humans}")
print(f"- AI models: {num_ai}")
print(f"- Table rows generated: {len(df_sorted)}")
print(f"\nSaved to: {output_file}")
