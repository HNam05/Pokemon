# Pocket Pet

Ein Pokémon-inspiriertes Tamagotchi für einen späteren ESP32 im aufklappbaren, 3D-gedruckten Pokéball. **Software zuerst:** ein spielbarer PC-Simulator mit demselben C++17-Kern, der später auf dem Gerät laufen soll. Normales Display, drei Tasten, kein Touch erforderlich.

## Jetzt spielbar

Aus 130 Begleitern wählen: 129 SpriteCollab-Sets mit 85 Pokémon und ihren Formen sowie unser eigener Enton. Danach das Ei ausbrüten, füttern, streicheln und säubern, schlafen lassen, Krankheiten behandeln, Beeren fangen und Entons Denkpause spielen. Der Begleiter **ruft**, wenn er etwas braucht; ignorierte Rufe werden zu Pflegefehlern, ein guter Tag verzeiht einen. Er wächst vom Baby zum Kind und zum Erwachsenen, steigt im Level, schläft ab 21 Uhr und wacht um 7 Uhr auf. Sieben Linien können sich bei guter Pflege entwickeln: Evoli, Pichu, Lilminip, Fynx, Psiau, Wuffels und Typ:Null.

**Stand:** Desktop-Prototyp mit gerätefertigem Kern. Seit 28.10.2026 erzeugt C++ den kompletten 240×320-Bildschirm und wertet die drei Tasten aus; der Browser zeigt nur noch die fertigen Pixel. ESP32-Treiber (LCD, GPIO, NVS) und Hardwarevalidierung folgen nach Prüfung des Schaltplans.

## 3D-Gehäuseprototyp

V1 war ein integrierter Geräteentwurf. V2 setzt die bestätigte Idee um: Das Tamagotchi ist ein eigenständiges, herausnehmbares Handheld, das in der geöffneten Pokéball-Schutzhülle sitzt. CAD-Quellen, Maße, Montagehinweise und druckbare STL-/STEP-/3MF-Dateien: [V2-Prototyp](hardware/pokeball_v2/README.md) und [Druckpaket](hardware/pokeball_v2/release/README.md). Zuerst die Passproben drucken; digitale Passungsprüfungen ersetzen keine reale Montage.

Die Begleiter bewegen sich jetzt zustandsabhängig: zufälliges Gehen, Hüpfen, Umsehen und Freude mit Ruhepausen, Essreaktion nach dem Füttern sowie Schlaf-/Erschöpfungsposen. Die Auswahl berücksichtigt Beiträge aller Künstler im geprüften SpriteCollab-Stand. Als Begleiter sind unter anderem Fynx, Bauz, Wolly und Felori dabei. Jedes importierte Set bietet neun Pflegeabläufe. Enton nutzt eigene animierte Prototypposen. Die Auswahl und Zeitsteuerung laufen ebenfalls im C++-Kern. Größere Begleiter stehen vor einer Pixelart-Waldlichtung mit Bach, Beeren und Tag-/Nachtfarben. Details und Herkunft: [Animationen](docs/ANIMATION.md), [Grafik-Credits](assets/README.md).

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

Alle Aktionen sind mit drei Tasten erreichbar. Fünf Menüzeilen bleiben sichtbar; die zwölf Einträge scrollen mit. Entprellung (30 ms), langes OK und Blättern wertet derselbe C++-Decoder aus, der später die GPIO-Pegel liest. Unter „Uhr stellen“ lässt sich die Tageszeit mit den drei Tasten einstellen. Kategorien und Hinweise erklären die gewählte Aktion. Kurzes OK bestätigt beim Loslassen, **OK halten (700 ms)** führt zurück. Im Menü gibt es zusätzlich „Zurück“. `F` öffnet die Vollbildansicht, `Esc` verlässt sie.

Beide Spiele zeigen zuerst eine kostenlose Anleitung. Erst **OK: Start** verbraucht 5 Satt und 8 Energie. Im Beerenfang den Korb bewegen und im markierten Fangfeld OK drücken; fünf Versuche mit kurzer Rückmeldung nach jeder Beere. In **Entons Denkpause** wächst dieselbe Folge von zwei auf drei und vier Zeichen. Erst ansehen, dann Links/OK/Rechts nachspielen. Bereits gelöste Runden zählen bei einem späteren Fehler oder Zeitablauf; manueller Abbruch bringt keine Belohnung. Ergebnisse zeigen den tatsächlichen Zuwachs nach Begrenzung auf die Maximalwerte.

Satt, Froh und Energie haben Zahlenwerte und Balken auf Home und neben dem Simulator. Warnfarben entsprechen den Pflegegrenzen des C++-Kerns. Füttern, Säubern und Medizin zeigen kurz ihre tatsächliche Wirkung; Schlaf regeneriert Energie mit der Spielzeit.

