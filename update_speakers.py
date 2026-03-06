#!/usr/bin/env python3
"""Read plenary speaker data from xlsx and update program.html.

Assigns CSS classes based on 'Status San Diego' column:
  - Confirmed / Confirmed *  → (no class, plain text)
  - Pending                  → speaker-unconfirmed  (grey)
  - Not contacted yet        → speaker-missing      (red)
  - (no status, redacted)    → speaker-maybe        (blue)

Speakers with RSVP = REMOTE get '(Remote)' appended.
Speakers whose status is 'Removed' are skipped entirely.
Redacted names (xxxxx…) at a slot already occupied by a named speaker are dropped.
"""

import re
import sys

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl not installed. Run: pip install openpyxl")

XLSX = "TSCdata/Abi notes Plenary 2026.xlsx"
HTML = "program.html"

# Status → CSS class mapping
STATUS_CLASS = {
    "confirmed": "",
    "confirmed 12 or 13 only": "",
    "pending": "speaker-unconfirmed",
    "not contacted yet": "speaker-missing",
}
DEFAULT_CLASS = "speaker-maybe"  # for entries with no status (redacted names)


def read_speakers(path):
    """Parse xlsx and return dict: {session: [(order, name, css_class, is_remote), ...]}."""
    wb = openpyxl.load_workbook(path)
    ws = wb["Plenary"]

    raw = {}  # key = (session, order) → list of (name, css_class, is_remote, has_status)
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = str(row[2]).strip() if row[2] else ""
        session = str(row[3]).strip() if row[3] else ""
        order = row[4]
        rsvp = str(row[5]).strip() if row[5] else ""
        status_raw = str(row[6]).strip() if row[6] else ""

        if not name or not session or order is None:
            continue
        if not session.startswith("PL-"):
            continue

        status_lower = status_raw.lower()
        if status_lower == "removed":
            continue

        css_class = STATUS_CLASS.get(status_lower, DEFAULT_CLASS)
        is_remote = rsvp.upper() == "REMOTE"
        has_status = bool(status_raw)
        order_int = int(float(order))

        key = (session, order_int)
        if key not in raw:
            raw[key] = []
        raw[key].append((name, css_class, is_remote, has_status))

    # Resolve duplicates: prefer entry with status over no-status
    speakers = {}  # session → [(order, name, css_class, is_remote)]
    for (session, order), entries in raw.items():
        with_status = [e for e in entries if e[3]]
        pick = with_status[0] if with_status else entries[0]
        name, css_class, is_remote, _ = pick
        speakers.setdefault(session, []).append((order, name, css_class, is_remote))

    # Sort each session by order
    for session in speakers:
        speakers[session].sort(key=lambda x: x[0])

    return speakers


def format_speaker(name, css_class, is_remote):
    """Return HTML for a single speaker name."""
    display = name
    if is_remote:
        display += " (Remote)"
    if css_class:
        return f'<span class="{css_class}">{display}</span>'
    return display


def update_html(html_path, speakers):
    """Find each PL-N block in program.html and replace its session-speakers div."""
    with open(html_path, "r") as f:
        html = f.read()

    changes = []

    # Match: session-title line with PL-N, then the next session-speakers line.
    # Both are always on separate single lines in the HTML.
    pattern = re.compile(
        r'(<div class="session-title">PL-(\d+):[^<]*</div>\n)'
        r'(\s*)<div class="session-speakers">.*?</div>'
    )

    def replacer(m):
        prefix = m.group(1)
        pl_num = m.group(2)
        indent = m.group(3)
        session_key = f"PL-{pl_num}"

        if session_key not in speakers:
            return m.group(0)  # no data, leave unchanged

        parts = []
        for order, name, css_class, is_remote in speakers[session_key]:
            parts.append(format_speaker(name, css_class, is_remote))

        new_speakers_html = ", ".join(parts)
        changes.append(session_key)
        return f'{prefix}{indent}<div class="session-speakers">{new_speakers_html}</div>'

    new_html = pattern.sub(replacer, html)

    with open(html_path, "w") as f:
        f.write(new_html)

    return changes


def main():
    speakers = read_speakers(XLSX)

    print("Speakers by session:")
    for session in sorted(speakers, key=lambda s: int(s.split("-")[1])):
        names = [f"  {o}. {n} [{c or 'confirmed'}]{' (R)' if r else ''}"
                 for o, n, c, r in speakers[session]]
        print(f"  {session}:")
        for line in names:
            print(f"    {line}")

    print()
    changed = update_html(HTML, speakers)
    print(f"Updated {len(changed)} plenary blocks in {HTML}: {', '.join(changed)}")


if __name__ == "__main__":
    main()
