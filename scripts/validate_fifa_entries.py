"""Validate FIFA 2026 Group Stage prediction contest entries."""

import csv
import re
import sys
from collections import Counter

DEFAULT_CSV = "active-contest/FIFA Group Stage (Responses) - Form Responses 1.csv"

# Normalize team name variants (3rd-place header spelling → R32 header spelling)
TEAM_NAME_NORMALIZE = {
    "Türkiye": "Turkey",
}


def parse_headers(headers):
    """Extract group and team info from CSV headers.

    Returns:
        r32_cols: dict of {col_index: (group_letter, team_name)}
        third_cols: dict of {col_index: (group_letter, team_name)}
    """
    r32_cols = {}
    for i in range(4, 52):
        m = re.search(r"Group (\w) \[(.+)\]", headers[i])
        if m:
            r32_cols[i] = (m.group(1), m.group(2))

    third_cols = {}
    for i in range(52, 100):
        m = re.search(r"\[(\w)-(.+)\]", headers[i])
        if m:
            team = m.group(2)
            team = TEAM_NAME_NORMALIZE.get(team, team)
            third_cols[i] = (m.group(1), team)

    return r32_cols, third_cols


def validate_entry(row, r32_cols, third_cols):
    """Validate a single entry. Returns list of error strings."""
    errors = []

    # --- R32 picks ---
    r32_by_group = {}  # group -> list of team names
    for col, (group, team) in r32_cols.items():
        if row[col].strip():
            r32_by_group.setdefault(group, []).append(team)

    total_r32 = sum(len(teams) for teams in r32_by_group.values())

    for group in sorted(r32_by_group):
        count = len(r32_by_group[group])
        if count != 2:
            teams_str = ", ".join(r32_by_group[group])
            errors.append(
                f"Group {group} has {count} R32 pick(s) (expected 2): {teams_str}"
            )

    if total_r32 != 24:
        errors.append(f"{total_r32} total R32 picks (expected 24)")

    # --- 3rd place picks ---
    third_by_group = {}  # group -> list of team names
    third_rankings = []  # list of (rank_int, team)
    third_teams_set = set()

    for col, (group, team) in third_cols.items():
        val = row[col].strip()
        if not val:
            continue
        third_by_group.setdefault(group, []).append(team)
        third_teams_set.add(team)

        # Parse ranking number from "3rd Place-N"
        rank_match = re.search(r"-(\d+)", val)
        if rank_match:
            third_rankings.append((int(rank_match.group(1)), team))

    total_third = sum(len(teams) for teams in third_by_group.values())

    if total_third != 8:
        errors.append(f"{total_third} third-place picks (expected 8)")

    # Check: max 1 pick per group
    dup_groups = []
    for group in sorted(third_by_group):
        if len(third_by_group[group]) > 1:
            teams_str = ", ".join(third_by_group[group])
            dup_groups.append(group)
            errors.append(
                f"Group {group} has {len(third_by_group[group])} third-place picks "
                f"(max 1): {teams_str}"
            )

    # Check: rankings must be unique integers 1-8
    if third_rankings:
        rank_nums = [r for r, _ in third_rankings]
        rank_counts = Counter(rank_nums)
        duplicates = {r: c for r, c in rank_counts.items() if c > 1}
        if duplicates:
            dup_strs = [f"{r} appears {c}x" for r, c in sorted(duplicates.items())]
            errors.append(f"Duplicate ranking numbers: {', '.join(dup_strs)}")

        expected = set(range(1, total_third + 1))
        actual = set(rank_nums)
        missing = expected - actual
        extra = actual - expected
        if missing and not duplicates:
            errors.append(f"Missing ranking numbers: {sorted(missing)}")
        if extra:
            errors.append(f"Ranking numbers out of range (expected 1-{total_third}): {sorted(extra)}")

    # --- Overlap check ---
    r32_teams_set = set()
    for teams in r32_by_group.values():
        r32_teams_set.update(teams)

    overlaps = r32_teams_set & third_teams_set
    if overlaps:
        for team in sorted(overlaps):
            errors.append(f"Team overlap - {team} picked as both R32 and 3rd place")

    return errors, total_r32, total_third, dup_groups, len(overlaps)


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    r32_cols, third_cols = parse_headers(headers)

    summary_rows = []

    for row in rows:
        name = row[2].strip()
        errors, total_r32, total_third, dup_groups, overlap_count = validate_entry(
            row, r32_cols, third_cols
        )

        # Per-person detail
        print(f"=== {name} ===")
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
        else:
            print("  VALID")
        print()

        # Collect summary
        dup_str = ", ".join(dup_groups) if dup_groups else "-"
        rankings_ok = all(
            "Duplicate ranking" not in e and "Missing ranking" not in e
            for e in errors
        )
        status = "VALID" if not errors else "INVALID"
        summary_rows.append(
            (name, total_r32, total_third, dup_str, overlap_count,
             "OK" if rankings_ok else "INVALID", status)
        )

    # Summary table
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    header_fmt = "{:<25s} {:>4s} {:>4s}  {:<14s} {:>9s} {:>10s}  {:<7s}"
    row_fmt = "{:<25s} {:>4d} {:>4d}  {:<14s} {:>9d} {:>10s}  {:<7s}"
    print(header_fmt.format(
        "Name", "R32", "3rd", "Dup Groups", "Overlaps", "Rankings", "Status"
    ))
    print("-" * 90)
    for name, r32, third, dups, overlaps, rankings, status in summary_rows:
        print(row_fmt.format(name, r32, third, dups, overlaps, rankings, status))


if __name__ == "__main__":
    main()
