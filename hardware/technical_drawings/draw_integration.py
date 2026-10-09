"""Revision B: reproducible coloured electronics placement and assembly sheets.

Uses measured existing CAD, manufacturer references and explicitly marked
design envelopes. Keeps revision A and existing enclosure CAD unchanged.
"""
import csv
import hashlib
import json
import draw as d
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

OUT = d.ROOT / 'output/pdf/pocket_pet_technical_rev_b'
OUT.mkdir(parents=True, exist_ok=True)
FIT = json.loads((OUT / 'integration_check.json').read_text(encoding='utf-8'))
assert not FIT['intersections'], FIT['intersections']
d.OUT = OUT
d.REVISION, d.PAGE_COUNT = 'B', 14
PDF = OUT / 'Pocket_Pet_V2_RevB_Einbau_und_Montage.pdf'
S = d.Sheet
BLUE, GREEN, GOLD, RED, VIOLET = '#216484', '#427759', '#aa7620', '#a84937', '#715477'
LIGHT = {'case':'#e9e9e5','board':'#d6e7db','battery':'#f2e3b8','button':'#e8c8bd','audio':'#dfd8e8'}


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.').replace('.', ',')


def xy(s, ox, oy, k, x, y, w, h, color, label='', fill=None):
    """Local datum X left edge, Y bottom edge; screen Y down."""
    s.rect(ox+x*k, oy+(90-y-h)*k, w*k, h*k, color=color, fill=fill, lw=.3)
    if label:
        s.text(ox+(x+w/2)*k, oy+(90-y-h/2)*k+1, label, 2.6, bold=True, align='center', color=color)


def base(s, x, y, k=1):
    s.rect(x,y,62*k,90*k,6*k,fill=LIGHT['case'])
    s.rect(x+2.4*k,y+2.4*k,57.2*k,85.2*k,3.6*k)
    for xx in (7,55):
        for yy in (4,86):
            s.circle(x+xx*k,y+(90-yy)*k,2.8*k,fill='#c8c8c4')
            s.circle(x+xx*k,y+(90-yy)*k,.8*k)
    s.dimh(x,x+62*k,y,y-9,'62,0')
    s.dimv(y,y+90*k,x,x-10,'90,0')
    s.circle(x,y+90*k,1,fill=d.INK)
    s.text(x+1,y+90*k+7,'A/B: X0, Y0',2.5)


def legend(s,x,y):
    for i,(color,label) in enumerate(((GREEN,'ESP + Display'),(GOLD,'Akku'),(RED,'Tasten'),(VIOLET,'Audio'),(BLUE,'Kabel / Freiraum'))):
        s.rect(x,y+i*7,4,3,fill=color,color=color)
        s.text(x+6,y+2.8+i*7,label,2.7)


def trays(pdf):
    s=S(pdf,5,'P03/P11 / Ballhalterung und konkreter Akku-Einbauraum','P03 M 1:1; P11 M 2:1')
    s.text(23,45,'P03 / HALTERUNG IM BALL',3.1,bold=True)
    s.cad('03_removable_cradle',38,69)
    s.dimh(38,106.8,69,58,'68,8')
    s.dimv(69,165.8,106.8,118,'96,8')
    s.dimh(40.4,104.4,98,179,'64,0 lichte Breite')
    s.text(21,195,'62,0 Handheld + 1,0 Sollspiel je Seite',2.8)
    s.text(21,202,'Hülle h17; Basis 3; Seitenwand 2,4',2.8)
    s.text(21,209,'4× Ø3,3 / Senk Ø6,7×1,7; Raster 48×40',2.8)
    s.text(21,216,'Bandschlitze 11×2,2 für 10-mm-Textilband',2.8)
    s.text(158,45,'P11 / AKKUHALTER UND E04',3.1,bold=True)
    s.cad('11_battery_tray',173,69,2)
    # Carrier's full width is 55; tray body spans -21..21.
    s.rect(192,75,72,126,color=GOLD)
    s.text(228,135,'E04 max.',2.8,align='center',color=GOLD,bold=True)
    s.text(228,142,'36 × 63',2.8,align='center',color=GOLD)
    s.dimh(173,283,69,57,'55,0 inkl. Laschen')
    s.dimv(69,207,283,295,'69,0')
    s.dimh(186,270,190,222,'42,0 Halterkörper')
    s.text(161,235,'Innen 38×65 R3; außen 42×69 R5; Boden/Wand2',2.8)
    s.text(161,242,'2× Ø3,2 / Raster47; 2× Bandschlitz2×12 / Raster37',2.8)
    s.text(161,249,'Kabelöffnung12×7, obere Stirnseite; Hülle h7',2.8)
    s.notes(316,48,82,'AKKUVORSCHLAG / H + P',[
        'Adafruit 258, LP-503562 mit PCM, 1S/3,7 V/1200 mAh. Produktseite nominal 34×62×5.',
        'Vorhandene CAD-Prüfhülle 36×63×5,2. Kein zugesichertes Liefer-Maximalmaß; reales Teil inklusive PCM und Folie messen.',
        'Zur Aufnahme 38×65: 1,0 seitlich und 1,0 stirnseitig bei Prüf-Maximalhülle. Keine feste Klemmung oder Reserve für aufgeblähte Zellen behauptet.',
        'Akku-Unterseite Zlokal6,9; Oberseite bis12,1. Weiches Band über Zelle; Leitungen nach oben.',
        '2× M3×6 an Rückschale. JST-PH-Adapter zum passenden Boardstecker nötig, Polarität prüfen.',
        '1200 mAh ist ein konkreter Vorschlag für den vorhandenen Halter. Kleinerer Akku erfordert einen passenden Einsatz.'
    ])
    s.finish()


