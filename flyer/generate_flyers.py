#!/usr/bin/env python3
"""Generate 10 JCS journal ad variants for Consciousness Science 2026.

Dimensions: 220mm x 156mm portrait, no bleed, 300 DPI.
Output: SVG files with embedded base64 images.
"""

import base64
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# Paths
FLYER_DIR = Path(__file__).parent
IMG_DIR = FLYER_DIR.parent / "img"
OUT_DIR = FLYER_DIR / "variants"
OUT_DIR.mkdir(exist_ok=True)

# Load and encode images
def load_b64(path, convert_cmd=None):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

LOGO_B64 = load_b64(IMG_DIR / "logo.png")
# Use pre-converted JPEG for the aerial
AERIAL_B64 = open("/tmp/aerial_b64.txt").read().strip()

# Dimensions in mm
W = 156
H = 220

# Colors from cs2026.org
NAVY = "#0a2440"
NAVY_MID = "#0d3868"
TEAL = "#1a96b8"
TEAL_DARK = "#14628a"
GOLD = "#e8a727"
GOLD_LIGHT = "#f0bc4a"
WHITE = "#ffffff"
LIGHT_BG = "#f5f8fb"
NEAR_WHITE = "#e8eef4"
DARK_TEXT = "#222222"
GRAY = "#555555"

# Conference content
TITLE = "Consciousness Science 2026"
SUBTITLE = "International Interdisciplinary Conference"
DATES = "October 11–16, 2026"
VENUE = "Paradise Point Resort & Spa"
LOCATION = "San Diego, California"
WEBSITE = "cs2026.org"
ABSTRACT_DEADLINE = "Abstract Deadline: July 1, 2026"
ABSTRACT_NOTE = "(check website for extensions)"

THEMES_SHORT = [
    "Neural Correlates",
    "Predictive Coding",
    "Theories of Consciousness",
    "Quantum Brain Biology",
    "Origins of Life",
    "AI & Consciousness",
    "The Hard Problem",
    "Free Will & Causation",
    "Consciousness & Reality",
    "Phenomenology",
    "Psychedelics",
    "Non-local Hypotheses",
]

THEMES_COMPACT = [
    "Neuroscience", "Quantum Biology", "AI & Computation",
    "Philosophy", "Physics", "Origins of Life",
]


def svg_header(extra_defs=""):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}mm" height="{H}mm"
     viewBox="0 0 {W} {H}">
<defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&amp;display=swap');
    text {{ font-family: 'Inter', 'Segoe UI', Helvetica, Arial, sans-serif; }}
  </style>
  {extra_defs}
</defs>
"""


def svg_footer():
    return "</svg>\n"


_logo_clip_counter = 0

def logo_image(x, y, width, height=None, corner_radius=None):
    """Embed logo. Aspect ratio ~0.874:1 (346x396). Subtle rounded corners."""
    global _logo_clip_counter
    if height is None:
        height = width / 0.874
    if corner_radius is None:
        corner_radius = width * 0.06  # subtle ~6% of width
    _logo_clip_counter += 1
    clip_id = f"logoClip{_logo_clip_counter}"
    return (
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{corner_radius:.1f}" /></clipPath>\n'
        f'<image x="{x}" y="{y}" width="{width}" height="{height}" xlink:href="data:image/png;base64,{LOGO_B64}" clip-path="url(#{clip_id})" />\n'
    )


def aerial_image(x, y, width, height, clip_id=None, opacity=1.0):
    """Embed aerial photo. Aspect ratio ~1.6:1."""
    clip = f'clip-path="url(#{clip_id})"' if clip_id else ""
    op = f'opacity="{opacity}"' if opacity < 1.0 else ""
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" xlink:href="data:image/jpeg;base64,{AERIAL_B64}" preserveAspectRatio="xMidYMid slice" {clip} {op} />\n'


def text_elem(x, y, text, size=4, weight=400, fill=WHITE, anchor="middle", spacing=None, transform=None):
    ls = f'letter-spacing="{spacing}"' if spacing else ""
    tr = f'transform="{transform}"' if transform else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {ls} {tr}>{xml_escape(str(text))}</text>\n'


def multiline_text(x, y, lines, size=3, weight=400, fill=WHITE, anchor="middle", line_height=1.4):
    """Multiple tspan lines."""
    out = f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">\n'
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else size * line_height
        out += f'  <tspan x="{x}" dy="{dy}">{xml_escape(str(line))}</tspan>\n'
    out += "</text>\n"
    return out


def rect(x, y, w, h, fill, rx=0, opacity=1.0):
    op = f'opacity="{opacity}"' if opacity < 1.0 else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="{rx}" {op} />\n'


def line_elem(x1, y1, x2, y2, stroke, width=0.5):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" />\n'


def gradient_rect(id_name, x, y, w, h, color1, color2, direction="vertical"):
    grad_id = f"grad_{id_name}"
    if direction == "vertical":
        grad = f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{color1}"/><stop offset="100%" stop-color="{color2}"/></linearGradient>'
    elif direction == "diagonal":
        grad = f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{color1}"/><stop offset="100%" stop-color="{color2}"/></linearGradient>'
    else:
        grad = f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="{color1}"/><stop offset="100%" stop-color="{color2}"/></linearGradient>'
    return grad, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{grad_id})" />\n'


def wave_pattern(y_offset, color=WHITE, opacity=0.08, scale=1.0):
    """Decorative wave curves."""
    sw = W * scale
    return f"""<path d="M 0 {y_offset} Q {W*0.25} {y_offset-6*scale} {W*0.5} {y_offset} Q {W*0.75} {y_offset+6*scale} {W} {y_offset}"
      fill="none" stroke="{color}" stroke-width="0.3" opacity="{opacity}" />
