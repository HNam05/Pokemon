"""One A1 master sheet: genuine CAD isometrics, dimensions and installation.

Sources and older revisions are preserved. Simplified electronics are clearly
labelled envelopes. No manufacturing certification is implied.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import math
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw as d

OUT = d.ROOT / 'output/pdf/pocket_pet_technical_rev_c'
DATA = json.loads((OUT/'isometric_geometry.json').read_text(encoding='utf-8'))
PDF = OUT/'Pocket_Pet_V2_RevC_Isometrische_Gesamtzeichnung.pdf'
SVG = PDF.with_suffix('.svg')
for name, expected in DATA['sources'].items():
    assert hashlib.sha256((d.ROOT/name).read_bytes()).hexdigest() == expected, name


class MasterSheet(d.Sheet):
    width, height = 841, 594

    def __init__(self, pdf):
        self.pdf, self.elements = pdf, []
        self.text_boxes = []
        self.rect(8, 8, 825, 578, lw=.35)
        self.text(14, 20, 'POCKET PET / V2 / REVISION C', 3.6, bold=True)
        self.text(14, 32, 'Isometrische Gesamtzeichnung: Gehäuse, Elektronik und Montage', 6.3, bold=True)
        self.text(827, 20, 'Dat + Jennie | 08.10.2026 | 1 Blatt | A1 quer', 3.2, align='right')
        self.text(827, 32, 'ENTWICKLUNGSSTAND / KEINE FERTIGUNGSFREIGABE', 3.3, bold=True, align='right', color=d.WARN)
        self.line(8, 40, 833, 40, lw=.3)

    def text(self, x, y, text, size=2.8, bold=False, align='left', color=d.INK, rotate=0):
        super().text(x, y, text, size, bold, align, color, rotate)
        w = pdfmetrics.stringWidth(text, 'Arial-Bold' if bold else 'Arial', size*mm)/mm
        offset = {'left':0, 'center':.5, 'right':1}[align]
        if not rotate:
            self.text_boxes.append([x-w*offset, y-size, x+w*(1-offset), y+.7, text])

    def paragraph(self, x, y, width, value, size=2.8, leading=4.4, color=d.INK, bold=False):
        line = ''
        for word in value.split():
            trial = (line+' '+word).strip()
            if pdfmetrics.stringWidth(trial, 'Arial-Bold' if bold else 'Arial', size*mm)/mm > width and line:
                self.text(x, y, line, size, bold=bold, color=color)
                y += leading
                line = word
            else:
                line = trial
        if line:
            self.text(x, y, line, size, bold=bold, color=color)
            y += leading
        return y

    def image(self, name, x, y, w, h):
        entry = DATA['renders'][name]
        pw, ph = entry['pixels']
        factor = min(w/pw, h/ph)
        iw, ih = pw*factor, ph*factor
        ix, iy = x+(w-iw)/2, y+(h-ih)/2
        path = OUT/entry['path']
        self.pdf.drawImage(str(path), ix*mm, (self.height-iy-ih)*mm, iw*mm, ih*mm)
        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        self.elements.append(f'<image x="{ix}" y="{iy}" width="{iw}" height="{ih}" href="data:image/png;base64,{encoded}"/>')
        def project(p): return ix+p[0]*iw, iy+p[1]*ih
        for dim in entry['dimensions']:
            ends, lines = [project(p) for p in dim['ends']], [project(p) for p in dim['line']]
            for a,b in zip(ends, lines): self.line(*a,*b,lw=.15)
            a,b = lines
            self.line(*a,*b,lw=.18)
            length=math.hypot(b[0]-a[0],b[1]-a[1]);ux=(b[0]-a[0])/length;uy=(b[1]-a[1])/length
            for p,sign in ((a,1),(b,-1)):
                self.poly([(p[0]+sign*ux*2-uy*.6,p[1]+sign*uy*2+ux*.6),p,
                           (p[0]+sign*ux*2+uy*.6,p[1]+sign*uy*2-ux*.6)],lw=.18)
            self.text((a[0]+b[0])/2+2,(a[1]+b[1])/2-2,dim['text'],3,bold=True,align='center')
        return {key:project(value) for key,value in entry['anchors'].items()}

    def heading(self, x, y, width, number, title):
        self.text(x, y, number+'  '+title, 3.8, bold=True)
        self.line(x, y+3, x+width, y+3, lw=.25)

    def cells(self, x, y, widths, headings, rows, rowheight=8, size=2.7):
        self.rect(x,y,sum(widths),rowheight,fill='#edf0ee',lw=.18)
        for r,row in enumerate([headings]+rows):
            xx=x
            for value,w in zip(row,widths):
                assert pdfmetrics.stringWidth(str(value),'Arial-Bold' if r==0 else 'Arial',size*mm)/mm <= w-3,(value,w)
                self.text(xx+1.5,y+r*rowheight+rowheight*.66,str(value),size,bold=r==0)
                xx+=w
            self.line(x,y+(r+1)*rowheight,x+sum(widths),y+(r+1)*rowheight,lw=.12,color=d.GRAY)
        return y+(len(rows)+1)*rowheight

    def link(self,x,y,label,url):
        self.text(x,y,label,2.6,color='#245868')
        width=pdfmetrics.stringWidth(label,'Arial',2.6*mm)/mm
        self.pdf.linkURL(url,(x*mm,(self.height-y-1)*mm,(x+width)*mm,(self.height-y+3)*mm),relative=0)
        self.elements[-1]=f'<a href="{html.escape(url,quote=True)}">{self.elements[-1]}</a>'

    def finish(self):
        xml=f'<svg xmlns="http://www.w3.org/2000/svg" width="841mm" height="594mm" viewBox="0 0 841 594"><rect width="841" height="594" fill="white"/>'+ '\n'.join(self.elements)+'</svg>'
        SVG.write_text(xml,encoding='utf-8')
        self.pdf.showPage()
        (OUT/'text_layout.json').write_text(json.dumps(self.text_boxes,ensure_ascii=False),encoding='utf-8')


def part(s,x,y,name,title,lines,quantity='1 / 2'):
    s.rect(x,y,97,70,lw=.18,color='#919a99')
    s.text(x+3,y+6,title,2.9,bold=True)
    s.text(x+94,y+6,quantity,2.7,align='right',color=d.GRAY)
    s.image(name,x+3,y+8,91,28)
    dims=DATA['parts'].get(name,{}).get('size')
    if name == '12_ball_emblem':
        s.text(x+3,y+41,'Ø17 × 1,8 mm | CAD-Sollmaß',2.8,bold=True)
    elif dims:
        values=' × '.join(f'{v:.2f}'.rstrip('0').rstrip('.').replace('.',',') for v in dims)
        s.text(x+3,y+41,values+' mm | CAD-Hülle',2.8,bold=True)
    else:
        s.text(x+3,y+41,'Je Kappe Ø11,2 × 7,1 mm',2.8,bold=True)
    yy=y+47
    for line in lines:
        yy=s.paragraph(x+3,yy,91,line,size=2.65,leading=3.9)
    assert yy<=y+71,(title,yy)


def main():
    pdf=canvas.Canvas(str(PDF),pagesize=(841*mm,594*mm))
    pdf.setTitle('Pocket Pet V2 Revision C – Isometrische Gesamtzeichnung')
    pdf.setAuthor('OpenAI Codex / Projekt Pocket Pet')
    s=MasterSheet(pdf)
    s.heading(12,51,210,'1','So sieht das Gerät aus')
    anchors=s.image('ball_open',15,65,204,171)
    for key,x,y,label in [('P02',158,68,'P02 Deckel'),('P01',146,231,'P01 Unterschale'),
                         ('P03',17,201,'P03 Halterung'),('handheld',17,188,'Handheld herausnehmbar')]:
        a=anchors[key]
        label_width=pdfmetrics.stringWidth(label,'Arial-Bold',2.9*mm)/mm
        end_x=x+label_width+2 if key in ('P03','handheld') else x
        s.poly([a,(end_x,y+2)],lw=.18);s.circle(*a,.55,fill=d.INK);s.text(x,y,label,2.9,bold=True)
    s.text(15,244,'Ball: Ø130 | Wand 2,4 | Trennspalt 0,6',3.1,bold=True)
    s.text(15,251,'Geschlossen mit Anbauten: 130 × 142,55 × 118,6',2.9)
    s.image('handheld_closed',19,258,145,118)
    # Axis symbol matches the actual camera projection; local origin is the
    # rear, lower, left enclosure corner, not the front face.
    s.text(179,350,'Handheld-Achsen',2.7,bold=True)
    for dx,dy,label in [(13,7.5,'X'),(13,-7.5,'Y'),(0,-15,'Z')]:
        s.line(185,370,185+dx,370+dy,lw=.25)
        s.text(187+dx,370+dy,label,2.7,bold=True)
    s.paragraph(166,280,52,'Handheld: 62 × 90 × 31,4 mm. Mit Tasten 33,2 mm tief.',3,5,bold=True)
    s.paragraph(166,311,52,'Fenster: 31,2 × 41,4. Bild: 30,6 × 40,8. Randspiel 0,3 je Seite.',2.8,4.5)
    s.paragraph(15,383,203,'Der Ball schützt den eigenständig nutzbaren Handheld. Zum USB-Laden herausnehmen. Keine Kabel durch das Scharnier.',2.9,4.7)
    s.text(15,402,'Farben dienen der Zuordnung; keine verbindlichen Druckfarben.',2.6,color=d.GRAY)

    s.heading(228,51,299,'2','Innenaufbau / echte CAD-Explosionsansicht')
    s.text(230,62,'Explosionsabstände sind grafisch. Reale Einbaupositionen: Tabelle 4.',2.8,color=d.GRAY)
    anchors=s.image('exploded',233,68,173,337)
    labels=[('caps','P07 / P08 / P09','Links / OK / Rechts','Kopf Ø9,5; Führung Ø10'),
            ('P04','P04 Frontschale','Displayfenster + Führungen','Vier M2 schließen das Gerät'),
            ('E01','E01 ESP32 + Display','Waveshare ESP32-S3-LCD-2','Originales Hersteller-STEP'),
            ('P06','P06 Boardträger','E01: M01 / Träger: M02','Pins im 14-mm-STEP enthalten'),
            ('P10','P10 + E03 + 3 × E02','Tastenträger + FR4 + Taster','M03; Taster fest verlöten'),
            ('E08','E08 + E09 Audio','Lautsprecher + Verstärker','Vereinfachte Hüllen; Halter offen'),
            ('P11','P11 + E04 Akku','Akkuhalter + LiPo, M05','Zelle mit weichem Band halten'),
            ('P05','P05 Rückschale','M04 verbindet P05 mit P04','5 Körper: CAD-Verbindung offen')]
    for key,title,a,b in labels:
        p=anchors[key];yy=p[1]-2
        s.poly([p,(411,yy-1),(418,yy-1)],lw=.18);s.circle(*p,.55,fill=d.INK)
        s.text(420,yy,title,3.1,bold=True)
        s.paragraph(420,yy+6,104,a,2.8,4.3)
        s.paragraph(420,yy+13,104,b,2.65,4.1,color=d.WARN if key in ('P05','E08') else d.GRAY)

    s.heading(538,51,291,'3','Alle Druckteile / Anzahl: 1 Gerät / 2 Geräte')
    cards=[
      ('01_ball_lower','P01 Unterschale',['Wand 2,4; Halterung: Raster 48 × 40.','4 × Ø2,5, effektiv 9 tief.','Scharnier außen Ø8,4; Bohrung Ø3,4.']),
      ('02_ball_lid','P02 Deckel',['Wand 2,4; Scharnier Ø8,4 / Ø3,4.','Verschluss Ø3,4; Kopfraum Ø6,4.','Gegenstück P01: Ø2,6, 6 tief.']),
      ('03_removable_cradle','P03 Ball-Halter',['Innenbreite 64: Spiel 1 je Seite.','Boden 3; Wand 2,4; Bandfenster 11 × 2,2.','4 × Ø3,3 / Senk Ø6,7 × 1,7.']),
      ('04_handheld_front','P04 Frontschale',['Fenster 31,2 × 41,4; Front 2,4; R6.','3 × Ø10: X15 / 31 / 47; Y15.','M04: Ø1,6, effektiv 7,9 tief.']),
      ('05_handheld_back','P05 Rückschale',['Innen 57,2 × 85,2; Wand/Boden 2,4.','Lippe 56,4 × 84,4 × 2,7; Wand 1,2.','Seitenspiel 0,4; 4 × Ø2,3,','Senk Ø4,8 × 1,25; aktuell 5 Körper.']),
      ('06_board_carrier','P06 Boardträger',['Ausschnitt 41 × 49; USB-Korridor 15.','E01: 4 × Ø2,3; Raster 29 × 42,2.','P04: 4 × Ø2,5; Raster 46 × 52.']),
      ('caps','P07–P09 Tastenkappen',['Kopf Ø9,5 × 4,2; Flansch Ø11,2 × 1,2.','Stift Ø3,4 × 1,7; radial frei 0,25.','OK-Mulde Ø3 × 0,3; Seitenkerbe','3,5 × 0,8 × 0,3.'],'je 1 / 2'),
      ('10_switch_tray','P10 Tastenträger',['Boden 2; Auflage 43,4 × 12,4.','Lötfreiraum darunter 41 × 10.','2 × Ø2,5; Raster 50; M03.']),
      ('11_battery_tray','P11 Akkuhalter',['Körper 42 × 69; innen 38 × 65.','Boden/Wand 2; 2 × Ø3,2, Raster 47.','Bandschlitze 2 × 12; Raster 37.','Kabelöffnung 12 × 7; M05.']),
      ('12_ball_emblem','P12 Emblem',['Scheibe Ø17 × 1,8.','Nur an Deckelbrücke kleben.','Verschlussbewegung freihalten.']),
      ('13_button_fit_coupon','P13 Tasten-Passprobe',['Führungen Ø9,8 / 10 / 10,2.','Mit P07–P09 prüfen.','Vor Gehäusedruck am selben Material.'],'1 gesamt'),
      ('14_hinge_fit_coupon','P14 Scharnierprobe',['Bohrung Ø3,4; mit M3 testen.','Kein metrisches Gewinde modelliert.','Schraubhalt separat prüfen.'],'1 gesamt'),
      ('15_cradle_fit_coupon','P15 Halter-Passprobe',['Innenbreite 64.','Mit Handheldbreite 62 prüfen.','Sollspiel 1 pro Seite.'],'1 gesamt'),
    ]
    for i,card in enumerate(cards):
        name,title,lines,*qty=card
        part(s,538+(i%3)*97,58+(i//3)*70,name,title,lines,qty[0] if qty else '1 / 2')
    s.rect(635,338,194,70,lw=.18,color='#919a99')
    s.text(639,345,'Maße lesen / Bezugsachsen',3.1,bold=True)
    yy=352
    for value in ['Alle Werte in mm. × bedeutet Breite × Höhe × Tiefe (X × Y × Z); Hüllmaße ohne Schrauben. P12 ist eine Scheibe.',
                  'Handheld-Datum: X=0 links, Y=0 unten, Z=0 an der äußeren Rückwand; Z zeigt zum Display. Positionen gelten im montierten Zustand.',
                  'CAD = Sollgeometrie; Hersteller = Nennmaß; R = reservierter Raum. Keine Allgemeintoleranz oder Materialschwindung freigegeben.',
                  '12 Druckteile je Gerät (P01–P12): 24 für Dat/Jennie. Drei Passproben gemeinsam. Isometrie ohne festen Druckmaßstab.']:
        yy=s.paragraph(639,yy,186,value,2.8,4.5)+2

    s.heading(12,420,325,'4','Elektronik / Modelle, Maße und reale Positionen')
    s.text(14,430,'Vorschläge, noch nicht bestellt. Stückzahl für 1 / 2 Geräte. Z ab äußerer Rückwand.',2.7)
    rows=[
      ['E01','1/2','Waveshare ESP32-S3-LCD-2','35,01 × 48,21; STEP-Höhe 14','X13,49–48,51 / Y26,89–76,29 / Z14,6–28,6'],
      ['E02','3/6','Omron B3F-1000','6±0,2 × 6±0,2; Höhe 4,3±0,2','Mitte X15 / 31 / 47; Y15; Z21,6–25,9'],
      ['E03','1/2','Eigene FR4-Tasterplatine','43 × 12 × 1,6','X9,5–52,5 / Y9–21 / Z20–21,6'],
      ['E04','1/2','Adafruit 258 / LiPo 1200 mAh','Nenn 34 × 62 × 5; R 36 × 63 × 5,2','X13–49 / Y11,5–74,5 / Z6,9–12,1 (R)'],
      ['E05','1/2','JST-PH → MX1.25 Adapter','Kupplungsraum R 10 × 8 × 6','Mitte X31 / Y82 / Z8; Polung prüfen'],
      ['E06','1/2','Taster-Kabelsatz, AWG28','4 Adern; Startzuschnitt je 90','3 Signale + GND; Ø isoliert höchstens 1'],
      ['E07','1/2','USB-C-Kabel, noch offen','Steckerraum R 12 × 6','USB-P04: X23–39 / Y73,5–98,5 / Z16,4–27,4'],
      ['E08','1/2','Adafruit 3923, 8 Ω / 1 W','30 × 20 × 5; Kabel aktuell 30','X25,5–55,5 / Y7–27 / Z12,6–17,6'],
      ['E09','1/2','Adafruit 3006 / MAX98357A','Nenn 19,4 × 17,8 × 3,0 (flach)','90° gedreht: X4,9–22,7 / Y7,3–26,7 / Z13,1–16,1'],
      ['E10','0/0','Zusatz-Powerschalter','Nicht eingeplant','Kein zusätzliches Ladeboard nötig'],
      ['E11','1/2','Audio-Kabelsatz, AWG28','5 Adern je 90 + 2 Lautsprecheradern','Abisolieren 3; Servicebogen 15; Länge prüfen'],
    ]
    end=s.cells(12,435,[15,13,78,85,134],['ID','Anz.','Bauteil','Maße / Raum','Einbaulage (Handheld-Datum)'],rows,8.2,2.65)
    yy=end+6
    for value in ['Display: aktiv 30,6 × 40,8; Modul 33,6 × 46,6; Backlight 34,6±0,1 × 47,8±0,1; ohne Stiftleisten 8,2 hoch. Frontabstand nominal 0,4.',
                  'FR4: 12 × Ø1±0,1. Je Taster Bohrbild 6,5±0,1 × 4,5±0,1. Tasterachsen ab FR4-Unterkante: X5,5 / 21,5 / 37,5; Y6. Kein 2,54-mm-Lochraster-Ersatz.',
                  'Akku→Board-Pins nominal 2,5; Akku→Speaker 0,5; Speaker→P10 0,4; Audiohüllen seitlich 2,8. E09: 3-mm-Hülle gilt ohne aktuelle Schraubklemme/Pinleiste; Lieferhöhe offen.',
                  'Tastenspalt nominal 0,2 (Tastertoleranz beachten). E04-Prüfhülle ist keine garantierte Maximalgröße der gelieferten Zelle. Reale Teile vor Gehäusedruck messen.']:
        yy=s.paragraph(14,yy,321,value,2.65,4.2)+1
    assert yy<567,yy

    s.heading(343,420,304,'5','Schrauben, Bohrungen und Befestigung')
    s.text(345,430,'M2: Steigung 0,4; M3: 0,5. Gedruckte Vorlöcher ohne modelliertes Gewinde.',2.7)
    fasteners=[
      ['M01','4/8','M2 × 4','E01 → P06','Ø2,3; E01 M2-Hülse 2,5; Eingriff 2'],
      ['M02','4/8','M2 × 5','P06 → P04','Ø2,5 / Pilot Ø1,6 × 7,4; Eingriff 3'],
      ['M03','2/4','M2 × 6','P10 → P04','Ø2,5 / Pilot Ø1,6 × 7,9; Eingriff 4'],
      ['M04','4/8','M2 × 6 Senk','P05 → P04','Ø2,3 / Senk Ø4,8 × 1,25 / Pilot Ø1,6 × 7,9'],
      ['M05','2/4','M3 × 6','P11 → P05','Ø3,2 / Pilot Ø2,5 × 4; Restwand 0,9'],
      ['M06','4/8','M3 × 8 Senk','P03 → P01','Ø3,3 / Senk Ø6,7 × 1,7 / Pilot Ø2,5 × 9'],
      ['M07','1/2','M3 × 45','Ball-Scharnier','Ø3,4; Knöchellänge 36; 2 Scheiben + Mutter'],
      ['M08','1/2','M3 × 10','Ball-Verschluss','Ø3,4 / Kopf Ø6,4 / Pilot Ø2,6 × 6'],
      ['M09','1/2','M3 Mutter','für M07','Ausführung / reale Mutterhöhe abgleichen'],
      ['M10','2/4','M3 Scheibe','für M07','Außen ca. Ø7; reale Dicke offen'],
      ['M11','2/4','Weiches Band','Akku + Handheld','Breite 10; Endlänge nach Probemontage'],
      ['M12','n.B.','Geeigneter Kleber','P12 → P02','Nur Deckelbrücke; Menge nach Bedarf'],
    ]
    end=s.cells(343,435,[15,13,44,47,185],['ID','Anz.','Schraube / Teil','Verbindung','Bohrungen / effektive Tiefe / Hinweis'],fasteners,6.6,2.65)
    yy=end+6
    for value in ['Schraubachsen X/Y lokal: M01 16,5/45,5 × 29,9/72,1; M02 8/54 × 25/77; M03 6/56 × 15; M04 7/55 × 4/86; M05 7,5/54,5 × 43.',
                  'Ball-Datum: Mittelpunkt X0/Y0; Trennebene Z0. M06 X±24/Y±20. M07-Achse Y67/Z0,3: 10,8 + 0,4 + 13,6 + 0,4 + 10,8 = 36. M08 X0/Y−66.',
                  'Längen ohne Senkkopf ab Kopfunterseite; Senkschrauben inklusive Kopf. M05 kein M3×8: zu lang. M05 Kopf Ø≤6 (Raum Ø6,4). Eingriff, Schraubhalt und Drehmoment physisch ungeprüft.']:
        yy=s.paragraph(345,yy,300,value,2.65,4.2)+1
    assert yy<567,yy

    s.heading(659,420,170,'6','Anschlüsse / Montage / offene Punkte')
    yy=431
    for value in ['USB-Buchse mindestens 13,71 hinter Außenkante; Kabelstecker muss hineinreichen. Reales Kabel und Zugang vor Druck prüfen. microSD / BOOT / RESET ohne eigene Außenöffnung.',
                  'E04 JST-PH passt nicht direkt auf Board-MX1.25. Passenden Adapter und Polung verifizieren. E08: PicoBlade 1,25; 30-mm-Leitung ggf. verlängern.',
                  'Kabelkorridor reserviert: X56–58 / Y25–76 / Z12,6–14,6 (2 × 2). Stecker, Lötstellen und Schraubköpfe nicht vollständig in der Hüllenprüfung.',
                  'Montage: 1 Passproben; 2 E01 an P06 (M01); 3 Kappen in P04; 4 E02 an E03 löten, P10 montieren (M03); 5 P06 an P04 (M02).',
                  '6 P11 an P05 (M05), Akku weich fixieren; 7 Audiohalter entwickeln, Kabel verlegen; 8 P05/P04 mit M04 schließen; 9 P03 mit M06, Deckel mit M07 und Emblem kleben.',
                  'Noch offen: P05-Körper verbinden; Audiohalter und Schallöffnung modellieren (Vorschlag 5 Schlitze 1,2 × 8, Raster 2,4); E09-Lieferhöhe; Gesamtmontage / Bewegung / echte Passung prüfen.',
                  'Elektrik: Boardrevision / Pins / Ladestrom prüfen. Speaker an Verstärker +/−, kein Anschluss an GND. GPIO, Audio, Akkulaufzeit und Laden noch nicht geprüft.']:
        yy=s.paragraph(661,yy,166,value,2.7,4.25,color=d.INK)+2
    assert yy<568,yy
    s.text(661,503,'Elektronik: Hersteller-STEP / vereinfachte Hüllen',2.8,bold=True)
    for name,x,w,label in [('E01',661,52,'E01: STEP mit Pins'),('E03',718,52,'E03: FR4-Bohrbild'),('E04',775,52,'E04: Akku-Prüfhülle')]:
        s.image(name,x,506,w,24)
        s.text(x+w/2,534,label,2.6,align='center')
    for name,x,label,dimensions in [('E08',670,'E08: Speaker-Hülle','30 × 20 × 5'),('E09',752,'E09: Amp-Hülle, flach','17,8 × 19,4 × 3')]:
        s.image(name,x,539,65,18)
        s.text(x+32.5,561,label,2.6,align='center')
        s.text(x+32.5,566,dimensions+' mm',2.6,align='center')

    s.line(8,571,833,571,lw=.3)
    s.text(14,578,'Darstellung in Anlehnung an ISO (öffentliche Kurzbeschreibungen); keine Normkonformität behauptet. Herstellerquellen anklickbar:',2.6)
    links=[('ISO 5456-3','https://www.iso.org/standard/11503.html'),('ISO 129-1','https://www.iso.org/standard/64007.html'),
           ('ISO 128-3','https://www.iso.org/standard/83356.html'),('Waveshare','https://docs.waveshare.com/ESP32-S3-LCD-2'),
           ('Waveshare CAD','https://files.waveshare.com/wiki/ESP32-S3-LCD-2/ESP32-S3-LCD-2-2Dand3D.rar'),
           ('Omron B3F','https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf'),('Akku 258','https://www.adafruit.com/product/258'),
           ('Speaker 3923','https://www.adafruit.com/product/3923'),('Amp 3006','https://www.adafruit.com/product/3006')]
    x=14
    for label,url in links:
        s.link(x,584,label,url);x+=pdfmetrics.stringWidth(label,'Arial',2.6*mm)/mm+8
    s.text(827,584,'Maßzahlen gelten; Ansichten nicht abmessen. | OpenAI Codex',2.6,align='right')
    s.finish();pdf.save()
    print(PDF)


if __name__=='__main__': main()
