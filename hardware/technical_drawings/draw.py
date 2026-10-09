"""Generate an A3 drawing set from the existing V2 CAD and verified references.

No CAD edits or manufacturing-release claims. PDF and SVG share primitives.
Use collect_geometry.py with the existing CAD venv first, then run with a
Python runtime containing reportlab and Pillow.
"""
from pathlib import Path
import csv
import hashlib
import html
import json
import math
import textwrap

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/pdf/pocket_pet_technical"
DATA = json.loads((OUT / "geometry_reference.json").read_text(encoding="utf-8"))
for name, expected in DATA["sources"].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
PDF = OUT / "Pocket_Pet_V2_Technische_Zeichnungen.pdf"
INK, GRAY, WARN = "#20262b", "#70777a", "#a03d23"
REVISION = "A"
PAGE_COUNT = 8


class Sheet:
    width = 420
    height = 297

    def __init__(self, pdf, number, title, scale):
        self.pdf, self.number, self.title = pdf, number, title
        self.elements = []
        self.rect(8, 8, 404, 281, lw=.3)
        self.text(14, 18, "POCKET PET / ENTWICKLUNGSZEICHNUNG", 3.2, bold=True)
        self.text(14, 26, title, 4.4, bold=True)
        self.text(406, 18, f"PP-V2-Z{number:02d} / REV {REVISION}", 3.0, align="right")
        self.line(8, 32, 412, 32, lw=.3)
        self.line(8, 269, 412, 269, lw=.3)
        self.text(14, 277, "Maße in mm | Keine Allgemeintoleranz freigegeben | CAD-Sollmaße, sofern nicht anders bezeichnet", 2.6)
        self.text(14, 284, f"08.10.2026 | {scale} | A3 quer | Druck: tatsächliche Größe / 100 %", 2.6)
        self.text(406, 277, "ENTWURF - KEINE FERTIGUNGSFREIGABE", 2.7, align="right", color=WARN, bold=True)
        self.text(406, 284, f"OpenAI Codex | Blatt {number} / {PAGE_COUNT}", 2.6, align="right")

    def line(self, x1, y1, x2, y2, lw=.22, color=INK, dash=False):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(lw * mm)
        self.pdf.setDash([1.5 * mm, 1 * mm] if dash else [])
        self.pdf.line(x1 * mm, (self.height-y1) * mm, x2 * mm, (self.height-y2) * mm)
        d = ' stroke-dasharray="1.5 1"' if dash else ""
        self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{lw}"{d}/>')

    def rect(self, x, y, w, h, r=0, lw=.3, color=INK, fill=None):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(lw * mm)
        self.pdf.setDash([])
        if fill:
            self.pdf.setFillColor(fill)
        self.pdf.roundRect(x*mm, (self.height-y-h)*mm, w*mm, h*mm, r*mm, stroke=1, fill=int(bool(fill)))
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" stroke="{color}" stroke-width="{lw}" fill="{fill or "none"}"/>')

    def circle(self, x, y, r, lw=.25, color=INK, fill=None):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(lw * mm)
        self.pdf.setDash([])
        if fill:
            self.pdf.setFillColor(fill)
        self.pdf.circle(x*mm, (self.height-y)*mm, r*mm, stroke=1, fill=int(bool(fill)))
        self.elements.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{color}" stroke-width="{lw}" fill="{fill or "none"}"/>')

    def poly(self, points, lw=.22, color=INK):
        p = self.pdf.beginPath()
        for i, (x, y) in enumerate(points):
            (p.moveTo if i == 0 else p.lineTo)(x*mm, (self.height-y)*mm)
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(lw*mm)
        self.pdf.setDash([])
        self.pdf.drawPath(p)
        coords = " ".join(f"{x:.5f},{y:.5f}" for x, y in points)
        self.elements.append(f'<polyline points="{coords}" stroke="{color}" stroke-width="{lw}" fill="none"/>')

    def text(self, x, y, text, size=2.7, bold=False, align="left", color=INK, rotate=0):
        self.pdf.saveState()
        self.pdf.setFillColor(color)
        self.pdf.setFont("Arial-Bold" if bold else "Arial", size*mm)
        self.pdf.translate(x*mm, (self.height-y)*mm)
        self.pdf.rotate(-rotate)
        offset = {"left": 0, "center": .5, "right": 1}[align]
        width = pdfmetrics.stringWidth(text, "Arial-Bold" if bold else "Arial", size*mm)
        self.pdf.drawString(-width*offset, 0, text)
        self.pdf.restoreState()
        anchor = {"left": "start", "center": "middle", "right": "end"}[align]
        tr = f' transform="rotate({rotate},{x},{y})"' if rotate else ""
        self.elements.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}"{tr}>{html.escape(text)}</text>')

    def dimh(self, x1, x2, fromy, y, value):
        for x in (x1, x2):
            self.line(x, fromy, x, y+2 if y > fromy else y-2, lw=.15)
        self.line(x1, y, x2, y, lw=.16)
        for x, direction in ((x1, 1), (x2, -1)):
            self.poly([(x+direction*2, y-.65), (x, y), (x+direction*2, y+.65)], lw=.18)
        self.text((x1+x2)/2, y-1.8, value, 2.8, align="center")

    def dimv(self, y1, y2, fromx, x, value):
        for y in (y1, y2):
            self.line(fromx, y, x+2 if x > fromx else x-2, y, lw=.15)
        self.line(x, y1, x, y2, lw=.16)
        for y, direction in ((y1, 1), (y2, -1)):
            self.poly([(x-.65, y+direction*2), (x, y), (x+.65, y+direction*2)], lw=.18)
        self.text(x-2, (y1+y2)/2, value, 2.8, align="center", rotate=-90)

    def leader(self, x, y, tx, ty, label):
        self.poly([(x, y), (tx-3, ty-1), (tx, ty-1)], lw=.18)
        self.circle(x, y, .5, fill=INK)
        self.text(tx+1, ty, label, 2.7)

    def notes(self, x, y, width, title, entries, color=INK):
        self.text(x, y, title, 3.1, bold=True, color=color)
        yy = y+7
        for entry in entries:
            words, line = entry.split(), ""
            for word in words:
                candidate = f"{line} {word}".strip()
                if pdfmetrics.stringWidth(candidate, "Arial", 2.7) > width:
                    self.text(x, yy, line, 2.7, color=color)
                    yy += 4.5
                    line = word
                else:
                    line = candidate
            if line:
                self.text(x, yy, line, 2.7, color=color)
                yy += 6
        return yy

    def cad(self, name, x, y, scale=1, view="top"):
        paths = DATA["parts"][name][view]
        xs = [p[0] for path in paths for p in path]
        ys = [p[1] for path in paths for p in path]
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        for path in paths:
            self.poly([(x+(xx-xmin)*scale, y+(ymax-yy)*scale) for xx, yy in path], lw=.23)
        return (xmax-xmin)*scale, (ymax-ymin)*scale

    def table(self, x, y, columns, rows, rowheight=8, size=2.55):
        widths = [w for _, w in columns]
        self.rect(x, y, sum(widths), rowheight, fill="#eef0f0", lw=.2)
        for r, row in enumerate([[t for t, _ in columns]] + rows):
            xx = x
            yy = y + r*rowheight
            if r:
                self.line(x, yy+rowheight, x+sum(widths), yy+rowheight, lw=.12, color=GRAY)
            for value, w in zip(row, widths):
                assert pdfmetrics.stringWidth(str(value), "Arial-Bold" if r == 0 else "Arial", size) <= w-3, (value, w)
                self.text(xx+1.5, yy+rowheight*.65, str(value), size, bold=r == 0)
                xx += w
        return y + rowheight*(len(rows)+1)

    def finish(self):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}mm" height="{self.height}mm" viewBox="0 0 {self.width} {self.height}"><rect width="{self.width}" height="{self.height}" fill="white"/>' + "\n".join(self.elements) + '</svg>'
        (OUT / f"PP-V2-Z{self.number:02d}.svg").write_text(svg, encoding="utf-8")
        self.pdf.showPage()


