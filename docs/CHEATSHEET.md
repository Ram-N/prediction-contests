# Prediction Contests Cheat Sheet

Quick reference for common tasks.

## Daily Operations

### Update Leaderboard
```bash
vim current-contest/leaderboard.md
git add current-contest/leaderboard.md
git commit -m "feat(leaderboard): update scores after [round/game]"
git push
```

### Add Blog Post
```bash
vim _posts/$(date +%Y-%m-%d)-descriptive-title.md
git add _posts/
git commit -m "docs(blog): [brief description]"
git push
```

### Publish Predictions
```bash
vim current-contest/predictions.md
git add current-contest/predictions.md
git commit -m "feat(predictions): publish all entries"
git push
```

## Transition to New Contest

### Quick Steps
```bash
# 1. Archive current
mv current-contest/ past/current-contest/
vim past/current-contest.md          # Create index
vim past/hof.md                      # Add winner
vim past/index.md                    # Add to list

# 2. Create new
mkdir new-contest && cd new-contest
touch index.md rules.md leaderboard.md predictions.md entry.md

# 3. Update site
vim ../_config.yml                   # Change title
vim ../_includes/navbar.html         # Update nav
vim ../index.html                    # Change background

# 4. Announce
vim ../_posts/$(date +%Y-%m-%d)-new-contest.md

# 5. Deploy
git add -A
git commit -m "feat: launch [new] and archive [old]"
git push
```

## Table Formatting

### Basic Table
```markdown
{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Score |
|:-----|------:|
| **Winner** | 38 |
| Player 2 | 36 |
```

### Formatting Tips
- Bold winners: `**Name**`
- Italics for partial: `*5*`
- Right align numbers: `---:`
- Left align text: `:---`

## Test Locally
```bash
bundle exec jekyll serve
# Visit: http://127.0.0.1:4000/prediction-contests/
```

## Common File Locations
```
├── _config.yml              # Site title (requires restart)
├── _includes/navbar.html    # Navigation
├── _posts/                  # Blog posts (YYYY-MM-DD-title.md)
├── index.html               # Home page (background only)
├── current-contest/         # Active contest pages
│   ├── index.md
│   ├── rules.md
│   ├── leaderboard.md
│   ├── predictions.md
│   └── entry.md
└── past/                    # Archived contests
    ├── index.md             # List of past contests
    ├── hof.md               # Hall of Fame
    └── contest-name/        # Archived contest files
```

## Blog Post Template
```markdown
---
layout: post
title: "Clear Title Here"
subtitle: "Brief subtitle"
date: YYYY-MM-DD HH:MM:SS
background: '/img/contest-bg.webp'
---

Content here...
```

## Commit Message Patterns
```
feat(leaderboard): update after divisional round
docs(blog): announce winner
feat(predictions): publish entries
fix(leaderboard): correct score calculation
docs(rules): clarify deadline
```

## Emergency Commands
```bash
# Undo last commit (before push)
git reset --soft HEAD~1

# Discard all local changes
git checkout .

# Force pull from GitHub
git fetch origin
git reset --hard origin/main

# Check what changed
git diff
git status
```

## Help Commands
```bash
./remind-me.sh              # Quick reminders
cat docs/QUICKSTART.md      # Quick start guide
less docs/CONTEST-MANAGEMENT.md  # Full management guide
cat docs/archive-current-contest.md  # Archiving details
```

## Troubleshooting

### Changes Not Showing
1. Clear browser cache
2. Check file saved
3. Restart Jekyll if `_config.yml` changed
4. Check console for errors

### Table Not Formatting
1. Check style line: `{:.thead-dark .table-striped .table-bordered .table-sm }`
2. Must be directly before table
3. Check pipe `|` alignment
4. Verify separator row `|---|---|`

### 404 Error
1. Check permalink in front matter
2. Use absolute paths: `/prediction-contests/page`
3. Don't use relative `../` paths
4. Verify baseurl in `_config.yml`

---

**Full Documentation**: See `docs/CONTEST-MANAGEMENT.md`
