/**
 * FIFA 2026 — 4-2-1 Long Range Entry Form (Google Apps Script)
 *
 * Deployed as: Web App (Execute as me, Anyone can access)
 * Apps Script URL used in lr-421-entry.js:
 *   https://script.google.com/macros/s/AKfycbwF_hfQbEzLwDF1OrmbXjZ6ns0E4CUtX89wzCDdVL5p8cLv1JOhtT-_5nVByIM1pwBF/exec
 *
 * Sheet columns (in order):
 *   Timestamp | Name | Email | Location | Semi1 | Semi2 | Semi3 | Semi4 | Finalist1 | Finalist2 | Winner
 */

var SHEET_NAME = 'LR-421 Entries';

function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  // Write to spreadsheet
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    var headers = ['Timestamp', 'Name', 'Email', 'Location',
                   'Semi1', 'Semi2', 'Semi3', 'Semi4',
                   'Finalist1', 'Finalist2', 'Winner'];
    sheet.appendRow(headers);
  }

  var semis = data.semis || [];
  var finals = data.finals || [];

  var row = [
    new Date(),
    data.name || '',
    data.email || '',
    data.location || '',
    semis[0] || '',
    semis[1] || '',
    semis[2] || '',
    semis[3] || '',
    finals[0] || '',
    finals[1] || '',
    data.winner || ''
  ];

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
  var subject = 'FIFA 2026 Long Range (4-2-1) Predictions — Confirmation';

  var semis = data.semis || [];
  var finals = data.finals || [];

  var lines = [
    'Hi ' + data.name + ',',
    '',
    'Your 4-2-1 Long Range predictions have been recorded. Here is a summary:',
    '',
    'Semifinalists (4): ' + semis.join(', '),
    'Finalists (2):     ' + finals.join(', '),
    'Winner (1):        ' + (data.winner || ''),
    '',
    'Location: ' + (data.location || ''),
    '',
    'Good luck!',
    '— FIFA 2026 Prediction Contest'
  ];

  var body = lines.join('\n');

  MailApp.sendEmail({
    to: data.email,
    subject: subject,
    body: body
  });
}

function doGet(e) {
  return ContentService
    .createTextOutput('LR-421 entry endpoint is active.')
    .setMimeType(ContentService.MimeType.TEXT);
}
