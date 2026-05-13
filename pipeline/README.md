# Conference Submission Pipeline

Automated pipeline: Google Form submission creates a pull request to add a conference to `conferences.html`.

```
User submits Google Form
        |
Google Sheet row created
        |
Apps Script validates + calls GitHub repository_dispatch
        |
GitHub Action runs add_conference.py
        |
Script edits conferences.html (chronological insertion)
        |
HTML validation runs
        |
Pull request created for review
```

## Setup

### 1. Google Form

Create a Google Form in the `cs2026` folder on `arnodelorme@gmail.com` with these fields (in order):

| # | Field | Type | Required |
|---|-------|------|----------|
| 1 | Conference name | Short text | Yes |
| 2 | Start date | Date (or short text YYYY-MM-DD) | Yes |
| 3 | End date | Date (or short text YYYY-MM-DD) | No |
| 4 | Location | Short text | Yes |
| 5 | Website URL | Short text | Yes |
| 6 | Description | Paragraph | Yes |
| 7 | Year | Short text (default: 2026) | Yes |

Link the form to a Google Sheet (Form > Responses > Link to Sheets).

### 2. Apps Script

1. Open the linked Sheet > **Extensions > Apps Script**
2. Delete default code, paste contents of `apps_script.gs`
3. Go to **Project Settings > Script Properties**, add:
   - `GITHUB_TOKEN` = a GitHub Personal Access Token (classic) with `repo` scope
     - Create at: https://github.com/settings/tokens
     - Needs permission to trigger `repository_dispatch` on `arnodelorme/cs2026`
4. Add a trigger:
   - **Triggers > Add Trigger**
   - Function: `onFormSubmit`
   - Event source: From spreadsheet
   - Event type: On form submit

### 3. GitHub Repository

The workflow file `.github/workflows/add-conference.yml` is already in the repo. It will activate once pushed to `main`.

No additional secrets needed — the workflow uses the default `GITHUB_TOKEN` which has write access to contents and pull requests.

### 4. Test

Submit a test entry via the Google Form and verify:
- The Sheet gets a "Dispatched" status in the last column
- A new branch `conf/...` appears on GitHub
- A pull request is created with the conference diff

## Files

| File | Purpose |
|------|---------|
| `pipeline/apps_script.gs` | Google Apps Script — validates form data, fires `repository_dispatch` |
| `pipeline/add_conference.py` | Python — generates HTML card, inserts chronologically into `conferences.html` |
| `.github/workflows/add-conference.yml` | GitHub Action — runs on dispatch, commits, creates PR |
| `pipeline/README.md` | This file |

## How the insertion works

`add_conference.py` parses the existing `conferences.html`, finds the correct year section (or creates one), then inserts the new card in chronological order by comparing date sort keys. The card HTML follows the same structure as hand-written entries. A PR is always created — never a direct push to main.