def handheld(s, x, y, k=1):
    s.rect(x, y, 62*k, 90*k, 6*k, lw=.4)
    s.rect(x+15.4*k, y+20.1*k, 31.2*k, 41.4*k, lw=.25)
    for bx in (15, 31, 47):
        s.circle(x+bx*k, y+75*k, 4.75*k, lw=.3)


def overview(pdf):
    s = Sheet(pdf, 1, "Gesamtaufbau / herausnehmbarer Handheld und Pokéball", "M 1:1; Prinzipschnitt ohne Maßstab")
    s.text(34, 45, "HANDHELD / FRONT", 3.2, bold=True)
    handheld(s, 39, 67)
    s.dimh(39, 101, 67, 58, "62,0")
    s.dimv(67, 157, 39, 29, "90,0")
    s.text(39, 166, "Gehäuse: 31,4 tief", 2.8)
    s.text(39, 172, "Mit Tasten: 33,2 tief", 2.8)
    s.text(121, 45, "SEITE", 3.0, bold=True, align="center")
    s.rect(110, 67, 31.4, 90, lw=.35)
    s.line(126, 67, 126, 157, lw=.2)
    s.rect(108.2, 137.25, 1.8, 9.5, lw=.25)
    s.text(126, 165, "Prinzipsicht", 2.5, align="center")
    s.dimh(108.2, 141.4, 157, 184, "33,2")
    s.text(149, 45, "POKÉBALL / PRINZIP-FRONTANSICHT", 3.2, bold=True)
    # Flattened poles: nominal spherical envelope is 130 mm, height 118.6.
    xs = [65*math.cos(t) for t in [i*math.pi/180 for i in range(181)]]
    upper = [(220+x, 115-min(59, math.sqrt(max(0,65*65-x*x)))) for x in xs]
    lower = [(220+x, 115.6+min(59, math.sqrt(max(0,65*65-x*x)))) for x in reversed(xs)]
    s.poly(upper+lower+[upper[0]], lw=.4)
    s.line(155, 115, 285, 115, lw=.25)
    s.line(155, 115.6, 285, 115.6, lw=.25)
    s.circle(220, 115.3, 8.5, lw=.35)
    s.dimh(155, 285, 115, 185, "Ø130,0 Kugel-Sollmaß")
    s.dimv(56, 174.6, 285, 294, "118,6")
    s.leader(220, 115.3, 247, 141, "P12 Emblem Ø17 × 1,8")
    s.text(160, 197, "Mit Scharnier/Emblem: 130 × 142,55 × 118,6", 2.8)
    s.notes(310, 49, 88, "AUFBAU", [
        "P02 Deckel oben; P01 Unterschale unten.",
        "P03 offene Halterung im Ball. Handheld nach oben herausnehmen; 10-mm-Band vor Entnahme lösen.",
        "P04/P05 bilden das eigenständig nutzbare Handheld-Gehäuse.",
        "P06 Boardträger, P07-P09 Tasten, P10 Tastenträger und P11 Akkuhalter liegen im Handheld.",
        "Durch das Ball-Scharnier laufen keine Kabel. USB-Laden am entnommenen Handheld vorgesehen."
    ])
    s.notes(20, 216, 180, "ZEICHNUNGSSTATUS", [
        "Maßplan aus bestehendem V2-CAD, kein freigegebener Fertigungsdatensatz.",
        "P05 Rückschale aktuell fünf getrennte Volumen: Verbindung konstruktiv nacharbeiten.",
        "CAD-/Bewegungsprüfung V2 unvollständig; keine physische Passprüfung."
    ], color=WARN)
    s.notes(219, 216, 180, "DARSTELLUNG UND BEZÜGE", [
        "Orthogonale Einzelteilansichten aus tatsächlichen CAD-Kanten. Prinzipsichten sind ausdrücklich bezeichnet.",
        "X = Breite, Y = Länge, Z = Tiefe. Maße gelten bei 100 % Skalierung.",
        "H = Herstellerreferenz, C = CAD-Sollmaß, O = offen. Mengen in Blatt 7/8 jeweils für 1 und 2 Geräte."
    ])
    s.finish()


