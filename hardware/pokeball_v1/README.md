# Pocket Pet: druckbarer Gehäuseprototyp V1

Stand: 16.09.2026. Eigene Konstruktion für das vom Nutzer gewählte **Waveshare ESP32-S3-LCD-2**, ohne Kamera. Ein mechanischer Entwicklungsprototyp, kein nachgewiesen fertiges Elektronikgerät.

Die Druckdateien und die vollständige STEP-Baugruppe werden in `output/pokeball_v1` erzeugt. Das geprüfte V1-Druckpaket ist als [Pocket_Pet_V1_Druckpaket.zip](Pocket_Pet_V1_Druckpaket.zip) im Repository abgelegt. STL-Einheiten sind **Millimeter**, Skalierung im Slicer **100 %**. Jedes STL ist bereits einzeln in Drucklage orientiert. STEP-Einzelteile verwenden dagegen gemeinsame Montagekoordinaten. Die große STEP-Baugruppe nicht als zusammengewachsenes Teil drucken.

## Konstruktion

| Merkmal | V1 |
|---|---|
| Kugeldurchmesser | 100 mm |
| Geschlossene Höhe mit abgeflachten Polen | 90,6 mm |
| Gesamttiefe einschließlich Scharnier und Emblem | ca. 113 mm |
| Wand und Boden | 2,4 mm nominal |
| Spalt zwischen Hälften | 0,6 mm |
| Bedienplatte | herausnehmbar, 2,4 mm stark, vier Schrauben |
| Displayfenster | 31,2 × 41,4 mm |
| Tasten | drei Köpfe Ø9,5 mm; Abstand 16 mm; Führung Ø10,0 mm |
| Tastenflansch | Ø11,2 × 1,2 mm; verhindert Herausfallen nach oben |
| Scharnier | drei Knöchel, Ø3,4-mm-Bohrung für M3-Achse |
| Verschluss | M3-Schraube vorn; weißes Emblem ist Dekoration |
| Akkuaufnahme | innen 38 × 65 mm, abgerundete Ecken; unten freier Kabelweg |

Display, ESP32, Akku und drei Mikrotaster sitzen gemeinsam im Unterteil. Der Deckel schützt die Bedienfläche; durch das Scharnier laufen keine Kabel. Der Akku ist von der Platine getrennt und wird mit einem weichen Band gehalten. Unter dem Scharnier liegt ein großzügiger, zurückgesetzter USB-Zugang. Er ist kein bündiger USB-Panelausschnitt: Steckergehäuse und Biegeradius müssen am vorhandenen Kabel geprüft werden.

Die obere Hälfte lässt sich in der digitalen Kollisionsprüfung bis 130° öffnen. Es gibt keinen Rastmechanismus und keinen konstruierten 110°-Anschlag. Die Vorschau zeigt 110°. Die M3-Achse mit Scheiben und Mutter nur so einstellen, dass das Scharnier beweglich bleibt; eine dauerhaft selbsthaltende Deckelstellung ist nicht nachgewiesen.

## Tatsächliche Quellen und Annahmen