ELECTRONICS = [
 ['E01','Waveshare ESP32-S3-LCD-2','1','2','PCB 35,01 × 48,21; STEP 35,02 × 49,40 × 14','H / Referenz 20250122'],
 ['E02','Omron B3F-1000','3','6','6 ±0,2 × 6 ±0,2; Höhe 4,3 ±0,2','H / Vorschlag'],
 ['E03','Eigene FR4-Tasterplatine','1','2','43 × 12 × 1,6; 12 × Ø1 ±0,1','C / Sonderteil'],
 ['E04','Adafruit 258 / LP-503562 mit PCM','1','2','nominal 34 × 62 × 5; Prüf-Hülle 36 × 63 × 5,2','H + P / Vorschlag'],
 ['E05','Akku-Adapterleitung','1','2','JST-PH 2-pol. auf passendes Board-Pigtail','P / Ausführung offen'],
 ['E06','Tasterleitung, flexible Litze','4','8','3 Signale + GND; AWG28, Startlänge 90','P / Ablängmaß am Aufbau'],
 ['E07','USB-C-Daten-/Ladekabel','1','1-2','Stecker-Prüfhülle 12 × 6; Einsteckweg prüfen','P / Kabelmodell offen'],
 ['E08','Adafruit 3923, ovaler Lautsprecher','1','2','30 × 20 × 5; 8 Ohm, 1 W; Kabel 30','H / Vorschlag'],
 ['E09','Adafruit 3006 / MAX98357A','1','2','19,4 × 17,8 × 3,0 ohne hohe Anschlussklemme','H + P / flache Variante'],
 ['E10','Schalter, optionaler späterer Ausbau','0','0','Kein Schalter/Ausschnitt im aktuellen Entwurf','O / nicht eingeplant'],
 ['E11','Audioleitungssatz + Isolation','1','2','5 I2S-/Versorgungsadern; 2 Lautsprecheradern','P / Halter noch offen'],
]


def electronics(pdf):
    s=S(pdf,8,'Konkrete Bauteilvorschläge / zwei Geräte für Dat und Jennie','Tabelle; H Hersteller, C CAD, P Planung, O offen')
    s.table(16,43,[('Pos.',12),('Bauteil / Bezugsmodell',88),('1',11),('2',11),('Maß / Ausführung in mm',158),('Status',109)],ELECTRONICS,rowheight=10,size=2.5)
    s.notes(18,179,178,'BAUTEILWAHL UND KOMPATIBILITÄT',[
        'Das Waveshare-Modul enthält ESP32, TFT und Ladeelektronik. Kein zusätzliches ESP32-Devboard, TFT oder separates Lademodul einplanen.',
        'Akkuvorschlag 1200 mAh: passt zur vorhandenen großen Akkuaufnahme. Nominal- und Maximalhülle sind getrennt; Schutzplatine/Kabel/Stecker mitprüfen.',
        'Adafruit 258 hat JST-PH, Waveshare nennt MX1.25. Raster 1,25 allein beweist keine Steckkompatibilität. Adapter und Polarität vor Anschluss prüfen.',
        'Keine Hardware bestellt. Vorschläge sind keine Kauf- oder Montagefreigabe; Boardrevision und Ladestrom zuerst abgleichen.'
    ])
    s.notes(223,179,176,'AUDIO UND ZEICHNUNGSBEZUG',[
        '3923: Herstellerhülle und aktuelles 30-mm-Kabel eingeplant. Speaker-/Kabelrevision von November 2025 beachten.',
        '3006: Hersteller nennt 3,0 Höhe, liefert seit Juni 2024 aber eine Schraubklemme. Die Prüfung gilt nur für die flache Ausführung ohne Klemme und Pinleiste.',
        'Blätter 9-14 ergänzen den bestehenden CAD-Maßplan 1-7. Bauteilquellen/URLs stehen in QUELLEN.md. Reservierte Kabelhüllen sind unsere Sollvorgaben.',
        'Audiohalter und Schallöffnung fehlen noch im CAD. Eine freie Hülle beweist keine befestigte oder akustisch funktionierende Montage.'
    ],color=d.WARN)
    for x,y,label,url in (
        (18,245,'Waveshare: docs.waveshare.com/ESP32-S3-LCD-2','https://docs.waveshare.com/ESP32-S3-LCD-2'),
        (223,245,'Omron: B3F Herstellerdatenblatt','https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf'),
        (18,252,'Akku: adafruit.com/product/258','https://www.adafruit.com/product/258'),
        (223,252,'Akku-Datenblatt: LP-503562 mit PCM','https://cdn-shop.adafruit.com/product-files/258/C101-_Li-Polymer_503562_1200mAh_3.7V_with_PCM_APPROVED_8.18.pdf'),
        (18,259,'Verstärker: adafruit.com/product/3006','https://www.adafruit.com/product/3006'),
        (223,259,'Lautsprecher: adafruit.com/product/3923','https://www.adafruit.com/product/3923'),
    ):
        s.text(x,y,label,2.55,color=BLUE)
        s.pdf.linkURL(url,(x*mm,(297-y-1)*mm,(x+175)*mm,(297-y+3)*mm),relative=0)
    s.finish()


