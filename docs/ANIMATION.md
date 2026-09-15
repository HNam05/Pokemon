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

Der kosmetische Xorshift-PRNG besitzt einen eigenen Seed. Der Desktop erzeugt ihn aus dem Betriebssystem; bei manueller Testuhr ist er fest 42. Hardware übergibt später einen Seed aus ihrem Adapter. Er verändert weder `State::rng` noch Pflegeregeln und wird nicht gespeichert. V2-Spielstände bleiben unverändert 44 Bytes. Ohne gespeicherten Animationszustand kann beim Neustart eine andere Bewegung beginnen.

Bei „reduzierte Bewegung“ im Browser bleibt ein zum Zustand passendes Standbild ohne Positionsbewegung sichtbar. Es gibt keine Browser-Zufallslogik und keinen zweiten Pflegealgorithmus. Das Umschalten von Clip, Frame und Position kommt vollständig aus C++; nur die barrierearme statische Darstellung ist ein Renderer-Modus.

## Darstellung und Daten

Die Evoli-Fanart und ihre konkreten Rechte stehen in [assets/README.md](../assets/README.md). Neun Cliptypen teilen sich 19 verschiedene Evoli-Bitmaps. Enton benutzt eigene zusätzliche Posen. Es wird nur die vordere Blickrichtung importiert; Gehen ist daher ein frontaler Schritt mit seitlicher Bewegung, noch kein vollständiger Satz seitlicher Laufansichten.

`animation_frame` liefert ein palettiertes Sprite, X/Y-Versatz relativ zum gemeinsamen Mittelpunkt und Anzeigedauer. Transparente Randbereiche kosten keinen Pixel-Speicher. Der Versatz bleibt erhalten, damit Hüpfen und Schlafen nicht durch automatisches Zentrieren ungewollt verrutschen. Bildschirmbewegung ist begrenzt; Gehen kehrt zur Mitte zurück. Der Home-Renderer beschneidet auf die Landschaft, damit kein Frame die Statusleisten übermalt.

Der Browser lädt die Frames einmal vom lokalen C++-Adapter und baut Canvas-Bitmaps für die Darstellung. Danach braucht ein Bildwechsel nur `drawImage`. Home-Abfragen etwa alle 60 ms, im pausierten Spiel etwa alle 400 ms. Der Browser läuft vollständig offline, ohne Grafik-CDN.

## Speicherstand vom Host-Build

Evolis ursprüngliche Sprungbahn wird bei vierfacher Darstellung in ihrer vertikalen Auslenkung halbiert. Dadurch bleiben die Ohren vollständig unter der Kopfzeile, ohne die Pixelgrafik zu verzerren. Browserprüfungen kontrollieren die Ober- und Unterkante sämtlicher im Ablauf gezeigter Frames.

- Spielkern unverändert: `Game` 64 Byte, darin `State` 32 Byte.
- Zusätzlicher `Animator`: 20 Byte, statische Obergrenze 32 Byte.
- Importierte Evoli-Pixel und Palette: 3.875 Byte.
- Zusätzliche Animationsdaten einschließlich eigener Enton-Posen und Host-Frame-Tabellen: 8.819 Byte; statische Testgrenze 16 KiB.
- Vorherige Standgrafiken und Paletten: weiterhin 908 Byte.

Tabellen enthalten Zeiger, ihre Größe hängt vom Zielsystem ab. Das sind deklarierte Datengrößen des Host-Builds, kein gemessener ESP32-Flash-/RAM-Gesamtbedarf. Konstanten sind für Flash vorgesehen; LCD-Ausgabe kann Pixel direkt aus der Palette lesen. Kein GIF-, PNG- oder XML-Decoder und kein vollständiger Animationsframebuffer sind auf dem Gerät nötig. Tatsächliche Flash-Platzierung und Laufzeit werden erst mit der Board-Toolchain verifiziert.
