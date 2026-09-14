# Pocket Pet

Ein Pokémon-inspiriertes Tamagotchi für einen späteren ESP32 im aufklappbaren, 3D-gedruckten Pokéball. **Software zuerst:** ein spielbarer PC-Simulator mit demselben C++17-Kern, der später auf dem Gerät laufen soll. Normales Display, drei Tasten, kein Touch erforderlich.

## Jetzt spielbar

Ei ausbrüten, Evoli füttern und säubern, schlafen lassen, Krankheiten behandeln, Beeren fangen, Freundschaft aufbauen und zu Psiana oder Nachtara entwickeln. Mit 240×320-Display-Simulation, Zeitraffer, Speicherständen und selbst gezeichneten Pixel-Platzhaltern.

**Stand:** erster Desktop-Prototyp. ESP32-Treiber, endgültige Grafik und Hardwarevalidierung folgen nach Auswahl der Komponenten.

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
| Links / ← | Status | Vorheriger Eintrag | Linke Spur |
| Mitte / Enter | Menü | Bestätigen | Beere fangen |
| Rechts / → | Status | Nächster Eintrag | Rechte Spur |

Alle Aktionen sind mit drei Tasten erreichbar. Status und Ergebnis mit beliebiger Taste verlassen. Im Menü gibt es „Zurück“. Im Minispiel die Beere im markierten Fangbereich mit OK fangen; fünf Versuche. `F` öffnet die Vollbildansicht, `Esc` verlässt sie.

Das Ei schlüpft nach zehn Spielminuten. Für den Einstieg im Simulator **+ 10 Minuten** drücken. Standard ist Echtzeit; Zeitraffer beschleunigt die Pflege, das Minispiel behält normale Reaktionszeiten. Pflegewerte stehen unter „Status“. Entwicklung braucht 1 Tag, 70 Freundschaft, 60 EP und ein gesundes, waches Tier; Details in der Recherche.

## Speichern und Tests

Spielstände liegen in `saves/pet.json`, automatisch alle 30 Sekunden und nach Eingaben. Beim Neustart werden höchstens acht Stunden reale Abwesenheit nachgerechnet. Kaputte/unbekannte Spielstände werden nicht überschrieben; der Server erklärt den Fehler. Für ein **separates neues Tier** einen neuen Pfad benutzen: `python desktop/server.py --save saves/zweites-tier.json`. Eine Betriebssystem-Sperre verhindert zwei Server mit derselben Speicherdatei.

Der Build führt die C++-Tests aus. Weitere Adaptertests:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Browser-Testanleitung und tatsächlicher Prüfstand stehen in [docs/VALIDATION.md](docs/VALIDATION.md). Builds und Tests auf weiteren Betriebssystemen sind noch nicht bestätigt.

## Dokumentation

- [Recherche, Quellen und Spielregeln](docs/RESEARCH.md)
- [Architektur, Speicherformat und Hardware-Port](docs/ARCHITECTURE.md)
- [Git- und Modell-Zusammenarbeit](docs/COLLABORATION.md)
- [Übergabe und nächste Schritte](progress.md)

Privates, inoffizielles Fanprojekt. Pokémon-Namen und -Figuren gehören ihren jeweiligen Rechteinhabern. Keine Firmware oder Grafiken des MakerWorld-Projekts übernommen; eigene Software und Platzhaltergrafik. Die Rechte am Fanmaterial sind nicht durch eine pauschale Open-Source-Lizenz dieses Repositories freigegeben.
