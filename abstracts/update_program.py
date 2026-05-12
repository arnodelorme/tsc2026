#!/usr/bin/env python3
"""Update program.html plenary talk titles from abstract JSON files.

For each plenary block in the Detailed Timetable, extracts speaker names
from the session-speakers div, looks up their talk title in abstracts/*.json
by matching last name (and first name to disambiguate), and inserts
session-note divs with "LastName: Title" or "LastName: TBD".

Existing auto-generated talk-title notes are replaced on each run.
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRAM = ROOT / "program.html"
ABSTRACTS_DIR = Path(__file__).resolve().parent

# Tag used to mark auto-generated lines so we can replace them on re-run
TAG = "talk-title"


def load_abstracts():
    """Load all abstract JSON files, keyed by normalized last name."""
    abstracts = {}
    for path in ABSTRACTS_DIR.glob("*.json"):
        if path.name == "index.json":
            continue
        with open(path) as f:
            data = json.load(f)
        if "speaker" not in data:
            continue
        name = data["speaker"]
        # Normalize: remove accents for matching
        norm = name.lower()
        for src, dst in [("é", "e"), ("á", "a"), ("ü", "u"), ("ö", "o"),
                         ("ñ", "n"), ("ç", "c")]:
            norm = norm.replace(src, dst)
        parts = norm.split()
        last = parts[-1] if parts else ""
        first = parts[0] if parts else ""
        abstracts[last] = {
            "first": first,
            "last": last,
            "full_name": name,
            "title": data.get("title"),
        }
    return abstracts


def strip_html_tags(s):
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", s)


def decode_entities(s):
    """Decode HTML entities."""
    return html.unescape(s)


def normalize_name(name):
    """Normalize a speaker name for matching."""
    name = name.strip()
    # Remove parenthetical notes like (Remote), (provisional)
    name = re.sub(r"\(.*?\)", "", name).strip()
    name = name.lower()
    for src, dst in [("é", "e"), ("á", "a"), ("ü", "u"), ("ö", "o"),
                     ("ñ", "n"), ("ç", "c")]:
        name = name.replace(src, dst)
    return name


def extract_speakers_from_line(line):
    """Extract individual speaker names from a session-speakers div."""
    # Get the text content, stripping HTML tags
    m = re.search(r'class="session-speakers"[^>]*>(.*?)</div>', line)
    if not m:
        return []
    raw = m.group(1)
    text = strip_html_tags(raw)
    text = decode_entities(text)
    # Split by comma
    names = [n.strip() for n in text.split(",")]
    return [n for n in names if n and n not in ("TBD", "TBA")]


def escape_html_title(title):
    """Escape special chars for HTML output."""
    title = title.replace("&", "&amp;")
    title = title.replace("<", "&lt;")
    title = title.replace(">", "&gt;")
    # Use HTML entities for special dashes/chars
    title = title.replace("\u2013", "&ndash;")  # en-dash
    title = title.replace("\u2014", "&mdash;")  # em-dash
    title = title.replace("\u2018", "&lsquo;")
    title = title.replace("\u2019", "&rsquo;")
    title = title.replace("\u201c", "&ldquo;")
    title = title.replace("\u201d", "&rdquo;")
    return title


def lookup_speaker(name, abstracts):
    """Look up a speaker name in the abstracts dict. Returns (last_name, title|None)."""
    norm = normalize_name(name)
    parts = norm.split()
    if not parts:
        return None, None
    last = parts[-1]
    first = parts[0]

    # Try exact last name match
    if last in abstracts:
        entry = abstracts[last]
        return entry["full_name"].split()[-1], entry["title"]

    # Try hyphenated last names (e.g. "carhart-harris" -> "carhartharris")
    last_nohyphen = last.replace("-", "")
    for key, entry in abstracts.items():
        if key.replace("-", "") == last_nohyphen:
            return entry["full_name"].split()[-1], entry["title"]

    return last.capitalize(), None


def update_program():
    """Read program.html, insert/update talk titles, write back."""
    text = PROGRAM.read_text(encoding="utf-8")
    lines = text.split("\n")
    abstracts = load_abstracts()

    new_lines = []
    i = 0
    stats = {"added": 0, "tbd": 0}

    while i < len(lines):
        line = lines[i]

        # Skip previously auto-generated talk-title lines
        if f'data-auto="{TAG}"' in line:
            i += 1
            continue

        new_lines.append(line)

        # Detect plenary blocks: look for session-speakers inside bg-plenary
        # We check if the previous non-empty lines indicate a bg-plenary block
        if 'class="session-speakers"' in line:
            # Walk back to check if this is inside a bg-plenary block
            in_plenary = False
            for j in range(len(new_lines) - 1, max(len(new_lines) - 6, -1), -1):
                if "bg-plenary" in new_lines[j]:
                    in_plenary = True
                    break

            if in_plenary:
                speakers = extract_speakers_from_line(line)
                # Determine indentation from current line
                indent = re.match(r"(\s*)", line).group(1)
                for spk in speakers:
                    last_name, title = lookup_speaker(spk, abstracts)
                    if last_name:
                        if title:
                            safe_title = escape_html_title(title)
                            note = (f'{indent}<div class="session-note" '
                                    f'data-auto="{TAG}">'
                                    f'{last_name}: {safe_title}</div>')
                            stats["added"] += 1
                        else:
                            note = (f'{indent}<div class="session-note" '
                                    f'data-auto="{TAG}">'
                                    f'{last_name}: TBA</div>')
                            stats["tbd"] += 1
                        new_lines.append(note)

        i += 1

    PROGRAM.write_text("\n".join(new_lines), encoding="utf-8")
    total = stats["added"] + stats["tbd"]
    print(f"Updated program.html: {stats['added']} talk titles added, "
          f"{stats['tbd']} marked TBD ({total} total speakers in plenary blocks)")


if __name__ == "__main__":
    update_program()
