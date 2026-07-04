import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def score_group(pred1, pred2):
    """
    pred1, pred2: tuples like ('NZ', 'SA')
    returns score in {0, 1, 2, 4}
    """
    if pred1 == pred2:
        return 4

    set1, set2 = set(pred1), set(pred2)

    if set1 == set2:
        return 2

    if len(set1 & set2) == 1:
        return 1

    return 0

def model_similarity(model_a, model_b):
    """
    model_a, model_b: dicts {group: (first, second)}
    returns normalized similarity in [0, 1]
    """
    total_score = 0
    max_score = 4 * len(model_a)

    for group in model_a:
        total_score += score_group(model_a[group], model_b[group])

    return total_score / max_score

# Load the processed predictions
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv')

# Filter AI entries
ai_df = df[df['AI'] == 1].copy()

# Create a mapping for shortened names
name_mapping = {
    'ChatGPT': 'ChatGPT',
    'Claude (Sonnet 4.5)': 'Claude',
    'Gemini (Thinking Mode)': 'Gemini',
    'Perplexity': 'Perplexity'
}

# Extract predictions for each AI model
ai_predictions = {}
for _, row in ai_df.iterrows():
    original_name = row['Name']
    short_name = name_mapping.get(original_name, original_name)

    ai_predictions[short_name] = {
        'A': (row['A1'], row['A2']),
        'B': (row['B1'], row['B2']),
        'C': (row['C1'], row['C2']),
        'D': (row['D1'], row['D2'])
    }

# Print predictions for verification
print("AI Model Predictions:")
print("=" * 80)
for model_name, preds in ai_predictions.items():
    print(f"\n{model_name}:")
    for group, teams in preds.items():
        print(f"  Group {group}: {teams[0]}, {teams[1]}")

# Create similarity matrix
model_names = list(ai_predictions.keys())
n_models = len(model_names)
similarity_matrix = np.zeros((n_models, n_models))

for i, model_a in enumerate(model_names):
    for j, model_b in enumerate(model_names):
        if i == j:
            similarity_matrix[i, j] = np.nan  # Leave diagonal blank
        else:
            similarity_matrix[i, j] = model_similarity(
                ai_predictions[model_a],
                ai_predictions[model_b]
            )

# Create DataFrame
similarity_df = pd.DataFrame(
    similarity_matrix,
    index=model_names,
    columns=model_names
)

# Print the matrix
print("\n\nSimilarity Matrix:")
print("=" * 80)
print(similarity_df.to_string())

# Save as CSV
csv_path = '/home/ram/projects/prediction-contests/data/AI-Model-Similarity.csv'
similarity_df.to_csv(csv_path)
print(f"\n\nSaved similarity matrix to: {csv_path}")

# Create heatmap
plt.figure(figsize=(10, 8))
mask = np.eye(n_models, dtype=bool)  # Mask diagonal
sns.heatmap(
    similarity_df,
    annot=True,
    fmt='.3f',
    cmap='RdYlGn',
    vmin=0,
    vmax=1,
    mask=mask,
    square=True,
    cbar_kws={'label': 'Similarity Score'},
    linewidths=1,
    linecolor='gray'
)
plt.title('AI Model Prediction Similarity\nT20 World Cup 2026 Group Stage',
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Model', fontsize=12, fontweight='bold')
plt.ylabel('Model', fontsize=12, fontweight='bold')
plt.tight_layout()

# Save heatmap
heatmap_path = '/home/ram/projects/prediction-contests/data/AI-Model-Similarity-Heatmap.png'
plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
print(f"Saved heatmap to: {heatmap_path}")

plt.show()

# Additional analysis
print("\n\nAdditional Analysis:")
print("=" * 80)

# Fill NaN for calculations
sim_values = similarity_matrix[~np.isnan(similarity_matrix)]
print(f"Average pairwise similarity: {sim_values.mean():.3f}")
print(f"Std deviation: {sim_values.std():.3f}")
print(f"Min similarity: {sim_values.min():.3f}")
print(f"Max similarity: {sim_values.max():.3f}")

# Find most similar pair
max_sim = 0
most_similar = None
for i in range(n_models):
    for j in range(i+1, n_models):
        if similarity_matrix[i, j] > max_sim:
            max_sim = similarity_matrix[i, j]
            most_similar = (model_names[i], model_names[j])

print(f"\nMost similar pair: {most_similar[0]} ↔ {most_similar[1]} ({max_sim:.3f})")

# Find least similar pair
min_sim = 1.0
least_similar = None
for i in range(n_models):
    for j in range(i+1, n_models):
        if similarity_matrix[i, j] < min_sim:
            min_sim = similarity_matrix[i, j]
            least_similar = (model_names[i], model_names[j])

print(f"Least similar pair: {least_similar[0]} ↔ {least_similar[1]} ({min_sim:.3f})")
