---
layout: page
title: Leaderboard
description: NFL 2025 Playoff Predictions - Live Scoring
background: '/img/nfl/bg_nfl.webp'
permalink: "/nfl-2025/leaderboard"
---

*Last updated: January 25, 2026 at 10:35 PM EST*

## Contest Status

**6 of 7 games completed** (1 remaining)

---

## Current Leaderboard

Lower scores are better! The scoring uses cross-entropy (log loss) to penalize incorrect predictions more heavily.

- **Bold numbers** indicate directionally correct predictions (you gave the winner a higher confidence score)
- <u>Underlined numbers</u> indicate the best (lowest penalty) prediction for that game

{:.thead-dark .table-striped .table-bordered .table-sm }
| Rank | Name | Total | BUF-DEN | SF-SEA | HOU-NE | LAR-CHI | NE-DEN | LAR-SEA |
| :--------: | :------------ | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: |
| 1 | Chink | 4.37 | <strong>0.94</strong> | <strong><u>0.32</u></strong> | <strong>0.74</strong> | <strong>0.6</strong> | <strong>0.9</strong> | <strong>0.87</strong> |
| 2 | Go Seahawks! Tees | 4.44 | <strong>0.7</strong> | <strong>0.77</strong> | <strong>0.64</strong> | <strong>0.69</strong> | <strong>0.92</strong> | <strong>0.72</strong> |
| 3 | Dodo | 4.71 | <strong><u>0.32</u></strong> | <strong>0.74</strong> | <strong>0.62</strong> | 1.0 | 1.16 | <strong>0.87</strong> |
| 4 | Chayan Chakrabarti | 4.73 | 1.15 | <strong>0.96</strong> | <strong>0.76</strong> | <strong><u>0.04</u></strong> | <strong>0.84</strong> | <strong>0.98</strong> |
| 5 | Kshitij | 4.85 | <strong>0.74</strong> | <strong>0.74</strong> | <strong>0.74</strong> | <strong>0.51</strong> | 1.0 | 1.12 |
| 6 | Surendra Gona | 4.87 | <strong><u>0.32</u></strong> | <strong>0.86</strong> | <strong>0.32</strong> | 1.74 | 1.0 | <strong>0.63</strong> |
| 7 | Sackett | 4.96 | <strong>0.86</strong> | <strong>0.74</strong> | <strong>0.74</strong> | <strong>0.62</strong> | <strong>0.94</strong> | 1.06 |
| 8 | Siva | 5.01 | 1.22 | <strong>0.7</strong> | <strong>0.65</strong> | <strong>0.74</strong> | <strong>0.89</strong> | <strong>0.81</strong> |
| 9 | Shaji | 5.06 | <strong>0.94</strong> | <strong>0.86</strong> | <strong>0.69</strong> | <strong>0.51</strong> | <strong>0.88</strong> | 1.18 |
| 10 | Siva Kantamneni | 5.09 | <strong>0.51</strong> | <strong>0.74</strong> | <strong>0.86</strong> | <strong>0.86</strong> | 1.18 | <strong>0.94</strong> |
| 11 | Sridhar Seshadri | 5.83 | 1.74 | 1.0 | <strong>0.74</strong> | <strong>0.51</strong> | <strong>0.58</strong> | 1.26 |
| 12 | Pankaj Tyagi | 5.84 | <strong>0.99</strong> | <strong>0.96</strong> | <strong>0.98</strong> | <strong>0.93</strong> | <strong>0.99</strong> | <strong>0.99</strong> |
| 13 | Harsh | 6.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 14 | Niners Iyer | 6.28 | 1.74 | 1.32 | <strong>0.74</strong> | <strong>0.32</strong> | <strong>0.58</strong> | 1.58 |
| 15 | Sreenivas G | 6.63 | 1.32 | 1.15 | 1.32 | <strong>0.42</strong> | 1.0 | 1.42 |
| 16 | Mukund N. | 6.69 | <strong>0.87</strong> | <strong>0.99</strong> | 1.61 | <strong>0.85</strong> | 1.64 | <strong>0.73</strong> |
| 17 | Jyothi Sadhu | 6.73 | 1.51 | 1.32 | 1.15 | <strong>0.36</strong> | <strong>0.83</strong> | 1.56 |
| 18 | Sriram Venkatesh | 6.75 | 1.84 | 1.47 | <strong>0.81</strong> | <strong>0.47</strong> | <strong>0.58</strong> | 1.58 |
| 19 | Ranga Setlur | 6.93 | 2.0 | <strong>0.74</strong> | 1.32 | 1.32 | <strong>0.81</strong> | <strong>0.74</strong> |
| 20 | bala | 7.38 | 2.0 | <strong>0.97</strong> | 1.51 | 1.25 | <strong>0.78</strong> | <strong>0.87</strong> |
| 21 | Aarush | 8.27 | 2.0 | 2.32 | <strong>0.74</strong> | <strong>0.62</strong> | <strong>0.5</strong> | 2.09 |
| 22 | Gokul Krishnan | 9.28 | 2.32 | 1.32 | 2.32 | 1.32 | 1.0 | 1.0 |
| 23 | Alok | 11.16 | 6.66 | <strong>0.51</strong> | 1.51 | 2.0 | <strong>0.04</strong> | <strong><u>0.44</u></strong> |
| 24 | vivek | 21.0 | 6.66 | 6.66 | <strong><u>0.01</u></strong> | 6.66 | <strong><u>0.01</u></strong> | 1.0 |


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

[View All Predictions](/prediction-contests/nfl-2025/predictions) | [Contest Rules](/prediction-contests/nfl-2025/rules)
