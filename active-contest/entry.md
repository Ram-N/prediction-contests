---
layout: page
title: "Entry Form - FIFA 2026 Group Stage"
description: "Submit your Group Stage predictions"
background: '/img/soccer/bg_fifa.webp'
permalink: "/fifa-2026/entry"
---

<style>
  .group-card { border: 2px solid #dee2e6; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
  .group-card.complete { border-color: #28a745; }
  .group-card .badge { font-size: 0.85rem; }
  .group-card h4 { margin-bottom: 0.75rem; }
  .team-check { padding: 0.3rem 0; font-size: 1rem; }
  .team-check label { cursor: pointer; margin-left: 0.4rem; }
  .team-check input[type="checkbox"] { transform: scale(1.2); cursor: pointer; }
  .team-check input[type="checkbox"]:disabled { cursor: not-allowed; opacity: 0.4; }

  #third-place-section { display: none; margin-top: 2rem; padding: 1.5rem; border: 2px solid #007bff; border-radius: 8px; background: #f8f9ff; }
  #third-place-section.visible { display: block; }
  #third-place-grid { display: flex; flex-direction: column; gap: 0.4rem; }
  .third-place-row { display: flex; align-items: center; gap: 1.5rem; padding: 0.5rem 0; border-bottom: 2px solid #adb5bd; }
  .third-place-row:last-child { border-bottom: none; }
  .third-place-row:first-child { padding-top: 0; }
  .third-place-group-label { font-weight: 700; min-width: 5rem; }

  #validation-panel { margin-top: 1.5rem; padding: 1rem; border-radius: 8px; background: #fff3cd; border: 1px solid #ffc107; }
  #validation-panel.valid { background: #d4edda; border-color: #28a745; }
  #validation-panel ul { margin-bottom: 0; padding-left: 1.2rem; }

  #submit-btn { margin-top: 1rem; }
  #submit-btn:disabled { opacity: 0.5; }

  #progress-bar { margin-bottom: 1.5rem; }
  #progress-bar .progress { height: 1.5rem; border-radius: 0.5rem; }
  #progress-bar .progress-bar { font-size: 0.9rem; font-weight: 600; transition: width 0.3s; }

  #submission-result { margin-top: 1rem; }

  .third-place-item label { cursor: pointer; margin-left: 0.4rem; }
  .third-place-item input[type="checkbox"] { transform: scale(1.2); cursor: pointer; }
  .third-place-item input[type="checkbox"]:disabled { cursor: not-allowed; opacity: 0.4; }
</style>

## FIFA World Cup 2026 — Group Stage Predictions

Pick the **2 teams from each group** that you think will advance to the Round of 32, then pick **8 best third-place teams** that will also advance.

Read the [contest rules](/prediction-contests/fifa-2026/rules) before submitting.

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

### Round of 32 Picks

Pick **exactly 2 teams** from each group to advance.

<div id="progress-bar">
  <div class="progress">
    <div class="progress-bar bg-success" role="progressbar" style="width: 0%">0 / 12 groups</div>
  </div>
</div>

<div class="row" id="r32-groups">
  <!-- Group A -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-A">
      <h4>Group A <span class="badge badge-secondary" id="badge-A">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="A" data-team="Mexico" id="r32-A-0"> <label for="r32-A-0">Mexico</label></div>
      <div class="team-check"><input type="checkbox" data-group="A" data-team="South Africa" id="r32-A-1"> <label for="r32-A-1">South Africa</label></div>
      <div class="team-check"><input type="checkbox" data-group="A" data-team="Korea Republic" id="r32-A-2"> <label for="r32-A-2">Korea Republic</label></div>
      <div class="team-check"><input type="checkbox" data-group="A" data-team="Czechia" id="r32-A-3"> <label for="r32-A-3">Czechia</label></div>
    </div>
  </div>
  <!-- Group B -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-B">
      <h4>Group B <span class="badge badge-secondary" id="badge-B">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="B" data-team="Canada" id="r32-B-0"> <label for="r32-B-0">Canada</label></div>
      <div class="team-check"><input type="checkbox" data-group="B" data-team="Switzerland" id="r32-B-1"> <label for="r32-B-1">Switzerland</label></div>
      <div class="team-check"><input type="checkbox" data-group="B" data-team="Qatar" id="r32-B-2"> <label for="r32-B-2">Qatar</label></div>
      <div class="team-check"><input type="checkbox" data-group="B" data-team="Bosnia &amp; Herz." id="r32-B-3"> <label for="r32-B-3">Bosnia &amp; Herz.</label></div>
    </div>
  </div>
  <!-- Group C -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-C">
      <h4>Group C <span class="badge badge-secondary" id="badge-C">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="C" data-team="Brazil" id="r32-C-0"> <label for="r32-C-0">Brazil</label></div>
      <div class="team-check"><input type="checkbox" data-group="C" data-team="Morocco" id="r32-C-1"> <label for="r32-C-1">Morocco</label></div>
      <div class="team-check"><input type="checkbox" data-group="C" data-team="Haiti" id="r32-C-2"> <label for="r32-C-2">Haiti</label></div>
      <div class="team-check"><input type="checkbox" data-group="C" data-team="Scotland" id="r32-C-3"> <label for="r32-C-3">Scotland</label></div>
    </div>
  </div>
  <!-- Group D -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-D">
      <h4>Group D <span class="badge badge-secondary" id="badge-D">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="D" data-team="USA" id="r32-D-0"> <label for="r32-D-0">USA</label></div>
      <div class="team-check"><input type="checkbox" data-group="D" data-team="Paraguay" id="r32-D-1"> <label for="r32-D-1">Paraguay</label></div>
      <div class="team-check"><input type="checkbox" data-group="D" data-team="Australia" id="r32-D-2"> <label for="r32-D-2">Australia</label></div>
      <div class="team-check"><input type="checkbox" data-group="D" data-team="Türkiye" id="r32-D-3"> <label for="r32-D-3">T&uuml;rkiye</label></div>
    </div>
  </div>
  <!-- Group E -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-E">
      <h4>Group E <span class="badge badge-secondary" id="badge-E">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="E" data-team="Germany" id="r32-E-0"> <label for="r32-E-0">Germany</label></div>
      <div class="team-check"><input type="checkbox" data-group="E" data-team="Ecuador" id="r32-E-1"> <label for="r32-E-1">Ecuador</label></div>
      <div class="team-check"><input type="checkbox" data-group="E" data-team="Côte d'Ivoire" id="r32-E-2"> <label for="r32-E-2">C&ocirc;te d'Ivoire</label></div>
      <div class="team-check"><input type="checkbox" data-group="E" data-team="Curaçao" id="r32-E-3"> <label for="r32-E-3">Cura&ccedil;ao</label></div>
    </div>
  </div>
  <!-- Group F -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-F">
      <h4>Group F <span class="badge badge-secondary" id="badge-F">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="F" data-team="Netherlands" id="r32-F-0"> <label for="r32-F-0">Netherlands</label></div>
      <div class="team-check"><input type="checkbox" data-group="F" data-team="Japan" id="r32-F-1"> <label for="r32-F-1">Japan</label></div>
      <div class="team-check"><input type="checkbox" data-group="F" data-team="Sweden" id="r32-F-2"> <label for="r32-F-2">Sweden</label></div>
      <div class="team-check"><input type="checkbox" data-group="F" data-team="Tunisia" id="r32-F-3"> <label for="r32-F-3">Tunisia</label></div>
    </div>
  </div>
  <!-- Group G -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-G">
      <h4>Group G <span class="badge badge-secondary" id="badge-G">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="G" data-team="Belgium" id="r32-G-0"> <label for="r32-G-0">Belgium</label></div>
      <div class="team-check"><input type="checkbox" data-group="G" data-team="Egypt" id="r32-G-1"> <label for="r32-G-1">Egypt</label></div>
      <div class="team-check"><input type="checkbox" data-group="G" data-team="IR Iran" id="r32-G-2"> <label for="r32-G-2">IR Iran</label></div>
      <div class="team-check"><input type="checkbox" data-group="G" data-team="New Zealand" id="r32-G-3"> <label for="r32-G-3">New Zealand</label></div>
    </div>
  </div>
  <!-- Group H -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-H">
      <h4>Group H <span class="badge badge-secondary" id="badge-H">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="H" data-team="Spain" id="r32-H-0"> <label for="r32-H-0">Spain</label></div>
      <div class="team-check"><input type="checkbox" data-group="H" data-team="Uruguay" id="r32-H-1"> <label for="r32-H-1">Uruguay</label></div>
      <div class="team-check"><input type="checkbox" data-group="H" data-team="Saudi Arabia" id="r32-H-2"> <label for="r32-H-2">Saudi Arabia</label></div>
      <div class="team-check"><input type="checkbox" data-group="H" data-team="Cabo Verde" id="r32-H-3"> <label for="r32-H-3">Cabo Verde</label></div>
    </div>
  </div>
  <!-- Group I -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-I">
      <h4>Group I <span class="badge badge-secondary" id="badge-I">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="I" data-team="France" id="r32-I-0"> <label for="r32-I-0">France</label></div>
      <div class="team-check"><input type="checkbox" data-group="I" data-team="Senegal" id="r32-I-1"> <label for="r32-I-1">Senegal</label></div>
      <div class="team-check"><input type="checkbox" data-group="I" data-team="Iraq" id="r32-I-2"> <label for="r32-I-2">Iraq</label></div>
      <div class="team-check"><input type="checkbox" data-group="I" data-team="Norway" id="r32-I-3"> <label for="r32-I-3">Norway</label></div>
    </div>
  </div>
  <!-- Group J -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-J">
      <h4>Group J <span class="badge badge-secondary" id="badge-J">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="J" data-team="Argentina" id="r32-J-0"> <label for="r32-J-0">Argentina</label></div>
      <div class="team-check"><input type="checkbox" data-group="J" data-team="Algeria" id="r32-J-1"> <label for="r32-J-1">Algeria</label></div>
      <div class="team-check"><input type="checkbox" data-group="J" data-team="Austria" id="r32-J-2"> <label for="r32-J-2">Austria</label></div>
      <div class="team-check"><input type="checkbox" data-group="J" data-team="Jordan" id="r32-J-3"> <label for="r32-J-3">Jordan</label></div>
    </div>
  </div>
  <!-- Group K -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-K">
      <h4>Group K <span class="badge badge-secondary" id="badge-K">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="K" data-team="Portugal" id="r32-K-0"> <label for="r32-K-0">Portugal</label></div>
      <div class="team-check"><input type="checkbox" data-group="K" data-team="Colombia" id="r32-K-1"> <label for="r32-K-1">Colombia</label></div>
      <div class="team-check"><input type="checkbox" data-group="K" data-team="Congo DR" id="r32-K-2"> <label for="r32-K-2">Congo DR</label></div>
      <div class="team-check"><input type="checkbox" data-group="K" data-team="Uzbekistan" id="r32-K-3"> <label for="r32-K-3">Uzbekistan</label></div>
    </div>
  </div>
  <!-- Group L -->
  <div class="col-md-4 col-sm-6">
    <div class="group-card" id="card-L">
      <h4>Group L <span class="badge badge-secondary" id="badge-L">Pick 2</span></h4>
      <div class="team-check"><input type="checkbox" data-group="L" data-team="England" id="r32-L-0"> <label for="r32-L-0">England</label></div>
      <div class="team-check"><input type="checkbox" data-group="L" data-team="Croatia" id="r32-L-1"> <label for="r32-L-1">Croatia</label></div>
      <div class="team-check"><input type="checkbox" data-group="L" data-team="Ghana" id="r32-L-2"> <label for="r32-L-2">Ghana</label></div>
      <div class="team-check"><input type="checkbox" data-group="L" data-team="Panama" id="r32-L-3"> <label for="r32-L-3">Panama</label></div>
    </div>
  </div>
</div>

---

<div id="third-place-section">
  <h3>Best Third-Place Picks <span class="badge badge-info" id="badge-third">Pick 8</span></h3>
  <p>From the teams you <strong>didn't</strong> pick above, select <strong>exactly 8</strong> that will advance as best third-place finishers. (Max 1 per group.)</p>
  <div id="third-place-grid"></div>
</div>

<div id="validation-panel">
  <strong>Checklist</strong>
  <ul id="validation-list"></ul>
</div>

<button class="btn btn-lg btn-success btn-block" id="submit-btn" disabled>Submit Predictions</button>

<div id="submission-result"></div>