<path d="M 0 {y_offset+3} Q {W*0.25} {y_offset-3*scale} {W*0.5} {y_offset+3} Q {W*0.75} {y_offset+9*scale} {W} {y_offset+3}"
      fill="none" stroke="{color}" stroke-width="0.2" opacity="{opacity*0.7}" />\n"""


def neural_dots(cx, cy, radius, count=6, dot_r=0.4, color=TEAL, opacity=0.3):
    """Radial dot pattern suggesting neural connectivity."""
    import math
    out = ""
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        out += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_r}" fill="{color}" opacity="{opacity}" />\n'
        # connecting line
        out += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="0.15" opacity="{opacity*0.5}" />\n'
    out += f'<circle cx="{cx}" cy="{cy}" r="{dot_r*0.8}" fill="{color}" opacity="{opacity}" />\n'
    return out


def connectome_grid(x0, y0, w, h, spacing=8, color=TEAL, opacity=0.06):
    """Grid of connected dots suggesting connectomics."""
    import math, random
    random.seed(42)
    out = ""
    nodes = []
    for gx in range(int(w/spacing) + 1):
        for gy in range(int(h/spacing) + 1):
            nx = x0 + gx * spacing + random.uniform(-1.5, 1.5)
            ny = y0 + gy * spacing + random.uniform(-1.5, 1.5)
            nodes.append((nx, ny))
            out += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="0.3" fill="{color}" opacity="{opacity*3}" />\n'
    # connect nearby nodes
    for i, (ax, ay) in enumerate(nodes):
        for j, (bx, by) in enumerate(nodes):
            if i >= j:
                continue
            dist = math.sqrt((ax-bx)**2 + (ay-by)**2)
            if dist < spacing * 1.5 and random.random() < 0.3:
                out += f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="0.12" opacity="{opacity}" />\n'
    return out


def themes_column(x, y, themes, size=2.8, fill=WHITE, anchor="start", spacing=4.2):
    """Vertical list of themes."""
    out = ""
    for i, t in enumerate(themes):
        out += text_elem(x, y + i * spacing, t, size=size, weight=400, fill=fill, anchor=anchor)
    return out


def abstract_box(x, y, w, h, fill_bg, fill_text):
    """Abstract deadline call-out box."""
    out = rect(x, y, w, h, fill_bg, rx=2)
    out += text_elem(x + w/2, y + h*0.4, ABSTRACT_DEADLINE, size=3, weight=700, fill=fill_text)
    out += text_elem(x + w/2, y + h*0.75, ABSTRACT_NOTE, size=2.2, weight=400, fill=fill_text)
    return out


# ─── VARIANT 1: Navy gradient + aerial strip at bottom ───────────────

def variant_01():
    defs_grad = f'''
    <linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{NAVY}"/>
      <stop offset="60%" stop-color="{NAVY_MID}"/>
      <stop offset="100%" stop-color="{TEAL_DARK}"/>
    </linearGradient>'''

    s = svg_header(defs_grad)
    # Background
    s += f'<rect width="{W}" height="{H}" fill="url(#bg1)" />\n'

    # Subtle wave decorations
    for i in range(5):
        s += wave_pattern(40 + i*25, WHITE, 0.04 + i*0.01)

    # Logo — large, centered at top
    logo_w = 45
    s += logo_image((W - logo_w)/2, 8, logo_w)

    # Title
    s += text_elem(W/2, 68, "CONSCIOUSNESS", size=9, weight=800, fill=WHITE, spacing="0.8")
    s += text_elem(W/2, 78, "SCIENCE 2026", size=7, weight=300, fill=NEAR_WHITE, spacing="1.5")

    # Teal accent line
    s += line_elem(W/2 - 25, 83, W/2 + 25, 83, TEAL, 0.6)

    # Subtitle
    s += text_elem(W/2, 89, SUBTITLE, size=3.2, weight=400, fill=NEAR_WHITE)

    # Dates & venue
    s += text_elem(W/2, 100, DATES, size=4, weight=600, fill=GOLD)
    s += text_elem(W/2, 106, VENUE, size=3.2, weight=500, fill=WHITE)
    s += text_elem(W/2, 111, LOCATION, size=3, weight=400, fill=NEAR_WHITE)

    # Themes in two columns
    left_themes = THEMES_SHORT[:6]
    right_themes = THEMES_SHORT[6:]
    s += text_elem(W/2, 120, "— CONFERENCE THEMES —", size=2.5, weight=600, fill=TEAL, spacing="0.5")
    s += themes_column(12, 127, left_themes, size=2.5, fill=NEAR_WHITE)
    s += themes_column(W/2 + 4, 127, right_themes, size=2.5, fill=NEAR_WHITE)

    # Abstract deadline box
    s += abstract_box(12, 154, W - 24, 12, GOLD, NAVY)

    # Aerial photo strip at bottom
    s += aerial_image(0, 172, W, 38)
    # Dark overlay at top of photo for blending
    s += f'<rect x="0" y="172" width="{W}" height="10" fill="url(#bg1)" opacity="0.5" />\n'

    # Website at very bottom over photo
    s += rect(0, H - 10, W, 10, NAVY, opacity=0.8)
    s += text_elem(W/2, H - 3.5, WEBSITE, size=3.5, weight=700, fill=GOLD)

    s += svg_footer()
    return s


# ─── VARIANT 2: Pure navy, neural network pattern, large logo ────────

def variant_02():
    s = svg_header()
    s += rect(0, 0, W, H, NAVY)

    # Neural connectome background
    s += connectome_grid(0, 0, W, H, spacing=10, color=TEAL, opacity=0.05)

    # Logo large
    logo_w = 45
    s += logo_image((W - logo_w)/2, 6, logo_w)

    # Title block
    s += text_elem(W/2, 66, "CONSCIOUSNESS", size=9.5, weight=900, fill=WHITE, spacing="0.5")
    s += text_elem(W/2, 77, "SCIENCE 2026", size=7.5, weight=300, fill=TEAL, spacing="1.2")

    # Thin gold line
    s += line_elem(20, 82, W-20, 82, GOLD, 0.4)

    s += text_elem(W/2, 89, SUBTITLE, size=3, weight=400, fill=NEAR_WHITE)

    # Central info block
    s += text_elem(W/2, 101, DATES, size=4.5, weight=700, fill=GOLD)
    s += text_elem(W/2, 107, f"{VENUE} — {LOCATION}", size=3, weight=400, fill=NEAR_WHITE)

    # Compact theme pills
    s += text_elem(W/2, 118, "THEMES", size=2.8, weight=700, fill=TEAL, spacing="1")
    pill_themes = THEMES_COMPACT
    pill_y = 124
    for i, t in enumerate(pill_themes):
        col = i % 3
        row = i // 3
        px = 10 + col * 46
        py = pill_y + row * 8
        s += rect(px, py, 42, 6, TEAL_DARK, rx=1.5)
        s += text_elem(px + 21, py + 4.2, t, size=2.5, weight=500, fill=WHITE)

    # Abstract deadline
    s += rect(10, 148, W-20, 14, GOLD, rx=2)
    s += text_elem(W/2, 155.5, ABSTRACT_DEADLINE, size=3.2, weight=700, fill=NAVY)
    s += text_elem(W/2, 160, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Neural dot clusters as decoration
    s += neural_dots(20, 175, 6, 8, 0.4, TEAL, 0.15)
    s += neural_dots(W-20, 185, 5, 6, 0.35, TEAL, 0.12)

    # Footer
    s += line_elem(20, 197, W-20, 197, TEAL, 0.3)
    s += text_elem(W/2, 203, WEBSITE, size=4, weight=700, fill=GOLD)

    # Bottom accent
    s += rect(0, H-2, W, 2, TEAL)

    s += svg_footer()
    return s


# ─── VARIANT 3: Aerial full background with dark overlay, large logo ─

def variant_03():
    defs = f'''
    <linearGradient id="overlay3" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{NAVY}" stop-opacity="0.92"/>
      <stop offset="50%" stop-color="{NAVY}" stop-opacity="0.75"/>
      <stop offset="80%" stop-color="{NAVY}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{NAVY}" stop-opacity="0.3"/>
    </linearGradient>'''

    s = svg_header(defs)
    # Aerial as full background
    s += aerial_image(0, 0, W, H)
    # Dark gradient overlay
    s += f'<rect width="{W}" height="{H}" fill="url(#overlay3)" />\n'

    # Logo large
    logo_w = 45
    s += logo_image((W - logo_w)/2, 10, logo_w)

    # Title
    s += text_elem(W/2, 72, "CONSCIOUSNESS", size=9, weight=800, fill=WHITE, spacing="0.6")
    s += text_elem(W/2, 82, "SCIENCE 2026", size=7, weight=300, fill=WHITE, spacing="1.5")

    # Subtitle
    s += text_elem(W/2, 90, SUBTITLE, size=3, weight=400, fill=NEAR_WHITE)

    # Gold divider
    s += line_elem(W/2-20, 95, W/2+20, 95, GOLD, 0.5)

    # Dates centered
    s += text_elem(W/2, 103, DATES, size=4.5, weight=700, fill=GOLD)
    s += text_elem(W/2, 109, VENUE, size=3.5, weight=500, fill=WHITE)
    s += text_elem(W/2, 114, LOCATION, size=3, weight=400, fill=NEAR_WHITE)

    # Themes in single centered column
    s += text_elem(W/2, 125, "— THEMES —", size=2.5, weight=600, fill=GOLD, spacing="0.8")
    for i, t in enumerate(THEMES_SHORT[:8]):
        s += text_elem(W/2, 131 + i*5, t, size=2.6, weight=400, fill=NEAR_WHITE)

    # Abstract deadline
    s += rect(15, 174, W-30, 13, GOLD, rx=2, opacity=0.95)
    s += text_elem(W/2, 181, ABSTRACT_DEADLINE, size=3.2, weight=700, fill=NAVY)
    s += text_elem(W/2, 185.5, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Website
    s += text_elem(W/2, 200, WEBSITE, size=4, weight=700, fill=GOLD)

    # Bottom teal accent
    s += rect(0, H-1.5, W, 1.5, TEAL)

    s += svg_footer()
    return s


# ─── VARIANT 4: Split — aerial top half, white bottom, small logo ────

def variant_04():
    split_y = 95
    defs = f'''
    <clipPath id="topClip4">
      <rect x="0" y="0" width="{W}" height="{split_y}"/>
    </clipPath>
    <linearGradient id="topOverlay4" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{NAVY}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{NAVY}" stop-opacity="0.4"/>
    </linearGradient>'''

    s = svg_header(defs)

    # Top half: aerial with overlay
    s += aerial_image(0, 0, W, split_y * 1.2, clip_id="topClip4")
    s += f'<rect x="0" y="0" width="{W}" height="{split_y}" fill="url(#topOverlay4)" />\n'

    # Small logo top-left
    s += logo_image(8, 6, 22)

    # Title over photo
    s += text_elem(W/2, 45, "CONSCIOUSNESS", size=8.5, weight=800, fill=WHITE, spacing="0.5")
    s += text_elem(W/2, 55, "SCIENCE 2026", size=6.5, weight=300, fill=WHITE, spacing="1.2")
    s += text_elem(W/2, 63, SUBTITLE, size=2.8, weight=400, fill=NEAR_WHITE)

    # Date badge over photo
    s += rect(W/2-30, 70, 60, 9, GOLD, rx=20)
    s += text_elem(W/2, 76.5, DATES, size=3, weight=700, fill=NAVY)

    # Bottom half: white
    s += rect(0, split_y, W, H - split_y, WHITE)

    # Venue info
    s += text_elem(W/2, split_y + 10, VENUE, size=3.5, weight=600, fill=NAVY)
    s += text_elem(W/2, split_y + 15.5, LOCATION, size=3, weight=400, fill=GRAY)

    # Teal accent line
    s += line_elem(W/2-25, split_y + 20, W/2+25, split_y + 20, TEAL, 0.5)

    # Themes grid on white
    s += text_elem(W/2, split_y + 27, "Conference Themes", size=3, weight=700, fill=NAVY)
    left_themes = THEMES_SHORT[:6]
    right_themes = THEMES_SHORT[6:]
    s += themes_column(12, split_y + 33, left_themes, size=2.3, fill=DARK_TEXT)
    s += themes_column(W/2 + 4, split_y + 33, right_themes, size=2.3, fill=DARK_TEXT)

    # Abstract deadline
    s += rect(10, split_y + 60, W-20, 12, NAVY, rx=2)
    s += text_elem(W/2, split_y + 66.5, ABSTRACT_DEADLINE, size=3, weight=700, fill=GOLD)
    s += text_elem(W/2, split_y + 70.5, ABSTRACT_NOTE, size=2, weight=400, fill=NEAR_WHITE)

    # Footer
    s += rect(0, H-8, W, 8, NAVY)
    s += text_elem(W/2, H-3, WEBSITE, size=3.5, weight=700, fill=GOLD)

    s += svg_footer()
    return s


# ─── VARIANT 5: Light/white minimalist, large logo, no aerial ────────

def variant_05():
    s = svg_header()
    s += rect(0, 0, W, H, WHITE)

    # Top navy accent band
    s += rect(0, 0, W, 3, NAVY)

    # Logo large centered
    logo_w = 45
    s += logo_image((W - logo_w)/2, 8, logo_w)

    # Title in navy
    s += text_elem(W/2, 68, "CONSCIOUSNESS", size=9, weight=800, fill=NAVY, spacing="0.6")
    s += text_elem(W/2, 78, "SCIENCE 2026", size=7, weight=300, fill=TEAL, spacing="1.5")

    # Teal underline
    s += line_elem(W/2-30, 83, W/2+30, 83, TEAL, 0.6)

    s += text_elem(W/2, 90, SUBTITLE, size=3, weight=400, fill=GRAY)

    # Date in gold pill
    s += rect(W/2-32, 96, 64, 10, NAVY, rx=20)
    s += text_elem(W/2, 103, DATES, size=3.5, weight=700, fill=GOLD)

    # Venue
    s += text_elem(W/2, 113, VENUE, size=3.5, weight=600, fill=NAVY)
    s += text_elem(W/2, 118, LOCATION, size=3, weight=400, fill=GRAY)

    # Light theme cards
    s += text_elem(W/2, 128, "Conference Themes", size=3, weight=700, fill=NAVY)
    for i, t in enumerate(THEMES_SHORT):
        col = i % 2
        row = i // 2
        bx = 8 + col * 73
        by = 132 + row * 7
        s += rect(bx, by, 70, 5.5, LIGHT_BG, rx=1.5)
        s += line_elem(bx, by, bx, by+5.5, TEAL, 1)
        s += text_elem(bx + 4, by + 4, t, size=2.3, weight=500, fill=NAVY, anchor="start")

    # Abstract deadline
    s += rect(10, 177, W-20, 13, GOLD, rx=2)
    s += text_elem(W/2, 184, ABSTRACT_DEADLINE, size=3.2, weight=700, fill=NAVY)
    s += text_elem(W/2, 188.5, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Footer
    s += rect(0, H-8, W, 8, NAVY)
    s += text_elem(W/2, H-3, WEBSITE, size=3.5, weight=700, fill=GOLD)

    # Bottom teal accent
    s += rect(0, H-1, W, 1, TEAL)

    s += svg_footer()
    return s


# ─── VARIANT 6: Centered symmetrical, circular aerial inset, large logo ─

def variant_06():
    defs = f'''
    <clipPath id="circleClip6">
      <circle cx="{W/2}" cy="160" r="28"/>
    </clipPath>
    <linearGradient id="bg6" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{NAVY}"/>
      <stop offset="100%" stop-color="{NAVY_MID}"/>
    </linearGradient>'''

    s = svg_header(defs)
    s += f'<rect width="{W}" height="{H}" fill="url(#bg6)" />\n'

    # Decorative circles
    s += f'<circle cx="{W/2}" cy="110" r="55" fill="none" stroke="{TEAL}" stroke-width="0.15" opacity="0.2" />\n'
    s += f'<circle cx="{W/2}" cy="110" r="70" fill="none" stroke="{TEAL}" stroke-width="0.1" opacity="0.12" />\n'
    s += f'<circle cx="{W/2}" cy="110" r="85" fill="none" stroke="{TEAL}" stroke-width="0.08" opacity="0.07" />\n'

    # Large logo
    logo_w = 45
    s += logo_image((W - logo_w)/2, 5, logo_w)

    # Title
    s += text_elem(W/2, 64, "CONSCIOUSNESS", size=8.5, weight=800, fill=WHITE, spacing="0.5")
    s += text_elem(W/2, 74, "SCIENCE 2026", size=6.5, weight=300, fill=TEAL, spacing="1.2")
    s += text_elem(W/2, 81, SUBTITLE, size=2.8, weight=400, fill=NEAR_WHITE)

    # Date
    s += text_elem(W/2, 92, DATES, size=4, weight=700, fill=GOLD)
    s += text_elem(W/2, 98, VENUE, size=3.2, weight=500, fill=WHITE)
    s += text_elem(W/2, 103, LOCATION, size=2.8, weight=400, fill=NEAR_WHITE)

    # Compact themes ring-style (horizontal)
    s += text_elem(W/2, 113, "THEMES", size=2.5, weight=600, fill=TEAL, spacing="1")
    for i, t in enumerate(THEMES_COMPACT):
        col = i % 3
        row = i // 3
        tx = 15 + col * 44
        ty = 118 + row * 6
        s += text_elem(tx + 20, ty + 4, t, size=2.3, weight=400, fill=NEAR_WHITE)

    # Circular aerial inset
    s += f'<circle cx="{W/2}" cy="160" r="29" fill="{TEAL_DARK}" />\n'
    s += aerial_image(W/2-30, 130, 60, 60, clip_id="circleClip6")
    s += f'<circle cx="{W/2}" cy="160" r="28" fill="none" stroke="{GOLD}" stroke-width="0.5" />\n'

    # Abstract deadline below circle
    s += text_elem(W/2, 195, ABSTRACT_DEADLINE, size=3, weight=700, fill=GOLD)
    s += text_elem(W/2, 200, ABSTRACT_NOTE, size=2.2, weight=400, fill=NEAR_WHITE)

    # Website
    s += text_elem(W/2, 210, WEBSITE, size=3.5, weight=700, fill=GOLD)

    # Bottom accent
    s += rect(0, H-1.5, W, 1.5, TEAL)

    s += svg_footer()
    return s


# ─── VARIANT 7: Bold typographic, small logo, no aerial, gold accents ─

def variant_07():
    s = svg_header()
    s += rect(0, 0, W, H, NAVY)

    # Gold top accent
    s += rect(0, 0, W, 2, GOLD)

    # Small logo top-right
    s += logo_image(W - 28, 4, 22)

    # Giant typography
    s += text_elem(12, 30, "CON", size=18, weight=900, fill=WHITE, anchor="start", spacing="-0.5")
    s += text_elem(12, 48, "SCIOUS", size=18, weight=900, fill=WHITE, anchor="start", spacing="-0.5")
    s += text_elem(12, 66, "NESS", size=18, weight=900, fill=TEAL, anchor="start", spacing="-0.5")

    # Thin line
    s += line_elem(12, 72, 80, 72, GOLD, 0.5)

    s += text_elem(12, 79, "SCIENCE 2026", size=6, weight=300, fill=NEAR_WHITE, anchor="start", spacing="1.5")
    s += text_elem(12, 85, SUBTITLE, size=2.8, weight=400, fill=NEAR_WHITE, anchor="start")

    # Date block
    s += rect(12, 92, W - 24, 14, TEAL_DARK, rx=2)
    s += text_elem(W/2, 99.5, DATES, size=4, weight=700, fill=WHITE)
    s += text_elem(W/2, 104, f"{VENUE} · {LOCATION}", size=2.5, weight=400, fill=NEAR_WHITE)

    # Themes left-aligned with dots
    s += text_elem(12, 115, "THEMES", size=2.8, weight=700, fill=GOLD, anchor="start", spacing="1")
    for i, t in enumerate(THEMES_SHORT):
        ty = 121 + i * 5
        s += f'<circle cx="14" cy="{ty-0.8}" r="0.7" fill="{TEAL}" />\n'
        s += text_elem(18, ty, t, size=2.5, weight=400, fill=NEAR_WHITE, anchor="start")

    # Abstract deadline
    s += rect(12, 183, W-24, 13, GOLD, rx=2)
    s += text_elem(W/2, 190, ABSTRACT_DEADLINE, size=3.2, weight=700, fill=NAVY)
    s += text_elem(W/2, 194.5, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Website
    s += text_elem(12, 207, WEBSITE, size=4, weight=700, fill=GOLD, anchor="start")

    # Bottom gold accent
    s += rect(0, H-2, W, 2, GOLD)

    s += svg_footer()
    return s


# ─── VARIANT 8: Diagonal slice with aerial, large logo ───────────────

def variant_08():
    defs = f'''
    <clipPath id="diagClip8">
      <polygon points="0,130 {W},110 {W},{H} 0,{H}"/>
    </clipPath>
    <linearGradient id="bg8" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{NAVY}"/>
      <stop offset="100%" stop-color="{TEAL_DARK}"/>
    </linearGradient>'''

    s = svg_header(defs)
    s += f'<rect width="{W}" height="{H}" fill="url(#bg8)" />\n'

    # Aerial in diagonal bottom section
    s += aerial_image(0, 100, W, 120, clip_id="diagClip8")
    # Overlay on aerial
    s += f'<polygon points="0,130 {W},110 {W},{H} 0,{H}" fill="{NAVY}" opacity="0.5" />\n'

    # Diagonal divider line
    s += f'<line x1="0" y1="130" x2="{W}" y2="110" stroke="{GOLD}" stroke-width="0.5" />\n'

    # Logo large
    logo_w = 45
    s += logo_image((W - logo_w)/2, 5, logo_w)

    # Title
    s += text_elem(W/2, 62, "CONSCIOUSNESS", size=8.5, weight=800, fill=WHITE, spacing="0.5")
    s += text_elem(W/2, 72, "SCIENCE", size=6.5, weight=300, fill=WHITE, spacing="1.2")

    s += text_elem(W/2, 80, SUBTITLE, size=2.8, weight=400, fill=NEAR_WHITE)

    # Date & venue
    s += text_elem(W/2, 92, DATES, size=4, weight=700, fill=GOLD)
    s += text_elem(W/2, 98, VENUE, size=3, weight=500, fill=WHITE)
    s += text_elem(W/2, 103, LOCATION, size=2.8, weight=400, fill=NEAR_WHITE)

    # Plenary session themes over the diagonal area
    s += text_elem(W/2, 118, "PLENARY SESSIONS", size=2.8, weight=600, fill=GOLD, spacing="0.8")
    plenary_left = [
        "Quantum Biophotonics",
        "Cerebral Organoids",
        "Neuroscience",
        "Psychedelics & Consciousness",
        "Non-Local Consciousness & Psi",
        "Quantum AI & Consciousness",
        "Origins of Life & Consciousness",
    ]
    plenary_right = [
        "Psi and UAP",
        "Connectomics or Wavefields?",
        "Life or Consciousness First?",
        "Altered States of Consciousness",
        "Consciousness and AI",
        "Anesthesia & Consciousness",
        "Geometry & Platonic Values",
    ]
    s += themes_column(12, 124, plenary_left, size=2.8, fill=NEAR_WHITE)
    s += themes_column(W/2 + 4, 124, plenary_right, size=2.8, fill=NEAR_WHITE)

    # Abstract deadline
    s += rect(12, 178, W-24, 12, GOLD, rx=2, opacity=0.95)
    s += text_elem(W/2, 184.5, ABSTRACT_DEADLINE, size=3, weight=700, fill=NAVY)
    s += text_elem(W/2, 188.5, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Website
    s += rect(0, H-9, W, 9, NAVY, opacity=0.85)
    s += text_elem(W/2, H-3.5, WEBSITE, size=3.5, weight=700, fill=GOLD)

    s += svg_footer()
    return s


# ─── VARIANT 9: Dark with wave pattern, coastal feel, large logo ─────

def variant_09():
    s = svg_header()
    s += rect(0, 0, W, H, NAVY)

    # Multiple wave layers for ocean feel
    for i in range(12):
        y = 30 + i * 16
        opacity = 0.03 + (i % 3) * 0.02
        color = TEAL if i % 2 == 0 else "#1a7fa0"
        s += wave_pattern(y, color, opacity, scale=1.0 + i*0.1)

    # Teal top accent
    s += rect(0, 0, W, 1.5, TEAL)

    # Logo large
    logo_w = 45
    s += logo_image((W - logo_w)/2, 5, logo_w)

    # Title
    s += text_elem(W/2, 65, "CONSCIOUSNESS", size=9, weight=800, fill=WHITE, spacing="0.5")
    s += text_elem(W/2, 76, "SCIENCE", size=8, weight=200, fill=TEAL, spacing="2")
    s += text_elem(W/2, 85, "2026", size=8, weight=200, fill=TEAL, spacing="3")

    s += text_elem(W/2, 93, SUBTITLE, size=2.8, weight=400, fill=NEAR_WHITE)

    # Wave divider
    s += f'<path d="M 20 98 Q {W/2} 92 {W-20} 98" fill="none" stroke="{GOLD}" stroke-width="0.4" />\n'

    # Date
    s += text_elem(W/2, 106, DATES, size=4.2, weight=700, fill=GOLD)
    s += text_elem(W/2, 112, VENUE, size=3.2, weight=500, fill=WHITE)
    s += text_elem(W/2, 117, LOCATION, size=3, weight=400, fill=NEAR_WHITE)

    # Themes as a flowing list
    s += text_elem(W/2, 127, "· CONFERENCE THEMES ·", size=2.5, weight=600, fill=TEAL, spacing="0.5")
    # Two columns
    left_themes = THEMES_SHORT[:6]
    right_themes = THEMES_SHORT[6:]
    s += themes_column(12, 133, left_themes, size=2.4, fill=NEAR_WHITE)
    s += themes_column(W/2 + 4, 133, right_themes, size=2.4, fill=NEAR_WHITE)

    # Decorative wave before deadline
    s += f'<path d="M 10 162 Q {W/2} 156 {W-10} 162" fill="none" stroke="{TEAL}" stroke-width="0.3" opacity="0.3" />\n'

    # Abstract deadline
    s += rect(15, 166, W-30, 13, GOLD, rx=2)
    s += text_elem(W/2, 173, ABSTRACT_DEADLINE, size=3.2, weight=700, fill=NAVY)
    s += text_elem(W/2, 177.5, ABSTRACT_NOTE, size=2.2, weight=400, fill=NAVY)

    # Neural dots bottom
    s += neural_dots(30, 195, 8, 10, 0.35, TEAL, 0.1)
    s += neural_dots(W-30, 195, 6, 8, 0.3, TEAL, 0.08)

    # Website
    s += text_elem(W/2, 210, WEBSITE, size=4, weight=700, fill=GOLD)

    # Bottom accents
    s += rect(0, H-1.5, W, 1.5, GOLD)

    s += svg_footer()
    return s


# ─── VARIANT 10: Classic academic, small logo, aerial bottom third ───

def variant_10():
    aerial_y = 148
    defs = f'''
    <clipPath id="bottomClip10">
      <rect x="0" y="{aerial_y}" width="{W}" height="{H - aerial_y}"/>
    </clipPath>'''

    s = svg_header(defs)
    s += rect(0, 0, W, H, WHITE)

    # Top navy header band
    s += rect(0, 0, W, 50, NAVY)

    # Small logo in header
    s += logo_image(8, 5, 22)

    # Title in header
    s += text_elem(W/2 + 8, 20, "Consciousness Science", size=6, weight=700, fill=WHITE, spacing="0.2")
    s += text_elem(W/2 + 8, 28, "2026", size=5, weight=300, fill=GOLD, spacing="2")
    s += text_elem(W/2 + 8, 34, SUBTITLE, size=2.5, weight=400, fill=NEAR_WHITE)

    # Teal accent under header
    s += rect(0, 50, W, 1.5, TEAL)

    # Date & venue centered on white
    s += text_elem(W/2, 62, DATES, size=4.5, weight=700, fill=NAVY)
    s += text_elem(W/2, 68, VENUE, size=3.2, weight=500, fill=TEAL_DARK)
    s += text_elem(W/2, 73, LOCATION, size=3, weight=400, fill=GRAY)

    # Divider
    s += line_elem(20, 78, W-20, 78, NEAR_WHITE, 0.5)

    # Themes in structured grid on white
    s += text_elem(W/2, 85, "Conference Themes", size=3.2, weight=700, fill=NAVY)
    for i, t in enumerate(THEMES_SHORT):
        col = i % 2
        row = i // 2
        bx = 10 + col * 73
        by = 90 + row * 7.5
        s += rect(bx, by, 70, 6, LIGHT_BG, rx=1)
        s += line_elem(bx, by, bx, by+6, TEAL, 0.8)
        s += text_elem(bx + 4, by + 4.3, t, size=2.3, weight=500, fill=NAVY, anchor="start")

    # Abstract deadline
    s += rect(10, 137, W-20, 9, GOLD, rx=2)
    s += text_elem(W/2, 142.5, ABSTRACT_DEADLINE, size=2.8, weight=700, fill=NAVY)
    s += text_elem(W/2, 145.5, ABSTRACT_NOTE, size=2, weight=400, fill=NAVY)

    # Aerial bottom third
    s += aerial_image(0, aerial_y, W, H - aerial_y, clip_id="bottomClip10")
    # Overlay band for website
    s += rect(0, H - 10, W, 10, NAVY, opacity=0.85)
    s += text_elem(W/2, H - 3.5, WEBSITE, size=3.5, weight=700, fill=GOLD)

    s += svg_footer()
    return s


# ─── Generate all variants ───────────────────────────────────────────

VARIANTS = [
    ("01_navy_gradient_aerial_strip", variant_01),
    ("02_navy_neural_network", variant_02),
    ("03_aerial_full_overlay", variant_03),
    ("04_split_aerial_top_white_bottom", variant_04),
    ("05_white_minimalist", variant_05),
    ("06_centered_circular_aerial", variant_06),
    ("07_bold_typographic_gold", variant_07),
    ("08_diagonal_slice_aerial", variant_08),
    ("09_dark_wave_coastal", variant_09),
    ("10_classic_academic_aerial", variant_10),
]


def generate_gallery():
    """Generate HTML gallery for side-by-side comparison."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CS2026 Flyer Variants — Comparison Gallery</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 2rem; }
