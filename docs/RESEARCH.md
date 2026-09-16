# Recherche und Spielkonzept

Stand: 14.09.2026. Autor der Recherche und Implementierung: OpenAI Codex.

## Quellen und verifizierte Grundlagen

1. [Bandai: Original Tamagotchi, offizielles Handbuch](https://tamagotchi-official.com/manual/toy/original/Original_webmanual.pdf): drei Tasten, Futter und Snacks, Spielen, Licht/Schlaf, Hinterlassenschaften entfernen, Medizin, Aufmerksamkeit und Statusanzeigen. Pflege beeinflusst das Aufwachsen. Das ist die Grundlage des Pflegekreislaufs; konkrete Zahlen unten sind unsere eigenen Regeln.
2. [Nintendo: Pokémon Sonne, Abschnitt Pokémon Refresh](https://www.nintendo.com/en-gb/Games/Nintendo-3DS-games/Pokemon-Sun-1092368.html): Pokémon pflegen, säubern, füttern und Statusprobleme behandeln. Für dieses Projekt wird daraus ein reduziertes Spiel mit Bindung und Entwicklung, ohne Kampf- oder Sammelsystem.
3. [Waveshare: ESP32-S3-LCD-2](https://www.waveshare.com/wiki/ESP32-S3-LCD-2): 2-Zoll-LCD, 240×320, SPI/ST7789T3, ESP32-S3R8, PSRAM und Flash, Lithium-Akku-Anschluss/Ladefunktion sowie USB-C. Boardkandidat, noch keine Kaufentscheidung. Die Wiki enthält widersprüchliche Touch-Verweise in Demoabschnitten; SKU, Schaltplan und Boardrevision vor Kauf/Pinbelegung abgleichen.
4. [Espressif: Non-Volatile Storage](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/storage/nvs_flash.html): NVS als späterer Speicheradapter für kleine versionierte Spielstände; Fehler prüfen und Schreibfrequenz begrenzen.
5. [Espressif: System Time](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/system_time.html): Zeitquellen und RTC-Verhalten hängen vom Betriebs-/Resetmodus ab. Verstrichene Spielzeit und Kalenderzeit getrennt behandeln. Vollständiger Stromverlust verlangt eine ausdrückliche Zeitstrategie.
6. [MakerWorld-Inspiration](https://makerworld.com/de/models/3169383-pokemon-tamagotchi-with-magsafe-charging?from=search#profileId-3583049): Abruf in dieser Sitzung sowohl über DE- als auch EN-URL fehlgeschlagen. Aufbau, Dateien, Maße, Firmware, Lizenz und MagSafe-Lösung wurden nicht verifiziert oder übernommen.

Die drei angehängten Schaubilder sind Inspirationsmaterial. Ihre Preise, Aufwandsangaben, Bauteilbezeichnungen, Touch-Angaben und GPIO16/17/18 gelten ausdrücklich nicht als geprüfte Spezifikation. Gewünscht ist ein aufklappbarer Pokéball, nicht automatisch die in den Bildern gezeigte Handheld-Gehäuseform.

## Was ein vollständiger kleiner Virtual Pet braucht

Ein verlässlicher Kern besteht aus Pflegewerten, zeitlichem Verfall, klaren Aktionen mit Bedingungen, sichtbaren Bedürfnissen, kurzen Spielanreizen, Wachstum, dauerhafter Speicherung und einfacher Bedienung. Für ein mobiles Gerät kommen entprellte Tasten, Display, Akku-/Energiesparen und eine definierte Offline-Zeitstrategie hinzu. Die meisten Komplexitäten kommen aus Zeit, Speicherung und Zustandsübergängen, nicht aus dem Display allein.

Erster spielbarer Umfang: Ei → Evoli → Psiana oder Nachtara, eine Pflegeoberfläche, sechs Statuswerte, ein Minispiel, lokale Speicherung, Simulator-Zeitsteuerung. Selbst gezeichnete Pixel-Platzhalter statt übernommener Sprites. Später: weitere Arten, unterschiedliche Animationen, optionale Töne, mehr Spiele, Gehäuse-/Deckelzustand und eventuell Gerätekontakt. Für den Kern werden weder SD-Karte noch Netzwerk benötigt.

## Eigene M1-Spielregeln, keine exakte Pokémon-/Tamagotchi-Nachbildung

| Bereich | Implementierte Regel |
|---|---|
| Zeit | Start 08:00 Spielzeit; 1 reale Minute = 1 Spielminute. Simulator optional 60×/3600× und Pause. Tageszeit ist zunächst Spielzeit, nicht die PC-Uhr. |
| Ei | Schlüpft nach 10 Spielminuten; vorher sind Pflegeaktionen gesperrt. |
| Sättigung | Start 75/100; wach −1 je 6 Min., schlafend −1 je 12 Min. Beere +25, Glück +3; bei >85 Sättigung kein weiteres Futter. |
| Glück | Start 70; wach −1 je 12 Min. Spiel verbessert es. |
| Energie | Start 85; wach −1 je 6 Min.; Schlaf +1 je 2 Min.; bei 100 automatisch wach. Schlaf manuell umschaltbar. |
| Sauberkeit | Start 90; −1 je 10 Min., mit Abfall −3. Alle 180 Min. eine Hinterlassenschaft, maximal vier. Säubern entfernt alles und setzt Sauberkeit auf 100. |
| Gesundheit | 30 Min. am Stück ohne Sättigung/Energie oder mit Sauberkeit <20 machen krank. Krank oder vernachlässigt: −2 Gesundheit je 10 Min. Gute Versorgung regeneriert +1 je 10 Min. |
| Erschöpfung | Bei 0 Gesundheit Pflege-/Medizinbedarf, kein permanenter Tod. Medizin kuriert Krankheit und stellt mindestens 40 Gesundheit her. Grundbedürfnisse weiter versorgen, sonst erneute Erkrankung. |
| Bindung | Start 20; +2 pro gefangener Beere; bei Vernachlässigung −1 je Stunde. Kein endloser Bonus durch wiederholtes Saubermachen. |
| Beerenfang | Drei Spuren, Links/Rechts bewegen, OK fängt. Fünf Beeren, je 1,8 Sek.; Fangfenster seit M7 1,2 bis <1,8 Sek. in richtiger Spur. Früh/zu spät/falsche Spur zählt als Fehlversuch. |
| Spielkosten | Mindestens 15 Sättigung/Energie, wach und gesund; Start kostet 8 Energie und 5 Sättigung. Je Treffer +4 Glück, +2 Bindung, +3 EP, Belohnung einmal nach fünf Versuchen. |
| Entwicklung | Evoli, mindestens 1 Tag, 70 Bindung, 60 EP, 60 Gesundheit, gesund und wach. Menüaktion entwickelt 06:00 bis <20:00 zu Psiana, sonst Nachtara. Vereinfachte eigene Regeln. |

Im Minispiel pausiert die Pflegezeit; seine Reaktionszeit bleibt in jedem Zeitraffermodus gleich. „Pause“ friert beide Uhren ein; Menüaktionen bleiben möglich. Ein gestartetes Spiel lässt sich durch Warten abschließen. Nach Programmneustart wird die Home-Ansicht wiederhergestellt; bezahlte Spielkosten bleiben bestehen, ein unterbrochenes Spiel bringt keine Belohnung.

## Erweiterung M2, 14.–15.09.2026

- Evoli oder Enton auswählen, bevor die Ei-Uhr startet. Enton nutzt dieselben Pflegewerte; seine Entwicklung folgt später.
- Zehn Menüeinträge, fünf sichtbare Zeilen; Links/Rechts bedeuten vorheriges/nächstes und im Menü hoch/runter. Kurzes OK bestätigt beim Loslassen, langes OK führt zurück oder bricht ein Spiel ohne Belohnung ab.
- Neue Pflegehilfe und konkrete Hinweise. Aufmerksamkeitsgrenzen: satt <25, Energie <25, Freude <30, Hygiene <25, Gesundheit <40, Krankheit oder Abfall.
- Zweites Spiel: Entons Denkpause. Ursprünglicher M2-Entwurf: drei Zeichen à 600 ms plus 200 ms Pause, zehn Sekunden Eingabezeit, drei Runden ohne Teilbelohnung. Seit M7 gelten die unten beschriebenen wachsenden Folgen und Teilbelohnungen.
- Persönlicher Name als getrennte lokale Gerätekonfiguration, getrennte Spielstände für zwei Geräte.
- Palettensprites als gemeinsame C++-Daten und explizite Speicherbudgets. Offizielle Espressif-Quellen und Hardwarestrategie in [UX_HARDWARE.md](UX_HARDWARE.md).

## Ergänzung 15.09.2026: Animationsquellen und Verhalten

SpriteCollab bietet mehrere Aktionen pro Pokémon, enthält aber sowohl Originalspielgrafiken als auch Fanbeiträge. Die konkrete Evoli-Variante `0133/0002` nennt Emmuffin als Künstler; sie wurde mit festem Quellcommit, Credits und den CC-BY-NC-Nutzungsbedingungen übernommen. Die Standardsets für Evoli und Enton nennen Chunsoft und wurden nicht importiert. Vergleichsquellen und genaue Fundstellen: [Grafikherkunft](../assets/README.md).

Die neue kosmetische Zustandsmaschine wählt zufällig zwischen kurzen Aktionen mit Ruhepausen. Schlaf, Krankheit und niedrige Energie haben Priorität; Hunger/niedrige Freude unterdrücken Jubel und Hüpfen. Erfolgreiches Füttern löst einen Essablauf aus. Der Zufall ist unabhängig von Minispielen und Pflegelogik. Pflegezahlen und Save-Format bleiben unverändert. Vollständiger Vertrag und Speicherstand: [Animationen](ANIMATION.md).

## Offline-Verhalten (unverändert)

Der Server betreibt das Pet auch bei geschlossenem Browser. Beim Serverneustart werden maximal acht Stunden reale Abwesenheit nachgeholt, nie mit dem vorherigen Zeitrafferfaktor. Eine rückwärts korrigierte PC-Uhr erzeugt keine negative Spielzeit. Nach acht Stunden greift ein Abwesenheitslimit; das Tier stirbt nicht. Der Simulator startet immer in Echtzeit. Tests können eine manuelle Uhr verwenden.

## Hardware vor Bestellung klären

- Konkretes Board samt Revision, tatsächliche nutzbare Displayfläche, Ausrichtung, Einbaumaße und Anschlüsse. 240×320 ist bislang der Software-Entwurf.
- Drei freie GPIOs anhand des Schaltplans wählen; Display, Flash, PSRAM, USB und Boot-Pins berücksichtigen. Beispielpins aus dem Bild nicht übernehmen.
- Geschützter 1S-Akku, Anschluss und Polarität, geeignete Lade-/Schutzschaltung und mechanischer Platz. Ein nackter Akku ersetzt keine Ladeelektronik. Kapazität/Laufzeit erst nach Messung beurteilen.
- Power-Schalter, Backlight und Sleep-Verhalten festlegen. MagSafe/Qi ist ein separates Hardwarethema und für die erste Software nicht erforderlich.
- Zeit nach vollständigem Ausschalten: Uhr stellen, optional Zeitabgleich, externer RTC oder ausdrücklich pausiertes Pet. Keine verlässliche Offline-Zeit aus einem uninitialisierten Zähler ableiten.

Es wurde keine Hardware bestellt, verdrahtet, geflasht oder vermessen.

## Katalogerweiterung M4 / 15.09.2026

Auf ausdrücklichen Wunsch werden alle Künstler aus SpriteCollab berücksichtigt. Der festgehaltene Tracker wurde vollständig anhand von Herkunft und Pflege-Framezahl geprüft: 129 geeignete Sets, 85 Pokémon, neun Abläufe je Set, 5.470 Frames. Gemeinsam mit dem eigenen Enton sind 130 Begleiter auswählbar. Quellen, quantitative Kriterien und Ausschlussgründe: [Grafikherkunft](../assets/README.md), [Katalog](../assets/ROSTER.md).

Alle neuen Arten verwenden dieselben bestehenden Pflege- und Minispielregeln. Zusätzliche Entwicklungen werden nicht aus der Form oder Art abgeleitet; nur Evoli entwickelt sich wie bisher. Seitentasten blättern zyklisch, Halten wiederholt ausschließlich in Auswahl/Menü. V3 erweitert die zulässigen Art-IDs bei unverändert 44 Bytes; V1/V2 werden ausdrücklich migriert. Die Save-Anpassung ändert keine Pflegewerte.

Die frühere allgemeine CC-BY-NC-Beschreibung ist durch die tatsächlichen historischen Credit-Kennungen PMDCollab_1, PMDCollab_2 und CC_BY-NC_4 je Set ersetzt. CHUNSOFT-/Mischmaterial bleibt ausgeschlossen.

## Spielabläufe und Pflegefeedback M7 / 16.09.2026

Eigene Designänderungen, keine übernommenen offiziellen Pokémon-Regeln:

- Beide Spiele öffnen eine kostenlose Anleitung; Seitentasten/langes OK kehren ins Menü zurück. Erst kurzes OK startet, prüft die Zugangsvoraussetzungen erneut und zieht einmal 5 Satt und 8 Energie ab. Während Anleitung und Spiel pausiert die Pflegezeit.
- 900 ms Vorbereitung ohne Eingaben. Beeren fallen jeweils 1.800 ms; Fangfenster ab exakt 1.200 ms bis vor 1.800 ms. Jeder Versuch erhält 450 ms Rückmeldung. Fünf Versuche, anschließend einmalige Belohnung. Tasten während Vorbereitung/Rückmeldung erzeugen keine weiteren Versuche.
- Memory erzeugt eine gemeinsame Viererfolge und zeigt nacheinander deren erste zwei, drei und vier Zeichen. Ein Zeichen ist 650 ms sichtbar, danach 250 ms dunkel, damit Wiederholungen erkennbar bleiben. Eingabezeit: 10/12/14 Sekunden. Korrekte Eingaben blinken 250 ms auf; jede abgeschlossene Runde oder ein Fehler erhält 900 ms Rückmeldung.
- Pro gefangener Beere oder vollständig gelöster Memory-Runde bis zu +4 Froh, +2 Bindung und +3 EP. Memory-Fehler und Zeitablauf behalten gelöste Runden. Manueller Abbruch bleibt ohne Belohnung; bezahlte Kosten bleiben bestehen. Grenzen: Pflege/Bindung 100, EP 1.000.000.
- Ergebnis- und Pflegeanzeigen verwenden die tatsächlichen Differenzen nach Begrenzung, keine geschätzten `score * Faktor`-Werte im Browser. Pflegefeedback bleibt vier reale Sekunden sichtbar, Ergebnisse bis zum Verlassen. Die Pflege- und Schlafraten bleiben unverändert.
- Warnschwellen kommen gemeinsam aus C++: Satt <25, Froh <30, Energie <25, Sauberkeit <25, Gesundheit <40. Die frühere pauschale Balkengrenze 25 zeigte insbesondere niedrige Freude zu spät an.

Diese Zeiten sind am Desktop überprüft. Ob Fangfenster und Schriftgrößen am echten kleinen LCD angenehm sind, muss mit dem späteren Gerät erprobt werden.
