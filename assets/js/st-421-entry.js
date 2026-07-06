// FIFA 2026 — Short-Term 4-2-1 Entry Form Logic

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'PASTE_YOUR_ST421_APPS_SCRIPT_URL_HERE';
  var STORAGE_KEY = 'fifa2026_st421_entry';

  // Quarterfinal matches — update team names as they become known
  // SF pairings: QF1 winner vs QF2 winner, QF3 winner vs QF4 winner
  var QF_MATCHES = [
    { num: 1, team1: 'France', team2: 'Morocco' },
    { num: 2, team1: '?', team2: '?', slot1: 'W(QF1)', slot2: 'W(QF2)' },
    { num: 3, team1: 'England', team2: 'Norway' },
    { num: 4, team1: '?', team2: '?', slot1: 'W(QF3)', slot2: 'W(QF4)' }
  ];

  // SF bracket: SF1 = QF1 winner vs QF2 winner, SF2 = QF3 winner vs QF4 winner
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

  function isKnown(team) {
    return team && team !== '?';
  }

  function displayName(team, slot) {
    return (team && team !== '?') ? team : (slot || 'TBD');
  }

  function displayNameWithFlag(team, slot) {
    if (team && team !== '?') {
      return flagHtml(team) + escapeHtml(team);
    }
    return escapeHtml(slot || 'TBD');
  }

  // ---- Build QF Match Cards ----

  function buildQFCards() {
    var container = document.getElementById('qf-matches');
    QF_MATCHES.forEach(function (m) {
      var col = document.createElement('div');
      col.className = 'col-md-6';

      var t1 = displayName(m.team1, m.slot1);
      var t2 = displayName(m.team2, m.slot2);
      var bothKnown = isKnown(m.team1) && isKnown(m.team2);
      var disabledAttr = bothKnown ? '' : ' disabled';
      var cardClass = bothKnown ? 'match-card' : 'match-card disabled-match';

      var safe1 = t1.replace(/[^a-zA-Z0-9]/g, '_');
      var safe2 = t2.replace(/[^a-zA-Z0-9]/g, '_');
      var id1 = 'qf' + m.num + '-' + safe1;
      var id2 = 'qf' + m.num + '-' + safe2;
      var radioName = 'qf-' + m.num;

      var badgeText = bothKnown ? 'Pick' : 'TBD';
      var badgeClass = bothKnown ? 'badge badge-secondary' : 'badge badge-warning';

      var dataTeam1 = isKnown(m.team1) ? m.team1 : t1;
      var dataTeam2 = isKnown(m.team2) ? m.team2 : t2;

      // Bracket hint
      var hint = '';
      if (m.num === 1 || m.num === 2) {
        hint = '<div class="bracket-hint">SF1 bracket</div>';
      } else {
        hint = '<div class="bracket-hint">SF2 bracket</div>';
      }

      col.innerHTML =
        '<div class="' + cardClass + '" id="qf-card-' + m.num + '">' +
          '<h5>QF' + m.num + ': ' + escapeHtml(t1) + ' vs ' + escapeHtml(t2) +
            ' <span class="' + badgeClass + '" id="qf-badge-' + m.num + '">' + badgeText + '</span></h5>' +
          hint +
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

  // ---- QF State ----

  function getQFPick(matchNum) {
    var radio = document.querySelector('input[name="qf-' + matchNum + '"]:checked');
    return radio ? radio.getAttribute('data-team') : null;
  }

  function countPickableQFs() {
    return QF_MATCHES.filter(function (m) { return isKnown(m.team1) && isKnown(m.team2); }).length;
  }

  function countPickedQFs() {
    var count = 0;
    QF_MATCHES.forEach(function (m) {
      if (isKnown(m.team1) && isKnown(m.team2) && getQFPick(m.num)) count++;
    });
    return count;
  }

  function allPickableQFsDone() {
    return countPickedQFs() === countPickableQFs();
  }

  function onQFChange(matchNum) {
    var card = document.getElementById('qf-card-' + matchNum);
    var badge = document.getElementById('qf-badge-' + matchNum);
    badge.textContent = 'Done';
    badge.className = 'badge badge-success';
    card.classList.add('complete');

    rebuildSF();
    validateAll();
    saveState();
  }

  // ---- SF Section ----

  function rebuildSF() {
    var section = document.getElementById('sf-section');
    var container = document.getElementById('sf-matches');

    if (!allPickableQFsDone()) {
      section.classList.remove('visible');
      // Also hide final
      document.getElementById('final-section').classList.remove('visible');
      return;
    }

    // Preserve existing SF picks
    var existingSF = {};
    SF_PAIRINGS.forEach(function (sf) {
      var pick = getSFPick(sf.num);
      if (pick) existingSF[sf.num] = pick;
    });

    container.innerHTML = '';
    section.classList.add('visible');

    SF_PAIRINGS.forEach(function (sf) {
      var teamA = getQFPick(sf.qfA);
      var teamB = getQFPick(sf.qfB);

      if (!teamA || !teamB) return; // shouldn't happen if allPickableQFsDone

      var col = document.createElement('div');
      col.className = 'col-md-6';

      var safeA = teamA.replace(/[^a-zA-Z0-9]/g, '_');
      var safeB = teamB.replace(/[^a-zA-Z0-9]/g, '_');
      var idA = 'sf' + sf.num + '-' + safeA;
      var idB = 'sf' + sf.num + '-' + safeB;
      var radioName = 'sf-' + sf.num;

      var wasCheckedA = existingSF[sf.num] === teamA;
      var wasCheckedB = existingSF[sf.num] === teamB;

      col.innerHTML =
        '<div class="match-card" id="sf-card-' + sf.num + '">' +
          '<h5>SF' + sf.num + ': ' + escapeHtml(teamA) + ' vs ' + escapeHtml(teamB) +
            ' <span class="badge badge-secondary" id="sf-badge-' + sf.num + '">Pick</span></h5>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + sf.num + '" data-team="' + escapeAttr(teamA) + '" id="' + idA + '"' + (wasCheckedA ? ' checked' : '') + '> ' +
            '<label for="' + idA + '">' + flagHtml(teamA) + escapeHtml(teamA) + '</label>' +
          '</div>' +
          '<div class="match-pick">' +
            '<input type="radio" name="' + radioName + '" data-match="' + sf.num + '" data-team="' + escapeAttr(teamB) + '" id="' + idB + '"' + (wasCheckedB ? ' checked' : '') + '> ' +
            '<label for="' + idB + '">' + flagHtml(teamB) + escapeHtml(teamB) + '</label>' +
          '</div>' +
        '</div>';

      container.appendChild(col);

      // Update badge if already picked
      if (wasCheckedA || wasCheckedB) {
        var badge = document.getElementById('sf-badge-' + sf.num);
        var card = document.getElementById('sf-card-' + sf.num);
        badge.textContent = 'Done';
        badge.className = 'badge badge-success';
        card.classList.add('complete');
      }
    });

    // Attach SF listeners
    container.querySelectorAll('input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        onSFChange(this.getAttribute('data-match'));
      });
    });

    rebuildFinal();
  }

  function getSFPick(matchNum) {
    var radio = document.querySelector('input[name="sf-' + matchNum + '"]:checked');
    return radio ? radio.getAttribute('data-team') : null;
  }

  function allSFsDone() {
    return SF_PAIRINGS.every(function (sf) { return !!getSFPick(sf.num); });
  }

  function onSFChange(matchNum) {
    var card = document.getElementById('sf-card-' + matchNum);
    var badge = document.getElementById('sf-badge-' + matchNum);
    badge.textContent = 'Done';
    badge.className = 'badge badge-success';
    card.classList.add('complete');

    rebuildFinal();
    validateAll();
    saveState();
  }

  // ---- Final Section ----

  function rebuildFinal() {
    var section = document.getElementById('final-section');
    var container = document.getElementById('final-match');

    if (!allSFsDone()) {
      section.classList.remove('visible');
      return;
    }

    var teamA = getSFPick(1);
    var teamB = getSFPick(2);

    // Preserve existing winner pick
    var existingWinner = getWinnerPick();

    container.innerHTML = '';
    section.classList.add('visible');

    var col = document.createElement('div');
    col.className = 'col-md-6';

    var safeA = teamA.replace(/[^a-zA-Z0-9]/g, '_');
    var safeB = teamB.replace(/[^a-zA-Z0-9]/g, '_');
    var idA = 'final-' + safeA;
    var idB = 'final-' + safeB;

    var wasCheckedA = existingWinner === teamA;
    var wasCheckedB = existingWinner === teamB;

    col.innerHTML =
      '<div class="match-card" id="final-card">' +
        '<h5>Final: ' + escapeHtml(teamA) + ' vs ' + escapeHtml(teamB) +
          ' <span class="badge badge-secondary" id="final-badge">Pick</span></h5>' +
        '<div class="match-pick">' +
          '<input type="radio" name="winner" data-team="' + escapeAttr(teamA) + '" id="' + idA + '"' + (wasCheckedA ? ' checked' : '') + '> ' +
          '<label for="' + idA + '">' + flagHtml(teamA) + escapeHtml(teamA) + '</label>' +
        '</div>' +
        '<div class="match-pick">' +
          '<input type="radio" name="winner" data-team="' + escapeAttr(teamB) + '" id="' + idB + '"' + (wasCheckedB ? ' checked' : '') + '> ' +
          '<label for="' + idB + '">' + flagHtml(teamB) + escapeHtml(teamB) + '</label>' +
        '</div>' +
      '</div>';

    container.appendChild(col);

    // Update badge if already picked
    if (wasCheckedA || wasCheckedB) {
      var badge = document.getElementById('final-badge');
      var card = document.getElementById('final-card');
      badge.textContent = 'Done';
      badge.className = 'badge badge-success';
      card.classList.add('complete');
    }

    // Attach final listeners
    container.querySelectorAll('input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        var badge = document.getElementById('final-badge');
        var card = document.getElementById('final-card');
        badge.textContent = 'Done';
        badge.className = 'badge badge-success';
        card.classList.add('complete');
        validateAll();
        saveState();
      });
    });
  }

  function getWinnerPick() {
    var radio = document.querySelector('input[name="winner"]:checked');
    return radio ? radio.getAttribute('data-team') : null;
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

    if (allPickableQFsDone()) {
      var sfCount = 0;
      SF_PAIRINGS.forEach(function (sf) { if (getSFPick(sf.num)) sfCount++; });
      if (sfCount < 2) {
        issues.push('Pick ' + (2 - sfCount) + ' more SF winner' + ((2 - sfCount) !== 1 ? 's' : '') + ' (' + sfCount + '/2)');
      }

      if (allSFsDone() && !getWinnerPick()) {
        issues.push('Pick the World Cup champion');
      }
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

      // Restore QF picks
      if (state.qf) {
        state.qf.forEach(function (team, i) {
          if (team) {
            var matchNum = i + 1;
            var radio = document.querySelector('input[name="qf-' + matchNum + '"][data-team="' + team + '"]');
            if (radio && !radio.disabled) {
              radio.checked = true;
              var card = document.getElementById('qf-card-' + matchNum);
              var badge = document.getElementById('qf-badge-' + matchNum);
              if (badge) { badge.textContent = 'Done'; badge.className = 'badge badge-success'; }
              if (card) card.classList.add('complete');
            }
          }
        });
      }

      // Rebuild SF from QF picks
      rebuildSF();

      // Restore SF picks
      if (state.sf && state.sf.length > 0) {
        setTimeout(function () {
          state.sf.forEach(function (team, i) {
            if (team) {
              var sfNum = i + 1;
              var radio = document.querySelector('input[name="sf-' + sfNum + '"][data-team="' + team + '"]');
              if (radio) {
                radio.checked = true;
                var card = document.getElementById('sf-card-' + sfNum);
                var badge = document.getElementById('sf-badge-' + sfNum);
                if (badge) { badge.textContent = 'Done'; badge.className = 'badge badge-success'; }
                if (card) card.classList.add('complete');
              }
            }
          });

          rebuildFinal();

          // Restore winner
          if (state.winner) {
            setTimeout(function () {
              var radio = document.querySelector('input[name="winner"][data-team="' + state.winner + '"]');
              if (radio) {
                radio.checked = true;
                var badge = document.getElementById('final-badge');
                var card = document.getElementById('final-card');
                if (badge) { badge.textContent = 'Done'; badge.className = 'badge badge-success'; }
                if (card) card.classList.add('complete');
              }
              validateAll();
            }, 50);
          } else {
            validateAll();
          }
        }, 50);
      }
    } catch (e) { /* ignore corrupt data */ }
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

    // Show immediate confirmation
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
    buildQFCards();

    // QF radio listeners
    document.querySelectorAll('#qf-matches input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        onQFChange(parseInt(this.getAttribute('data-match'), 10));
      });
    });

    // Name/email/location listeners
    document.getElementById('entry-name').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-email').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-location').addEventListener('input', function () { validateAll(); saveState(); });

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
