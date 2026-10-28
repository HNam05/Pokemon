Original prompt: Ein eigenes Pokemon-Tamagotchi fuer ESP32 im aufklappbaren, 3D-gedruckten Pokeball bauen. Zuerst online recherchieren, dann Software in C++ von Grund auf implementieren und auf dem PC simulieren. Normales Display und drei Tasten, Akku; Hardware noch nicht bestellt. Eigener Branch und nachvollziehbare Commits fuer Zusammenarbeit mit einem zweiten Rechner und Anthropic-Modellen.

## 2026-09-14 / OpenAI Codex

- Ausgangspunkt: nur README, sauberer main, origin HNam05/Pokemon.
- Branch: codex/2026-09-14-desktop-pet-foundation.
- Recherche: Bandai Original-Handbuch, Nintendo Pokemon Refresh, Waveshare Board-Wiki, Espressif NVS und Systemzeit. MakerWorld nicht auslesbar.
- Entscheidung: portabler C++17-Kern, Python-Standardbibliothek als lokale Desktop-Bruecke, Browser-Canvas als Display. Keine zweite Spielsimulation in JavaScript.
- Gestaltung: warmes Papier, Zinnoberrot und ein kontrastreiches Pixel-Spielfeld. Spielanzeige zuerst, daneben Bedienung und Simulator-Zeit. Bewegung nur fuer lebendiges Pet und Minispiel.
- Hardwaretreiber erst nach Board-Auswahl. Keine ungeprueften GPIOs aus den Bildern.

### Fertiger M1-Stand

- Portabler C++17-Kern implementiert: Pflege, Zeit, Ei/Evoli, Psiana/Nachtara, Behandlung, Drei-Tasten-Menue und Beerenfang.
- Versionierter 42-Byte-Spielstand mit CRC und strenger Wertepruefung; C ABI und Python-Loopback-Server. Atomare Speicherung, Datei-Sperre, Offline-Limit und sichtbare Fehler.
- Browser-Simulator mit 240x320-Canvas, selbst gezeichnetem Pixel-Platzhalter, Tastatur/Maus, Status, Mobilansicht und Vollbild.
- Lokaler offizieller Zig 0.15.2 Windows x64 nach SHA-256-Pruefung in ignoriertem .tools-Verzeichnis. Kein globaler Compiler installiert. Kein Grafik-/Python-Laufzeitpaket fuer das Spiel erforderlich.
- Geprueft: C++-Release-Build ohne Warnungen; 20.115 Checks (inklusive 20.000 randomisierter Zustandsinvarianten), 11 Python-Tests, Playwright-Spielablauf und Skill-Testclient. Unabhaengige Python-Referenz fuer binaeres Saveformat und CRC.
- Browser-Screenshots von Home/Ei/Evoli, Menue, Status, Fangspiel, Ergebnis, Mobilansicht und Vollbild unter output/. Visuell kontrolliert, keine Konsolenfehler.
- Gefundene und behobene Probleme: Fangbereich an tatsaechliches Timing angepasst; Tastatur nach Klick auf Geraetetasten; Pause nach langem Host-Suspend; Vollbild-Steuerelemente; Mehrfachzugriff auf Save-Datei.
- AGENTS.md, Quellen, Architektur, Build-/Testanleitung und Modell-/Git-Konventionen hinzugefuegt.

### Naechste Schritte fuer beide Rechner

1. Auf zweitem Rechner bauen und testen. Browser ist nur Renderer; Regeln weiter ausschliesslich in C++ pflegen.
2. Einige echte Tage spielen und Pflege-/Entwicklungsschwellen beurteilen. „+10 Minuten“ und Zeitraffer sind reine Simulatorhilfen.
3. Board und Display samt Revision/Schaltplan festlegen; Pins, Einbauraum, Akku und Stromstrategie klaeren.
4. ESP-IDF-Projekt mit Display-, Button-, Zeit- und NVS-Adaptern bauen. Das vorhandene firmware/components/pet_core ist nur eine Component-Einbindung, noch keine Firmware.
5. Pixel-Sprites/Animationen verbessern und weitere Arten erst danach ergaenzen.

Offen: echter ESP32-Build/Flash, Hardwaretests, CMake/MSVC und andere Betriebssysteme. MakerWorld-Inhalt blieb nicht auslesbar. Keine Bestellung, kein Gehaeusemodell und keine ungeprueften Pin-Zuordnungen erstellt.

## 14.–15.09.2026 / OpenAI Codex / M2

