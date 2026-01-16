# Archiving the Current Contest

This guide walks through the process of archiving a completed contest and preparing for the next one.

## When to Archive

Archive a contest when:
- All matches are complete
- Final leaderboard is published
- Winners are announced
- No further updates are needed

## Pre-Archive Checklist

Before archiving, ensure:
- [ ] Final leaderboard is updated and correct
- [ ] All match results are recorded
- [ ] Winner(s) announced in a final blog post
- [ ] Winner(s) added to Hall of Fame (`past/hof.md`)
- [ ] All contest pages are complete and accurate

## Archive Process

### Step 1: Identify Current Contest Directory

```bash
# List top-level directories (excluding standard Jekyll dirs)
ls -d */ | grep -v '^_\|^docs\|^assets\|^img\|^bin\|^past'

# Current contest example: t20-2024/
```

### Step 2: Move to Past Directory

```bash
# Move current contest to past/
mv t20-2024/ past/t20-2024/

# Verify the move
ls past/t20-2024/
```

### Step 3: Update Internal Links

The archived contest pages may have relative links that need updating:

```bash
# Check for links in archived contest
grep -r "permalink:" past/t20-2024/

# Update permalinks if needed (should already be absolute with /t20-2024/ prefix)
```

**Important**: If permalinks were correctly set with the contest name prefix (e.g., `/t20-2024/rules`), they will continue to work after moving to `past/`.

### Step 4: Update Hall of Fame

Edit `past/hof.md` to add the contest winner(s):

```markdown
## T20 World Cup 2024
**Winner**: Ishaan (Oakland, USA)
**Score**: 38 out of 48 points
**Contest Page**: [T20 2024 Results](/prediction-contests/past/t20-2024/leaderboard)
```

### Step 5: Update Past Contests Index

Edit `past/index.md` to add a link to the archived contest:

```markdown
## Past Contests

- [T20 World Cup 2024](/prediction-contests/past/t20-2024/) - Winner: Ishaan
- [ICC World Cup 2023](/prediction-contests/past/icc2023/) - Winner: ...
```

### Step 6: Update Home Page

Edit `index.html` to remove or update references to the completed contest:

```html
<!-- Update or remove current contest callouts -->
<!-- Add "View Past Contests" link if not present -->
```

### Step 7: Create Final Summary Post

Create a blog post summarizing the contest:

```bash
# Create final post
touch _posts/$(date +%Y-%m-%d)-t20-2024-final-results.md
```

Example content:
```markdown
---
layout: post
title: "T20 2024 World Cup Contest - Final Results"
subtitle: "Congratulations to our champion!"
date: 2024-06-30 10:00:00
background: '/img/t20-final.jpg'
---

The T20 2024 World Cup Prediction Contest has concluded!

**Champion**: Ishaan with 38 points out of a possible 48.

View the complete [final leaderboard](/prediction-contests/past/t20-2024/leaderboard).

Thank you to all participants!
```

## Setting Up Next Contest

### Step 1: Create New Contest Directory

```bash
# Example for next contest
mkdir -p world-cup-2026
cd world-cup-2026
```

### Step 2: Create Standard Pages

```bash
# Create standard contest pages
touch index.md rules.md leaderboard.md predictions.md schedule.md
```

### Step 3: Set Up Page Templates

**index.md**:
```markdown
---
layout: page
title: World Cup 2026 Prediction Contest
description: Predict the 2026 World Cup outcomes
background: '/img/wc-2026-bg.jpg'
permalink: "/world-cup-2026/"
---

Welcome to the World Cup 2026 Prediction Contest!

- [Contest Rules](/prediction-contests/world-cup-2026/rules)
- [Submit Predictions](/prediction-contests/world-cup-2026/entry)
- [Leaderboard](/prediction-contests/world-cup-2026/leaderboard)
```

**rules.md**:
```markdown
---
layout: page
title: Rules - 2026 World Cup Contest
description: Contest rules and scoring system
background: '/img/wc-2026-bg.jpg'
permalink: "/world-cup-2026/rules"
---

# World Cup 2026 Prediction Contest Rules

[Add contest-specific rules here]
```

### Step 4: Update Site Configuration

If the contest name should appear in site title:

```bash
# Edit _config.yml
vim _config.yml
```

```yaml
title: World Cup 2026 Prediction Contest
description: Predict the outcomes of the 2026 FIFA World Cup
```

Restart Jekyll after config changes:
```bash
bundle exec jekyll serve
```

### Step 5: Announce New Contest

Create announcement blog post:

```bash
touch _posts/$(date +%Y-%m-%d)-world-cup-2026-opens.md
```

```markdown
---
layout: post
title: "World Cup 2026 Contest Now Open!"
subtitle: "Make your predictions for the 2026 FIFA World Cup"
date: 2024-07-01 09:00:00
background: '/img/wc-2026-announcement.jpg'
---

The World Cup 2026 Prediction Contest is now open!

[Enter your predictions here](/prediction-contests/world-cup-2026/entry)

See the [contest rules](/prediction-contests/world-cup-2026/rules) for details.
```

### Step 6: Update Home Page

Edit `index.html` to feature the new contest.

## Testing After Archive

Before deploying:

```bash
# Start local server
bundle exec jekyll serve

# Test these pages:
# 1. Home page displays correctly
# 2. Archived contest pages still work (past/t20-2024/*)
# 3. Past contests index shows new archive
# 4. Hall of Fame updated
# 5. New contest pages are accessible
# 6. Internal links work correctly
```

## Deploy Changes

```bash
# Commit all changes
git add .
git commit -m "Archive T20 2024 contest and set up World Cup 2026"

# Push to GitHub Pages
git push origin main
```

## Quick Command Summary

```bash
# Archive current contest
mv current-contest-dir/ past/current-contest-dir/

# Update Hall of Fame
vim past/hof.md

# Update past index
vim past/index.md

# Create new contest
mkdir new-contest-2026
cd new-contest-2026
touch index.md rules.md leaderboard.md predictions.md schedule.md

# Test locally
bundle exec jekyll serve

# Deploy
git add . && git commit -m "Archive and setup new contest" && git push origin main
```

## Troubleshooting

**Archived pages return 404**:
- Check that permalinks include the contest directory (e.g., `/t20-2024/rules` not just `/rules`)
- Verify files were moved correctly to `past/` directory

**Images not loading on archived pages**:
- Image paths should be absolute: `/img/filename.jpg`
- Don't use relative paths like `../img/filename.jpg`

**Links broken after archive**:
- Use absolute paths with baseurl: `/prediction-contests/past/t20-2024/page`
- Avoid relative links between contest pages

## Notes

- Keep archived contest directories read-only (don't modify after archiving unless fixing bugs)
- Archived contests remain accessible at their original URLs
- Historical data is valuable for reference when setting up future contests
- Consider backing up contest data before archiving (git already provides this)
