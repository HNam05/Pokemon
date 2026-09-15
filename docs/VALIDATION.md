# Validierung M2

Ausgeführt am 14.–15.09.2026 auf Windows x64. Die folgenden Ergebnisse beziehen sich auf den Desktop-Prototyp einschließlich Enton, Profilen und Drei-Tasten-Erweiterung.

## Ausgeführte Prüfungen

| Prüfung | Ergebnis |
|---|---|
| C++17-Build, Zig 0.15.2/Clang, `-O2 -Wall -Wextra -Wpedantic -Werror` | Erfolgreich, ohne Warnungen |
| C++-Tests | 22.907 Checks bestanden; darunter 20.000 Aktions-/Zeit-Invarianten sowie Prüfung aller Sprite-Palettenindizes |
| Python-Adaptertests | 14 Tests bestanden |
| Browserabläufe, Chromium/Playwright | Mit Evoli und Enton bestanden, keine erfassten Konsolen-/JavaScript-Fehler |
| Develop-Web-Game Skill-Client | Mit Tastenfolge ausgeführt, State und Canvas-Screenshot kontrolliert |
| Desktop 1280×920, Mobil 390×844 | Screenshots kontrolliert; kein horizontaler Überlauf mobil |
| Vollbild | Spiel und drei Tasten sichtbar; Umschalten geprüft |
| Syntaxprüfungen | `node --check` und Python `py_compile` erfolgreich |
| Git-Diff | Auf unerwünschte Dateien, Geheimnisse, Speicherstände, Builddateien und Whitespace geprüft |

### Verhaltensnachweise

- Schlüpfen exakt nach zehn Minuten, kein vorzeitiger Schlupf.
- Startauswahl beider Arten, kein Zeitverfall vor Bestätigung, Wiederaufnahme einer unbestätigten Auswahl.
- Füttern und Überfütterung, Schlaf, Aufwachen, Krankheit, Erschöpfung und vollständige Behandlung.
- Minutenberechnung unabhängig von kleinen/großen Zeitschritten außerhalb des Minispiels.
- Pause einschließlich längerem Suspend des Rechners; Zeitraffer wird bei längerem Suspend nicht auf Offline-Zeit angewendet.
- Fünf erfolgreiche Beerenfänge, verpasste/zu frühe Fänge, Kosten und einmalige Belohnung.
- Entwicklungsgrenzen und Tages-/Nachtgrenze.
- Enton kann nicht versehentlich Evoli-Entwicklungen annehmen.
- Denkpause: Anzeigephase, Eingabe, vollständiger Erfolg, falsche Antwort, Timeout und Abbruch ohne Belohnung.
- Speicherrundlauf, einzelne beschädigte Bytes, ungültige Werte trotz passender CRC, kurze/fehlende Daten, unverändertes Ziel bei Fehler.
- **Unabhängige Formatprüfung**: Python `struct.pack` + `zlib.crc32` erzeugen den erwarteten C++-Spielstand. Keine Verwendung des C++-Encoders zur Berechnung des Sollwerts.
- Separat erzeugter V1-Spielstand wird nach V2 migriert, mit identischen bisherigen Datenbytes und erhaltener entwickelter Art.
- UTF-8-Namen, Ablehnung von zu langen/ungültigen Namen, getrennte Profile trotz Laden desselben Spielstands.
- 908 Byte gepackte Sprite-/Palettendaten, Palette jedes Pixels geprüft. Host-Größen: Game 64 Byte, darin State 32 Byte; Profile 25 Byte.
- Simulierter Schreibfehler bewahrt vorherige Datei und wird sichtbar gemeldet. Ein zweiter Sperrzugriff wird abgewiesen; Sperre nach Freigabe wieder nutzbar.
- Offline-Zeit auf acht Stunden begrenzt, rückwärts gehende Uhr erzeugt keine negative Zeit.
- Browser: drei Tasten mit Tastatur/Maus, zyklisches Scrollmenü, Status/Pflegehilfe, beide Minispiele, Speichern, Seitenneuladen, Pause/Zeitraffer, Mobilansicht, Vollbild und Dialog.
- Langes OK mit Tastatur und Maus: genau einmal zurück, kein zusätzliches Bestätigen beim Loslassen. Die Rückkehr aus der Pflegehilfe erhält die Menüauswahl.
- HTTP: ungültige Bool-Taste, fremder Origin und Zugriff außerhalb der erlaubten Webdateien abgewiesen. Zweiter Browser-Tab beschleunigt die manuelle Testuhr nicht.