h1 { text-align: center; font-size: 2rem; margin-bottom: .5rem; }
.subtitle { text-align: center; color: #888; margin-bottom: 2rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 2rem; max-width: 1600px; margin: 0 auto; }
.card { background: #16213e; border-radius: 12px; overflow: hidden; transition: transform .2s; }
.card:hover { transform: scale(1.02); }
.card img, .card object { width: 100%; height: auto; display: block; border-bottom: 2px solid #0f3460; }
.card .info { padding: 1rem; }
.card h3 { font-size: 1rem; margin: 0 0 .3rem; color: #e8a727; }
.card p { font-size: .85rem; color: #aaa; margin: 0; }
.specs { text-align: center; color: #666; font-size: .8rem; margin-top: 2rem; }
</style>
</head>
<body>
<h1>Consciousness Science 2026 — Flyer Variants</h1>
<p class="subtitle">JCS Journal Ad · 220 × 156 mm · 300 DPI · Click any card to open full SVG</p>
<div class="grid">
"""
    descriptions = [
        ("Navy Gradient + Aerial Strip", "Large logo, navy-to-teal gradient, aerial photo strip at bottom, editorial type"),
        ("Neural Network Pattern", "Large logo, pure navy, connectome dot grid background, teal pill themes"),
        ("Aerial Full Background", "Large logo, full aerial photo with dark gradient overlay, cinematic immersive"),
        ("Split: Aerial Top / White Bottom", "Small logo, aerial top half with overlay, clean white bottom half with theme cards"),
        ("White Minimalist", "Large logo, white background, navy/teal typography, light theme cards, computational clean"),
        ("Centered Circular Aerial", "Large logo, centered symmetrical layout, circular aerial inset, concentric ring decoration"),
        ("Bold Typographic + Gold", "Small logo, oversized broken CONSCIOUSNESS type, left-aligned editorial, gold accents"),
        ("Diagonal Slice + Aerial", "Large logo, diagonal geometric cut revealing aerial, dynamic angular energy"),
        ("Dark Wave / Coastal", "Large logo, dark navy with layered wave patterns, ocean-inspired coastal atmosphere"),
        ("Classic Academic + Aerial", "Small logo, traditional navy header band, white body with structured theme grid, aerial bottom"),
    ]
    for i, ((name, func), (title, desc)) in enumerate(zip(VARIANTS, descriptions)):
        html += f"""  <a href="variants/{name}.svg" target="_blank" style="text-decoration:none">
  <div class="card">
    <img src="variants/{name}.svg" alt="Variant {i+1}">
    <div class="info">
      <h3>#{i+1}: {title}</h3>
      <p>{desc}</p>
    </div>
  </div></a>
"""
    html += """</div>
<p class="specs">All variants: 220×156mm portrait · No bleed · 300 DPI compatible · SVG with embedded images</p>
</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Generating 10 flyer variants...")
    for name, func in VARIANTS:
        svg = func()
        out_path = OUT_DIR / f"{name}.svg"
        out_path.write_text(svg, encoding="utf-8")
        size_kb = out_path.stat().st_size / 1024
        print(f"  ✓ {name}.svg ({size_kb:.0f} KB)")

    # Generate gallery
    gallery = generate_gallery()
    gallery_path = FLYER_DIR / "gallery.html"
    gallery_path.write_text(gallery, encoding="utf-8")
    print(f"\n  ✓ gallery.html")
    print(f"\nOpen gallery.html in a browser to compare all variants.")
