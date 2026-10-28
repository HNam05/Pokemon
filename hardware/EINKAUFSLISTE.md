# Einkaufsliste: zwei Pocket-Pet-Handhelds

Stand: 28.10.2026, recherchiert von Anthropic Claude Opus 5.5. Preise inkl. MwSt., so wie AliExpress/eBay sie an diesem Tag für Deutschland anzeigten. Preise und Lieferbarkeit ändern sich täglich; vor dem Bestellen prüfen. Nichts davon wurde bestellt.

Grundlage ist die V2-Stückliste (Rev. B) unter `output/pdf/pocket_pet_technical_rev_b/` und das CAD in `hardware/pokeball_v2/`. Mengen gelten für **zwei Geräte** plus etwas Reserve.

## Hardware-Überlegungen

- **Board bleibt das Waveshare ESP32-S3-LCD-2, und zwar ohne Touch und ohne Kamera.** Das Gehäuse ist auf dieses Board gezeichnet (35,01 × 48,21 mm). Die Touch-Variante „ESP32-S3-Touch-LCD-2“ ist ein eigenes Produkt; Touch braucht unser Drei-Tasten-Konzept nicht, und ob die Maße identisch sind, ist nicht belegt. Das Board bringt Ladeelektronik, MX1.25-Akkuanschluss, USB-C, 16 MB Flash (reicht für die 974 KB Pokémon-Grafiken), 8 MB PSRAM und einen Bewegungssensor (später „Schütteln“) mit.
- **Kein Uhrbaustein, kein Ein/Aus-Schalter** laut Herstellerseiten. Die Uhrzeit wird deshalb im Menü gestellt (schon umgesetzt); später ginge auch Zeitabgleich über WLAN. Ausgeschaltet wird per Tiefschlaf; die Tasten sollten an GPIOs, die aus dem Tiefschlaf wecken können (vor dem Löten im Schaltplan prüfen).
- **Akku:** Die Akkuhalterung erlaubt höchstens 36 × 63 × 5,2 mm. Der PKCell LP-503562 (1200 mAh, ca. 62,5 × 36 × 5,05 mm, mit Schutzschaltung) passt knapp. Er hat einen JST-PH-2.0-Stecker; das Board braucht MX1.25 → Adapterkabel. **Polarität vor dem ersten Einstecken mit Multimeter prüfen** – bei MX1.25-Kabeln aus China ist Rot/Schwarz oft vertauscht, ein verpolter Akku kann das Board zerstören.
- **Einzelne LiPo-Akkus gibt es auf AliExpress für Deutschland praktisch nicht** (Gefahrgut beim Versand). Darum kommt der Akku von einem deutschen eBay-Händler.
- **Tasten:** drei 6 × 6 mm Taster mit 4,3 mm Höhe (Bauform wie Omron B3F-1000) auf einem selbst zugeschnittenen Stück Platine (43 × 12 mm). Das Rastermaß der Taster (6,5 × 4,5 mm) passt nicht genau auf Lochraster; die Beinchen werden durch zusätzlich gebohrte 1-mm-Löcher gesteckt. Später kann man eine kleine Tasterplatine günstig fertigen lassen.
- **Ton ist optional.** Verstärker und Lautsprecher kosten zusammen rund 5 €, haben aber noch keine Halterung im Gehäuse. Mitbestellen lohnt sich, weil es billig ist.
- **Akkulaufzeit:** grob geschätzt, nicht gemessen: Bildschirm an etwa 10 Stunden Spielzeit, mit Tiefschlaf zwischendurch mehrere Tage. Wird am echten Gerät gemessen.

## Zoll und Versand (Stand Oktober 2026)

