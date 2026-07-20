"""
Score FIFA 2026 ST-421 predictions.

Reads predictions + results → scores → generates color-coded markdown →
updates leaderboard.

Input:
  - active-contest/data/predictions/ST-421-Predictions-Clean.csv
  - active-contest/results/421-results.csv

Output:
  - active-contest/predictions-st421-table.md  (color-coded predictions table)
  - active-contest/leaderboard.md              (ST-421 column + ST-421 section)

Results CSV format (per team):
  Team, QF, SF, Finals
  where each stage value is:
    +1  = advanced / won that stage
    -1  = eliminated at that stage
    0   = did not participate (eliminated earlier)
    (empty) = not yet decided

Scoring:
  - Correct QF match pick:   +4 pts  (4 picks, max 16)
  - Correct Finalist pick:   +4 pts  (2 picks, max  8)  — SF1/SF2 columns
  - Correct Winner pick:     +8 pts  (1 pick,  max  8)
  Total max: 32 pts

Usage:
  uv run python score_fifa_st421.py
"""

import csv
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PREDICTIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "predictions", "ST-421-Predictions-Clean.csv"
)
RESULTS_CSV = os.path.join(PROJECT_ROOT, "active-contest", "results", "421-results.csv")
ST421_TABLE_MD = os.path.join(PROJECT_ROOT, "active-contest", "predictions-st421-table.md")
ST421_PAGE_MD = os.path.join(PROJECT_ROOT, "active-contest", "st-421.md")
LEADERBOARD_MD = os.path.join(PROJECT_ROOT, "active-contest", "leaderboard.md")
CANONICAL_LOCATIONS_CSV = os.path.join(
    PROJECT_ROOT, "active-contest", "data", "canonical-locations.csv"
)

# QF match definitions: (column_label_in_csv, team1_abbrev, team2_abbrev)
QF_MATCHES = [
    ("FRA v MAR", "FRA", "MAR"),
    ("ESP v BEL", "ESP", "BEL"),
    ("ENG v NOR", "ENG", "NOR"),
    ("ARG v SUI", "ARG", "SUI"),
]

FINALIST_COLS = ["SF1", "SF2"]
WINNER_COL = "Winner"

POINTS_QF = 4
POINTS_FINALIST = 4
POINTS_WINNER = 8

AI_NAMES = {"ChatGPT (AI)", "Claude (AI)", "Gemini (AI)"}

# Full country name → 3-letter abbreviation (as used in results CSV)
COUNTRY_ABBREV = {
    "France": "FRA", "Morocco": "MAR",
    "Spain": "ESP", "Belgium": "BEL",
    "England": "ENG", "Norway": "NOR",
    "Argentina": "ARG", "Switzerland": "SUI",
}


def abbrev(name):
    """Convert full country name to abbreviation, or return as-is if already abbrev."""
    return COUNTRY_ABBREV.get(name, name)

PLOT_BASE = "/prediction-contests/active-contest/data/plots/st421"
QF_PLOT_LINKS = {
    "FRA v MAR": f'<a href="#" class="r16-plot-link" data-plot="{PLOT_BASE}/st421_FRA_v_MAR.png">FRA v MAR</a>',
    "ESP v BEL": f'<a href="#" class="r16-plot-link" data-plot="{PLOT_BASE}/st421_ESP_v_BEL.png">ESP v BEL</a>',
    "ENG v NOR": f'<a href="#" class="r16-plot-link" data-plot="{PLOT_BASE}/st421_ENG_v_NOR.png">ENG v NOR</a>',
    "ARG v SUI": f'<a href="#" class="r16-plot-link" data-plot="{PLOT_BASE}/st421_ARG_v_SUI.png">ARG v SUI</a>',
}

ST421_PLOT_CSS_JS = """
<style>
.r16-plot-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}
.r16-plot-overlay.active { display: flex; }
.r16-plot-overlay img {
  max-width: 90%;
  max-height: 80%;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  background: #fff;
}
a.r16-plot-link {
  text-decoration: underline dotted;
  cursor: pointer;
  color: inherit;
}
</style>

<div class="r16-plot-overlay" id="plotOverlay" onclick="this.classList.remove('active')">
  <img id="plotImg" src="" alt="ST-421 prediction split">
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.r16-plot-link').forEach(function(a) {
    a.addEventListener('click', function(e) {
      e.preventDefault();
      document.getElementById('plotImg').src = this.dataset.plot;
      document.getElementById('plotOverlay').classList.add('active');
    });
  });
});
</script>
"""


