# Grafikherkunft und Animationsimport

Stand: 15.09.2026. Die Bilder sind Fanmaterial, keine pauschal frei lizenzierten Pokémon-Marken oder Originalspielgrafiken.

## Übernommen: Evoli Alternate von Emmuffin

- Künstler: **Emmuffin**, [Künstlerprofil](https://twitter.com/Ernmuffin), SpriteCollab-ID `356635814668664832`.
- Quelle: [PMDCollab/SpriteCollab, sprite/0133/0002](https://github.com/PMDCollab/SpriteCollab/tree/83681005aa8f37cea7dfe8e68c51aa4b7bf8384a/sprite/0133/0002).
- Gepinnter Stand: `83681005aa8f37cea7dfe8e68c51aa4b7bf8384a`. Variante heißt im Tracker **Alternate**. Die Varianten-Credits nennen Emmuffin für die übernommenen Animationen.
- Upstream-Nutzungsbedingungen: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), Namensnennung und nichtkommerzielle Nutzung. Volltext und Gewährleistungsausschluss liegen in `vendor/spritecollab/LICENSE.md`; ursprüngliche Nutzungsrichtlinie in `vendor/spritecollab/README.md`.
- Originale PNGs, XML, Credits und SHA-256-Manifest liegen in `vendor/spritecollab/eevee-alternate/`. `credit_names.txt` ist der unveränderte öffentliche Upstream-Namensnachweis.
- Enthalten: Idle, Walk, Hop, Pose, Sleep, Eat, Sit, Hurt, LookUp. 38 Frames in der vorderen Blickrichtung, 19 unterschiedliche Bitmaps.
- Änderungen: Nur vordere Richtungszeile exportiert; transparente Ränder beschnitten; Positionsversatz beibehalten; RGB888 nach RGB565; verlustfrei innerhalb dieser Farbkonvertierung mit 4 Bit pro Pixel gepackt und identische Bilder geteilt. Anzeige integer-skaliert, bei Bewegung gespiegelt. Zeitabläufe bewusst verlangsamt (XML-Einheit auf 1/30 Sekunde, mindestens 70 ms pro Frame).
- Urheber und Lizenz stehen zusätzlich im Simulator unter „Über diesen Prototyp“. Beim Weitergeben von Code, Gerät oder Assets diese Attribution mitgeben. Für eine spätere reine Geräteauslieferung einen Credits-Bildschirm oder beiliegenden Quellenhinweis ergänzen.

Die CC-Lizenz betrifft die von den Beitragenden lizenzierbaren Anteile. Rechte an Pokémon-Figuren, Marken und anderen fremden Bestandteilen bleiben bei ihren Rechteinhabern; keine offizielle Verbindung oder Zusicherung vollständiger Rechtefreiheit.

## Enton und andere Varianten

Die geprüften SpriteCollab-Standardsets für Enton und Evoli führen **CHUNSOFT** als Urheber. Sie wurden **nicht importiert** und werden nicht als CC-Fanarbeit umetikettiert. Für Enton wurde bisher kein geeigneter eigenständig gezeichneter Satz mit hinreichend klarer Freigabe gefunden.

Enton verwendet deshalb weiterhin das projektinterne Pixelbild mit zusätzlichen prozeduralen Augen-, Schnabel- und Fußposen in C++. Blinzeln, Gehen, Hüpfen, Freude, Fressen, Umsehen und ruhige Schlaf-/Erschöpfungsposen sind verfügbar. Ei, Psiana und Nachtara behalten eigene Prototypgrafiken; die beiden Entwicklungsvarianten haben noch keine eigenständigen Frame-Sets. Das ist im UI ausdrücklich als Prototypgrafik bezeichnet.

## Andere geprüfte Quellen

- [PokeAPI/sprites](https://github.com/PokeAPI/sprites): umfangreiche Sammlung, darunter Spielgrafiken; eine offene Codebasis ist kein Nachweis einer freien Lizenz jeder Bilddatei. Hier nichts übernommen.
- [Pokémon Showdown Credits](https://pokemonshowdown.com/credits): Animationen und viele Beitragende, aber weniger passend für mehrere Pflegeaktionen und keine pauschale Freigabe aller Originalsprites. Hier nichts übernommen.
- [Ghasty001](https://github.com/Ghasty001/Animated_sprites_by_Ghasty001): ausdrückliche Nutzung mit Credits einschließlich jeweiliger Basis-Künstler; als weitere Recherchequelle vorgemerkt, keine Dateien übernommen.

## Reproduzieren

`python scripts/import_sprites.py` erzeugt `src/eevee_frames.inc` offline aus den gepinnten Originalen. Dafür ist Pillow nötig (hier 12.3.0 genutzt), aber nicht für einen normalen Build oder den Simulator. Keine neue Laufzeitabhängigkeit.

`python scripts/import_sprites.py --check` prüft Quellhashes und deterministische Ausgabe. `python tests/verify_sprite_import.py` vergleicht unabhängig alle 59.200 Quellpixel der ausgewählten Richtungszeile einschließlich transparenter Ränder gegen die tatsächlich kompilierte C++-Bibliothek.

Der Importer akzeptiert ausschließlich vollständige Transparenz oder Deckkraft und höchstens 15 sichtbare RGB565-Farben. Überschreitungen schlagen fehl statt still Bilder umzuwandeln. Die PNG-/XML-Dateien werden auf dem Gerät nicht benötigt; dort liegen nur die gepackten konstanten C++-Daten.