def case(pdf):
    s = Sheet(pdf, 2, "P04/P05 / Handheld-Gehäuse, Fenster und Befestigung", "M 1:1")
    s.text(32, 45, "P04 FRONT / AUSSENSEITE", 3.1, bold=True)
    s.cad("04_handheld_front", 43, 67)
    s.dimh(43, 105, 67, 57, "62,0")
    s.dimv(67, 157, 43, 30, "90,0")
    s.dimh(58.4, 89.6, 87.1, 80, "31,2")
    s.dimv(87.1, 128.5, 89.6, 116, "41,4")
    s.dimh(58, 74, 142, 176, "16,0")
    s.dimh(74, 90, 142, 176, "16,0")
    s.dimv(142, 157, 43, 21, "15,0")
    s.leader(90, 142, 115, 151, "3 × Ø10,0 Führung")
    s.text(39, 190, "Außenradius R6; Sichtplatte t = 2,4", 2.8)
    s.text(39, 196, "Fenster-Unterkante: 28,5 über Unterkante", 2.8)
    s.text(177, 45, "P05 RÜCKSCHALE / INNENANSICHT", 3.1, bold=True)
    s.cad("05_handheld_back", 185, 67)
    s.dimh(185, 247, 67, 57, "62,0")
    s.dimv(67, 157, 247, 257, "90,0")
    s.text(182, 178, "Innenraum: 57,2 × 85,2; Wand/Boden 2,4", 2.8)
    s.text(182, 185, "Führungsbund: 56,4 × 84,4; h 2,7; t 1,2", 2.8)
    s.text(182, 192, "0,4 nominales Spiel je Seite am Bund", 2.8)
    s.notes(280, 47, 117, "SCHRAUBEN UND KABEL", [
        "Gehäuse: 4 × M2×6 Senkkopf, vorläufig. Rückseite Ø2,3 Durchgang; Senkung Ø4,8, 1,25 tief. Front Ø1,6 Kernloch, 8 tief.",
        "Boardträger: 4 × Ø1,6 Kernloch in Front; Raster 46 × 52.",
        "Tastenträger: 2 × Ø1,6 Kernloch; Raster 50.",
        "USB-Korridor: 16 breit, 11 hoch; CAD-Ausschnitt 25 lang. Kein bündiger Panel-Port. Kabelgehäuse real prüfen.",
        "Alle Schraubenlängen und gedruckten Kernlöcher am Muster bestätigen."
    ])
    s.table(20, 215, [("Bezug: linke / untere Außenkante", 100), ("X-Koordinaten", 57), ("Y-Koordinaten", 57)], [
        ["Gehäuseverschraubung (4×)", "7,0 / 55,0", "4,0 / 86,0"],
        ["Boardträger (4×)", "8,0 / 54,0", "25,0 / 77,0"],
        ["Tastenträger (2×)", "6,0 / 56,0", "15,0"],
        ["Tastenachsen (3×)", "15,0 / 31,0 / 47,0", "15,0"],
    ], rowheight=8)
    s.notes(255, 224, 140, "OFFENER CAD-BEFUND P05", [
        "Rückschale hat fünf getrennte Körper. Der Führungsbund bzw. Anschlussbereiche sind noch nicht durchgängig verbunden.",
        "Gezeigte Maße dokumentieren den Ist-Entwurf; vor Druck CAD reparieren und gesamte Baugruppe prüfen."
    ], color=WARN)
    s.finish()


