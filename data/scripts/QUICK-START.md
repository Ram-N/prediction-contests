# NFL 2025 - Quick Workflow for Score Updates

## Tomorrow's Workflow (After Games Complete)

### Step 1: Update Results File
```bash
vim /home/ram/projects/prediction-contests/data/NFL-2025-results.csv
```

Change TBD to the winning team code:
- Current results file has: `HOU-NE, TBD` and `LAR-CHI, TBD`
- Update to winners, e.g.: `HOU-NE, HOU` and `LAR-CHI, CHI`
- **Important**: Use exact team codes (HOU not Houston, LAR not LA or LAR)

### Step 2: Run Scoring Script
```bash
cd /home/ram/projects/prediction-contests/data/scripts
uv run python score_active_contest_predictions.py
```

The script will:
- Calculate penalties for all participants
- Update `active-contest/leaderboard.md`
- Create new blog post in `_posts/`

### Step 3: Preview Locally (Optional but Recommended)
```bash
cd /home/ram/projects/prediction-contests
bundle exec jekyll serve
```

Visit: http://localhost:4000/prediction-contests/nfl-2025/leaderboard

### Step 4: Commit and Push
```bash
cd /home/ram/projects/prediction-contests

# Add the changed files
git add data/NFL-2025-results.csv active-contest/leaderboard.md _posts/2026-01-*

# Commit with descriptive message
git commit -m "feat(nfl-2025): update leaderboard after divisional round

- HOU defeats NE [score]
- CHI defeats LAR [score]
- Updated standings
- Added blog post with analysis

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push
```

## Current Status

**Games Scored**: 2 of 7
- ✅ BUF-DEN: DEN won
- ✅ SF-SEA: SEA won
- ⏳ HOU-NE: TBD (tomorrow)
- ⏳ LAR-CHI: TBD (tomorrow)

**Remaining Games**: 3 (2 conference championships + Super Bowl)

## Team Codes Reference

Make sure to use these exact codes in the results file:

- **BUF** - Buffalo Bills
- **DEN** - Denver Broncos
- **HOU** - Houston Texans
- **NE** - New England Patriots
- **SF** - San Francisco 49ers (not SFO)
- **SEA** - Seattle Seahawks
- **LAR** - Los Angeles Rams (not LA)
- **CHI** - Chicago Bears

## Troubleshooting

**If you see "Winner X not in matchup Y-Z":**
- Check that team codes match exactly between results and predictions files
- Add mapping to `contest_config.json` if needed

**If Jekyll doesn't rebuild:**
- Wait 1-2 minutes after push
- Check GitHub Actions tab for build status

**If script fails:**
- Check that results file has proper format: `Column, Winner`
- Verify no trailing spaces or extra commas
- Make sure winning team code exists in predictions CSV
