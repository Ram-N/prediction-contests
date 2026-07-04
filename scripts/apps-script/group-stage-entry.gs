/**
 * FIFA 2026 — Group Stage Entry Form (Google Apps Script)
 *
 * Deployed as: Web App (Execute as me, Anyone can access)
 * Apps Script URL used in entry-form.js:
 *   https://script.google.com/macros/s/AKfycbzsW-n6vbxIhT-WPZXeIx7uyBm3RNrwGZwm6jOci8WBdAzsLywRHGwe7qw6erMxJgxV/exec
 *
 * Payload from frontend:
 *   { name, email, location, r32: { A: [team1, team2], B: [...], ... }, thirdPlace: [{group, team}, ...] }
 *
 * Sheet columns:
 *   Timestamp | Name | Email | Location | A1 | A2 | B1 | B2 | ... | L1 | L2 | 3rd_1 | 3rd_2 | 3rd_3 | 3rd_4 | 3rd_5 | 3rd_6 | 3rd_7 | 3rd_8
 */

var SHEET_NAME = 'Group Stage Entries';
var GROUPS = ['A','B','C','D','E','F','G','H','I','J','K','L'];

function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    var headers = ['Timestamp', 'Name', 'Email', 'Location'];
    GROUPS.forEach(function (g) {
      headers.push(g + '1');
      headers.push(g + '2');
    });
    for (var i = 1; i <= 8; i++) {
      headers.push('3rd_' + i);
    }
    sheet.appendRow(headers);
  }

  var r32 = data.r32 || {};
  var thirdPlace = data.thirdPlace || [];

  var row = [
    new Date(),
    data.name || '',
    data.email || '',
    data.location || ''
  ];

  GROUPS.forEach(function (g) {
    var picks = r32[g] || [];
    row.push(picks[0] || '');
    row.push(picks[1] || '');
  });

  thirdPlace.forEach(function (tp) {
    row.push((tp.group || '') + ': ' + (tp.team || ''));
  });
  // Pad to 8 third-place columns
  for (var i = thirdPlace.length; i < 8; i++) {
    row.push('');
  }

  sheet.appendRow(row);

  // Send confirmation email
  if (data.email) {
    sendConfirmationEmail(data);
  }

  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function sendConfirmationEmail(data) {
  var subject = 'FIFA 2026 Group Stage Predictions — Confirmation';

  var r32 = data.r32 || {};
  var thirdPlace = data.thirdPlace || [];

  var lines = [
    'Hi ' + data.name + ',',
    '',
    'Your Group Stage predictions have been recorded. Here is a summary:',
    '',
    'Top-2 picks per group:'
  ];

  GROUPS.forEach(function (g) {
    var picks = r32[g] || [];
    if (picks.length > 0) {
      lines.push('  Group ' + g + ': ' + picks.join(', '));
    }
  });

  if (thirdPlace.length > 0) {
    lines.push('');
    lines.push('Best 3rd-place teams:');
    thirdPlace.forEach(function (tp) {
      lines.push('  ' + tp.team + ' (Group ' + tp.group + ')');
    });
  }

  lines.push('');
  lines.push('Location: ' + (data.location || ''));
  lines.push('');
  lines.push('Good luck!');
  lines.push('— FIFA 2026 Prediction Contest');

  var body = lines.join('\n');

  MailApp.sendEmail({
    to: data.email,
    subject: subject,
    body: body
  });
}

function doGet(e) {
  return ContentService
    .createTextOutput('Group Stage entry endpoint is active.')
    .setMimeType(ContentService.MimeType.TEXT);
}