def placement(pdf):
    s=S(pdf,9,'Farbiger Einbauplan / Frontpaket und Rückschalenpaket','M 1,5:1; positive lokale X/Y-Koordinaten')
    s.text(20,45,'FRONT GEÖFFNET / BLICK AUF EINBAULAGE',3.1,bold=True)
    x,y,k=40,66,1.5
    base(s,x,y,k)
    xy(s,x,y,k,13.49137,26.89137,35.01726,49.40191,GREEN,'E01',LIGHT['board'])
    xy(s,x,y,k,15.7,28.8,30.6,40.8,BLUE,'TFT 30,6 × 40,8')
    for xx in (8,54):
        for yy in (25,77):s.circle(x+xx*k,y+(90-yy)*k,1.25*k,color=GREEN)
    for xx in (16.5,45.5):
        for yy in (29.9,72.1):s.circle(x+xx*k,y+(90-yy)*k,1.15*k,color=GREEN)
    xy(s,x,y,k,9.5,9,43,12,RED,'',LIGHT['button'])
    s.text(x+31*k,y+(90-10)*k,'E03',2.1,align='center',color=RED)
    for xx in (15,31,47):
        s.circle(x+xx*k,y+75*k,3*k,color=RED)
        s.text(x+xx*k,y+75*k+1,'L' if xx==15 else 'OK' if xx==31 else 'R',2.2,align='center')
    xy(s,x,y,k,23,73.5,16,16.5,BLUE,'USB')
    s.text(20,217,'USB oben; Tasten unten. Keine Spiegelung der Achskoordinaten.',2.7)
    s.text(161,45,'RÜCKPAKET / GLEICHE PROJEKTIONSRICHTUNG',3.1,bold=True)
    x2=181
    base(s,x2,y,k)
    xy(s,x2,y,k,10,8.5,42,69,GOLD,'',LIGHT['battery'])
    s.text(x2+31*k,y+(90-76)*k,'P11',2.4,align='center',color=GOLD)
    xy(s,x2,y,k,13,11.5,36,63,GOLD,'E04 max. 36 × 63')
    for xx in (7.5,54.5):s.circle(x2+xx*k,y+47*k,1.6*k,color=GOLD)
    xy(s,x2,y,k,25.5,7,30,20,VIOLET,'E08',LIGHT['audio'])
    xy(s,x2,y,k,4.9,7.3,17.8,19.4,VIOLET,'E09',LIGHT['audio'])
    s.text(164,217,'Audio liegt VOR dem Akku, in einer anderen Z-Ebene.',2.7)
    legend(s,304,47)
    s.notes(304,92,93,'DATUM / ABLESEN',[
        'A: linke Außenkante X = 0. B: untere Außenkante Y = 0. C: Rückfläche Z = 0.',
        'X wächst rechts, Y oben, Z zum Display. Außen: X 0...62, Y 0...90, Z 0...31,4.',
        'Im CAD: Xlokal = X + 31; Ylokal = Y + 43; Zlokal = Z + 26,4.',
        'Front- und Rückpaket sind transparent überlagert gedacht; keine separate gespiegelte Rückansicht.',
        'Positionshüllen sind mit bestehenden Handheld-Teilen digital geprüft. Befestigung/Stecker/Leitungen zusätzlich entwickeln.'
    ])
    s.table(18,231,[('Merkmal',59),('X lokal',55),('Y lokal',55),('Z lokal',69),('Bedeutung',144)],[
        ['E01 volle STEP-Hülle','13,491...48,509','26,891...76,293','14,6...28,6','Lange Pins enthalten; Lage aus Original-STEP'],
        ['E04 max. Akkuhülle','13...49','11,5...74,5','6,9...12,1','Zelle mit PCM; Kabel/Stecker separat'],
        ['E03 Tasterplatine','9,5...52,5','9...21','20...21,6','Tasterhöhe ab Oberseite E03'],
    ],rowheight=8,size=2.5)
    s.finish()


def section_block(s,x,y,k,y0,y1,z0,z1,label,color,fill):
    # In side sections horizontal Y increases toward USB, vertical Z increases up.
    s.rect(x+y0*k,y+(33.2-z1)*k,(y1-y0)*k,(z1-z0)*k,color=color,fill=fill)
    if label:s.text(x+(y0+y1)/2*k,y+(33.2-(z0+z1)/2)*k+1,label,2.3,align='center',color=color,bold=True)


