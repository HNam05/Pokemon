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

## Bestellung 1: AliExpress (alles außer Akku)

| # | Teil | Menge | Preis gesehen | Link / Suchbegriff |
|---|---|---|---|---|
| 1 | Waveshare ESP32-S3-LCD-2, Variante **„No Touch-No-Camera“**, Verkäufer SpotPear Electronics | 2 (optional 3 als Ersatz) | 25,99 €, ab 2 Stück 23,39 €/Stück, Versand kostenlos, Lieferung ca. 4.–7. Nov. | [AliExpress 1005008497879276](https://de.aliexpress.com/item/1005008497879276.html) |
| 1b | Alternative: gleiches Board, Variante „ESP32-S3-LCD-2“, Funkeydo Store | 2 | 22,99 €/Stück, Versandkosten nicht angezeigt, Lieferung ca. 5.–13. Nov. | [AliExpress 1005008460109655](https://de.aliexpress.com/item/1005008460109655.html) |
| 2 | Adapterkabel MX1.25 (2-pol.) auf JST-PH 2.0 | 1 Pack (10 Stück) | 8,01 € | Suche „MX1.25 PH2.0 2pin cable“ |
| 2b | Alternative: MX1.25-Kabel mit einem Stecker, 28 AWG (selbst an Akkukabel löten) | 1 Pack (20 Stück) | 2,95 € | Suche „MX1.25 2pin single head cable“ |
| 3 | Taster 6 × 6 × 4,3 mm, 4 Pins, THT | 1 Pack | ab 2,69 € | Suche „6x6x4.3 tactile switch“ (Höhe **4,3 mm** wählen) |
| 4 | Lochrasterplatine FR4 doppelseitig 2 × 8 cm | 1 Pack (5 Stück) | 3,99 € | Suche „double sided pcb prototype board“ |
| 5 | Silikonlitze 30 AWG, mehrere Farben | 1 Set | 5,99 € | Suche „30awg silicone wire“ |
| 6 | Innensechskant-Schraubensortiment M1,6–M8 (enthält M2 und M3) | 1 Set (692 Stück) | 8,19 € | Suche „M2 M3 hex socket screw assortment“ |
| 7 | Senkkopfschrauben M2 × 6 und M3 × 8 (je kleines Pack) | je 1 | ca. 2–5 €, nicht einzeln geprüft | Suche „M2x6 countersunk“, „M3x8 countersunk“ |
| 8 | Schraube M3 × 45 (Scharnierachse) mit Mutter und Scheiben | 1 Pack | 3,85 € | Suche „M3x45 screw“ |
| 9 | Klettband 10 mm, Rolle 5 m (Halteband im Ball) | 1 | 2,09 € | Suche „velcro 10mm roll“ |
| 10 | Optional Ton: MAX98357A I2S-Verstärker | 2 | 1,99 € (ab 2 Stück 1,88 €) | Suche „MAX98357A“ |
| 11 | Optional Ton: Lautsprecher 2030 oval, 8 Ω, 1 W | 1 Pack (5 Stück) | 3,19 € | Suche „2030 speaker 8ohm 1w“ |

Zwischensumme mit Position 1, 2, 3–11: etwa **93 €** zuzüglich Zoll. Ohne Ton (10, 11) etwa 86 €.

Günstiger, aber nicht über AliExpress: Waveshare direkt listet das Board für 13,99–17,99 USD ([waveshare.com](https://www.waveshare.com/esp32-s3-lcd-2.htm)); Versand, Einfuhrumsatzsteuer und Zoll kommen dazu und wurden nicht geprüft.

## Bestellung 2: eBay.de (Akku aus Deutschland)

| # | Teil | Menge | Preis gesehen | Link |
|---|---|---|---|---|
| 12 | PKCell LP-503562, 3,7 V, 1200 mAh, Schutzschaltung, JST-PH 2-pol. | 2 | 2 Stück à 4,99 € + 2,50 € Versand, 2–3 Tage | [eBay 135283921460](https://www.ebay.de/itm/135283921460) |
| 12b | Gleiche Zelle bei BerryBase (zuletzt nicht lieferbar) | 2 | 5,50 €/Stück | [BerryBase LP-503562](https://www.berrybase.de/en/lp-503562-lithium-polymer-lipo-battery-3.7v-1200mah-with-2-pin-jst-connector) |

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
