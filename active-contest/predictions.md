---
layout: page
title: "Predictions - FIFA 2026"
description: "All submitted predictions for the FIFA 2026 contests"
background: '/img/soccer/bg_fifa.webp'
permalink: "/fifa-2026/predictions"
---

# Semi-Final 4-2-1 (ST-421) Predictions

All submitted predictions for the **ST-421** contest. Participants picked the winner of each of the 4 quarterfinal matches, then 2 finalists and the overall winner.

**Total Entries:** 62 participants (59 humans + 3 AI models)

---

{% include_relative predictions-st421-table.md %}

---

# Round of 16 Predictions

All submitted predictions for the **Round of 16** knockout stage. Participants picked the winner of each of the 8 matches. Each correct pick is worth **4 points**.

**Total Entries:** 67 participants (63 humans + 3 AI models + WOTC)

---

{% include_relative predictions-r16-table.md %}

---

# Round of 32 Predictions

All submitted predictions for the **Round of 32** knockout stage. Participants picked the winner of each of the 16 matches. Each correct pick is worth **2 points**.

**Total Entries:** 65 participants (62 humans + 3 AI models)

---

{% include_relative predictions-r32-table.md %}

---

# Group Stage Predictions

All submitted predictions for the **Group Stage** contest are shown below. Participants picked 2 teams per group (A–L) to advance to the Round of 32, plus 8 best third-place teams.

**Total Entries:** 54 participants (51 humans + 3 AI models)

---

{% include_relative predictions-group-stage-table.md %}

---

# Long Range 4-2-1 Predictions

All submitted predictions for the **4-2-1 Long Range** contest are shown below. Participants picked 4 semifinalists (1 pt each), 2 finalists (2 pts each), and 1 winner (4 pts).

**Total Entries:** 55 participants (52 humans + 3 AI models)

---

{% include_relative predictions-lr421-table.md %}

<style>
.r16-plot-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}
.r16-plot-overlay.active { display: flex; }
.r16-plot-overlay img {
  max-width: 90%;
  max-height: 80%;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  background: #fff;
}
a.r16-plot-link {
  text-decoration: underline dotted;
  cursor: pointer;
  color: inherit;
}
</style>

<div class="r16-plot-overlay" id="plotOverlay" onclick="this.classList.remove('active')">
  <img id="plotImg" src="" alt="Match prediction split">
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.r16-plot-link').forEach(function(a) {
    a.addEventListener('click', function(e) {
      e.preventDefault();
      document.getElementById('plotImg').src = this.dataset.plot;
      document.getElementById('plotOverlay').classList.add('active');
    });
  });
});
</script>
