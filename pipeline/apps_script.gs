/**
 * Google Apps Script — CS 2026 Conference Submission Pipeline
 *
 * Install in the Google Sheet that receives Google Form responses.
 * Sheet is in arnodelorme@gmail.com / cs2026 Drive folder.
 *
 * Setup:
 *  1. Open the Sheet > Extensions > Apps Script
 *  2. Paste this file's contents
 *  3. Add a Script Property:  GITHUB_TOKEN = <your fine-grained PAT>
 *     (Project Settings > Script Properties)
 *  4. Add trigger: onFormSubmit → From spreadsheet → On form submit
 *
 * Google Form columns (actual):
 *   [0] Timestamp
 *   [1] Event Title
 *   [2] Short Description (1 sentence)
 *   [3] Event Start Date and Time
 *   [4] Event End Date and Time
 *   [5] Location/Venue Name
 *   [6] Type of Event
 *
 * Optional: add a "Website URL" field as column [7] in the form.
 */

function onFormSubmit(e) {
  var row = e.values;
  if (!row || row.length < 6) {
    Logger.log("Incomplete submission, skipping");
    return;
  }

  // Parse dates — Google Forms may give "M/D/YYYY H:MM:SS" or "YYYY-MM-DD"
  var startRaw = (row[3] || "").trim();
  var endRaw   = (row[4] || "").trim();

  var payload = {
    name:        (row[1] || "").trim(),
    description: (row[2] || "").trim(),
    start_date:  toISO_(startRaw),
    end_date:    toISO_(endRaw),
    location:    (row[5] || "").trim(),
    event_type:  (row[6] || "").trim(),
    url:         (row[7] || "").trim(),    // optional column
    year:        ""                         // derived below
  };

  // Derive year from start date
  if (payload.start_date) {
    payload.year = payload.start_date.substring(0, 4);
  }

  // ── Validate ──────────────────────────────
  var errors = [];
  if (!payload.name)        errors.push("Missing event title");
  if (!payload.start_date)  errors.push("Missing or unparseable start date");
  if (!payload.location)    errors.push("Missing location");
  if (!payload.description) errors.push("Missing description");

  if (errors.length > 0) {
    Logger.log("Validation failed: " + errors.join("; "));
    flagRow_(e.range.getRow(), errors.join("; "));
    return;
  }

  // Default end_date to start_date
  if (!payload.end_date) payload.end_date = payload.start_date;

  // URL: add https if present but missing scheme
  if (payload.url && !/^https?:\/\//i.test(payload.url))
    payload.url = "https://" + payload.url;

  // ── Dispatch to GitHub ────────────────────
  var token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  if (!token) {
    Logger.log("GITHUB_TOKEN not set in Script Properties");
    return;
  }

  var ghUrl = "https://api.github.com/repos/arnodelorme/cs2026/dispatches";
  var options = {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "token " + token },
    payload: JSON.stringify({
      event_type: "add-conference",
      client_payload: payload
    }),
    muteHttpExceptions: true
  };

  var resp = UrlFetchApp.fetch(ghUrl, options);
  var code = resp.getResponseCode();
  Logger.log("GitHub dispatch: HTTP " + code + " body: " + resp.getContentText());

  // Mark the row with status
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var statusCol = 8;  // column H — after the 7 form columns
  if (code === 204) {
    sheet.getRange(e.range.getRow(), statusCol).setValue("Dispatched " + new Date().toISOString());
  } else {
    sheet.getRange(e.range.getRow(), statusCol).setValue("FAILED: HTTP " + code + " " + resp.getContentText());
  }
}


/**
 * Convert various date formats to YYYY-MM-DD.
 * Handles: "M/D/YYYY H:MM:SS", "M/D/YYYY", "YYYY-MM-DD", Date objects.
 */
function toISO_(raw) {
  if (!raw) return "";

  // Already YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}/.test(raw))
    return raw.substring(0, 10);

  // Try parsing as Date (handles "M/D/YYYY H:MM:SS" and others)
  var d = new Date(raw);
  if (!isNaN(d.getTime())) {
    var y = d.getFullYear();
    var m = ("0" + (d.getMonth() + 1)).slice(-2);
    var day = ("0" + d.getDate()).slice(-2);
    return y + "-" + m + "-" + day;
  }

  return "";
}


/**
 * Flag a row with validation errors.
 */
function flagRow_(rowNum, msg) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(rowNum, 8).setValue("INVALID: " + msg);
}
