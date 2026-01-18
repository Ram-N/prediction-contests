---
layout: page
title: Leaderboard
description: NFL 2025 Playoff Predictions - Live Scoring
background: '/img/bg_nfl.webp'
permalink: "/nfl-2025/leaderboard"
---

## Contest Status

**2 of 7 games completed** (5 remaining)

*Last updated: January 18, 2026 at 03:39 PM EST*

---

## Current Leaderboard

Lower scores are better! The scoring uses cross-entropy (log loss) to penalize incorrect predictions more heavily.

- **Bold numbers** indicate directionally correct predictions (you gave the winner a higher confidence score)
- <u>Underlined numbers</u> indicate the best (lowest penalty) prediction for that game

{:.thead-dark .table-striped .table-bordered .table-sm }
| Name | Total | BUF-DEN | SF-SEA |
| :------------ | ---------: | ---------: | ---------: |
| Dodo | 1.06 | <u>**0.32**</u> | **0.74** |
| Surendra Gona | 1.18 | <u>**0.32**</u> | **0.86** |
| Siva Kantamneni | 1.25 | **0.51** | **0.74** |
| Chink | 1.26 | **0.94** | <u>**0.32**</u> |
| Go Seahawks! Tees | 1.47 | **0.7** | **0.77** |
| Kshitij | 1.48 | **0.74** | **0.74** |
| Sackett | 1.6 | **0.86** | **0.74** |
| Shaji | 1.8 | **0.94** | **0.86** |
| Mukund N. | 1.86 | **0.87** | **0.99** |
| Siva | 1.92 | 1.22 | **0.7** |
| Pankaj Tyagi | 1.95 | **0.99** | **0.96** |
| Harsh | 2.0 | 1.0 | 1.0 |
| Chayan Chakrabarti | 2.11 | 1.15 | **0.96** |
| Sreenivas G | 2.47 | 1.32 | 1.15 |
| Sridhar Seshadri | 2.74 | 1.74 | 1.0 |
| Ranga Setlur | 2.74 | 2.0 | **0.74** |
| Jyothi Sadhu | 2.83 | 1.51 | 1.32 |
| bala | 2.97 | 2.0 | **0.97** |
| Niners Iyer | 3.06 | 1.74 | 1.32 |
| Sriram Venkatesh | 3.31 | 1.84 | 1.47 |
| Gokul Krishnan | 3.64 | 2.32 | 1.32 |
| Aarush | 4.32 | 2.0 | 2.32 |
| Alok | 7.17 | 6.66 | **0.51** |
| vivek | 13.32 | 6.66 | 6.66 |


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

[View All Predictions](/prediction-contests/{contest_slug}/predictions) | [Contest Rules](/prediction-contests/{contest_slug}/rules)
