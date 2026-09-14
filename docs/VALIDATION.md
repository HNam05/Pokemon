# Validierung M1

Ausgeführt am 14.09.2026 auf Windows x64. Die folgenden Ergebnisse beziehen sich auf den Desktop-Prototyp.

## Ausgeführte Prüfungen

| Prüfung | Ergebnis |
|---|---|
| C++17-Build, Zig 0.15.2/Clang, `-O2 -Wall -Wextra -Wpedantic -Werror` | Erfolgreich, ohne Warnungen |
| C++-Tests | 20.115 Checks bestanden; davon 20.000 Invariantenprüfungen einer deterministischen Aktions-/Zeitsprungfolge |
| Python-Adaptertests | 11 Tests bestanden |
| Browserabläufe, Chromium/Playwright | Bestanden, keine erfassten Konsolen-/JavaScript-Fehler |
| Develop-Web-Game Skill-Client | Mit Tastenfolge ausgeführt, State und Canvas-Screenshot kontrolliert |
| Desktop 1280×920, Mobil 390×844 | Screenshots kontrolliert; kein horizontaler Überlauf mobil |
| Vollbild | Spiel und drei Tasten sichtbar; Umschalten geprüft |
| Syntaxprüfungen | `node --check` und Python `py_compile` erfolgreich |
| Git-Diff | Auf unerwünschte Dateien, Geheimnisse, Speicherstände, Builddateien und Whitespace geprüft |

### Verhaltensnachweise

- Schlüpfen exakt nach zehn Minuten, kein vorzeitiger Schlupf.
- Füttern und Überfütterung, Schlaf, Aufwachen, Krankheit, Erschöpfung und vollständige Behandlung.
- Minutenberechnung unabhängig von kleinen/großen Zeitschritten außerhalb des Minispiels.
- Pause einschließlich längerem Suspend des Rechners; Zeitraffer wird bei längerem Suspend nicht auf Offline-Zeit angewendet.
- Fünf erfolgreiche Beerenfänge, verpasste/zu frühe Fänge, Kosten und einmalige Belohnung.
- Entwicklungsgrenzen und Tages-/Nachtgrenze.
- Speicherrundlauf, einzelne beschädigte Bytes, ungültige Werte trotz passender CRC, kurze/fehlende Daten, unverändertes Ziel bei Fehler.
- **Unabhängige Formatprüfung**: Python `struct.pack` + `zlib.crc32` erzeugen den erwarteten C++-Spielstand. Keine Verwendung des C++-Encoders zur Berechnung des Sollwerts.
- Simulierter Schreibfehler bewahrt vorherige Datei und wird sichtbar gemeldet. Ein zweiter Sperrzugriff wird abgewiesen; Sperre nach Freigabe wieder nutzbar.
- Offline-Zeit auf acht Stunden begrenzt, rückwärts gehende Uhr erzeugt keine negative Zeit.
- Browser: drei Tasten mit Tastatur/Maus, zyklisches Menü, Status, Minispiel, Speichern, Seitenneuladen, Pause/Zeitraffer, Mobilansicht, Vollbild und Dialog.
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
```

Der Browser-Test startet selbst einen Server mit manueller Uhr auf Port 8877 und einem separaten Testspielstand. `PET_TEST_PORT` kann einen anderen freien Port setzen. Er beendet nur den eigenen Prozess. Artefakte liegen unter `output/browser/` und werden nicht eingecheckt.

## Noch nicht nachgewiesen

- CMake-Build mit MSVC/GCC auf einem zweiten Rechner; hier wurde der direkte portable Zig-Build verwendet.
- Linux/macOS, andere Browser, Bildschirmleser mit realer Assistenzsoftware.
- ESP-IDF-Toolchain-Build, echter LCD-Renderer, GPIO-Entprellung, Flash/NVS unter Stromausfall.
- Akku, Ladeelektronik, Sleep-Strom, Laufzeit, Gehäusepassung, Displayablesbarkeit auf dem Gerät.
- Spielbalance über mehrere reale Tage; Grafik und Entwicklungsvarianten sind Platzhalter.

Diese Punkte sind nächste Integrationsschritte, keine behaupteten Testergebnisse.