def sections(pdf):
    s=S(pdf,10,'Schichtfolge / Display, Akku, Taster und Audio in der Tiefe','M 2:1; Hüllenprojektionen, keine OCCT-Schnittkonturen')
    x,y,k=22,70,2
    s.text(22,45,'Y/Z-PROJEKTION / USB RECHTS, DISPLAY OBEN',3.1,bold=True)
    section_block(s,x,y,k,0,90,0,2.4,'P05',d.GRAY,LIGHT['case'])
    section_block(s,x,y,k,0,28.5,29,31.4,'P04',d.GRAY,LIGHT['case'])
    section_block(s,x,y,k,69.9,90,29,31.4,'P04',d.GRAY,LIGHT['case'])
    section_block(s,x,y,k,8.5,77.5,4.9,6.9,'P11',GOLD,LIGHT['battery'])
    section_block(s,x,y,k,11.5,74.5,6.9,12.1,'E04',GOLD,LIGHT['battery'])
    # Header-containing board bounding envelope is deliberately not a full solid.
    s.rect(x+26.89137*k,y+(33.2-28.6)*k,49.40191*k,14*k,color=GREEN)
    s.text(x+55*k,y+16,'E01 STEP-Hülle',2.5,align='center',color=GREEN)
    s.line(x+26.9*k,y+(33.2-14.6)*k,x+76.3*k,y+(33.2-14.6)*k,color=GREEN,dash=True)
    section_block(s,x,y,k,9,21,20,21.6,'FR4',RED,LIGHT['button'])
    section_block(s,x,y,k,12,18,21.6,25.9,'E02',RED,LIGHT['button'])
    section_block(s,x,y,k,13.3,16.7,26.1,27.8,'',RED,LIGHT['button'])
    section_block(s,x,y,k,9.4,20.6,27.8,29,'',RED,LIGHT['button'])
    section_block(s,x,y,k,10.25,19.75,29,33.2,'P08',RED,LIGHT['button'])
    section_block(s,x,y,k,7,27,12.6,17.6,'E08*',VIOLET,LIGHT['audio'])
    s.dimh(x,x+180,y+66.4,153,'90,0')
    s.dimv(y,y+66.4,x+180,213,'33,2 mit Tasten')
    s.text(22,165,'* Audio ist bei X = 40,5; diese Ansicht projiziert mehrere X-Ebenen.',2.7)
    s.text(22,172,'Kein massiver Boardquader: reale Bauteile/Pins liegen innerhalb der grünen Hülle.',2.7)
    s.notes(246,48,149,'FREIRÄUME / NOMINAL',[
        'Displayoberseite Z28,6 bis Frontinnenseite Z29,0: 0,4. Fensterübermaß zur aktiven Fläche: je 0,3 an jeder Kante.',
        'Akku-Maximalhülle Z12,1 bis tiefste Boardpins Z14,6: 2,5. Ein Halteband verbraucht einen Teil dieses Freiraums.',
        'Akku zu Lautsprecher: 0,5. Lautsprecher zu Tastenträgerunterseite Z18,0: 0,4. Das ist knapp; kein Halter unter der Zelle einquetschen.',
        'Stößel Z26,1 zu Tasteroberseite Z25,9: 0,2 nominal. Bei Tasterhöhe +0,2 fällt dieses Spiel auf 0. Toleranz-/Hubprüfung erforderlich.',
        'Die großen Hüllenabstände sind nur nominal. Pins, Lötpunkte, Litzen und Audiohalter dürfen sie nicht vollständig ausfüllen.'
    ])
    s.table(18,191,[('Schicht / Bezug C',85),('Z unten',35),('Z oben',35),('Dicke / Funktion',106),('Quellenstatus',121)],[
        ['Rückwand P05','0','2,4','2,4; Innenboden bei 2,4','C / Rückschale noch getrennte Körper'],
        ['Akkuhalter P11 / Boden','4,9','6,9','2,0; Auflage auf Rückwanddomen','C'],
        ['Akku E04 / Maximalhülle','6,9','12,1','5,2; noch ohne Band/Kabel','P / Herstellermaß separat'],
        ['Board E01 / komplette STEP-Hülle','14,6','28,6','14,0 mit langen Stiftleisten','H / keine neue Platinengeometrie'],
        ['P06 / Trägerplatte','18,3','20,3','2,0; Board sitzt an Herstelleraufnahmen','C'],
        ['P10 / Hülle; E03 / FR4','18,0 / 20,0','21,5 / 21,6','3,5 / 1,6','C / Stützen und Durchbruch beachten'],
        ['P04 Frontfläche / Tastenkopf','29,0 / 29,0','31,4 / 33,2','2,4 / 4,2','C / Taste steht 1,8 vor'],
    ],rowheight=8,size=2.5)
    s.finish()


HOLES = [
 ['M01','4','16,5 / 45,5','29,9 / 72,1','P06 Ø2,3 durch, t2','E01 M2, H2,5','M2×4; Eingriff ca. 2'],
 ['M02','4','8 / 54','25 / 77','P06 Ø2,5 durch, t2','P04 Ø1,6; geometr. 7,4*','M2×5; Eingriff 3'],
 ['M03','2','6 / 56','15','P10 Ø2,5 durch; Kopf Ø6,4','P04 Ø1,6; geometr. 7,9*','M2×6; Eingriff 4'],
 ['M04','4','7 / 55','4 / 86','P05 Ø2,3; Senk Ø4,8×1,25','P04 Ø1,6; geometr. 7,9*','M2×6 Senk; ca. 3,6'],
 ['M05','2','7,5 / 54,5','43','P11 Ø3,2 durch; t2','P05 Ø2,5; 4,0 tief*','M3×6; Eingriff 4'],
 ['M06','4','X CAD ±24','Y CAD ±20','P03 Ø3,3; Senk Ø6,7×1,7','P01 Ø2,5; 9,0 tief*','M3×8 Senk; ca. 5'],
 ['M07','1','X-Achse','Y CAD67; Z0,3','Scharnier Ø3,4; Länge36','M3-Mutter + 2 Scheiben','M3×45; Durchgang'],
 ['M08','1','X CAD0','Y CAD -66','P02 Ø3,4; Kopf Ø6,4','P01 Ø2,6; 6,0 tief*','M3×10; Eingriff prüfen'],
]


