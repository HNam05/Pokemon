# Pocket Pet: Projektregeln

- Spielregeln und Zustandsmaschine liegen ausschließlich im portablen C++17-Kern (`include/pet`, `src`). Keine parallele Simulation in JavaScript oder Python.
- Drei Tasten sind der vollständige Gerätevertrag. Jede normale Spielaktion muss damit erreichbar sein. Simulator-Zeitsteuerung gehört nicht auf die Hardware.
- Vor Änderungen `README.md`, `docs/ARCHITECTURE.md` und `progress.md` lesen. Regeländerungen auch in `docs/RESEARCH.md` dokumentieren.
- Speicherformatänderungen ausdrücklich versionieren. Fehlerhafte Spielstände erhalten; niemals beim Ladefehler automatisch ein neues Tier speichern.
- Kein ungeprüftes GPIO-Mapping. Board, Revision und Schaltplan zuerst festlegen. Desktop-Tests sind kein Beleg für funktionierende ESP32-Firmware.
- Keine heruntergeladenen Pokémon-/MakerWorld-Assets ohne geklärte Herkunft übernehmen. Aktuelle Pixelgrafik ist ein eigener Platzhalter.
- Build und C++-Tests: `python scripts/build.py` oder der dokumentierte `--zig`-Weg. Adaptertests: `python -m unittest discover -s tests -p "test_*.py" -v`. UI-Verhalten im Browser prüfen.
- Themenbranches verwenden. Keine Commits, Pushes oder Merges ohne Auftrag. Wenn beauftragt, Herkunft als `AI-Assisted-By: OpenAI Codex` oder `AI-Assisted-By: Anthropic <bekanntes Modell>` dokumentieren. Menschliche Git-Autoridentität erhalten.
- Keine Builds, `.tools`, `node_modules`, Testbilder oder Saves committen. `progress.md` mit geprüften Ergebnissen und offenen Punkten aktualisieren.
