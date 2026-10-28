# Architektur und ESP32-Port

## Entscheidung

C++17 für Spielregeln und Spielzustandsmaschine. Ein Kern für Desktop und ESP32. CMake baut ohne Fremdbibliotheken. Standard-C++ statt Arduino-Aufrufe im Kern erleichtert reproduzierbare Tests vor dem Hardwarekauf.

Ein natives Fenster mit SDL wäre ebenfalls möglich, verlangt aber eine zusätzliche Grafik-Abhängigkeit. Der erste PC-Simulator nutzt deshalb Canvas im Browser und eine lokale Python-Standardbibliothek-Brücke zu einer **kompilierten C++-Bibliothek**. JavaScript zeichnet ausschließlich und transportiert Eingaben. Kein doppeltes Implementieren der Spielregeln, kein Cloud-Service, kein WebAssembly-Toolchain-Zwang.

```text
Tasten (rohe Pegel) -> lokaler Python-Server -> C ABI -> pet::Device
                                                          |  InputDecoder (Entprellen, Halten, Wiederholen)
                                                          |  Game (Regeln) + Animator (Kosmetik)
                                                          |  render() -> RGB565 240x320
Browser-Canvas  <---------- fertige Pixel ----------------+

Später: GPIO-Pegel -> dasselbe pet::Device -> render() in Streifen -> ST7789 per SPI/DMA
                                         \-> 48-Byte-Spielstand -> NVS
```

Seit 28.10.2026 zeichnet der Browser **nichts mehr selbst**. Der komplette Geräte-Bildschirm entsteht in `src/render.cpp` und wird als RGB565-Frame übertragen. Damit ist der Simulator pixelgleich mit dem späteren LCD, und die Firmware muss keine zweite Oberfläche implementieren. Auch Entprellung, langes OK und Auto-Wiederholung laufen im C++-`InputDecoder`, nicht mehr in JavaScript.

## Dateien und Verantwortlichkeiten

| Pfad | Zweck |
|---|---|
| `include/pet/game.hpp`, `src/game.cpp` | Zustände, Aktionen, Minuten-/Reaktionszeit, Entwicklung, deterministischer Zufall |
| `include/pet/save.hpp`, `src/save.cpp` | 44-Byte-V3-Format, V1-/V2-Migration, Little Endian, CRC32, Werteprüfung |
| `include/pet/sprite.hpp`, `src/sprite.cpp` | Gemeinsame gepackte 4-/8-Bit-Palettengrafik (aktuell alle Sets 4 Bit), RGB565-Farben |
| `include/pet/profile.hpp` | Festes Namensprofil, UTF-8-Prüfung, unabhängig vom Spielstand |
| `include/pet/animation.hpp`, `src/animation.cpp` | Kosmetische Zustandsmaschine mit eigenem Zufall, Echtzeit-Frames und begrenzter Bewegung; Wachstumsstufen verkleinern die Skalierung |
| `include/pet/render.hpp`, `src/render.cpp`, `src/font.inc`, `scripts/make_font.py` | Geräte-Renderer für alle Bildschirme in beliebigen Zeilenstreifen; eigene 5×9-Pixelschrift mit Umlauten, ß und Symbolen |
| `include/pet/input.hpp`, `src/input.cpp` | Drei-Tasten-Decoder: 30 ms Entprellung, OK beim Loslassen, 700 ms Halten = einmal Zurück, Seitentasten 450/160 ms Wiederholung |
| `include/pet/device.hpp`, `src/device.cpp` | Bündelt Game, Animator, Decoder, Profil und Renderer; einziger Einstiegspunkt für Firmware und Desktop-Brücke |
| `include/pet/catalog.hpp`, `src/roster_frames.inc`, `scripts/import_sprites.py`, `assets/` | Gepinnte Fanart, Offline-Import, Quellhashes, Credits und komprimierte konstante Frames |
| `desktop/bridge.cpp` | C ABI für Spiel, Profil, Menühinweise und Sprite-Daten. Profilname separat vom formatierten JSON; Python übernimmt korrektes Escaping. |
| `desktop/server.py` | Loopback-HTTP, monotone Uhr, atomare lokale Speicherung, begrenzte Offline-Zeit |
| `desktop/web/` | Responsive Simulator-Seite: zeigt den C++-Frame, sendet rohe Tastenpegel (jeder Pegel mindestens 80 ms, wie ein echter Tastenhub), Seitenleiste und zugängliche Statusbeschreibung |
| `tests/` | Regeln, Grenzwerte, Korruption, Integration und Browserabläufe |

`pet::Game` besitzt keine Heap-Allokationen, Dateipfade, GPIO-Abhängigkeiten oder Wanduhraufrufe. Es nimmt höchstens 60.000 reale Millisekunden und Geschwindigkeit 0…3600 pro `advance` entgegen; längere Intervalle müssen vom Adapter zerlegt werden. Pflege wird minutengenau und mit gespeichertem Millisekundenrest berechnet. Im aktiven Minispiel läuft nur dessen Uhr. Aufrufe erfolgen aus einem Thread/Task.