Seit 1. Juli 2026 erhebt die EU auf Sendungen bis 150 € einen pauschalen Zoll von **3 € pro Artikelart** (Zolltarif-Position), nicht pro Stück und nicht pro Paket ([EU-Kommission](https://commission.europa.eu/news-and-media/news/ensuring-fairness-and-safety-eur3-customs-duty-low-value-parcels-2026-06-29_en), [Leitfaden](https://taxation-customs.ec.europa.eu/news/guidance-and-legal-text-temporary-flat-fee-low-value-imports-which-will-apply-until-1-july-2028-2026-06-08_en)). Beispiel der Kommission: 5 T-Shirts = 3 €, 3 T-Shirts + 1 Uhr = 6 €. AliExpress rechnet das an der Kasse ein („Zölle werden an der Kasse berechnet“). Eine zusätzliche EU-Bearbeitungsgebühr ist für Herbst 2026 angekündigt, Höhe noch offen. Folge: Viele verschiedene Kleinteile aus China werden spürbar teurer; nur bestellen, was wirklich gebraucht wird. Mit allen Positionen unten etwa 15–30 € Zoll einplanen; den exakten Betrag zeigt die Kasse.

Temu ließ sich nicht prüfen, weil dort schon die Suche eine Anmeldung verlangt. AliExpress führt alle Teile außer dem Akku, das passende Board sogar vom Waveshare-Partner SpotPear.

## Bestellung 1: AliExpress – Klickliste (alles außer Akku)

Einen fertig gefüllten Warenkorb als Link bieten weder AliExpress noch eBay an; der Warenkorb gehört immer zu einem angemeldeten Konto. Deshalb hier jeder Link mit genau der Variante und Menge, die man auswählen muss: Link öffnen → Variante wählen → Menge einstellen → „In den Warenkorb“. Am Ende alles zusammen bezahlen. Alle Angebote zeigten am 28.10.2026 kostenlosen Versand nach Deutschland und Lieferung etwa 4.–18. November.

| # | Teil | Variante auswählen | Menge | Preis gesehen |
|---|---|---|---|---|
| 1 | [Waveshare ESP32-S3-LCD-2 (SpotPear)](https://de.aliexpress.com/item/1005008497879276.html) | Farbe: **No Touch-No-Camera** | **2** (3 mit Ersatz) | 23,39 €/Stück ab 2 |
| 2 | [MX1.25-Kabel 2-pol., 20 Stück (Pai-Pai)](https://de.aliexpress.com/item/1005005277872548.html) | red black, Länge 100 mm | 1 | 2,95 € |
| 3 | [JST-PH 2.0 Stecker + Buchse mit Kabel, 10 Stück (Z7)](https://de.aliexpress.com/item/1005007292597698.html) | 2P, 150 mm, Single head | 1 | ca. 1–2 € (Variantenpreis prüfen) |
| 4 | [Taster 6×6 mm (YT Technology)](https://de.aliexpress.com/item/1005005937822191.html) | 10PCS, Größe **6X6X4.3** | 1 | 2,69 € |
| 5 | [Lochrasterplatine doppelseitig 2×8 cm, 10 Stück (alinsin)](https://de.aliexpress.com/item/1005009006745424.html) | 2X8CM | 1 | 1,79 € |
| 6 | [Silikonlitze, 5 Rollen (100MillioFang)](https://de.aliexpress.com/item/1005008467990750.html) | Spezifikation **30AWG x10m x5 rolls** | 1 | ca. 9,69 € (Variantenpreis prüfen) |
| 7 | [M2-Schraubenset Innensechskant, 692 Teile (JYG)](https://de.aliexpress.com/item/1005010249990703.html) | **M2 692pcs set** | 1 | 7,79 € |
| 8 | [M2/M3 Senkkopf-Set mit Muttern, 400 Teile](https://de.aliexpress.com/item/1005006904727350.html) | countersunk head | 1 | 6,39 € |
| 9 | [M3 × 45 DIN 912 (Scharnierachse)](https://de.aliexpress.com/item/1005004912301752.html) | **20pcs M3x45 half** (Teilgewinde) | 1 | ab 3,85 € (Variantenpreis prüfen) |
| 10 | [Klettband 5 m (YOUBO)](https://de.aliexpress.com/item/1005009828366776.html) | 1 Roll, **Width 10mm** | 1 | 1,49 € |
| 11 | Optional Ton: [MAX98357A-Verstärker](https://de.aliexpress.com/item/1005010228868375.html) | 1pcs | **2** | 1,99 €/Stück |
| 12 | Optional Ton: [Lautsprecher 2030, 8 Ω, 1 W](https://de.aliexpress.com/item/1005009984830273.html) | 5 Stück | 1 | 3,19 € |

Zwischensumme etwa **92 €** (ohne Ton etwa 85 €), zuzüglich EU-Zoll von 3 € je Artikelart; AliExpress zeigt ihn an der Kasse.

Hinweise zu den Teilen:

- **Akkuadapter (2 + 3):** Das Akkukabel endet in einer JST-PH-Buchse. Aus einem MX1.25-Kabel (2) und dem passenden PH-Gegenstück aus dem Paar-Set (3) einen kurzen Adapter löten und mit Schrumpfschlauch isolieren. Vorteil gegenüber einem fertigen Adapter: Die Polarität bestimmst du selbst. Plus am Akku an Plus am Board-Anschluss – mit dem Multimeter prüfen, bevor der Akku das erste Mal steckt.
- **Schrauben (7–9):** Set 7 liefert M2 × 4/5/6 mit Zylinderkopf, Set 8 die Senkkopfschrauben M2 × 6 und M3 × 8 sowie M3 × 6/10 und M3-Muttern. Die beiden M3-Unterlegscheiben pro Scharnier sind in keinem Set sicher enthalten; im Baumarkt kosten sie Cent-Beträge, das Scharnier funktioniert notfalls auch ohne.
- **Taster (4):** Unbedingt die Größe 6X6X4.3 wählen; vorausgewählt ist 6X6X5.
- Die Ton-Teile (11, 12) haben noch keine Halterung im Gehäuse. Wer Zoll sparen will, lässt sie weg.
- Ausgewichen wurde bewusst: ein 20er-Pack M3 × 45 für 11,79 € und ein „Adapter“, der sich als USB-Kabel herausstellte.

Günstiger, aber nicht über AliExpress: Waveshare direkt listet das Board für 13,99–17,99 USD ([waveshare.com](https://www.waveshare.com/esp32-s3-lcd-2.htm)); Versand, Einfuhrumsatzsteuer und Zoll kommen dazu und wurden nicht geprüft.

## Bestellung 2: eBay.de (Akku aus Deutschland)

| # | Teil | Menge | Preis gesehen | Link |
|---|---|---|---|---|
| 13 | PKCell LP-503562, 3,7 V, 1200 mAh, Schutzschaltung, JST-PH 2-pol. | **2** (Angebot „2 Stück“) | 2 Stück à 4,99 € + 2,50 € Versand, 2–3 Tage | [eBay 135283921460](https://www.ebay.de/itm/135283921460) |
| 13b | Gleiche Zelle bei BerryBase (zuletzt nicht lieferbar) | 2 | 5,50 €/Stück | [BerryBase LP-503562](https://www.berrybase.de/en/lp-503562-lithium-polymer-lipo-battery-3.7v-1200mah-with-2-pin-jst-connector) |

Etwa **12,50 €**.

## Wahrscheinlich schon vorhanden (sonst ergänzen)

- USB-C-**Datenkabel** (nicht nur Ladekabel) zum Flashen.
- PLA-Filament: Rot, Weiß, Schwarz für den Pokéball; Farbe für das Handheld nach Wunsch.
- Werkzeug: Lötkolben, Lötzinn, Flussmittel, **Multimeter** (Pflicht für die Akkupolarität), Schrumpfschlauch, 1-mm-Bohrer, Seitenschneider, Innensechskantschlüssel 1,5 und 2,5 mm.
- Etwas Sekundenkleber für das Emblem.

## Gesamt

Rund **105 €** für zwei Geräte plus etwa 15–30 € EU-Zoll (abhängig von der Zahl der Artikelarten). Ein drittes Board als Ersatz kostet etwa 23 € mehr.

## Später, noch nicht kaufen

- Gewindeeinsätze M2 zum Einschmelzen: erst sinnvoll, wenn das CAD dafür angepasst ist.
- Kleiner Schiebeschalter für die Akkuleitung: das Gehäuse hat noch keine Aussparung.
- Gefertigte Tasterplatine (z. B. bei einem PCB-Fertiger): erst, wenn die Passprobe der Tasten gedruckt und geprüft ist.
