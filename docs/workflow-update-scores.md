This is how to update the Prediction scores for Players, as and when the results come in.

## Updated checklist (including the new requirements):

* **Write a new Python program** to process **active contests** (games currently in progress).
* **Read predictions** from <latest-contest>-Predictions-Clean.csv (people's submitted probabilities/picks).
* **Read results** from <latest-contest>-results.csv (game outcomes or latest known results).
* Note that the games that are yet to be played will have TBD as the result. Don't use those for scoring.
* **IMPORTANT**: Game columns in the leaderboard must appear in the same order as rows in the results.csv file (NOT alphabetically sorted). This preserves the chronological order of games.
*
### For each game in the contest:

  * **Compute a per-user score using cross-entropy (log loss)**, based on predictions vs results.
  * **Mark whether the user was directionally correct** (picked the winner correctly).
  * **Render the per-game score in bold when directionally correct** (so “got it right” is visually obvious in the output).
* **Compute each user’s total score** across all games in the contest.

  * **Add a new column** for the total score (e.g., `total_score`).
* **Sort the final leaderboard** so the **highest total score is at the top**.

Step 3: Output for publishing
* **Generate an output suitable for publishing** 
* Markdown tables

Step 4: Update leaderboard.md and group leaderboards
  * The script automatically updates:
    - Main leaderboard: `active-contest/leaderboard.md`
    - Group leaderboards: `active-contest/groups/*.md` (if groups are configured)
  * Each leaderboard includes:
    - A quick status summary (for example: **"2 games are over, X games remaining"** or **"2 games over out of N"**)
    - The **current leaderboard standings** "as of now" (embedded table with the bold per-game scores)
    - **Final note (starred/emphasized at the very end):** explicitly state the scoring metric used, i.e. **cross-entropy / log loss**

Step 5: Create a new blog post with the updated results
- write a nice post (after each update of the scores)
- Include a few comments, based on who's leading, how many people got it right etc.
- **IMPORTANT - Blog Post Title Guidelines:**
  - ✅ GOOD: "Chink leads after the Divisional Round"
  - ✅ GOOD: "Go Seahawks! Tees takes the lead after 5 games"
  - ❌ BAD: "Chink leads with a penalty of 2.6"
  - ❌ BAD: "Updated standings - 5 games completed"
  - The title should mention WHO is leading (by name) and AFTER WHICH round/game
  - Keep it fun and personalized, NOT technical about penalties or scores

Step 6:
- Post to the blog.
- Git commit and push
