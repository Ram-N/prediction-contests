# Prediction Processing Workflow

Step-by-step guide for processing predictions after the Google Form closes.

This workflow is repeated for each new contest.

---

## Overview

After your Google Form closes and you have all predictions:

1. Download predictions CSV from Google Forms
2. Store in `data/` folder
3. Create Google Contacts list for participants
4. Process predictions with Python script
5. Update predictions.md page with generated table

**Time Required:** ~15-20 minutes

---

## Step 1: Download Predictions from Google Forms

1. Open your Google Form
2. Click on **Responses** tab
3. Click the Google Sheets icon (green) to open responses in Sheets
4. In Google Sheets: **File → Download → Comma-separated values (.csv)**
5. Rename the downloaded file to match the contest (e.g., `NFL-2025-Predictions.csv`)

---

## Step 2: Store in Data Folder

Move the CSV to the `data/` folder:

```bash
# Navigate to project root
cd /home/ram/projects/prediction-contests

# Move downloaded file
mv ~/Downloads/NFL-2025-Predictions.csv data/

# Verify it's there
ls -la data/
```

**File naming convention:** `[CONTEST-NAME]-Predictions.csv`
- Examples: `NFL-2025-Predictions.csv`, `T20-2026-Predictions.csv`, `FIFA-2026-Predictions.csv`

---

## Step 3: Create Google Contacts List

Extract participant emails to create a labeled contact group for easy communication.

### 3a. Create Contacts CSV

Run the prediction processing script (see Step 4) which also creates a contacts CSV, OR manually create:

```bash
vim data/NFL-2025-Contacts.csv
```

**Format:**
```csv
Name,Email Address
Player Name,email@example.com
Another Player,another@example.com
```

### 3b. Import to Google Contacts

