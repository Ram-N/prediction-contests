import pandas as pd
import re

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

# Function to standardize locations
def standardize_location(loc):
    if pd.isna(loc) or loc.strip() == '':
        return ''

    # Remove extra spaces
    loc = ' '.join(loc.split())

    # State abbreviations mapping
    state_abbrev = {
        'California': 'CA',
        'Florida': 'FL',
        'Texas': 'TX',
        'Pennsylvania': 'PA',
        'Washington': 'WA',
        'New York': 'NY',
        'Massachusetts': 'MA',
        'Virginia': 'VA',
        'Colorado': 'CO',
        'Georgia': 'GA',
        'Maryland': 'MD',
        'Ohio': 'OH',
        'Illinois': 'IL'
    }

    for state, abbr in state_abbrev.items():
        loc = loc.replace(state, abbr)

    # Clean up slashes and replace with commas
    loc = loc.replace('/', ', ')

    # Replace common US variations
    loc = re.sub(r',?\s*USA\s*$', '', loc)
    loc = re.sub(r',?\s*United States\s*$', '', loc)
    loc = re.sub(r',?\s*U\.S\.A\.?\s*$', '', loc)
    loc = re.sub(r',?\s*US\s*$', '', loc)

    # Remove multiple commas and spaces
    loc = re.sub(r'\s*,\s*', ', ', loc)
    loc = re.sub(r',\s*,', ',', loc)
    loc = re.sub(r'\s+', ' ', loc)

    # Remove leading/trailing commas and spaces
    loc = loc.strip(', ')

    # If it's just a state abbreviation, make it more compact
    if loc in ['CA', 'FL', 'TX', 'PA', 'WA', 'NY', 'MA', 'VA', 'CO', 'GA', 'MD', 'OH', 'IL']:
        return loc

    # If location is just "India" or other country, keep it
    if loc in ['India', 'Chennai', 'Bangalore', 'Bengaluru', 'Mumbai', 'Malaysia', 'Dubai']:
        return loc

    # For "City, State" format, ensure no extra whitespace
    parts = [p.strip() for p in loc.split(',')]
    parts = [p for p in parts if p]  # Remove empty parts

    if len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts)

    return loc

# Standardize locations
df['Location'] = df['Location'].apply(standardize_location)

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

# Start building the markdown content with sortable table script
md_content = """---
layout: page
title: "Predictions - T20 2026"
description: "All submitted predictions"
background: '/img/bg_t20.webp'
permalink: "/t20-2026/predictions"
---

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap4.min.css">
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap4.min.js"></script>

<style>
  .table td, .table th {
    white-space: nowrap;
    padding: 0.5rem;
  }
  .table {
    font-size: 0.9rem;
  }
  table.dataTable thead .sorting:before,
  table.dataTable thead .sorting_asc:before,
  table.dataTable thead .sorting_desc:before {
    right: 0.5em;
    content: "↑";
    opacity: 0.3;
  }
  table.dataTable thead .sorting:after,
  table.dataTable thead .sorting_asc:after,
  table.dataTable thead .sorting_desc:after {
    right: 0.1em;
    content: "↓";
    opacity: 0.3;
  }
  table.dataTable thead .sorting_asc:before {
    opacity: 1;
  }
  table.dataTable thead .sorting_desc:after {
    opacity: 1;
  }
</style>

# T20 World Cup 2026 - Group Stage Predictions

<table id="predictionsTable" class="table table-striped table-bordered table-sm table-hover">
  <thead class="thead-dark">
    <tr>
      <th>Name</th>
      <th>Location</th>
      <th>A1</th>
      <th>A2</th>
      <th>B1</th>
      <th>B2</th>
      <th>C1</th>
      <th>C2</th>
      <th>D1</th>
      <th>D2</th>
      <th>AI Sim</th>
      <th>AI</th>
    </tr>
  </thead>
  <tbody>
"""

# Generate table rows
for idx, row in df.iterrows():
    name = row['Name']
    location = row['Location'] if row['Location'] else ''

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

    md_content += f"""    <tr>
      <td>{name}</td>
      <td>{location}</td>
      <td>{a1}</td>
      <td>{a2}</td>
      <td>{b1}</td>
      <td>{b2}</td>
      <td>{c1}</td>
      <td>{c2}</td>
      <td>{d1}</td>
      <td>{d2}</td>
      <td>{ai_sim}</td>
      <td>{ai_marker}</td>
    </tr>
"""

md_content += """  </tbody>
</table>

<script>
$(document).ready(function() {
    $('#predictionsTable').DataTable({
        "paging": false,
        "searching": true,
        "info": false,
        "order": [[10, "desc"]],  // Sort by AI Similarity column (index 10) descending by default
        "columnDefs": [
            { "type": "num", "targets": 10 }  // Treat AI Sim column as numeric
        ]
    });
});
</script>

"""

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
print(f"\nUpdates:")
print(f"  - Locations standardized (City, ST format)")
print(f"  - Bootstrap sortable table added")
print(f"  - Compact styling to prevent line wraps")
