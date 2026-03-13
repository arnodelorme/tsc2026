#!/usr/bin/env python3
"""Compile board packet PDFs into a single document with title pages and TOC."""

from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

PACKET_DIR = Path(__file__).parent
LOGO = PACKET_DIR.parent / "img" / "logo.png"
OUTPUT = PACKET_DIR / "Board_Packet_CS2026.pdf"

# Ordered sections: (filename, title for divider page)
SECTIONS = [
    ("TSC Discernment Process.pdf",            "Discernment Process"),
    ("FAQ.pdf",                                "FAQ"),
    ("budget_slide.pdf",                       "Budget Overview"),
    ("Contract assessment.pdf",                "Contract Assessment"),
    ("Memo_MOU_Consciousness Conveyance-dsl.pdf", "MOU: Consciousness Conveyance"),
    ("Conference_approval_ucsd.pdf",           "UCSD Conference Approval"),
    ("donations.pdf",                          "Donations & Pledges"),
    ("AZSpace_UA Foundation Report_Dec 2025.pdf", "Univ. Arizona Conference Funds"),
    ("Conference_website.pdf",                 "Conference Website"),
    ("disclosure_review.pdf",                  "Epstein Connection Review"),
    ("Vetting_Cyan_Banister.pdf",              "Vetting: Cyan Banister"),
    ("Vetting_Eugene_Jhong.pdf",               "Vetting: Eugene Jhong"),
]

# --- LaTeX-compiled additional pages (insert before vetting block) ---
# Add entries here as (pdf_path, title) to include LaTeX-generated pages.
# Example: ("extra/cover_letter.pdf", "Cover Letter")
EXTRA_PAGES = []


