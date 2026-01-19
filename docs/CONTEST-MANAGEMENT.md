# Contest Management Guide

Complete guide for managing prediction contests - from launching to archiving.

---

## Table of Contents

- [Part 1: Transitioning Between Contests](#part-1-transitioning-between-contests)
- [Part 2: Managing an Active Contest](#part-2-managing-an-active-contest)

---

# Part 1: Transitioning Between Contests

When a contest ends and you're ready to start a new one, follow this workflow.

## Quick Checklist

- [ ] Verify final results are correct
- [ ] Archive current contest to `past/`
- [ ] Update Hall of Fame
- [ ] Update past contests index
- [ ] Create new contest directory
- [ ] Update site configuration
- [ ] Update navigation bar
- [ ] Update home page
- [ ] Create announcement blog post
- [ ] Test locally
- [ ] Commit and deploy

## Step-by-Step Process

### 1. Finalize Current Contest

Before archiving, ensure everything is complete:

```bash
# Check current contest directory
ls -la t20-2024/  # or current contest name

# Verify final leaderboard
cat t20-2024/leaderboard.md
```

**Checklist:**
- [ ] Final leaderboard updated with winner
- [ ] All match results recorded
- [ ] Winner clearly identified

### 2. Archive Current Contest

Move the completed contest to the `past/` directory:

```bash
# Move contest directory
mv current-contest/ past/current-contest/

# Example:
mv t20-2024/ past/t20-2024/
```

### 3. Create Past Contest Index Page

Create an index page for the archived contest:

```bash
vim past/current-contest.md
```

**Template:**
```markdown
---
layout: page
title: "2024 T20 World Cup Prediction Contest"
background: '/img/contest-bg.webp'
permalink: "/past/current-contest/"
---

<img class="img-fluid" src="../../img/contest-logo.jpg" alt="Contest Logo">

**Overall Winner**: [Winner Name] ([Location]) - [Score] points

- [Overall Leaderboard](leaderboard.html)
- [Rules](rules.html)

### Contest Stages

- [Stage 1](stage1.html)
- [Stage 2](stage2.html)

### Other Pages

- [Schedule](schedule.html)
- [Predictions](predictions.html)
```

### 4. Update Hall of Fame

Add the winner to `past/hof.md`:

```bash
vim past/hof.md
```

Add a new row at the top of the table:

```markdown
|2024|	T20 2024 WC Overall Contest	|Winner Name|
```

### 5. Update Past Contests Index

Update `past/index.md` to list the newly archived contest:

```bash
vim past/index.md
```

Add the new contest at the top of the list:

```markdown
## Past Contests

- [T20 World Cup 2024](/prediction-contests/past/t20-2024/) - Winner: Ishaan
- [NFL 2023](/prediction-contests/past/nfl2023/) - Winner: Ankit Agrawal
...
```

### 6. Create New Contest Directory

Create the directory structure for the new contest:

```bash
# Create new contest directory
mkdir -p nfl-2025

# Create standard pages
cd nfl-2025
touch index.md rules.md leaderboard.md predictions.md entry.md
```

### 7. Set Up New Contest Pages

**index.md**:
```markdown
---
layout: page
title: "NFL 2025-26 Playoff Prediction Contest"
description: "Predict the NFL playoff outcomes"
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/"
---

# NFL 2025-26 Playoff Prediction Contest

Welcome to the NFL 2025-26 Playoff Prediction Contest!

## 🏈 Enter Now

**[Submit Your Predictions](https://forms.gle/YOUR_FORM_ID)**

## Contest Information

- [Contest Rules](/prediction-contests/nfl-2025/rules)
- [Entry Form](https://forms.gle/YOUR_FORM_ID)
- [Current Leaderboard](/prediction-contests/nfl-2025/leaderboard)
- [All Predictions](/prediction-contests/nfl-2025/predictions)
```

**rules.md**:
```markdown
---
layout: page
title: "Rules - NFL 2025-26 Playoff Contest"
description: "Contest rules and scoring system"
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/rules"
---

# Contest Rules

[Add contest-specific rules, scoring system, deadlines]
```

**leaderboard.md**:
```markdown
---
layout: page
title: "Leaderboard - NFL 2025"
description: "Current standings"
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/leaderboard"
---

# Leaderboard

The leaderboard will be updated as games are completed.

Check back after the first games!
```

### 8. Update Site Configuration

Edit `_config.yml`:

```bash
vim _config.yml
```

Update the title:
```yaml
title: NFL 2025 Playoff Prediction Contest
```

**⚠️ Important**: Restart Jekyll after changing `_config.yml`:
```bash
# Stop server (Ctrl+C) and restart
bundle exec jekyll serve
```

### 9. Update Navigation Bar

Edit `_includes/navbar.html`:

```bash
vim _includes/navbar.html
```

Update the current contest dropdown:
```html
<li class="nav-item dropdown" style="text-decoration: none;">
  <a href={{ "/nfl-2025/" | relative_url }}>NFL 2025 &#9660;</a>
  <div class="dropdown-content">
    <a href={{ "/nfl-2025/" | relative_url }}>Home</a>
    <a href={{ "/nfl-2025/leaderboard" | relative_url }}>Leaderboard</a>
    <a href={{ "/nfl-2025/predictions" | relative_url }}>Predictions</a>
    <a href={{ "/nfl-2025/rules" | relative_url }}>Rules</a>
    <a href={{ "/nfl-2025/entry" | relative_url }}>Entry Form</a>
  </div>
</li>
```

Add archived contest to past contests dropdown:
```html
<li class="nav-item dropdown" style="text-decoration: none;">
  <a href={{ '/past' | relative_url }}> Past Contests &#9660;</a>
  <div class="dropdown-content">
    <a href={{ "/past/t20-2024" | relative_url }}> T20 WC 2024 </a>
    <a href={{ "/past/nfl2023" | relative_url }}> NFL 2023 </a>
    ...
  </div>
</li>
```

### 10. Update Home Page

Edit `index.html`:

```bash
vim index.html
```

Change the background image:
```yaml
---
layout: home
background: '/img/bg_nfl.webp'
---
```

### 11. Create Announcement Blog Post

Create a new blog post:

```bash
touch _posts/$(date +%Y-%m-%d)-new-contest-opens.md
```

**Template:**
```markdown
---
layout: post
title: "NFL 2025-26 Playoff Contest Now Open!"
subtitle: "Predict the playoff outcomes and Super Bowl LX"
date: 2026-01-16 10:00:00
background: '/img/bg_nfl.webp'
---

The NFL 2025-26 Playoff Prediction Contest is now open!

## Contest Details

Predict the outcomes of the remaining playoff games:
- Divisional Round (4 games)
- Conference Championships (2 games)
- Super Bowl LX (1 game)

## How to Enter

**[Submit your predictions now!](https://forms.gle/YOUR_FORM_ID)**

## Scoring

[Explain scoring system]

Good luck to all participants!

**[Submit Your Predictions](https://forms.gle/YOUR_FORM_ID)**
```

### 12. Test Locally

```bash
# Start Jekyll server
bundle exec jekyll serve

# Test these URLs:
# http://127.0.0.1:4000/prediction-contests/
# http://127.0.0.1:4000/prediction-contests/nfl-2025/
# http://127.0.0.1:4000/prediction-contests/past/
# http://127.0.0.1:4000/prediction-contests/past/t20-2024/
```

Verify:
- [ ] Home page shows new contest
- [ ] Navigation bar updated
- [ ] New contest pages work
- [ ] Archived contest pages still work
- [ ] Past contests index shows archived contest
- [ ] Hall of Fame updated

### 13. Commit and Deploy

```bash
# Stage all changes
git add -A

# Create commit
git commit -m "feat: launch nfl 2025 contest and archive t20 2024

Archive completed T20 2024 contest and launch new NFL 2025
playoff prediction contest.

Major changes:
- Archive T20 2024 to past/ with winner [Name]
- Create NFL 2025 contest structure
- Update site configuration and navigation
- Add entry form link
- Update home page

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub Pages
git push origin main
```

Site will be live at: https://ram-n.github.io/prediction-contests/

---

# Part 2: Managing an Active Contest

Day-to-day operations for running the current contest.

## Common Tasks Overview

| Task | Frequency | File(s) to Update |
|------|-----------|-------------------|
| Collect predictions | After entry deadline | `data/*.csv` |
| Create contacts list | After entry deadline | Google Contacts |
| Update leaderboard | After each match/round | `leaderboard.md` |
| Add predictions | After entry deadline | `predictions.md` |
| Post updates | As needed | `_posts/*.md` |
| Update rules/deadlines | Before each stage | `rules.md` |
| Add mini-contests | Per contest design | New `.md` files |

## 1. Updating the Leaderboard

The leaderboard is the most frequently updated page.

### Location
```
current-contest/leaderboard.md
```

### Process

1. **Calculate scores** (offline/spreadsheet)
2. **Update the markdown table**

```bash
vim nfl-2025/leaderboard.md
```

3. **Use proper table formatting**

```markdown
{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Location | Game1 | Game2 | Game3 | Total |
|:-----|:---------|------:|------:|------:|------:|
| **Winner** | USA | 0.5 | 0.8 | 1.2 | 2.5 |
| Player 2 | India | 1.0 | 1.5 | 0.9 | 3.4 |
```

**Formatting tips:**
- `{:.thead-dark .table-striped .table-bordered .table-sm }` must be on the line before the table
- Use `:` in separator row for alignment (`:---` left, `---:` right)
- Bold winners: `**Name**`
- Italics for partial points: `*2*`

4. **Test and deploy**

```bash
# Refresh browser (Jekyll auto-reloads)
# If looks good:
git add nfl-2025/leaderboard.md
git commit -m "feat(leaderboard): update scores after divisional round"
git push origin main
```

### Example: Adding Section Headers

```markdown
## Final Leaderboard

**Winner: Ishaan - 38 points**

{:.thead-dark .table-striped .table-bordered .table-sm }
| Rank | Name | Total Score |
|-----:|:-----|------------:|
| 1 | **Ishaan** | 38 |
| 2 | Kripa | 36 |

## Stage-by-Stage Breakdown

### Divisional Round

{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Game1 | Game2 | Game3 | Game4 | Subtotal |
...
```

## 2. Collecting and Processing Predictions

After the entry deadline closes, download and process the predictions from Google Forms.

### Location
```
data/CONTEST-NAME-Predictions.csv
data/CONTEST-NAME-results.csv
```

### Process

1. **Download predictions from Google Forms**
   - Open your Google Form responses
   - Click the Google Sheets icon to view responses in Sheets
   - File → Download → Comma-separated values (.csv)
   - Save as `NFL-2025-Predictions.csv` (or appropriate contest name)

2. **Store in data/ folder**

```bash
# Move downloaded file to data folder
mv ~/Downloads/NFL-2025-Predictions.csv data/
```

3. **Extract email addresses for Google Contacts**

This is useful for sending contest updates and reminders.

```bash
# Read the predictions file
cat data/NFL-2025-Predictions.csv
```

Create a simplified CSV for Google Contacts import:

```bash
# Create contacts CSV with name and email columns
# (Can be done manually or with a script)
vim data/NFL-2025-Contacts.csv
```

**Format:**
```csv
Name,Email Address
Player Name,email@example.com
Another Player,another@example.com
```

4. **Import to Google Contacts with label**

- Go to [contacts.google.com](https://contacts.google.com)
- Click **Import** (left sidebar)
- Click **Select file** and choose `NFL-2025-Contacts.csv`
- Click **Import**
- After import completes, select all newly imported contacts
- Click the **Label** icon (tag icon)
- Create new label: "NFL 2025 Contest" (or appropriate name)
- Click to apply the label

**Note:** Google Contacts will merge with existing contacts if emails already exist (no duplicates created).

5. **Create results tracking file**

Create a CSV to track actual game results:

```bash
vim data/NFL-2025-results.csv
```

**Initial format:**
```csv
Game,Winner,Result
Divisional 1,,
Divisional 2,,
```

As games complete, update this file with results for scoring calculations.

### Tips

- Keep the original predictions CSV unchanged as the source of truth
- The contacts label makes it easy to email all participants
- The results CSV should match the structure of your predictions for easy scoring
- Consider keeping a backup of the raw form responses

## 3. Publishing Predictions

After entry deadline, publish all predictions for transparency.

### Location
```
current-contest/predictions.md
```

### Process

1. **Export predictions from form** (Google Sheets, CSV, etc.)
2. **Format as markdown table**

```bash
vim nfl-2025/predictions.md
```

3. **Update the page**

```markdown
---
layout: page
title: "Predictions - NFL 2025"
description: "All submitted predictions"
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/predictions"
---

# All Submitted Predictions

Predictions submitted before the deadline on [Date].

{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Location | Team1 | Conf1 | Team2 | Conf2 | Winner |
|:-----|:---------|:------|------:|:------|------:|:-------|
| Player1 | USA | Chiefs | 0.8 | Eagles | 0.7 | Chiefs |
| Player2 | India | Bills | 0.9 | 49ers | 0.6 | Bills |

## Prediction Summary

- Total entries: 45
- Most popular pick: Chiefs (32 votes)
- Deadline: January 18, 2026, 1:00 PM EST
```

## 4. Adding Blog Posts

Use blog posts to announce updates, results, and milestones.

### Common Post Types

#### Contest Update Post

```bash
# Create new post
vim _posts/$(date +%Y-%m-%d)-divisional-round-results.md
```

```markdown
---
layout: post
title: "Divisional Round Complete - Updated Standings"
subtitle: "Close race after dramatic games"
date: 2026-01-19 18:00:00
background: '/img/bg_nfl.webp'
---

The Divisional Round is complete with some surprising results!

## Top Performers

- **Leading**: Ishaan with 12 points
- **Best Pick**: Sarah correctly predicted the upset with 95% confidence

## Updated Standings

Check the full [leaderboard](/prediction-contests/nfl-2025/leaderboard) for all scores.

## Next Up

Conference Championships kick off this weekend. Your predictions are locked in!
```

#### Winner Announcement Post

```markdown
---
layout: post
title: "Congratulations to Our Champion!"
subtitle: "NFL 2025 Contest Winner Announced"
date: 2026-02-10 20:00:00
background: '/img/bg_nfl.webp'
---

The NFL 2025 Playoff Prediction Contest has concluded!

## Champion

**Ishaan** wins with a total score of 38 points!

[View final standings](/prediction-contests/nfl-2025/leaderboard)

## Hall of Fame

Ishaan joins our [Hall of Fame](/prediction-contests/past/hof) alongside past champions.

Thank you to all 45 participants!
```

#### Mini-Contest Announcement

```markdown
---
layout: post
title: "Super Bowl Mini-Contest Open"
subtitle: "Special predictions for the big game"
date: 2026-02-03 10:00:00
background: '/img/bg_nfl.webp'
---

We're running a special Super Bowl mini-contest!

## How It Works

Predict additional details:
- Final score
- MVP
- Total yards

[Enter the mini-contest](/prediction-contests/nfl-2025/superbowl-mini)

Open to everyone, even if you didn't enter the main contest!
```

### Deploying Posts

```bash
git add _posts/2026-01-19-divisional-round-results.md
git commit -m "docs(blog): add divisional round results post"
git push origin main
```

## 5. Creating Stage-Specific Pages

For multi-stage contests (like World Cups), create separate pages for each stage.

### Example: Creating a Semi-Finals Page

```bash
vim current-contest/semifinals.md
```

```markdown
---
layout: page
title: "Semi-Finals - T20 2024"
description: "Semi-finals predictions and results"
background: '/img/semifinals.jpg'
permalink: "/t20-2024/semifinals"
---

# Semi-Finals

## Matches

### Match 1: India vs England
**Result**: India wins by 68 runs

### Match 2: South Africa vs Australia
**Result**: South Africa wins by 3 wickets

## Semi-Finals Leaderboard

{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Match1 | Match2 | Total |
|:-----|-------:|-------:|------:|
| Ishaan | 2.0 | 1.5 | 3.5 |
...

[View overall leaderboard](/prediction-contests/t20-2024/leaderboard)
```

Update navigation to include the new stage:

```bash
vim _includes/navbar.html
```

Add to dropdown:
```html
<a href={{ "/t20-2024/semifinals" | relative_url }}> Semi-Finals </a>
```

## 6. Updating Entry Deadline / Rules

As contest progresses, update deadlines or add clarifications.

```bash
vim current-contest/rules.md
```

**Before:**
```markdown
## Deadlines

- **Predictions close**: TBD
```

**After:**
```markdown
## Deadlines

- **Predictions close**: January 18, 2026, 1:00 PM EST
- **Late entries**: Not accepted after deadline

## Entry Status

**CLOSED** - Deadline has passed. 45 entries received.
```

## 7. Adding Mini-Contests

Mini-contests are short, focused prediction challenges within the main contest.

### Create Mini-Contest Page

```bash
vim current-contest/superbowl-mini.md
```

```markdown
---
layout: page
title: "Super Bowl Mini-Contest"
description: "Special Super Bowl predictions"
background: '/img/superbowl.jpg'
permalink: "/nfl-2025/superbowl-mini"
---

# Super Bowl LX Mini-Contest

Predict specific game details for bonus points!

## How to Enter

**[Submit Mini-Contest Entry](https://forms.gle/MINI_CONTEST_FORM)**

## Predictions

1. Final score (exact)
2. MVP
3. Total yards (closest wins)
4. First touchdown scorer

## Prizes

Winner added to Hall of Fame as "Super Bowl Mini-Contest Champion"

## Deadline

Sunday, February 9, 2026, 6:00 PM EST (before kickoff)
```

### Announce via Blog Post

```bash
vim _posts/2026-02-03-superbowl-mini-contest.md
```

## 8. Quick Commands Reference

### Daily Operations

```bash
# Update leaderboard
vim current-contest/leaderboard.md
git add current-contest/leaderboard.md
git commit -m "feat(leaderboard): update after game X"
git push

# Add blog post
vim _posts/$(date +%Y-%m-%d)-update.md
git add _posts/
git commit -m "docs(blog): add update post"
git push

# Update predictions
vim current-contest/predictions.md
git add current-contest/predictions.md
git commit -m "feat(predictions): publish all entries"
git push
```

### Testing Locally

```bash
# Start server
bundle exec jekyll serve

# View at:
# http://127.0.0.1:4000/prediction-contests/
```

## 9. Contest-Specific Tips

### For NFL Contests

- Update after each playoff round
- Mini-contests for Super Bowl are popular
- Include confidence levels in predictions table
- Show game-by-game breakdown

### For Cricket/World Cup Contests

- Create pages for each stage (Group, Super 8, Knockouts)
- Update frequently during group stages
- Create mini-contests for specific matches
- Include both stage winners and overall winners

### For FIFA Contests

- Group stage predictions first
- Knockout bracket predictions
- Separate leaderboards per stage
- Update brackets visually if possible

## 10. Troubleshooting

### Leaderboard Not Updating

- Clear browser cache
- Check Jekyll regenerated (look for file change timestamp)
- Verify markdown table syntax
- Ensure proper front matter in file

### Blog Post Not Appearing

- Check date isn't in future
- Verify file name format: `YYYY-MM-DD-title.md`
- Check front matter has `layout: post`
- Restart Jekyll if `_config.yml` changed

### Links Breaking

- Use absolute paths: `/prediction-contests/contest/page`
- Don't use relative `../` paths
- Verify permalink in front matter
- Check baseurl in `_config.yml`

## 11. Best Practices

### Commit Message Patterns

```bash
# Leaderboard updates
git commit -m "feat(leaderboard): update scores after divisional round"

# Blog posts
git commit -m "docs(blog): announce super bowl mini-contest"

# Predictions
git commit -m "feat(predictions): publish all 45 entries"

# Rules/info updates
git commit -m "docs(rules): clarify scoring system"

# Fixes
git commit -m "fix(leaderboard): correct player name spelling"
```

### Update Frequency

- **Leaderboard**: After each game/round
- **Blog posts**: Major milestones (rounds complete, deadlines, winners)
- **Predictions**: Once after entry deadline
- **Rules**: Before contest starts, rarely after

### Backup Strategy

- Git history is your backup
- Consider exporting leaderboard spreadsheet
- Save form responses from Google Forms
- Take screenshots of final results

---

## Quick Reference Card

Print this section for quick access:

```
┌─────────────────────────────────────────────────────────┐
│ PREDICTION CONTESTS - QUICK REFERENCE                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│ UPDATE LEADERBOARD                                       │
│ $ vim current-contest/leaderboard.md                     │
│ $ git add . && git commit -m "feat: update scores"       │
│ $ git push                                               │
│                                                           │
│ ADD BLOG POST                                            │
│ $ vim _posts/$(date +%Y-%m-%d)-title.md                  │
│ $ git add . && git commit -m "docs: add post"            │
│ $ git push                                               │
│                                                           │
│ ARCHIVE CONTEST                                          │
│ $ mv current/ past/current/                              │
│ $ vim past/hof.md         # Add winner                   │
│ $ vim past/index.md       # Add to list                  │
│ $ mkdir new-contest && cd new-contest                    │
│ $ touch index.md rules.md leaderboard.md predictions.md  │
│                                                           │
│ TEST LOCALLY                                             │
│ $ bundle exec jekyll serve                               │
│ $ open http://127.0.0.1:4000/prediction-contests/        │
│                                                           │
│ QUICK HELP                                               │
│ $ ./remind-me.sh          # Show options                 │
│ $ cat docs/QUICKSTART.md  # Full guide                   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Additional Resources

- **Full archiving details**: See `docs/archive-current-contest.md`
- **Quick start**: See `docs/QUICKSTART.md`
- **Helper script**: Run `./remind-me.sh` for common commands
- **Project overview**: See `CLAUDE.md`

---

**Last Updated**: January 2026