def screws(pdf):
    s=S(pdf,11,'Verschraubung / Achskoordinaten, Bohrungen und Einschraubwege','Tabellen; Schraubenprinzip M 5:1')
    s.table(16,43,[('Pos.',12),('n',9),('X lokal / mm',47),('Y lokal / mm',51),('Durchgang / Kopf',93),('Gegenstück / Kernloch',96),('Schraube / Länge',75)],HOLES,rowheight=12,size=2.45)
    s.text(18,161,'* Effektive Sacklochtiefe ab Auflagefläche; CAD-Schneidwerkzeug kann über die Fläche hinaus beginnen.',2.7)
    # Bottom-mount battery fastener section, exact nominal depth chain.
    x,y,k=41,194,5
    s.text(20,178,'M05 / AKKUHALTER AN RÜCKWAND',3.1,bold=True)
    s.rect(x,y,27,10,fill=LIGHT['battery'],color=GOLD)
    s.rect(x,y+10,27,12.5,fill=LIGHT['case'])
    s.rect(x,y+22.5,27,12,fill=LIGHT['case'])
    s.rect(x+8.5,y-8,10,8,fill='#bcc2c4')
    s.rect(x+10,y,7,30,fill='#bcc2c4')
    s.dimv(y,y+30,x+27,x+43,'6,0 Schraube ohne Kopf')
    s.text(22,239,'2,0 Halter + 2,5 Dom + 1,5 in Rückwand = 6,0',2.65)
    s.text(22,246,'Restwand am Schraubenende: 0,9 nominal. M3×8 passt hier nicht.',2.65,color=d.WARN)
    s.notes(162,179,111,'SCHRAUBENDETAILS',[
        'M2: Nenndurchmesser 2,0, Regelgewinde Steigung 0,4. M3: 3,0 und Steigung 0,5.',
        'M01/M02/M03/M05: flacher Kopf; Länge ab Kopfunterseite. M04/M06: Senkkopf, Länge einschließlich Kopf.',
        'M05 Kopf darf maximal Ø6,0 haben: Freischnitt im P11 Ø6,4. Kopfmodell und Schraubenlieferant abgleichen.',
        'Keine metrischen Gewinde in die gedruckten Kernlöcher hineininterpretieren; direktes Einschrauben erst am Muster prüfen.'
    ])
    s.notes(293,179,104,'NICHT FREIGEGEBEN',[
        'M02/M03 ohne modellierte Schraubenkopf-Hüllen geprüft. M2-Köpfe/Lötstellen am vollständigen Aufbau prüfen.',
        'Senkungen stammen aus CAD. Winkel/Paarung des tatsächlichen Senkkopfs vor Serienmontage abgleichen.',
        'Keine Gewindeeinsätze vorgesehen. Kein Anzugsdrehmoment freigegeben; PLA kann bei Überlast reißen.',
        'Für Ballachsen gelten CAD-Koordinaten; Handheld-Datumsystem gilt nur für M01-M05.'
    ],color=d.WARN)
    s.finish()


