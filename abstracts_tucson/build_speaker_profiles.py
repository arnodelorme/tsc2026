#!/usr/bin/env python3
"""Build speaker profile JSON files and generate ranked markdown table.

Reads speakers_raw.json (from Excel extraction) and research_results.json
(from web research), merges them, computes academic rating scores,
writes individual JSON files per speaker, and generates a ranked markdown table.
"""

import json
import os
import re
import unicodedata

SPEAKERS_DIR = "speakers"
RAW_FILE = "speakers_raw.json"
RESEARCH_FILE = "research_results.json"
OUTPUT_MD = "speaker_rankings.md"


def compute_institution_score(tier: str) -> int:
    tier = tier.lower().strip()
    mapping = {"r1": 25, "r2": 18, "institute": 15, "industry": 12, "independent": 5}
    return mapping.get(tier, 5)


def compute_publication_score(n: int) -> int:
    if n >= 200: return 25
    if n >= 100: return 22
    if n >= 50: return 18
    if n >= 20: return 14
    if n >= 10: return 10
    if n >= 5: return 6
    if n >= 1: return 3
    return 0


def compute_citation_score(n: int) -> int:
    if n >= 20000: return 30
    if n >= 10000: return 27
    if n >= 5000: return 23
    if n >= 2000: return 19
    if n >= 1000: return 15
    if n >= 500: return 11
    if n >= 100: return 7
    if n >= 1: return 3
    return 0


def compute_hindex_score(h: int) -> int:
    if h >= 60: return 20
    if h >= 40: return 17
    if h >= 25: return 14
    if h >= 15: return 11
    if h >= 10: return 8
    if h >= 5: return 5
    if h >= 1: return 2
    return 0


def compute_total_score(research: dict) -> dict:
    inst = compute_institution_score(research.get("institution_tier", "independent"))
    pubs = compute_publication_score(research.get("estimated_publications", 0))
    cites = compute_citation_score(research.get("estimated_citations", 0))
    hidx = compute_hindex_score(research.get("h_index", 0))
    total = inst + pubs + cites + hidx

    if total >= 80: tier = "Tier 1 - Top Academic"
    elif total >= 60: tier = "Tier 2 - Strong Academic"
    elif total >= 40: tier = "Tier 3 - Established Researcher"
    elif total >= 20: tier = "Tier 4 - Emerging/Niche Researcher"
    else: tier = "Tier 5 - Early Career/Independent"

    return {
        "institution_score": inst,
        "publication_score": pubs,
        "citation_score": cites,
        "h_index_score": hidx,
        "total_score": total,
        "tier": tier,
    }


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[-\s]+", "_", name).strip("_")


def main():
    with open(RAW_FILE) as f:
        raw_speakers = json.load(f)

    with open(RESEARCH_FILE) as f:
        research_data = json.load(f)

    # Index research by normalized name
    research_index = {}
    for r in research_data:
        key = r.get("name", "").strip().lower()
        research_index[key] = r

    os.makedirs(SPEAKERS_DIR, exist_ok=True)

    profiles = []
    for speaker in raw_speakers:
        name = speaker["name"].strip()
        key = name.lower()

        # Try to match research data
        research = research_index.get(key, {})
        if not research:
            # Try partial matching
            for rk, rv in research_index.items():
                if name.lower().split()[-1] in rk:
                    last_name_match = name.lower().split()[-1]
                    first_initial = name.lower()[0]
                    if rk.startswith(first_initial) and last_name_match in rk:
                        research = rv
                        break

        scores = compute_total_score(research)

        profile = {
            "name": name,
            "submission_id": speaker.get("submission_id"),
            "decision": speaker.get("decision", ""),
            "abstract_title": speaker.get("title", ""),
            "abstract": speaker.get("abstract", ""),
            "authors": speaker.get("authors", ""),
            "category": speaker.get("category", ""),
            "topic": speaker.get("topic", ""),
            "affiliation": research.get("affiliation", "Unknown"),
            "position": research.get("position", "Unknown"),
            "field": research.get("field", speaker.get("category", "Unknown")),
            "institution_tier": research.get("institution_tier", "independent"),
            "estimated_publications": research.get("estimated_publications", 0),
            "estimated_citations": research.get("estimated_citations", 0),
            "h_index": research.get("h_index", 0),
            "google_scholar": research.get("google_scholar", False),
            "notable": research.get("notable", ""),
            "notes": research.get("notes", ""),
            "rating": scores,
        }
        profiles.append(profile)

        # Write individual JSON file
        filename = slugify(name) + ".json"
        filepath = os.path.join(SPEAKERS_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    # Sort by total score descending
    profiles.sort(key=lambda p: p["rating"]["total_score"], reverse=True)

    # Generate markdown table
    lines = []
    lines.append("# TSC 2026 Speaker Academic Rankings\n")
    lines.append(f"*Generated from {len(profiles)} accepted speakers (concurrent, plenary, workshop)*\n")
    lines.append("## Rating System\n")
    lines.append("| Component | Max Points |")
    lines.append("|-----------|-----------|")
    lines.append("| Institution Tier | 25 |")
    lines.append("| Publication Count | 25 |")
    lines.append("| Citation Count | 30 |")
    lines.append("| H-index | 20 |")
    lines.append("| **Total** | **100** |")
    lines.append("")
    lines.append("## Rankings\n")
    lines.append("| Rank | Name | Affiliation | Decision | Score | Tier | Pubs | Citations | H-index |")
    lines.append("|------|------|-------------|----------|-------|------|------|-----------|---------|")

    for i, p in enumerate(profiles, 1):
        name = p["name"]
        aff = p["affiliation"][:40]
        dec = p["decision"].replace("Accepted: ", "")
        score = p["rating"]["total_score"]
        tier = p["rating"]["tier"].split(" - ")[0]
        pubs = p["estimated_publications"]
        cites = p["estimated_citations"]
        h = p["h_index"]
        lines.append(f"| {i} | {name} | {aff} | {dec} | {score} | {tier} | {pubs} | {cites} | {h} |")

    lines.append("")
    lines.append("---")
    lines.append(f"*{len(profiles)} speakers ranked. Fringe science included if speaker is respected in their community.*")

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {len(profiles)} speaker profiles in {SPEAKERS_DIR}/")
    print(f"Generated rankings: {OUTPUT_MD}")
    print(f"\nTop 20 speakers:")
    for i, p in enumerate(profiles[:20], 1):
        print(f"  {i}. {p['name']} ({p['affiliation'][:30]}) - Score: {p['rating']['total_score']}")


if __name__ == "__main__":
    main()
