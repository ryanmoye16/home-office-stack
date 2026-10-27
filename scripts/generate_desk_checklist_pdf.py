#!/usr/bin/env python3
"""Generate the HOS desk-setup checklist lead-magnet PDF (P1 #11).

Source of content: work-tools/ergonomic-desk-setup.html (the four layers,
OSHA workstation targets as published there). Compliance: the PDF contains
NO affiliate/Amazon links — every link points to a homeofficestack.com page
(Associates Operating Agreement section 4: no Special Links in PDFs/email).
No prices, ratings, review counts, or ASINs appear anywhere in the PDF.

Run:  python3 scripts/generate_desk_checklist_pdf.py
Out:  downloads/desk-setup-checklist.pdf
Requires: reportlab (use a disposable venv if the system python lacks it).
"""
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads", "desk-setup-checklist.pdf")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DVS", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-I", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))

INK = HexColor("#17171f")
MUTE = HexColor("#4a4a55")
ACCENT = HexColor("#7c3aed")
ACCENT_SOFT = HexColor("#f1eafd")
RULE = HexColor("#d8d8e0")
WARM = HexColor("#fff7ea")

S = {
    "kicker": ParagraphStyle("kicker", fontName="DVS-B", fontSize=8.5, leading=11,
                             textColor=ACCENT, spaceAfter=4),
    "title": ParagraphStyle("title", fontName="DVS-B", fontSize=23, leading=27,
                            textColor=INK, spaceAfter=6),
    "intro": ParagraphStyle("intro", fontName="DVS", fontSize=10.5, leading=15,
                            textColor=MUTE, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="DVS-B", fontSize=13.5, leading=17,
                         textColor=INK, spaceBefore=9, spaceAfter=3),
    "layer_note": ParagraphStyle("ln", fontName="DVS-I", fontSize=9.5, leading=13,
                                 textColor=MUTE, spaceAfter=5),
    "item": ParagraphStyle("item", fontName="DVS", fontSize=10.5, leading=14,
                           textColor=INK, leftIndent=2, spaceAfter=4),
    "box_h": ParagraphStyle("boxh", fontName="DVS-B", fontSize=11, leading=14,
                            textColor=INK, spaceAfter=4),
    "box": ParagraphStyle("box", fontName="DVS", fontSize=10, leading=13.5,
                          textColor=INK, spaceAfter=3),
    "link": ParagraphStyle("link", fontName="DVS", fontSize=10, leading=13.5,
                           textColor=INK, spaceAfter=2),
    "foot": ParagraphStyle("foot", fontName="DVS", fontSize=8, leading=11,
                           textColor=MUTE),
}


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.7)
    canvas.line(0.75 * inch, 10.45 * inch, 7.75 * inch, 10.45 * inch)
    canvas.setFont("DVS-B", 8.5)
    canvas.setFillColor(ACCENT)
    canvas.drawString(0.75 * inch, 10.58 * inch, "HOME OFFICE STACK")
    canvas.setFont("DVS", 8.5)
    canvas.setFillColor(MUTE)
    canvas.drawRightString(7.75 * inch, 10.58 * inch, "homeofficestack.com")
    canvas.setFont("DVS", 8)
    canvas.drawString(0.75 * inch, 0.55 * inch,
                      "Research-based, not hands-on: grounded in manufacturer specs and published owner feedback.")
    canvas.drawRightString(7.75 * inch, 0.55 * inch, f"Page {doc.page} of 2")
    canvas.restoreState()


def layer(num, title, note, items):
    out = [Paragraph(f"Layer {num} — {title}", S["h2"]),
           Paragraph(note, S["layer_note"])]
    for it in items:
        out.append(Paragraph(f"☐&nbsp;&nbsp;{it}", S["item"]))
    return out