## Reproduzieren

```powershell
python scripts/build.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Alternativen zum CMake-Build stehen in README. Für den optionalen Browser-Test wird das Node-Paket `playwright` mit passendem Chromium benötigt; es ist **keine Laufzeitabhängigkeit** des Spiels. Auf diesem Arbeitsrechner wurde das vorhandene gebündelte Playwright verwendet (lokale ignorierte `node_modules`-Verknüpfung).

Mit lokal installiertem Testwerkzeug:

```powershell
npm install --no-save --package-lock=false playwright
npx playwright install chromium
node tests/browser_smoke.mjs
$env:PET_TEST_STARTER = '4'
node tests/browser_smoke.mjs
```

Der Browser-Test startet selbst einen Server mit manueller Uhr auf Port 8877, neutralem Testprofil und separatem Spielstand. `PET_TEST_PORT` kann einen anderen freien Port setzen. Starter 1 ist Evoli (Standard), Starter 4 Enton. Er beendet nur den eigenen Prozess. Artefakte liegen unter `output/browser/` bzw. `output/browser-enton/` und werden nicht eingecheckt.

## Animationsausbau / 15.09.2026

- Warning-clean Zig-Release-Build: 121.168 C++-Prüfungen bestanden, darunter Framegrenzen, Paletten, Statusprioritäten, Seed-Reproduzierbarkeit, Chunk-Zeitinvarianz, eigener Zufall und unveränderte Save-Daten.
- 15 Python-Adaptertests bestanden; Essereignis, Pause und Animationsbudget ergänzt.
- `node tests/animation_smoke.mjs`: Evoli und Enton je über 70 Sekunden simuliert. Alle fünf spontanen Abläufe sichtbar, 27 bzw. 20 unterschiedliche Clip-/Frame-Kombinationen; Füttern, Schlafen, Pause und reduzierte Bewegung bestanden. Ober-/Unterkante der Frames geprüft. Screenshots unter `output/animations` visuell kontrolliert.
- Bisheriger Browser-Smoke für beide Starter samt Pflege, Minispielen, Speichern, Mobilansicht und HTTP-Grenzen weiterhin bestanden.
- Mit Pillow: `python scripts/import_sprites.py --check` bestätigt die Quellhashes und reproduzierbare C++-Ausgabe. `python tests/verify_sprite_import.py` bestätigt unabhängig 59.200 Quellpixel gegen die kompilierte Darstellung.
- Zusätzlicher Skill-Client-Lauf mit drei Sequenzen bestanden; Status und Canvas-Screenshots unter `output/skill-animation` kontrolliert. Keine Browserfehler. Diese lokalen Artefakte werden nicht eingecheckt.
- Kein ESP32-Build und keine Messung am LCD; Pixelbilder stammen ausschließlich aus der dokumentierten Evoli-Fanvariante bzw. projektinternen Grafiken.

## Noch nicht nachgewiesen (Hardware und weitere Plattformen)

- CMake-Build mit MSVC/GCC auf einem zweiten Rechner; hier wurde der direkte portable Zig-Build verwendet.
- Linux/macOS, andere Browser, Bildschirmleser mit realer Assistenzsoftware.
- ESP-IDF-Toolchain-Build, echter LCD-Renderer, GPIO-Entprellung, Flash/NVS unter Stromausfall.
- Akku, Ladeelektronik, Sleep-Strom, Laufzeit, Gehäusepassung, Displayablesbarkeit auf dem Gerät.
- Spielbalance über mehrere reale Tage; Grafik und Entwicklungsvarianten sind Platzhalter.

Diese Punkte sind nächste Integrationsschritte, keine behaupteten Testergebnisse.

## Vollständiger Fan-Katalog M4 / 15.09.2026

- Warning-clean Zig-Release-Build: **3.492.014 C++-Checks** bestanden. Alle 130 Starter auswählen, schlüpfen lassen, speichern und wiederherstellen; stabile/ungültige IDs, keine artfremde Entwicklung; sämtliche Frames, Paletten und Bildschirmgrenzen geprüft.
- **17 Python-Adaptertests** bestanden, einschließlich unabhängiger V3-Byte-Referenz, V1/V2-Migration, Ablehnung neuer IDs in alten Formaten und gezieltem Asset-Abruf.
- Import mit Pillow 12.3.0: Quellhashes und `scripts/import_sprites.py --check` bestanden. Separater `tests/verify_sprite_import.py` bestätigt **12.146.208 Quellpixel über alle 129 Sets** gegen die kompilierte Ausgabe.
- `node tests/roster_smoke.mjs`: alle 130 Begleiter per Tastatur durchlaufen, Name/Credits und Cachegrenze kontrolliert; Halten/Loslassen, komplettes zyklisches Blättern, Schlüpfen, Animation, Speichern/Neuladen, Mobilansicht, Credits-Endpunkt und ungültige Asset-IDs bestanden. Alle sechs Kontaktübersichten unter `output/roster/` und die Mobilansicht visuell kontrolliert.
- Bestehende `tests/browser_smoke.mjs` für Evoli und Enton sowie `tests/animation_smoke.mjs` weiterhin bestanden: Pflege, Minispiele, Speicherverhalten, spontane Abläufe, Fressen, Schlaf, Pause und reduzierte Bewegung. Keine Browserfehler.
- Originaler Develop-Web-Game-Skill-Client mit drei Sequenzen: Canvas und Textzustand in `output/skill-roster/` geprüft, keine Fehlerlogs. Bilder und Testspielstände bleiben ignoriert.
- Gemessene Host-Datengrößen: Game 64, State 32, Profile 25, Animator 20 Byte; Animationen mit Tabellen 974.322 Byte, zusätzlich 908 Byte bestehende Standgrafiken. Keine Messung des gesamten ESP32-Verbrauchs.
- Persönliche Spielstände vor dem V3-Update lokal gesichert. Kein Hardwarebuild, keine LCD-/GPIO-/Strommessung. Andere Betriebssysteme bleiben offen.

## Größere Begleiter und Waldlichtung / 15.09.2026

- Warning-clean Zig-Release-Build: 3.562.268 C++-Checks; 18 Python-Tests bestanden.
- Sämtliche Posen der 130 Begleiter einschließlich gespiegelter Darstellung und Bewegungsgrenzen geprüft. Alle 129 importierten Sets haben eine höhere Skalierung als in M4; Evoli 5×, Enton 4×. Palette, Dimensionen und Tag-/Nacht-Pixelteilung geprüft.
- Browser-Smokes für alle 130 Starter, Größen, Credits, Navigation, Animation, Speicher/Laden, Mobile und HTTP-Grenzen bestanden. Pflege-Smoke und Animations-Smokes Evoli/Enton mit Sprungspitzen, Essen, Schlaf, Pause und reduzierter Bewegung bestanden.
- Alle sechs Kontaktübersichten der neuen Auswahl und Mobilansicht visuell kontrolliert. Tag-, Nacht-, Enton-, Evoli- und Sprungansichten geprüft. Originaler Skill-Client: drei Sequenzen ohne Browserfehler; Screenshots und Textzustand unter output/skill-nature geprüft.
- Beide Offline-Importer reproduzierbar; 12.146.208 SpriteCollab-Quellpixel unverändert zur kompilierten Darstellung. Zusätzlich sämtliche 42.720 Pixel der Hintergrund-Displayfassung unabhängig gegen C++ geprüft.
- Hintergrund: 21.424 Byte konstante Daten einschließlich beider Paletten. Spielkern, Animator und Save V3 unverändert. Kein ESP32-Build oder physischer LCD-Test.
