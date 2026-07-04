import pandas as pd
from datetime import datetime
from collections import Counter

# Load data
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Separate humans and AI
human_df = df[df['AI'] == 0]
ai_df = df[df['AI'] == 1]

# Gather statistics
num_total = len(df)
num_humans = len(human_df)
num_ai = len(ai_df)

# Team popularity analysis
def get_team_counts(df, group_cols):
    """Count how many times each team was picked in specific positions"""
    all_teams = []
    for col in group_cols:
        all_teams.extend(df[col].tolist())
    return Counter(all_teams)

# Group stage picks
group_a_teams = get_team_counts(human_df, ['A1', 'A2'])
group_b_teams = get_team_counts(human_df, ['B1', 'B2'])
group_c_teams = get_team_counts(human_df, ['C1', 'C2'])
group_d_teams = get_team_counts(human_df, ['D1', 'D2'])

# First place picks
a1_picks = Counter(human_df['A1'])
b1_picks = Counter(human_df['B1'])
c1_picks = Counter(human_df['C1'])
d1_picks = Counter(human_df['D1'])

# AI Similarity stats
perfect_score = human_df[human_df['AI_Similarity'] == 1.0]
num_perfect = len(perfect_score)
avg_similarity = human_df['AI_Similarity'].mean()
median_similarity = human_df['AI_Similarity'].median()

# Most and least similar
most_similar = human_df.nlargest(5, 'AI_Similarity')[['Name', 'Location', 'AI_Similarity']]
least_similar = human_df.nsmallest(5, 'AI_Similarity')[['Name', 'Location', 'AI_Similarity']]

# Location analysis
locations = human_df['Location'].dropna()
location_words = []
for loc in locations:
    # Extract country/state
    if ',' in str(loc):
        parts = str(loc).split(',')
        location_words.append(parts[-1].strip())
    else:
        location_words.append(str(loc).strip())

location_counts = Counter(location_words)
top_locations = location_counts.most_common(5)

# Generate blog post
today = datetime.now().strftime('%Y-%m-%d')
blog_title = "Humans vs AI: The T20 World Cup 2026 Prediction Battle Begins!"

blog_content = f"""---
layout: post
title: "{blog_title}"
subtitle: "53 Predictors Enter the Arena: Who Will Reign Supreme?"
date: {today} 10:00:00
background: '/img/bg-post.jpg'
---

The T20 World Cup 2026 prediction contest is officially underway, and we've got an exciting lineup of participants—including some unexpected competitors!

## The Lineup

We have **{num_total} total entries** in this tournament:
- **{num_humans} human predictors** ready to prove their cricket expertise
- **{num_ai} AI models** ({', '.join(ai_df['Name'].tolist())}) joining the fun

That's right—we're pitting human intuition against artificial intelligence!

## Geographic Diversity

Our predictors hail from around the globe, with the top locations being:
{chr(10).join([f"- **{loc}**: {count} participants" for loc, count in top_locations[:5]])}

## The AI-Canonical Predictions

Three AI models (Claude, ChatGPT, and Perplexity) made **identical predictions**:
- **Group A**: India, Pakistan
- **Group B**: Australia, Sri Lanka
- **Group C**: England, West Indies
- **Group D**: South Africa, New Zealand

Interestingly, Gemini had a different take—particularly on Group D, where it picked Afghanistan and South Africa instead.

## What Are Humans Predicting?

Let's look at the most popular picks for group winners:

### Group A - The Favorites
{chr(10).join([f"- **{team}**: {count}/{num_humans} predictions ({count/num_humans*100:.1f}%)" for team, count in a1_picks.most_common(3)])}

### Group B - Down Under Dominance?
{chr(10).join([f"- **{team}**: {count}/{num_humans} predictions ({count/num_humans*100:.1f}%)" for team, count in b1_picks.most_common(3)])}

### Group C - The British Isles Battle
{chr(10).join([f"- **{team}**: {count}/{num_humans} predictions ({count/num_humans*100:.1f}%)" for team, count in c1_picks.most_common(3)])}

### Group D - The Most Divided
{chr(10).join([f"- **{team}**: {count}/{num_humans} predictions ({count/num_humans*100:.1f}%)" for team, count in d1_picks.most_common(3)])}

## Consensus vs Contrarians

We calculated each human's "AI Similarity Score"—how closely their predictions match the AI-canonical picks.

**The Conformists**: {num_perfect} participants achieved a **perfect 1.000 similarity score**, making identical predictions to the AI consensus:
{chr(10).join([f"- {row['Name']} ({row['Location']})" for _, row in perfect_score.head(10).iterrows()])}

**The Average Human**: {avg_similarity:.3f} (or {avg_similarity*100:.1f}% aligned with AI)

**The Contrarians**: Our most divergent thinkers who dare to defy the AI overlords:
{chr(10).join([f"- **{row['Name']}** ({row['Location']}): {row['AI_Similarity']:.3f} similarity" for _, row in least_similar.iterrows()])}

Special shoutout to **{least_similar.iloc[0]['Name']}** for being the boldest contrarian with a {least_similar.iloc[0]['AI_Similarity']:.3f} similarity score!

## Surprise Picks

While most went with the favorites, some participants made bold choices:

**Group A Surprises**: {', '.join([team for team, count in group_a_teams.items() if team not in ['India', 'Pakistan'] and count > 0][:5])}

**Group B Dark Horses**: {', '.join([team for team, count in group_b_teams.items() if team not in ['Australia', 'Sri Lanka'] and count > 0][:5])}

**Group C Underdogs**: {', '.join([team for team, count in group_c_teams.items() if team not in ['England', 'West Indies'] and count > 0][:5])}

**Group D Wild Cards**: {', '.join([team for team, count in group_d_teams.items() if team not in ['South Africa', 'New Zealand'] and count > 0][:5])}

## The Question on Everyone's Mind

Will the wisdom of the crowd (and AI) prevail, or will the contrarians have the last laugh?

Will conforming to the AI consensus lead to victory, or is being different the key to winning?

Only time will tell! As the tournament progresses, we'll be tracking:
- Who's leading the leaderboard
- Whether AI similarity correlates with actual success
- Which dark horse picks pay off

## What's Next?

Predictions are still coming in, so these numbers may shift. Stay tuned for updates!

The tournament kicks off soon, and we'll be updating the leaderboard as matches unfold. May the best predictor—human or AI—win!

---

*Want to see the full predictions? Check out our [predictions page](/prediction-contests/active-contest/predictions.html).*

*Curious about the methodology? Visit our [rules page](/prediction-contests/active-contest/rules.html).*
"""

# Save blog post
output_file = f'/home/ram/projects/prediction-contests/_posts/{today}-t20-2026-predictions-analysis.md'
with open(output_file, 'w') as f:
    f.write(blog_content)

print(f"Blog post generated: {output_file}")
print(f"\nTitle: {blog_title}")
print(f"Date: {today}")
print(f"\nKey stats:")
print(f"- Total participants: {num_total}")
print(f"- Humans: {num_humans}")
print(f"- AI models: {num_ai}")
print(f"- Perfect AI matches: {num_perfect}")
print(f"- Average AI similarity: {avg_similarity:.3f}")
print(f"- Most contrarian: {least_similar.iloc[0]['Name']} ({least_similar.iloc[0]['AI_Similarity']:.3f})")