- Nutzerwunsch: universelle Seitentasten, vertikales Scrollen, Enton, persoenliche Texte fuer zwei Geschenkgeraete, witzige Spiele, Audio spaeter und geringe Speichernutzung.
- Branch: codex/2026-09-14-enton-three-button-ux, aufgebaut auf cac3bc3.
- Zehn Menueeintraege mit fuenf sichtbaren Zeilen, kontextabhaengige Tastenlegende, kurze Effekthinweise und Pflegehilfe. OK bestaetigt beim Loslassen; 700 ms Halten fuehrt einmal zurueck.
- Startauswahl Evoli/Enton und eigenes 32x32-Enton-Pixelbild. Alle Sprite-Daten zentral in C++, 4 Bit pro Pixel/RGB565-Palette, insgesamt 908 Bytes.
- Entons Denkpause als zweites kurzes Spiel mit drei Zeichen und drei Runden. Abbruch ohne Gewinn, normale Reaktionszeit auch im Zeitraffer.
- Zwei lokale persoenliche Profile konfiguriert. Namen und Profildateien sind absichtlich nicht in Git. Neutraler Beispiel-Config und portable Anleitung fuer den zweiten Rechner.
- V2-Spielstand 44 Byte, strikte Migration aus V1 mit erhaltener Art und Pflege. Der echte V1-Stand wurde vor dem Update lokal gesichert. Profile bleiben vom Save getrennt.
- Gemessene Hostgroessen: Game 64 Byte (State 32 darin enthalten), Profile 25 Byte; keine Behauptung des gesamten ESP32-Verbrauchs.
- Audio bleibt dokumentierte naechste Hardwareintegration, keine ungenutzten Audiodateien oder Schein-Treiber angelegt.
- Abschlusspruefung: warning-clean Release-Build, 22.907 C++-Checks, 14 Python-Tests, Browser-Spielablaeufe fuer beide Starter und beide Minispiele bestanden. Long-OK per Tastatur und Maus, Scrollen, Profiltext, Vollbild und Mobilansicht geprueft. Keine Browserfehler. Screenshots kontrolliert; sie bleiben unter output/.

Naechster Entwicklungsschritt: echtes Board festlegen und GPIO-/LCD-/NVS-Adapter integrieren. Danach Pixelanimationen und Sound. Pflegebalance durch Spielen im Alltag beurteilen. Die beiden persoenlichen Konfigurationsdateien muessen bei einem Rechnerwechsel lokal uebertragen oder neu angelegt werden.

## 15.09.2026 / OpenAI Codex / M3 Animationen

- Auftrag: online nach offenen Pixel-Animationsquellen suchen, geeignete Pokémon-Bilder übernehmen und spontane, zum Zustand passende Bewegungen implementieren.
- Branch codex/2026-09-15-pokemon-animations, Basis 3d08c53. SpriteCollab, PokeAPI, Showdown und weitere Fanquellen geprüft. Konkrete Evoli-Alternate-Variante von Emmuffin übernommen: CC BY-NC, gepinnter Commit, Credits, Lizenztext und Quellhashes. Keine Chunsoft-Sprites übernommen; Enton erhält eigene prozedurale Augen-, Schnabel- und Fußposen.
- Kosmetischer C++-Animator mit separatem PRNG: Ruhepausen, Gehen, Umsehen, Hüpfen, Freude; Schlaf/Krankheit/Erschöpfung priorisiert, Hunger unterdrückt Jubel; Füttern löst Essen aus. Kein Eingriff in Pflegewerte oder das 44-Byte-Saveformat.
- Offline-Importer: 38 Evoli-Frames auf 19 einzigartige Bitmaps reduziert, transparente Ränder mit Registrierung erhalten, 4-Bit-Palette/RGB565. Original-PNGs/XML nur Entwicklungsquellen, kein Bilddecoder auf Hardware nötig.
- Browser zeichnet vorgeladene Canvas-Bitmaps; C++ liefert Clip/Frame/Position. Reduzierte Bewegung mit ruhigem Zustandsbild. Sprunghöhe für die kleine Anzeige korrigiert, Framegrenzen im Browser geprüft.
- Host-Datengrößen: Animator 20 Byte; zusätzliche Assets samt Host-Tabellen 8.819 Byte, zusätzlich zu bisherigen 908 Byte. Keine ESP32-Gesamtspeicherbehauptung.
- Bestanden: Zig-Release-Build, 121.168 C++-Checks, 15 Python-Tests, bestehende Browserflows beider Starter, neuer 70-Sekunden-Animationsablauf je Art, Quellhash-/Generierungsprüfung, unabhängiger Vergleich aller 59.200 Quellpixel.
- Screenshots: Schlaf, Freude, Essen, Umsehen, Gehen und Sprung kontrolliert. Spielstände vor Austausch der laufenden DLL gesichert.
- Abschließender Develop-Web-Game-Skill-Client mit drei Sequenzen bestanden; Screenshots und Textzustand kontrolliert, keine Browserfehler.
- Offen: eigener hochwertiger Enton-Animationssatz mit klarer Freigabe, seitliche Laufansichten, eigenständige Frames für Psiana/Nachtara, LCD-/GPIO-/Audioadapter, physische Hardwareprüfung. Lizenzhinweis bei Geräteweitergabe beilegen; Details in assets/README.md und docs/ANIMATION.md.