def connectors(pdf):
    s=S(pdf,12,'Anschlüsse und Leitungsführung / USB, Akku, Taster und Audio','M 2:1 USB-Korridor; elektrische Funktionsskizze ohne GPIO-Freigabe')
    s.text(19,46,'USB / OBERE HANDHELD-KANTE',3.1,bold=True)
    s.rect(24,65,124,22,fill=LIGHT['case'])
    s.rect(70,65,32,22,color=BLUE,fill='#dce9ef')
    s.rect(74,70,24,12,color=BLUE)
    s.dimh(70,102,65,57,'16,0 freier Korridor')
    s.dimv(65,87,102,120,'11,0')
    s.text(19,103,'Innere Steckerhülle als Planvorgabe: maximal 12,0 × 6,0.',2.65)
    s.text(19,110,'Reserve zur 16×11-Öffnung: 2,0 seitlich, 2,5 je Höhenkante.',2.65)
    s.text(19,117,'Diese Ansicht ist das Öffnungsprinzip, keine neue USB-Buchse.',2.65)
    s.notes(184,47,211,'MECHANISCHE ANSCHLÜSSE',[
        'Board-STEP endet am USB-Bereich bei Ylokal76,293; Gehäuserand liegt bei Y90. Rezess: mindestens 13,707 bis zur vordersten Boardhülle. Ein normaler breiter Stecker kann vor vollständigem Kontakt hängen bleiben.',
        'P04 USB-Ausschnitt: Xlokal23...39; Ylokal73,5...98,5; Zlokal16,4...27,4. Schnittvolumen 16 × 25 × 11. Nicht automatisch die nutzbare Buchsenhöhe.',
        'Kein Ausschnitt in P05 für USB, SD oder Akku. Im aktuellen Aufbau sind nur USB und drei Bedientasten von außen vorgesehen. SD/Boot/Reset intern nach Öffnen zugänglich.',
        'Akkuadapter: Original-JST-PH erhalten, passende MX1.25-Seite über geprüften Pigtail. Für die zusätzliche JST-PH-Kupplung ist eine Planungsbox 10 × 8 × 6 im oberen Rückraum reserviert, Center X31/Y82/Z8. Boardstecker/Liefermaße separat prüfen.'
    ])
    s.text(18,142,'FUNKTIONSSKIZZE / KEINE VERDRAHTUNGSFREIGABE',3.1,bold=True)
    s.rect(20,158,57,20,fill=LIGHT['battery'],color=GOLD)
    s.text(48.5,169,'1S-LiPo + PCM',2.8,align='center',bold=True)
    s.rect(111,154,91,32,fill=LIGHT['board'],color=GREEN)
    s.text(156.5,164,'Waveshare E01',3,align='center',bold=True)
    s.text(156.5,173,'USB-C / Laderegler / TFT / GPIO',2.6,align='center')
    s.line(77,168,111,168,color=GOLD,lw=.5)
    s.text(93,163,'2 Adern',2.5,align='center')
    s.rect(235,151,61,22,fill=LIGHT['button'],color=RED)
    s.text(265.5,161,'3 Taster',2.8,align='center',bold=True)
    s.text(265.5,168,'3 Signale + GND',2.4,align='center')
    s.line(202,162,235,162,color=RED,lw=.5)
    s.rect(235,183,61,25,fill=LIGHT['audio'],color=VIOLET)
    s.text(265.5,193,'MAX98357A E09',2.7,align='center',bold=True)
    s.text(265.5,201,'BCLK / LRC / DIN',2.5,align='center')
    s.poly([(202,180),(219,180),(219,196),(235,196)],color=VIOLET,lw=.5)
    s.rect(331,183,61,25,fill=LIGHT['audio'],color=VIOLET)
    s.text(361.5,194,'Speaker E08',2.7,align='center',bold=True)
    s.text(361.5,202,'8 Ohm / max. 1 W',2.5,align='center')
    s.line(296,196,331,196,color=VIOLET,lw=.5)
    s.text(314,190,'+ / -',2.6,align='center')
    s.notes(18,224,179,'KABEL ALS STARTVORGABEN P',[
        'Taster: 4 × AWG28, Startzuschnitt 90. I2S/Versorgung: 5 × 90. Litzenhülle max. Ø1,0; Abisolierung 3,0; Wärmeschrumpfschlauch auf Lötstellen.',
        'Kabelkorridor als Planvorgabe: Xlokal56...58, Y25...76, Z12,6...14,6. Bündel maximal 2 × 2. Oben 15 mm Servicebogen; Kabelkollisionen noch nicht geprüft, finale Länge am Muster.'
    ])
    s.notes(223,224,175,'ELEKTRISCHE PRÜFPUNKTE',[
        'Keine ungeprüften GPIO16/17/18. Der aktuell verlinkte Waveshare-Schaltplan trägt Touch im Dateinamen; Zuordnung zur realen Boardrevision erst bestätigen.',
        'Audio-Ausgänge sind BTL: Speaker an + und -, keine Seite an GND. Versorgung, Abschaltung, Ladestrom und Leistungsbegrenzung auf 1 W müssen noch festgelegt werden.'
    ],color=d.WARN)
    s.finish()


