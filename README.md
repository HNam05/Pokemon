# Pocket Pet

Ein Pokémon-inspiriertes Tamagotchi für einen späteren ESP32 im aufklappbaren, 3D-gedruckten Pokéball. **Software zuerst:** ein spielbarer PC-Simulator mit demselben C++17-Kern, der später auf dem Gerät laufen soll. Normales Display, drei Tasten, kein Touch erforderlich.

## Jetzt spielbar

Aus 130 Begleitern wählen: 129 SpriteCollab-Sets mit 85 Pokémon und ihren Formen sowie unser eigener Enton. Danach das Ei ausbrüten, füttern und säubern, schlafen lassen, Krankheiten behandeln, Beeren fangen und Entons Denkpause spielen. Evoli kann sich zu Psiana oder Nachtara entwickeln. Mit scrollendem Menü, persönlichen Profilen, 240×320-Display-Simulation und kompakten gemeinsamen C++-Pixelgrafiken.

**Stand:** erster Desktop-Prototyp. ESP32-Treiber, endgültige Grafik und Hardwarevalidierung folgen nach Auswahl der Komponenten.

Die Begleiter bewegen sich jetzt zustandsabhängig: zufälliges Gehen, Hüpfen, Umsehen und Freude mit Ruhepausen, Essreaktion nach dem Füttern sowie Schlaf-/Erschöpfungsposen. Die Auswahl berücksichtigt Beiträge aller Künstler im geprüften SpriteCollab-Stand. Als Begleiter sind unter anderem Fynx, Bauz, Wolly und Felori dabei. Jedes importierte Set bietet neun Pflegeabläufe. Enton nutzt eigene animierte Prototypposen. Die Auswahl und Zeitsteuerung laufen ebenfalls im C++-Kern. Details und Herkunft: [Animationen](docs/ANIMATION.md), [Grafik-Credits](assets/README.md).

## Starten

Voraussetzungen: Python 3.10+, CMake 3.20+ und C++17-Compiler (Windows: Visual Studio Build Tools mit C++-Workload; Linux: GCC/Clang; macOS: Xcode Command Line Tools). Keine Python-Pakete und keine npm-Installation für den Simulator erforderlich.

```powershell
python scripts/build.py
python desktop/server.py
```

