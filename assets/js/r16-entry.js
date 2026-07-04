// FIFA 2026 — Round of 16 Entry Form Logic

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbzPduyPreZQ7r3oKVPBYwNLYZVvkr5uFi2-4DhFMVUD0UVTacM74fTnOhdia1ur6y_2mg/exec';
  var STORAGE_KEY = 'fifa2026_r16_entry';

  // 8 R16 matches
  // Source: active-contest/matches/r16-matches.csv
  var MATCHES = [
    { num: 1, team1: 'Canada', team2: 'Morocco', col: 'CAN v MAR' },
    { num: 2, team1: 'Paraguay', team2: 'France', col: 'PAR v FRA' },
    { num: 3, team1: 'Brazil', team2: 'Norway', col: 'BRA v NOR' },
    { num: 4, team1: 'Mexico', team2: 'England', col: 'MEX v ENG' },
    { num: 5, team1: 'Spain', team2: 'Portugal', col: 'ESP v POR' },
    { num: 6, team1: 'United States', team2: 'Belgium', col: 'USA v BEL' },
    { num: 7, team1: 'Egypt', team2: 'Argentina', col: 'EGY v ARG' },
    { num: 8, team1: 'Switzerland', team2: 'Colombia', col: 'SUI v COL' }
  ];

  // ISO country codes for flag-icons CSS library
  var COUNTRY_CODES = {
    'Canada': 'ca', 'Morocco': 'ma', 'Paraguay': 'py', 'France': 'fr',
    'Brazil': 'br', 'Norway': 'no', 'Mexico': 'mx', 'England': 'gb-eng',
    'Spain': 'es', 'Portugal': 'pt', 'United States': 'us', 'Belgium': 'be',
    'Egypt': 'eg', 'Switzerland': 'ch', 'Argentina': 'ar', 'Cape Verde': 'cv',
    'Ghana': 'gh', 'Colombia': 'co'
  };

  function flagHtml(team) {
    var code = COUNTRY_CODES[team];
    if (!code) return '';
    return '<span class="fi fi-' + code + '" style="margin-right:0.4em;"></span>';
  }

  // ---- Build Match Cards ----

  function displayName(team, slot) {
    return (team && team !== '?') ? team : (slot || 'TBD');
  }

  function displayNameWithFlag(team, slot) {
    if (team && team !== '?') {
      return flagHtml(team) + escapeHtml(team);
    }
    return escapeHtml(slot || 'TBD');
  }

  function isKnown(team) {
    return team && team !== '?';
  }

  function buildMatchCards() {
    var container = document.getElementById('r16-matches');
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

      var dataTeam1 = isKnown(m.team1) ? m.team1 : t1;
      var dataTeam2 = isKnown(m.team2) ? m.team2 : t2;

      col.innerHTML =
        '<div class="' + cardClass + '" id="card-' + m.num + '">' +
          '<h5>Match ' + m.num + ': ' + escapeHtml(t1) + ' vs ' + escapeHtml(t2) +
            ' <span class="' + badgeClass + '" id="badge-' + m.num + '">' + badgeText + '</span></h5>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + m.num + '" data-team="' + escapeAttr(dataTeam1) + '" id="' + id1 + '"' + disabledAttr + '> ' +
            '<label for="' + id1 + '">' + displayNameWithFlag(m.team1, m.slot1) + '</label>' +
          '</div>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + m.num + '" data-team="' + escapeAttr(dataTeam2) + '" id="' + id2 + '"' + disabledAttr + '> ' +
            '<label for="' + id2 + '">' + displayNameWithFlag(m.team2, m.slot2) + '</label>' +
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

  var dirtyAfterSubmit = false;

  function markDirty() {
    dirtyAfterSubmit = true;
    var btn = document.getElementById('submit-btn');
    if (btn.getAttribute('data-submitted') === 'true') {
      btn.textContent = 'Re-submit Predictions';
      btn.disabled = false;
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-success');
    }
  }

  // ---- State ----

  function getSelections() {
    var picks = {};
    MATCHES.forEach(function (m) {
      var checked = document.querySelector('input[name="match-' + m.num + '"]:checked');
      if (checked) {
        picks[m.col] = checked.getAttribute('data-team');
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
    markDirty();
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
      var key = m.col;
      var pick = picks[key] || '';
      var t1Flag = displayNameWithFlag(m.team1, m.slot1);
      var t2Flag = displayNameWithFlag(m.team2, m.slot2);
      var t1Class = pick === m.team1 ? 'pick-highlight' : (pick ? 'pick-not' : '');
      var t2Class = pick === m.team2 ? 'pick-highlight' : (pick ? 'pick-not' : '');
      rows += '<tr>' +
        '<td>' + m.num + '</td>' +
        '<td class="' + t1Class + '">' + t1Flag + '</td>' +
        '<td class="' + t2Class + '">' + t2Flag + '</td>' +
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
          var key = m.col;
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
    document.querySelectorAll('#r16-matches input[type="radio"]').forEach(function (rb) {
      rb.checked = false;
    });

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

    // Immediately show confirmation inside the button and turn it gray
    var now = new Date();
    var timestamp = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) +
      ' at ' + now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    btn.innerHTML = 'Submitted! Thanks, ' + escapeHtml(payload.name) + '.<br><small>' + timestamp + '</small>';
    btn.setAttribute('data-submitted', 'true');
    btn.classList.remove('btn-success');
    btn.classList.add('btn-secondary');
    result.innerHTML = '';
    dirtyAfterSubmit = false;

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
    buildMatchCards();

    // Match radio listeners
    document.querySelectorAll('#r16-matches input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        onMatchChange(this.getAttribute('data-match'));
      });
    });

    // Name/email/location listeners
    document.getElementById('entry-name').addEventListener('input', function () { validateAll(); saveState(); markDirty(); });
    document.getElementById('entry-email').addEventListener('input', function () { validateAll(); saveState(); markDirty(); });
    document.getElementById('entry-location').addEventListener('input', function () { validateAll(); saveState(); markDirty(); });

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
