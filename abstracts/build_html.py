#!/usr/bin/env python3
"""Generate individual HTML pages for each plenary speaker abstract.

Reads abstracts/*.json and produces one HTML file per speaker in
abstracts_html/.  Pages share the site nav/footer via ../nav.js and
../footer.js and link back to program.html.
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABSTRACTS_DIR = ROOT / "abstracts"
HTML_DIR = ROOT / "abstracts_html"
SKIP = {"index.json"}


def speaker_to_slug(name):
    """Convert speaker name to URL-friendly slug."""
    name = name.lower()
    for src, dst in [("é", "e"), ("á", "a"), ("ü", "u"), ("ö", "o"),
                     ("ñ", "n"), ("ç", "c"), ("â", "a")]:
        name = name.replace(src, dst)
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    return re.sub(r"\s+", "-", name.strip())


def escape(text):
    """HTML-escape text and convert special chars to entities."""
    if not text:
        return ""
    text = html.escape(text)
    text = text.replace("\u2013", "&ndash;")
    text = text.replace("\u2014", "&mdash;")
    text = text.replace("\u2018", "&lsquo;")
    text = text.replace("\u2019", "&rsquo;")
    text = text.replace("\u201c", "&ldquo;")
    text = text.replace("\u201d", "&rdquo;")
    return text


def format_abstract(text):
    """Split abstract into paragraphs."""
    if not text:
        return ""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if len(paragraphs) <= 1:
        # Try splitting on double-space or long text as single block
        return f"<p>{escape(text)}</p>"
    return "\n".join(f"<p>{escape(p)}</p>" for p in paragraphs)


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_text} &mdash; CS 2026</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #222; line-height: 1.6; background: #fff;
}}
a {{ color: #1a6fa0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
img {{ max-width: 100%; height: auto; }}

.topnav {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(10, 36, 64, 0.97); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem; height: 56px;
  box-shadow: 0 2px 8px rgba(0,0,0,.25);
}}
.topnav .nav-brand {{
  display: flex; align-items: center; gap: .6rem;
  color: #fff; font-weight: 700; font-size: 1.05rem;
}}
.topnav .nav-brand img {{ height: 36px; border-radius: 4px; }}
.topnav ul {{ list-style: none; display: flex; gap: 1.6rem; }}
.topnav ul li a {{
  color: #c8ddf0; font-size: .9rem; font-weight: 500;
  text-transform: uppercase; letter-spacing: .04em; transition: color .2s;
}}
.topnav ul li a:hover {{ color: #fff; text-decoration: none; }}
.hamburger {{ display: none; background: none; border: none; cursor: pointer; padding: 4px; }}
.hamburger span {{ display: block; width: 24px; height: 2px; background: #fff; margin: 5px 0; transition: .3s; }}

.page-header {{
  background: linear-gradient(135deg, #0a2440 0%, #0d3868 40%, #14628a 70%, #1a96b8 100%);
  color: #fff; text-align: center; padding: 7rem 2rem 2.5rem;
}}
.page-header h1 {{
  font-size: 1.8rem; font-weight: 800;
  text-shadow: 0 2px 12px rgba(0,0,0,.35); margin-bottom: .3rem;
}}
.page-header .subtitle {{ font-size: 1rem; opacity: .85; }}

.abstract-wrap {{
  max-width: 800px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem;
}}
.speaker-card {{
  display: flex; gap: 1.5rem; align-items: flex-start;
  margin-bottom: 2rem;
}}
.speaker-photo {{
  width: 120px; height: 120px; border-radius: 50%;
  object-fit: cover; flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,.15);
}}
.speaker-info h2 {{
  font-size: 1.4rem; font-weight: 700; color: #0a2440;
  margin-bottom: .2rem;
}}
.speaker-info .affiliation {{
  font-size: .95rem; color: #555; margin-bottom: .3rem;
}}
.speaker-info .tags {{
  display: flex; gap: .4rem; flex-wrap: wrap; margin-top: .3rem;
}}
.speaker-info .tag {{
  font-size: .72rem; padding: .15rem .5rem; border-radius: 10px;
  font-weight: 600; text-transform: uppercase; letter-spacing: .03em;
}}
.tag-remote {{ background: #e0f0ff; color: #1a6fa0; }}
.tag-plenary {{ background: #d6e6f0; color: #1a3050; }}

.talk-title {{
  font-size: 1.15rem; font-weight: 700; color: #0a2440;
  margin-bottom: 1.2rem; line-height: 1.4;
}}
.abstract-text {{
  font-size: .95rem; line-height: 1.7; color: #333;
}}
.abstract-text p {{ margin-bottom: 1rem; }}

.back-link {{
  display: inline-block; margin-bottom: 1.5rem;
  font-size: .9rem; font-weight: 600;
}}

footer {{
  background: #0a2440; color: #8baac8;
  padding: 2.5rem 2rem; text-align: center; font-size: .85rem;
}}
footer a {{ color: #c8ddf0; }}
footer .foot-brand {{ font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: .5rem; }}

@media (max-width: 768px) {{
  .topnav ul {{ display: none; flex-direction: column; position: absolute; top: 56px; left: 0; right: 0; background: rgba(10,36,64,.98); padding: 1rem 2rem; gap: .8rem; }}
  .topnav ul.open {{ display: flex; }}
  .hamburger {{ display: block; }}
  .page-header h1 {{ font-size: 1.4rem; }}
  .speaker-card {{ flex-direction: column; align-items: center; text-align: center; }}
  .abstract-wrap {{ padding: 1.5rem 1rem 3rem; }}
}}
</style>
</head>
<body>

<nav class="topnav">
  <a href="../index.html" class="nav-brand">
    <img src="../img/logo.png" alt="CS Logo">
    <span>CS 2026</span>
  </a>
  <button class="hamburger" aria-label="Menu" onclick="document.querySelector('.topnav ul').classList.toggle('open')">
    <span></span><span></span><span></span>
  </button>
  <ul></ul>
</nav>
<script src="../nav.js"></script>

<header class="page-header">
  <h1>{speaker_name}</h1>
  <p class="subtitle">{affiliation}</p>
</header>

<div class="abstract-wrap">
  <a href="../program.html" class="back-link">&larr; Back to Program</a>

  <div class="speaker-card">
{photo_html}
    <div class="speaker-info">
      <h2>{speaker_name}</h2>
      <div class="affiliation">{affiliation}</div>
      <div class="tags">
        <span class="tag tag-plenary">{talk_type}</span>
{remote_tag}
      </div>
    </div>
  </div>

{title_html}

{abstract_html}

</div>

<footer></footer>
<script src="../footer.js"></script>

</body>
</html>
"""


