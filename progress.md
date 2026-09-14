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
