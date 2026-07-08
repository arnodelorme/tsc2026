#!/usr/bin/env python3
"""Fill an existing speaker's abstract from a GitHub issue and rebuild pages.

Reads ISSUE_TITLE / ISSUE_BODY from the environment, updates the matching
abstracts_json/<name>.json (which must already exist), and regenerates the
per-speaker HTML pages and index.json. Reports the result to the workflow via
GITHUB_OUTPUT (matched / speaker / message).
"""

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABSTRACTS_DIR = ROOT / "abstracts_json"

sys.path.insert(0, str(ABSTRACTS_DIR))
import build_html   # noqa: E402  (build scripts live in abstracts_json/)
import build_index  # noqa: E402


def filename_for(name):
    """Map a speaker name to its file stem, e.g. 'Robin Carhart-Harris' -> 'robin_carhartharris'."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-z0-9 ]", "", name.lower())
    return re.sub(r"\s+", "_", name.strip())


def parse_issue(body):
    """Pull (speaker, abstract) from the issue-form body sections."""
    sections, current = {}, None
    for line in body.splitlines():
        heading = re.match(r"^#{2,3}\s+(.*)$", line)
        if heading:
            current = heading.group(1).strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    speaker = "\n".join(sections.get("speaker name", [])).strip()
    abstract = "\n".join(sections.get("abstract", [])).strip()
    return speaker, abstract


def report(matched, message, speaker=""):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
        for key, value in (("matched", matched), ("speaker", speaker), ("message", message)):
            f.write(f"{key}<<__EOF__\n{value}\n__EOF__\n")


def main():
    speaker, abstract = parse_issue(os.environ.get("ISSUE_BODY", ""))
    if not speaker or not abstract:
        report("false", "Missing speaker name or abstract. Use the 'Add speaker abstract' issue template.")
        return

    path = ABSTRACTS_DIR / f"{filename_for(speaker)}.json"
    if not path.exists():
        report("false", f"No page exists for '{speaker}' (expected {path.name}). "
                        "Check the name matches the speaker's existing page.")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    data["abstract"] = abstract
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    build_index.build_index()
    build_html.build_all()

    report("true", f"Added abstract for {data['speaker']} ({path.name}).", data["speaker"])
    print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