# ---------------------------------------------------------------------------
# Timestamp
# ---------------------------------------------------------------------------


def get_timestamp():
    edt = ZoneInfo("America/New_York")
    now = datetime.now(edt)
    suffix = "EDT" if now.dst() else "EST"
    return now.strftime("%B %-d, %Y — %I:%M %p") + f" {suffix}"


# ---------------------------------------------------------------------------
# Parse results
# ---------------------------------------------------------------------------


def parse_results(filepath):
    """Parse 421-results.csv.

    Returns dict: team_abbrev -> {"QF": val, "SF": val, "Finals": val}
    where val is "+1", "-1", "0", or "" (unknown).
    """
    results = {}
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize field names (strip whitespace); skip None keys from trailing commas
        normalized_rows = [
            {k.strip(): (v or "").strip() for k, v in row.items() if k is not None}
            for row in reader
        ]
        team_col = reader.fieldnames[0].strip()

    for row in normalized_rows:
        team = row[team_col]
        qf = row.get("QF", "")
        sf = row.get("SF", "")
        finals = row.get("Finals", "")
        results[team] = {"QF": qf, "SF": sf, "Finals": finals}
    return results


def is_eliminated(team, results):
    """Return True if team is known to be eliminated (any stage = -1 or 0)."""
    r = results.get(team, {})
    for stage in ("QF", "SF", "Finals"):
        val = r.get(stage, "")
        if val in ("-1", "0"):
            return True
    return False


def get_qf_winner(match_label, t1, t2, results):
    """Return the winning team abbreviation for a QF match, or None if unknown."""
    if results.get(t1, {}).get("QF") == "+1":
        return t1
    if results.get(t2, {}).get("QF") == "+1":
        return t2
    return None


def get_finalist_status(team, results):
    """Return '+1' if team made the final, '-1'/'' otherwise."""
    return results.get(team, {}).get("SF", "")


def get_winner_status(team, results):
    """Return '+1' if team won the tournament, '-1'/'' otherwise."""
    return results.get(team, {}).get("Finals", "")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_entry(row, results):
    """Score a participant. Returns (total_pts, breakdown_dict)."""
    pts = 0
    breakdown = {}

    # QF picks
    qf_pts = 0
    for col, t1, t2 in QF_MATCHES:
        pick = abbrev(row[col].strip())
        winner = get_qf_winner(col, t1, t2, results)
        if winner and pick == winner:
            qf_pts += POINTS_QF
    pts += qf_pts
    breakdown["QF"] = qf_pts

    # Finalist picks (SF1, SF2)
    sf_pts = 0
    for col in FINALIST_COLS:
        pick = abbrev(row[col].strip())
        status = get_finalist_status(pick, results)
        if status == "+1":
            sf_pts += POINTS_FINALIST
    pts += sf_pts
    breakdown["SF"] = sf_pts

    # Winner pick
    winner_pick = abbrev(row[WINNER_COL].strip())
    winner_status = get_winner_status(winner_pick, results)
    win_pts = POINTS_WINNER if winner_status == "+1" else 0
    pts += win_pts
    breakdown["Winner"] = win_pts

    return pts, breakdown


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def style_qf_pick(pick_raw, match_label, t1, t2, results):
    """Color-code a QF pick. pick_raw may be full name or abbreviation."""
    pick = abbrev(pick_raw)
    winner = get_qf_winner(match_label, t1, t2, results)
    if winner is None:
        return pick  # result unknown
    if pick == winner:
        return f'<span style="color:green"><b>{pick}</b></span>'
    else:
        return f'<span style="color:red"><s>{pick}</s></span>'


