#!/usr/bin/env python3
"""Build index.json from individual plenary abstract JSON files.

Reads all *.json files in abstracts/ (excluding index.json itself),
and produces index.json with one entry per talk.
"""

import json
from pathlib import Path

ABSTRACTS_DIR = Path(__file__).resolve().parent
INDEX_PATH = ABSTRACTS_DIR / "index.json"
SKIP = {"index.json"}


def build_index():
    entries = []
    for path in sorted(ABSTRACTS_DIR.glob("*.json")):
        if path.name in SKIP:
            continue
        with open(path) as f:
            data = json.load(f)
        # Only include speaker JSON files (have "speaker" key)
        if "speaker" not in data:
            continue
        entries.append({
            "file": path.name,
            "speaker": data["speaker"],
            "affiliation": data.get("affiliation"),
            "title": data.get("title"),
            "type": data.get("type", "plenary"),
            "remote": data.get("remote", False),
            "has_abstract": data.get("abstract") is not None,
            "decision": data.get("decision"),
            "submission_id": data.get("submission_id"),
        })

    with open(INDEX_PATH, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    total = len(entries)
    with_abstract = sum(1 for e in entries if e["has_abstract"])
    print(f"Index: {total} plenary speakers, {with_abstract} with abstracts, "
          f"{total - with_abstract} without")
    return entries


if __name__ == "__main__":
    build_index()
