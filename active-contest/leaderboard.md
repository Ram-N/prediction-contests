---
layout: page
title: Leaderboard
description: NFL 2025 Playoff Predictions - Live Scoring
background: '/img/nfl/bg_nfl.webp'
permalink: "/nfl-2025/leaderboard"
---

*Last updated: January 21, 2026 at 04:29 PM EST*

## Contest Status

**4 of 7 games completed** (3 remaining)

---

## Current Leaderboard

Lower scores are better! The scoring uses cross-entropy (log loss) to penalize incorrect predictions more heavily.

- **Bold numbers** indicate directionally correct predictions (you gave the winner a higher confidence score)
- <u>Underlined numbers</u> indicate the best (lowest penalty) prediction for that game

{:.thead-dark .table-striped .table-bordered .table-sm }
| Rank | Name | Total | BUF-DEN | HOU-NE | LAR-CHI | SF-SEA |
| :--------: | :------------ | ---------: | ---------: | ---------: | ---------: | ---------: |
| 1 | Chink | 2.6 | <strong>0.94</strong> | <strong>0.74</strong> | <strong>0.6</strong> | <strong><u>0.32</u></strong> |
| 2 | Dodo | 2.68 | <strong><u>0.32</u></strong> | <strong>0.62</strong> | 1.0 | <strong>0.74</strong> |
| 3 | Kshitij | 2.73 | <strong>0.74</strong> | <strong>0.74</strong> | <strong>0.51</strong> | <strong>0.74</strong> |
| 4 | Go Seahawks! Tees | 2.8 | <strong>0.7</strong> | <strong>0.64</strong> | <strong>0.69</strong> | <strong>0.77</strong> |
| 5 | Chayan Chakrabarti | 2.91 | 1.15 | <strong>0.76</strong> | <strong><u>0.04</u></strong> | <strong>0.96</strong> |
| 6 | Sackett | 2.96 | <strong>0.86</strong> | <strong>0.74</strong> | <strong>0.62</strong> | <strong>0.74</strong> |
| 7 | Siva Kantamneni | 2.97 | <strong>0.51</strong> | <strong>0.86</strong> | <strong>0.86</strong> | <strong>0.74</strong> |
| 8 | Shaji | 3.0 | <strong>0.94</strong> | <strong>0.69</strong> | <strong>0.51</strong> | <strong>0.86</strong> |
| 9 | Surendra Gona | 3.24 | <strong><u>0.32</u></strong> | <strong>0.32</strong> | 1.74 | <strong>0.86</strong> |
| 10 | Siva | 3.31 | 1.22 | <strong>0.65</strong> | <strong>0.74</strong> | <strong>0.7</strong> |
| 11 | Pankaj Tyagi | 3.86 | <strong>0.99</strong> | <strong>0.98</strong> | <strong>0.93</strong> | <strong>0.96</strong> |
| 12 | Sridhar Seshadri | 3.99 | 1.74 | <strong>0.74</strong> | <strong>0.51</strong> | 1.0 |
| 13 | Harsh | 4.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 14 | Niners Iyer | 4.12 | 1.74 | <strong>0.74</strong> | <strong>0.32</strong> | 1.32 |
| 15 | Sreenivas G | 4.21 | 1.32 | 1.32 | <strong>0.42</strong> | 1.15 |
| 16 | Mukund N. | 4.32 | <strong>0.87</strong> | 1.61 | <strong>0.85</strong> | <strong>0.99</strong> |
| 17 | Jyothi Sadhu | 4.34 | 1.51 | 1.15 | <strong>0.36</strong> | 1.32 |
| 18 | Sriram Venkatesh | 4.59 | 1.84 | <strong>0.81</strong> | <strong>0.47</strong> | 1.47 |
| 19 | Ranga Setlur | 5.38 | 2.0 | 1.32 | 1.32 | <strong>0.74</strong> |
| 20 | Aarush | 5.68 | 2.0 | <strong>0.74</strong> | <strong>0.62</strong> | 2.32 |
| 21 | bala | 5.73 | 2.0 | 1.51 | 1.25 | <strong>0.97</strong> |
| 22 | Gokul Krishnan | 7.28 | 2.32 | 2.32 | 1.32 | 1.32 |
| 23 | Alok | 10.68 | 6.66 | 1.51 | 2.0 | <strong>0.51</strong> |
| 24 | vivek | 19.99 | 6.66 | <strong><u>0.01</u></strong> | 6.66 | 6.66 |


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

[View All Predictions]({{ site.baseurl }}/{{ site.contest.slug }}/predictions) | [Contest Rules]({{ site.baseurl }}/{{ site.contest.slug }}/rules)
