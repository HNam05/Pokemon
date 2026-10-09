# Pocket Pet V2: technischer Maßplan

## Aktuelle Übersicht: Revision C, ein isometrisches A1-Blatt

Auf Nutzerwunsch 08.10.2026 sind Gehäuse, Innenaufbau, technische Komponenten,
Maße in mm, Einbaulagen und Befestigung nun gemeinsam auf einem A1-Blatt
zusammengefasst: `output/pdf/pocket_pet_technical_rev_c/Pocket_Pet_V2_RevC_Isometrische_Gesamtzeichnung.pdf`.
Die früheren Revisionen A/B bleiben erhalten. Die folgenden älteren Abschnitte
dokumentieren deren eigenen Umfang.

Revision C verwendet echte orthografische CAD-Isometrien: Zusammenbau,
Explosionsansicht und alle 15 Druckteile. Elektronikmodelle sind entweder
originales Hersteller-STEP oder ausdrücklich bezeichnete Maßhüllen.
Die öffentlichen ISO-Beschreibungen 5456-3, 129-1 und 128-3 wurden online
recherchiert; keine vollständige Normkonformität behauptet.

Neue Generatoren: `render_isometric.py` (vorhandene CAD-venv),
`draw_isometric.py` (ReportLab), `verify_isometric.py` (pypdf).
Der gemeinsame A3-Zeichnungshelfer unterstützt jetzt variable Seitengrößen;
seine Standardgröße bleibt A3. Bestehende CAD-/Spielquellen unverändert.

Geprüft: eine A1-PDF-Seite, 24 echte Isometrien mit gleicher Achsprojektion,
15 analytische CAD-Teilhüllen identisch zur Originalreferenz, vollständige
Positionsnummern, 38 Stücklistenpositionen, neun klickbare Quellenlinks,
SVG-XML, Textlayout ohne Überlappung und ZIP-Integrität. Das komplette Blatt
und vier Detailregionen wurden gerendert und visuell geprüft. Der begrenzte
92-Paar-Elektronikhüllenbericht aus B ist bei identischen Quellhashes lediglich
als Referenz übernommen; keine neue vollständige Montageprüfung.

P05 weiterhin fünf Körper; Audiohalter/Schallöffnung, aktuelle Amp-Lieferhöhe,
USB-Steckerzugang und physische Passung bleiben offen und stehen direkt auf
dem Blatt. Keine Fertigungsfreigabe. Ausgabe enthält PDF, eigenständiges SVG,
CSV-Stückliste, Quellen und Prüfprovenienz in einem ZIP.

Stand 08.10.2026, Revision A. Herausnehmbarer Handheld in einer aufklappbaren Pokéball-Außenhülle, entsprechend der später präzisierten Produktarchitektur.

Ausgabe: `output/pdf/pocket_pet_technical/Pocket_Pet_V2_Technische_Zeichnungen.pdf`, acht A3-Querformatseiten, acht bearbeitbare SVG-Blätter und eine CSV-Stückliste für ein bzw. zwei Geräte. PDF/SVG bei tatsächlicher Größe/100 % drucken. Alle Maße in Millimeter. Der Plan dokumentiert den vorhandenen V2-Entwurf, ohne dessen CAD zu verändern.

## Zeichnungsumfang

1. Gesamtaufbau, Front-/Prinzipsicht und Hüllmaße.
2. Handheld-Front/Rückschale, Fenster, Schrauben- und Tastenkoordinaten.
3. Waveshare-Modulreferenz und Boardträger.
4. Tastenkappen, Tasterplatinen-Bohrbild und Tastenträger.
5. Handheld-Halterung im Ball und Akkuhalter.
6. Ballhälften, Scharnier, Verschluss, Emblem und Passproben.
7. Druckteil-/Montagestückliste.
8. Elektronikstückliste, Quellen und offene Bauteilwahl.

## Geprüfter Stand und Grenzen

- CAD-Sollmaße direkt aus den bestehenden CadQuery-Quellen; sichtbare Einzelteilkanten mit OCCT-Projektion gewonnen. Quellhashes und Geometrie in `geometry_reference.json`.
- Handheld-Gehäuse 62 × 90 × 31,4 mm; inklusive hervorstehender Tasten 33,2 mm tief. Kugel Ø130; komplette geschlossene Hülle mit Emblem/Scharnier 130 × 142,55 × 118,6 mm.
- Der aktuelle CAD-Rückschalenentwurf P05 besteht aus fünf getrennten Körpern. Die bisherige V2-Validierung enthält lediglich vier Meshes. Damit liegt keine vollständige V2-Fertigungsfreigabe vor. CAD-Verbindungen und Gesamtmontage sind vor einem Drucksatz zu reparieren/prüfen.
- V2-Akkuhalterschraube vorläufig M3×6: aus Halterboden 2 mm und 4 mm Einschraubweg abgeleitet; V1-M3×8 kann an der flachen V2-Rückwand durchstoßen. Physisch nicht geprüft.
- Akku, Lautsprecher, Verstärker, optionaler Power-Schalter sowie Kabellängen sind nicht endgültig festgelegt. Nicht bekannte Einbaumaße bleiben ausdrücklich offen. Kein Lautsprecherhalter oder elektrische GPIO-Zuordnung erfunden.
- Alle acht PDF-Seiten gerendert und visuell geprüft; A3-Seitenformat, Seitenzahl, SVG-XML und Stücklisten geprüft. Keine CAD-Reparatur, kein Druck, kein Hardware-Funktionstest.

