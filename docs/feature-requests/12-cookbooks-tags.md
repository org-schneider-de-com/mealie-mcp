# Kochbücher und Tags mit Mealie-Werkzeugen vollständig pflegen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(5 + 3 + 2) / 3 = 3,33`.

**Kontext:** Der Fork listet/erstellt Kochbücher und kann Tags auflisten/Rezepte zuordnen. Details, Bearbeiten/Löschen von Kochbüchern und gezielte Tag-Pflege fehlen.

**Änderung:** Mealies Cookbook- und Tag-CRUD ergänzen, inklusive Such-/Filterbezügen. Kein eigener Sammlungs- oder Favoritenzustand; gemeinsame Backend-Identität bleibt bestehen.

**Abnahme:** Kochbuch mit Filter anlegen, lesen, umbenennen, wieder löschen; Tag bearbeiten und einer Rezeptsuche zuordnen. Persönliche Favoriten/Bewertungen sind ausdrücklich nicht enthalten.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** Issue 5 für komfortable gefilterte Rezeptliste, CRUD technisch unabhängig.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
