# Pocket Pet V2: Handheld zum Herausnehmen

Das Tamagotchi ist ein eigenes Handheld. Die geoeffnete Pokeball-Huelle dient als Transport- und Schutzgehaeuse; sie ist beim Spielen abnehmbar. V1 bleibt unter `hardware/pokeball_v1` als frueher Entwurf erhalten.

Ausgelegt auf das vom Nutzer gewaehlte **Waveshare ESP32-S3-LCD-2**: rechteckiges 2-Zoll-Display, Board 35,01 x 48,21 mm, aktive Flaeche 30,60 x 40,80 mm und 29 x 42,2 mm M2-Schraubraster nach der offiziellen Herstellerreferenz. Das Board ist um 180 Grad gedreht; USB zeigt zum oberen/rear Ende des Handhelds. Das Gehaeuse ist dafuer etwa 62 x 90 x 33 mm inklusive Tasten. Die Schutzhuelle hat etwa 130 mm Kugeldurchmesser.

Die lockere Aufnahme traegt das Handheld an Rueckenschienen und Querstegen. Zwei 10-mm-Textilbaender laufen durch Oeffnungen der Seitenwaende und halten das Geraet bei geschlossenem Ball. Ein Band sitzt oberhalb der Displayflaeche, unterhalb der Randkante. Zum Spielen die Baender loesen und das ganze Geraet nach oben aus der Aufnahme heben. Sie muessen reale Abstaende zu Display, USB-Kabel und Verschluss erst nach dem Probieren erhalten. Das Band nicht ueber Display oder Tasten spannen.

## Dateien

Der versionierte Download liegt in `hardware/pokeball_v2/release/`: STL-Einzelteile in `STL_print/`, STEP-Einzelteile in `STEP_parts/`, drei neutrale 3MF-Druckplatten, CAD-Baugruppe, Handheld-STEP, Vorschau und Pruefbericht. Die neutralen Platten enthalten keine Druckerprofile oder G-Code. `output/pokeball_v2/` ist nur der lokale, ignorierte Arbeitsausgang des Generators.

| STL-Präfix | Menge | Teil |
|---|---:|---|
| 01 | 1 | Untere Pokéball-Haelfte |
| 02 | 1 | Pokéball-Deckel |
| 03 | 1 | Herausnehmbare Aufnahme mit Bandfuehrungen |
| 04 | 1 | Handheld-Front mit Displayausschnitt und drei Tasten |
| 05 | 1 | Rueckdeckel des Handhelds |
| 06 | 1 | Boardtraeger |
| 07-09 | je 1 | Links-, OK- und Rechts-Taste |
| 10 | 1 | Träger fuer Tasterplatine |
| 11 | 1 | Akkuhalter |
| 12 | 1 | Emblem des Pokéballs |
| 13 | optional 1 | Tasten-Passprobe |
| 14 | optional 1 | Horizontale Scharnier-Passprobe |
| 15 | optional 1 | Aufnahme-/Breiten-Passprobe |

## Passform und Montage

Erst die Teile 13, 14 und 15 drucken. Taster und Scharnierbohrung wie in V1 pruefen; Teil 15 prueft das Gehaeuse an den Seitenfuehrungen. Nicht die Gesamtkonstruktion prozentual skalieren.

Das Handheld verschraubt Front und Rueckdeckel mit vier M2-Schrauben bei X=±26 mm und Y=±13 mm. Die vier Ruecklocher sind fuer Senkkopf M2 ausgelegt; die Rueckseite liegt spaeter an der Aufnahme an. Gewindekernloch in gedrucktem Boss ist Ø1,6 mm und muss nach erster Passprobe gegebenenfalls manuell kalibriert werden. Keine groessere Schraube gewaltsam eindrehen. Bei wiederholtem Oeffnen Gewindeeinsaetze in einer Folgerevision vorsehen.

