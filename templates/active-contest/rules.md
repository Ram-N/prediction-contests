---
layout: page
title: "Rules - CONTEST_NAME"
description: "Contest rules and scoring system"
background: '/img/bg_default.webp'
permalink: "/{{ site.contest.slug }}/rules"
---

# {{ site.contest.full_title }} Rules

## Overview

<!-- Customize the contest overview -->
Predict the outcomes of [describe the games/matches].

## Contest Format

<!-- Describe the contest format -->
The contest covers:
- **Round 1** (X games)
- **Round 2** (X games)
- **Final** (1 game)

**Total: X games**

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
- Predictions must be submitted before [deadline]
- You are competing for glory and a spot in the [Prediction Hall of Fame]({{ site.baseurl }}/hof)
- The winner will be declared after [final event]

## Deadlines

- **Predictions close**: [Insert deadline]
- **All predictions must be in by**: [Insert deadline]

## Entry

Submit your predictions using the [entry form]({{ site.contest.entry_form }}).

Good luck!
