#!/usr/bin/env python3
"""Extract plenary speaker abstracts from old_abstracts Excel and JSON files.

Creates one JSON file per plenary talk in abstracts/ and generates index.json
via build_index.py.
"""

import json
import os
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
ABSTRACTS_DIR = ROOT / "abstracts"
OLD_SPEAKERS = ROOT / "old_abstracts" / "speakers"
EXCEL_PATH = ROOT / "old_abstracts" / "Old - 2026 Tucson Abstracts.xlsx"

# Plenary speakers from index.html with their affiliations
PLENARY_SPEAKERS = [
    {"speaker": "Roger Penrose", "affiliation": "University of Oxford", "remote": True},
    {"speaker": "Sarika Katiyar", "affiliation": "Indian Council of Medical Research"},
    {"speaker": "Nirosha Murugan", "affiliation": "Wilfrid Laurier University"},
    {"speaker": "Anirban Bandyopadhyay", "affiliation": "National Institute for Materials Science, Tsukuba, Japan"},
    {"speaker": "Susan Schneider", "affiliation": "Florida Atlantic University"},
    {"speaker": "Tracy Brandmeyer", "affiliation": "BrainMind"},
    {"speaker": "André M. Bastos", "affiliation": "Vanderbilt University"},
    {"speaker": "Edward Boyden", "affiliation": "MIT & HHMI"},
    {"speaker": "Robin Carhart-Harris", "affiliation": "UCSF Neurology"},
    {"speaker": "Stuart Hameroff", "affiliation": "University of Arizona"},
    {"speaker": "Edward Large", "affiliation": "University of Connecticut"},
    {"speaker": "Helané Wahbeh", "affiliation": "Institute of Noetic Sciences"},
    {"speaker": "Michael Levin", "affiliation": "Tufts University", "remote": True},
    {"speaker": "Alysson Muotri", "affiliation": "UC San Diego"},
    {"speaker": "Lea Gassab", "affiliation": "University of Waterloo"},
    {"speaker": "Jennifer Prendki", "affiliation": "AI & Data Science Researcher"},
    {"speaker": "Hartmut Neven", "affiliation": "Google Quantum AI"},
    {"speaker": "Beatriz Villarroel", "affiliation": "Nordic Institute for Theoretical Physics"},
    {"speaker": "Dean Radin", "affiliation": "Institute of Noetic Sciences"},
    {"speaker": "Steen Rasmussen", "affiliation": "Univ. of Southern Denmark & Santa Fe Institute"},
    {"speaker": "Terry Sejnowski", "affiliation": "Salk Institute for Biological Studies"},
    {"speaker": "Kenneth Kosik", "affiliation": "UC Santa Barbara"},
    {"speaker": "Roumiana Tsenkova", "affiliation": "Kobe University"},
]

# Map plenary speakers to their submission IDs in the Excel
# (found by searching authors column)
EXCEL_SUBMISSIONS = {
    70: "Alysson Muotri",
    81: "Nirosha Murugan",  # co-authored with Martin Picard
    105: "Edward Large",
    177: "Sarika Katiyar",
    221: "Susan Schneider",
    448: "Beatriz Villarroel",
    456: "Dean Radin",
    459: "Michael Levin",
    461: "André M. Bastos",
    462: "Kenneth Kosik",
    463: "Anirban Bandyopadhyay",
}


def speaker_to_filename(name):
    """Convert speaker name to snake_case filename."""
    name = name.lower()
    name = name.replace("é", "e").replace("á", "a").replace("ü", "u")
    name = re.sub(r"[^a-z\s]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def load_excel_abstracts():
    """Load full abstracts from the Excel file."""
    wb = openpyxl.load_workbook(str(EXCEL_PATH), read_only=True)
    ws = wb["Sheet1"]
    abstracts = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        sub_id = row[0]
        if sub_id in EXCEL_SUBMISSIONS:
            abstracts[sub_id] = {
                "submission_id": sub_id,
                "decision": row[3],
                "title": row[4],
                "abstract": row[5],
                "authors": row[6],
                "category": row[8],
                "topic": row[9],
            }
    wb.close()
    return abstracts


def load_old_speaker_json(speaker_name):
    """Try to load supplementary info from old_abstracts/speakers/ JSON."""
    fname = speaker_to_filename(speaker_name) + ".json"
    path = OLD_SPEAKERS / fname
    if path.exists():
        with open(path) as f:
            return json.load(f)
    # Try with middle initial for Kosik
    if "kosik" in fname:
        alt = OLD_SPEAKERS / "kenneth_s_kosik.json"
        if alt.exists():
            with open(alt) as f:
                return json.load(f)
    return None


def build_talk_json(speaker_info, excel_data, old_json):
    """Build the final JSON for one plenary talk."""
    talk = {
        "speaker": speaker_info["speaker"],
        "affiliation": speaker_info["affiliation"],
        "type": "plenary",
        "remote": speaker_info.get("remote", False),
        "title": None,
        "abstract": None,
        "authors": None,
        "submission_id": None,
        "decision": None,
        "category": None,
        "topic": None,
    }
    if excel_data:
        talk["title"] = excel_data["title"]
        talk["abstract"] = excel_data["abstract"]
        talk["authors"] = excel_data["authors"]
        talk["submission_id"] = excel_data["submission_id"]
        talk["decision"] = excel_data["decision"]
        talk["category"] = excel_data["category"]
        talk["topic"] = excel_data["topic"]
    elif old_json:
        talk["title"] = old_json.get("abstract_title")
        talk["abstract"] = old_json.get("abstract")
        talk["authors"] = old_json.get("authors")
        talk["submission_id"] = old_json.get("submission_id")
        talk["decision"] = old_json.get("decision")
        talk["category"] = old_json.get("category")
        talk["topic"] = old_json.get("topic")
    return talk


def main():
    excel_abstracts = load_excel_abstracts()

    # Build reverse map: speaker name -> submission ID
    name_to_sub = {}
    for sub_id, name in EXCEL_SUBMISSIONS.items():
        name_to_sub[name] = sub_id

    created = []
    missing = []

    for sp in PLENARY_SPEAKERS:
        name = sp["speaker"]
        sub_id = name_to_sub.get(name)
        excel_data = excel_abstracts.get(sub_id) if sub_id else None
        old_json = load_old_speaker_json(name)

        talk = build_talk_json(sp, excel_data, old_json)
        fname = speaker_to_filename(name) + ".json"
        out_path = ABSTRACTS_DIR / fname

        with open(out_path, "w") as f:
            json.dump(talk, f, indent=2, ensure_ascii=False)

        if talk["abstract"]:
            created.append((name, fname))
        else:
            missing.append((name, fname))

    print(f"Created {len(created)} files with abstracts:")
    for name, fname in created:
        print(f"  {fname} — {name}")

    print(f"\nCreated {len(missing)} files WITHOUT abstracts:")
    for name, fname in missing:
        print(f"  {fname} — {name}")


if __name__ == "__main__":
    main()
