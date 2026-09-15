# Architektur und ESP32-Port

## Entscheidung

C++17 für Spielregeln und Spielzustandsmaschine. Ein Kern für Desktop und ESP32. CMake baut ohne Fremdbibliotheken. Standard-C++ statt Arduino-Aufrufe im Kern erleichtert reproduzierbare Tests vor dem Hardwarekauf.

Ein natives Fenster mit SDL wäre ebenfalls möglich, verlangt aber eine zusätzliche Grafik-Abhängigkeit. Der erste PC-Simulator nutzt deshalb Canvas im Browser und eine lokale Python-Standardbibliothek-Brücke zu einer **kompilierten C++-Bibliothek**. JavaScript zeichnet ausschließlich und transportiert Eingaben. Kein doppeltes Implementieren der Spielregeln, kein Cloud-Service, kein WebAssembly-Toolchain-Zwang.

```text
Drei Tasten / Tastatur -> lokaler Python-Server -> C ABI -> pet::Game
                                               |
                           Zustandsansicht <----+
                                  |
                         Browser-Canvas 240x320

Später: GPIO -> entprellte Button-Ereignisse -> derselbe pet::Game
                                            |
                                  LCD-Renderer + NVS-Adapter
```

## Dateien und Verantwortlichkeiten

| Pfad | Zweck |
|---|---|
| `include/pet/game.hpp`, `src/game.cpp` | Zustände, Aktionen, Minuten-/Reaktionszeit, Entwicklung, deterministischer Zufall |
| `include/pet/save.hpp`, `src/save.cpp` | 44-Byte-V2-Format, V1-Migration, Little Endian, CRC32, Werteprüfung |
| `include/pet/sprite.hpp`, `src/sprite.cpp` | Gemeinsame gepackte 4-Bit-Palettengrafik, RGB565-Farben |
| `include/pet/profile.hpp` | Festes Namensprofil, UTF-8-Prüfung, unabhängig vom Spielstand |
| `include/pet/animation.hpp`, `src/animation.cpp` | Kosmetische Zustandsmaschine mit eigenem Zufall, Echtzeit-Frames und begrenzter Bewegung |
| `src/eevee_frames.inc`, `scripts/import_sprites.py`, `assets/` | Gepinnte Fanart, Offline-Import, Quellhashes, Credits und komprimierte konstante Frames |
| `desktop/bridge.cpp` | C ABI für Spiel, Profil, Menühinweise und Sprite-Daten. Profilname separat vom formatierten JSON; Python übernimmt korrektes Escaping. |
| `desktop/server.py` | Loopback-HTTP, monotone Uhr, atomare lokale Speicherung, begrenzte Offline-Zeit |
| `desktop/web/` | Responsive Simulator-Ansicht, eigenes Pixelbild, Maus/Tastatur und zugängliche Statusbeschreibung |
| `tests/` | Regeln, Grenzwerte, Korruption, Integration und Browserabläufe |

`pet::Game` besitzt keine Heap-Allokationen, Dateipfade, GPIO-Abhängigkeiten oder Wanduhraufrufe. Es nimmt höchstens 60.000 reale Millisekunden und Geschwindigkeit 0…3600 pro `advance` entgegen; längere Intervalle müssen vom Adapter zerlegt werden. Pflege wird minutengenau und mit gespeichertem Millisekundenrest berechnet. Im aktiven Minispiel läuft nur dessen Uhr. Aufrufe erfolgen aus einem Thread/Task.

## Spielstandformat V2 und Migration

44 Bytes: stabile Magic ASCII `PET1` (4), Version (u16=2), Länge (u16=44), Alter/Rest-ms/PRNG/EP (je u32), Tagesminute/Vernachlässigung (je u16), Sättigung/Glück/Energie/Hygiene/Gesundheit/Bindung/Abfall/Art/Schlaf/Krankheit (je u8), Starter-Art und Auswahl-bestätigt (je u8), CRC32 über Bytes 0…39 (u32). CRC32 ist Fehlererkennung, keine Authentifizierung. Struktur-Padding wird nie gespeichert.

