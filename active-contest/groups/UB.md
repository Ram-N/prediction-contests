---
layout: page
title: "Group Leaderboard - UB"
description: NFL 2025 - UB Group Standings
background: '/img/nfl/bg_nfl.webp'
permalink: "/nfl-2025/groups/ub"
---

*Last updated: January 25, 2026 at 10:35 PM EST*

[← Back to Main Leaderboard]({{ site.baseurl }}/{{ site.contest.slug }}/leaderboard)

---

## UB Group Standings

**6 of 7 games completed** (1 remaining)

{:.thead-dark .table-striped .table-bordered .table-sm }
| Rank | Name | Total | BUF-DEN | SF-SEA | HOU-NE | LAR-CHI | NE-DEN | LAR-SEA |
| :--------: | :------------ | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: |
| 1 | Siva | 5.01 | <u>1.22</u> | <strong>0.7</strong> | <strong>0.65</strong> | <strong>0.74</strong> | <strong>0.89</strong> | <strong>0.81</strong> |
| 2 | Sridhar Seshadri | 5.83 | 1.74 | 1.0 | <strong>0.74</strong> | <strong>0.51</strong> | <strong>0.58</strong> | 1.26 |
| 3 | Sreenivas G | 6.63 | 1.32 | 1.15 | 1.32 | <strong><u>0.42</u></strong> | 1.0 | 1.42 |
| 4 | Ranga Setlur | 6.93 | 2.0 | <strong>0.74</strong> | 1.32 | 1.32 | <strong>0.81</strong> | <strong>0.74</strong> |
| 5 | Alok | 11.16 | 6.66 | <strong><u>0.51</u></strong> | 1.51 | 2.0 | <strong>0.04</strong> | <strong><u>0.44</u></strong> |
| 6 | vivek | 21.0 | 6.66 | 6.66 | <strong><u>0.01</u></strong> | 6.66 | <strong><u>0.01</u></strong> | 1.0 |


---

## How Scoring Works

The penalty for each game is calculated using cross-entropy (log loss):

**Penalty = log₂((Team1_Score + Team2_Score) / Winner_Score)**

This is equivalent to: **-log₂(probability you assigned to the winner)**

### Examples:

- **Perfect prediction** (100-1): penalty = log₂(101/100) = **0.01**
- **Confident correct** (80-20): penalty = log₂(100/80) = **0.32**
- **Moderate correct** (60-40): penalty = log₂(100/60) = **0.74**
- **50-50 prediction**: penalty = log₂(100/50) = **1.0** (not directionally correct)
- **Wrong direction** (40-60, winner got 40): penalty = log₂(100/40) = **1.32**
- **Very wrong** (20-80, winner got 20): penalty = log₂(100/20) = **2.32**

The more confident you were in the winner, the lower your penalty. Being confident in the loser results in high penalties!

---

[View All Predictions]({{ site.baseurl }}/{{ site.contest.slug }}/predictions) | [Contest Rules]({{ site.baseurl }}/{{ site.contest.slug }}/rules) | [Main Leaderboard]({{ site.baseurl }}/{{ site.contest.slug }}/leaderboard)