def audio(pdf):
    s=S(pdf,13,'Audio-Einbauraum / Lautsprecher und flacher I²S-Verstärker','M 3:1; Positionshüllen, Halter noch zu konstruieren')
    x,y,k=35,67,3
    s.text(20,45,'UNTERES HANDHELD / GLEICHE X/Y-DATUMSBEZÜGE',3.1,bold=True)
    # Cropped local Y0..30 region.
    s.rect(x,y,62*k,30*k,fill=LIGHT['case'])
    for xx in (7,55):s.circle(x+xx*k,y+26*k,2.8*k,fill='#c8c8c4')
    ax,ay=x+4.9*k,y+(30-26.7)*k
    sx,sy=x+25.5*k,y+(30-27)*k
    s.rect(ax,ay,17.8*k,19.4*k,color=VIOLET,fill=LIGHT['audio'])
    s.rect(sx,sy,30*k,20*k,color=VIOLET,fill=LIGHT['audio'])
    s.text(ax+8.9*k,ay+29,'E09',3.2,align='center',bold=True)
    s.text(sx+15*k,sy+30,'E08',3.2,align='center',bold=True)
    s.dimh(sx,sx+90,sy,57,'30,0')
    s.dimv(sy,sy+60,sx+90,238,'20,0')
    s.dimh(ax,ax+53.4,ay+58.2,176,'17,8 (Modul um 90° gedreht)')
    s.dimh(ax+53.4,sx,sy+60,194,'2,8 Abstand')
    s.text(20,211,'E08 Mitte X40,5 / Y17,0; Z12,6...17,6.',2.8)
    s.text(20,218,'E09 Mitte X13,8 / Y17,0; Z13,1...16,1 (nur flache Variante).',2.8)
    s.text(20,225,'Reale Raster/Bohrungen am Verstärker nicht aus dem Foto ableiten.',2.8)
    s.notes(262,47,135,'WARUM GENAU DIESE LAGE?',[
        'Die Lage bei Y17 hält die Audiohüllen von den unteren Gehäusedomen frei. Eine Verschiebung um 2,0 nach unten auf Y15 führt an beiden Modulen zu einer Überschneidung.',
        'Aktuelle elektronische Hüllen haben im OCCT-Schnitt keine Volumenüberschneidung mit P04-P11, dem offiziellen Board-STEP, Akku oder Tasterpaket.',
        'Freiraum zum Board in Y: Speaker rechnerisch -0,109 (Hüllen überlappen minimal), aber reale STEP-Körper schneiden ihn dort nicht. Kein pauschaler Sicherheitsabstand behauptet.',
        'Der Amp ist ohne Klemme/Pinleisten geplant. Geliefertes 3006 inklusive Klemme und Kabel ist noch nicht als Einbaukörper erfasst.',
        'Die Herstellerhülle des Speakers ist ohne bewegte Membran, Leitungsbogen und Montageclips geprüft.'
    ])
    s.notes(262,183,135,'NÖTIGE KONSTRUKTION / NICHT IM CAD',[
        'Haltekonzept: seitliche, isolierte Auflager an der Frontschale; Speaker am Rahmen halten, Membran freilassen. Keine Befestigung auf der Akku-Folie.',
        'Schallöffnung als Vorschlag: 5 Schlitze je 1,2 × 8,0, Raster 2,4 auf unterer Stirnseite. Center X40,5 / Z16,0. Öffnung, Domabstände und Halter zuerst gemeinsam modellieren.',
        'Nur 0,5 zum Akku und 0,4 zum Tastenträger: falls Halter, Isolation und Lötstellen nicht hineinpassen, Tiefe vergrößern oder Akku-/Audiokonzept ändern.'
    ],color=d.WARN)
    s.finish()


def assembly(pdf):
    s=S(pdf,14,'Montagefolge / Explosionsprinzip und Freigabegrenzen','Explosionsprinzip ohne Maßstab; keine Druckfreigabe')
    s.text(18,45,'HANDHELD / LAGEN UND MONTAGERICHTUNG',3.1,bold=True)
    # Exploded stack boxes use common XY proportions, deliberately no fake scale.
    layers=[('P04 Front + P07/P08/P09',LIGHT['button'],RED),('E01 Board + P06 Träger',LIGHT['board'],GREEN),('E02 Taster + E03 FR4 + P10',LIGHT['button'],RED),('E08/E09 Audio, Halter offen',LIGHT['audio'],VIOLET),('E04 Akku + P11 Halter + Band',LIGHT['battery'],GOLD),('P05 Rückschale',LIGHT['case'],d.INK)]
    for i,(label,fill,col) in enumerate(layers):
        yy=61+i*28
        s.rect(25,yy,100,15,r=2,fill=fill,color=col)
        s.text(75,yy+9.7,label,2.55,align='center',bold=True,color=col)
        if i<5:s.line(75,yy+15,75,yy+28,dash=True,color=d.GRAY)
    s.text(22,241,'Schließen: 4 × M04 von der Rückseite.',2.8)
    s.text(22,249,'Geometrische Reihenfolge, Audio separat befestigen.',2.7)
    s.notes(154,45,118,'1-5 / ELEKTRONIKPAKETE',[
        '1. Tasten von innen in P04 einsetzen. Flansch innen, Stößel zur Tasterplatine; Führung Ø10 / Kopf Ø9,5.',
        '2. E01 an P06: 4×M01. Danach Träger an P04: 4×M02. USB zur oberen Kante; kein Druck auf Display oder Flex.',
        '3. E02 auf E03 löten, leitend gleiche Tasterpins prüfen. E03 auf P10-Randauflage; P10 mit 2×M03 montieren. Hub/Loslassen prüfen.',
        '4. P11 mit 2×M05 an P05, Akku in Aufnahme legen, weiches 10-mm-Band. Keine Klemmung der Zelle. Kabel durch 12×7-Auslass oben führen.',
        '5. Audiohalter erst konstruktiv fertigstellen, Module isolieren und Kabel führen. Nicht lose zwischen Akku und Tastenträger einklemmen.'
    ])
    s.notes(286,45,111,'6-9 / ZUSAMMENBAU',[
        '6. Anschlüsse/Polarität prüfen und Leitungen stecken. Ohne Verschrauben Probeschluss; kein Kabel unter Bund oder Schraubdom.',
        '7. P05 auf P04, 4×M04 gleichmäßig einschrauben. Kein Kraftschluss gegen Akku, Display oder Stecker.',
        '8. P03 im P01: 4×M06. Handheld in 64-mm-Aufnahme; 10-mm-Sicherungsband durch 11×2,2-Fenster führen.',
        '9. P02 mit M07, Scheiben und Mutter am Scharnier. Emblem nur am Deckel verkleben. M08 schließt den Ball. USB nur am entnommenen Handheld laden.'
    ])
    s.notes(155,205,242,'GEPRÜFT UND NOCH OFFEN',[
        'Geprüft: Herstellerquellen, CAD-Maße, offizielle Boardhülle und elektronische Einbauhüllen; Revision-B-PDF/SVG. Hüllenprüfung enthält weder Befestiger noch Kabel und ist kein vollständiger V2-Montagenachweis.',
        'Offen vor einem Drucksatz: P05 fünf Körper verbinden; Audiohalter/Schallöffnung konstruieren; USB-Einsteckbarkeit lösen; Stecker/Lötstellen/Schraubköpfe vollständig modellieren und Deckel/Entnahme erneut prüfen.',
        'Danach erst Passproben, echter Einbau, Tastenhub, Ladung, Audioleistung und Wärme prüfen. Keine STL-Fertigungsfreigabe, kein Druck und kein Hardware-Funktionstest in dieser Runde.'
    ],color=d.WARN)
    s.finish()


