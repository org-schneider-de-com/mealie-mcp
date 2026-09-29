# Wochenplan mit allen Mealie-Typen und Eintragsänderung bedienen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(8 + 5 + 3) / 3 = 5,33`.

**Kontext:** Der Fork erlaubt vier von sieben `PlanEntryType`-Werten; `text` und In-place-Update fehlen als MCP-Eingaben. Große Zeiträume benötigen Pagination.

**Änderung:** Sieben Typen, Text, GET/PUT eines Eintrags und seitenweise Zeitraumabfrage bieten. „Diese/nächste Woche“ interpretiert der Assistent Montag bis Sonntag in `Europe/Berlin`. Kein eigenes Portionsfeld oder Scheduler.

**Abnahme:** Snack, Getränk und Dessert lassen sich anlegen/ändern. Ein Rezepttermin und ein freier Texttermin bleiben nach Änderung korrekt. Alle Seiten eines gewählten Zeitraums sind erreichbar.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** keine; für vollständigen Chat-Einkauf mit Issue 3 kombinieren.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
