import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Change to script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv('../T20-2026-Predictions-Clean.csv')

# Define teams for context
teams_per_group = {
    'A': ['India', 'Pakistan', 'USA', 'Namibia', 'Netherlands'],
    'B': ['Australia', 'Sri Lanka', 'Zimbabwe', 'Ireland', 'Oman'],
    'C': ['West Indies', 'England', 'Italy', 'Scotland', 'Nepal'],
    'D': ['South Africa', 'Afghanistan', 'New Zealand', 'Canada', 'UAE']
}

# Separate humans and AI
human_df = df[df['AI'] == 0].copy()
ai_df = df[df['AI'] == 1].copy()

print(f"Total entries: {len(df)}")
print(f"Human entries: {len(human_df)}")
print(f"AI entries: {len(ai_df)}")

# Create img directory if it doesn't exist
img_dir = '../../img'
os.makedirs(img_dir, exist_ok=True)

# ---------------------------------------------------------
# 2. VISUALIZATIONS
# ---------------------------------------------------------

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

# A. The AI Similarity Distribution
print("\nGenerating AI Similarity chart...")
fig, ax = plt.subplots(figsize=(10, 6))
bins = np.arange(0, 1.1, 0.0625) - 0.03125  # Center bins on actual values
sns.histplot(human_df['AI_Similarity'], bins=bins, kde=False, color='skyblue', edgecolor='black')
plt.title('How "AI-Like" Are Human Predictions?', fontsize=16, fontweight='bold')
plt.xlabel('Similarity to AI Consensus (0.0 = completely different, 1.0 = identical)', fontsize=12)
plt.ylabel('Number of Participants', fontsize=12)
avg_sim = human_df['AI_Similarity'].mean()
plt.axvline(avg_sim, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_sim:.3f}')
plt.legend(fontsize=11)
plt.tight_layout()
output_path = os.path.join(img_dir, 't20-2026-ai-similarity.png')
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_path}")
plt.close()

# B. Group D Consensus Heatmap (most divided group)
print("Generating Group D heatmap...")
def plot_group_heatmap(group_name):
    teams = teams_per_group[group_name]
    # Create empty matrix
    matrix = pd.DataFrame(0, index=teams, columns=['1st Place Picks', '2nd Place Picks'])

    # Fill matrix
    for _, row in human_df.iterrows():
        t1 = row[f'{group_name}1']
        t2 = row[f'{group_name}2']
        if t1 in teams:
            matrix.loc[t1, '1st Place Picks'] += 1
        if t2 in teams:
            matrix.loc[t2, '2nd Place Picks'] += 1

    # Sort by total picks
    matrix['Total'] = matrix.sum(axis=1)
    matrix = matrix.sort_values('Total', ascending=False).drop('Total', axis=1)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='YlGnBu', cbar_kws={'label': 'Number of Picks'})
    plt.title(f'Group {group_name}: Who Will Qualify?', fontsize=16, fontweight='bold')
    plt.ylabel('Team', fontsize=12)
    plt.xlabel('', fontsize=12)
    plt.tight_layout()
    output_path = os.path.join(img_dir, f't20-2026-group-{group_name}-heatmap.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()

plot_group_heatmap('D')

# C. The "Consensus vs Chaos" Chart
print("Generating prediction diversity chart...")
unique_counts = {}
for group in ['A', 'B', 'C', 'D']:
    cols = [f'{group}1', f'{group}2']
    # Create a tuple of the prediction to count uniques
    combos = human_df[cols].apply(lambda x: tuple(sorted([x.iloc[0], x.iloc[1]])), axis=1)
    unique_counts[f'Group {group}'] = combos.nunique()

fig, ax = plt.subplots(figsize=(10, 6))
bars = plt.bar(unique_counts.keys(), unique_counts.values(),
               color=['#ff9999','#66b3ff','#99ff99','#ffcc99'], edgecolor='black', linewidth=1.5)
plt.title('Prediction Diversity: How Many Different Outcomes Per Group?', fontsize=16, fontweight='bold')
plt.xlabel('Group', fontsize=12)
plt.ylabel('Unique Prediction Combinations', fontsize=12)
plt.ylim(0, max(unique_counts.values()) + 2)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(img_dir, 't20-2026-prediction-diversity.png')
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_path}")
plt.close()

# ---------------------------------------------------------
# 4. INTERESTING STATISTICS
# ---------------------------------------------------------

print("\n" + "="*60)
print("INTERESTING STATISTICS FOR BLOG POST")
print("="*60)

# Total counts
print(f"\nTotal Participants: {len(df)}")
print(f"  - Humans: {len(human_df)}")
print(f"  - AI Models: {len(ai_df)}")

# AI Similarity stats
print(f"\nAI Similarity Scores:")
print(f"  - Average (all): {df['AI_Similarity'].mean():.3f}")
print(f"  - Average (humans only): {human_df['AI_Similarity'].mean():.3f}")
print(f"  - Highest: {human_df['AI_Similarity'].max():.3f}")
print(f"  - Lowest: {human_df['AI_Similarity'].min():.3f}")

# Perfect matches
perfect_matches = human_df[human_df['AI_Similarity'] == 1.0]
print(f"\n  - Perfect AI matches (humans): {len(perfect_matches)}")
if len(perfect_matches) > 0:
    print("    Names:", ", ".join(perfect_matches['Name'].tolist()))

# Most contrarian
most_contrarian = human_df.nsmallest(5, 'AI_Similarity')[['Name', 'Location', 'AI_Similarity']]
print(f"\nMost Contrarian Predictors:")
for idx, row in most_contrarian.iterrows():
    loc = row['Location'] if pd.notna(row['Location']) else 'Unknown'
    print(f"  - {row['Name']} ({loc}): {row['AI_Similarity']:.3f}")

# Popular picks by group
print("\nMost Popular Predictions:")
for group in ['A', 'B', 'C', 'D']:
    print(f"\n  Group {group}:")
    for pos in ['1', '2']:
        col = f'{group}{pos}'
        top_picks = human_df[col].value_counts().head(3)
        position_name = "1st" if pos == '1' else "2nd"
        print(f"    {position_name} Place:")
        for team, count in top_picks.items():
            pct = (count / len(human_df)) * 100
            print(f"      - {team}: {count} picks ({pct:.1f}%)")

# Unique picks
print("\nUnique/Rare Picks (only 1 person picked this team):")
for group in ['A', 'B', 'C', 'D']:
    for pos in ['1', '2']:
        col = f'{group}{pos}'
        counts = human_df[col].value_counts()
        singles = counts[counts == 1]
        if len(singles) > 0:
            position_name = "1st" if pos == '1' else "2nd"
            print(f"  Group {group} - {position_name} Place:")
            for team in singles.index:
                person = human_df[human_df[col] == team]['Name'].iloc[0]
                print(f"    - {team} (only {person})")

# Prediction diversity
print(f"\nPrediction Diversity (unique combinations per group):")
for group in ['A', 'B', 'C', 'D']:
    print(f"  Group {group}: {unique_counts[f'Group {group}']} different outcomes predicted")

# Geographic diversity
print(f"\nTop Locations:")
location_counts = human_df['Location'].value_counts().head(10)
for loc, count in location_counts.items():
    if pd.notna(loc) and str(loc).strip():
        print(f"  - {loc}: {count} participant{'s' if count > 1 else ''}")

print("\n" + "="*60)
print("✓ All visualizations saved successfully!")
print("="*60)
