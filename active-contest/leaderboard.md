---
layout: page
title: Leaderboard
description: NFL 2025 Playoff Predictions - Live Scoring
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/leaderboard"
---

*Last updated: January 18, 2026 at 11:28 PM EST*

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
| 1 | Chink | 2.6 | **0.94** | **0.74** | **0.6** | <u>**0.32**</u> |
| 2 | Dodo | 2.68 | <u>**0.32**</u> | **0.62** | 1.0 | **0.74** |
| 3 | Kshitij | 2.73 | **0.74** | **0.74** | **0.51** | **0.74** |
| 4 | Go Seahawks! Tees | 2.8 | **0.7** | **0.64** | **0.69** | **0.77** |
| 5 | Chayan Chakrabarti | 2.91 | 1.15 | **0.76** | <u>**0.04**</u> | **0.96** |
| 6 | Sackett | 2.96 | **0.86** | **0.74** | **0.62** | **0.74** |
| 7 | Siva Kantamneni | 2.97 | **0.51** | **0.86** | **0.86** | **0.74** |
| 8 | Shaji | 3.0 | **0.94** | **0.69** | **0.51** | **0.86** |
| 9 | Surendra Gona | 3.24 | <u>**0.32**</u> | **0.32** | 1.74 | **0.86** |
| 10 | Siva | 3.31 | 1.22 | **0.65** | **0.74** | **0.7** |
| 11 | Pankaj Tyagi | 3.86 | **0.99** | **0.98** | **0.93** | **0.96** |
| 12 | Sridhar Seshadri | 3.99 | 1.74 | **0.74** | **0.51** | 1.0 |
| 13 | Harsh | 4.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 14 | Niners Iyer | 4.12 | 1.74 | **0.74** | **0.32** | 1.32 |
| 15 | Sreenivas G | 4.21 | 1.32 | 1.32 | **0.42** | 1.15 |
| 16 | Mukund N. | 4.32 | **0.87** | 1.61 | **0.85** | **0.99** |
| 17 | Jyothi Sadhu | 4.34 | 1.51 | 1.15 | **0.36** | 1.32 |
| 18 | Sriram Venkatesh | 4.59 | 1.84 | **0.81** | **0.47** | 1.47 |
| 19 | Ranga Setlur | 5.38 | 2.0 | 1.32 | 1.32 | **0.74** |
| 20 | Aarush | 5.68 | 2.0 | **0.74** | **0.62** | 2.32 |
| 21 | bala | 5.73 | 2.0 | 1.51 | 1.25 | **0.97** |
| 22 | Gokul Krishnan | 7.28 | 2.32 | 2.32 | 1.32 | 1.32 |
| 23 | Alok | 10.68 | 6.66 | 1.51 | 2.0 | **0.51** |
| 24 | vivek | 19.99 | 6.66 | <u>**0.01**</u> | 6.66 | 6.66 |


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
