# Contest Prediction Scoring Scripts

## Overview

These scripts calculate cross-entropy (log loss) penalties for prediction contests and generate leaderboard pages and blog posts for the Jekyll site.

## Usage

### Running the Script

```bash
cd /home/ram/projects/prediction-contests/data/scripts
uv run python score_active_contest_predictions.py
```

The script will:
1. Read configuration from `contest_config.json`
2. Load predictions and results
3. Calculate penalties for all participants
4. Generate updated leaderboard markdown
5. Create a blog post announcing the update

### When to Run

After each round of playoff games completes:
1. Update the results CSV file (change TBD to the winning team code)
2. Run the scoring script
3. Preview locally with `bundle exec jekyll serve`
4. Commit and push the changes

## Configuration

### `contest_config.json`

This file contains all contest-specific settings:

```json
{
  "contest_name": "NFL 2025",           // Display name for the contest
  "contest_slug": "nfl-2025",           // URL slug (used in permalinks)
  "predictions_file": "../NFL-2025-Predictions-Clean.csv",
  "results_file": "../NFL-2025-results.csv",
  "leaderboard_file": "../../nfl-2025/leaderboard.md",
  "blog_post_dir": "../../_posts/",
  "background_image": "/img/bg_nfl.webp",
  "total_games": 7,                     // Total games in the contest
  "round_names": {                      // Round names for blog post filenames
    "2": "divisional-round-saturday",
    "4": "divisional-round",
    "6": "conference-championships",
    "7": "super-bowl"
  },
  "team_code_map": {                    // Maps alternate team codes to standard codes
    "SFO": "SF",
    "LA": "LAR"
  }
}
```

## Setting Up a New Contest

### 1. Prepare Data Files

Create two CSV files in the `/data` directory:

**Predictions CSV** (e.g., `FIFA-2026-Predictions-Clean.csv`):
```csv
Name,TEAM1,TEAM2,TEAM3,TEAM4,...
Participant 1,80,60,40,70,...
Participant 2,70,30,40,60,...
```

**Results CSV** (e.g., `FIFA-2026-results.csv`):
```csv
Column, Winner
TEAM1-TEAM2, TBD
TEAM3-TEAM4, TBD
```

### 2. Create Contest Directory

```bash
mkdir /home/ram/projects/prediction-contests/fifa-2026
```

### 3. Update Configuration

Edit `contest_config.json` with new contest details:

```json
{
  "contest_name": "FIFA 2026",
  "contest_slug": "fifa-2026",
  "predictions_file": "../FIFA-2026-Predictions-Clean.csv",
  "results_file": "../FIFA-2026-results.csv",
  "leaderboard_file": "../../fifa-2026/leaderboard.md",
  "blog_post_dir": "../../_posts/",
  "background_image": "/img/bg_fifa.webp",
  "total_games": 7,
  "round_names": {
    "4": "round-of-16",
    "6": "quarterfinals",
    "7": "semifinals",
    "8": "final"
  },
  "team_code_map": {}
}
```

### 4. Run Script

```bash
uv run python score_active_contest_predictions.py
```

This will generate:
- `fifa-2026/leaderboard.md`
- `_posts/YYYY-MM-DD-fifa-2026-after-[round].md`

### 5. Test and Deploy

```bash
cd /home/ram/projects/prediction-contests
bundle exec jekyll serve
# Visit http://localhost:4000/prediction-contests/fifa-2026/leaderboard
```

## File Formats

### Predictions CSV Format

- First column: `Name` (participant name)
- Remaining columns: Team codes (must match results file exactly)
- Values: Confidence scores (1-100)

### Results CSV Format

- First column: `Column` (matchup in format "TEAM1-TEAM2")
- Second column: ` Winner` (note the leading space - this is from Excel export)
- Winner values: Team code or "TBD" for incomplete games

**Important**: Team codes in results must exactly match predictions columns, or use `team_code_map` to handle variations.

## Scoring Formula

**Cross-Entropy (Log Loss):**

```
Penalty = log₂((score_team1 + score_team2) / score_winner)
```

This is equivalent to `-log₂(p_winner)` where `p_winner = score_winner / total_score`

### Examples

- Perfect prediction (100-1): penalty = 0.01
- Confident correct (80-20): penalty = 0.32
- Moderate correct (60-40): penalty = 0.74
- 50-50 prediction: penalty = 1.0
- Wrong direction (40-60, winner got 40): penalty = 1.32
- Very wrong (20-80, winner got 20): penalty = 2.32

### Leaderboard Formatting

- **Bold numbers**: Directionally correct (higher score given to winner)
- <u>Underlined numbers</u>: Best (lowest penalty) prediction for that game
- Combined `<u>**0.32**</u>`: Both directionally correct AND best score

## Troubleshooting

### Team Code Mismatch

If you see an error like "Winner SF not in matchup SFO-SEA", add a mapping:

```json
"team_code_map": {
  "SFO": "SF"
}
```

### Missing Predictions

Ensure all team codes in results file have corresponding columns in predictions CSV.

### Jekyll Build Errors

Check that:
- Permalink paths match contest directory structure
- Background images exist at specified paths
- Markdown syntax is valid (especially table formatting)

## Git Workflow

```bash
# 1. Update results
vim /home/ram/projects/prediction-contests/data/FIFA-2026-results.csv

# 2. Run scoring
cd /home/ram/projects/prediction-contests/data/scripts
uv run python score_active_contest_predictions.py

# 3. Test locally
cd /home/ram/projects/prediction-contests
bundle exec jekyll serve

# 4. Commit and push
git add data/FIFA-2026-results.csv fifa-2026/leaderboard.md _posts/2026-*
git commit -m "feat(fifa-2026): update leaderboard after quarterfinals

- [Game results summary]
- Updated standings
- Added blog post with analysis

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push
```

## Future Enhancements

Possible improvements for future versions:

- Command-line arguments to specify config file
- Automatic team code detection/normalization
- Support for multiple contest formats (not just playoffs)
- Historical data export (CSV, JSON)
- Visualization generation (charts, graphs)
