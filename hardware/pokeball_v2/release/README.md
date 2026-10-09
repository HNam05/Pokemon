# Pocket Pet V2 Druckdateien

Geometriepaket zum Prototyp **herausnehmbares Handheld in einer aufklappbaren Pokeball-Schutzhulle**. Das Handheld ist fuer das Waveshare ESP32-S3-LCD-2 mit rechteckigem 2-Zoll-Display ausgelegt.

## Druckplatten

- `00_Passproben.3mf`: Tasten-, Scharnier- und Aufnahme-Passproben. Diese zuerst drucken.
- `01_Ball_unten.3mf` und `02_Ball_Deckel.3mf`: je eine grosse Schalenhaelfte pro Platte.
- `03_Handheld_und_Halter.3mf`: Handheld-Front/-Rueckseite, Aufnahme, Boardtraeger, Akkuhalter, Tastentraeger, Tasten und Emblem.

Die neutralen 3MF-Dateien enthalten Modellgeometrie und Objektnamen, aber kein Druckerprofil und keinen G-Code. Die STL-Dateien in `STL_print/` sind einzeln und in Drucklage; die STEP-Dateien in `STEP_parts/` lassen sich weiterbearbeiten. Zusaetzlich liegen die CAD-Baugruppe, das Handheld-STEP, eine Vorschau und der digitale Pruefbericht bei.

## Status

Der CAD-Quellcode und die Hashes aller 15 STL-Meshes sind im Pruefbericht gebunden. Geprueft wurden zusammenhaengende wasserdichte Meshes, Volumenueberschneidungen der Teile, Board-/Akku-/Tasterhuellen, Deckelbewegung bis 130 Grad und die Entnahme des Handhelds in diskreten Hoehenschritten. Alle diese digitalen Checks sind bestanden.

Das ist ein **druckbarer Funktionsprototyp**, keine physische oder elektrische Freigabe. Zuerst die Passproben und danach einen einfarbigen Montageprototyp drucken. Kabel, Loetstellen, Akku, Antennen, Schraubhalt, Bandzug, Tastergefuehl und reale Drucktoleranzen sind noch nicht am realen Aufbau geprueft. Mass-, Material- und Montagehinweise stehen in [`../README.md`](../README.md).
