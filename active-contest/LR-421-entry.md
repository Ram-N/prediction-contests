---
layout: page
title: "4-2-1 Long Range Contest"
description: "Predict the Semifinalists, Finalists, and World Cup Winner"
background: '/img/soccer/421-banner.png'
permalink: "/fifa-2026/421-entry"
---

<style>
  .group-card { border: 2px solid #dee2e6; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
  .group-card h4 { margin-bottom: 0.75rem; }
  .team-check { padding: 0.3rem 0; font-size: 1rem; }
  .team-check label { cursor: pointer; margin-left: 0.4rem; }
  .team-check input[type="checkbox"] { transform: scale(1.2); cursor: pointer; }
  .team-check input[type="checkbox"]:disabled { cursor: not-allowed; opacity: 0.4; }
  .team-check.selected-semi label { color: #155724; font-weight: 700; }

  .reveal-section { display: none; margin-top: 2rem; padding: 1.5rem; border-radius: 8px; }
  .reveal-section.visible { display: block; }

  #semi-section { background: #fff; }
  #finals-section { background: #f8f9ff; border: 2px solid #007bff; }
  #winner-section { background: #fff9e6; border: 2px solid #ffc107; }

  .pick-option { display: inline-block; margin: 0.5rem 0.75rem 0.5rem 0; }
  .pick-option label { cursor: pointer; margin-left: 0.4rem; font-size: 1.1rem; }
  .pick-option input[type="radio"] { transform: scale(1.3); cursor: pointer; }

  #semi-counter { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; }

  #validation-panel { margin-top: 1.5rem; padding: 1rem; border-radius: 8px; background: #fff3cd; border: 1px solid #ffc107; }
  #validation-panel.valid { background: #d4edda; border-color: #28a745; }
  #validation-panel ul { margin-bottom: 0; padding-left: 1.2rem; }

  #submit-btn { margin-top: 1rem; }
  #submit-btn:disabled { opacity: 0.5; }
  #submission-result { margin-top: 1rem; }

  .finalist-pick, .winner-pick { font-size: 1.15rem; padding: 0.4rem 0; }
</style>

## FIFA World Cup 2026 — 4-2-1 Long Range Predictions

Pick **4 Semifinalists**, then **2 Finalists**, then the **World Cup Winner**.

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

### Step 1: Pick 4 Semifinalists

Select **exactly 4 teams** from any groups.

<div id="semi-counter">0 / 4 semifinalists selected</div>

<div class="row" id="semi-groups">
  <!-- Group A -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group A</h4>
      <div class="team-check"><input type="checkbox" data-team="Mexico" id="semi-A-0"> <label for="semi-A-0">Mexico</label></div>
      <div class="team-check"><input type="checkbox" data-team="South Africa" id="semi-A-1"> <label for="semi-A-1">South Africa</label></div>
      <div class="team-check"><input type="checkbox" data-team="Korea Republic" id="semi-A-2"> <label for="semi-A-2">Korea Republic</label></div>
      <div class="team-check"><input type="checkbox" data-team="Czechia" id="semi-A-3"> <label for="semi-A-3">Czechia</label></div>
    </div>
  </div>
  <!-- Group B -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group B</h4>
      <div class="team-check"><input type="checkbox" data-team="Canada" id="semi-B-0"> <label for="semi-B-0">Canada</label></div>
      <div class="team-check"><input type="checkbox" data-team="Switzerland" id="semi-B-1"> <label for="semi-B-1">Switzerland</label></div>
      <div class="team-check"><input type="checkbox" data-team="Qatar" id="semi-B-2"> <label for="semi-B-2">Qatar</label></div>
      <div class="team-check"><input type="checkbox" data-team="Bosnia &amp; Herz." id="semi-B-3"> <label for="semi-B-3">Bosnia &amp; Herz.</label></div>
    </div>
  </div>
  <!-- Group C -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group C</h4>
      <div class="team-check"><input type="checkbox" data-team="Brazil" id="semi-C-0"> <label for="semi-C-0">Brazil</label></div>
      <div class="team-check"><input type="checkbox" data-team="Morocco" id="semi-C-1"> <label for="semi-C-1">Morocco</label></div>
      <div class="team-check"><input type="checkbox" data-team="Haiti" id="semi-C-2"> <label for="semi-C-2">Haiti</label></div>
      <div class="team-check"><input type="checkbox" data-team="Scotland" id="semi-C-3"> <label for="semi-C-3">Scotland</label></div>
    </div>
  </div>
  <!-- Group D -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group D</h4>
      <div class="team-check"><input type="checkbox" data-team="USA" id="semi-D-0"> <label for="semi-D-0">USA</label></div>
      <div class="team-check"><input type="checkbox" data-team="Paraguay" id="semi-D-1"> <label for="semi-D-1">Paraguay</label></div>
      <div class="team-check"><input type="checkbox" data-team="Australia" id="semi-D-2"> <label for="semi-D-2">Australia</label></div>
      <div class="team-check"><input type="checkbox" data-team="T&uuml;rkiye" id="semi-D-3"> <label for="semi-D-3">T&uuml;rkiye</label></div>
    </div>
  </div>
  <!-- Group E -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group E</h4>
      <div class="team-check"><input type="checkbox" data-team="Germany" id="semi-E-0"> <label for="semi-E-0">Germany</label></div>
      <div class="team-check"><input type="checkbox" data-team="Ecuador" id="semi-E-1"> <label for="semi-E-1">Ecuador</label></div>
      <div class="team-check"><input type="checkbox" data-team="C&ocirc;te d'Ivoire" id="semi-E-2"> <label for="semi-E-2">C&ocirc;te d'Ivoire</label></div>
      <div class="team-check"><input type="checkbox" data-team="Cura&ccedil;ao" id="semi-E-3"> <label for="semi-E-3">Cura&ccedil;ao</label></div>
    </div>
  </div>
  <!-- Group F -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group F</h4>
      <div class="team-check"><input type="checkbox" data-team="Netherlands" id="semi-F-0"> <label for="semi-F-0">Netherlands</label></div>
      <div class="team-check"><input type="checkbox" data-team="Japan" id="semi-F-1"> <label for="semi-F-1">Japan</label></div>
      <div class="team-check"><input type="checkbox" data-team="Sweden" id="semi-F-2"> <label for="semi-F-2">Sweden</label></div>
      <div class="team-check"><input type="checkbox" data-team="Tunisia" id="semi-F-3"> <label for="semi-F-3">Tunisia</label></div>
    </div>
  </div>
  <!-- Group G -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group G</h4>
      <div class="team-check"><input type="checkbox" data-team="Belgium" id="semi-G-0"> <label for="semi-G-0">Belgium</label></div>
      <div class="team-check"><input type="checkbox" data-team="Egypt" id="semi-G-1"> <label for="semi-G-1">Egypt</label></div>
      <div class="team-check"><input type="checkbox" data-team="IR Iran" id="semi-G-2"> <label for="semi-G-2">IR Iran</label></div>
      <div class="team-check"><input type="checkbox" data-team="New Zealand" id="semi-G-3"> <label for="semi-G-3">New Zealand</label></div>
    </div>
  </div>
  <!-- Group H -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group H</h4>
      <div class="team-check"><input type="checkbox" data-team="Spain" id="semi-H-0"> <label for="semi-H-0">Spain</label></div>
      <div class="team-check"><input type="checkbox" data-team="Uruguay" id="semi-H-1"> <label for="semi-H-1">Uruguay</label></div>
      <div class="team-check"><input type="checkbox" data-team="Saudi Arabia" id="semi-H-2"> <label for="semi-H-2">Saudi Arabia</label></div>
      <div class="team-check"><input type="checkbox" data-team="Cabo Verde" id="semi-H-3"> <label for="semi-H-3">Cabo Verde</label></div>
    </div>
  </div>
  <!-- Group I -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group I</h4>
      <div class="team-check"><input type="checkbox" data-team="France" id="semi-I-0"> <label for="semi-I-0">France</label></div>
      <div class="team-check"><input type="checkbox" data-team="Senegal" id="semi-I-1"> <label for="semi-I-1">Senegal</label></div>
      <div class="team-check"><input type="checkbox" data-team="Iraq" id="semi-I-2"> <label for="semi-I-2">Iraq</label></div>
      <div class="team-check"><input type="checkbox" data-team="Norway" id="semi-I-3"> <label for="semi-I-3">Norway</label></div>
    </div>
  </div>
  <!-- Group J -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group J</h4>
      <div class="team-check"><input type="checkbox" data-team="Argentina" id="semi-J-0"> <label for="semi-J-0">Argentina</label></div>
      <div class="team-check"><input type="checkbox" data-team="Algeria" id="semi-J-1"> <label for="semi-J-1">Algeria</label></div>
      <div class="team-check"><input type="checkbox" data-team="Austria" id="semi-J-2"> <label for="semi-J-2">Austria</label></div>
      <div class="team-check"><input type="checkbox" data-team="Jordan" id="semi-J-3"> <label for="semi-J-3">Jordan</label></div>
    </div>
  </div>
  <!-- Group K -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group K</h4>
      <div class="team-check"><input type="checkbox" data-team="Portugal" id="semi-K-0"> <label for="semi-K-0">Portugal</label></div>
      <div class="team-check"><input type="checkbox" data-team="Colombia" id="semi-K-1"> <label for="semi-K-1">Colombia</label></div>
      <div class="team-check"><input type="checkbox" data-team="Congo DR" id="semi-K-2"> <label for="semi-K-2">Congo DR</label></div>
      <div class="team-check"><input type="checkbox" data-team="Uzbekistan" id="semi-K-3"> <label for="semi-K-3">Uzbekistan</label></div>
    </div>
  </div>
  <!-- Group L -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card">
      <h4>Group L</h4>
      <div class="team-check"><input type="checkbox" data-team="England" id="semi-L-0"> <label for="semi-L-0">England</label></div>
      <div class="team-check"><input type="checkbox" data-team="Croatia" id="semi-L-1"> <label for="semi-L-1">Croatia</label></div>
      <div class="team-check"><input type="checkbox" data-team="Ghana" id="semi-L-2"> <label for="semi-L-2">Ghana</label></div>
      <div class="team-check"><input type="checkbox" data-team="Panama" id="semi-L-3"> <label for="semi-L-3">Panama</label></div>
    </div>
  </div>
</div>

---

<div id="finals-section" class="reveal-section">
  <h3>Step 2: Pick 2 Finalists</h3>
  <p>From your 4 semifinalists, who makes the <strong>Final</strong>?</p>
  <div id="finals-picks"></div>
</div>

<div id="winner-section" class="reveal-section">
  <h3>Step 3: Pick the World Cup Winner</h3>
  <p>Who lifts the trophy?</p>
  <div id="winner-picks"></div>
</div>

<div id="validation-panel">
  <strong>Checklist</strong>
  <ul id="validation-list"></ul>
</div>

<button class="btn btn-lg btn-success btn-block" id="submit-btn" disabled>Submit Predictions</button>

<div id="submission-result"></div>