## 15.09.2026 / OpenAI Codex / M4 Gesamter SpriteCollab-Fankatalog

- Auftrag präzisiert: alle geeigneten Künstler aus SpriteCollab, nicht nur Emmuffin. Branch `codex/2026-09-15-expanded-roster`, Basis b8be91e.
- Gepinnter Katalog vollständig auditiert; 210 detailliert geprüfte Fan-Kandidaten, davon 129 geeignet. 85 Pokémon in 129 Sets plus eigener Enton ergeben 130 Starter. Kriterien: vollständiger Upstream-Status, mindestens 25 Aktionen, neun Pflegeclips, mindestens 35 Frames, Walk/Hop >=4 und Sleep >=2; keine CHUNSOFT-/Mischcredits, keine unbekannten Bedingungen. Ausschlüsse vollständig in assets/roster.json.
- Quell-PNGs/XML/Credits mit SHA-256 übernommen; historische PMDCollab_1/PMDCollab_2/CC_BY-NC_4-Texte beigelegt. Frühere pauschale CC-Zuordnung für Evoli präzisiert. Künstler je Set im UI und generiertem ROSTER.md genannt.
- 5.470 Frames auf 2.455 einzigartige Bitmaps reduziert. Alle 129 Sets vier Bit pro Pixel, 770.930 Byte Pixel/Paletten. Mit Host-Tabellen und Enton-Posen 974.322 Byte; Game/State/Profile/Animator unverändert 64/32/25/20 Byte. Texte und Firmwaregesamtbedarf nicht darin enthalten.
- C++-Katalog verwaltet Namen, Formen, IDs, Auswahl und Animationen. Drei-Tasten-Vertrag bleibt vollständig. Seitentasten halten blättert durch Auswahl/Menü. Browser/Server laden einzelne Sets bei Bedarf, maximal vier zusätzliche Sets im Cache. Neue Arten nutzen dieselben Pflegeregeln, keine erfundenen Entwicklungsketten.
- V3 behält das 44-Byte-Layout und erweitert die gültigen Art-IDs; V1/V2-Migration ohne Zurücksetzen. Bestehende IDs nie ändern oder neu vergeben. Beide privaten Spielstände vor Update lokal gesichert.
- Alle Frameausdehnungen geprüft; Evolis Anker auf Y=152 korrigiert, damit Sitz-/Müdigkeitspose nicht unten abgeschnitten wird.
- Bestanden: warning-clean Build mit 3.492.014 C++-Checks, 17 Python-Tests, reproduzierbarer Import, unabhängiger Vergleich von 12.146.208 Quellpixeln. Browser: alle 130 Starter, Auswahl durch Halten, Schlüpfen, Animation, Save/Reload, Cachegrenzen, Mobilansicht und HTTP-Grenzen. Bisherige Pflege- und Animations-Smokes beider ursprünglicher Starter ebenfalls bestanden.
- Alle sechs Auswahl-Kontaktübersichten und Mobilansicht visuell geprüft. Drei Sequenzen mit dem originalen Skill-Client bestanden; Canvas/Textzustand geprüft, keine Browserfehler.
- Nächste Schritte: flüssige Seitenansichten, eigenständige hochwertige Enton-/Entwicklungssets, gegebenenfalls Lieblingsbegleiter für die zwei Geräte eingrenzen. Board festlegen, echtes Flash-/RAM-Budget und LCD-/GPIO-/NVS-/Audioadapter auf Hardware prüfen. Der komplette Katalog erhöht konstanten Speicher deutlich; vor Firmwareauslieferung Boardbudget messen.

- Abschlussvorschau: beide persönlichen Instanzen auf 8765/8767 mit vorhandenen Tieren und ohne Speicherfehler gestartet. Separate neutrale Auswahl unter 8768 mit eigenem ignoriertem output-Spielstand; 130 Katalogeinträge auf allen Instanzen bestätigt. Lokale Profile/Sicherungen bleiben außerhalb von Git.

## 15.09.2026 / OpenAI Codex / M5 Größere Pokémon und Naturkulisse