SOURCES = '''# Quellen und Maßstatus / Revision B, 08.10.2026

H = veröffentlichte Herstellerreferenz, C = bestehendes CAD-Sollmaß,
P = eigene Planvorgabe, O = offene Freigabe. Nicht bekannte Istmaße werden
nicht durch scheinbar präzise Zeichnungswerte ersetzt.

- Waveshare ESP32-S3-LCD-2: https://docs.waveshare.com/ESP32-S3-LCD-2
- Ressourcen: https://docs.waveshare.com/ESP32-S3-LCD-2/Resources-And-Documents
- Mechanische Referenz: https://files.waveshare.com/wiki/ESP32-S3-LCD-2/ESP32-S3-LCD-2-2Dand3D.rar
- Verlinkter Schaltplan (Touch im Dateinamen, reale Revision abgleichen): https://files.waveshare.com/wiki/ESP32-S3-LCD-2/ESP32-S3-Touch-LCD-2-SchDoc.pdf
- Omron B3F: https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf
- Akkuvorschlag Adafruit 258: https://www.adafruit.com/product/258
- Aktuell verlinktes Akkudatenblatt (503562 mit PCM): https://cdn-shop.adafruit.com/product-files/258/C101-_Li-Polymer_503562_1200mAh_3.7V_with_PCM_APPROVED_8.18.pdf
- Audioverstärker 3006: https://www.adafruit.com/product/3006
- Verstärker-Dokumentation: https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/downloads
- Speaker 3923: https://www.adafruit.com/product/3923

Die aktuelle 3006-Lieferung hat eine Schraubklemme; eine volle 3-mm-Höhe
einschließlich dieser Klemme ist nicht nachgewiesen. Die Hüllenprüfung gilt
nur für die flache Variante ohne Klemme und Pinleiste. Deren physische
Höhe einschließlich Lötstellen ist vor Montage zu messen.

Akku: Produktseite nominal 34×62×5, bisherige CAD-Prüfhülle 36×63×5,2.
Die CAD-Prüfhülle wird nicht als garantierte Maximalabmessung des aktuell
gelieferten Akkus behauptet. PCM, Folie, Kabelausgang und Stecker prüfen.
Stecker: JST-PH des Akkuvorschlags und MX1.25 des Boards sind nicht direkt
kompatibel; gleiche 1,25-mm-Raster verschiedener Steckfamilien ebenso wenig.

Alle Kabel-/USB-/Kupplungshüllen und Zuschnittlängen sind Planvorgaben,
keine verifizierten Herstellermaße eines ausgewählten Zubehörmodells.
Keine GPIO-, Lade-, Audio- oder physische Fertigungsfreigabe.
'''


def main():
    pdf=canvas.Canvas(str(PDF),pagesize=(420*mm,297*mm))
    pdf.setTitle('Pocket Pet V2 / Revision B / Elektronik, Einbau und Montage')
    pdf.setAuthor('OpenAI Codex')
    for fun in (d.overview,d.case,d.board,d.controls,trays,d.ball,d.bom_mechanical,electronics,placement,sections,screws,connectors,audio,assembly):fun(pdf)
    pdf.save()
    with (OUT/'Stueckliste_2_Geraete_RevB.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.writer(fp,delimiter=';')
        w.writerow(['Pos','Bauteil','Menge1','Menge2','Maß oder Anschluss','Status'])
        for pos,title,key,one,two in d.PRINTED:
            w.writerow([pos,title,one,two,' × '.join(f(v) for v in d.DATA['parts'][key]['size']),'P05: 5 Körper offen' if pos=='P05' else 'CAD-Sollmaß'])
        for row in d.FASTENERS:w.writerow(row+['siehe Bezeichnung','vorläufig, physisch prüfen'])
        w.writerows(ELECTRONICS)
    (OUT/'QUELLEN.md').write_text(SOURCES,encoding='utf-8')
    status={'revision':'B','pages':14,'units':'mm','release':'development_dimension_and_integration_plan_only',
            'source_hashes':d.DATA['sources'],'board_step_sha256':FIT['board_step_sha256'],
            'envelope_intersections':FIT['intersections'],'back_shell_solids':5,
            'audio_holder_modelled':False,'usb_plug_insertion_verified':False,'physical_validation':False,
            'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest()}
    (OUT/'drawing_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(PDF)


if __name__=='__main__':main()
