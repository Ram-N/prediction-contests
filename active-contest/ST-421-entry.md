---
layout: page
title: "Short-Term 4-2-1 Contest"
description: "Predict the Quarterfinal, Semifinal, and Final winners"
background: '/img/soccer/421-banner.png'
permalink: "/fifa-2026/st-421-entry"
---

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/flag-icons/7.5.0/css/flag-icons.min.css">

<style>
  /* ── Bracket Grid ── */
  #bracket {
    display: grid;
    grid-template-columns: 1fr 1fr 1.2fr 1fr 1fr;
    grid-template-rows: auto auto auto;
    gap: 0.5rem 0.75rem;
    margin: 1.5rem 0;
    position: relative;
  }

  /* Grid placement */
  .bracket-slot[data-slot="qf1"] { grid-column: 1; grid-row: 1; }
  .bracket-slot[data-slot="qf2"] { grid-column: 1; grid-row: 2; }
  .bracket-slot[data-slot="sf1"] { grid-column: 2; grid-row: 1 / 3; align-self: center; }
  .bracket-slot[data-slot="final"] { grid-column: 3; grid-row: 1 / 3; align-self: center; }
  .bracket-slot[data-slot="sf2"] { grid-column: 4; grid-row: 1 / 3; align-self: center; }
  .bracket-slot[data-slot="qf3"] { grid-column: 5; grid-row: 1; }
  .bracket-slot[data-slot="qf4"] { grid-column: 5; grid-row: 2; }
  #champion-display { grid-column: 3; grid-row: 3; text-align: center; }

  /* ── Match Slot Styling ── */
  .bracket-slot {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
    min-width: 0;
  }
  .bracket-slot .slot-header {
    background: #343a40;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.25rem 0.6rem;
    letter-spacing: 0.05em;
  }

  .bracket-team {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.6rem;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    transition: background 0.15s, opacity 0.15s;
    user-select: none;
    font-size: 0.95rem;
  }
  .bracket-team:last-child { border-bottom: none; }
  .bracket-team:hover { background: #f0f7ff; }
  .bracket-team .fi { margin-right: 0.4em; }

  /* Picked (winner) */
  .bracket-team.picked {
    background: #d4edda;
    font-weight: 700;
    color: #155724;
  }
  .bracket-team.picked:hover { background: #c3e6cb; }

  /* Eliminated (loser) */
  .bracket-team.eliminated {
    opacity: 0.45;
    text-decoration: line-through;
    cursor: pointer;
  }

  /* TBD / waiting */
  .bracket-team.tbd {
    color: #999;
    font-style: italic;
    cursor: default;
    border-bottom-style: dashed;
  }
  .bracket-team.tbd:hover { background: transparent; }

  .bracket-slot.waiting {
    border-style: dashed;
    border-color: #dc3545;
  }

  /* Champion box — always visible as a call-to-action */
  #champion-display {
    font-size: 1.15rem;
    font-weight: 700;
    padding: 0.75rem;
    min-height: 3rem;
    border: 2px dashed #adb5bd;
    border-radius: 8px;
    text-align: center;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #champion-display .champion-prompt {
    color: #999;
    font-style: italic;
    font-weight: 400;
    font-size: 0.95rem;
  }
  #champion-display.has-winner {
    border-color: #28a745;
    border-style: solid;
    background: #d4edda;
    color: #155724;
    font-size: 1.3rem;
  }
  #champion-display .trophy { font-size: 1.5rem; }

  /* ── Connector Lines (desktop) ── */
  .bracket-slot {
    position: relative;
  }

  /* Right-side connectors: QF1/QF2 → SF1 */
  .bracket-slot[data-slot="qf1"]::after,
  .bracket-slot[data-slot="qf2"]::after {
    content: '';
    position: absolute;
    right: -0.75rem;
    top: 50%;
    width: 0.75rem;
    height: 2px;
    background: #adb5bd;
  }
  .bracket-slot[data-slot="sf1"]::after {
    content: '';
    position: absolute;
    right: -0.75rem;
    top: 50%;
    width: 0.75rem;
    height: 2px;
    background: #adb5bd;
  }

  /* Left-side connectors: QF3/QF4 → SF2 */
  .bracket-slot[data-slot="qf3"]::before,
  .bracket-slot[data-slot="qf4"]::before {
    content: '';
    position: absolute;
    left: -0.75rem;
    top: 50%;
    width: 0.75rem;
    height: 2px;
    background: #adb5bd;
  }
  .bracket-slot[data-slot="sf2"]::before {
    content: '';
    position: absolute;
    left: -0.75rem;
    top: 50%;
    width: 0.75rem;
    height: 2px;
    background: #adb5bd;
  }

  /* ── Mobile: Bracket-half grid layout ── */
  @media (max-width: 767px) {
    #bracket {
      display: flex;
      flex-direction: column;
      gap: 0;
    }
    /* Hide connector lines on mobile */
    .bracket-slot::before,
    .bracket-slot::after {
      display: none !important;
    }
    /* Reset desktop grid placement so mobile grid works */
    .bracket-slot[data-slot] {
      grid-column: auto !important;
      grid-row: auto !important;
      align-self: auto !important;
    }

    .bracket-half {
      margin-bottom: 1.25rem;
    }
    .bracket-half-header {
      display: block !important;
      font-weight: 700;
      font-size: 1rem;
      margin-bottom: 0.5rem;
      padding-bottom: 0.25rem;
      border-bottom: 2px solid #dee2e6;
      color: #343a40;
    }
    .bracket-half-grid {
      display: grid !important;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
    }
    .bracket-half-arrows {
      display: flex !important;
      grid-column: 1 / -1;
      justify-content: space-around;
      color: #adb5bd;
      font-size: 1.3rem;
      padding: 0.15rem 0;
      letter-spacing: 0.5em;
    }
    /* SF slot spans full width under the two QFs */
    .bracket-half-grid .bracket-slot[data-slot="sf1"],
    .bracket-half-grid .bracket-slot[data-slot="sf2"] {
      grid-column: 1 / -1;
    }

    .bracket-finals .bracket-half-header {
      display: block !important;
      margin-top: 0.25rem;
    }
    #champion-display {
      margin-top: 0.5rem;
    }

    /* Tap hint styling */
    .tap-hint, .bracket-tap-hint {
      display: block !important;
    }

    /* Show more of the banner on mobile */
    header.masthead .page-heading {
      padding: 60px 0 40px;
    }
  }

  /* Hide mobile-only elements on desktop */
  @media (min-width: 768px) {
    .bracket-half-header, .bracket-half-arrows { display: none !important; }
    .bracket-half, .bracket-finals { display: contents; }
    .bracket-half-grid { display: contents; }
    .tap-hint { display: none !important; }
  }

  /* ── Validation, Summary, Form (unchanged) ── */
  #validation-panel { margin-top: 1.5rem; padding: 1rem; border-radius: 8px; background: #fde8e8; border: 2px solid #dc3545; color: #721c24; }
  #validation-panel.valid { background: #d4edda; border-color: #28a745; color: #155724; }
  #validation-panel ul { margin-bottom: 0; padding-left: 1.2rem; }

  #summary-section { display: none; margin-top: 1.5rem; }
  #summary-section.visible { display: block; }
  #summary-table { width: 100%; }
  #summary-table th { background: #343a40; color: #fff; padding: 0.5rem 0.75rem; }
  #summary-table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #dee2e6; font-size: 1.05rem; }
  #summary-table tr:nth-child(even) { background: #f8f9fa; }
  .pick-highlight { font-weight: 700; color: #155724; }

  #submit-btn { margin-top: 1rem; }
  #submit-btn:disabled { opacity: 0.5; }
  #submission-result { margin-top: 1rem; }

  .resubmit-note { background: #e8f4fd; border: 1px solid #b8daff; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 1.5rem; color: #004085; font-size: 0.95rem; }

  /* Per-level tap hints (mobile only) */
  .bracket-tap-hint {
    display: none;
    color: #6c757d;
    font-size: 0.82rem;
    font-style: italic;
    margin: 0.25rem 0 0.4rem;
    padding: 0;
  }
</style>

## FIFA World Cup 2026 — Short-Term 4-2-1 Predictions

The tournament is down to the **Quarterfinals**! Click a team to pick the winner — your picks flow through the bracket to the Final.

<div class="resubmit-note">
  You can re-submit at any time — only your latest entry counts.
</div>

---

### Your Info

<div class="form-group">
  <label for="entry-name"><strong>Name</strong></label>
  <input type="text" class="form-control" id="entry-name" placeholder="Your name" maxlength="50">
</div>
<div class="form-group">
  <label for="entry-email"><strong>Email</strong></label>
  <input type="email" class="form-control" id="entry-email" placeholder="your@email.com" maxlength="100">
  <small class="form-text text-muted">We'll send you a copy of your picks and contest updates.</small>
</div>
<div class="form-group">
  <label for="entry-location"><strong>Location</strong></label>
  <input type="text" class="form-control" id="entry-location" placeholder="City or country" maxlength="50">
</div>

---

### Pick Your Bracket

<p style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">Click a team to pick the winner. Click again to change your mind. <a href="#" id="clear-selections" style="color: #dc3545; font-size: 0.85rem; margin-left: 0.5rem;">Clear all selections</a></p>
<p class="tap-hint" style="display:none; background: #e8f4fd; border: 1px solid #b8daff; border-radius: 6px; padding: 0.6rem 0.9rem; color: #004085; font-size: 0.9rem; margin-bottom: 0.75rem;">👆 <strong>Tap a team name</strong> to select the winner of each match. Your picks flow through the bracket automatically.</p>

<div id="bracket">
  <!-- Built by st-421-entry.js -->
</div>

---

<div id="summary-section">
  <h3>Your Bracket</h3>
  <table class="table" id="summary-table">
    <thead><tr><th>Stage</th><th>Your Picks</th></tr></thead>
    <tbody id="summary-body"></tbody>
  </table>
</div>

<div id="validation-panel">
  <strong id="validation-heading">Missing Info</strong>
  <ul id="validation-list"></ul>
</div>

<button class="btn btn-lg btn-success btn-block" id="submit-btn" disabled>Submit Predictions</button>

<div id="submission-result"></div>

<script src="{{ '/assets/js/st-421-entry.js' | relative_url }}"></script>