## Herstellerreferenzen

- [Waveshare Dokumentation](https://docs.waveshare.com/ESP32-S3-LCD-2), [offizielle 2D-/3D-Dateien](https://files.waveshare.com/wiki/ESP32-S3-LCD-2/ESP32-S3-LCD-2-2Dand3D.rar): lokal vorhandene mechanische Referenz `ESP32-S3-LCD-2-20250122.pdf/.stp`. Referenzzeichnung visuell geprüft, vollständige STEP-Hülle in dieser Runde ausgelesen. Hersteller-Webseite nennt MX1.25. Revision am realen Board abgleichen.
- [Omron B3F-Datenblatt](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf): B3F-1000 als vorläufiger Taster, 6 × 6 mm, Betätigungshöhe 4,3 ±0,2 mm; PCB-Bohrbild 6,5 ±0,1 × 4,5 ±0,1, vier Bohrungen Ø1 ±0,1 je Taster.
- [Adafruit 258](https://www.adafruit.com/product/258), [503562-Datenblatt](https://cdn-shop.adafruit.com/datasheets/Li-poly%20503562-1200mAh.pdf): bereits verwendetes Größenbeispiel, keine verbindliche Zellauswahl; dessen JST-PH passt nicht direkt zum Boardanschluss.

## Reproduzieren

`collect_geometry.py` mit dem bestehenden `.tools/cad-venv/Scripts/python.exe` ausführen. Danach `draw.py` mit Python plus ReportLab starten. Kein neues Paket im Spielruntime nötig. PDF und SVG verwenden dieselben Zeichnungsprimitive. Ausgabe und Vorschaubilder bleiben außerhalb von Git.

## Revision B / Elektronik und Montage

Nutzerauftrag 08.10.2026: mehr Details zum tatsächlichen Innenaufbau, Bauteilwahl, Befestigung und Anschlüssen. Hardware ist ausdrücklich noch nicht bestellt. Revision A bleibt erhalten.

Ausgabe: `output/pdf/pocket_pet_technical_rev_b/Pocket_Pet_V2_RevB_Einbau_und_Montage.pdf`, 14 A3-Seiten, einzelne SVG-Blätter, CSV-Stückliste für Dat/Jennie, Quellen und begrenzter CAD-Hüllenprüfbericht. PDF/SVG bleiben vektorbasiert; die Herstellerlinks in Blatt 8 sind im PDF anklickbar.

Zusätzlich zu den Einzelteilzeichnungen: farbige Einbaulagen, ein lokales positives X/Y/Z-Bezugssystem, Hüllenprojektion der Schichten, Schraubentabelle einschließlich effektiver Sacklochtiefen und Einschraubweg, USB-Korridor/Adapter-/Kabelraum, Audioeinbauraum und Montagefolge. Hüllenprojektionen und Explosionsprinzip sind ausdrücklich keine echten CAD-Schnitte bzw. maßstäbliche Explosion.

Konkrete Vorschläge: vorhandenes Waveshare ESP32-S3-LCD-2, drei Omron B3F-1000 auf eigener FR4-Platine, Adafruit 258/LP-503562 mit PCM, Speaker Adafruit 3923 und MAX98357A Adafruit 3006. Zusatz-Ladeplatine ist beim gewählten Modul nicht vorgesehen. Akkuadapter nötig: JST-PH passt nicht direkt zu MX1.25. Herstellermaße, CAD-Sollmaße, reservierte Zubehörhüllen und offene Maße sind getrennt gekennzeichnet.

`inspect_integration.py` mit CadQuery ausführen, danach `draw_integration.py` mit ReportLab. Die digitalen Prüfungen verwenden das vollständige offizielle Board-STEP, Akku-Prüfhülle, FR4, konservative Tasterkörper und Audiohüllen. Speaker und Amp sitzen jetzt bei CAD-Y=-26 / lokal Y=17, mit 2,8 mm XY-Abstand. Kein Schnittvolumen gegen vorhandene Handheld-Teile oder die übrigen Elektronikhüllen. Quellhashes und Prüfumfang stehen im Bericht. Die 3-mm-Amp-Prüfung gilt nur ohne Schraubklemme/Pinleiste; das aktuelle Lieferteil ist damit nicht vollständig geprüft.

Offen: P05 verbinden, Audiohalter und Schallöffnung modellieren, tiefliegende USB-Buchse und reale Stecker prüfen, Kabel/Lötstellen/Schraubköpfe ergänzen, vollständige Baugruppen-/Bewegungsprüfung und reale Pass-/Elektroprüfung. Der Satz ist ein präziserer Entwicklungsplan, keine Fertigungsfreigabe. Es wurden keine bestehenden CAD- oder Softwarefunktionen geändert.