def make_cover_page():
    """Return a one-page PDF cover with centered logo and conference title."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter

    # Logo centered, ~150pt wide, preserving aspect ratio
    img_w = 150
    img_h = img_w * (397 / 346)  # original 346x397
    c.drawImage(str(LOGO), (w - img_w) / 2, h / 2 + 20,
                width=img_w, height=img_h, mask="auto")

    # Title lines below the logo
    y = h / 2 - 10
    c.setFillColorRGB(0.04, 0.14, 0.25)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w / 2, y, "Consciousness Science 2026")
    y -= 28
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.drawCentredString(w / 2, y, "International Interdisciplinary Conference")
    y -= 36
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(w / 2, y, "October 11\u201316, 2026 \u00b7 San Diego, California")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def _wrap_text(text, canvas_obj, font, size, max_width):
    """Split text into lines that fit within max_width."""
    canvas_obj.setFont(font, size)
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if canvas_obj.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def make_background_page():
    """Return a one-page PDF with the conference background summary."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    margin = 72
    text_width = w - 2 * margin
    y = h - margin

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.04, 0.14, 0.25)
    c.drawString(margin, y, "Background")
    y -= 32

    # Body paragraphs
    paragraphs = [
        "The Science of Consciousness is the largest and longest-running "
        "interdisciplinary conference on consciousness, since 1994.",

        "The Science of Consciousness conference organized at the University "
        "of Arizona has been an established international forum dedicated to "
        "interdisciplinary research on the nature and mechanisms of conscious "
        "experience and causal agency. Bringing together neuroscientists, "
        "clinicians, philosophers, physicists, computational researchers, and "
        "scholars from related fields, the meeting fosters rigorous scientific "
        "exchange across theoretical and empirical domains.",

        "The 32nd annual conference is shifting to San Diego under the auspices "
        "of UCSD and IONS and under a different name: Consciousness Science "
        "2026 (CS26).",

        "The 2026 meeting in San Diego will convene approximately 600 to 700 "
        "participants for five and a half days of workshops, plenary lectures, "
        "concurrent sessions, posters, exhibits, and interdisciplinary dialogue. "
        "In addition to its academic program, the conference includes carefully "
        "curated experiential and social events that have historically enriched "
        "scientific exchange and community building.",

        "The conference also aims to cultivate emerging scholars and foster "
        "cross-generational mentorship. The October conference builds on the "
        "previously developed scientific program within a strengthened "
        "administrative and governance structure designed to ensure long-term "
        "sustainability.",
    ]

    bullet_items = [
        "Sunday Oct 11 \u2013 Friday Oct 16 (five and 1/2 days)",
        "Interdisciplinary Workshops, Plenary Lectures, Concurrent talk "
        "sessions, Poster presentations and Exhibits",
        "Curated experiential and artistic events",
        "Social events and networking",
        "Accommodation is available on-site at the resort. Additional hotel "
        "information will be announced soon.",
    ]

    font, size, leading = "Helvetica", 11, 15
    c.setFont(font, size)
    c.setFillColorRGB(0.1, 0.1, 0.1)

    for para in paragraphs:
        lines = _wrap_text(para, c, font, size, text_width)
        for line in lines:
            c.drawString(margin, y, line)
            y -= leading
        y -= 6  # paragraph spacing

    # "The meeting will feature:" header
    y -= 4
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "The meeting will feature:")
    y -= leading + 2
    c.setFont(font, size)

    for item in bullet_items:
        lines = _wrap_text(item, c, font, size, text_width - 18)
        c.drawString(margin + 4, y + 1, "\u2022")
        for i, line in enumerate(lines):
            c.drawString(margin + 18, y, line)
            y -= leading
        y -= 2

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def make_page_number(page_num, total):
    """Return a single-page transparent PDF with a centered page number."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, _ = letter
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(w / 2, 28, f"{page_num}")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def make_title_page(title, subtitle="Consciousness Science 2026 — Board Packet"):
    """Return a one-page PDF (as bytes) with centered title text."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    # Light grey background band
    c.setFillColorRGB(0.94, 0.96, 0.98)
    c.rect(0, h / 2 - 60, w, 120, fill=True, stroke=False)
    # Title
    c.setFillColorRGB(0.04, 0.14, 0.25)  # navy
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w / 2, h / 2 + 10, title)
    # Subtitle
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(w / 2, h / 2 - 25, subtitle)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def make_toc_page(entries):
    """Return a one-page PDF with a table of contents.

    entries: list of (title, page_number)
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    y = h - 72
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.04, 0.14, 0.25)
    c.drawString(72, y, "Table of Contents")
    y -= 40
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.15, 0.15, 0.15)
    right_margin = w - 72
    dot_w = c.stringWidth(".", "Helvetica", 12)
    for title, page in entries:
        # Draw title left-aligned
        c.drawString(72, y, title)
        # Draw page number right-aligned
        page_str = str(page)
        c.drawRightString(right_margin, y, page_str)
        # Fill dots between title and page number
        title_end = 72 + c.stringWidth(title + "  ", "Helvetica", 12)
        page_start = right_margin - c.stringWidth("  " + page_str, "Helvetica", 12)
        x = title_end
        while x + dot_w <= page_start:
            c.drawString(x, y, ".")
            x += dot_w
        y -= 22
        if y < 72:
            c.showPage()
            y = h - 72
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def main():
    writer = PdfWriter()

    # Cover page (unnumbered conceptually, but page 1)
    cover_buf = make_cover_page()
    cover_reader = PdfReader(cover_buf)
    for p in cover_reader.pages:
        writer.add_page(p)

    # First pass: compute page numbers for TOC
    # Page 1 = cover, page 2 = TOC, page 3 = background, sections start at 4
    toc_entries = []
    page_cursor = 4
    all_sections = SECTIONS[:]
    for fname, title in all_sections:
        path = PACKET_DIR / fname
        if not path.exists():
            print(f"  SKIP (not found): {fname}")
            continue
        toc_entries.append((title, page_cursor))
        reader = PdfReader(str(path))
        page_cursor += 1 + len(reader.pages)  # +1 for divider

    # Build TOC page
    toc_buf = make_toc_page(toc_entries)
    toc_reader = PdfReader(toc_buf)
    for p in toc_reader.pages:
        writer.add_page(p)

    # Background page
    bg_buf = make_background_page()
    bg_reader = PdfReader(bg_buf)
    for p in bg_reader.pages:
        writer.add_page(p)

    # Second pass: append divider + content for each section
    for fname, title in all_sections:
        path = PACKET_DIR / fname
        if not path.exists():
            continue
        # Divider page
        div_buf = make_title_page(title)
        div_reader = PdfReader(div_buf)
        for p in div_reader.pages:
            writer.add_page(p)
        # Content pages
        reader = PdfReader(str(path))
        for p in reader.pages:
            writer.add_page(p)
        print(f"  Added: {title} ({len(reader.pages)} pages)")

    # Extra LaTeX-compiled pages (if any)
    for extra_path, extra_title in EXTRA_PAGES:
        ep = PACKET_DIR / extra_path
        if not ep.exists():
            print(f"  SKIP extra (not found): {extra_path}")
            continue
        div_buf = make_title_page(extra_title)
        div_reader = PdfReader(div_buf)
        for p in div_reader.pages:
            writer.add_page(p)
        reader = PdfReader(str(ep))
        for p in reader.pages:
            writer.add_page(p)
        print(f"  Added extra: {extra_title} ({len(reader.pages)} pages)")

    # Stamp page numbers on every page
    total = len(writer.pages)
    for i in range(total):
        num_buf = make_page_number(i + 1, total)
        num_reader = PdfReader(num_buf)
        writer.pages[i].merge_page(num_reader.pages[0])

    with open(OUTPUT, "wb") as f:
        writer.write(f)

    print(f"\nWrote {OUTPUT.name}: {total} pages")


if __name__ == "__main__":
    main()
