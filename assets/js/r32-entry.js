// FIFA 2026 — Round of 32 Entry Form Logic

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbyYb9GcaEsCsT1BNcZKlT3VmEeK30K8i0YRKgcPL-rDW8y2_t4c2PsYq7BfLjSmw_b4/exec';
  var STORAGE_KEY = 'fifa2026_r32_entry';

  // 16 R32 matches (FIFA match numbers 73–88)
  // Auto-generated from data/FIFA-2026/r32-matches.csv
  // To update: edit the CSV, then run:
  //   cd data/scripts && uv run python update_r32_entry.py
  var MATCHES = [
    { num: 73, team1: 'South Africa', team2: 'Canada', slot1: 'Runner-up Group A', slot2: 'Runner-up Group B' },
    { num: 74, team1: 'Germany', team2: 'Paraguay', slot1: 'Winner Group E', slot2: 'Best 3rd A/B/C/D/F' },
    { num: 75, team1: 'Netherlands', team2: 'Morocco', slot1: 'Winner Group F', slot2: 'Runner-up Group C' },
    { num: 76, team1: 'Brazil', team2: 'Japan', slot1: 'Winner Group C', slot2: 'Runner-up Group F' },
    { num: 77, team1: 'France', team2: 'Sweden', slot1: 'Winner Group I', slot2: 'Best 3rd C/D/F/G/H' },
    { num: 78, team1: 'Ivory Coast', team2: 'Norway', slot1: 'Runner-up Group E', slot2: 'Runner-up Group I' },
    { num: 79, team1: 'Mexico', team2: 'Ecuador', slot1: 'Winner Group A', slot2: 'Best 3rd C/E/F/H/I' },
    { num: 80, team1: 'England', team2: 'YYY', slot1: 'Winner Group L', slot2: 'Best 3rd E/H/I/J/K' },
    { num: 81, team1: 'United States', team2: 'Bosnia & Herzegovina', slot1: 'Winner Group D', slot2: 'Best 3rd B/E/F/I/J' },
    { num: 82, team1: 'Belgium', team2: '?', slot1: 'Winner Group G', slot2: 'Best 3rd A/E/H/I/J' },
    { num: 83, team1: 'Croatia', team2: '?', slot1: 'Runner-up Group K', slot2: 'Runner-up Group L' },
    { num: 84, team1: 'Spain', team2: '?', slot1: 'Winner Group H', slot2: 'Runner-up Group J' },
    { num: 85, team1: 'Switzerland', team2: '?', slot1: 'Winner Group B', slot2: 'Best 3rd E/F/G/I/J' },
    { num: 86, team1: 'Argentina', team2: 'Cape Verde', slot1: 'Winner Group J', slot2: 'Runner-up Group H' },
    { num: 87, team1: 'Ghana', team2: 'YYY', slot1: 'Winner Group K', slot2: 'Best 3rd D/E/I/J/L' },
    { num: 88, team1: 'Australia', team2: 'Egypt', slot1: 'Runner-up Group D', slot2: 'Runner-up Group G' }
  ];

  // ---- Build Match Cards ----

  function displayName(team, slot) {
    return (team && team !== '?') ? team : slot;
  }

  function isKnown(team) {
    return team && team !== '?';
  }

  function buildMatchCards() {
    var container = document.getElementById('r32-matches');
    MATCHES.forEach(function (m) {
      var col = document.createElement('div');
      col.className = 'col-md-6';

      var t1 = displayName(m.team1, m.slot1);
      var t2 = displayName(m.team2, m.slot2);
      var bothKnown = isKnown(m.team1) && isKnown(m.team2);
      var disabledAttr = bothKnown ? '' : ' disabled';
      var cardClass = bothKnown ? 'match-card' : 'match-card disabled-match';

      var safe1 = t1.replace(/[^a-zA-Z0-9]/g, '_');
      var safe2 = t2.replace(/[^a-zA-Z0-9]/g, '_');
      var id1 = 'match' + m.num + '-' + safe1;
      var id2 = 'match' + m.num + '-' + safe2;
      var radioName = 'match-' + m.num;

      var badgeText = bothKnown ? 'Pick' : 'TBD';
      var badgeClass = bothKnown ? 'badge badge-secondary' : 'badge badge-warning';

      // For the data-team attribute, always use the actual team abbrev (not slot description)
      var dataTeam1 = isKnown(m.team1) ? m.team1 : t1;
      var dataTeam2 = isKnown(m.team2) ? m.team2 : t2;

      col.innerHTML =
        '<div class="' + cardClass + '" id="card-' + m.num + '">' +
          '<h5>Match ' + m.num + ': ' + escapeHtml(t1) + ' vs ' + escapeHtml(t2) +
            ' <span class="' + badgeClass + '" id="badge-' + m.num + '">' + badgeText + '</span></h5>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + m.num + '" data-team="' + escapeAttr(dataTeam1) + '" id="' + id1 + '"' + disabledAttr + '> ' +
            '<label for="' + id1 + '">' + escapeHtml(t1) + '</label>' +
          '</div>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + m.num + '" data-team="' + escapeAttr(dataTeam2) + '" id="' + id2 + '"' + disabledAttr + '> ' +
            '<label for="' + id2 + '">' + escapeHtml(t2) + '</label>' +
          '</div>' +
        '</div>';

      container.appendChild(col);
    });
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function escapeAttr(str) {
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ---- State ----

  function getSelections() {
    var picks = {};
    MATCHES.forEach(function (m) {
      var checked = document.querySelector('input[name="match-' + m.num + '"]:checked');
      if (checked) {
        picks['Match ' + m.num] = checked.getAttribute('data-team');
      }
    });
    return picks;
  }

  // ---- Match Change ----

  function onMatchChange(matchNum) {
    var card = document.getElementById('card-' + matchNum);
    var badge = document.getElementById('badge-' + matchNum);

    badge.textContent = 'Done';
    badge.className = 'badge badge-success';
    card.classList.add('complete');

    updateProgress();
    updateSummary();
    validateAll();
    saveState();
  }

  function countPickableMatches() {
    return MATCHES.filter(function (m) { return isKnown(m.team1) && isKnown(m.team2); }).length;
  }

  function updateProgress() {
    var pickable = countPickableMatches();
    var done = 0;
    MATCHES.forEach(function (m) {
      var picked = !!document.querySelector('input[name="match-' + m.num + '"]:checked');
      var bothKnown = isKnown(m.team1) && isKnown(m.team2);
      var card = document.getElementById('card-' + m.num);
      if (picked) {
        done++;
        if (card) card.classList.remove('needs-pick');
      } else if (bothKnown && card) {
        card.classList.add('needs-pick');
      }
    });
    var pct = pickable > 0 ? Math.round((done / pickable) * 100) : 0;
    var bar = document.querySelector('#progress-bar .progress-bar');
    bar.style.width = pct + '%';
    bar.textContent = done + ' / ' + pickable + ' available matches';
  }

  // ---- Summary Table ----

  function updateSummary() {
    var picks = getSelections();
    var section = document.getElementById('summary-section');
    var body = document.getElementById('summary-body');

    if (Object.keys(picks).length === 0) {
      section.classList.remove('visible');
      return;
    }

    section.classList.add('visible');
    var rows = '';
    MATCHES.forEach(function (m) {
      var key = 'Match ' + m.num;
      var pick = picks[key] || '';
      var t1Display = displayName(m.team1, m.slot1);
      var t2Display = displayName(m.team2, m.slot2);
      var t1Class = pick === m.team1 ? 'pick-highlight' : (pick ? 'pick-not' : '');
      var t2Class = pick === m.team2 ? 'pick-highlight' : (pick ? 'pick-not' : '');
      rows += '<tr>' +
        '<td>' + m.num + '</td>' +
        '<td class="' + t1Class + '">' + escapeHtml(t1Display) + '</td>' +
        '<td class="' + t2Class + '">' + escapeHtml(t2Display) + '</td>' +
        '</tr>';
    });
    body.innerHTML = rows;
  }

  // ---- Validation ----

  function validateAll() {
    var issues = [];
    var name = document.getElementById('entry-name').value.trim();
    var email = document.getElementById('entry-email').value.trim();
    var location = document.getElementById('entry-location').value.trim();

    if (!name) issues.push('Enter your name');
    if (!email) issues.push('Enter your email');
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) issues.push('Enter a valid email address');
    if (!location) issues.push('Enter your location');

    var picks = getSelections();
    var pickCount = Object.keys(picks).length;
    var pickable = countPickableMatches();
    if (pickCount < pickable) {
      var remaining = pickable - pickCount;
      issues.push('Pick a winner for ' + remaining + ' more match' + (remaining !== 1 ? 'es' : '') + ' (' + pickCount + '/' + pickable + ')');
    }

    var panel = document.getElementById('validation-panel');
    var heading = document.getElementById('validation-heading');
    var list = document.getElementById('validation-list');
    var btn = document.getElementById('submit-btn');

    if (issues.length === 0) {
      panel.classList.add('valid');
      heading.textContent = 'Ready';
      list.innerHTML = '<li>All good — ready to submit!</li>';
      btn.disabled = false;
    } else {
      panel.classList.remove('valid');
      heading.textContent = 'Missing Info';
      list.innerHTML = issues.map(function (i) { return '<li>' + i + '</li>'; }).join('');
      btn.disabled = true;
    }
  }

  // ---- localStorage ----

  function saveState() {
    var state = {
      name: document.getElementById('entry-name').value,
      email: document.getElementById('entry-email').value,
      location: document.getElementById('entry-location').value,
      picks: getSelections()
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) { /* ignore */ }
  }

  function loadState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      var state = JSON.parse(raw);

      if (state.name) document.getElementById('entry-name').value = state.name;
      if (state.email) document.getElementById('entry-email').value = state.email;
      if (state.location) document.getElementById('entry-location').value = state.location;

      if (state.picks) {
        MATCHES.forEach(function (m) {
          var key = 'Match ' + m.num;
          var team = state.picks[key];
          if (team) {
            var radio = document.querySelector('input[name="match-' + m.num + '"][data-team="' + team + '"]');
            if (radio) {
              radio.checked = true;
              onMatchChange(m.num);
            }
          }
        });
      }
    } catch (e) { /* ignore corrupt data */ }
  }

  // ---- Clear Selections ----

  function clearSelections() {
    // Uncheck all radio buttons
    document.querySelectorAll('#r32-matches input[type="radio"]').forEach(function (rb) {
      rb.checked = false;
    });

    // Reset card styling and badges
    MATCHES.forEach(function (m) {
      var card = document.getElementById('card-' + m.num);
      var badge = document.getElementById('badge-' + m.num);
      if (card) card.classList.remove('complete');
      if (badge) {
        var bothKnown = isKnown(m.team1) && isKnown(m.team2);
        badge.textContent = bothKnown ? 'Pick' : 'TBD';
        badge.className = bothKnown ? 'badge badge-secondary' : 'badge badge-warning';
      }
    });

    updateProgress();
    updateSummary();
    validateAll();
    saveState();
  }

  // ---- Submission ----

  function submitForm() {
    var btn = document.getElementById('submit-btn');
    var result = document.getElementById('submission-result');
    btn.disabled = true;
    btn.textContent = 'Submitting...';
    result.innerHTML = '';

    var picks = getSelections();
    var payload = {
      name: document.getElementById('entry-name').value.trim(),
      email: document.getElementById('entry-email').value.trim(),
      location: document.getElementById('entry-location').value.trim()
    };
    for (var key in picks) {
      if (picks.hasOwnProperty(key)) {
        payload[key] = picks[key];
      }
    }

    fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function () {
      // Check if this is a re-submission
      var isResubmit = btn.getAttribute('data-submitted') === 'true';
      var now = new Date();
      var timestamp = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) +
        ' at ' + now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
      var msg = isResubmit
        ? '<div class="alert alert-success"><strong>Predictions updated!</strong> Thanks, ' + escapeHtml(payload.name) + '. Your latest R32 picks have been recorded.<br><small>Submitted ' + timestamp + '</small></div>'
        : '<div class="alert alert-success"><strong>Predictions submitted!</strong> Thanks, ' + escapeHtml(payload.name) + '. Your R32 picks have been recorded.<br><small>Submitted ' + timestamp + '</small></div>';
      result.innerHTML = msg;
      btn.textContent = 'Re-submit Predictions';
      btn.setAttribute('data-submitted', 'true');
      btn.disabled = false;
      // Do NOT clear localStorage — allow re-submission
    })
    .catch(function (err) {
      result.innerHTML = '<div class="alert alert-danger">Submission failed: ' + err.message + '. Please try again.</div>';
      btn.disabled = false;
      btn.textContent = 'Submit Predictions';
    });
  }

  // ---- Init ----

  function init() {
    buildMatchCards();

    // Match radio listeners
    document.querySelectorAll('#r32-matches input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        onMatchChange(this.getAttribute('data-match'));
      });
    });

    // Name/email/location listeners
    document.getElementById('entry-name').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-email').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-location').addEventListener('input', function () { validateAll(); saveState(); });

    // Submit button
    document.getElementById('submit-btn').addEventListener('click', submitForm);

    // Clear buttons
    document.querySelectorAll('.clear-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (confirm('Clear all match selections? (Name, email, and location will be kept.)')) {
          clearSelections();
        }
      });
    });

    // beforeunload warning
    window.addEventListener('beforeunload', function (e) {
      var hasData = document.getElementById('entry-name').value.trim() ||
        Object.keys(getSelections()).length > 0;
      if (hasData) {
        e.preventDefault();
        e.returnValue = '';
      }
    });

    // Load saved state
    loadState();

    // Initial validation and summary
    updateSummary();
    validateAll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/*
 * ---- Google Apps Script (paste into your Google Sheet's script editor) ----
 */

