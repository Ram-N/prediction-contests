import pandas as pd

# Read the CSV file
df = pd.read_csv('/home/ram/projects/prediction-contests/data/T20-2026-responses.csv')

# Define new column names
new_columns = ['Time', 'Email', 'Name', 'Location', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']

# Rename columns
df.columns = new_columns

# Define AI entries
ai_names = ['ChatGPT', 'Claude (Sonnet 4.5)', 'Gemini (Thinking Mode)', 'Perplexity']

# Add AI column (1 for AI, 0 for human)
df['AI'] = df['Name'].apply(lambda x: 1 if x in ai_names else 0)

# Drop Email column
df = df.drop('Email', axis=1)

# Save the processed file
df.to_csv('/home/ram/projects/prediction-contests/data/T20-2026-Predictions-Clean.csv', index=False)

print(f"Processed {len(df)} entries")
print(f"AI entries: {df['AI'].sum()}")
print(f"Human entries: {len(df) - df['AI'].sum()}")
print("\nFirst few rows:")
print(df.head())
print("\nLast few rows:")
print(df.tail())
