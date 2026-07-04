/**
 * FIFA 2026 — Round of 16 Entry Form (Google Apps Script)
 *
 * Deployed as: Web App (Execute as me, Anyone can access)
 * Apps Script URL used in r16-entry.js:
 *   https://script.google.com/macros/s/AKfycbzhpo6lmefj1_GGrui4GmrvBlWV4v0XF05ITA_HDnbbRki9KINMM3JId2JXcr8ENhBz/exec
 *
 * Sheet columns (in order):
 *   Timestamp | Name | Email | Location | CAN v MAR | PAR v FRA | BRA v NOR | MEX v ENG | ESP v POR | USA v BEL | Match 7 | Match 8
 */

var SHEET_NAME = 'R16 Entries';

// Match columns in the order they appear on the form
var MATCH_COLS = [
  'CAN v MAR',
  'PAR v FRA',
  'BRA v NOR',
  'MEX v ENG',
  'ESP v POR',
  'USA v BEL',
  'EGY v ARG',
  'SUI v COL'
];

function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  // Write to spreadsheet
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    // Add header row
    var headers = ['Timestamp', 'Name', 'Email', 'Location'].concat(MATCH_COLS);
    sheet.appendRow(headers);
  }

  var row = [
    new Date(),
    data.name || '',
    data.email || '',
    data.location || ''
  ];

  MATCH_COLS.forEach(function (col) {
    row.push(data[col] || '');
  });

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
  var subject = 'FIFA 2026 R16 Predictions — Confirmation';

  var lines = [
    'Hi ' + data.name + ',',
    '',
    'Your Round of 16 predictions have been recorded. Here is a summary:',
    ''
  ];

  MATCH_COLS.forEach(function (col) {
    var pick = data[col];
    if (pick) {
      lines.push('  ' + col + ':  ' + pick);
    }
  });

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
    .createTextOutput('R16 entry endpoint is active.')
    .setMimeType(ContentService.MimeType.TEXT);
}