def board(pdf):
    s = Sheet(pdf, 3, "E01/P06 / ESP32-Displaymodul und Boardträger", "M 2:1")
    x, y, k = 35, 70, 2
    s.text(25, 45, "E01 WAVESHARE / MECHANISCHE REFERENZ H", 3.1, bold=True)
    s.rect(x, y, 35.01*k, 48.21*k, 2*k)
    s.rect(x+2.205*k, y+1.8*k, 30.6*k, 40.8*k, lw=.2)
    for hx in (3, 32):
        for hy in (3, 45.2):
            s.circle(x+hx*k, y+hy*k, 1*k)
    s.dimh(x, x+70.02, y, 57, "35,01")
    s.dimv(y, y+96.42, x, 22, "48,21")
    s.dimh(x+6, x+64, y+6, 183, "29,00 Schraubraster")
    s.dimv(y+6, y+90.4, x+64, 118, "42,20 Schraubraster")
    s.text(29, 198, "4 × M2, vorhandene Aufnahmen H2,5", 2.8)
    s.text(29, 205, "Aktive Anzeige: 30,60 × 40,80", 2.8)
    s.text(29, 212, "Fenster im Gehäuse: 31,20 × 41,40", 2.8)
    s.text(168, 45, "P06 BOARDTRÄGER / DRAUFSICHT C", 3.1, bold=True)
    s.cad("06_board_carrier", 172, 70, 2)
    s.dimh(172, 278, 70, 57, "53,0")
    s.dimv(70, 182, 278, 291, "56,0")
    s.dimh(184, 266, 100, 195, "41,0 Durchbruch")
    s.text(168, 214, "Platte t 2,0; Eckradius R2; Durchbruch 41 × 49", 2.8)
    s.text(168, 221, "Modul: Ø2,3 Durchgänge im 29,0 × 42,2 Raster", 2.8)
    s.text(168, 228, "Träger: Ø2,5 Durchgänge im 46,0 × 52,0 Raster", 2.8)
    s.notes(310, 49, 89, "EINBAU", [
        "Herstellerzeichnung ESP32-S3-LCD-2-20250122. Mechanische Revision am gekauften Board abgleichen.",
        "Zeichnungs-Bauhöhe 8,20 ohne lange Stiftleisten. Vollständiges STEP inklusive Pins: 14,00 tief.",
        "STEP-Hülle: ca. 35,02 × 49,40 × 14,00; Anschlüsse können über Platinenkontur hinausragen.",
        "4 × M2×4 Modul an Träger; 4 × M2×5 Träger an Front. Nicht gegen Display/Flexkabel einschrauben.",
        "USB zeigt zur oberen Handheld-Kante. Displayrotation später in Firmware festlegen."
    ])
    s.text(22, 250, "Quelle H: Waveshare 2D/3D-Datei 20250122; keine separate Display-/ESP32-Platine notwendig.", 2.8)
    s.finish()