- Wunsch: Pokémon größer im Vordergrund, besseres Pixelartwork mit Pokémon-/Naturthema. Branch codex/2026-09-15-pixel-nature-scene, Basis b5b89f1.
- Waldlichtung mit Bäumen, Bach, Beeren und Pokéball-Wegschild per eingebautem OpenAI Imagegen erstellt. Unveränderte Quelle, technische Displayfassung und vollständiger Prompt unter assets/backgrounds/ dokumentiert. Keine heruntergeladenen Fremdhintergründe.
- Offline-Import nach 240×178, 16 Farben, 4 Bit/RGB565; Tag/Nacht teilen Pixelbestand. 21.424 Byte einschließlich beider Paletten. Gemeinsame C++-Daten, keine Python-/JS-Spielregeln oder Bilddecoder auf Hardware nötig.
- Alle 129 importierten Sets größer. Evoli 4×→5×, Enton 3×→4×. Größter Frame bestimmt zulässige Skalierung; C++ place_frame begrenzt tatsächliche Positionen inklusive Bewegung und Spiegelung. Quellenoffsets bleiben unberührt. Ruhige Vorschau und reduzierte Bewegung erhalten passende Platzierungen; Auswahl nutzt 128 Pixel hohe Landschaftsfläche.
- Bestanden: warning-clean Build, 3.562.268 C++-Checks, 18 Python-Tests, Browserkatalog aller 130 Starter, Pflege-Smoke, beide Animations-Smokes, beide reproduzierbaren Importe, unabhängiger Vergleich von 12.146.208 Figuren- und 42.720 Hintergrundpixeln. Drei Skill-Client-Sequenzen ohne Fehler; sämtliche Auswahl-Kontaktübersichten, Mobile, Tag/Nacht und Sprungspitzen visuell kontrolliert.
- Alle drei bestehenden lokalen Instanzen vor DLL-Wechsel gespeichert und separat gesichert. Keine Saveformat- oder Pflegeregeländerung. Offene Hardwarearbeit wie M4; tatsächliche LCD-Farben und Laufzeit erst nach Boardwahl prüfen.

## 15.09.2026 / OpenAI Codex / M6 Simulator-Testreset

- Präzisierung: Spielstand zurücksetzen statt nur Server neu starten; Reset ausschließlich zum Testen, nicht im finalen Gerät. Branch codex/2026-09-15-simulator-reset, Basis 3bf88b5.
- Explizites Desktop-Flag --test-controls. Nur dann Resetbutton unter Simulator-Hilfen und POST /api/reset aktiv. Bestätigungsdialog, Abbrechen, Sicherung mit eindeutigem Dateinamen. Frische C++-Session übernimmt Profil; atomare Speicherung vor Sessionwechsel. Fehler bewahren altes Spiel/Datei und bleiben sichtbar. Standardmäßig kein Reset-Endpunkt, keine Geräte-Menüaktion oder Firmwareänderung.
- 21 Python-Tests und neuer Browser-Smoke tests/reset_smoke.mjs bestanden, inklusive Schreibfehler, deaktiviertem Modus, Dialog/Backup, Neu-Auswahl, Reload, Mobile und neuem spielbaren Begleiter. Originaler Skill-Client mit drei Sequenzen bestanden; Screenshots kontrolliert. C++ unverändert, kein neuer Build erforderlich.
- Port 8768 mit --test-controls neu gestartet; auf direkten Nutzerwunsch den Testspielstand tatsächlich auf Ei/Alter 0/Auswahl zurückgesetzt. Alte Datei als .reset-*.bak gesichert. Persönliche Tiere auf 8765/8767 nicht zurückgesetzt.

## 16.09.2026 / OpenAI Codex / M7 Spiel- und Pflege-UX

- Auftrag: beide Spiele, Bedürfnisse und Menü überarbeiten; bestehende Pokémon, Animationen und Hintergrund beibehalten. Basis 9a980b0; zu Beginn Themenbranch `codex/2026-09-16-game-experience` angelegt.
- Gestaltung: ruhiges Retro-Menü mit Kategorien, konsistenten Bedürfnisfarben und Zahlen. Der Begleiter bleibt auf Home im Mittelpunkt. Anleitung → Vorbereitung → Spielen → Rückmeldung → Ergebnis bildet den sichtbaren Ablauf. Keine zusätzlichen Untermenüs für die zehn Aktionen.
- Beerenfang: kostenlose Anleitung, explizite Startkosten, erkennbares Fangfeld passend zur C++-Grenze, Treffer-/Fehlerrückmeldung nach jeder Beere. Memory: wachsende gemeinsame 2/3/4-Folge, getrennte Vorführungs-/Eingabephase, sichtbare Eingaben, Timer und Teilbelohnung nach späterem Fehler. Abbruch bleibt ohne Gewinn.
- Tatsächliche Änderungen nach Begrenzung für Futter, Säubern, Medizin und Spielergebnisse. Numerische Satt-/Froh-/Energiebalken auf Display und Simulatorseite. Warnschwellen einheitlich aus C++; frühere falsche Ergebnisfaktoren und pauschale Balkengrenze beseitigt. Schlaf-/Pflegebalance unverändert.
- Kein neuer Heap-Verbrauch im Kern, keine parallele JS-/Python-Simulation. Game am Host 80 statt 64 Byte; State 32, Profile 25 und Animator 20 unverändert. Save V3 weiterhin 44 Byte; neue Phasen/Feedback sind transient.
- Bestanden: warning-clean Release-Build mit 3.562.287 C++-Checks, alle 21 Python-Tests, vollständiger Pflege-/Spiel-Browserflow für Evoli und Enton, neuer UX-Smoke für Teilgewinn/Timeout/Schlaf/Verfall/gesperrte Aktionen. Tatsächliche Canvas-Pixel bei niedriger Sättigung geprüft. Animationen beider Arten, Reset und alle 130 Starter ohne Regression.
- Originaler Skill-Client dreimal ausgeführt; Screenshots/Textzustand geprüft. Desktop-, Mobile-, Anleitungs-, Fang-, Memory- und Ergebnisansichten kontrolliert. Bei der Sichtprüfung aufgetretene Zeichenkodierungsfehler und Layout-Leerraum behoben und Browserprüfungen wiederholt. Testartefakte unter ignoriertem `output/`.
- Vorschau 8768 vor DLL-Wechsel gespeichert und als `output/roster-preview.json.pre-ux.backup` gesichert. Mit bestehendem Porenta und `--test-controls` wieder gestartet, keine Speicherfehler. Kein Reset; persönliche Profile/Saves unverändert.
- Arbeitsordner währenddessen extern auf `codex/2026-09-16-shell-prototype` gewechselt; zusätzliche unversionierte `hardware/`-Dateien und `result.json` nicht verändert oder übernommen. Softwareänderungen bleiben uncommittet. Vor einer später beauftragten Veröffentlichung Branch-Zuordnung der parallelen Arbeiten klären; kein Commit/Push dieser Runde.
- Offen: einige Tage echte Pflegebalance spielen, Timing/Lesbarkeit am physischen LCD prüfen. Kein ESP32-Build, GPIO-, Audio- oder Hardwaretest in dieser Runde. Regeln und Messwerte in RESEARCH, ARCHITECTURE, UX_HARDWARE und VALIDATION aktualisiert.

