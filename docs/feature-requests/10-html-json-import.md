# Eingefügtes HTML oder JSON über Mealie importieren

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(5 + 3 + 3) / 3 = 3,67`.

**Kontext:** URL-Import existiert, aber eingefügte HTML-/JSON-Rezepte bei blockiertem Seitenabruf haben kein MCP-Werkzeug.

**Änderung:** Mealies `/api/recipes/create/html-or-json` sicher exponieren; importiertes Rezept und seine Zutaten zurückgeben, um Struktur/Portionen zu prüfen. Keine eigenständige Scraper-Plattform bauen.

**Abnahme:** Ein gültiger HTML/JSON-Rezeptauszug erzeugt ein Rezept; fehlende strukturierte Mengen werden gemeldet. Ein fehlerhafter Import liefert eine verständliche API-Fehlermeldung ohne leeres Doppelrezept.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Mocks. **Abhängigkeit:** Issue 2.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
