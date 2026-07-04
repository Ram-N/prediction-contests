import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Separate humans and AI
human_df = df[df['AI'] == 0]
ai_df = df[df['AI'] == 1]

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('AI Similarity Analysis - T20 World Cup 2026 Predictions',
             fontsize=16, fontweight='bold', y=0.995)

# 1. Distribution histogram
ax1 = axes[0, 0]
ax1.hist(human_df['AI_Similarity'], bins=15, alpha=0.7, color='steelblue', edgecolor='black')
ax1.axvline(human_df['AI_Similarity'].mean(), color='red', linestyle='--',
            linewidth=2, label=f'Mean: {human_df["AI_Similarity"].mean():.3f}')
ax1.axvline(human_df['AI_Similarity'].median(), color='orange', linestyle='--',
            linewidth=2, label=f'Median: {human_df["AI_Similarity"].median():.3f}')
ax1.set_xlabel('AI Similarity Score', fontweight='bold')
ax1.set_ylabel('Number of Participants', fontweight='bold')
ax1.set_title('Distribution of AI Similarity Scores (Humans)', fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 2. Box plot comparing humans vs AI
ax2 = axes[0, 1]
data_to_plot = [human_df['AI_Similarity'], ai_df['AI_Similarity']]
bp = ax2.boxplot(data_to_plot, labels=['Humans', 'AI Models'], patch_artist=True,
                 widths=0.6)
bp['boxes'][0].set_facecolor('steelblue')
bp['boxes'][1].set_facecolor('coral')
ax2.set_ylabel('AI Similarity Score', fontweight='bold')
ax2.set_title('Humans vs AI Models Similarity', fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# 3. Top/Bottom performers
ax3 = axes[1, 0]
top_10 = human_df.nlargest(10, 'AI_Similarity')[['Name', 'AI_Similarity']].sort_values('AI_Similarity')
bottom_10 = human_df.nsmallest(10, 'AI_Similarity')[['Name', 'AI_Similarity']].sort_values('AI_Similarity', ascending=False)

# Combine and color code
combined = pd.concat([
    bottom_10.assign(Category='Bottom 10'),
    top_10.assign(Category='Top 10')
])

y_positions = range(len(combined))
colors = ['#d62728' if cat == 'Bottom 10' else '#2ca02c' for cat in combined['Category']]

ax3.barh(y_positions, combined['AI_Similarity'], color=colors, alpha=0.7, edgecolor='black')
ax3.set_yticks(y_positions)
ax3.set_yticklabels(combined['Name'], fontsize=8)
ax3.set_xlabel('AI Similarity Score', fontweight='bold')
ax3.set_title('Top 10 vs Bottom 10 Performers', fontweight='bold')
ax3.axvline(human_df['AI_Similarity'].mean(), color='black', linestyle='--',
            linewidth=1, alpha=0.5, label='Mean')
ax3.legend()
ax3.grid(axis='x', alpha=0.3)

# 4. Cumulative distribution
ax4 = axes[1, 1]
sorted_sim = np.sort(human_df['AI_Similarity'])
cumulative = np.arange(1, len(sorted_sim) + 1) / len(sorted_sim) * 100

ax4.plot(sorted_sim, cumulative, linewidth=2, color='steelblue')
ax4.fill_between(sorted_sim, cumulative, alpha=0.3, color='steelblue')
ax4.set_xlabel('AI Similarity Score', fontweight='bold')
ax4.set_ylabel('Cumulative Percentage (%)', fontweight='bold')
ax4.set_title('Cumulative Distribution of AI Similarity', fontweight='bold')
ax4.grid(alpha=0.3)

# Add some key percentiles
percentiles = [25, 50, 75]
for p in percentiles:
    val = np.percentile(human_df['AI_Similarity'], p)
    ax4.axvline(val, color='red', linestyle=':', alpha=0.5)
    ax4.text(val, p, f' {p}th: {val:.2f}', fontsize=8, verticalalignment='center')

plt.tight_layout()

# Save figure
output_path = '/home/ram/projects/prediction-contests/data/AI-Similarity-Distribution.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved visualization to: {output_path}")

# Also create a simple scatter plot showing all participants
fig2, ax = plt.subplots(figsize=(12, 8))

# Sort by similarity for better visualization
sorted_df = df.sort_values('AI_Similarity', ascending=False).reset_index(drop=True)
human_mask = sorted_df['AI'] == 0
ai_mask = sorted_df['AI'] == 1

# Plot humans and AI separately
ax.scatter(sorted_df[human_mask].index, sorted_df[human_mask]['AI_Similarity'],
           s=100, alpha=0.6, color='steelblue', label='Humans', edgecolors='black', linewidth=0.5)
ax.scatter(sorted_df[ai_mask].index, sorted_df[ai_mask]['AI_Similarity'],
           s=150, alpha=0.8, color='coral', label='AI Models', marker='s', edgecolors='black', linewidth=0.5)

# Add horizontal line at mean
ax.axhline(human_df['AI_Similarity'].mean(), color='red', linestyle='--',
           linewidth=2, alpha=0.7, label=f'Human Mean: {human_df["AI_Similarity"].mean():.3f}')

# Annotate AI models
for idx, row in sorted_df[ai_mask].iterrows():
    ax.annotate(row['Name'],
                xy=(idx, row['AI_Similarity']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

ax.set_xlabel('Participant (sorted by similarity)', fontweight='bold', fontsize=12)
ax.set_ylabel('AI Similarity Score', fontweight='bold', fontsize=12)
ax.set_title('All Participants: Similarity to AI-Canonical Predictions',
             fontsize=14, fontweight='bold', pad=20)
ax.set_ylim(0.3, 1.05)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()

# Save scatter plot
scatter_path = '/home/ram/projects/prediction-contests/data/AI-Similarity-Scatter.png'
plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
print(f"Saved scatter plot to: {scatter_path}")

print("\nVisualization complete!")
