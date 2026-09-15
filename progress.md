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
