# Rezeptbilder über Mealie setzen, ersetzen und entfernen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(3 + 2 + 2) / 2 = 3,50`.

**Kontext:** Der Fork unterstützt Bild-Upload aus URL/Base64, aber kein ausdrückliches Löschen; im manuellen Referenzexport liegt ein Bild vor.

**Änderung:** Vorhandene Upload-Aufrufe mit Mealies DELETE-Bildroute vervollständigen und Ergebnis/Fehler klar zurückgeben. Sonstige Assets und Videos bleiben außerhalb des ersten Ausbaus.

**Abnahme:** Ein Wegwerf-Rezept erhält ein Bild, wird ersetzt und danach ohne Bild aus Mealie gelesen. Ungültige Bilddaten führen nicht zu einer Erfolgsmeldung.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Bild-Vertragstests. **Abhängigkeit:** keine.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
