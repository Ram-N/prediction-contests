import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# 1. GENERATE MOCK DATA (Replace this with pd.read_csv)
# ---------------------------------------------------------

#pd.read_csv('t20_predictions.csv') #uncomment this line to read from actual CSV

# Define teams for context
teams_per_group = {
    'A': ['India', 'Pakistan', 'USA', 'Namibia', 'NED'],
    'B': ['Australia', 'Sri Lanka', 'Zimbabwe', 'Ireland', 'Oman'],
    'C': ['West Indies', 'England', 'Italy', 'Scotland', 'Nepal'],
    'D': ['South Africa', 'Afghanistan', 'New Zealand', 'Canada', 'UAE']
}


# Add the "Canonical AI" (The Hive Mind)
canonical_ai = {
    'Participant': 'Canonical_AI',
    'Group A - 1st': 'India', 'Group A - 2nd': 'Pakistan',
    'Group B - 1st': 'Australia', 'Group B - 2nd': 'Sri Lanka',
    'Group C - 1st': 'England', 'Group C - 2nd': 'West Indies',
    'Group D - 1st': 'South Africa', 'Group D - 2nd': 'New Zealand'
}

# Use the AI column 0/1 to detect humans vs AI for later analysis

# ---------------------------------------------------------
# 2. CALCULATE SIMILARITY SCORES
# ---------------------------------------------------------

def calculate_similarity(human_row, ai_row):
    score = 0
    for group in ['A', 'B', 'C', 'D']:
        h1, h2 = human_row[f'Group {group} - 1st'], human_row[f'Group {group} - 2nd']
        a1, a2 = ai_row[f'Group {group} - 1st'], ai_row[f'Group {group} - 2nd']
        
        # Scoring logic: 2 pts for exact match, 1 pt for correct pair but wrong order
        if h1 == a1 and h2 == a2:
            score += 2 
        elif h1 == a2 and h2 == a1:
            score += 1
        # No points if partial match (per your rules for this specific metric)
    return score

human_df = human_df.copy() # Avoid SettingWithCopyWarning
human_df['AI_Similarity_Score'] = human_df.apply(lambda x: calculate_similarity(x, ai_row), axis=1)

# ---------------------------------------------------------
# 3. VISUALIZATIONS
# ---------------------------------------------------------

# A. The AI Similarity Bell Curve
plt.figure(figsize=(10, 6))
sns.histplot(human_df['AI_Similarity_Score'], bins=np.arange(0, 10)-0.5, kde=True, color='skyblue')
plt.title('How "Robotic" Are The Humans?')
plt.xlabel('Similarity Score vs Canonical AI (Max 8)')
plt.ylabel('Number of Participants')
plt.axvline(human_df['AI_Similarity_Score'].mean(), color='red', linestyle='--', label='Average')
plt.legend()
plt.tight_layout()
plt.show()

# B. The Consensus Heatmap (Example for Group D)
def plot_group_heatmap(group_name):
    teams = teams_per_group[group_name]
    # Create empty matrix
    matrix = pd.DataFrame(0, index=teams, columns=['1st Place Pick', '2nd Place Pick'])
    
    # Fill matrix
    for _, row in human_df.iterrows():
        t1 = row[f'Group {group_name} - 1st']
        t2 = row[f'Group {group_name} - 2nd']
        if t1 in teams: matrix.loc[t1, '1st Place Pick'] += 1
        if t2 in teams: matrix.loc[t2, '2nd Place Pick'] += 1
            
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='YlGnBu')
    plt.title(f'Group {group_name} Consensus Heatmap')
    plt.tight_layout()
    plt.show()

plot_group_heatmap('D')

# C. The "Chaos" Bar Chart (Unique Combinations per Group)
unique_counts = {}
for group in ['A', 'B', 'C', 'D']:
    cols = [f'Group {group} - 1st', f'Group {group} - 2nd']
    # Create a tuple of the prediction to count uniques
    combos = human_df[cols].apply(lambda x: (x[0], x[1]), axis=1)
    unique_counts[group] = combos.nunique()

plt.figure(figsize=(8, 5))
plt.bar(unique_counts.keys(), unique_counts.values(), color=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
plt.title('The Chaos Index: Unique Predictions per Group')
plt.xlabel('Group')
plt.ylabel('Unique Outcome Combinations')
plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# 4. FACTOIDS GENERATION
# ---------------------------------------------------------

print("\n--- INTERESTING FACTOIDS ---")

# 1. The Echo Chamber (Identical Predictions)
pred_cols = [c for c in df.columns if 'Group' in c]
duplicates = human_df[human_df.duplicated(subset=pred_cols, keep=False)]

if not duplicates.empty:
    print(f"\n[Echo Chamber Alert!] {len(duplicates)} participants have identical brackets.")
    # Group by the prediction string to show who matches whom
    duplicates['combined_preds'] = duplicates[pred_cols].astype(str).sum(axis=1)
    for preds, group_df in duplicates.groupby('combined_preds'):
        names = group_df['Participant'].tolist()
        print(f"  -> Prediction Twins: {', '.join(names)}")
else:
    print("\n[The Individualists] No two humans have the exact same bracket!")

# 2. The Lone Ranger (Unique Picks)
print("\n[The Lone Rangers]")
found_lone_ranger = False
for group in ['A', 'B', 'C', 'D']:
    for rank in ['1st', '2nd']:
        col = f'Group {group} - {rank}'
        counts = human_df[col].value_counts()
        singles = counts[counts == 1].index.tolist()
        for team in singles:
            person = human_df[human_df[col] == team]['Participant'].iloc[0]
            print(f"  -> {person} is the ONLY one who picked {team} to finish {rank} in Group {group}.")
            found_lone_ranger = True
if not found_lone_ranger:
    print("  -> None found. Everyone has at least one ally.")

# 3. Average Similarity Score
avg_score = human_df['AI_Similarity_Score'].mean()
print(f"\n[Man vs Machine] Average Human Similarity to AI: {avg_score:.2f} / 8.0")