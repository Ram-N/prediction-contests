# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based static website for hosting prediction contests for major sporting events (cricket world cups, FIFA, NFL). Built using the Clean Blog Jekyll theme and deployed to GitHub Pages.

**Tech Stack**: Jekyll (Ruby), Bootstrap 4, GitHub Pages

## Key Commands

```bash
# Install dependencies
bundle install

# Run local development server
bundle exec jekyll serve
# Site available at http://localhost:4000/prediction-contests

# Build static site
bundle exec jekyll build
```

## Site Configuration

- **Base URL**: `/prediction-contests` (configured for GitHub Pages at `ram-n.github.io/prediction-contests`)
- **Important**: All internal links and asset paths must respect the baseurl setting in `_config.yml`
- Jekyll pagination is set to 5 posts per page

## Content Architecture

### Current Contest Workflow

**Important Pattern**: The site maintains one "current" contest that is featured on the main home page. When a contest concludes:
1. The current contest directory (e.g., `t20-2024/`) is moved to `past/t20-2024/`
2. A new current contest directory is created for the next event
3. The home page and navigation are updated to point to the new current contest
4. Archived contests in `past/` remain accessible for historical reference

See `docs/archive-current-contest.md` for the complete archival process.

### Directory Structure

- `_posts/` - Blog posts announcing contest updates and results
- `t20-2024/` - Current active contest pages (example - varies by event)
- `past/` - Historical completed contests (ICC 2019, ICC 2023, FIFA 2022, NFL 2023, etc.)
- `_layouts/` - Jekyll templates (home, post, page, default)
- `_includes/` - Reusable components (scripts, analytics, read time)
- `_sass/` - SCSS styling
- `assets/` - Static assets
- `img/` - Images and backgrounds

### Contest Page Types

Each contest typically contains:
- `rules.md` - Contest rules, scoring system, deadlines
- `leaderboard.md` - Live scoring tables (uses Bootstrap tables with custom CSS classes)
- `predictions.md` - Submitted predictions
- `schedule.md` / `group.md` / `knockout.md` - Match schedules and brackets
- `news.md` - Contest announcements
- `groups/` - **PRIVATE/UNLISTED** group leaderboards (never link publicly)

### Leaderboard Tables

Leaderboard markdown files use custom table styling:
```markdown
{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Location | Score |
```

## Jekyll Configuration

### Front Matter Requirements

All content pages require YAML front matter:
```yaml
---
layout: page              # or 'post' for blog posts
title: Page Title
description: Description text
background: '/img/bg.jpg'  # Path relative to baseurl
permalink: "/custom-url"   # Optional custom URL
---
```

Blog posts additionally require:
```yaml
date: YYYY-MM-DD HH:MM:SS
subtitle: Post subtitle
```

### Plugins

- `jekyll-feed` - RSS feed generation
- `jekyll-paginate` - Post pagination
- `jekyll-sitemap` - Sitemap generation

## Development Notes

- Site uses kramdown for markdown processing
- Bootstrap 4.6.0 is included via npm dependencies
- No automated testing or CI/CD configured
- Site is manually updated with contest results and leaderboards
- Historical contests are archived in `past/` directory for reference

## Group Leaderboards - Privacy Policy

**IMPORTANT:** Group leaderboards are PRIVATE/UNLISTED pages.

- Group pages are located in `[contest]/groups/*.md` (e.g., `nfl-2025/groups/UB.md`, `nfl-2025/groups/Narmada.md`)
- These pages are accessible ONLY via direct URL
- **NEVER** link to group pages from any public pages including:
  - Contest landing pages (`past/[contest].md` or `[contest]/index.md`)
  - Main leaderboards
  - Blog posts
  - Navigation menus
  - README files
- Group URLs are shared privately with participants to check standings among friends
- While discoverable, they should not be advertised publicly

## Scoring and Updates

### Running the Scoring Script

The scoring script is located at `data/scripts/score_active_contest_predictions.py`.

**Always use `uv` to run Python scripts:**

```bash
cd data/scripts
uv run python score_active_contest_predictions.py --generate-blog
```

This will automatically update:
- Main leaderboard (`active-contest/leaderboard.md`)
- Group leaderboards (`active-contest/groups/*.md`) - if groups are configured
- Blog post announcing the update (`_posts/*.md`) - only with --generate-blog flag

**Files Updated:**
- `active-contest/leaderboard.md` - Overall contest standings
- `active-contest/groups/UB.md` - UB group standings (if configured)
- `active-contest/groups/Narmada.md` - NARMADA group standings (if configured)
- `_posts/YYYY-MM-DD-nfl-2025-after-X-games.md` - Blog post (if --generate-blog used)

### Important: Column Order in Leaderboards

**Game columns in leaderboards MUST match the order in the results.csv file.**

The script preserves the row order from `data/NFL-2025-results.csv`:
- If results.csv has: BUF-DEN, SF-SEA, HOU-NE, LAR-CHI, NE-DEN
- Then leaderboard columns appear in the same order (not alphabetically sorted)

This ensures that:
- The visual progression matches the chronological game order
- It's easier to track which games happened when
- The leaderboard reads naturally from left to right

### Blog Post Guidelines

**Blog post titles should be fun and engaging**, not technical:
- ✅ GOOD: "Chink leads after the Divisional Round"
- ✅ GOOD: "Go Seahawks! Tees takes the lead after 5 games"
- ❌ BAD: "Chink leads with a penalty of 2.6"
- ❌ BAD: "Updated standings - 5 games completed"

The title should mention:
1. Who is leading (by name)
2. After which round/game milestone

Keep it fun and personalized - readers should immediately know who's winning and at what stage of the contest.