## Begleiterkatalog und Darstellung

129 importierte Sets plus eigener Enton sind über `catalog.hpp` auswählbar. Namen, Formen, Künstler, Frame-Tabellen und integerbasierte Darstellung liegen bei den konstanten C++-Assets. Alle Arten verwenden denselben Pflegekern. Zusätzliche Entwicklungsketten sind nicht implementiert.

`/api/assets` liefert Metadaten und nur die bisherigen fünf Arten (Ei, Evoli, Psiana, Nachtara, Enton). Weitere Bilder lädt `/api/assets/<id>` bedarfsgerecht. Browser und Server halten höchstens vier zusätzliche Sets im Cache. Der Browser baut Canvas-Bitmaps und verwirft die übertragenen Pixelarrays. `/credits` liefert den generierten Künstlerkatalog. Auf Hardware ist dieser HTTP-/Canvas-Weg nicht nötig. Der Hintergrund liegt ebenfalls palettiert in C++ (`forest_scene.inc`); zwei Paletten teilen einen Pixelbestand. `place_frame` liefert bildschirmbegrenzte Positionen für die vergrößerten Figuren, einschließlich ruhiger Darstellung bei reduzierter Bewegung.

## Spielstandformat V4 und Migration

**V4 (seit 28.10.2026), 48 Bytes:** Bytes 0…39 wie V3 mit Version 4 und Länge 48, danach Pflegefehler, Rufminuten, Streichel-Abklingzeit und Flags (je u8, Flags nur Bit 0 „Fehler seit dem Morgen“), CRC32 über Bytes 0…43. V1–V3 werden gelesen und mit sauberer Pflegebilanz (alle neuen Felder 0) übernommen; beim nächsten Speichern entsteht V4. Zulässige Arten: Starter selbst oder ein Ziel seiner Entwicklungslinie (`Game::evolves_into`). Alte Programme können V4 nicht lesen.

Bisheriges V3-Layout, 44 Bytes: stabile Magic ASCII `PET1` (4), Version (u16=3), Länge (u16=44), Alter/Rest-ms/PRNG/EP (je u32), Tagesminute/Vernachlässigung (je u16), Sättigung/Glück/Energie/Hygiene/Gesundheit/Bindung/Abfall/Art/Schlaf/Krankheit (je u8), Starter-Art und Auswahl-bestätigt (je u8), CRC32 über Bytes 0…39 (u32). CRC32 ist Fehlererkennung, keine Authentifizierung. Struktur-Padding wird nie gespeichert.

V1 mit 42 Bytes und CRC über Bytes 0…37 wird weiter gelesen: Starter Evoli, Auswahl bereits bestätigt. Werte und gewachsene Art bleiben unverändert. Enton ist in V1 nicht zulässig. V2 mit 44 Bytes wird ebenfalls gelesen; seine zulässigen Arten bleiben auf den damaligen Katalog begrenzt. V3 behält das Layout bei und erweitert ausdrücklich die zulässigen Art-IDs. Beim nächsten Speichern wird V3 geschrieben. Alte Programme können V3 nicht lesen; vor Downgrade eine passende Sicherung verwenden. IDs 0–4 bleiben stabil, neue IDs stehen in `assets/roster.json`. Bestehende IDs niemals neu vergeben oder ohne Migration entfernen.

Beim Lesen müssen Länge, Version, Prüfsumme, Boolwerte und Wertebereiche stimmen. Dekodierung und Restore sind transaktional: Fehler verändern das laufende Spiel nicht. Unbekannte Versionen werden abgewiesen; künftige Migrationen explizit ergänzen.

Desktop-Hülle: JSON mit `version`, `saved_at` als Unix-Sekunden und hexkodiertem Payload (84, 88 oder 96 Hexzeichen). Schreiben in temporäre Datei, Flush/fsync, dann `os.replace`. Nach jeder Taste, manuellem Speichern, Zeitsprung und alle 30 Sekunden. Fehler sichtbar in der Oberfläche. Ein kaputter gespeicherter Stand bricht den Serverstart ab und wird nicht überschrieben. Eine Betriebssystem-Sperre verhindert mehrere Server für dieselbe Speicherdatei und wird auch bei einem Prozessabbruch freigegeben. Saves gehören nicht ins Git.

## Drei-Tasten-Vertrag

