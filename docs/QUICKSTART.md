# Prediction Contests - Quick Start Guide

Quick reference for running and updating the prediction contests website.

## Running Locally

```bash
# 1. Install dependencies (first time only, or after Gemfile changes)
bundle install

# 2. Start local server
bundle exec jekyll serve

# 3. Open in browser
# http://localhost:4000/prediction-contests
```

**Note**: The site uses baseurl `/prediction-contests` so you must include it in the URL.

To auto-rebuild on changes:
```bash
bundle exec jekyll serve --livereload
```

## Creating a New Blog Post

Blog posts go in `_posts/` directory.

**File naming**: `YYYY-MM-DD-title-with-dashes.md`

```bash
# Example: Create a new post
touch _posts/2024-01-16-contest-announcement.md
```

**Post template**:
```markdown
---
layout: post
title: "Contest Opens for 2026 World Cup"
subtitle: "Make your predictions now!"
date: 2024-01-16 10:00:00
background: '/img/bg-post.jpg'
---

Your post content here in markdown...
```

## Creating/Updating Contest Pages

### Structure for New Contest

```bash
# Create new contest directory
mkdir -p new-contest-2026

# Common pages to create:
touch new-contest-2026/index.md
touch new-contest-2026/rules.md
touch new-contest-2026/leaderboard.md
touch new-contest-2026/predictions.md
touch new-contest-2026/schedule.md
```

### Page Template

```markdown
---
layout: page
title: Rules - 2026 Contest
description: Contest rules and scoring
background: '/img/stadium.jpg'
permalink: "/new-contest-2026/rules"
---

# Page content here
```

## Updating Leaderboards

Leaderboard tables use Bootstrap styling. Use this format:

```markdown
{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Location | Score | Status |
|:-----|:---------|------:|:-------|
| Player 1 | USA | 45 | Leading |
| Player 2 | India | 42 | 2nd |
```

**Important styling classes**:
- `{:.thead-dark .table-striped .table-bordered .table-sm }` - Add before table
- Use `:` in separator row for alignment (`:---` left, `:---:` center, `---:` right)

**Bold for winners**:
```markdown
| **Winner Name** | Location | **50** |
```

## Archiving Completed Contests

When a contest ends, archive it to keep the site organized:

```bash
# Move current contest to archive
mv current-contest/ past/current-contest/

# Update Hall of Fame and past contests index
vim past/hof.md
vim past/index.md
```

**Complete archiving guide**: See `docs/archive-current-contest.md` for full step-by-step process.

Quick reminder:
```bash
./remind-me.sh archive
```

## Common Tasks

### Add New Contest to Navigation

Edit `_includes/navbar.html` (if exists) or the main layout to add navigation links.

### Update Site Configuration

Edit `_config.yml`:
```yaml
title: T20 2024 WC Prediction Contest
description: Predict the outcomes of major sporting events
baseurl: "/prediction-contests"
url: "https://ram-n.github.io"
```

After changing `_config.yml`, restart the Jekyll server.

### Move Contest to Archives

```bash
# Move completed contest to past directory
mv current-contest/ past/current-contest/

# Update internal links in past/index.md
```

## Testing Before Deploy

```bash
# Build the site (generates _site/ directory)
bundle exec jekyll build

# Check for broken links or issues
# Navigate through pages at http://localhost:4000/prediction-contests
```

## Deploying to GitHub Pages

```bash
# Commit your changes
git add .
git commit -m "Update leaderboard for round 2"

# Push to GitHub (auto-deploys via GitHub Pages)
git push origin main
```

Site will be live at: https://ram-n.github.io/prediction-contests

## Quick Reference

| Task | Command/File |
|------|--------------|
| Start server | `bundle exec jekyll serve` |
| New blog post | `_posts/YYYY-MM-DD-title.md` |
| New contest page | `contest-name/page-name.md` |
| Update config | `_config.yml` (requires restart) |
| Leaderboard | Add table to `leaderboard.md` |
| Images | Place in `img/` directory |

## Troubleshooting

**Port already in use**:
```bash
# Kill existing Jekyll process
pkill -f jekyll

# Or use different port
bundle exec jekyll serve --port 4001
```

**Changes not showing**:
- Did you restart after editing `_config.yml`?
- Clear browser cache
- Check if file is in `_site/` after build

**Broken images/styles**:
- Verify baseurl is `/prediction-contests` in `_config.yml`
- Image paths should be `/img/filename.jpg` (relative to baseurl)

## File Locations Cheat Sheet

```
prediction-contests/
├── _config.yml          # Site configuration
├── _posts/              # Blog posts (YYYY-MM-DD-title.md)
├── _layouts/            # Page templates
├── _includes/           # Reusable components
├── img/                 # Images and backgrounds
├── t20-2024/            # Current contest pages
├── past/                # Historical contests
│   ├── icc2023/
│   ├── fifa2022/
│   └── hof.md           # Hall of Fame
└── index.html           # Homepage
```

## Tips

- Use markdown tables for leaderboards (easier to update than HTML)
- Keep contest images in `img/` with descriptive names
- Archive completed contests to `past/` to keep root clean
- Test locally before pushing to avoid broken production site
- Use `--livereload` during active development for instant updates
