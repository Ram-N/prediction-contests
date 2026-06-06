// FIFA 2026 — 4-2-1 Long Range Entry Form Logic

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwF_hfQbEzLwDF1OrmbXjZ6ns0E4CUtX89wzCDdVL5p8cLv1JOhtT-_5nVByIM1pwBF/exec';
  var STORAGE_KEY = 'fifa2026_421_entry';

  // ---- Semifinalist Logic ----

  function getSemiSelections() {
    var teams = [];
    document.querySelectorAll('#semi-groups input[type="checkbox"]:checked').forEach(function (cb) {
      teams.push(cb.getAttribute('data-team'));
    });
    return teams;
  }

  function onSemiChange() {
    var allCbs = document.querySelectorAll('#semi-groups input[type="checkbox"]');
    var checked = document.querySelectorAll('#semi-groups input[type="checkbox"]:checked');
    var count = checked.length;

    // Update counter
    var counter = document.getElementById('semi-counter');
    counter.textContent = count + ' / 4 semifinalists selected';

    // Disable unchecked when 4 selected
    allCbs.forEach(function (cb) {
      if (count >= 4 && !cb.checked) {
        cb.disabled = true;
      } else {
        cb.disabled = false;
      }
    });

    // Highlight selected
    allCbs.forEach(function (cb) {
      var wrapper = cb.closest('.team-check');
      if (cb.checked) {
        wrapper.classList.add('selected-semi');
      } else {
        wrapper.classList.remove('selected-semi');
      }
    });

    rebuildFinals();
    validateAll();
    saveState();
  }

  // ---- Finals Logic ----

  function rebuildFinals() {
    var semis = getSemiSelections();
    var section = document.getElementById('finals-section');
    var container = document.getElementById('finals-picks');

    if (semis.length !== 4) {
      section.classList.remove('visible');
      // Also hide winner if finals hidden
      document.getElementById('winner-section').classList.remove('visible');
      return;
    }

    section.classList.add('visible');

    // Preserve existing selections
    var existingFinals = getFinalsSelections();

    container.innerHTML = '';
    semis.forEach(function (team) {
      var div = document.createElement('div');
      div.className = 'finalist-pick pick-option';
      var id = 'fin-' + team.replace(/[^a-zA-Z0-9]/g, '_');
      var wasChecked = existingFinals.indexOf(team) !== -1;
      div.innerHTML = '<input type="checkbox" data-team="' + team + '" id="' + id + '"' +
        (wasChecked ? ' checked' : '') + '> <label for="' + id + '">' + team + '</label>';
      container.appendChild(div);
    });

    container.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
      cb.addEventListener('change', onFinalsChange);
    });

    enforceFinalsConstraints();
    rebuildWinner();
  }

  function getFinalsSelections() {
    var teams = [];
    document.querySelectorAll('#finals-picks input[type="checkbox"]:checked').forEach(function (cb) {
      teams.push(cb.getAttribute('data-team'));
    });
    return teams;
  }

  function onFinalsChange() {
    enforceFinalsConstraints();
    rebuildWinner();
    validateAll();
    saveState();
  }

  function enforceFinalsConstraints() {
    var allCbs = document.querySelectorAll('#finals-picks input[type="checkbox"]');
    var checked = document.querySelectorAll('#finals-picks input[type="checkbox"]:checked');
    var count = checked.length;

    allCbs.forEach(function (cb) {
      if (count >= 2 && !cb.checked) {
        cb.disabled = true;
      } else {
        cb.disabled = false;
      }
    });
  }

  // ---- Winner Logic ----

  function rebuildWinner() {
    var finals = getFinalsSelections();
    var section = document.getElementById('winner-section');
    var container = document.getElementById('winner-picks');

    if (finals.length !== 2) {
      section.classList.remove('visible');
      return;
    }

    section.classList.add('visible');

    var existingWinner = getWinnerSelection();

    container.innerHTML = '';
    finals.forEach(function (team) {
      var div = document.createElement('div');
      div.className = 'winner-pick pick-option';
      var id = 'win-' + team.replace(/[^a-zA-Z0-9]/g, '_');
      var wasChecked = existingWinner === team;
      div.innerHTML = '<input type="radio" name="winner" data-team="' + team + '" id="' + id + '"' +
        (wasChecked ? ' checked' : '') + '> <label for="' + id + '">' + team + '</label>';
      container.appendChild(div);
    });

    container.querySelectorAll('input[type="radio"]').forEach(function (rb) {
      rb.addEventListener('change', function () {
        validateAll();
        saveState();
      });
    });
  }

  function getWinnerSelection() {
    var el = document.querySelector('#winner-picks input[type="radio"]:checked');
    return el ? el.getAttribute('data-team') : null;
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

    var semis = getSemiSelections();
    if (semis.length !== 4) {
      issues.push('Pick ' + (4 - semis.length) + ' more semifinalist' + (4 - semis.length !== 1 ? 's' : '') + ' (' + semis.length + '/4)');
    }

    var finals = getFinalsSelections();
    if (semis.length === 4 && finals.length !== 2) {
      issues.push('Pick ' + (2 - finals.length) + ' more finalist' + (2 - finals.length !== 1 ? 's' : '') + ' (' + finals.length + '/2)');
    }

    var winner = getWinnerSelection();
    if (finals.length === 2 && !winner) {
      issues.push('Pick the World Cup winner');
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

    updateSummary(semis, finals, winner);
  }

  // ---- Summary Table ----

  function updateSummary(semis, finals, winner) {
    var section = document.getElementById('summary-section');
    var body = document.getElementById('summary-body');

    if (semis.length === 0 && finals.length === 0 && !winner) {
      section.classList.remove('visible');
      return;
    }

    section.classList.add('visible');
    var rows = '';

    if (semis.length > 0) {
      rows += '<tr><td><strong>Semifinalists</strong></td><td>' + semis.join(', ') + '</td></tr>';
    }
    if (finals.length > 0) {
      rows += '<tr><td><strong>Finalists</strong></td><td>' + finals.join(', ') + '</td></tr>';
    }
    if (winner) {
      rows += '<tr><td><strong>Winner</strong></td><td>' + winner + '</td></tr>';
    }

    body.innerHTML = rows;
  }

  // ---- localStorage ----

  function saveState() {
    var state = {
      name: document.getElementById('entry-name').value,
      email: document.getElementById('entry-email').value,
      location: document.getElementById('entry-location').value,
      semis: getSemiSelections(),
      finals: getFinalsSelections(),
      winner: getWinnerSelection()
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

      if (state.semis && state.semis.length > 0) {
        state.semis.forEach(function (team) {
          var cb = document.querySelector('#semi-groups input[data-team="' + team + '"]');
          if (cb) cb.checked = true;
        });
        onSemiChange();
      }

      // Finals and winner restored via rebuild callbacks from onSemiChange
      if (state.finals && state.finals.length > 0) {
        setTimeout(function () {
          state.finals.forEach(function (team) {
            var cb = document.querySelector('#finals-picks input[data-team="' + team + '"]');
            if (cb && !cb.checked) cb.checked = true;
          });
          enforceFinalsConstraints();
          rebuildWinner();

          if (state.winner) {
            setTimeout(function () {
              var rb = document.querySelector('#winner-picks input[data-team="' + state.winner + '"]');
              if (rb) rb.checked = true;
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

    var payload = {
      name: document.getElementById('entry-name').value.trim(),
      email: document.getElementById('entry-email').value.trim(),
      location: document.getElementById('entry-location').value.trim(),
      semis: getSemiSelections(),
      finals: getFinalsSelections(),
      winner: getWinnerSelection()
    };

    if (APPS_SCRIPT_URL === 'PASTE_YOUR_421_APPS_SCRIPT_URL_HERE') {
      result.innerHTML = '<div class="alert alert-danger">Apps Script URL not configured. Contact the contest organizer.</div>';
      btn.disabled = false;
      btn.textContent = 'Submit Predictions';
      return;
    }

    fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function () {
      result.innerHTML = '<div class="alert alert-success"><strong>Predictions submitted!</strong> Thanks, ' +
        payload.name + '. Your 4-2-1 picks have been recorded.</div>';
      btn.textContent = 'Submitted';
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
    })
    .catch(function (err) {
      result.innerHTML = '<div class="alert alert-danger">Submission failed: ' + err.message + '. Please try again.</div>';
      btn.disabled = false;
      btn.textContent = 'Submit Predictions';
    });
  }

  // ---- Init ----

  function init() {
    document.querySelectorAll('#semi-groups input[type="checkbox"]').forEach(function (cb) {
      cb.addEventListener('change', onSemiChange);
    });

    document.getElementById('entry-name').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-email').addEventListener('input', function () { validateAll(); saveState(); });
    document.getElementById('entry-location').addEventListener('input', function () { validateAll(); saveState(); });

    document.getElementById('submit-btn').addEventListener('click', submitForm);

    window.addEventListener('beforeunload', function (e) {
      var hasData = document.getElementById('entry-name').value.trim() ||
        document.querySelectorAll('#semi-groups input[type="checkbox"]:checked').length > 0;
      if (hasData) {
        e.preventDefault();
        e.returnValue = '';
      }
    });

    loadState();
    validateAll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