Neue Spielstände beginnen mit der vollständigen Begleiterauswahl. Seitentasten wechseln einzeln; Halten blättert automatisch durch Auswahl oder Menü (450 ms Anlauf, anschließend alle 160 ms). Mit OK bestätigen, danach schlüpft das gewählte Ei nach zehn Spielminuten. Für den Einstieg im Simulator **+ 10 Minuten** drücken. Standard ist Echtzeit; Zeitraffer beschleunigt die Pflege, beide Minispiele behalten normale Reaktionszeiten. Pflegewerte stehen unter „Status“, konkrete Empfehlungen unter „Pflegehilfe“. Evoli-Entwicklung braucht 1 Tag, 70 Freundschaft, 60 EP und ein gesundes, waches Tier. Entwicklung weiterer Arten ist noch offen; neue Begleiter verwenden dieselben Pflegeregeln.

## Testspielstand zurücksetzen (nur Simulator)

Für wiederholte Testläufe den Simulator ausdrücklich mit `--test-controls` starten:

```powershell
python desktop/server.py --port 8768 --save output/roster-preview.json --test-controls
```

Unter den Simulator-Hilfen erscheint „Testspielstand zurücksetzen“. Nach Bestätigung beginnt die Pokémon-Auswahl neu; Profilname bleibt erhalten, Geschwindigkeit wird auf Echtzeit gesetzt. Der bisher gespeicherte Stand bleibt daneben als `*.reset-<zeitpunkt>.bak` erhalten. Bei Schreibfehlern bleibt auch die laufende Sitzung erhalten. Ohne Flag sind Button und Reset-Endpunkt deaktiviert. Die Funktion liegt ausschließlich im Desktop-Adapter und gehört nicht zur ausgelieferten ESP32-Bedienung.

## Zwei persönliche Geräte

Die gleiche Software unterstützt getrennte Namen und Speicherdateien. `config/personalization.example.json` als `config/geraet-a.local.json` und `config/geraet-b.local.json` kopieren und jeweils `trainer_name` eintragen (maximal 24 UTF-8-Bytes). Die persönlichen Dateien sind von Git ausgeschlossen.

```powershell
python desktop/server.py --profile config/geraet-a.local.json --port 8765
python desktop/server.py --profile config/geraet-b.local.json --port 8767
```

Ohne `--save` verwendet jedes Profil eine eigene gleichnamige Speicherdatei unter `saves/`. Ein bestehendes Tier mit `--save saves/pet.json` weiterführen. Namen werden unabhängig vom Spielstand verwaltet. Lokale Profile auf dem zweiten Rechner separat anlegen.

## Speichern und Tests

Spielstände liegen in `saves/pet.json`, automatisch alle 30 Sekunden und nach Eingaben. Beim Neustart werden höchstens acht Stunden reale Abwesenheit nachgerechnet. Kaputte/unbekannte Spielstände werden nicht überschrieben; der Server erklärt den Fehler. Für ein **separates neues Tier** einen neuen Pfad benutzen: `python desktop/server.py --save saves/zweites-tier.json`. Eine Betriebssystem-Sperre verhindert zwei Server mit derselben Speicherdatei. Das 48-Byte-Format V4 liest bestehende V1-/V2-/V3-Stände, erhält deren Begleiter und Werte und startet mit sauberer Pflegebilanz. Vor einem Downgrade eine alte Sicherung verwenden; ältere Programmstände können V4 nicht lesen.

Der Build führt die C++-Tests aus. Weitere Adaptertests und Browser-Smokes (Playwright/Chromium):

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
node tests/browser_smoke.mjs
```

Weitere Smokes: `ux_smoke.mjs`, `animation_smoke.mjs`, `roster_smoke.mjs`, `reset_smoke.mjs`. Nach Änderungen an der Pixelschrift `python scripts/make_font.py` ausführen.

Browser-Testanleitung und tatsächlicher Prüfstand stehen in [docs/VALIDATION.md](docs/VALIDATION.md). Builds und Tests auf weiteren Betriebssystemen sind noch nicht bestätigt.

## Dokumentation

- [Drei-Tasten-UX, Pflegekonzept, Profile und Speicherbudget](docs/UX_HARDWARE.md)
- [Recherche, Quellen und Spielregeln](docs/RESEARCH.md)
- [Architektur, Speicherformat und Hardware-Port](docs/ARCHITECTURE.md)
- [Git- und Modell-Zusammenarbeit](docs/COLLABORATION.md)
- [Übergabe und nächste Schritte](progress.md)

Privates, inoffizielles Fanprojekt. Pokémon-Namen und -Figuren gehören ihren jeweiligen Rechteinhabern. Keine Firmware oder Grafiken des MakerWorld-Projekts übernommen. SpriteCollab-Fanart: individuelle Künstler und historische Nutzungsbedingungen in [ROSTER.md](assets/ROSTER.md). Originale Credits, Lizenztexte und dokumentierte Anpassungen liegen bei; Ei, Enton und Evoli-Entwicklungen sind eigene Prototypgrafiken. Die Rechte am Fanmaterial sind nicht durch eine pauschale Open-Source-Lizenz dieses Repositories freigegeben. Siehe [vollständige Grafik-Credits](assets/README.md).
