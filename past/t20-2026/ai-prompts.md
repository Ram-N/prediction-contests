---
layout: page
title: "AI Super 8 Prompt"
description: "The prompt used to query AI models for Super 8 predictions"
background: '/img/cricket/bg_cricket.jpg'
permalink: "/t20-2026/ai-super8-prompt"
---

# PROMPT: Super 8 T20 World Cup Prediction Challenge (Research Allowed)


You are participating in a structured sports prediction experiment for the ICC Men’s T20 World Cup Super 8 stage.

### Tournament Structure

* 2 groups: Group 1 and Group 2
* 4 teams per group
* Round-robin within each group (each team plays 3 matches)
* 6 matches per group
* Top two teams from each group advance to semifinals

### Your Task

For each group:

1. Predict the team that will finish 1st
2. Predict the team that will finish 2nd

You must make definitive selections.

Here are the teams and details: https://en.wikipedia.org/wiki/2026_Men%27s_T20_World_Cup#Super_8_stage

## Group 1	
Advanced from the group stage
(Top 2 teams from each group)	

 India | 
 Zimbabwe |
 West Indies |
 South Africa

## Group 2
Pakistan |
England |
Sri Lanka |
New Zealand


### Research Policy

You are explicitly allowed to use any available information, including:

* Current form
* Player availability and injuries
* Historical head-to-head data
* Venue conditions
* Net run rate trends
* Betting odds
* Expert predictions
* Statistical models
* News reports
* Any other relevant public information

There are no restrictions on research sources.

However, your goal is not to copy betting markets blindly. Your goal is to generate the most accurate prediction possible using structured reasoning.

Required Output Format (Strict)
```
Group 1
1st: [Team Name]
2nd: [Team Name]
Confidence (Group 1 overall prediction): [0–100%]

Group 2
1st: [Team Name]
2nd: [Team Name]
Confidence (Group 2 overall prediction): [0–100%]
```

### Reasoning Section (max 400 words total)

In your reasoning:

1. Briefly identify the 3–5 most important factors influencing your decision.
2. State whether your prediction aligns with current betting favorites or differs from them.
3. If it aligns, explain why you independently agree.
4. If it differs, explain why you believe the market may be mispricing risk.
5. Explicitly describe at least one downside risk for each group prediction.

Do not hedge excessively. Make a clear call.


## Scoring Rules for the Prediction Contest

### Super 8 Group Scoring

In each group, let **W** = actual group winner and **R** = actual runner-up.

| Points | Condition |
|--------|-----------|
| **6** | You picked both W and R to advance, and correctly picked W as the group winner. |
| **5** | You picked both W and R to advance, but incorrectly picked R to win the group. |
| **4** | You picked W to advance and correctly as group winner, but did not pick R to advance. |
| **3** | You picked W to advance, but as runner-up, and did not pick R. |
| **2** | You picked R to advance as runner-up, but did not pick W. |
| **1** | You picked R to advance and as group winner, but did not pick W. |
| **0** | You picked neither W nor R to advance. |

- Maximum possible points per group = 6
- Maximum possible points across all Super 8 groups = **12** (2 groups × 6 points)
