---
layout: post
title: "Chink leads after the Divisional Round"
subtitle: "Leaderboard Update: After 4 Games"
date: 2026-01-18 23:44:15 -0500
background: '/img/nfl/bg_nfl.webp'
---

# NFL 2025 - After 4 Games

**Standings after 4 games** (Lower scores are better!)

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


**Legend:**
- **Bold numbers** = Directionally correct predictions (you gave the winner a higher score)
- <u>Underlined numbers</u> = Best (lowest penalty) prediction for that game

---

### Current Leader

**Chink** has taken over first place with a total penalty of **2.6**, edging out Dodo (2.68) by just 0.08 points! Kshitij rounds out the top three at 2.73. After Saturday's games, Dodo was leading with 1.06, but Chink's strong performance on the Sunday games (especially an impressive 0.32 penalty on SF-SEA) propelled them to the top.

The race at the top is incredibly tight - the top 8 participants are all separated by less than 0.4 points. Go Seahawks! Tees (2.8) and Chayan Chakrabarti (2.91) are right in the mix, while Sackett, Siva Kantamneni, and Shaji are all clustered around the 3.0 mark.

### Game Results

- **BUF-DEN**: DEN defeats BUF
- **HOU-NE**: NE defeats HOU
- **LAR-CHI**: LAR defeats CHI
- **SF-SEA**: SEA defeats SF

### Perfect Directional Predictions

These participants got **all 4 games directionally correct** (all penalties under 1.0):

- Chink
- Dodo
- Kshitij
- Go Seahawks! Tees
- Sackett
- Siva Kantamneni
- Shaji
- Surendra Gona
- Pankaj Tyagi

Nine participants nailed the direction on every game! The difference in standings comes down to confidence levels - those who were more confident in the correct picks earned lower penalties.

---

## How Cross-Entropy Scoring Works

Our scoring system penalizes confident wrong predictions more heavily than tentative ones:

**Formula:** Penalty = log₂((Team1_Score + Team2_Score) / Winner_Score)

**Examples:**
- Confidently picked the winner (80-20): low penalty (~0.32)
- No strong opinion (50-50): penalty of 1.0
- Confidently picked the loser (20-80): high penalty (~2.32)

This rewards participants who correctly identified strong winners with high confidence!

---

[See All Predictions]({{ site.baseurl }}/{{ site.contest.slug }}/predictions) | [Contest Rules]({{ site.baseurl }}/{{ site.contest.slug }}/rules) | [Leaderboard Page]({{ site.baseurl }}/{{ site.contest.slug }}/leaderboard)
