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

# Load data
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

# Create img directory
img_dir = '../../img'
os.makedirs(img_dir, exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

print("Generating updated visualizations...")

# 1. AI Similarity Distribution - MUCH SMALLER
fig, ax = plt.subplots(figsize=(6, 3.5))  # Reduced from (10, 6)
bins = np.arange(0, 1.1, 0.0625) - 0.03125
sns.histplot(human_df['AI_Similarity'], bins=bins, kde=False, color='skyblue', edgecolor='black')
plt.title('How "AI-Like" Are Human Predictions?', fontsize=12, fontweight='bold')
plt.xlabel('Similarity to AI Consensus', fontsize=10)
plt.ylabel('Number of Participants', fontsize=10)
avg_sim = human_df['AI_Similarity'].mean()
plt.axvline(avg_sim, color='red', linestyle='--', linewidth=2, label=f'Avg: {avg_sim:.3f}')
plt.legend(fontsize=9)
plt.tight_layout()
output_path = os.path.join(img_dir, 't20-2026-ai-similarity.png')
plt.savefig(output_path, dpi=120, bbox_inches='tight')
print(f"✓ Saved smaller AI similarity chart: {output_path}")
plt.close()

# 2. Group D Heatmap - TOP 3 TEAMS ONLY, 50% SIZE
teams = teams_per_group['D']
# Create empty matrix
matrix = pd.DataFrame(0, index=teams, columns=['1st Place Picks', '2nd Place Picks'])

# Fill matrix
for _, row in human_df.iterrows():
    t1 = row['D1']
    t2 = row['D2']
    if t1 in teams:
        matrix.loc[t1, '1st Place Picks'] += 1
    if t2 in teams:
        matrix.loc[t2, '2nd Place Picks'] += 1

# Sort by total picks and take top 3
matrix['Total'] = matrix.sum(axis=1)
matrix = matrix.sort_values('Total', ascending=False).head(3).drop('Total', axis=1)

# Smaller figure - 50% of original (8, 6)
fig, ax = plt.subplots(figsize=(4, 3))
sns.heatmap(matrix, annot=True, fmt='d', cmap='YlGnBu',
            cbar_kws={'label': 'Picks'}, annot_kws={'size': 10})
plt.title('Group D: Top 3 Teams', fontsize=12, fontweight='bold')
plt.ylabel('Team', fontsize=10)
plt.xlabel('', fontsize=10)
plt.xticks(fontsize=9)
plt.yticks(fontsize=9)
plt.tight_layout()
output_path = os.path.join(img_dir, 't20-2026-group-D-heatmap.png')
plt.savefig(output_path, dpi=120, bbox_inches='tight')
print(f"✓ Saved smaller Group D heatmap (top 3 only): {output_path}")
plt.close()

print("\n✓ All visualizations updated successfully!")
print("  - AI Similarity: Much smaller size")
print("  - Group D Heatmap: 50% size, top 3 teams only")
print("  - Prediction Diversity: (to be removed from blog)")