Im Browser [127.0.0.1:8765](http://127.0.0.1:8765) öffnen. Mit Strg+C den Server beenden und speichern. Er bindet ausschließlich an Loopback. Der Browser allein führt keine Spiellogik aus.

**Auf diesem Arbeitsrechner ohne installierten C++-Compiler:** ein lokaler, ignorierter Zig-Compiler wurde bereitgestellt. Damit bauen:

```powershell
$env:ZIG_GLOBAL_CACHE_DIR = Join-Path (Get-Location) '.tools/zig-cache'
python scripts/build.py --zig .tools/zig-x86_64-windows-0.15.2/zig.exe
python desktop/server.py
```

Auf einem anderen Rechner entweder die CMake-Variante nutzen oder eine passende offizielle [Zig-Distribution](https://ziglang.org/download/) lokal entpacken und `--zig <pfad>` angeben. Zig wird hier nur als C++-Compiler verwendet. Download der Windows-Version 0.15.2 in dieser Runde anhand des offiziellen SHA-256 geprüft: `3a0ed1e8799a2f8ce2a6e6290a9ff22e6906f8227865911fb7ddedc3cc14cb0c`.

## Bedienung

| Taste | Home | Menü | Beerenfang |
|---|---|---|---|
| Links / ← oder ↑ | Status | Eine Zeile hoch | Linke Spur |
| Mitte / Enter | Menü | Bestätigen | Beere fangen |
| Rechts / → oder ↓ | Status | Eine Zeile runter | Rechte Spur |

Alle Aktionen sind mit drei Tasten erreichbar. Fünf Menüzeilen bleiben sichtbar; längere Listen scrollen mit. Kurzes OK bestätigt beim Loslassen, **OK halten (700 ms)** führt zurück. Im Menü gibt es zusätzlich „Zurück“. Im Beerenfang die Beere im markierten Fangbereich mit OK fangen; fünf Versuche. In Entons Denkpause drei Zeichen merken und über die drei Tasten wiederholen. `F` öffnet die Vollbildansicht, `Esc` verlässt sie.

Neue Spielstände beginnen mit der vollständigen Begleiterauswahl. Seitentasten wechseln einzeln; Halten blättert automatisch durch Auswahl oder Menü (450 ms Anlauf, anschließend alle 160 ms). Mit OK bestätigen, danach schlüpft das gewählte Ei nach zehn Spielminuten. Für den Einstieg im Simulator **+ 10 Minuten** drücken. Standard ist Echtzeit; Zeitraffer beschleunigt die Pflege, beide Minispiele behalten normale Reaktionszeiten. Pflegewerte stehen unter „Status“, konkrete Empfehlungen unter „Pflegehilfe“. Evoli-Entwicklung braucht 1 Tag, 70 Freundschaft, 60 EP und ein gesundes, waches Tier. Entwicklung weiterer Arten ist noch offen; neue Begleiter verwenden dieselben Pflegeregeln.

## Zwei persönliche Geräte

Die gleiche Software unterstützt getrennte Namen und Speicherdateien. `config/personalization.example.json` als `config/geraet-a.local.json` und `config/geraet-b.local.json` kopieren und jeweils `trainer_name` eintragen (maximal 24 UTF-8-Bytes). Die persönlichen Dateien sind von Git ausgeschlossen.

```powershell
python desktop/server.py --profile config/geraet-a.local.json --port 8765
python desktop/server.py --profile config/geraet-b.local.json --port 8767
```

Ohne `--save` verwendet jedes Profil eine eigene gleichnamige Speicherdatei unter `saves/`. Ein bestehendes Tier mit `--save saves/pet.json` weiterführen. Namen werden unabhängig vom Spielstand verwaltet. Lokale Profile auf dem zweiten Rechner separat anlegen.

## Speichern und Tests

Spielstände liegen in `saves/pet.json`, automatisch alle 30 Sekunden und nach Eingaben. Beim Neustart werden höchstens acht Stunden reale Abwesenheit nachgerechnet. Kaputte/unbekannte Spielstände werden nicht überschrieben; der Server erklärt den Fehler. Für ein **separates neues Tier** einen neuen Pfad benutzen: `python desktop/server.py --save saves/zweites-tier.json`. Eine Betriebssystem-Sperre verhindert zwei Server mit derselben Speicherdatei. Das 44-Byte-Format V3 liest bestehende V1-/V2-Stände und erhält deren Begleiter. Vor einem Downgrade eine alte Sicherung verwenden.

Der Build führt die C++-Tests aus. Weitere Adaptertests:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Browser-Testanleitung und tatsächlicher Prüfstand stehen in [docs/VALIDATION.md](docs/VALIDATION.md). Builds und Tests auf weiteren Betriebssystemen sind noch nicht bestätigt.

## Dokumentation

- [Drei-Tasten-UX, Pflegekonzept, Profile und Speicherbudget](docs/UX_HARDWARE.md)
- [Recherche, Quellen und Spielregeln](docs/RESEARCH.md)
- [Architektur, Speicherformat und Hardware-Port](docs/ARCHITECTURE.md)
- [Git- und Modell-Zusammenarbeit](docs/COLLABORATION.md)
- [Übergabe und nächste Schritte](progress.md)

Privates, inoffizielles Fanprojekt. Pokémon-Namen und -Figuren gehören ihren jeweiligen Rechteinhabern. Keine Firmware oder Grafiken des MakerWorld-Projekts übernommen. SpriteCollab-Fanart: individuelle Künstler und historische Nutzungsbedingungen in [ROSTER.md](assets/ROSTER.md). Originale Credits, Lizenztexte und dokumentierte Anpassungen liegen bei; Ei, Enton und Evoli-Entwicklungen sind eigene Prototypgrafiken. Die Rechte am Fanmaterial sind nicht durch eine pauschale Open-Source-Lizenz dieses Repositories freigegeben. Siehe [vollständige Grafik-Credits](assets/README.md).
