---
layout: page
title: "Group Leaderboard - NARMADA"
description: NFL 2025 Playoffs - NARMADA Group Standings
background: '/img/nfl/bg_nfl1.webp'
permalink: "/nfl-2025/groups/narmada"
---

*Last updated: February 08, 2026 at 04:03 PM EST*

[← Back to Main Leaderboard]({{ site.baseurl }}/{{ site.contest.slug }}/leaderboard)

---

## NARMADA Group Standings

**This contest ended on February 08, 2026. Chink won with a score of 5.18!**

**7 of 7 games completed** (0 remaining)

{:.thead-dark .table-striped .table-bordered .table-sm }
| Rank | Name | Total | BUF-DEN | SF-SEA | HOU-NE | LAR-CHI | NE-DEN | LAR-SEA | SEA-NE |
| :--------: | :------------ | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: |
| 1 | Chink | 5.18 | <strong>0.94</strong> | <strong><u>0.32</u></strong> | <strong>0.74</strong> | <strong>0.6</strong> | <strong>0.9</strong> | <strong>0.87</strong> | <strong>0.81</strong> |
| 2 | Go Seahawks! Tees | 5.37 | <strong>0.7</strong> | <strong>0.77</strong> | <strong>0.64</strong> | <strong>0.69</strong> | <strong>0.92</strong> | <strong><u>0.72</u></strong> | <strong>0.93</strong> |
| 3 | Dodo | 5.77 | <strong><u>0.32</u></strong> | <strong>0.74</strong> | <strong><u>0.62</u></strong> | 1.0 | 1.16 | <strong>0.87</strong> | 1.06 |
| 4 | Sackett | 5.96 | <strong>0.86</strong> | <strong>0.74</strong> | <strong>0.74</strong> | <strong>0.62</strong> | <strong>0.94</strong> | 1.06 | 1.0 |
| 5 | Shaji | 6.15 | <strong>0.94</strong> | <strong>0.86</strong> | <strong>0.69</strong> | <strong>0.51</strong> | <strong>0.88</strong> | 1.18 | 1.09 |
| 6 | Harsh | 7.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 7 | Niners Iyer | 7.6 | 1.74 | 1.32 | <strong>0.74</strong> | <strong><u>0.32</u></strong> | <strong>0.58</strong> | 1.58 | 1.32 |
| 8 | bala | 8.13 | 2.0 | <strong>0.97</strong> | 1.51 | 1.25 | <strong>0.78</strong> | <strong>0.87</strong> | <strong>0.75</strong> |
| 9 | Gokul Krishnan | 9.86 | 2.32 | 1.32 | 2.32 | 1.32 | 1.0 | 1.0 | <strong><u>0.58</u></strong> |
| 10 | Aarush | 10.27 | 2.0 | 2.32 | <strong>0.74</strong> | <strong>0.62</strong> | <strong><u>0.5</u></strong> | 2.09 | 2.0 |


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
