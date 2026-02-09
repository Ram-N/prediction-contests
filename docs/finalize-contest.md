# Finalizing a Contest

This document describes the steps to finalize a contest after all games are complete.

## When to Use This Process

Use this checklist when:
- All games in the contest have been played
- Final scores have been calculated and published
- You're ready to officially close the contest

## Step-by-Step Finalization Process

### 1. Update the Final Blog Post

The final blog post (generated after the last game) needs several modifications:

**a) Update the blog post date**
- Change the date to today's date (or desired publication date)
- Format: `YYYY-MM-DD HH:MM:SS -0500`

**b) Move "Current Leader" section to the top and rename it**
- Change section title from "### Current Leader" to "## Top Predictors"
- Move this section to appear immediately after the main heading
- Update text to past tense:
  ```markdown
  ## Top Predictors

  **[Winner Name]** won the contest with a total penalty of **[score]**, followed by [2nd place name] ([score]) and [3rd place name] ([score]). Congratulations to our top three finishers!
  ```

**c) Make the winner's name bold in the table**
- In the leaderboard table, make the winner's row bold:
  ```markdown
  | 1 | **Winner Name** | **5.18** | ...
  ```

**d) Update section titles to past tense**
- "Current Leaderboard" → "Final Standings"
- Keep "Final Standings" as a section header above the table

**e) Remove "so far" and other in-progress language**
- "Perfect Predictions So Far" → "Perfect Predictions"
- "Standings after X games" → "Final Standings"
- Update any other language that implies the contest is ongoing

### 2. Update All Leaderboards

Add contest completion notice to all leaderboard files:

**Files to update:**
- Main leaderboard: `past/[contest-slug]/leaderboard.md`
- Group leaderboards: `past/[contest-slug]/groups/[group1].md`, `past/[contest-slug]/groups/[group2].md`, etc.

**What to add:**

In each file, add this text in the "Contest Status" section (or create one if it doesn't exist):

```markdown
## Contest Status

**This contest ended on [Month DD, YYYY]. [Winner Name] won with a score of [X.XX]!**

**X of X games completed** (0 remaining)
```

**Format:**
- Date only, no time (e.g., "February 08, 2026")
- Winner name should match the group's winner (Main = overall winner, each group = that group's winner)
- Score should match the winner's final score

**IMPORTANT - Group Privacy:**
- Group leaderboards are UNLISTED - accessible only via direct URL
- DO NOT link to group pages from any public pages (landing pages, main leaderboards, blog posts, etc.)
- Groups are private for participants to share with their friends only

### 3. Update Hall of Fame

Add the top three finishers to the Hall of Fame page.

**File to update:** `past/hof.md`

**What to change:**

Find the row for the current contest and update from:
```markdown
|2025| NFL 2025 Playoffs Main Contest | TBD (Super Bowl LIX not yet played)|
```

To:
```markdown
|2025| NFL 2025 Playoffs Main Contest | [Winner] (1st), [2nd Place] (2nd), [3rd Place] (3rd)|
```

**Format:**
- List top 3 finishers in order
- Include "(1st)", "(2nd)", "(3rd)" designations
- Use participant names as they appear in the leaderboard

### 4. Final Review

Before committing, verify:

- [ ] Blog post date is updated
- [ ] Blog post has "Top Predictors" section at the top
- [ ] Winner's name is bold in blog post table
- [ ] "so far" removed from all sections
- [ ] All leaderboards show contest end notice
- [ ] Contest end notices show correct winner for each group
- [ ] Hall of Fame is updated with top 3
- [ ] All past tense language is correct

### 5. Commit and Push

```bash
git add _posts/ past/
git commit -m "feat: finalize [Contest Name] with winners and final standings"
git push
```

## Example Commands

If using the scoring script, the final run should be:

```bash
cd data/scripts
uv run python score_active_contest_predictions.py --generate-blog
```

This generates the final blog post, which you'll then manually edit following steps 1-3 above.

## Notes

- The contest directory should already be in `past/[contest-slug]/` before finalizing
- If it's still in the root directory, follow the archival process first (see `docs/ARCHIVAL-PROCESS.md`)
- Keep the "Last updated" timestamp on leaderboards as-is (shows when scoring last ran)
- The blog post date can be different from the contest end date (blog posts timing of publication)
