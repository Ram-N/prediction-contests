import pandas as pd

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

# Define AI-canonical predictions (Claude/ChatGPT/Perplexity)
ai_canonical = {
    'A': ('India', 'Pakistan'),
    'B': ('Australia', 'Sri Lanka'),
    'C': ('England', 'West Indies'),
    'D': ('South Africa', 'New Zealand')
}

print("AI-Canonical Predictions:")
print("=" * 80)
for group, teams in ai_canonical.items():
    print(f"  Group {group}: {teams[0]}, {teams[1]}")
print()

# Calculate similarity for each entry
similarities = []

for idx, row in df.iterrows():
    person_preds = {
        'A': (row['A1'], row['A2']),
        'B': (row['B1'], row['B2']),
        'C': (row['C1'], row['C2']),
        'D': (row['D1'], row['D2'])
    }

    sim = model_similarity(person_preds, ai_canonical)
    similarities.append(sim)

# Add similarity column
df['AI_Similarity'] = similarities

# Save the updated file
output_path = '/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv'
df.to_csv(output_path, index=False)

print(f"Updated predictions with AI similarity scores")
print(f"Saved to: {output_path}")
print()

# Show statistics
print("Statistics:")
print("=" * 80)
print(f"Total entries: {len(df)}")
print(f"Average AI similarity: {df['AI_Similarity'].mean():.3f}")
print(f"Std deviation: {df['AI_Similarity'].std():.3f}")
print(f"Min similarity: {df['AI_Similarity'].min():.3f}")
print(f"Max similarity: {df['AI_Similarity'].max():.3f}")
print()

# Show human vs AI statistics
human_df = df[df['AI'] == 0]
ai_df = df[df['AI'] == 1]

print("Human predictions:")
print(f"  Average similarity to AI-canonical: {human_df['AI_Similarity'].mean():.3f}")
print(f"  Std deviation: {human_df['AI_Similarity'].std():.3f}")
print()

print("AI predictions:")
print(f"  Average similarity to AI-canonical: {ai_df['AI_Similarity'].mean():.3f}")
print()

# Top 5 humans most similar to AI
print("Top 5 humans most similar to AI-canonical:")
print("=" * 80)
top_5 = human_df.nlargest(5, 'AI_Similarity')[['Name', 'Location', 'AI_Similarity']]
for idx, row in top_5.iterrows():
    print(f"  {row['Name']:30} ({row['Location']:30}) - {row['AI_Similarity']:.3f}")
print()

# Top 5 humans least similar to AI
print("Top 5 humans least similar to AI-canonical:")
print("=" * 80)
bottom_5 = human_df.nsmallest(5, 'AI_Similarity')[['Name', 'Location', 'AI_Similarity']]
for idx, row in bottom_5.iterrows():
    print(f"  {row['Name']:30} ({row['Location']:30}) - {row['AI_Similarity']:.3f}")
print()

# Show sample of the data
print("Sample of updated data:")
print("=" * 80)
print(df[['Name', 'Location', 'A1', 'A2', 'AI', 'AI_Similarity']].head(10).to_string(index=False))
