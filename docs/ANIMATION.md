# Zustandsabhängige Animationen

Die Auswahl und Zeitsteuerung liegen in `pet::Animator`, unabhängig von `pet::Game`. Beide sind portables C++17 ohne Heap-Allokationen. Browser und spätere Hardware bekommen dieselben Clip-/Frame- und Positionsdaten.

## Verhalten

| Zustand | Darstellung |
|---|---|
| Gesund, satt, wach | Zufällig Gehen, Umsehen, Hüpfen oder Freude; dazwischen 2–5 Sekunden Ruhe |
| Hunger unter 25 oder Freude unter 30 | Umsehen und Gehen, keine spontanen Jubel-/Sprungsequenzen |
| Energie unter 25 | Ruhige, müde Pose |
| Krank oder Gesundheit unter 40 | Krankheits-/Erschöpfungspose |
| Schlafend | Schlafablauf; hat auch bei Krankheit Vorrang |
| Erfolgreich gefüttert und fit | 2,2 Sekunden Essen, danach Ruhe |

Aktive spontane Clips dauern 1,6–3,4 Sekunden. Die Wahl fällt am Ende eines Clips, nicht bei jedem Bild. Animationen laufen in echter Zeit, unabhängig vom Pflege-Zeitraffer; „Pause“ friert die Pose ein. Außerhalb des Home-Screens pausiert die Animationsuhr. Startauswahl, Minispiel und Ergebnis verwenden bewusst eine ruhige Vorschau. Zustandssprünge werden auch bei null verstrichener Zeit synchronisiert.

Der kosmetische Xorshift-PRNG besitzt einen eigenen Seed. Der Desktop erzeugt ihn aus dem Betriebssystem; bei manueller Testuhr ist er fest 42. Hardware übergibt später einen Seed aus ihrem Adapter. Er verändert weder `State::rng` noch Pflegeregeln und wird nicht gespeichert. Der Animationszustand bleibt unabhängig vom Spielstand; das Katalogupdate verwendet V3 mit weiterhin 44 Bytes. Ohne gespeicherten Animationszustand kann beim Neustart eine andere Bewegung beginnen.

Bei „reduzierte Bewegung“ im Browser bleibt ein zum Zustand passendes Standbild ohne Positionsbewegung sichtbar. Es gibt keine Browser-Zufallslogik und keinen zweiten Pflegealgorithmus. Das Umschalten von Clip, Frame und Position kommt vollständig aus C++; nur die barrierearme statische Darstellung ist ein Renderer-Modus.

## Darstellung und Daten

Herkunft und konkrete Rechte aller 129 Fanart-Sets stehen in [assets/README.md](../assets/README.md) und [ROSTER.md](../assets/ROSTER.md). Neun Cliptypen enthalten insgesamt 5.470 Frames und teilen sich 2.455 verschiedene Bitmaps. Enton benutzt eigene zusätzliche Posen. Es wird nur die vordere Blickrichtung importiert; Gehen ist daher ein frontaler Schritt mit seitlicher Bewegung, noch kein vollständiger Satz seitlicher Laufansichten.

`animation_frame` liefert ein palettiertes Sprite, X/Y-Versatz relativ zum gemeinsamen Mittelpunkt und Anzeigedauer. Transparente Randbereiche kosten keinen Pixel-Speicher. Der Versatz bleibt erhalten, damit Hüpfen und Schlafen nicht durch automatisches Zentrieren ungewollt verrutschen. Bildschirmbewegung ist begrenzt; Gehen kehrt zur Mitte zurück. Der Home-Renderer beschneidet auf die Landschaft, damit kein Frame die Statusleisten übermalt.

Der Browser lädt die Frames vom lokalen C++-Adapter bedarfsgerecht und baut Canvas-Bitmaps für die Darstellung. Neben den fünf bisherigen Arten bleiben höchstens vier weitere Sets im Cache; ein verdrängtes Set wird bei Bedarf erneut geladen. Danach braucht ein Bildwechsel nur `drawImage`. Home-Abfragen etwa alle 60 ms, im pausierten Spiel etwa alle 400 ms. Der Browser läuft vollständig offline, ohne Grafik-CDN.

## Speicherstand vom Host-Build

Die Begleiter erhalten eine größere ganzzahlige Skalierung für sämtliche Posen ihrer Art. Evoli verwendet 5×, Enton 4×. Der Importer erhöht die bisherige Skalierung um eine Stufe, begrenzt auf 180 Pixel Breite und 168 Pixel Höhe des größten Bildes. `place_frame` im C++-Kern berechnet anschließend die endgültige Position einschließlich Spiegelung und Bewegung; sichtbare Grenzen sind X=8…232 und Y=42…210. Die Originalregistrierung der Quellbilder bleibt für unabhängige Pixelprüfungen erhalten. Große Sprünge können an der Szenengrenze eine kürzere sichtbare Flugbahn haben; die Pixelbilder werden dabei weder gestaucht noch abgeschnitten.

Die C-ABI liefert `draw_x`, `draw_y` und `scale` für bewegte und ruhige Frames. Der Browser übernimmt diese Werte auch für reduzierte Bewegung. Die Auswahl vergrößert ihre ruhige Vorschau innerhalb eines eigenen 128-Pixel-Bereichs.

- Spielkern unverändert: `Game` 64 Byte, darin `State` 32 Byte.
- Zusätzlicher `Animator`: 20 Byte, statische Obergrenze 32 Byte.
- Alle importierten Pixel und Paletten: 770.930 Byte, etwa 753 KiB; alle 129 Sets passen in 4 Bit pro Pixel.
- Animationsdaten einschließlich eigener Enton-Posen sowie Host-Frame-/Clip-/Set-Tabellen: 974.322 Byte, etwa 952 KiB; Testgrenze für den vollständigen Katalog 1 MiB. Namen und weitere Texte sind nicht in dieser Datengröße enthalten.
- Vorherige Standgrafiken und Paletten: weiterhin 908 Byte.
- Neue Waldlichtung: 21.424 Byte einschließlich beider Paletten für Tag/Nacht. Beide Varianten teilen dieselben Pixel. [Quelle und Prompt](../assets/backgrounds/README.md).

Tabellen enthalten Zeiger, ihre Größe hängt vom Zielsystem ab. Das sind deklarierte Datengrößen des Host-Builds, kein gemessener ESP32-Flash-/RAM-Gesamtbedarf. Konstanten sind für Flash vorgesehen; LCD-Ausgabe kann Pixel direkt aus der Palette lesen. Kein GIF-, PNG- oder XML-Decoder und kein vollständiger Animationsframebuffer sind auf dem Gerät nötig. Tatsächliche Flash-Platzierung und Laufzeit werden erst mit der Board-Toolchain verifiziert.