## 16.09.2026 / OpenAI Codex / Gehaeuseprototyp V1

- Nutzerauftrag: eigene druckbare Shell und drei Tasten erstellen; Waveshare ESP32-S3-LCD-2 anschliessend ausdruecklich als Board gewaehlt. Lokaler Themenbranch codex/2026-09-16-shell-prototype. Parallel entstandene Softwareaenderungen nicht bearbeitet; kein Commit oder Push.
- Offizielle Waveshare-Zeichnung und STEP-Referenz ESP32-S3-LCD-2-20250122 untersucht: 35,01 x 48,21 mm, M2-Raster 29 x 42,2 mm, aktive Flaeche 30,6 x 40,8 mm. Stiftleisten im vollstaendigen 3D-Modell beruecksichtigt. Quellen und offene Akku-/Tasterwahl in hardware/pokeball_v1/README.md.
- Eigene parametrische CadQuery-Konstruktion: 100-mm-Pokeball mit 2,4-mm-Wand, flachen Polen, Schutzdeckel, M3-Stiftscharnier, vorlaeufigem Schraubverschluss, austauschbarer Bedienplatte, drei gefuehrten Kappen, Boardtraeger, Tasterplatinenaufnahme und getrenntem Akkuhalter. Keine Fremdgeometrie von MakerWorld uebernommen; kein Qi/MagSafe oder ungeprueftes GPIO-Mapping.
- Ausgabe unter output/pokeball_v1: 12 einzelne STL in Drucklage (10 Bauteile plus zwei Passproben), STEP-Einzelteile/Baugruppe, drei neutrale 3MF-Platten ohne Druckerprofil/G-Code, Taster-Bohrbild, echte CAD-Vorschau und ZIP-Druckpaket. Quellen unter hardware/pokeball_v1; CAD-Abhaengigkeiten nur in isolierter .tools/cad-venv.
- Geprueft: 12 gueltige zusammenhaengende CAD-Volumen und wasserdichte STL mit konsistenter Orientierung. Keine Paarueberschneidungen; Deckel 0 bis 130 Grad in 5-Grad-Schritten kollisionsfrei; offizielles Board-STEP, Akku-Maximalhuelle, FR4-Tasterplatine, Schraubkopf-Freiraum sowie 0 bis 0,6 mm Tastenhub mit 0,25 mm seitlichem Spiel geprueft. SHA-256 bindet Bericht an finalen Export und CAD-Quelle.
- Unabhaengiger mechanischer Review: Platinen-/Pfostenkollision, Loetstellenfreiraum, Platinenklemmung, horizontale Scharnierprobe und seitliches Tastenflanschspiel verbessert. CAD-Vorschau und alle zwoelf Slicer-Objektansichten visuell geprueft.
- Bambu Studio 2.6.0.51: alle 12 Einzelteile erfolgreich gesliced, leere geometrische Warnmeldungen, Vergleichsprofil A1/0,4 mm/Generic PLA/0,20 mm, vier Waende, 15 Prozent Infill, automatische Stuetze. Summierte Einzelteil-Prognose einschliesslich Passproben ca. 4 h 49 min und 135 g; keine physische Druck- oder Passungsgarantie. Neutrale 3MFs vom Slicer als manifold eingelesen, ZIP-Integritaet und Objektzahlen geprueft. Kein Druck gestartet.
- Offen: zuerst START_Passproben drucken; reale Bauteilrevision, USB-Stecker, Schaltergefuehl, Stuetzenentfernung und Schraubhalt pruefen. Akku noch nicht ausgewaehlt; Quellenakku hat anderen Stecker als Waveshare. Keine Lade-, Laufzeit-, Funk-, Dauerhaltbarkeits- oder ESP32-Firmwarevalidierung. Montage- und Druckanleitung liegt dem ZIP bei.

