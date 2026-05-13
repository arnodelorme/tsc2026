#!/usr/bin/env python3
"""Insert a new conference card into conferences.html chronologically.

Reads conference data from environment variables (set by GitHub Action
from the repository_dispatch payload) and inserts a new <li> card into
the correct chronological position within the matching year section.

Env vars (all required unless noted):
  CONF_NAME        — Event title
  CONF_START_DATE  — YYYY-MM-DD
  CONF_END_DATE    — YYYY-MM-DD (optional, defaults to start)
  CONF_LOCATION    — e.g. "Copenhagen, Denmark"
  CONF_URL         — https://... (optional, card won't link if empty)
  CONF_DESCRIPTION — Short description
  CONF_YEAR        — e.g. 2026 (derived from start date)
  CONF_EVENT_TYPE  — e.g. "Conference/Symposium" (optional, for PR metadata)
"""

import html
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF_HTML = ROOT / "conferences.html"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def env(key, required=True):
    val = os.environ.get(key, "").strip()
    if required and not val:
        print(f"Error: missing env var {key}", file=sys.stderr)
        sys.exit(1)
    return val


def format_date_range(start_str, end_str):
    """Format date range as 'Month D–D, YYYY' or 'Month D, YYYY'."""
    start = datetime.strptime(start_str, "%Y-%m-%d")
    if end_str and end_str != start_str:
        end = datetime.strptime(end_str, "%Y-%m-%d")
        if start.month == end.month and start.year == end.year:
            return f"{MONTHS[start.month - 1]} {start.day}&ndash;{end.day}, {start.year}"
        elif start.year == end.year:
            return (f"{MONTHS[start.month - 1]} {start.day} &ndash; "
                    f"{MONTHS[end.month - 1]} {end.day}, {start.year}")
        else:
            return (f"{MONTHS[start.month - 1]} {start.day}, {start.year} &ndash; "
                    f"{MONTHS[end.month - 1]} {end.day}, {end.year}")
    return f"{MONTHS[start.month - 1]} {start.day}, {start.year}"


def escape(text):
    """HTML-escape text."""
    return html.escape(text)


def build_card(name, date_display, location, url, description):
    """Build the HTML for one conference card."""
    if url:
        open_tag = f'    <a class="conf-card" href="{escape(url)}" target="_blank" rel="noopener">'
        close_tag = '    </a>'
    else:
        open_tag = '    <div class="conf-card">'
        close_tag = '    </div>'
    return (
        f'  <li>\n'
        f'{open_tag}\n'
        f'      <div class="conf-date">{date_display}</div>\n'
        f'      <h3>{escape(name)}</h3>\n'
        f'      <div class="conf-location">{escape(location)}</div>\n'
        f'      <div class="conf-desc">{escape(description)}</div>\n'
        f'{close_tag}\n'
        f'  </li>\n'
    )


def parse_sort_key(date_div_text):
    """Extract a sortable date from an existing conf-date div.

    Handles formats like:
      'October 12&ndash;16, 2026'
      'June 30 &ndash; July 3, 2026'
      'October 1, 2026'
      '2026 (dates TBA)'
    Returns (year, month, day) tuple for sorting.
    """
    text = date_div_text.replace("&ndash;", "-").strip()

    # Try: Month D-D, YYYY or Month D, YYYY
    m = re.match(r"(\w+)\s+(\d+)", text)
    year_m = re.search(r"(\d{4})", text)
    if m and year_m:
        month_name = m.group(1)
        day = int(m.group(2))
        year = int(year_m.group(1))
        month_idx = next(
            (i + 1 for i, mn in enumerate(MONTHS) if mn.lower() == month_name.lower()),
            13,
        )
        return (year, month_idx, day)

    # Fallback: just year
    if year_m:
        return (int(year_m.group(1)), 13, 0)

    return (9999, 13, 0)


def insert_conference():
    name = env("CONF_NAME")
    start_date = env("CONF_START_DATE")
    end_date = env("CONF_END_DATE", required=False) or start_date
    location = env("CONF_LOCATION")
    url = env("CONF_URL", required=False)
    description = env("CONF_DESCRIPTION")
    year = env("CONF_YEAR")

    date_display = format_date_range(start_date, end_date)
    new_card = build_card(name, date_display, location, url, description)
    new_sort_key = parse_sort_key(date_display)

    content = CONF_HTML.read_text(encoding="utf-8")

    # Check if year section exists
    year_marker = f'class="year-header">{year}</h2>'
    if year_marker not in content:
        # Insert a new year section before </ul> or before the footer note
        insert_before = '<p style="font-size:.85rem;color:#888;margin-top:2rem;">'
        year_block = (
            f'</ul>\n\n'
            f'<h2 class="year-header">{year}</h2>\n\n'
            f'<ul class="conf-list">\n\n'
            f'{new_card}\n'
        )
        content = content.replace(insert_before, year_block + insert_before)
        CONF_HTML.write_text(content, encoding="utf-8")
        print(f"Added {name} in new {year} section")
        return

    # Find the conf-list for this year and insert chronologically
    lines = content.split("\n")
    # Find the year header
    year_line_idx = None
    for i, line in enumerate(lines):
        if year_marker in line:
            year_line_idx = i
            break

    if year_line_idx is None:
        print("Error: could not locate year section", file=sys.stderr)
        sys.exit(1)

    # Find the <ul class="conf-list"> after the year header
    ul_start = None
    for i in range(year_line_idx + 1, len(lines)):
        if '<ul class="conf-list">' in lines[i]:
            ul_start = i
            break

    if ul_start is None:
        print("Error: no conf-list after year header", file=sys.stderr)
        sys.exit(1)

    # Parse existing cards: find each <li>...</li> block and its sort key
    cards = []  # [(start_line, end_line, sort_key)]
    i = ul_start + 1
    while i < len(lines):
        if "</ul>" in lines[i]:
            break
        if "<li>" in lines[i]:
            li_start = i
            # Find the conf-date
            sort_key = (9999, 13, 0)
            for j in range(i, min(i + 8, len(lines))):
                dm = re.search(r'class="conf-date">(.*?)</div>', lines[j])
                if dm:
                    sort_key = parse_sort_key(dm.group(1))
                    break
            # Find the closing </li>
            li_end = i
            for j in range(i, len(lines)):
                if "</li>" in lines[j]:
                    li_end = j
                    break
            cards.append((li_start, li_end, sort_key))
            i = li_end + 1
        else:
            i += 1

    # Find insertion point
    insert_line = None
    for start, end, key in cards:
        if new_sort_key < key:
            insert_line = start
            break

    new_card_lines = new_card.rstrip("\n").split("\n")

    if insert_line is not None:
        # Insert before this card
        lines[insert_line:insert_line] = [""] + new_card_lines
    else:
        # Append at end of list (before </ul>)
        for i in range(len(lines) - 1, ul_start, -1):
            if "</ul>" in lines[i]:
                lines[i:i] = new_card_lines + [""]
                break

    CONF_HTML.write_text("\n".join(lines), encoding="utf-8")
    print(f"Added {name} ({date_display}) to {year} section")


if __name__ == "__main__":
    insert_conference()
