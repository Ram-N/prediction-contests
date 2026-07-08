// FIFA 2026 — Short-Term 4-2-1 Entry Form Logic (Bracket UI)

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbz0ooX4IA2NoKJlqNTuohNb_L9U4dVSYQuean-2JLCbxDtHOEL1bn2gl6IHpxmPKJI/exec';
  var STORAGE_KEY = 'fifa2026_st421_entry';

  var QF_MATCHES = [
    { num: 1, team1: 'France', team2: 'Morocco' },
    { num: 2, team1: 'Spain', team2: 'Belgium' },
    { num: 3, team1: 'England', team2: 'Norway' },
    { num: 4, team1: 'Argentina', team2: 'Switzerland' }
  ];

  var SF_PAIRINGS = [
    { num: 1, qfA: 1, qfB: 2 },
    { num: 2, qfA: 3, qfB: 4 }
  ];

  var COUNTRY_CODES = {
    'France': 'fr', 'Morocco': 'ma', 'England': 'gb-eng', 'Norway': 'no',
    'Canada': 'ca', 'Paraguay': 'py', 'Brazil': 'br', 'Mexico': 'mx',
    'Spain': 'es', 'Portugal': 'pt', 'United States': 'us', 'Belgium': 'be',
    'Egypt': 'eg', 'Switzerland': 'ch', 'Argentina': 'ar', 'Colombia': 'co',
    'Germany': 'de', 'Netherlands': 'nl', 'Japan': 'jp', 'Croatia': 'hr',
    'Uruguay': 'uy', 'Senegal': 'sn', 'South Africa': 'za', 'Ecuador': 'ec'
  };

  // ---- Utilities (unchanged) ----

  function flagHtml(team) {
    var code = COUNTRY_CODES[team];
    if (!code) return '';
    return '<span class="fi fi-' + code + '" style="margin-right:0.4em;"></span>';
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function escapeAttr(str) {
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ---- Build Bracket ----

  function buildBracket() {
    var container = document.getElementById('bracket');
    var html = '';

    // ── Bracket Half 1: QF1 + QF2 → SF1 ──
    html += '<div class="bracket-half" id="bracket-half-1">';
    html += '<div class="bracket-half-header">Semifinal 1 Bracket</div>';
    html += '<div class="bracket-tap-hint">\u261D Tap a team to pick the QF winner</div>';
    html += '<div class="bracket-half-grid">';
    html += matchSlotHtml('qf1', 'QF1 \u00B7 4 pts', QF_MATCHES[0]);
    html += matchSlotHtml('qf2', 'QF2 \u00B7 4 pts', QF_MATCHES[1]);
    html += '<div class="bracket-half-arrows">\u25BC \u25BC</div>';
    html += '<div class="bracket-tap-hint" style="grid-column:1/-1">\u261D Winners appear here \u2014 tap to pick the semifinalist</div>';
    html += matchSlotHtml('sf1', 'SF1 \u00B7 4 pts', null);
    html += '</div></div>';

    // ── Bracket Half 2: QF3 + QF4 → SF2 ──
    html += '<div class="bracket-half" id="bracket-half-2">';
    html += '<div class="bracket-half-header">Semifinal 2 Bracket</div>';
    html += '<div class="bracket-tap-hint">\u261D Tap a team to pick the QF winner</div>';
    html += '<div class="bracket-half-grid">';
    html += matchSlotHtml('qf3', 'QF3 \u00B7 4 pts', QF_MATCHES[2]);
    html += matchSlotHtml('qf4', 'QF4 \u00B7 4 pts', QF_MATCHES[3]);
    html += '<div class="bracket-half-arrows">\u25BC \u25BC</div>';
    html += '<div class="bracket-tap-hint" style="grid-column:1/-1">\u261D Winners appear here \u2014 tap to pick the semifinalist</div>';
    html += matchSlotHtml('sf2', 'SF2 \u00B7 4 pts', null);
    html += '</div></div>';

    // ── Final ──
    html += '<div class="bracket-finals">';
    html += '<div class="bracket-half-header">Final</div>';
    html += '<div class="bracket-tap-hint">\u261D SF winners appear here \u2014 tap to pick the champion</div>';
    html += matchSlotHtml('final', 'Final \u00B7 8 pts', null);
    html += '<div id="champion-display"><span class="champion-prompt">\uD83C\uDFC6 Pick the World Cup Winner</span></div>';
    html += '</div>';

    container.innerHTML = html;
  }

  function matchSlotHtml(slot, label, match) {
    var waiting = match ? '' : ' waiting';
    var html = '<div class="bracket-slot' + waiting + '" data-slot="' + slot + '">';
    html += '<div class="slot-header">' + escapeHtml(label) + '</div>';

    if (match) {
      html += teamDivHtml(slot, match.team1);
      html += teamDivHtml(slot, match.team2);
    } else {
      html += '<div class="bracket-team tbd" data-slot="' + slot + '">TBD</div>';
      html += '<div class="bracket-team tbd" data-slot="' + slot + '">TBD</div>';
    }

    html += '</div>';
    return html;
  }

  function teamDivHtml(slot, team) {
    return '<div class="bracket-team" data-slot="' + slot + '" data-team="' + escapeAttr(team) + '">' +
      flagHtml(team) + escapeHtml(team) +
    '</div>';
  }

  // ---- Click Handler (single delegation) ----

  function onBracketClick(e) {
    var el = e.target.closest('.bracket-team');
    if (!el) return;
    if (el.classList.contains('tbd')) return;

    var slot = el.getAttribute('data-slot');
    var team = el.getAttribute('data-team');

    if (el.classList.contains('picked')) {
      // Toggle off — unpick and clear downstream
      unpick(slot, team);
    } else {
      // Pick this team
      pick(slot, team);
    }

    handlePostSubmitChange();
    validateAll();
    saveState();
  }

  function pick(slot, team) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="' + slot + '"]');
    var teams = slotEl.querySelectorAll('.bracket-team:not(.tbd)');

    teams.forEach(function (t) {
      if (t.getAttribute('data-team') === team) {
        t.classList.add('picked');
        t.classList.remove('eliminated');
      } else {
        t.classList.add('eliminated');
        t.classList.remove('picked');
      }
    });

    cascadePick(slot, team);
  }

  function unpick(slot, team) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="' + slot + '"]');
    var teams = slotEl.querySelectorAll('.bracket-team:not(.tbd)');

    teams.forEach(function (t) {
      t.classList.remove('picked', 'eliminated');
    });

    clearDownstream(slot);
  }

  // ---- Cascade / Clear ----

  function cascadePick(slot, winner) {
    if (slot === 'qf1' || slot === 'qf2') {
      populateSFSlot('sf1', winner, slot);
    } else if (slot === 'qf3' || slot === 'qf4') {
      populateSFSlot('sf2', winner, slot);
    } else if (slot === 'sf1' || slot === 'sf2') {
      populateFinalSlot(winner, slot);
    } else if (slot === 'final') {
      updateChampion(winner);
    }
  }

  function clearDownstream(slot) {
    if (slot === 'qf1' || slot === 'qf2') {
      clearSFSlot('sf1', slot);
    } else if (slot === 'qf3' || slot === 'qf4') {
      clearSFSlot('sf2', slot);
    } else if (slot === 'sf1' || slot === 'sf2') {
      clearFinalSlot(slot);
    } else if (slot === 'final') {
      updateChampion(null);
    }
  }

  function populateSFSlot(sfSlot, winner, fromQF) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="' + sfSlot + '"]');
    var teamDivs = slotEl.querySelectorAll('.bracket-team');

    // Which position does this QF feed? qf1/qf3 = position 0, qf2/qf4 = position 1
    var pos = (fromQF === 'qf1' || fromQF === 'qf3') ? 0 : 1;
    var otherPos = pos === 0 ? 1 : 0;
    var div = teamDivs[pos];

    // If the team in this position was previously picked, clear downstream before replacing
    if (div.classList.contains('picked')) {
      clearDownstream(sfSlot);
    }

    // Check if existing team is different — if so, clear any pick state on the slot
    var existingTeam = div.getAttribute('data-team');
    if (existingTeam !== winner) {
      // Clear pick state on both teams in this SF
      teamDivs.forEach(function (t) {
        t.classList.remove('picked', 'eliminated');
      });
      clearDownstream(sfSlot);
    }

    // Set the team
    div.className = 'bracket-team';
    div.setAttribute('data-team', winner);
    div.innerHTML = flagHtml(winner) + escapeHtml(winner);

    // Check if the slot is now fully populated
    var otherDiv = teamDivs[otherPos];
    if (otherDiv.classList.contains('tbd')) {
      slotEl.classList.add('waiting');
    } else {
      slotEl.classList.remove('waiting');
    }
  }

  function clearSFSlot(sfSlot, fromQF) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="' + sfSlot + '"]');
    var teamDivs = slotEl.querySelectorAll('.bracket-team');
    var pos = (fromQF === 'qf1' || fromQF === 'qf3') ? 0 : 1;
    var div = teamDivs[pos];

    // Any pick in this SF match is now invalid — clear downstream
    var hadPick = false;
    teamDivs.forEach(function (t) {
      if (t.classList.contains('picked')) hadPick = true;
    });
    if (hadPick) {
      clearDownstream(sfSlot);
    }

    // Clear pick/eliminated state on both
    teamDivs.forEach(function (t) {
      t.classList.remove('picked', 'eliminated');
    });

    // Reset to TBD
    div.className = 'bracket-team tbd';
    div.removeAttribute('data-team');
    div.innerHTML = 'TBD';
    slotEl.classList.add('waiting');
  }

  function populateFinalSlot(winner, fromSF) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="final"]');
    var teamDivs = slotEl.querySelectorAll('.bracket-team');
    var pos = (fromSF === 'sf1') ? 0 : 1;
    var otherPos = pos === 0 ? 1 : 0;
    var div = teamDivs[pos];

    if (div.classList.contains('picked')) {
      updateChampion(null);
    }

    var existingTeam = div.getAttribute('data-team');
    if (existingTeam !== winner) {
      teamDivs.forEach(function (t) {
        t.classList.remove('picked', 'eliminated');
      });
      updateChampion(null);
    }

    div.className = 'bracket-team';
    div.setAttribute('data-team', winner);
    div.innerHTML = flagHtml(winner) + escapeHtml(winner);

    var otherDiv = teamDivs[otherPos];
    if (otherDiv.classList.contains('tbd')) {
      slotEl.classList.add('waiting');
    } else {
      slotEl.classList.remove('waiting');
    }
  }

  function clearFinalSlot(fromSF) {
    var slotEl = document.querySelector('.bracket-slot[data-slot="final"]');
    var teamDivs = slotEl.querySelectorAll('.bracket-team');
    var pos = (fromSF === 'sf1') ? 0 : 1;
    var div = teamDivs[pos];

    // Any pick in the Final is now invalid — clear champion
    var hadPick = false;
    teamDivs.forEach(function (t) {
      if (t.classList.contains('picked')) hadPick = true;
    });
    if (hadPick) {
      updateChampion(null);
    }

    teamDivs.forEach(function (t) {
      t.classList.remove('picked', 'eliminated');
    });

    div.className = 'bracket-team tbd';
    div.removeAttribute('data-team');
    div.innerHTML = 'TBD';
    slotEl.classList.add('waiting');
  }

  function updateChampion(team) {
    var el = document.getElementById('champion-display');
    if (team) {
      el.innerHTML = '<span class="trophy">\uD83C\uDFC6</span> ' + flagHtml(team) + '<strong>' + escapeHtml(team) + '</strong>';
      el.classList.add('has-winner');
    } else {
      el.innerHTML = '<span class="champion-prompt">\uD83C\uDFC6 Pick the World Cup Winner</span>';
      el.classList.remove('has-winner');
    }
  }

  // ---- State Readers ----

  function getQFPick(matchNum) {
    var slot = 'qf' + matchNum;
    var picked = document.querySelector('.bracket-slot[data-slot="' + slot + '"] .bracket-team.picked');
    return picked ? picked.getAttribute('data-team') : null;
  }

  function getSFPick(matchNum) {
    var slot = 'sf' + matchNum;
    var picked = document.querySelector('.bracket-slot[data-slot="' + slot + '"] .bracket-team.picked');
    return picked ? picked.getAttribute('data-team') : null;
  }

  function getWinnerPick() {
    var picked = document.querySelector('.bracket-slot[data-slot="final"] .bracket-team.picked');
    return picked ? picked.getAttribute('data-team') : null;
  }

  function countPickableQFs() {
    return QF_MATCHES.length;
  }

  function countPickedQFs() {
    var count = 0;
    QF_MATCHES.forEach(function (m) {
      if (getQFPick(m.num)) count++;
    });
    return count;
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

    var pickable = countPickableQFs();
    var picked = countPickedQFs();
    if (picked < pickable) {
      var remaining = pickable - picked;
      issues.push('Pick ' + remaining + ' more QF winner' + (remaining !== 1 ? 's' : '') + ' (' + picked + '/' + pickable + ')');
    }

    var sfCount = 0;
    SF_PAIRINGS.forEach(function (sf) { if (getSFPick(sf.num)) sfCount++; });
    if (sfCount < 2) {
      issues.push('Pick ' + (2 - sfCount) + ' more SF winner' + ((2 - sfCount) !== 1 ? 's' : '') + ' (' + sfCount + '/2)');
    }

    if (!getWinnerPick()) {
      issues.push('Pick the World Cup champion');
    }

    var panel = document.getElementById('validation-panel');
    var heading = document.getElementById('validation-heading');
    var list = document.getElementById('validation-list');
    var btn = document.getElementById('submit-btn');

    if (issues.length === 0) {
      panel.classList.add('valid');
      heading.textContent = 'Ready';
      list.innerHTML = '<li>All good \u2014 ready to submit!</li>';
      btn.disabled = false;
    } else {
      panel.classList.remove('valid');
      heading.textContent = 'Missing Info';
      list.innerHTML = issues.map(function (i) { return '<li>' + i + '</li>'; }).join('');
      btn.disabled = true;
    }

    updateSummary();
  }

  // ---- Summary Table ----

  function updateSummary() {
    var section = document.getElementById('summary-section');
    var body = document.getElementById('summary-body');

    var qfPicks = [];
    QF_MATCHES.forEach(function (m) {
      var pick = getQFPick(m.num);
      if (pick) qfPicks.push(pick);
    });

    var sfPicks = [];
    SF_PAIRINGS.forEach(function (sf) {
      var pick = getSFPick(sf.num);
      if (pick) sfPicks.push(pick);
    });

    var winner = getWinnerPick();

    if (qfPicks.length === 0 && sfPicks.length === 0 && !winner) {
      section.classList.remove('visible');
      return;
    }

    section.classList.add('visible');
    var rows = '';

    if (qfPicks.length > 0) {
      var qfHtml = qfPicks.map(function (t) { return flagHtml(t) + escapeHtml(t); }).join(', ');
      rows += '<tr><td><strong>Semifinalists</strong> (QF winners)</td><td>' + qfHtml + '</td></tr>';
    }
    if (sfPicks.length > 0) {
      var sfHtml = sfPicks.map(function (t) { return flagHtml(t) + escapeHtml(t); }).join(', ');
      rows += '<tr><td><strong>Finalists</strong> (SF winners)</td><td>' + sfHtml + '</td></tr>';
    }
    if (winner) {
      rows += '<tr><td><strong>Champion</strong></td><td class="pick-highlight">' + flagHtml(winner) + escapeHtml(winner) + '</td></tr>';
    }

    body.innerHTML = rows;
  }

  // ---- localStorage ----

  function saveState() {
    var qf = [];
    QF_MATCHES.forEach(function (m) {
      qf.push(getQFPick(m.num));
    });

    var sf = [];
    SF_PAIRINGS.forEach(function (s) {
      sf.push(getSFPick(s.num));
    });

    var state = {
      name: document.getElementById('entry-name').value,
      email: document.getElementById('entry-email').value,
      location: document.getElementById('entry-location').value,
      qf: qf,
      sf: sf,
      winner: getWinnerPick()
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

      // Restore QF picks — all DOM exists so no timeouts needed
      if (state.qf) {
        state.qf.forEach(function (team, i) {
          if (team) {
            var slot = 'qf' + (i + 1);
            pick(slot, team);
          }
        });
      }

      // Restore SF picks
      if (state.sf) {
        state.sf.forEach(function (team, i) {
          if (team) {
            var slot = 'sf' + (i + 1);
            pick(slot, team);
          }
        });
      }

      // Restore winner
      if (state.winner) {
        pick('final', state.winner);
      }
    } catch (e) { /* ignore corrupt data */ }
  }

  // ---- Post-Submit Change Detection ----

  function handlePostSubmitChange() {
    var btn = document.getElementById('submit-btn');
    if (btn.getAttribute('data-submitted') !== 'true') return;

    if (!confirm('Do you wish to re-submit your updated entries?')) return;

    // Re-activate the submit button
    btn.removeAttribute('data-submitted');
    btn.textContent = 'Submit Predictions';
    btn.classList.remove('btn-secondary');
    btn.classList.add('btn-success');
    btn.disabled = false;
  }

  // ---- Submission ----

  function submitForm() {
    var btn = document.getElementById('submit-btn');
    var result = document.getElementById('submission-result');
    btn.disabled = true;
    btn.textContent = 'Submitting...';
    result.innerHTML = '';

    var qf = [];
    QF_MATCHES.forEach(function (m) { qf.push(getQFPick(m.num) || ''); });

    var sf = [];
    SF_PAIRINGS.forEach(function (s) { sf.push(getSFPick(s.num) || ''); });

    var payload = {
      name: document.getElementById('entry-name').value.trim(),
      email: document.getElementById('entry-email').value.trim(),
      location: document.getElementById('entry-location').value.trim(),
      qf: qf,
      sf: sf,
      winner: getWinnerPick() || ''
    };

    if (APPS_SCRIPT_URL === 'PASTE_YOUR_ST421_APPS_SCRIPT_URL_HERE') {
      result.innerHTML = '<div class="alert alert-danger">Apps Script URL not configured. Contact the contest organizer.</div>';
      btn.disabled = false;
      btn.textContent = 'Submit Predictions';
      return;
    }

    var now = new Date();
    var timestamp = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) +
      ' at ' + now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    btn.innerHTML = 'Submitted! Thanks, ' + escapeHtml(payload.name) + '.<br><small>' + timestamp + '</small>';
    btn.setAttribute('data-submitted', 'true');
    btn.classList.remove('btn-success');
    btn.classList.add('btn-secondary');

    fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function () {
      // Button stays disabled+gray until user makes changes
    })
    .catch(function (err) {
      btn.textContent = 'Submit Predictions';
      btn.disabled = false;
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-success');
      result.innerHTML = '<div class="alert alert-danger">Submission may have failed: ' + err.message + '. Please try again.</div>';
    });
  }

  // ---- Init ----

  function init() {
    buildBracket();

    // Single click handler for entire bracket
    document.getElementById('bracket').addEventListener('click', onBracketClick);

    // Name/email/location listeners
    document.getElementById('entry-name').addEventListener('input', function () { handlePostSubmitChange(); validateAll(); saveState(); });
    document.getElementById('entry-email').addEventListener('input', function () { handlePostSubmitChange(); validateAll(); saveState(); });
    document.getElementById('entry-location').addEventListener('input', function () { handlePostSubmitChange(); validateAll(); saveState(); });

    // Clear selections
    document.getElementById('clear-selections').addEventListener('click', function (e) {
      e.preventDefault();
      if (!confirm('Clear all bracket selections and start fresh?')) return;
      // Reset all QF picks (clears downstream via unpick)
      QF_MATCHES.forEach(function (m) {
        var team = getQFPick(m.num);
        if (team) unpick('qf' + m.num, team);
      });
      handlePostSubmitChange();
      validateAll();
      saveState();
    });

    // Submit button
    document.getElementById('submit-btn').addEventListener('click', submitForm);

    // beforeunload warning
    window.addEventListener('beforeunload', function (e) {
      var hasData = document.getElementById('entry-name').value.trim() ||
        countPickedQFs() > 0;
      if (hasData) {
        e.preventDefault();
        e.returnValue = '';
      }
    });

    // Load saved state and run initial validation
    loadState();
    validateAll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