## 08.10.2026 / OpenAI Codex / technischer Maßplan V2

- Nutzerauftrag: technische Zeichnung mit benötigten Bauteilen und Maßen. Später präzisierte Architektur berücksichtigt: unabhängig nutzbarer, herausnehmbarer Handheld in einer aufklappbaren Ball-Außenhülle.
- Bestehende V1/V2-CAD-Quellen nur gelesen. Neue Generatoren unter hardware/technical_drawings; acht A3-PDF-Seiten, acht bearbeitbare SVG-Blätter und Stückliste für ein/zwei Geräte unter output/pdf/pocket_pet_technical.
- Alle 15 V2-Teilmaße und sichtbaren Kanten aktuell aus CadQuery/OCCT gewonnen. Handheld-Schale 62 × 90 × 31,4; mit Tasten 33,2 tief; Kugel Ø130, komplette Ballhülle 130 × 142,55 × 118,6. Hersteller-STEP inklusive Pins 14 mm tief, PCB-Zeichnung 35,01 × 48,21. Omron-Bohrbild gegen Hersteller-Datenblatt geprüft.
- P05 ist aktuell gültige Geometrie, aber fünf getrennte Körper; V2-Prüfbericht enthält nur vier Meshes. Deshalb als Entwicklungsmaßplan gekennzeichnet, keine Druck-/Fertigungsfreigabe. Akku, Lautsprecher, Verstärker und optionaler Power-Schalter bleiben in der Stückliste ausdrücklich offen.
- Akkuhalter an der flachen V2-Rückschale: vorläufig M3×6 aus 2-mm-Halterboden und 4-mm-Einschraubweg abgeleitet; V1-M3×8 kann zu weit reichen. Keine CAD-Änderung oder physische Schraubprüfung.
- Geprüft: CAD-Quellhashes, Teil-/Gesamthüllen, acht A3-Seiten, lesbarer PDF-Text, SVG-XML, Stücklisten und alle gerenderten Seiten visuell. Keine Spiellogikänderung, kein CAD-Reparaturlauf, kein Druck oder Hardwaretest. Kein Commit/Push für diesen Dokumentauftrag.

## 08.10.2026 / OpenAI Codex / Einbau- und Montagezeichnungen Revision B

- Nutzerauftrag: farbiger, detaillierterer Innenaufbau mit Bauteilwahl, Einbaukoordinaten, Schrauben, Löchern und Anschlüssen. Rückmeldung: Hardware noch nicht bestellt. Revision A und bestehende CAD-/Softwarequellen erhalten.
- Neuer 14-seitiger A3-Zeichnungssatz unter output/pdf/pocket_pet_technical_rev_b mit 14 SVG-Blättern, CSV-Stückliste für Dat/Jennie, Herstellerquellen und ZIP. Einbauplan mit positivem X/Y/Z-Datum, Tiefenschichten, effektiven Sacklochtiefen, Schraubwegen, USB-/Kabelplan, Audiohüllen und Montagefolge. Projektionen und Explosionsprinzip ausdrücklich als solche bezeichnet.
- Konkrete Vorschläge: Waveshare ESP32-S3-LCD-2, Omron B3F-1000 auf eigener FR4-Platine, Adafruit 258/LP-503562 mit PCM, Speaker 3923 und Verstärker 3006/MAX98357A. Hersteller-/CAD-Maße und eigene Reservierungsmaße getrennt. Akku braucht einen geprüften Steckeradapter; aktuelle 3006-Schraubklemme ist nicht in der flachen 3-mm-Hülle enthalten.
- Frische OCCT-Prüfung: 92 Elektronik-/Handheld-Hüllenpaare, keine Volumenüberschneidung. Speaker und Amp bei lokal Y17 statt Y15, um die unteren Gehäusedome zu umgehen. Offizielles Board-STEP mit Pins berücksichtigt. Prüfbericht bindet CAD/STEP-Quellen per SHA-256 und nennt ausdrücklich ausgeschlossene Kabel, Lötstellen, Schalterpins, Audiohalter, Befestiger und Ballbewegung.
- Geprüft: 14 A3-PDF-Seiten gerendert und visuell geprüft, SVG-XML, 38 Stücklistenpositionen, sechs Herstellerlinks im PDF, ZIP-Integrität und Quellhashes. Keine Spieltests erforderlich, da keine Spielfunktion geändert. Digitale Hüllenprüfung ist keine vollständige Montage-/Hardwareprüfung.
- Offen vor Druckfreigabe: fünf P05-Körper verbinden, Audiohalter/Schallöffnung entwickeln, tiefliegende USB-Buchse mit realem Kabel prüfen, Zubehör-/Schraubkopf-/Löthüllen und vollständige V2-Montage/Bewegung ergänzen. Kein Druck, keine elektrische Freigabe, kein Commit/Push.