1. Go to [contacts.google.com](https://contacts.google.com)
2. Click **Import** (left sidebar)
3. Click **Select file** and choose `NFL-2025-Contacts.csv`
4. Click **Import**
5. After import completes:
   - Select all newly imported contacts (checkbox at top)
   - Click the **Label** icon (tag icon at top)
   - Create new label: "NFL 2025 Contest" (or appropriate name)
   - Click to apply the label

**Note:** Google Contacts automatically merges with existing contacts (no duplicates created).

**Use case:** This labeled group makes it easy to email all participants with updates, reminders, or results.

---

## Step 4: Process Predictions with Python Script

Use the Python script to clean predictions and generate markdown table.

### 4a. Update Script Configuration

Edit `data/scripts/process_predictions.py`:

```python
# Update these lines at the top of the script:
INPUT_FILE = '../NFL-2025-Predictions.csv'  # Your contest CSV
OUTPUT_FILE = '../NFL-2025-Predictions-Clean.csv'

# Update TEAM_ABBREV dictionary to match your contest teams
TEAM_ABBREV = {
    'Long Column Name from Google Form': 'ABBREV',
    # ... add all teams
}
```

**Important:** Match the exact column headers from your Google Form to team abbreviations.

### 4b. Run the Script

```bash
# Navigate to scripts folder
cd data/scripts

# Run with uv (uses virtual environment)
uv run python process_predictions.py
```

**Outputs:**
1. `data/NFL-2025-Predictions-Clean.csv` - Clean CSV without emails
2. `data/NFL-2025-Predictions-Table.md` - Markdown table ready for Jekyll
3. `data/NFL-2025-Contacts.csv` - Contacts CSV (if script generates it)

### 4c. Review the Output

The script will display:
- Number of predictions processed
- Team abbreviations used
- Preview of the markdown table

**Verify:**
- All 24 participants (or expected count) are included
- Team abbreviations are correct
- No email addresses are present
- Table formatting looks correct

---

## Step 5: Update Predictions Page

Copy the generated markdown table to your contest's predictions page.

### 5a. Open Predictions Page

```bash
vim nfl-2025/predictions.md
# OR whichever contest folder
```

### 5b. Replace Placeholder Content

Replace the "Check back after deadline" placeholder with:

```markdown
# NFL 2025-26 Playoff Contest Predictions

All submitted predictions are shown below. Predictions were submitted before the deadline on [DATE].

**Total Entries:** [COUNT] participants

## Confidence Scores

Each participant predicted confidence scores (1-100) for each team, where higher numbers indicate higher confidence of winning.

**Teams:**
- **AFC:** BUF (Buffalo Bills), DEN (Denver Broncos), ...
- **NFC:** SF (San Francisco 49ers), SEA (Seattle Seahawks), ...

---

[PASTE MARKDOWN TABLE FROM data/NFL-2025-Predictions-Table.md HERE]
```

### 5c. Test Locally

```bash
# Navigate to project root
cd /home/ram/projects/prediction-contests

# Start Jekyll server
bundle exec jekyll serve

# Visit in browser:
# http://127.0.0.1:4000/prediction-contests/nfl-2025/predictions
```

**Verify:**
- Table renders correctly with Bootstrap styling
- Columns are aligned
- No email addresses visible
- Team abbreviations are clear

---

## Step 6: Commit Changes

Once verified, commit to git:

```bash
# Stage files
git add data/NFL-2025-Predictions.csv
git add data/NFL-2025-Predictions-Clean.csv
git add data/NFL-2025-Predictions-Table.md
git add data/scripts/process_predictions.py  # if you modified it
git add nfl-2025/predictions.md

# Commit
git commit -m "feat(predictions): publish NFL 2025 participant predictions

- Add raw predictions CSV to data/
- Generate clean CSV without email addresses
- Update predictions.md with formatted table
- 24 total participants

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub Pages
git push origin main
```

---

## Complete Checklist

Use this checklist for each new contest:

- [ ] Download predictions CSV from Google Forms
- [ ] Move CSV to `data/` folder with proper naming
- [ ] Create contacts CSV (manually or via script)
- [ ] Import contacts to Google Contacts with label
- [ ] Update `process_predictions.py` with correct team mappings
- [ ] Run script with `uv run python process_predictions.py`
- [ ] Verify outputs (clean CSV, markdown table)
- [ ] Update `[contest]/predictions.md` with table
- [ ] Add team legend and metadata
- [ ] Test locally with Jekyll
- [ ] Verify table styling and accuracy
- [ ] Commit all files to git
- [ ] Push to GitHub Pages
- [ ] Verify live site shows predictions correctly

---

## Tips & Best Practices

### Team Abbreviations
- Use standard abbreviations (BUF, SF, etc.)
- Keep consistent with league conventions
- Document full team names in the predictions.md legend

### File Organization
```
data/
  ├── NFL-2025-Predictions.csv          # Original from Google Forms
  ├── NFL-2025-Predictions-Clean.csv    # Processed, no emails
  ├── NFL-2025-Predictions-Table.md     # Markdown table
  ├── NFL-2025-Contacts.csv             # For Google Contacts
  ├── NFL-2025-results.csv              # Game results (created later)
  └── scripts/
      └── process_predictions.py        # Processing script
```

### Privacy
- **NEVER** commit files with email addresses to git
- The raw predictions CSV (`NFL-2025-Predictions.csv`) contains emails
- Consider adding to `.gitignore` if concerned
- Only publish clean CSV and markdown table

### Script Modifications
- Keep a template version of `process_predictions.py`
- Copy and modify for each new contest
- Or use config file for team mappings

### Google Contacts Labels
- Use descriptive names: "NFL 2025 Contest", "T20 2026 Contest"
- Keep labels organized for multi-year contests
- Archive old labels after contest completes

---

## Troubleshooting

### Script Errors

**Error: ModuleNotFoundError: No module named 'pandas'**
```bash
# Install dependencies
cd data/scripts
uv pip install pandas tabulate
```

**Error: FileNotFoundError: No such file or directory**
- Check INPUT_FILE path in script
- Verify CSV file exists in data/ folder
- Use relative path from scripts/ folder: `../NFL-2025-Predictions.csv`

### Table Not Rendering

**Table shows as plain text:**
- Verify Bootstrap styling line is present: `{:.thead-dark .table-striped .table-bordered .table-sm }`
- Check Jekyll kramdown is processing markdown
- Ensure proper spacing before/after table

**Columns misaligned:**
- Verify column separator alignment row (`:---|------:|`)
- Check for extra/missing pipes `|`
- Ensure all rows have same number of columns

### Missing Participants

**Count doesn't match expected:**
- Check original CSV has all submissions
- Verify script processed all rows (check output count)
- Look for duplicate names (pandas may have dropped)
- Check for parsing errors in script output

---

## Related Documentation

- **Contest Management:** See `docs/CONTEST-MANAGEMENT.md` for overall contest workflow
- **Scoring System:** See `data/scripts/NFL_Predictions_Contest_2023.ipynb` for scoring algorithm
- **Quick Reference:** See `docs/QUICKSTART.md` for common commands

---

**Last Updated:** January 2026
