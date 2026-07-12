---
layout: page
title: "Round of 16 Predictions"
description: "All R16 predictions — entries are now closed"
background: '/img/soccer/bg_fifa.webp'
permalink: "/fifa-2026/round-of-16"
---

## FIFA World Cup 2026 — Round of 16 Predictions

*Last updated: July 12, 2026 — 01:11 PM EDT*

**67 participants** (63 humans + 3 AI models + WOTC) picked the winner of each of the 8 knockout matches. Each correct pick is worth **4 points**.

**8 of 8 matches decided.** 
**MAR** beat CAN, **FRA** beat PAR, **NOR** beat BRA, **ENG** beat MEX, **ESP** beat POR, **BEL** beat USA, **ARG** beat EGY, **SUI** beat COL.

**Color coding:**
- <span style="color:green"><b>Green/Bold</b></span> = Correct pick (winner guessed right)
- <span style="color:red"><s>Red/Strikethrough</s></span> = Wrong pick
- Plain text = Result pending

---

{% include_relative predictions-r16-table.md %}


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
  <img id="plotImg" src="" alt="R16 prediction split">
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

