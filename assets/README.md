# Grafikherkunft und Animationsimport

Stand: 15.09.2026. 129 importierte Fanart-Sets mit 85 Pokémon und ihren Formen, dazu der eigene Enton: 130 auswählbare Begleiter. Der vollständige [Katalog mit Künstlern, Bedingungen und Quelllinks](ROSTER.md) wird aus dem Importmanifest erzeugt.

## Geprüfte Quelle und Nutzungsbedingungen

Quelle ist [PMDCollab/SpriteCollab](https://github.com/PMDCollab/SpriteCollab) am festen Commit `83681005aa8f37cea7dfe8e68c51aa4b7bf8384a`. Alle Künstler wurden berücksichtigt, nicht nur Emmuffin. Originale PNGs, AnimData.xml und credits.txt liegen unter `vendor/spritecollab/`; `roster.json` dokumentiert deren SHA-256, den Tracker-Hash und sämtliche Ausschlüsse. `credit_names.txt` bleibt als ursprünglicher öffentlicher Namensnachweis erhalten.

Die konkreten Credits verwenden drei historische Kennungen. Die unveränderten Upstream-Texte liegen bei:

- [PMDCollab_1](vendor/spritecollab/LICENSE.PMDCollab_1.md): Nutzung, Kopieren, Weitergabe und Änderungen mit erhaltener Künstlernennung.
- [PMDCollab_2](vendor/spritecollab/LICENSE.PMDCollab_2.md): entsprechende Erlaubnis mit Künstlernennung und ohne Gewinnerzielung.
- [CC_BY-NC_4](vendor/spritecollab/LICENSE.CC_BY-NC_4.md): Creative Commons Attribution NonCommercial 4.0.

Welche Bedingungen ein Set nennt, steht in ROSTER.md und in seiner vollständigen credits.txt-Historie. Die pauschale CC-BY-NC-Beschreibung aus dem ersten Evoli-Import wurde deshalb präzisiert: Emmuffins Evoli Alternate nennt konkret **PMDCollab_1**. Die aktuelle allgemeine Upstream-README und LICENSE.md bleiben zusätzlich erhalten. Es wird keine neue pauschale Lizenz über fremde Dateien gelegt.

Künstler werden im Simulator beim jeweiligen Begleiter genannt; „Über diesen Prototyp“ verlinkt den vollständigen Katalog. Bei Weitergabe von Code oder Gerät Credits, Quellhinweise, Bedingungen und Änderungsvermerk beilegen. Ein Credits-Bildschirm auf dem tatsächlichen Gerät folgt mit dem Hardware-Renderer. Rechte an Pokémon-Figuren und Marken bleiben bei ihren Rechteinhabern; Fanart-Erlaubnisse sind keine Freigabe dieser Marken.

## Auswahl für flüssige Pflegeanimationen

Der Audit untersucht den gesamten gepinnten Tracker und beschränkt sich auf geeignete eigenständige Fan-Sets:

1. Vollständig ausgearbeiteter Upstream-Status (`sprite_complete == 2`) und mindestens 25 benannte Upstream-Aktionen.
2. Neun auflösbare Pflegeabläufe: Idle, Walk, Hop, Pose, Sleep, Eat, Sit, Hurt, LookUp. CopyOf-Verweise werden aufgelöst.
3. Mindestens vier Walk-, vier Hop- und zwei Sleep-Frames, insgesamt mindestens 35 Frames in diesen neun Abläufen. Gültige positive Zeitangaben.
4. Keine CHUNSOFT-Nennung im Tracker oder in der gesamten Credits-Historie; ausschließlich die oben verifizierten Lizenzkennungen.
5. Kein Dex-0000-Platzhalter. Pfade mit Shiny, Altcolor oder Female im Variantennamen werden nicht zusätzlich importiert. Andere Regional-, Typ- und Künstlerformen sind enthalten.

210 vollständig ausgearbeitete Fan-Kandidaten wurden näher untersucht; **129 bestehen**, 81 haben zu wenige passende Pflegeframes. Weitere Ausschlüsse: 665 Original-/Mischsets, 628 nicht vollständig ausgearbeitete Sets, 1.718 der genannten Farb-/Geschlechtsvarianten und acht Nicht-Pokémon-Einträge. Die Kategorien sind die erste zutreffende Ausschlussursache, keine unabhängigen Summen. Das ist eine reproduzierbare Auswahlregel; hohe Framezahl allein garantiert keine künstlerisch gleichmäßige Bewegung.

Importiert werden ausschließlich die vorderen Blickrichtungen: **5.470 Frames, 2.455 unterschiedliche Bitmaps**. Gehen nutzt frontale Schritte mit seitlicher Bildschirmbewegung; vollständige seitliche Laufansichten folgen gegebenenfalls später. Jedes importierte Set enthält über seine neun Clips insgesamt mindestens 14 unterschiedliche Bitmaps.

## Anpassungen und Speicher

Transparente Ränder sind beschnitten, der Registrierungsversatz bleibt erhalten. Farben werden von RGB888 nach RGB565 konvertiert, Bilder innerhalb eines Sets dedupliziert und palettiert gepackt. Die Skalierung bleibt für alle Posen eines Sets ganzzahlig und konstant. Die Laufzeit verwendet XML-Dauern mit 1/30 Sekunde pro Einheit, mindestens 70 ms pro Frame; Evolis große Sprungbewegung wird für das kleine Display vertikal begrenzt.

Alle jetzigen Sets passen in vier Bit pro Pixel: **770.930 Byte für Pixel und Paletten**. Der Importer unterstützt bei Bedarf acht Bit und höchstens 254 sichtbare Farben, lehnt partielle Transparenz und ungültige Geometrie ausdrücklich ab. PNG-/XML-Decoder sind auf dem Gerät nicht nötig. Host-Tabellen und Hardwaregrenzen: [Animationen](../docs/ANIMATION.md).

Deutsche Artnamen stammen aus der [Namenstabelle von PokeAPI](https://github.com/PokeAPI/pokeapi/blob/master/data/v2/csv/pokemon_species_names.csv); URL und Hash der verwendeten Tabelle stehen in roster.json. Es wurden keine PokeAPI-Bilder übernommen. Formen behalten die Upstream-Bezeichnung. Art-IDs sind stabil; neue Einträge werden angehängt, bestehende IDs nicht umnummeriert.

## Eigene Prototypgrafiken

Die SpriteCollab-Standardsets für Enton und Evoli nennen CHUNSOFT und wurden nicht übernommen. Evoli nutzt stattdessen Emmuffins [Alternate-Set](https://github.com/PMDCollab/SpriteCollab/tree/83681005aa8f37cea7dfe8e68c51aa4b7bf8384a/sprite/0133/0002). Enton behält das projektinterne Pixelbild mit eigenen Augen-, Schnabel- und Fußposen. Ei, Psiana und Nachtara bleiben eigene Platzhalter; für die beiden Entwicklungen fehlen eigenständige Frame-Sets.

## Reproduzieren

Ein normaler Build verwendet die eingecheckten konstanten C++-Daten und benötigt weder Netzwerk noch Pillow.

```powershell
# Nur bei bewusster Pflege des Katalogs: Online-Audit mit lokalem Cache unter output/
python scripts/acquire_roster.py
# Offline aus den vorhandenen Quellen generieren (Pillow erforderlich)
python scripts/import_sprites.py
python scripts/import_sprites.py --check
# Nach dem C++-Build: unabhängiger Pixelvergleich, ebenfalls mit Pillow
python tests/verify_sprite_import.py
```

Der Offline-Importer erzeugt `src/roster_frames.inc`, `roster_compiled.json` und ROSTER.md. Geprüft mit Pillow 12.3.0. `--check` verifiziert Quellhashes und deterministische Ausgabe; der separate Pixelvergleich prüft 12.146.208 Quellpixel einschließlich transparenter Ränder gegen die tatsächlich kompilierte Bibliothek. Credits und Lizenztexte bei einer zukünftigen Änderung erneut prüfen. Wechsel des Quellcommits erfordert einen frischen Cache und erneute Rechte-/Speicherprüfung.

## Eigene Naturkulisse

Die Waldlichtung wurde mit OpenAI Imagegen für das Projekt erstellt. Displayfassung, Quellbild, technischer Import und vollständiger Prompt: [backgrounds/README.md](backgrounds/README.md). Die größere Figurendarstellung verändert keine SpriteCollab-Quellbilder; der C++-Renderer begrenzt die Platzierung der skalierten Frames.

## Pixelschrift des Geräts

Die 5×9-Schrift in `scripts/make_font.py` (erzeugt `src/font.inc`) wurde am 28.10.2026 eigens für Pocket Pet gezeichnet; keine fremde Schriftdatei übernommen. Sie deckt ASCII, ÄÖÜäöüß und einige Symbole (♥ ★ ◀ ▶ ▲ ▼ … · °) ab.
