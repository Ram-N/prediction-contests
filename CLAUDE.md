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