1. [Waveshare Produktdokumentation](https://docs.waveshare.com/ESP32-S3-LCD-2) und [offizielle CAD-/Zeichnungsdateien](https://files.waveshare.com/wiki/ESP32-S3-LCD-2/ESP32-S3-LCD-2-2Dand3D.rar), enthalten `ESP32-S3-LCD-2-20250122.stp` und `.pdf`. Am 16.09.2026 heruntergeladen, Zeichnung visuell geprüft und STEP gegen die Konstruktion geprüft. Die allgemeinen Webseiten enthalten widersprüchliche Textbausteine; maßgeblich für V1 ist diese konkrete mechanische Referenz.
2. Aus dieser Zeichnung: Platine 35,01 × 48,21 mm; Schraubraster 29,00 × 42,20 mm; vier M2-Aufnahmen H2,5; aktive Fläche 30,60 × 40,80 mm. Die Bauhöhe 8,20 mm schließt nicht die langen Stiftleisten ein. Das Hersteller-STEP reicht insgesamt etwa 14 mm tief; V1 berücksichtigt diese Stiftleisten. Das Board ist um 180° gedreht, USB zeigt zum Scharnier. Die passende Displayrotation ist spätere Firmwarearbeit.
3. [Omron B3F-Datenblatt](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf): **B3F-1000** als vorläufiger Tasterkandidat, 6 × 6 mm, Betätigungshöhe 4,3 ±0,2 mm. Drei Exemplare auf einer 43 × 12 × 1,6-mm-Trägerplatine. Die Anschlussbohrungen liegen im 6,5 × 4,5-mm-Raster; normales 2,54-mm-Lochraster passt nicht ohne Anpassung. Die beigelegte SVG zeigt das vorgesehene Bohrbild. Noch keine Bestellung oder elektrische Pinbelegung.
4. [Adafruit 258, geschützter 1S-Akku](https://www.adafruit.com/product/258) und [zugehöriges Datenblatt](https://cdn-shop.adafruit.com/datasheets/Li-poly%20503562-1200mAh.pdf): nur ein **Maßbeispiel**, keine verbindliche Akkuwahl. Shop nominal 34 × 62 × 5 mm, Datenblatt maximal 36 × 63 × 5,2 mm; die größere Hülle wurde geprüft. Der JST-PH-Anschluss dieses Beispiels passt **nicht direkt** zum MX1.25 des Waveshare. Passenden geschützten Akku, Polarität und zulässigen Ladestrom vor Anschluss festlegen. Kabel, Stecker und Schutzplatine des tatsächlich bestellten Akkus nachmessen. Keine Laufzeitbehauptung.
5. [Deine MakerWorld-Inspiration](https://makerworld.com/de/models/3169383-pokemon-tamagotchi-with-magsafe-charging): direkter Abruf weiterhin blockiert. Ein [Suchindex-Spiegel](https://3dgo.app/models/makerworld/3169383) beschreibt ein anderes 1,75-Zoll-AMOLED und Qi-Laden. Weder Quelldateien, Lizenz noch komplette Stückliste wurden verifiziert. Keine MakerWorld-Geometrie übernommen. V1 enthält kein Qi-Modul, keine MagSafe-Magnete und keinen Lautsprecherhalter, da dafür noch keine Bauteile festgelegt sind.

Die Herstellerdateien dienen lokal nur als Referenz und werden nicht im Druckpaket weiterverteilt. Alle gedruckten Formen wurden neu erzeugt.

## Teile und Druck

| Datei | Anzahl | Vorschlag / Drucklage |
|---|---:|---|
| `01_lower_shell.stl` | 1 | Weiß; flache Unterseite auf Bett; Stützen aktivieren |
| `02_lid.stl` | 1 | Rot; flacher äußerer Pol auf Bett; Stützen aktivieren |
| `03_control_deck.stl` | 1 | Schwarz; sichtbare Fläche auf Bett; lokale Stützen für Klemmstege prüfen |
| `04_board_carrier.stl` | 1 | flach auf Bett |
| `05_button_left.stl` | 1 | helle Taste, sichtbare Kopfseite auf Bett |
| `06_button_ok.stl` | 1 | wie links; runde Vertiefung zur Unterscheidung |
| `07_button_right.stl` | 1 | wie links |
| `08_switch_tray.stl` | 1 | Boden auf Bett, offene Lötseite nach unten durch Durchbruch |
| `09_battery_tray.stl` | 1 | Boden auf Bett |
| `10_front_emblem.stl` | 1 | Weiß; flach auf Bett, später an Deckelsteg kleben |
| `11_button_fit_coupon.stl` | optional 1 | drei Bohrungen Ø9,8 / 10,0 / 10,2 mm von links nach rechts |
| `12_hinge_fit_coupon.stl` | optional 1 | horizontale Ø3,4-mm-Bohrung wie beim Gehäuse |

**Zuerst drucken:** `05`, `11` und `12`. Taste muss in der mittleren Bohrung leicht gleiten; M3-Achse muss durch den Scharnierprüfkörper passen. Flansch passt absichtlich nicht durch die Bohrung. Drucktoleranzen am eigenen Drucker prüfen, nicht das komplette Gehäuse prozentual skalieren. Nach Bedarf Bohrungen vorsichtig entgraten oder die CAD-Führung anpassen.

Im ZIP liegen außerdem `START_Passproben.3mf`, `Platte_1_Schalen.3mf` und `Platte_2_Innenteile.3mf`. Dies sind neutrale Geometrieplatten **ohne Druckerprofil, Supports oder G-Code**. Im Slicer den eigenen Drucker, Material und Stützen einstellen. Die beiden Hauptplatten benötigen ungefähr 240 × 160 mm nutzbare Fläche einschließlich Randreserve; für kleinere Druckbetten die einzelnen STLs laden und neu anordnen.

Für den Prototyp: PLA, 0,4-mm-Düse, 0,20-mm-Schichten, vier Wände, 15 % Infill, ausreichend Deck-/Bodenschichten und 4-mm-Brim bei den Schalen. Automatische normale Stützen **auch im Modellinneren** zulassen; besonders Scharnieransätze, waagerechte Bohrungen und innere Schraubdome prüfen. Entfernbarkeit der Stützen nach dem Slicen kontrollieren. Kleine Tasten bei Bedarf mit Brim, aber ohne Stützreste in der Führung. PETG ist eine spätere Option für bewegte Teile, verlangt einen neuen Passversuch.

Der schwarze Äquator in der Vorschau ist eine **Farbgestaltung**, kein zusätzliches dünnes Steckteil. Optional die Randzonen schwarz lackieren oder im Slicer einfärben. Mit einfarbigen STLs entsteht die vollständige Geometrie auch ohne AMS. Die Visualisierung zeigt keine mitgelieferten Schrauben.

## Zusätzlich benötigte Teile

| Teil | Menge / Richtmaß |
|---|---|
| Waveshare ESP32-S3-LCD-2 | 1, mechanische Revision mit Zeichnung abgleichen |
| Omron B3F-1000 oder mechanisch identischer Taster | 3; abweichende Tasterhöhe braucht angepassten Stößel |
| FR4-Träger | 43 × 12 × 1,6 mm, selbst gebohrt, entgratet, keine fertige Schaltung |
| M3-Achsschraube | 1 × M3×45, zwei Scheiben, passende Mutter; alternativ glatter 3-mm-Stift mit eigener Sicherung |
| M3-Schrauben | 6 × M3×8 für Bedienplatte/Akkuhalter, 1 × M3×10 für vorderen Verschluss |
| M2-Schrauben | 4 × M2×4 in Board-Abstandshalter, 4 × M2×5 Träger an Bedienplatte, 2 × M2×6 Tastenträger |
| Weiches Akku-Halteband | ca. 10 mm breit; Länge am Aufbau bestimmen |
| Kabel und geschützter 1S-Akku | noch konkret festzulegen |

Schraubenlängen sind anhand der CAD-Schichtfolge gewählt und vor Einschrauben real prüfen. M2 im Board: 2-mm-Träger plus ca. 2 mm Gewindeeingriff; nicht mit längeren Schrauben gegen das Display drücken. Gedruckte Sacklöcher sind Kernlöcher (M3 etwa Ø2,5/2,6, M2 Ø2,1), keine modellierten Gewinde. Vorsichtig passend nachschneiden; keine großen Schrauben gewaltsam eintreiben. Für häufige Wartung wären Gewindeeinsätze eine gezielte V2-Änderung.

## Montagefolge

1. Passproben prüfen. Alle Bauteile entgraten und sämtliche Stützen entfernen, insbesondere aus Führungen und Scharnier.
2. Akkuhalter mit zwei M3×8 am unteren Gehäuse befestigen. Zunächst mit einem **nichtleitenden Maßdummy** testen. Halteband durch die seitlichen Schlitze; tatsächliche Zelle später ohne Druck auf Folie, scharfe Kanten oder Lötstellen einsetzen.
3. Drei Tasten von der Unterseite in die Bedienplatte stecken. Die Flansche bleiben innen.
4. Drei Taster auf der gebohrten FR4-Platine bei x=-16/0/+16 mm montieren. Anschlüsse unterseitig verdrahten; Kontakte nach Datenblatt oder Durchgangsprüfung zuordnen. Der offene Tastenträger lässt Platz für Lötstellen. Platine in dessen Randführung einlegen und Träger mit zwei M2×6 an die Bedienplatte schrauben. Zwei Stege halten die Platine nach oben; sie darf nicht hochstehen. Alle Tasten müssen einzeln zurückfedern. Nominal 0,2 mm Abstand zwischen Stößel und unbelastetem Schalter; reale Toleranzen können eine Anpassung verlangen.
5. Waveshare-Board auf den separaten Boardträger setzen; vier M2×4 in die bestehenden Aufnahmen. USB zeigt zum Scharnier. Träger mit vier M2×5 unter der Bedienplatte befestigen. Frontscheibe darf nicht verspannt werden; keine Schraube darf an Display oder Flexkabel anstoßen.
6. Erst ohne Akku den kompletten Einsatz in die Unterschale setzen, Kabelwege prüfen, mit vier M3×8 verschrauben. USB-Stecker real einstecken und wieder abziehen. Die hintere Aussparung ermöglicht Sicht auf den zurückliegenden Anschluss.
7. Deckel und untere Scharnierknöchel ineinanderlegen. M3×45 seitlich durchschieben, Scheiben und Mutter montieren. Deckel öffnen und schließen; Achse nicht mit Gewalt verspannen.
8. Emblem ausschließlich an den kleinen vorderen **Deckelsteg** kleben. Nicht mit der unteren Verschlusslasche verkleben. Der Verschluss erfolgt durch die zugängliche M3×10 von oben; zum Öffnen lösen. Das ist bewusst ein einfacher Prototypverschluss.

## Prüfung und Grenzen

`validation.json` enthält die tatsächlichen Prüfergebnisse des jeweiligen Exports: gültige CAD-Volumen, STL-Wasserdichtheit/Orientierung/Anzahl zusammenhängender Körper, Paarüberschneidungen, Deckelbewegung in 5°-Schritten, offizielle Boardgeometrie, Akku-Maximalhülle, Tasterplatine und 0…0,6-mm-Tastenbewegung. Die Bewegungsprüfung ist eine diskrete Stichprobe, keine kontinuierliche mathematische Kollisionsgarantie.

Die zusätzliche Slicerprüfung verwendet lokal Bambu Studio 2.6.0.51 mit **A1 / 0,4 mm / Generic PLA / 0,20 mm**, vier Wänden, 15 % Infill und automatischen Stützen. Das ist eine definierte Vergleichskonfiguration, keine Festlegung deines Druckers. Maßgeblich sind die mitgelieferten STL-Dateien und erneutes Slicen für den eigenen Drucker; kein Druck wurde gestartet. `slicer_summary.json` enthält Zeiten, Material und Warnungen. G-Code wird nicht ins allgemeine Druckpaket aufgenommen.

Offen bleiben reale Druckpassung, Stützenentfernung, Schraubhalt, Dauerhaltbarkeit, Schaltergefühl, USB-Kabelzugang, Antennen-/Funkverhalten, Akku-/Ladefreigabe und elektrischer Aufbau. Kein MagSafe/Qi- oder Firmware-Funktionsnachweis. Spielelogik und GPIO-Zuordnung wurden durch diese Konstruktion nicht geändert.

## Reproduzieren / weiterentwickeln

```powershell
python -m venv .tools/cad-venv
.tools/cad-venv/Scripts/python.exe -m pip install -r hardware/pokeball_v1/requirements.txt
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v1/build.py
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v1/verify.py
.tools/cad-venv/Scripts/python.exe hardware/pokeball_v1/render.py
```

`verify.py` erwartet das oben verlinkte offizielle STEP unter `output/cad-research/ESP32-S3-LCD-2-20250122.stp` und bricht bei fehlender Referenz ab. Für die optionale Slicerprüfung `slice_check.py --studio <Pfad zur bambu-studio.exe>` verwenden. `package.py` bündelt Exporte, Dokumentation und Quellen. CAD-Pakete sind ausschließlich Entwicklungswerkzeuge; der Simulator bekommt keine neue Abhängigkeit.

`build.py` ist die bearbeitbare parametrische Quelle. Änderungen an Gehäusedurchmesser, Platine oder Tasterhöhe müssen mit der gesamten Baugruppe neu geprüft werden; nicht alle unabhängigen Montagekoordinaten skalieren automatisch mit. STEP kann in CAD-Systeme importiert werden, STL direkt in Bambu Studio/PrusaSlicer/OrcaSlicer oder Blender.