def style_finalist_pick(pick_raw, results):
    """Color-code a finalist (SF1/SF2) pick.

    Green  = team reached the final (SF=+1), regardless of Finals result.
    Red    = team confirmed did NOT reach the final (eliminated in QF or SF).
    Plain  = result still pending.

    Note: do NOT use is_eliminated() here — a finalist like Argentina that
    lost the final has Finals=-1, which would incorrectly trigger red.
    """
    pick = abbrev(pick_raw)
    status = get_finalist_status(pick, results)
    if status == "+1":
        return f'<span style="color:green"><b>{pick}</b></span>'
    r = results.get(pick, {})
    qf_val = r.get("QF", "")
    sf_val = r.get("SF", "")
    if qf_val in ("-1", "0") or sf_val in ("-1", "0"):
        return f'<span style="color:red"><s>{pick}</s></span>'
    return pick  # result still pending


def style_winner_pick(pick_raw, results):
    """Color-code the winner pick (bold always, strikethrough if eliminated)."""
    pick = abbrev(pick_raw)
    if is_eliminated(pick, results):
        return f'<span style="color:red"><s><b>{pick}</b></s></span>'
    status = get_winner_status(pick, results)
    if status == "+1":
        return f'<span style="color:green"><b>{pick}</b></span>'
    return f"**{pick}**"  # still alive


# ---------------------------------------------------------------------------
# Load predictions
# ---------------------------------------------------------------------------