## 08.10.2026 / OpenAI Codex / isometrischer Gesamtplan Revision C

- Nutzerauftrag: verständliche räumliche Darstellung mit allen Gehäuse-/Elektronikteilen und mm-Maßen, kompakt auf einem Blatt. Öffentliche ISO-Beschreibungen 5456-3, 129-1 und 128-3 sowie aktuelle Herstellerseiten recherchiert; keine vollständige Normkonformität behauptet.
- Ein A1-Querformatblatt unter output/pdf/pocket_pet_technical_rev_c: echter CAD-Zusammenbau, beschriftete Explosionsansicht, alle 15 Druckteile, Bauteilmodelle, Maße, Stückzahlen Dat/Jennie, lokale Einbaulagen, Schrauben-/Lochdaten, Anschlüsse und Montagefolge. Maßstatus und offene Punkte direkt am Teil bzw. auf demselben Blatt. Revision A/B erhalten.
- 24 orthografische CAD-Isometrien mit numerisch gleicher Projektion aller drei Achsen; echtes Waveshare-STEP, ausdrücklich vereinfachte Elektronik-Maßhüllen. Analytische OCCT-Teilhüllen vor Triangulation gewonnen und identisch zur Originalreferenz. Explosionsabstände rein grafisch.
- Geprüft: ein PDF-Blatt 841 × 594 mm, alle P/E/M-Positionen, 38 CSV-Positionen, neun klickbare Quellenlinks, SVG-XML, Textgrenzen und keine Textüberlappungen, Quellhashes, ZIP-Integrität. Komplettes Blatt und vier Detailregionen bei 150 dpi gerendert und visuell geprüft. Vorhandener begrenzter B-Hüllenbericht (92 Paare) nur bei identischen Quellhashes als Provenienz übernommen.
- Neue Render-/Zeichnungs-/Verifikationsgeneratoren; gemeinsamer Zeichenhelfer um variable Seitengröße erweitert (Standard A3 bleibt). Bestehende CAD- und Spielquellen unverändert. Kein Software-Build nötig, da keine Spielfunktion geändert.
- Unverändert offen: P05 fünf Körper, Audiohalter/Schallöffnung, aktuelle Verstärker-Lieferhöhe, tiefliegender USB-Zugang und vollständige Baugruppen-/Bewegungs-/physische Prüfung. Keine Fertigungsfreigabe, kein Druck, kein Elektrotest, kein Commit/Push.

## 09.10.2026 / Codex / Removable Handheld V2 und GitHub-Vorbereitung

- Nutzer hat die herausnehmbare Handheld-in-Pokéball-Idee bestätigt und ausdrücklich das Waveshare ESP32-S3-LCD-2 mit rechteckigem 2-Zoll-Display als Basis gewählt.
- V2-CAD überarbeitet: vier M2-Gehäuseschrauben weg von den Eckwänden verlegt, Bossdurchmesser auf 5 mm gesetzt und Rückschale als eigene geschlossene Rückwand mit Seitensteg ausgeführt.
- Druckpaket `hardware/pokeball_v2/release`: 15 STL, 15 STEP-Teile, offene Baugruppe und Handheld-STEP, Vorschau, SHA-gebundener Prüfbericht sowie vier neutrale 3MF-Platten (Passproben, Ball-Unterteil, Deckel, Handheld/Halter). Kein G-Code und kein Druckerprofil.
- CAD-Build bestanden. Unabhängige Mesh-/Volumen-/Bewegungsprüfung bestanden: 15 wasserdichte zusammenhängende Meshes; keine Kollisionen bei Teilepaaren, 0–130° Deckelbewegung, diskreter Entnahme, Board-/Akku-/Tasterhüllen und Tastenhub. Vorschau visuell kontrolliert.
- C++-Release-Build mit Zig 0.15.2 bestanden: 3.562.287 Kernprüfungen. Python-Adaptertests bestanden: 21 Tests. Beim ersten Testlauf blockierte Windows-Temp außerhalb des Arbeitsbereichs; erneuter Lauf mit projektinternem Temp erfolgreich.
- Playwright-UI-Smoke-Test konnte nicht starten, weil das passende Chromium nicht installiert ist. App-In-Browser konnte Loopback nicht erreichen (`ERR_CONNECTION_TIMED_OUT`). Browserverhalten bleibt somit unbestätigt.
- Das frühere V1-Druckpaket-ZIP liegt ergänzend bei `hardware/pokeball_v1/Pocket_Pet_V1_Druckpaket.zip`; V1-Quelle und Dokumentation bleiben getrennt vom neuen V2-Release.
- Keine Bestellung, kein Druck oder physischer Passform-/Elektroniktest. Gelötete Boardhöhe, USB-Kabel, Akku, Bandzug, Gewindehalt, Displaykontakt und reale Toleranzen sind offen. Die Designs sind digitale Funktionsprototypen.