V1 mit 42 Bytes und CRC über Bytes 0…37 wird weiter gelesen: Starter Evoli, Auswahl bereits bestätigt. Werte und gewachsene Art bleiben unverändert. Enton ist in V1 nicht zulässig. V2 wird beim nächsten Speichern geschrieben. Alte Programmversionen können V2 nicht lesen; vor Downgrade eine V1-Sicherung verwenden.

Beim Lesen müssen Länge, Version, Prüfsumme, Boolwerte und Wertebereiche stimmen. Dekodierung und Restore sind transaktional: Fehler verändern das laufende Spiel nicht. Unbekannte Versionen werden abgewiesen; künftige Migrationen explizit ergänzen.

Desktop-Hülle: JSON mit `version`, `saved_at` als Unix-Sekunden und hexkodiertem Payload. Schreiben in temporäre Datei, Flush/fsync, dann `os.replace`. Nach jeder Taste, manuellem Speichern, Zeitsprung und alle 30 Sekunden. Fehler sichtbar in der Oberfläche. Ein kaputter gespeicherter Stand bricht den Serverstart ab und wird nicht überschrieben. Eine Betriebssystem-Sperre verhindert mehrere Server für dieselbe Speicherdatei und wird auch bei einem Prozessabbruch freigegeben. Saves gehören nicht ins Git.

## Drei-Tasten-Vertrag

- Home: Mitte öffnet Menü, beide Seitentasten öffnen Status.
- Startauswahl: Seitentasten wechseln Evoli/Enton, Mitte bestätigt; vorher läuft keine Pflegezeit.
- Menü: Seitentasten scrollen vertikal durch zehn Einträge mit fünf sichtbaren Zeilen; Mitte aktiviert. „Zurück“ ist ein expliziter Eintrag. Beschriftungen und Hinweise kommen aus C++.
- Status/Ergebnis: beliebige Taste zurück.
- Beerenfang: Links/Rechts bewegen begrenzt auf drei Spuren, Mitte ist ein Fangversuch.
- Denkpause: drei Zeichen ansehen, dann über Links/OK/Rechts wiederholen; drei Runden, begrenzte Eingabezeit, Pflegezeit pausiert.

Auf Hardware später active-low + Pull-up nach Schaltplan, Entprellung etwa 25–40 ms. Kurzes OK beim Loslassen; nach 700 ms einmal `Game::back()` und kurzes OK unterdrücken. Keine Button-ISR führt Spiellogik aus. Der Simulator prüft diese UX, der echte GPIO-Adapter folgt mit der Boardintegration.

## Portierung: ehrlicher Stand

Der Kern ist plattformneutral und am PC kompiliert/getestet. **Es existiert noch keine getestete oder flashbare ESP32-Firmware.** `firmware/components/pet_core` bietet die ESP-IDF-Einbindung des vorhandenen Kerns; Board-Initialisierung und Renderer fehlen bewusst, solange Hardware offen ist.

Für M2:

1. Board/SKU und Schaltplan fixieren, ESP-IDF-Version pinnen, echtes `app_main` aufsetzen.
2. SPI/ST7789 oder tatsächlichen Controller initialisieren, Displayrotation testen. RGB565-Vollbild benötigt bei 240×320 etwa 150 KiB; Teilbereiche oder Zeilenpuffer bevorzugen, PSRAM nur bei bestätigter Ausstattung.
3. Entprellte Tastenadapter implementieren, dieselbe Zustandsansicht rendern. Für eingebettete Ausgabe direkt C++-State verwenden, kein JSON nötig.
4. `esp_timer_get_time()` als monotone Laufzeituhr anbinden; Sleep/Resume und Kaltstart getrennt behandeln.
5. 44-Byte-Payload via NVS, Rückgabewerte prüfen, Schreiblast reduzieren; getrennte vertrauenswürdige Wanduhr nur wenn verfügbar.
6. Akku-/Ladezustand, Low-Battery-Verhalten, Backlight/Sleep, Stromverbrauch und physische Einbautests.

Vollständige Bildschirmparität muss im Hardware-Renderer noch hergestellt werden. Gehäuse, Touch, Audio, Funkkontakte, Qi-Laden und SD-Karten sind noch offen. [UX und Speicherplanung](UX_HARDWARE.md) enthält aktuelle Messungen, Quellennachweise und die Audio-Richtung.
