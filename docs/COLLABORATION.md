# Zusammenarbeit zwischen Rechnern und Modellen

## Gemeinsamer Vertrag

- `main` bleibt der stabile Integrationsstand. Jede Arbeitsrunde verwendet einen Themenbranch.
- OpenAI-Branch dieser Runde: `codex/2026-09-14-desktop-pet-foundation`.
- Anthropic-Runden können beispielsweise `claude/<thema>` verwenden. Herkunft ist eine Dokumentationshilfe, keine andere Qualitätsanforderung.
- Vor Änderungen `git status --short --branch` und aktuelle Übergabe lesen. Uncommittete fremde Änderungen erhalten.
- Commits enthalten Problem, Änderung und tatsächlich ausgeführte Tests. Trailer: `AI-Assisted-By: OpenAI Codex` bzw. `AI-Assisted-By: Anthropic <tatsächliches Modell>`. Keinen Modellnamen erraten und menschliche Git-Autoridentität nicht umschreiben.
- Keine Secrets, lokalen Werkzeuge, Spielstände, Build-Binaries oder Testbilder committen.
- Save-Format oder öffentlichen C++-/C-ABI-Vertrag nicht nebenbei verändern; Version, Migration und Tests anpassen.
- Die JavaScript-Ansicht bekommt keine zweite Pflege-/Entwicklungslogik. Regeln in C++ ändern und dort testen.

## Zweiter Rechner

```powershell
git fetch origin
git switch --track origin/codex/2026-09-14-desktop-pet-foundation
python scripts/build.py
python desktop/server.py
```

Die Remote-Variante dieser Schritte setzt voraus, dass der Branch bereits gepusht wurde. Ohne Push kann der zweite Rechner ihn noch nicht beziehen. Für eigene Arbeit anschließend einen eigenen Branch anlegen. Buildvoraussetzungen stehen in README; Spielstände werden nicht synchronisiert.

## Übergabe je Arbeitsrunde

`progress.md` ergänzen: Ausgangspunkt, Änderungen, genaue Prüfungen, Einschränkungen und nächste Schritte. Ausgeführte Prüfung und bloß geplante Prüfung unterscheiden. Hardwarebehauptungen nur nach realem Build/Flash/Messung treffen. Vor Merge Änderungen unabhängig durchsehen; kein automatischer Main-Push.
