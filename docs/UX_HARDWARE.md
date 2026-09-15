# Drei Tasten, zwei persönliche Geräte

## Bedienung M2

Die beiden äußeren Tasten bedeuten **vorheriges/nächstes**. Das Display gibt die Richtung vor. Im vertikalen Menü heißen sie hoch/runter, beim Beerenfang links/rechts. Die Zahl der Hardwaretasten begrenzt damit nicht die Länge der Menüs.

| Kontext | Linke Taste | Kurzes OK | Rechte Taste | OK halten |
|---|---|---|---|---|
| Startauswahl | Vorheriges Pokémon | Ei wählen | Nächstes Pokémon | Keine Änderung |
| Zuhause | Status | Menü öffnen | Status | Keine Änderung |
| Menü | Eine Zeile hoch | Aktion ausführen | Eine Zeile runter | Zuhause |
| Status/Ergebnis | Zuhause | Zuhause | Zuhause | Zuhause |
| Pflegehilfe | Menü | Menü | Menü | Menü |
| Beerenfang | Linke Spur | Fangen | Rechte Spur | Abbrechen ohne Belohnung |
| Denkpause, Eingabephase | Linkes Zeichen | Mittleres Zeichen | Rechtes Zeichen | Abbrechen ohne Belohnung |

Das Menü hat zehn Einträge und fünf sichtbare Zeilen. Die Auswahl bleibt sichtbar; Positionszähler, Scrollmarkierung und die untere Tastenlegende helfen bei der Orientierung. Aktionen ohne Wirkung sind gedämpft, bleiben lesbar und erklären, warum sie gerade nicht möglich sind. Die Auswahl springt beim Aufrufen der Pflegehilfe und Zurückkehren nicht weg.

Kurzes OK wird **beim Loslassen** ausgeführt. Nach 700 ms Halten wird genau einmal Zurück ausgelöst; Loslassen darf anschließend kein zusätzliches OK senden. Maus, Touch und Tastatur sind im Simulator berücksichtigt. Auf Hardware muss diese Semantik in einem entprellten GPIO-Adapter umgesetzt und mit echten Tastern geprüft werden. Links/Rechts wiederholen in Auswahl und Menü nach 450 ms alle 160 ms; Loslassen beendet das Blättern. Auf Home und im Minispiel bleiben es einzelne Eingaben.

Langes OK ist ein Zusatzweg. „Zurück“ bleibt im Menü sichtbar. Die Startauswahl benötigt nur einen kurzen Tastendruck. Für später stark wachsende Menüs: Kategorien Pflege/Spiele/Begleiter/Einstellungen mit höchstens einer weiteren Ebene. Noch keine unnötige Untermenüstruktur für zehn Einträge.

## Ein angenehmer Pflegekreislauf

1. **Hinsehen:** Auf dem Startbild Sättigung, Freude und Energie; bei Bedarf eine konkrete Empfehlung. Im Status weitere Werte.
2. **Versorgen:** Beere für Sättigung, Schlaf für Energie, Säubern für Hygiene, Medizin bei Krankheit. Erfolgreiche Aktionen erklären die Wirkung.
3. **Zeit verbringen:** Kurze Spiele bauen Freude, Bindung und Erfahrung auf. Spielen kostet etwas Energie und Nahrung.
4. **Wiederkommen:** Ruhige Phasen sind erlaubt. Kein permanenter Tod im aktuellen Entwurf; Offline-Zeit ist begrenzt.

Futter bleibt vorerst immer verfügbar. Ein leerer Futtervorrat soll das Geschenk nicht in eine Pflicht zum Minispielen verwandeln. Später denkbar: freiwillig verdiente Lieblingssnacks oder Dekoration, ohne die Grundversorgung zu sperren. Energie kommt durch Ruhe, nicht durch dauerhaftes Füttern. Konkrete M1-Werte gelten weiter, siehe RESEARCH.

Die neue Pflegehilfe priorisiert Krankheit, Hygiene, Schlaf, Hunger, Müdigkeit und Langeweile. Emotionen und kleine Animationen dürfen die Zahlen ergänzen; ein sichtbarer Hinweis bleibt wichtig, wenn Audio deaktiviert ist.

## Enton und der kleine Scherz

Neue Spielstände wählen aus 130 Begleitern (129 importierte Sets plus eigener Enton). Die Wahl legt fest, was nach zehn Spielminuten schlüpft. Alte Spielstände behalten ihren Begleiter. Entons Weiterentwicklung ist noch nicht implementiert; die Oberfläche zeigt das ehrlich an.

„Entons Denkpause“ ist ein zweites, bewusst einfaches Minispiel für alle Begleiter: drei Zeichen ansehen, in gleicher Reihenfolge mit Links/OK/Rechts eingeben, drei Runden gewinnen. Jedes Zeichen erscheint 600 ms, gefolgt von 200 ms Abstand. Für die Eingabe gibt es zehn Sekunden pro Runde. Falsche oder fehlende Eingaben enden mit Entons vergesslicher Reaktion. Erfolg: +12 Freude, +6 Bindung, +9 Erfahrung. Kosten wie Beerenfang; kein Gewinn durch Abbrechen. Während beider Spiele pausiert die Pflegezeit.

Weitere Easter Eggs bleiben Ideen: seltene Enton-Kommentare, eine kleine Geschenk-Nachricht am Geburtstag, eine freischaltbare Quatsch-Animation. Dafür noch keine Datenmodelle oder Zufallsbelohnungen eingebaut.

## Persönliche Geräte

