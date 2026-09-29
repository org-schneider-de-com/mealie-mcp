# Rezeptsuche mit Mealie-Filtern und Pagination erweitern

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(5 + 3 + 3) / 2 = 5,50`.

**Kontext:** `search_recipes` liefert derzeit höchstens die erste Seite mit bis zu 100 Treffern; die API unterstützt weitere Filter.

**Änderung:** `page`, `perPage`, Gesamtzahl/nächste Seite und ausgewählte Mealie-Filter für Text, Tags, Kategorien, Foods und Kochbuch anbieten. Keine eigene Suchdatenbank oder errechnete Zeitfilter.

**Abnahme:** Mehr als 100 Treffer sind seitenweise erreichbar. Kombination aus Text, Tag und Kategorie wird korrekt an die Mealie-API gesendet; Antwort zeigt Pagination.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Parametertests. **Abhängigkeit:** keine.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