def controls(pdf):
    s = Sheet(pdf, 4, "P07-P10/E02-E03 / drei Tasten und Tasterplatine", "M 3:1 Details; P10 M 2:1")
    s.text(20, 45, "P07/P08/P09 / GLEICHER GRUNDKÖRPER", 3.1, bold=True)
    # Actual section, local origin at the actuator bottom.
    cx, yy, k = 59, 79, 5
    s.rect(cx-4.75*k, yy, 9.5*k, 4.2*k)
    s.rect(cx-5.6*k, yy+4.2*k, 11.2*k, 1.2*k)
    s.rect(cx-1.7*k, yy+5.4*k, 3.4*k, 1.7*k)
    s.line(cx, yy-7, cx, yy+43, lw=.13, dash=True)
    s.dimh(cx-4.75*k, cx+4.75*k, yy, yy-10, "Ø9,5 Kopf")
    s.dimh(cx-5.6*k, cx+5.6*k, yy+27, yy+47, "Ø11,2 Flansch")
    s.dimv(yy, yy+35.5, cx+28, cx+42, "7,1 gesamt")
    s.text(21, 139, "Schnittprinzip / M 5:1", 2.6)
    s.notes(20, 152, 116, "TASTENMASSE C", [
        "Kopf Ø9,5 × 4,2; Flansch Ø11,2 × 1,2; Stößel Ø3,4 × 1,7.",
        "Führung Ø10,0: 0,25 radiales Sollspiel. Flansch hält Taste im Gehäuse.",
        "OK: Vertiefung Ø3,0 × 0,3 effektiv. Seitentasten: Nut 3,5 × 0,8 × 0,3 effektiv.",
        "Nominaler Abstand Stößel/Schalter 0,2; digitale Hubprüfung aus V1: bis 0,6. Reale Rückstellung prüfen."
    ])
    s.text(156, 45, "E03 FR4 / 3 × E02 TASTER", 3.1, bold=True)
    x, y, k = 163, 77, 3
    s.rect(x, y, 43*k, 12*k)
    for bx in (5.5, 21.5, 37.5):
        s.rect(x+(bx-3)*k, y+3*k, 6*k, 6*k, lw=.2)
        for dx in (-3.25, 3.25):
            for dy in (-2.25, 2.25):
                s.circle(x+(bx+dx)*k, y+(6+dy)*k, .5*k, lw=.2)
        s.circle(x+bx*k, y+6*k, 1.75*k, lw=.2)
    s.dimh(x, x+129, y, 63, "43,0")
    s.dimv(y, y+36, x+129, 304, "12,0")
    s.dimh(x+16.5, x+64.5, y+18, 130, "16,0")
    s.dimh(x+64.5, x+112.5, y+18, 130, "16,0")
    s.text(163, 145, "FR4 t = 1,6; 12 × Ø1,0 ±0,1 nach Omron", 2.8)
    s.text(163, 152, "Je Taster: Bohrungsraster 6,5 ±0,1 × 4,5 ±0,1", 2.8)
    s.text(163, 159, "Achsen ab linker/unterer Kante: X 5,5 / 21,5 / 37,5; Y 6,0", 2.8)
    s.text(159, 177, "P10 TASTENTRÄGER / M 2:1", 3.1, bold=True)
    s.cad("10_switch_tray", 170, 191, 2)
    s.dimh(170, 282, 191, 183, "56,0")
    s.dimv(191, 221, 282, 298, "15,0")
    s.text(163, 234, "Hülle 56 × 15 × 3,5; Grundplatte 2,0; Ø2,5, Raster 50", 2.8)
    s.text(163, 242, "Freier Lötbereich 41 × 10; PCB-Aufnahme ca. 43,4 × 12,4", 2.8)
    s.notes(324, 50, 73, "TASTERKANDIDAT H", [
        "Omron B3F-1000: Gehäuse 6 ±0,2 × 6 ±0,2; Betätigungshöhe 4,3 ±0,2 über PCB.",
        "Keine beliebigen 6×6-Taster einsetzen: abweichende Höhe verändert den Stößel.",
        "2,54-mm-Lochraster entspricht nicht dem gezeichneten Bohrbild.",
        "Leitungen zur ESP32-Platine. GPIOs erst nach Schaltplanprüfung festlegen."
    ])
    s.finish()