## 28.10.2026 / Anthropic Claude Opus 5.5 / Geräte-Renderer, Tastendecoder, Pflegekreislauf V4

- Auftrag: alles sichten, recherchieren, Verbesserungen selbst wählen und umsetzen; Ziel Tamagotchi auf Mikrocontroller mit gutem Spielspaß. Branch `claude/2026-10-28-device-renderer-care-loop`, Basis 6803a04 (`codex/2026-10-09-removable-handheld`).
- Befund: (1) Die gesamte Bildschirmoberfläche existierte nur in JavaScript – die Firmware hätte sie komplett neu schreiben müssen, der Simulator war nicht pixelgleich. (2) Entprellung, langes OK und Wiederholung lagen ebenfalls in JavaScript. (3) Pflege ohne Folgen, kein Wachstum, kein Tagesrhythmus, nur Evoli entwickelt sich. (4) Board-Textseiten nennen keine GPIOs und keinen RTC.
- Umgesetzt: `pet::render` (alle Bildschirme in RGB565, beliebige Zeilenstreifen, ohne Heap) mit eigener 5×9-Pixelschrift inkl. Umlauten; `pet::InputDecoder`; `pet::Device` als gemeinsamer Einstieg für Firmware und Desktop. Browser zeigt nur noch C++-Frames und sendet rohe Tastenpegel (jeder Pegel ≥80 ms wie ein echter Tastenhub). Asset-Endpunkte entfallen; Start lädt sofort statt Pixel einzeln per ctypes zu übertragen.
- Spiel: Rufe mit Sprechblase, Pflegefehler nach 15 Min., tägliche Vergebung, Schlaf 21–7 Uhr, Streicheln, Wachstum Baby/Kind/Erwachsen mit sichtbarer Größe, Level, sieben Entwicklungslinien mit vorhandener Fanart, Feierbildschirm, „Uhr stellen“. Energie- und Nachthunger-Raten angepasst. Details und Quellen in RESEARCH.
- Spielstand V4 (48 Byte), V1–V3 werden migriert. Lokale `saves/pet.json` und `saves/jennie.local.json` vorher als `*.pre-v4.backup.json` gesichert; ältere Programmstände lesen V4 nicht.
- Simulator lauscht zusätzlich auf `::1`, sonst wartete jeder Aufruf über `localhost` unter Windows ~0,3–2 s auf den IPv6-Fallback.
- Geprüft: warning-clean Build, 3.562.599 C++-Checks, 23 Python-Tests, alle sechs Playwright-Smokes (Chromium jetzt verfügbar), Sichtprüfung aller Bildschirme als Renderings und im eingebauten Browser mit Tastatur/Maus. Siehe VALIDATION.
- Nicht geprüft/offen: ESP32-Build und Flash (keine ESP-IDF-Toolchain hier), echtes LCD inkl. Lesbarkeit der 1×-Schrift und Bildrate, GPIO-Pins (Schaltplan-PDF prüfen), Akku-/Deep-Sleep-Strategie, mehrtägige Balance der Rufe. Gehäuse unverändert; Empfehlung: Tasten auf RTC-fähige GPIOs für Weckfunktion aus dem Deep Sleep.
- Nächste Schritte: Schaltplan auswerten und Pinbelegung dokumentieren; ESP-IDF-App mit `esp_lcd`-ST7789, Streifen-DMA, GPIO-Abtasttask, NVS-Speicher und Deep Sleep; dann am Gerät Lesbarkeit und Ruf-Balance testen. Kein Commit/Push in dieser Runde.

## 28.10.2026 / Anthropic Claude Opus 5.5 / Einkaufsliste Hardware

- Auftrag: benötigte Hardware durchdenken, Einkaufsliste mit günstigen Bezugsquellen (bevorzugt China, möglichst ein Shop). Ergebnis: `hardware/EINKAUFSLISTE.md`.
- Geprüft im Browser: Waveshare ESP32-S3-LCD-2 „No Touch-No-Camera“ bei SpotPear auf AliExpress (23,39 € ab 2 Stück, Versand frei); Kleinteile auf AliExpress; Akku PKCell LP-503562 auf eBay.de (einzelne LiPo-Zellen auf AliExpress für DE praktisch nicht verfügbar). Temu verlangt für die Suche eine Anmeldung, nicht geprüft. EU-Pauschalzoll 3 € je Artikelart seit 1.7.2026 in der Kostenschätzung berücksichtigt.
- Nichts bestellt. Preise sind Momentaufnahmen. Offen: Senkkopfschrauben nicht einzeln geprüft, Akkupolarität am MX1.25-Adapter vor Inbetriebnahme messen, Tastenpins im Schaltplan auf Weckfähigkeit prüfen.