- Home: Mitte öffnet Menü, beide Seitentasten öffnen Status.
- Startauswahl: Seitentasten wechseln zyklisch durch 130 Begleiter, Mitte bestätigt; vorher läuft keine Pflegezeit.
- Menü: Seitentasten scrollen vertikal durch zwölf Einträge mit fünf sichtbaren Zeilen; Mitte aktiviert. „Zurück“ ist ein expliziter Eintrag. Beschriftungen und Hinweise kommen aus C++.
- Uhr stellen: Seitentasten ändern Stunde bzw. Minute (Halten wiederholt), OK wechselt zur Minute und übernimmt, langes OK bricht ohne Änderung ab.
- Entwicklung: Feierbildschirm, beliebige Taste zurück.
- Status/Ergebnis: beliebige Taste zurück.
- Beerenfang: Links/Rechts bewegen begrenzt auf drei Spuren, Mitte ist ein Fangversuch.
- Spielanleitung: Seitentaste oder langes OK zurück ins Menü, kurzes OK startet und bezahlt erst dann die Kosten. Pflegezeit pausiert beim Lesen.
- Denkpause: wachsende Folge mit zwei, drei, vier Zeichen ansehen, dann über Links/OK/Rechts wiederholen. Drei Runden, begrenzte Eingabezeit; gelöste Runden zählen auch nach Fehler/Zeitablauf. Pflegezeit pausiert.

`MiniPhase` trennt Vorbereitung, fallende Beere, Vorführung, Eingabe und Rückmeldung. Zeitgrenzen, aktives Memory-Zeichen, Sequenzlänge, Treffer und Belohnungen werden ausschließlich vom Kern berechnet. Der Browser zeichnet diese Zustandsansicht. `CareChange` meldet tatsächliche Differenzen nach Begrenzung; die Anzeige läuft vier reale Sekunden, auf dem Ergebnisbild bleibt sie erhalten. `Game::need_low` liefert dieselben Warnschwellen an Pflegelogik und Darstellung. Diese UI-Zustände sind transient: Save V3 bleibt unverändert bei 44 Bytes. Host-Game jetzt 80 Bytes inklusive State und Minispiel, keine Heap-Allokation.

Diese Semantik ist jetzt portabler Code (`pet::InputDecoder`) und wird im Simulator mit echten, rohen Tastenpegeln betrieben. Auf Hardware liest eine Task die drei Pegel (active-low + Pull-up nach Schaltplan, invertiert zu „1 = gedrückt“) etwa alle 5–10 ms und ruft `Device::input(raw, esp_timer_get_time()/1000)`. Keine Button-ISR führt Spiellogik aus. `Game::repeats_side_buttons()` legt fest, wo Halten wiederholt (Auswahl, Menü, Uhr). `Device::take_event()` liefert einmalige Ereignisse (Füttern, Streicheln, Schlüpfen, Wachsen, Entwicklung, Pflegefehler) für einen späteren Ton-/Vibrationsadapter; `Game::calling()` kann Display oder LED wecken.

## Portierung: ehrlicher Stand

Der Kern ist plattformneutral und am PC kompiliert/getestet. **Es existiert noch keine getestete oder flashbare ESP32-Firmware.** `firmware/components/pet_core` bietet die ESP-IDF-Einbindung des vorhandenen Kerns; Board-Initialisierung und Renderer fehlen bewusst, solange Hardware offen ist.

Nächste Hardwareintegration:

1. Board ist gewählt (Waveshare ESP32-S3-LCD-2). Schaltplan-PDF gegen die SKU prüfen, ESP-IDF-Version pinnen, echtes `app_main` aufsetzen.
2. ST7789T3 über `esp_lcd` initialisieren, Rotation testen. `pet::render` in Streifen aufrufen, z. B. zwei 240×16-Puffer (je 7.680 Byte) im Wechsel per DMA; RGB565 für den Controller ggf. byte-tauschen. Ein Vollbild (153.600 Byte) wäre im PSRAM möglich, ist aber nicht nötig.
3. Drei GPIO-Pegel abtasten und an `Device::input` geben. Bildschirm und Regeln sind fertig; kein JSON und keine zweite Oberfläche nötig.
4. `esp_timer_get_time()` als monotone Laufzeituhr anbinden; Sleep/Resume und Kaltstart getrennt behandeln.
5. 44-Byte-Payload via NVS, Rückgabewerte prüfen, Schreiblast reduzieren; getrennte vertrauenswürdige Wanduhr nur wenn verfügbar.
6. Akku-/Ladezustand, Low-Battery-Verhalten, Backlight/Sleep, Stromverbrauch und physische Einbautests.

Bildschirmparität ist durch den gemeinsamen Renderer hergestellt; Farben, Lesbarkeit und Bildrate müssen am echten LCD noch geprüft werden. Gehäuse, Touch, Audio, Funkkontakte, Qi-Laden und SD-Karten sind noch offen. [UX und Speicherplanung](UX_HARDWARE.md) enthält aktuelle Messungen, Quellennachweise und die Audio-Richtung.

## Testreset außerhalb der Firmware

Nur `desktop/server.py --test-controls` aktiviert `POST /api/reset` mit `confirm: true`. Ohne Flag antwortet der Endpunkt 404. Der Adapter erzeugt eine frische C++-Session mit dem bestehenden Profil, sichert den bisherigen Spielstand unter eindeutigem Namen und schreibt den neuen Stand atomar. Erst danach wird das Session-Handle übernommen. Fehler erhalten die alte laufende Session und den alten Spielstand. Geschwindigkeit/Uhren werden zurückgesetzt. Keine Reset-Aktion im Geräte-Menü, keine neue C++-Spielregel und keine Saveformatänderung.
