// FIFA 2026 Group Stage Entry Form Logic

(function () {
  'use strict';

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbzsW-n6vbxIhT-WPZXeIx7uyBm3RNrwGZwm6jOci8WBdAzsLywRHGwe7qw6erMxJgxV/exec';

  var GROUPS = {
    A: ['Mexico', 'South Africa', 'Korea Republic', 'Czechia'],
    B: ['Canada', 'Switzerland', 'Qatar', 'Bosnia &amp; Herz.'],
    C: ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    D: ['USA', 'Paraguay', 'Australia', 'Türkiye'],
    E: ['Germany', 'Ecuador', "Côte d'Ivoire", 'Curaçao'],
    F: ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    G: ['Belgium', 'Egypt', 'IR Iran', 'New Zealand'],
    H: ['Spain', 'Uruguay', 'Saudi Arabia', 'Cabo Verde'],
    I: ['France', 'Senegal', 'Iraq', 'Norway'],
    J: ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    K: ['Portugal', 'Colombia', 'Congo DR', 'Uzbekistan'],
    L: ['England', 'Croatia', 'Ghana', 'Panama']
  };

  var GROUP_LETTERS = Object.keys(GROUPS);
  var STORAGE_KEY = 'fifa2026_group_entry';

  // ---- State ----

  function getR32Selections() {
    var selections = {};
    GROUP_LETTERS.forEach(function (g) {
      selections[g] = [];
      document.querySelectorAll('#r32-groups input[data-group="' + g + '"]:checked').forEach(function (cb) {
        selections[g].push(cb.getAttribute('data-team'));
      });
    });
    return selections;
  }

  function getThirdPlaceSelections() {
    var picks = [];
    document.querySelectorAll('#third-place-grid input[type="checkbox"]:checked').forEach(function (cb) {
      picks.push({ team: cb.getAttribute('data-team'), group: cb.getAttribute('data-group') });
    });
    return picks;
  }

  // ---- R32 Logic ----

  function onR32Change(group) {
    var checkboxes = document.querySelectorAll('#r32-groups input[data-group="' + group + '"]');
    var checked = document.querySelectorAll('#r32-groups input[data-group="' + group + '"]:checked');
    var count = checked.length;
    var card = document.getElementById('card-' + group);
    var badge = document.getElementById('badge-' + group);

    // Disable unchecked boxes when 2 are selected
    checkboxes.forEach(function (cb) {
      if (count >= 2 && !cb.checked) {
        cb.disabled = true;
      } else {
        cb.disabled = false;
      }
    });

    // Update badge
    if (count === 2) {
      badge.textContent = 'Done';
      badge.className = 'badge badge-success';
      card.classList.add('complete');
    } else if (count === 1) {
      badge.textContent = 'Pick 1 more';
      badge.className = 'badge badge-warning';
      card.classList.remove('complete');
    } else {
      badge.textContent = 'Pick 2';
      badge.className = 'badge badge-secondary';
      card.classList.remove('complete');
    }

    updateProgress();
    rebuildThirdPlace();
    validateAll();
    saveState();
  }

  function updateProgress() {
    var done = 0;
    GROUP_LETTERS.forEach(function (g) {
      if (document.querySelectorAll('#r32-groups input[data-group="' + g + '"]:checked').length === 2) {
        done++;
      }
    });
    var pct = Math.round((done / 12) * 100);
    var bar = document.querySelector('#progress-bar .progress-bar');
    bar.style.width = pct + '%';
    bar.textContent = done + ' / 12 groups';
  }

  // ---- Third Place Logic ----

  function rebuildThirdPlace() {
    var section = document.getElementById('third-place-section');
    var allDone = GROUP_LETTERS.every(function (g) {
      return document.querySelectorAll('#r32-groups input[data-group="' + g + '"]:checked').length === 2;
    });

    if (!allDone) {
      section.classList.remove('visible');
      return;
    }

    section.classList.add('visible');

    var r32 = getR32Selections();
    var existing = getThirdPlaceSelections();
    var existingTeams = existing.map(function (p) { return p.team; });

    var grid = document.getElementById('third-place-grid');
    grid.innerHTML = '';

    GROUP_LETTERS.forEach(function (g) {
      var remaining = GROUPS[g].filter(function (t) {
        return r32[g].indexOf(t) === -1;
      });
      var row = document.createElement('div');
      row.className = 'third-place-row';
      var label = document.createElement('span');
      label.className = 'third-place-group-label';
      label.textContent = 'Group ' + g;
      row.appendChild(label);
      remaining.forEach(function (team) {
        var span = document.createElement('span');
        span.className = 'third-place-item';
        var id = 'tp-' + g + '-' + team.replace(/[^a-zA-Z0-9]/g, '_');
        var wasChecked = existingTeams.indexOf(team) !== -1;
        span.innerHTML = '<input type="checkbox" data-group="' + g + '" data-team="' + team + '" id="' + id + '"' +
          (wasChecked ? ' checked' : '') + '> <label for="' + id + '">' + team + '</label>';
        row.appendChild(span);
      });
      grid.appendChild(row);
    });

    // Attach listeners
    grid.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
      cb.addEventListener('change', function () {
        onThirdChange();
      });
    });

    // Re-enforce constraints after rebuild
    enforceThirdPlaceConstraints();
  }

  function onThirdChange() {
    enforceThirdPlaceConstraints();
    updateThirdBadge();
    validateAll();
    saveState();
  }

  function enforceThirdPlaceConstraints() {
    var allCbs = document.querySelectorAll('#third-place-grid input[type="checkbox"]');
    var checked = document.querySelectorAll('#third-place-grid input[type="checkbox"]:checked');
    var totalChecked = checked.length;

    // Collect which groups already have a pick
    var groupsPicked = {};
    checked.forEach(function (cb) {
      groupsPicked[cb.getAttribute('data-group')] = true;
    });

    allCbs.forEach(function (cb) {
      if (cb.checked) {
        cb.disabled = false;
        return;
      }
      var g = cb.getAttribute('data-group');
      // Disable if 8 total reached OR this group already has a pick
      if (totalChecked >= 8 || groupsPicked[g]) {
        cb.disabled = true;
      } else {
        cb.disabled = false;
      }
    });
  }

  function updateThirdBadge() {
    var badge = document.getElementById('badge-third');
    var count = document.querySelectorAll('#third-place-grid input[type="checkbox"]:checked').length;
    if (count === 8) {
      badge.textContent = 'Done (8/8)';
      badge.className = 'badge badge-success';
    } else {
      badge.textContent = 'Pick ' + (8 - count) + ' more (' + count + '/8)';
      badge.className = 'badge badge-info';
    }
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

    var r32 = getR32Selections();
    var incomplete = GROUP_LETTERS.filter(function (g) { return r32[g].length !== 2; });
    if (incomplete.length > 0) {
      issues.push('Pick 2 teams in group' + (incomplete.length > 1 ? 's' : '') + ': ' + incomplete.join(', '));
    }

    var section = document.getElementById('third-place-section');
    if (!section.classList.contains('visible')) {
      issues.push('Complete all R32 picks to unlock third-place section');
    } else {
      var thirdCount = document.querySelectorAll('#third-place-grid input[type="checkbox"]:checked').length;
      if (thirdCount !== 8) {
        issues.push('Pick ' + (8 - thirdCount) + ' more third-place team' + (8 - thirdCount !== 1 ? 's' : '') + ' (' + thirdCount + '/8)');
      }
    }

    var panel = document.getElementById('validation-panel');
    var list = document.getElementById('validation-list');
    var btn = document.getElementById('submit-btn');

    if (issues.length === 0) {
      panel.classList.add('valid');
      list.innerHTML = '<li>All good — ready to submit!</li>';
      btn.disabled = false;
    } else {
      panel.classList.remove('valid');
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
      r32: getR32Selections(),
      thirdPlace: getThirdPlaceSelections()
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

      if (state.r32) {
        GROUP_LETTERS.forEach(function (g) {
          var picks = state.r32[g] || [];
          picks.forEach(function (team) {
            var cb = document.querySelector('input[data-group="' + g + '"][data-team="' + team + '"]');
            if (cb) cb.checked = true;
          });
          onR32Change(g);
        });
      }

      // Third place is rebuilt by onR32Change → rebuildThirdPlace
      // We need to re-check after rebuild
      if (state.thirdPlace && state.thirdPlace.length > 0) {
        // rebuildThirdPlace already restores from existing checked state,
        // but we need to manually check them after rebuild since the DOM was recreated
        setTimeout(function () {
          state.thirdPlace.forEach(function (pick) {
            var cb = document.querySelector('#third-place-grid input[data-group="' + pick.group + '"][data-team="' + pick.team + '"]');
            if (cb && !cb.checked) cb.checked = true;
          });
          enforceThirdPlaceConstraints();
          updateThirdBadge();
          validateAll();
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
      r32: getR32Selections(),
      thirdPlace: getThirdPlaceSelections()
    };

    if (APPS_SCRIPT_URL === 'PASTE_YOUR_APPS_SCRIPT_URL_HERE') {
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
        payload.name + '. Your picks have been recorded.</div>';
      btn.textContent = 'Submitted';
      // Clear storage after successful submit
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
    // R32 checkbox listeners
    document.querySelectorAll('#r32-groups input[type="checkbox"]').forEach(function (cb) {
      cb.addEventListener('change', function () {
        onR32Change(this.getAttribute('data-group'));
      });
    });

    // Name/email/location listeners
    document.getElementById('entry-name').addEventListener('input', function () {
      validateAll();
      saveState();
    });
    document.getElementById('entry-email').addEventListener('input', function () {
      validateAll();
      saveState();
    });
    document.getElementById('entry-location').addEventListener('input', function () {
      validateAll();
      saveState();
    });

    // Submit button
    document.getElementById('submit-btn').addEventListener('click', submitForm);

    // beforeunload warning
    window.addEventListener('beforeunload', function (e) {
      var hasData = document.getElementById('entry-name').value.trim() ||
        GROUP_LETTERS.some(function (g) {
          return document.querySelectorAll('#r32-groups input[data-group="' + g + '"]:checked').length > 0;
        });
      if (hasData) {
        e.preventDefault();
        e.returnValue = '';
      }
    });

    // Load saved state
    loadState();

    // Initial validation
    validateAll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