def trays(pdf):
    s = Sheet(pdf, 5, "P03/P11 / offene Ballhalterung und Akkuaufnahme", "M 1:1; Akkuhalter M 2:1")
    s.text(23, 45, "P03 OFFENE HALTERUNG / DRAUFSICHT", 3.1, bold=True)
    s.cad("03_removable_cradle", 38, 69)
    s.dimh(38, 106.8, 69, 58, "68,8")
    s.dimv(69, 165.8, 106.8, 118, "96,8")
    s.dimh(40.4, 104.4, 98, 179, "64,0 lichte Breite")
    s.text(21, 195, "62,0 Handheld + 1,0 Spiel je Seite", 2.8)
    s.text(21, 202, "Hülle h 17,0; Basis 3,0; Seitenwand 2,4", 2.8)
    s.text(21, 209, "4 × Ø3,3; Senkung Ø6,7 × 1,7; Raster 48 × 40", 2.8)
    s.text(21, 216, "Bandfenster 11,0 × 2,2 für 10-mm-Textilband", 2.8)
    s.text(157, 45, "P11 AKKUHALTER / DRAUFSICHT", 3.1, bold=True)
    s.cad("11_battery_tray", 173, 69, 2)
    s.dimh(173, 283, 69, 57, "55,0 inkl. Laschen")
    s.dimv(69, 207, 283, 295, "69,0")
    s.dimh(186, 270, 190, 222, "42,0 Körperbreite")
    s.text(165, 235, "Innenkontur 38 × 65, R3; Außenkontur 42 × 69, R5", 2.8)
    s.text(165, 242, "Boden 2; Wand 2; Hülle 7; 2 × Ø3,2, Raster 47", 2.8)
    s.text(165, 249, "Bandschlitze 2 × 12, Abstand 37; Kabelöffnung 12 × 7", 2.8)
    s.notes(316, 48, 82, "AKKU / OFFENE AUSWAHL O", [
        "Planungs-Hülle der Zelle: maximal 36 × 63 × 5,2. Dies ist ein Maßbeispiel, keine ausgewählte Zelle.",
        "1S, 3,7 V, geschützt. Schutzplatine, Kabel und Stecker zusätzlich berücksichtigen.",
        "Waveshare: MX1.25-Akkuanschluss. Polarität am realen Board prüfen. Beispielakku Adafruit 258 hat JST-PH und passt nicht direkt.",
        "Akkuhalter am Handheld: vorläufig 2 × M3×6. Das V1-Maß M3×8 wäre an der flachen V2-Rückwand zu lang.",
        "Halter nicht zur Klemmung der Zelle verwenden. Weiches Band; kein Druck auf Folie oder Lötstellen."
    ])
    s.finish()


def ball(pdf):
    s = Sheet(pdf, 6, "P01/P02/P12-P15 / Pokéball, Scharnier und Passproben", "Schalen M 1:1; Details wie bezeichnet")
    s.text(18, 44, "P01 UNTERSCHALE / INNENANSICHT", 3.0, bold=True)
    s.cad("01_ball_lower", 21, 62)
    s.dimh(21, 151, 112, 54, "130,0")
    s.text(178, 44, "P02 DECKEL / INNENANSICHT", 3.0, bold=True)
    s.cad("02_ball_lid", 177, 62, view="bottom")
    s.dimh(177, 307, 112, 54, "130,0")
    s.text(18, 218, "Kugel R65 außen / R62,6 innen; Wand/Boden 2,4", 2.8)
    s.text(18, 225, "Pole bei Z = -59,0 und +59,6; Hälftenspalt 0,6", 2.8)
    s.text(18, 232, "Halterungsdome: Ø8; 4 × Ø2,5, 10 tief; Raster 48 × 40", 2.8)
    s.text(18, 239, "Verschluss: unten Ø2,6; oben Ø3,4; Kopffreiraum Ø6,4", 2.8)
    s.text(18, 246, "Verschlussachse: X 0, Y -66; Scharnier: Y 67, Z 0,3", 2.8)
    s.notes(322, 46, 77, "SCHARNIER / DETAIL C", [
        "Außen Ø8,4; Achsbohrung Ø3,4 für M3.",
        "Knöchel entlang X: 10,8 + 0,4 Spalt + 13,6 + 0,4 Spalt + 10,8 = 36,0.",
        "M3×45 Achsschraube, 2 Scheiben, 1 Mutter. Beweglichkeit real einstellen.",
        "Emblem P12 Ø17 × 1,8. Nur am Deckelsteg verkleben. Keine funktionale Verschlussrastung.",
        "Öffnungswinkel V2 nicht freigegeben; V1-Bewegungswerte sind nicht übertragbar."
    ])
    s.table(178, 215, [("Optionaler Prüfkörper", 58), ("Hülle / Detail", 66)], [
        ["P13 Tastenpassprobe", "46 × 19 × 2,4"],
        ["Führungen P13", "Ø9,8 / Ø10,0 / Ø10,2"],
        ["P14 Scharnierprobe", "16 × 12 × 10,7; Ø3,4"],
        ["P15 Halterungsprobe", "68,8 × 12 × 11,4; licht 64"],
    ], rowheight=8)
    s.finish()