Jedes Gerät erhält denselben Programmcode und ein separates `pet::Profile`. Der Name liegt in einem festen Puffer mit maximal 24 UTF-8-Bytes plus Nullabschluss. Profil und Spielstand sind getrennt: Ein Spielstandtransfer ändert nicht den Namen des Geräts. Ungültiges UTF-8, ASCII-Steuerzeichen und zu lange Namen werden abgewiesen; Texte werden im Browser als Text, nicht als HTML verwendet.

Desktop: `config/personalization.example.json` kopieren, z. B. nach `config/geraet-a.local.json`, `trainer_name` eintragen, dann:

```powershell
python desktop/server.py --profile config/geraet-a.local.json --port 8765
python desktop/server.py --profile config/geraet-b.local.json --port 8767
```

Ohne `--save` leitet sich der Speicherdateiname vom Profilnamen ab. `.local.json`-Profile und Saves sind ignoriert und müssen auf dem zweiten Rechner separat angelegt werden. Nur die neutrale Vorlage wird gepusht. Ein vorhandenes Tier explizit mit `--save saves/pet.json` weiterführen; neue Profilnamen sollen nicht unbemerkt alte Spielstände übernehmen.

## Hardware- und Speicherstrategie

RAM und Flash sind getrennte Budgets. Weniger Bytes sind sinnvoll, solange Lesbarkeit, Bildqualität und zuverlässige Pufferung erhalten bleiben. Espressif empfiehlt, erst statischen und dynamischen Verbrauch zu messen, konstante Daten in Flash zu halten und bei Task-Stacks Reserve zu lassen. [Espressif: RAM-Verbrauch reduzieren](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/performance/ram-usage.html)

Bereits umgesetzt:

- Keine Heap-Allokation in `pet::Game`, fest begrenzte Zustände und Ganzzahlarithmetik.
- Sprites aus einer C++-Quelle für beide Plattformen, zur Compilezeit mit 4 Bit pro Pixel gepackt. Ein Palettenindex ist transparent, Farben liegen als RGB565 vor. Keine zur Laufzeit entpackte Vollbildgrafik im Kern.
- Eigener 32×32-Enton und 12×12-Ei; importierte Pokémon mit variablen Framegrößen. Evoli-Entwicklungen teilen noch den Platzhalterumriss mit anderer Palette. Kein Claim fertiger offizieller Sprites.
- Versionierter Save: 44 Byte. Bestehende 42-Byte-V1-Spielstände werden validiert und nach V3 übernommen, ohne ihre Pflegewerte zurückzusetzen.
- Desktop-JSON, Python, Browser-Canvas und HTTP gehören nicht zur Firmware.

| Daten | Am Windows-x64-Build gemessen |
|---|---:|
| `sizeof(pet::Game)`, inklusive State und Minispiel | 64 Byte RAM |
| `sizeof(pet::State)`, bereits in Game enthalten | 32 Byte |
| `sizeof(pet::Profile)` | 25 Byte RAM |
| Bisherige Standgrafiken | 908 Byte konstante Daten |
| Importierte Pixel/Paletten | 770.930 Byte konstante Daten |
| Animationen inklusive Host-Tabellen und Enton-Posen | 974.322 Byte, enthält importierte Pixel/Paletten |
| Animator | 20 Byte RAM |
| Save V3 | 44 Byte |

Dies sind keine Gesamtspeicherwerte der ESP32-Firmware. Code, Texte, Fonts, SDK, Treiber und Puffer fehlen in dieser Rechnung. Pointergrößen und Alignment können auf dem ESP32 abweichen. Tests begrenzen Game auf 128 Byte und Profile auf 25 Byte.

Für den künftigen Displaytreiber: Ein RGB565-Vollbild 240×320 benötigt 153.600 Byte, ein Streifen mit acht Zeilen 3.840 Byte, zwei solcher Streifen 7.680 Byte. Plan ist ein kleiner, wiederverwendbarer Streifenpuffer und Aktualisierung betroffener Bereiche. Ein einzelner RGB565-Pixel braucht zwei Bytes; die Zahlen sind Berechnungen, kein gemessener Treiberverbrauch.

SPI-/I2S-DMA-Puffer benötigen die passenden Speicherfähigkeiten und Alignmentbedingungen des konkreten Controllers. PSRAM nicht pauschal voraussetzen. [Espressif: Heap-Fähigkeiten](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/mem_alloc.html)

Ein Displaypuffer darf bei asynchronem Transfer erst nach dessen Abschluss erneut beschrieben werden. Das muss der spätere Adapter über den Transfer-Abschluss organisieren. [Espressif: LCD-API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/index.html)

Vor Hardwarefreigabe: `idf.py size`, Map-Datei, freier interner Heap, größter freier Block, Stack-Hochwassermarken und Bildübertragungszeit bei Animationen messen. Keine SDK-Stackgrößen auf Verdacht verkleinern. Funk nur initialisieren, wenn eine spätere Funktion es braucht. Displayhelligkeit und Sleep sind für den Akku zusätzlich zu RAM-Optimierung entscheidend.

## Audio später

Noch keine Audiodateien, Audio-Puffer oder stummen Treiber-Attrappen eingebaut. Nach Wahl von Board, Verstärker und Lautsprecher wird ein Audioadapter ergänzt. Spielereignisse wie Füttern, Erfolg oder Hinweis können dann kurze Effekte auslösen; Pflege und Menü dürfen nie auf Ton warten. Lautstärke/Stumm und eine visuelle Alternative gehören dazu. Die konkrete Schnittstelle und Puffergröße richten sich nach der Hardware; aktuell keine Pinbelegung festgelegt.
