---
layout: page
title: "Rules - T20 2026"
description: "Contest rules and scoring system"
background: '/img/bg_t20.webp'
permalink: "/t20-2026/rules"
---

# {{ site.contest.full_title }} Rules

## Overview

Predict the winning teams for all knockout stage matches in the T20 World Cup 2026.

## Contest Format

The contest covers:
- **Super 8 Stage** (4 matches)
- **Semi-Finals** (2 matches)
- **Final** (1 match)

**Total: 9 knockout matches**

## Scoring System

Scoring is based on the accuracy of your predictions using a logarithmic scoring system that rewards confident correct predictions and penalizes overconfident wrong predictions.

For each game, you predict:
- The winning team
- Your confidence level (probability between 0.51 and 1.0)

### Scoring Formula

- **Correct prediction**: Score = -log₂(confidence)
- **Incorrect prediction**: Score = -log₂(1 - confidence)

**Lower total score is better!**

### Examples

- Predict team A with 0.6 confidence → Team A wins → Score: 0.74
- Predict team A with 0.9 confidence → Team A wins → Score: 0.15
- Predict team A with 0.9 confidence → Team B wins → Score: 3.32

## Rules

- One entry per person (honor system)
- Predictions must be submitted before the first knockout match
- You are competing for glory and a spot in the [Prediction Hall of Fame]({{ site.baseurl }}/past/hof)
- The winner will be declared after the T20 World Cup Final

## Deadlines

- **Predictions close**: TBD (before first Super 8 match)
- **All predictions must be in by**: TBD (tournament schedule to be announced)

## Entry

Submit your predictions using the [entry form]({{ site.contest.entry_form }}).

Good luck!