PRINTED = [
    ("P01", "Ball-Unterschale", "01_ball_lower", "1", "2"),
    ("P02", "Ball-Deckel", "02_ball_lid", "1", "2"),
    ("P03", "Offene Handheld-Halterung", "03_removable_cradle", "1", "2"),
    ("P04", "Handheld-Frontschale", "04_handheld_front", "1", "2"),
    ("P05", "Handheld-Rückschale", "05_handheld_back", "1", "2"),
    ("P06", "Boardträger", "06_board_carrier", "1", "2"),
    ("P07", "Taste links", "07_button_left", "1", "2"),
    ("P08", "Taste OK", "08_button_ok", "1", "2"),
    ("P09", "Taste rechts", "09_button_right", "1", "2"),
    ("P10", "Tastenträger", "10_switch_tray", "1", "2"),
    ("P11", "Akkuhalter", "11_battery_tray", "1", "2"),
    ("P12", "Ball-Emblem", "12_ball_emblem", "1", "2"),
    ("P13", "Tastenpassprobe (optional)", "13_button_fit_coupon", "1", "1*"),
    ("P14", "Scharnierprobe (optional)", "14_hinge_fit_coupon", "1", "1*"),
    ("P15", "Halterungsprobe (optional)", "15_cradle_fit_coupon", "1", "1*"),
]
FASTENERS = [
    ["M01", "M2×4, Modul an Boardträger", "4", "8"],
    ["M02", "M2×5, Boardträger an Front", "4", "8"],
    ["M03", "M2×6, Tastenträger an Front", "2", "4"],
    ["M04", "M2×6 Senkkopf, Handheld", "4", "8"],
    ["M05", "M3×6, Akkuhalter an Rückschale", "2", "4"],
    ["M06", "M3×8 Senkkopf, Halterung im Ball", "4", "8"],
    ["M07", "M3×45, Scharnierachse", "1", "2"],
    ["M08", "M3×10, Ball-Verschluss", "1", "2"],
    ["M09", "M3-Mutter, Scharnier", "1", "2"],
    ["M10", "M3-Scheibe, Achse (ca. Ø7)", "2", "4"],
    ["M11", "Weiches Band, 10 mm breit", "2", "4"],
    ["M12", "Klebstoff für Emblem", "n. B.", "n. B."],
]


def bom_mechanical(pdf):
    s = Sheet(pdf, 7, "Stückliste / Druckteile, Schrauben und Montagebedarf", "Tabellen; Hüllmaße X × Y × Z")
    rows = []
    for pos, title, key, one, two in PRINTED:
        p = DATA["parts"][key]
        size = " × ".join(f"{v:.2f}".replace(".", ",") for v in p["size"])
        if key == "12_ball_emblem":
            size = "Ø17 × 1,8"
        rows.append([pos, title, one, two, size, "5 Körper / OFFEN" if pos == "P05" else "CAD-Sollmaß"])
    s.table(16, 43, [("Pos.", 12), ("3D-Druckteil", 64), ("1 Ger.", 14), ("2 Ger.", 14), ("Hüllmaß / mm", 63), ("Status", 39)], rows, rowheight=9, size=2.5)
    s.text(16, 197, "* Passproben einmal je Drucker/Material. 12 Bauteile pro Gerät, 24 für beide Geräte.", 2.7)
    s.notes(16, 212, 188, "MONTAGE UND TOLERANZEN", [
        "Schrauben vorläufig anhand der Schichtfolge. M2-Längen am Board strikt prüfen. Gedruckte Kernlöcher sind keine modellierten Gewinde.",
        "Sollspiele sind Konstruktionswerte, keine garantierten Drucktoleranzen. Erst Passproben, dann Einzelteilpassung und komplette Montage prüfen.",
        "V2 darf trotz teilweise vorhandener STL nicht als vollständig validierter Drucksatz behandelt werden."
    ])
    s.table(236, 43, [("Pos.", 12), ("Zusatzteil / Richtmaß", 119), ("1", 12), ("2", 12)], FASTENERS, rowheight=11, size=2.55)
    s.notes(238, 204, 159, "BESCHAFFUNGSDETAILS", [
        "M05 bewusst M3×6: 2 mm Halterboden + 4 mm Einschraubweg. Bei 8 mm droht Durchstoß der V2-Rückwand.",
        "Bandlänge am montierten Aufbau bestimmen; einmal für Akku, einmal zur Handheld-Sicherung im Ball.",
        "Keine Gewindeeinsätze im vorhandenen CAD. Eine Änderung darauf benötigt angepasste Dome."
    ])
    s.finish()


