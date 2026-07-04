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

## Folder Structure

```
prediction-contests/
├── active-contest/                    # JEKYLL PAGES + CONTEST WORKING DATA
│   ├── *.md                           # Served pages (index, rules, leaderboard, etc.)
│   ├── predictions-*-table.md         # Generated tables (must stay here for include_relative)
│   ├── groups/                        # Private group leaderboards
│   ├── results/                       # Hand-edited results CSVs (no PII)
│   └── data/                          # Non-PII contest working data (committed)
│       ├── predictions/               # Clean prediction CSVs (Email column stripped)
│       ├── matches/                   # Match structure (r16-matches.csv, r32-matches.csv)
│       ├── schedule/                  # Tournament schedules
│       ├── ai-predictions/            # AI model prediction docs
│       ├── plots/                     # Generated visualizations (PNGs)
│       ├── prompts/                   # AI prompt documents
│       └── canonical-locations.csv    # Name→Location mapping (no emails)
│
├── scripts/                           # ALL PROCESSING SCRIPTS (committed)
│   ├── score_fifa_*.py                # Scoring scripts
│   ├── generate_*.py                  # Table/plot generators
│   ├── process_*.py                   # Data processing
│   ├── apps-script/                   # Google Apps Scripts (.gs files)
│   ├── contest_config.json            # Config files
│   └── archive/                       # Older/superseded scripts
│
├── pii-data/                          # PII DATA — NEVER COMMITTED (gitignored)
│   ├── FIFA-2026/
│   │   ├── contacts/                  # GroupStage-Contacts.csv, LR-421-Contacts.csv
│   │   ├── form-responses/            # Raw Google Form exports (.csv, .xlsx)
│   │   ├── raw-predictions/           # Prediction CSVs WITH Email column
│   │   ├── canonical-names.csv        # Has emails — PII
│   │   └── email-reconciliation.csv   # Has emails — PII
│   ├── NFL-2025/                      # Same pattern per contest
│   ├── T20-2026/                      # Same pattern per contest
│   └── contacts/                      # Cross-contest Google Contacts exports
│
├── past/                              # Archived completed contests (committed)
├── _posts/                            # Blog posts
├── img/                               # Images by sport
├── bin/                               # Shell utilities
├── templates/                         # New contest templates
├── docs/                              # Operational documentation
└── _config.yml
```

## Decision Rules — Where Does This File Go?

| Question | Answer |
|----------|--------|
| Has email addresses or phone numbers? | → `pii-data/` |
| Jekyll page with front matter? | → `active-contest/` root |
| Generated table used by `include_relative`? | → `active-contest/` root |
| Results CSV (team codes, no PII)? | → `active-contest/results/` |
| Clean predictions (no Email column)? | → `active-contest/data/predictions/` |
| Match structure, schedule, reference data? | → `active-contest/data/` |
| Generated plots/charts? | → `active-contest/data/plots/` |
| Python script? | → `scripts/` |
| Raw form response from Google? | → `pii-data/CONTEST/form-responses/` |
| Contact list with emails? | → `pii-data/CONTEST/contacts/` |

## Content Architecture

### Current Contest Workflow

**Important Pattern**: The site maintains one "current" contest that is featured on the main home page. When a contest concludes:
1. The current contest directory (e.g., `t20-2024/`) is moved to `past/t20-2024/`
2. A new current contest directory is created for the next event
3. The home page and navigation are updated to point to the new current contest
4. Archived contests in `past/` remain accessible for historical reference

See `docs/archive-current-contest.md` for the complete archival process.

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

**Leaderboard table rules (MUST follow every time you update a leaderboard):**

1. **No index column**: Never include a `#` or index column. The first column should be `Name`.
2. **Column order**: Always put `Name`, `Location`, `Pts` (or `Total`) as the first columns, then remaining columns after.
   - Group-stage table: `Name | Location | Pts | A | B | C | ... | L | WOTC%`
   - Overall leaderboard: `Name | GS | R32 | R16 | ST-421 | Total`
3. **Timestamp format**: Every leaderboard must have a `*Last updated: ...*` line. Use the format:
   `*Last updated: June 26, 2026 — 02:15 PM EDT*` (Month DD, YYYY — HH:MM AM/PM EDT/EST).
   Update this timestamp every time you modify the file.

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

### FIFA 2026 Group Stage Scoring

The group stage scoring script is at `scripts/score_fifa_group_stage.py`.

```bash
cd scripts
uv run python score_fifa_group_stage.py
```

**Workflow:**
1. User updates `active-contest/results/group-stage-results.csv` with new results
2. Run the script — it reads predictions + results, scores everything, generates output
3. Review the updated files and commit

**Input files:**
- `active-contest/data/predictions/GroupStage-Predictions-Clean.csv` — participant predictions
- `active-contest/results/group-stage-results.csv` — results (`TEAM, +1/+3/-1`)

**Output files:**
- `active-contest/group-stage.md` — full color-coded predictions table
- `active-contest/leaderboard.md` — updates GS column, Total, and GS detail section

**Results CSV format:** Each line is `TEAM_ABBREV, RESULT` where result is `+1` (qualified top-2), `+3` (3rd place), or `-1` (eliminated). Blank lines separate groups (cosmetic only).

**Scoring:** +1 for each correct top-2 pick, +1 for each correct 3rd-place pick.

### General Scoring Script (NFL etc.)

The general scoring script is at `scripts/score_active_contest_predictions.py`.

```bash
cd scripts
uv run python score_active_contest_predictions.py --generate-blog
```

**Files Updated:**
- `active-contest/leaderboard.md` - Overall contest standings
- `active-contest/groups/UB.md` - UB group standings (if configured)
- `active-contest/groups/Narmada.md` - NARMADA group standings (if configured)
- `_posts/YYYY-MM-DD-nfl-2025-after-X-games.md` - Blog post (if --generate-blog used)

### Blog Post Guidelines

**Blog post titles should be fun and engaging**, not technical:
- GOOD: "Chink leads after the Divisional Round"
- GOOD: "Go Seahawks! Tees takes the lead after 5 games"
- BAD: "Chink leads with a penalty of 2.6"
- BAD: "Updated standings - 5 games completed"

The title should mention:
1. Who is leading (by name)
2. After which round/game milestone

Keep it fun and personalized - readers should immediately know who's winning and at what stage of the contest.