def build_all():
    HTML_DIR.mkdir(exist_ok=True)

    count = 0
    for path in sorted(ABSTRACTS_DIR.glob("*.json")):
        if path.name in SKIP:
            continue
        with open(path) as f:
            data = json.load(f)
        if "speaker" not in data:
            continue

        slug = speaker_to_slug(data["speaker"])
        speaker = escape(data["speaker"])
        affiliation = escape(data.get("affiliation") or "")
        title = data.get("title")
        abstract = data.get("abstract")
        photo = data.get("photo")
        remote = data.get("remote", False)
        talk_type = escape(data.get("type", "plenary")).capitalize()

        title_text = escape(title) if title else speaker
        title_html = (f'  <div class="talk-title">{escape(title)}</div>'
                      if title else "")

        if abstract:
            abstract_html = f'  <div class="abstract-text">\n{format_abstract(abstract)}\n  </div>'
        else:
            abstract_html = '  <p style="color:#888;font-style:italic;">Abstract not yet available.</p>'

        if photo:
            photo_html = f'    <img class="speaker-photo" src="../{escape(photo)}" alt="{speaker}">'
        else:
            photo_html = ""

        remote_tag = ('        <span class="tag tag-remote">Remote</span>'
                      if remote else "")

        page = PAGE_TEMPLATE.format(
            title_text=title_text,
            speaker_name=speaker,
            affiliation=affiliation,
            photo_html=photo_html,
            talk_type=talk_type,
            remote_tag=remote_tag,
            title_html=title_html,
            abstract_html=abstract_html,
        )

        out_path = HTML_DIR / f"{slug}.html"
        out_path.write_text(page, encoding="utf-8")
        count += 1

    print(f"Generated {count} abstract pages in abstracts_html/")


if __name__ == "__main__":
    build_all()