ELECTRONICS = [
    ["E01", "Waveshare ESP32-S3-LCD-2", "1", "2", "35,01 × 48,21; STEP-Tiefe 14", "H / Revision prüfen"],
    ["E02", "Omron B3F-1000, Kandidat", "3", "6", "6 × 6; Betätigungshöhe 4,3", "H / vorläufig"],
    ["E03", "FR4-Tasterplatine, gebohrt", "1", "2", "43 × 12 × 1,6", "C / selbst erstellen"],
    ["E04", "Geschützter 1S-LiPo, 3,7 V", "1", "2", "Maßhülle 36 × 63 × 5,2", "O / keine Zellwahl"],
    ["E05", "Akkuanschluss / Kabel", "1 Satz", "2 Sätze", "MX1.25 boardseitig; Länge offen", "O / Polarität prüfen"],
    ["E06", "Tasterleitungen, flexibel", "1 Satz", "2 Sätze", "3 Signale + gemeinsamer GND", "O / Länge offen"],
    ["E07", "USB-C-Kabel, Laden/Flashen", "1", "1-2", "Steckerhülle am Ausschnitt prüfen", "O / extern"],
    ["E08", "Mini-Lautsprecher, Audioausbau", "1", "2", "Durchmesser/Tiefe noch offen", "O / Halter fehlt"],
    ["E09", "Audioverstärker, Audioausbau", "1", "2", "Modul-/Versorgungswahl offen", "O / Halter fehlt"],
    ["E10", "Power-Schalter, optional", "0-1", "0-2", "Bauform/Position offen", "O / kein Ausschnitt"],
]


def electronics(pdf):
    s = Sheet(pdf, 8, "Elektronik-Stückliste / Quellen und offene Freigabepunkte", "Tabellen; H Hersteller, C CAD, O offen")
    s.table(16, 43, [("Pos.", 12), ("Elektronik / Zubehör", 86), ("1 Gerät", 21), ("2 Geräte", 21), ("Maß / Anschluss", 123), ("Stand", 122)], ELECTRONICS, rowheight=11, size=2.55)
    s.notes(18, 176, 178, "VOR BESCHAFFUNG / FREIGABE", [
        "Akku konkret wählen: Zellhülle einschließlich Schutzplatine, Leitungen, Stecker, Polarität und zulässige Ladung abgleichen.",
        "Audio ist Nutzerwunsch, aber noch nicht mechanisch integriert. Keine erfundenen Lautsprecher-/Modulmaße; Ausschnitte/Halter erst nach Auswahl.",
        "P05 verbinden, alle 15 CAD-Teile/Exporte und Montage-, Deckel- sowie Entnahmekollisionen vollständig neu prüfen. Danach Passdruck und realer Aufbau."
    ], color=WARN)
    s.notes(222, 177, 176, "QUELLEN / STAND 08.10.2026", [
        "C: hardware/pokeball_v2/build.py; wiederverwendete Innenteile aus hardware/pokeball_v1/build.py. Quellhashes im Begleitbericht.",
        "H: Waveshare, ESP32-S3-LCD-2-20250122.pdf / .stp; docs.waveshare.com/ESP32-S3-LCD-2",
        "H: Omron B3F-Datenblatt, 6-mm-Standard-Flachtaster; omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf",
        "O: Adafruit 258 nur als bisheriges Größenbeispiel; Akku-Maximalhülle aus 503562-1200mAh-Datenblatt. Kein finaler Kaufvorschlag."
    ])
    s.finish()


def main():
    pdf = canvas.Canvas(str(PDF), pagesize=(420*mm, 297*mm))
    pdf.setTitle("Pocket Pet V2 - Technische Zeichnungen und Stückliste")
    pdf.setAuthor("OpenAI Codex / HNam05")
    for function in (overview, case, board, controls, trays, ball, bom_mechanical, electronics):
        function(pdf)
    pdf.save()
    with (OUT / "Stueckliste_2_Geraete.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Position", "Bauteil", "Menge_1_Geraet", "Menge_2_Geraete", "Masse_oder_Anschluss", "Status"])
        for pos, title, key, one, two in PRINTED:
            size = " x ".join(f"{v:.2f}" for v in DATA["parts"][key]["size"])
            w.writerow([pos, title, one, two, size, "5 getrennte Koerper; CAD-Korrektur offen" if pos == "P05" else "CAD-Sollmass; V2 nicht freigegeben"])
        for row in FASTENERS:
            w.writerow(row + ["siehe Bezeichnung", "vorlaeufig; real pruefen"])
        w.writerows(ELECTRONICS)
    status = {"drawing_revision": "A", "date": "2026-10-08", "pages": 8,
              "release": "development_dimension_plan_only", "source_hashes": DATA["sources"],
              "handheld_case_mm": [62, 90, 31.4], "handheld_with_buttons_mm": [62, 90, 33.2],
              "ball_closed_envelope_mm": [130, 142.55, 118.6],
              "back_shell_solids": DATA["parts"]["05_handheld_back"]["solids"],
              "open_components": ["battery", "speaker", "audio_amplifier", "optional_power_switch"],
              "physical_validation": False}
    (OUT / "drawing_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(PDF)


if __name__ == "__main__":
    main()
