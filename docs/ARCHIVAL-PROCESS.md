# Contest Archival Process

This document describes how to archive a completed contest and set up a new one using the automated archival script.

## Overview

The prediction-contests repository uses an `active-contest/` directory for the current contest. When a contest concludes, it is moved to `past/{contest-slug}/` and a new contest is set up in `active-contest/`.

## Quick Start

When the current contest is complete:

```bash
cd /home/ram/projects/prediction-contests
bash bin/archive_contest.sh
```

The script will guide you through:
1. Confirming archival of the current contest
2. Moving `active-contest/` to `past/{slug}/`
3. Setting up a new contest in `active-contest/`
4. Updating `_config.yml` with new contest details

## What the Script Does

### Step 1: Read Current Contest

The script reads the current contest slug from `_config.yml`:

```yaml
contest:
  slug: "nfl-2025"
  name: "NFL 2025 Playoffs"
  ...
```

### Step 2: Bake Liquid Variables

Before archiving, the script replaces all liquid variables in the contest files with hardcoded values:

- `{{ site.contest.slug }}` → `nfl-2025`
- `{{ site.baseurl }}/{{ site.contest.slug }}/` → `/prediction-contests/nfl-2025/`

This ensures that past contest URLs remain stable after archival.

### Step 3: Move to Past Directory

The contest directory is moved from `active-contest/` to `past/nfl-2025/` using git:

```bash
git mv active-contest/ past/nfl-2025/
```

### Step 4: Prompt for New Contest Details

The script prompts for:
- Contest slug (e.g., `fifa-2026`)
- Contest short name (e.g., `FIFA 2026`)
- Contest full title (e.g., `FIFA World Cup 2026 Prediction Contest`)
- Background image path (e.g., `/img/bg_fifa.webp`)
- Entry form URL (Google Form)

### Step 5: Update Configuration

The script updates `_config.yml` with new contest details:

```yaml
contest:
  slug: "fifa-2026"
  name: "FIFA 2026"
  full_title: "FIFA World Cup 2026 Prediction Contest"
  background: "/img/bg_fifa.webp"
  entry_form: "https://forms.gle/..."
```

### Step 6: Create New Active Contest

The script copies template files from `templates/active-contest/` to create a new `active-contest/` directory with skeleton files.

## After Running the Script

### 1. Update Active Contest Files

Customize the new contest files with specific content:

```bash
vim active-contest/index.md
vim active-contest/rules.md
vim active-contest/entry.md
vim active-contest/leaderboard.md
vim active-contest/predictions.md
```

Update:
- Contest descriptions
- Game schedules
- Scoring rules
- Deadlines

### 2. Create Data Files

Create new prediction and results CSV files:

```bash
vim data/FIFA-2026-Predictions-Clean.csv
vim data/FIFA-2026-results.csv
```

### 3. Update Scoring Script Config

Update `data/scripts/contest_config.json`:

```json
{
  "contest_name": "FIFA 2026",
  "contest_slug": "fifa-2026",
  "predictions_file": "../FIFA-2026-Predictions-Clean.csv",
  "results_file": "../FIFA-2026-results.csv",
  "leaderboard_file": "../../active-contest/leaderboard.md",
  "blog_post_dir": "../../_posts/",
  "background_image": "/img/bg_fifa.webp",
  "total_games": 7,
  "round_names": {
    "4": "round-of-16",
    "6": "quarterfinals",
    "7": "final"
  },
  "team_code_map": {}
}
```

Note: `leaderboard_file` should always be `../../active-contest/leaderboard.md` - it does not change between contests.

### 4. Update Navbar (if needed)

The navbar in `_includes/navbar.html` uses liquid variables and should automatically update to the new contest. Verify it looks correct.

### 5. Test Locally

```bash
bundle exec jekyll serve
```

Visit:
- http://localhost:4000/prediction-contests/fifa-2026/ (new contest)
- http://localhost:4000/prediction-contests/past/nfl-2025/ (archived contest)

### 6. Commit and Push

```bash
git add .
git commit -m "chore: archive nfl-2025 and start fifa-2026

- Moved nfl-2025 to past/
- Created new active-contest for fifa-2026
- Updated configuration and templates

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push
```

## Manual Archival (If Script Fails)

If you need to archive manually:

### 1. Read Current Slug

```bash
SLUG=$(grep -A1 "^contest:" _config.yml | grep "slug:" | awk '{print $2}' | tr -d '"')
echo $SLUG
```

### 2. Replace Variables

```bash
find active-contest/ -name "*.md" -exec sed -i \
  -e "s|{{ site.contest.slug }}|$SLUG|g" \
  -e "s|{{ site.baseurl }}/{{ site.contest.slug }}|/prediction-contests/$SLUG|g" \
  {} \;
```

### 3. Move Directory

```bash
git mv active-contest/ past/$SLUG/
```

### 4. Update _config.yml

Manually edit `_config.yml` to update the `contest:` section with new details.

### 5. Copy Templates

```bash
cp -r templates/active-contest/ ./
```

### 6. Proceed with steps in "After Running the Script" section above.

## Directory Structure

```
prediction-contests/
├── active-contest/          # Current contest (e.g., FIFA 2026)
│   ├── index.md
│   ├── rules.md
│   ├── leaderboard.md
│   ├── predictions.md
│   └── entry.md
├── past/                    # Archived contests
│   ├── nfl-2025/
│   ├── t20-2024/
│   ├── fifa2022/
│   └── ...
├── templates/               # Template files for new contests
│   └── active-contest/
├── bin/
│   └── archive_contest.sh   # Archival script
├── data/
│   ├── scripts/
│   │   ├── contest_config.json
│   │   └── score_active_contest_predictions.py
│   ├── NFL-2025-Predictions-Clean.csv
│   └── NFL-2025-results.csv
└── _config.yml              # Jekyll config with active contest slug
```

## Benefits of This Approach

1. **Single Source of Truth**: Contest slug defined once in `_config.yml`
2. **Stable URLs**: Past contests remain accessible at their original URLs
3. **Automated Transitions**: Script reduces manual work from ~15 steps to ~2
4. **Consistent Structure**: All contests follow the same pattern
5. **Scoring Script Never Changes Paths**: Always points to `active-contest/`

## Troubleshooting

### "Could not read contest slug from _config.yml"

Check that `_config.yml` has the correct structure:

```yaml
contest:
  slug: "nfl-2025"
```

### Archival Script Doesn't Run

Make sure it's executable:

```bash
chmod +x bin/archive_contest.sh
```

### Templates Not Found

Ensure `templates/active-contest/` exists with the required files:

```bash
ls templates/active-contest/
# Should show: index.md rules.md entry.md leaderboard.md predictions.md
```

### Jekyll Build Errors After Archival

1. Check that past contest permalinks are hardcoded (no liquid variables)
2. Verify new contest has proper front matter
3. Ensure background images exist at specified paths

## See Also

- [Contest Management Guide](CONTEST-MANAGEMENT.md)
- [Scoring Script README](../data/scripts/README.md)
- [Quick Start Guide](../data/scripts/QUICK-START.md)