def boxed(title, rows, bg):
    inner = [Paragraph(title, S["box_h"])] + [Paragraph(r, S["box"]) for r in rows]
    t = Table([[inner]], colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def build():
    doc = BaseDocTemplate(OUT, pagesize=LETTER,
                          leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                          topMargin=0.85 * inch, bottomMargin=0.75 * inch,
                          title="Desk Setup Checklist: The 4 Layers — Home Office Stack",
                          author="Home Office Stack")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=header_footer)])

    story = []
    story.append(Paragraph("FREE PRINTABLE CHECKLIST", S["kicker"]))
    story.append(Paragraph("Desk Setup Checklist: The 4 Layers", S["title"]))
    story.append(Paragraph(
        "Most desk setups get fixed in the wrong order — an accessory here, a cushion there — "
        "while the screen, the thing that sets your neck and shoulders for eight hours, stays "
        "exactly where it was. Work this checklist in order: <b>screen, surface, feet, light.</b> "
        "Tick a box only when it is true at the end of a full workday, not after five minutes. "
        "Skip any layer that does not apply to you — that is the checklist working, not failing.",
        S["intro"]))
    story.append(boxed("Measure first (write your numbers down)", [
        "☐&nbsp;&nbsp;Sitting eye height vs. the top of your screen: the target is top of screen at or just below eye level.",
        "☐&nbsp;&nbsp;Viewing distance, eyes to screen: __________ inches (target: 20–40 inches).",
        "☐&nbsp;&nbsp;Elbow height vs. your keyboard: the target is keyboard at or just below elbow height, shoulders relaxed.",
    ], ACCENT_SOFT))
    story.append(Spacer(1, 6))

    story += layer(1, "Screen (the only layer every desk needs)",
                   "Screen height drives neck and shoulder position all day, so this layer comes first — and it is two heights, not one.",
                   [
                       "Top of the screen sits at or just below eye level.",
                       "Screen sits 20–40 inches from my eyes — set deliberately, not wherever the desk happens to end.",
                       "Keyboard sits at or just below elbow height, with shoulders relaxed.",
                       "Laptop route: the laptop is raised on a stand AND an external keyboard and mouse sit on the desk — a raised laptop typed on directly just moves the strain.",
                       "Monitor route: I checked the panel's weight without its stand against the arm's stated range, with headroom under the ceiling — and the VESA pattern matches.",
                   ])
    story += layer(2, "Surface",
                   "A desk mat does not fix posture. What it fixes is drift — it keeps the positions Layer 1 set staying set.",
                   [
                       "One consistent surface runs under both keyboard and mouse — no crossing from mat to bare desk mid-task.",
                       "The mat stays planted (non-slip base) and the keyboard does not creep during a workday.",
                       "No desk edge digs into a wrist or forearm.",
                       "The mat fits the desk's depth without overhang — on a small desk, depth is the fit that fails first.",
                   ])
    story.append(PageBreak())

    story += layer(3, "Feet (only if you stand)",
                   "This layer is conditional, and the condition is standing. Seated all day? Skip it entirely and spend nothing here.",
                   [
                       "I stand for part of the day — if not, this whole layer is ticked by skipping it.",
                       "There is support underfoot, not a bare hard floor.",
                       "The surface gives my feet reasons to shift — micro-movement, a raised-foot position, a calf stretch — not just cushion.",
                       "If the mat is a compact size, I checked the maker's own sizing guidance against my height and stance before relying on it.",
                   ])
    story += layer(4, "Light",
                   "The last layer fixes a different kind of strain: squinting. It fixes the desk, not your posture.",
                   [
                       "Light lands on the desk, keyboard, and papers — not reflected off the screen.",
                       "No main light source sits directly behind the screen glaring past it.",
                       "I can read paper at the desk without squinting or leaning in.",
                       "The desk stays evenly lit as the room's light changes from morning to evening — re-check at both ends of the day.",
                   ])
    story.append(Paragraph("The foundation under all four layers", S["h2"]))
    story.append(Paragraph(
        "☐&nbsp;&nbsp;My chair lets my elbows sit near desk height. Chair and desk height are the "
        "foundation these layers sit on — no layer above compensates for a chair that puts your "
        "elbows far from the desk.", S["item"]))
    story.append(Spacer(1, 4))
    story.append(boxed("When to stop", [
        "☐&nbsp;&nbsp;<b>Stop buying when the targets are met:</b> screen at eye level, keyboard at elbow height, surface planted, feet supported if you stand, desk lit without glare. Anything past that is decoration, not ergonomics.",
        "☐&nbsp;&nbsp;<b>Pain rule:</b> if pain persists once the heights are genuinely right — or is sharp, new, or worsening — the next step is a medical professional, not a fifth layer in a shopping cart.",
    ], WARM))
    story.append(Paragraph("Go deeper, layer by layer (site pages only)", S["h2"]))
    for label, url in [
        ("The full guide this checklist condenses — Ergonomic Desk Setup:",
         "homeofficestack.com/work-tools/ergonomic-desk-setup.html"),
        ("Layer 1 in depth — Best Laptop Stand for Posture:",
         "homeofficestack.com/work-tools/best-laptop-stand-for-posture.html"),
        ("Layer 1 fit test — Monitor Arm Compatibility Checker:",
         "homeofficestack.com/work-tools/monitor-arm-checker.html"),
        ("Stand or arm? — Laptop Stand vs Monitor Arm:",
         "homeofficestack.com/work-tools/laptop-stand-vs-monitor-arm.html"),
        ("How we research every pick — How We Research:",
         "homeofficestack.com/how-we-research.html"),
    ]:
        story.append(Paragraph(f"{label}<br/><link href=\"https://{url}\" color=\"#7c3aed\">{url}</link>", S["link"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "This PDF contains no affiliate links, by design — affiliate links never belong in a PDF or an email. "
        "The site pages linked above carry their own affiliate disclosure. Home Office Stack reviews are "
        "research-based, grounded in manufacturer specs and published owner feedback; no sponsored "
        "placements. October 2026 edition.", S["foot"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