def load_canonical_locations():
    mapping = {}
    if os.path.exists(CANONICAL_LOCATIONS_CSV):
        with open(CANONICAL_LOCATIONS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row["Name"].strip()
                if name:
                    mapping[name] = row["Location"].strip()
    return mapping


def load_predictions(canonical_locations):
    """Load predictions CSV, apply canonical locations. Returns list of dicts."""
    entries = []
    with open(PREDICTIONS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = dict(row)
            name = entry["Name"].strip()
            if name in AI_NAMES:
                entry["Location"] = "🤖 AI"
            else:
                loc = canonical_locations.get(name)
                if loc:
                    entry["Location"] = loc
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Generate ST-421 table (predictions-st421-table.md)
# ---------------------------------------------------------------------------


def generate_st421_table(entries, results):
    """Generate color-coded ST-421 predictions table."""
    lines = []

    # Header with clickable QF columns
    qf_headers = [QF_PLOT_LINKS[col] for col, _, _ in QF_MATCHES]
    col_headers = ["Name", "Location"] + qf_headers + ["Finalist 1", "Finalist 2", "Winner"]
    header = "| " + " | ".join(col_headers) + " |"
    sep = "|" + "|".join(["---"] * len(col_headers)) + "|"
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    for entry in entries:
        name = entry["Name"].strip()
        location = entry["Location"].strip()

        # QF picks
        qf_cells = []
        for col, t1, t2 in QF_MATCHES:
            pick = entry[col].strip()
            qf_cells.append(style_qf_pick(pick, col, t1, t2, results))

        # Finalist picks
        sf_cells = [style_finalist_pick(entry[c].strip(), results) for c in FINALIST_COLS]

        # Winner pick
        win_cell = style_winner_pick(entry[WINNER_COL].strip(), results)

        all_cells = qf_cells + sf_cells + [win_cell]
        lines.append(f"| {name} | {location} | " + " | ".join(all_cells) + " |")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Generate ST-421 leaderboard section
# ---------------------------------------------------------------------------


def count_qf_decided(results):
    """Count how many QF matches have a known result."""
    count = 0
    for _, t1, t2 in QF_MATCHES:
        if get_qf_winner("", t1, t2, results) is not None:
            count += 1
    return count


def build_st421_leaderboard_section(entries, results, scores, timestamp):
    """Build the ## ST-421 Leaderboard section for leaderboard.md."""
    num_qf = count_qf_decided(results)

    lines = []
    lines.append("## ST-421 Leaderboard")
    lines.append("")
    lines.append(f"**{num_qf} of 4 QF matches decided.** Scoring: QF pick = {POINTS_QF} pts, Finalist pick = {POINTS_FINALIST} pts, Winner = {POINTS_WINNER} pts. Max: 32 pts.")
    lines.append("")

    if num_qf > 0:
        qf_results = []
        for col, t1, t2 in QF_MATCHES:
            winner = get_qf_winner(col, t1, t2, results)
            if winner:
                loser = t2 if winner == t1 else t1
                qf_results.append(f"**{winner}** beat {loser}")
        if qf_results:
            lines.append("QF results: " + ", ".join(qf_results) + ".")
            lines.append("")

    lines.append("**Color coding:**")
    lines.append('- <span style="color:green"><b>Green/Bold</b></span> = Correct pick')
    lines.append('- <span style="color:red"><s>Red/Strikethrough</s></span> = Wrong pick / eliminated')
    lines.append("- Plain text = Result pending")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Sorted table
    scored = []
    for entry in entries:
        name = entry["Name"].strip()
        pts = scores.get(name, 0)
        scored.append((pts, name, entry))
    scored.sort(key=lambda x: (-x[0], x[1].lower()))

    # Assign medal emojis by score tier (top 3 unique scores)
    unique_scores = sorted({pts for pts, _, _ in scored}, reverse=True)
    medal_map = {}
    if len(unique_scores) >= 1:
        medal_map[unique_scores[0]] = "🏆"
    if len(unique_scores) >= 2:
        medal_map[unique_scores[1]] = "🥈"
    if len(unique_scores) >= 3:
        medal_map[unique_scores[2]] = "🥉"

    qf_link_headers = [QF_PLOT_LINKS[col] for col, _, _ in QF_MATCHES]
    col_headers = ["Name", "Location", "Pts"] + qf_link_headers + ["Finalist 1", "Finalist 2", "Winner"]
    header = "| " + " | ".join(col_headers) + " |"
    sep = "|------|----------|:---:|" + "|".join(["---"] * (len(QF_MATCHES) + 3)) + "|"

    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append(header)
    lines.append(sep)

    for pts, name, entry in scored:
        location = entry["Location"].strip()
        medal = medal_map.get(pts, "")
        display_name = f"{name} {medal}" if medal else name
        qf_cells = [style_qf_pick(entry[col].strip(), col, t1, t2, results) for col, t1, t2 in QF_MATCHES]
        sf_cells = [style_finalist_pick(entry[c].strip(), results) for c in FINALIST_COLS]
        win_cell = style_winner_pick(entry[WINNER_COL].strip(), results)
        all_cells = qf_cells + sf_cells + [win_cell]
        lines.append(f"| {display_name} | {location} | {pts} | " + " | ".join(all_cells) + " |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(ST421_PLOT_CSS_JS)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Update leaderboard.md
# ---------------------------------------------------------------------------


def update_leaderboard(leaderboard_path, scores, entries, results, timestamp):
    with open(leaderboard_path, "r") as f:
        content = f.read()

    canonical_locations = load_canonical_locations()
    lines = content.split("\n")
    new_lines = []
    updated_top_timestamp = False
    in_st421_section = False
    found_st421_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Update the top-level timestamp
        if line.startswith("*Last updated:") and not updated_top_timestamp:
            new_lines.append(f"*Last updated: {timestamp}*")
            updated_top_timestamp = True
            i += 1
            continue

        # Update ST-421 status row (rounds summary — not the overall table header)
        if "| ST-421 |" in line and "| Name |" not in line and "| GS |" not in line:
            num_qf = count_qf_decided(results)
            has_sf = any(results.get(t, {}).get("SF") in ("+1", "-1") for _, t1, t2 in QF_MATCHES for t in (t1, t2))
            has_final = any(results.get(t, {}).get("Finals") == "+1" for _, t1, t2 in QF_MATCHES for t in (t1, t2))
            if has_final:
                status = "✅ Complete"
            elif has_sf:
                status = "🔄 SF in progress"
            elif num_qf == 4:
                status = "🔄 QF complete, SF upcoming"
            elif num_qf > 0:
                status = f"🔄 QF in progress ({num_qf}/4)"
            else:
                status = "⏳ Not started"
            new_lines.append(
                f"| ST-421 | [Quarterfinals → Semifinals → Final ↓](#st-421-leaderboard) | {status} |"
            )
            i += 1
            continue

        # Update overall leaderboard table (Name | Location | GS | R32 | R16 | ST-421 | Total | picks...)
        if "| Name |" in line and "| GS |" in line and "| ST-421 |" in line:
            # Replace header with extended version including ST-421 picks
            new_lines.append(
                "| Name | Location | GS | R32 | R16 | ST-421"
                " | FRA-MAR | ESP-BEL | ENG-NOR | ARG-SUI | SF1 | SF2 | 🏆 | Total |"
            )
            i += 1
            if i < len(lines) and lines[i].startswith("|") and "---" in lines[i]:
                new_lines.append(
                    "|------|----------|:---:|:---:|:---:|:---:"
                    "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
                )
                i += 1
            table_rows = []
            while i < len(lines) and lines[i].startswith("|"):
                table_rows.append(lines[i])
                i += 1
            # Extract prior-round scores from the individual sections so we can
            # restore any participant who was dropped due to a name mismatch
            prior_scores = {
                "GS": extract_round_scores(lines, "Group Stage Leaderboard"),
                "R32": extract_round_scores(lines, "Round of 32 Leaderboard"),
                "R16": extract_round_scores(lines, "Round of 16 Leaderboard"),
            }
            picks_by_name = {
                entry["Name"].strip(): {
                    col: entry.get(col, "").strip()
                    for col in [m[0] for m in QF_MATCHES] + FINALIST_COLS + [WINNER_COL]
                }
                for entry in entries
            }
            new_lines.extend(rebuild_overall_table(
                table_rows, scores, canonical_locations, prior_scores,
                picks_by_name=picks_by_name, results=results,
            ))
            continue

        # Replace ST-421 section
        if "## ST-421 Leaderboard" in line:
            found_st421_section = True
            in_st421_section = True
            new_lines.append(build_st421_leaderboard_section(entries, results, scores, timestamp))
            i += 1
            # Skip old section until next ## heading or end of file
            while i < len(lines):
                if lines[i].startswith("## ") and "ST-421" not in lines[i]:
                    break
                i += 1
            continue

        new_lines.append(line)
        i += 1

    result = "\n".join(new_lines)

    # If no existing ST-421 section, append it before the final newline
    if not found_st421_section:
        result = result.rstrip("\n")
        result += "\n\n" + build_st421_leaderboard_section(entries, results, scores, timestamp) + "\n"

    return result


def extract_round_scores(lines, section_heading):
    """Extract name -> pts from a leaderboard section identified by its ## heading.
    The Pts column is the 3rd pipe-delimited cell (after Name and Location).
    Medal emojis (🏆 🥈 🥉) are stripped from names.
    """
    MEDALS = ("🏆 ", "🥈 ", "🥉 ", "🏅 ")
    scores = {}
    in_section = False
    past_header = False
    for line in lines:
        if f"## {section_heading}" in line:
            in_section = True
            past_header = False
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue
        name = cells[1]
        # Skip header/separator rows
        if not name or name in ("Name", "---") or "---" in name:
            past_header = True
            continue
        if not past_header:
            continue
        pts_str = cells[3]
        # Strip medal emojis
        for medal in MEDALS:
            name = name.replace(medal, "")
        name = name.strip()
        try:
            scores[name] = int(pts_str)
        except ValueError:
            pass
    return scores


def rebuild_overall_table(table_rows, st421_scores, location_map=None, prior_scores=None,
                          picks_by_name=None, results=None):
    """Parse overall table rows, update ST-421/Total, re-sort by Total desc.

    prior_scores: dict with keys 'GS', 'R32', 'R16' mapping name -> pts,
    used to restore participants who may have been dropped due to prior name mismatches.
    picks_by_name: dict mapping name -> {col: pick_raw} for QF/SF/Winner columns.
    results: results dict (from parse_results) for color-coding picks.
    """
    if location_map is None:
        location_map = {}
    if prior_scores is None:
        prior_scores = {}

    parsed = []
    seen_names = set()
    for row in table_rows:
        cells = [c.strip() for c in row.split("|")]
        # cells: ['', 'Name', 'Location', 'GS', 'R32', 'R16', 'ST-421', 'Total', '']
        if len(cells) < 8:
            continue
        name = cells[1]
        location = location_map.get(name, cells[2])
        gs = cells[3]
        r32 = cells[4]
        r16 = cells[5]
        st421_cell = cells[6]

        # Update ST-421 from computed scores
        st421 = str(st421_scores[name]) if name in st421_scores else st421_cell

        # Compute total
        total = 0
        for val in [gs, r32, r16, st421]:
            if val not in ("-", ""):
                try:
                    total += int(val)
                except ValueError:
                    pass

        parsed.append((name, location, gs, r32, r16, st421, str(total), total))
        seen_names.add(name)

    # Add participants not already in the overall table.
    # For ST-421 participants, look up their prior round scores from the
    # individual round sections so they can be restored even if dropped.
    gs_scores = prior_scores.get("GS", {})
    r32_scores = prior_scores.get("R32", {})
    r16_scores = prior_scores.get("R16", {})

    for name, st421_pts in st421_scores.items():
        if name in seen_names:
            continue
        location = location_map.get(name, "")
        gs = str(gs_scores[name]) if name in gs_scores else "-"
        r32 = str(r32_scores[name]) if name in r32_scores else "-"
        r16 = str(r16_scores[name]) if name in r16_scores else "-"
        st421 = str(st421_pts)
        total = st421_pts
        for val in [gs, r32, r16]:
            if val != "-":
                try:
                    total += int(val)
                except ValueError:
                    pass
        parsed.append((name, location, gs, r32, r16, st421, str(total), total))
        seen_names.add(name)

    # Only include participants who have entries in all currently active rounds
    round_indices = {"GS": 2, "R32": 3, "R16": 4, "ST-421": 5}
    active_rounds = [idx for label, idx in round_indices.items()
                     if any(row[idx] not in ("-", "") for row in parsed)]

    parsed = [row for row in parsed if all(row[idx] not in ("-", "") for idx in active_rounds)]

    parsed.sort(key=lambda x: (-x[7], x[0].lower()))

    result_lines = []
    for name, location, gs, r32, r16, st421, total_str, _ in parsed:
        pick_cells = ""
        if picks_by_name is not None and results is not None:
            picks = picks_by_name.get(name, {})
            cells_list = []
            for col, t1, t2 in QF_MATCHES:
                pick_raw = picks.get(col, "")
                cells_list.append(style_qf_pick(pick_raw, col, t1, t2, results) if pick_raw else "")
            for sf_col in FINALIST_COLS:
                pick_raw = picks.get(sf_col, "")
                cells_list.append(style_finalist_pick(pick_raw, results) if pick_raw else "")
            pick_raw = picks.get(WINNER_COL, "")
            cells_list.append(style_winner_pick(pick_raw, results) if pick_raw else "")
            pick_cells = " | ".join(cells_list)

        if pick_cells:
            result_lines.append(
                f"| {name} | {location} | {gs} | {r32} | {r16} | {st421} | {pick_cells} | {total_str} |"
            )
        else:
            result_lines.append(
                f"| {name} | {location} | {gs} | {r32} | {r16} | {st421} | {total_str} |"
            )
    return result_lines


# ---------------------------------------------------------------------------
# Generate standalone st-421.md page
# ---------------------------------------------------------------------------


def generate_st421_page(entries, results, scores, timestamp):
    """Generate the full st-421.md standalone page."""
    num_qf = count_qf_decided(results)
    human_count = sum(1 for e in entries if e["Name"] not in AI_NAMES)
    ai_count = len(entries) - human_count

    lines = []
    lines.append("---")
    lines.append("layout: page")
    lines.append('title: "ST-421 Leaderboard"')
    lines.append('description: "FIFA World Cup 2026 — Quarterfinals to Final predictions and scores"')
    lines.append("background: '/img/soccer/421-banner.png'")
    lines.append('permalink: "/fifa-2026/st-421"')
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# FIFA World Cup 2026 — ST-421")
    lines.append("")
    lines.append(f"*Last updated: {timestamp}*")
    lines.append("")
    lines.append(f"**{len(entries)} participants** ({human_count} humans + {ai_count} AI) picked the winners of each quarterfinal, then 2 finalists and the overall winner.")
    lines.append("")
    lines.append("**Scoring:** Correct QF pick = 4 pts · Correct Finalist = 4 pts · Correct Winner = 8 pts · **Max: 32 pts**")
    lines.append("")

    if num_qf > 0:
        qf_results = []
        for col, t1, t2 in QF_MATCHES:
            winner = get_qf_winner(col, t1, t2, results)
            if winner:
                loser = t2 if winner == t1 else t1
                qf_results.append(f"**{winner}** beat {loser}")
        lines.append(f"**{num_qf} of 4 QF matches decided:** " + ", ".join(qf_results) + ".")
        lines.append("")

    lines.append("**Color coding:**")
    lines.append('- <span style="color:green"><b>Green/Bold</b></span> = Correct pick')
    lines.append('- <span style="color:red"><s>Red/Strikethrough</s></span> = Wrong pick / eliminated')
    lines.append("- Plain text = Result pending")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Sorted leaderboard table
    scored = sorted(
        ((scores.get(e["Name"].strip(), 0), e["Name"].strip(), e) for e in entries),
        key=lambda x: (-x[0], x[1].lower())
    )

    # Medal emojis by score tier
    unique_scores = sorted({pts for pts, _, _ in scored}, reverse=True)
    medal_map = {}
    if len(unique_scores) >= 1:
        medal_map[unique_scores[0]] = "🏆"
    if len(unique_scores) >= 2:
        medal_map[unique_scores[1]] = "🥈"
    if len(unique_scores) >= 3:
        medal_map[unique_scores[2]] = "🥉"

    qf_link_headers = [QF_PLOT_LINKS[col] for col, _, _ in QF_MATCHES]
    col_headers = ["Name", "Location", "Pts"] + qf_link_headers + ["Finalist 1", "Finalist 2", "Winner"]
    lines.append("{:.thead-dark .table-striped .table-bordered .table-sm .table-searchable }")
    lines.append("| " + " | ".join(col_headers) + " |")
    lines.append("|------|----------|:---:|" + "|".join(["---"] * (len(QF_MATCHES) + 3)) + "|")

    for pts, name, entry in scored:
        location = entry["Location"].strip()
        medal = medal_map.get(pts, "")
        display_name = f"{name} {medal}" if medal else name
        qf_cells = [style_qf_pick(entry[col].strip(), col, t1, t2, results) for col, t1, t2 in QF_MATCHES]
        sf_cells = [style_finalist_pick(entry[c].strip(), results) for c in FINALIST_COLS]
        win_cell = style_winner_pick(entry[WINNER_COL].strip(), results)
        all_cells = qf_cells + sf_cells + [win_cell]
        lines.append(f"| {display_name} | {location} | {pts} | " + " | ".join(all_cells) + " |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("[Back to Contest Home](/prediction-contests/fifa-2026/) | [Leaderboard](/prediction-contests/fifa-2026/leaderboard) | [All Predictions](/prediction-contests/fifa-2026/predictions)")
    lines.append("")
    lines.append(ST421_PLOT_CSS_JS)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading canonical locations...")
    canonical_locations = load_canonical_locations()

    print("Reading ST-421 predictions...")
    entries = load_predictions(canonical_locations)
    human_count = sum(1 for e in entries if e["Name"] not in AI_NAMES)
    print(f"  {len(entries)} entries ({human_count} humans + {len(entries) - human_count} AI)")

    print("Reading 421 results...")
    results = parse_results(RESULTS_CSV)
    print(f"  {len(results)} teams with results:")
    for team, r in results.items():
        print(f"    {team}: QF={r['QF'] or '?'}, SF={r['SF'] or '?'}, Finals={r['Finals'] or '?'}")

    print("\nScoring participants...")
    timestamp = get_timestamp()

    scores = {}
    for entry in entries:
        name = entry["Name"].strip()
        pts, breakdown = score_entry(entry, results)
        scores[name] = pts

    # Summary
    scored_list = sorted(scores.items(), key=lambda x: (-x[1], x[0].lower()))
    print(f"\n{'Name':<30} {'ST-421':>7}")
    print("-" * 40)
    for name, pts in scored_list[:15]:
        print(f"  {name:<30} {pts:>5}")
    if len(scored_list) > 15:
        print(f"  ... and {len(scored_list) - 15} more")

    print(f"\nWriting {ST421_TABLE_MD}...")
    table = generate_st421_table(entries, results)
    with open(ST421_TABLE_MD, "w") as f:
        f.write(table)
    print("  Done")

    print(f"Writing {ST421_PAGE_MD}...")
    page_content = generate_st421_page(entries, results, scores, timestamp)
    with open(ST421_PAGE_MD, "w") as f:
        f.write(page_content)
    print("  Done")

    print(f"Updating {LEADERBOARD_MD}...")
    lb_content = update_leaderboard(LEADERBOARD_MD, scores, entries, results, timestamp)
    with open(LEADERBOARD_MD, "w") as f:
        f.write(lb_content)
    print("  Done")

    print(f"\nTimestamp: {timestamp}")
    print("All files updated successfully.")


if __name__ == "__main__":
    main()