Das Board wird auf dem Boardtraeger an vier vorhandenen M2-Halterungen befestigt. Vier weitere M2-Schrauben verbinden Traeger und Handheld-Front. Tastentraeger und Akkuhalter entsprechen der separat dokumentierten V1-Aufnahme. Die 43 x 12 x 1,6-mm-FR4-Tasterplatine wird nach `hardware/pokeball_v1/README.md` gebohrt. Normales 2,54-mm-Lochraster passt nicht ohne Anpassung zum 6,5 x 4,5-mm-Pinraster der Omron B3F Taster.

Die Aufnahme wird mit vier M3-Senkkopfschrauben an den unteren Domen des Balls befestigt. Das Handheld soll auf den Querstegen sitzen und an vier Seiten etwa 1 mm Spiel haben. Textile Baender durch die seitlichen Schlitze faedeln, auf der Unterseite sichern und erst nach der Probemontage auf passende Laenge bringen. Baender muessen sich zum Herausnehmen ohne Werkzeug loesen lassen. Unten darf kein Band die USB-Buchse oder das Scharnier blockieren.

M3x45-Achse, Unterlegscheiben und Mutter durch die alternierenden Scharnierknuechel. Der vordere M3-Schraubverschluss sichert den Ball; das weisse Emblem ist nur Dekoration. Beide Hälften sind noch ein Montageprototyp, keine validierte Rast- oder Dauerhaltekonstruktion.

## Druck und Dateien generieren

0,20 mm Schichthoehe, 0,4-mm-Duese, PLA, vier Waende, 15 Prozent Infill, automatische normale Stuetzen auch innerhalb der Schaelen. Ball- und Handheldhaelften sind einzeln orientiert. Lange waagrechte Scharnierbohrungen vor dem Druck im eigenen Slicer ansehen; Durchmesser nach der horizontalen Passprobe einstellen. Erzeugte 3MF-Platten enthalten Geometrie und Objektnamen; kein Druckerprofil oder G-Code.

```powershell
python -m venv .tools/cad-venv
.tools/cad-venv/Scripts/python.exe -m pip install -r hardware/pokeball_v1/requirements.txt
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v2/build.py
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v2/verify.py
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v2/render.py
```

Zum Erzeugen der zusaetzlichen Release-Druckplatten nach erfolgreicher Validierung `python hardware/pokeball_v2/package_release.py` ausfuehren. Diese Datei kopiert die verifizierten Modelle in den versionierbaren Release-Ordner und legt daraus neutrale 3MF-Platten an.

Optionales Bambu-Slicer-Profil zum Slicen ist unter V1 dokumentiert. CAD-Quelle: `build.py`; Winkel, Halter, Spalte und Bauteillage vor einer Komponenten-/Gehaeuseaenderung kontrollieren.

## Digital geprueft; physisch offen

Der V2-Pruefbericht kontrolliert gueltige zusammenhaengende Volumen und wasserdichte STL, jede Teilepaarung, Displayboard, Akku-Maximalhuelle, Drei-Tasten-Hub, Deckelbewegung von 0 bis 130 Grad in 5-Grad-Schritten sowie die Herausziehbewegung des Handhelds in 12 mm-Schritten. Diese endlichen digitalen Stichproben beweisen keinen physischen Druck oder eine lueckenlose kontinuierliche Bewegung.

Noch zu pruefen: reale Loetstellen/Pinleisten, Kabelweg und USB-Stecker, Tastenfederung, Akku/Schutz und Ladefreigabe, Schraubenlaengen, Bandzug, Deckelanschlag, reale Drucktoleranzen, Innenantennen und Displaykontakt. Herstellerakku aus der V1-Stueckliste hat einen anderen Stecker als das Waveshare-Board. Erst Passproben und dann ein einfarbiger Funktionsprototyp drucken. Kein MagSafe/Qi, kein Lautsprecherhalter und keine Firmware-Aussage in V2.
