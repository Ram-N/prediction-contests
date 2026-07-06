/**
 * FIFA 2026 — Short-Term 4-2-1 Entry Form (Google Apps Script)
 *
 * Deployed as: Web App (Execute as me, Anyone can access)
 *
 * Sheet columns (in order):
 *   Timestamp | Name | Email | Location | QF1 | QF2 | QF3 | QF4 | SF1 | SF2 | Winner
 */

var SHEET_NAME = 'ST-421 Entries';

function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  // Write to spreadsheet
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    var headers = ['Timestamp', 'Name', 'Email', 'Location',
                   'QF1', 'QF2', 'QF3', 'QF4',
                   'SF1', 'SF2', 'Winner'];
    sheet.appendRow(headers);
  }

  var qf = data.qf || [];
  var sf = data.sf || [];

  var row = [
    new Date(),
    data.name || '',
    data.email || '',
    data.location || '',
    qf[0] || '',
    qf[1] || '',
    qf[2] || '',
    qf[3] || '',
    sf[0] || '',
    sf[1] || '',
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
  var subject = 'FIFA 2026 Short-Term (4-2-1) Predictions — Confirmation';

  var qf = data.qf || [];
  var sf = data.sf || [];

  var lines = [
    'Hi ' + data.name + ',',
    '',
    'Your Short-Term 4-2-1 predictions have been recorded. Here is your bracket:',
    '',
    'QUARTERFINAL WINNERS (Semifinalists):',
    '  QF1: ' + (qf[0] || ''),
    '  QF2: ' + (qf[1] || ''),
    '  QF3: ' + (qf[2] || ''),
    '  QF4: ' + (qf[3] || ''),
    '',
    'SEMIFINAL WINNERS (Finalists):',
    '  SF1 (' + (qf[0] || '?') + ' vs ' + (qf[1] || '?') + '): ' + (sf[0] || ''),
    '  SF2 (' + (qf[2] || '?') + ' vs ' + (qf[3] || '?') + '): ' + (sf[1] || ''),
    '',
    'CHAMPION: ' + (data.winner || ''),
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
    .createTextOutput('ST-421 entry endpoint is active.')
    .setMimeType(ContentService.MimeType.TEXT);
}
