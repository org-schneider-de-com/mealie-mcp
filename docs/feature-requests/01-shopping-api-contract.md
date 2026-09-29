# Einkaufslistenartikel über dokumentierte Mealie-Antworten lesen und anlegen

> Draft work item. Implementation is not present in this branch yet. Do not merge this PR until its acceptance criteria are met.

**Typ:** Bug. **WSJF:** `(8 + 8 + 8) / 2 = 12,00`.

**Kontext:** Der Fork sendet bei `GET /api/households/shopping/items` den nicht dokumentierten Queryparameter `shoppingListId`. `POST /api/households/shopping/items` liefert laut gelieferter OpenAPI `ShoppingListItemsCollectionOut` mit `createdItems`; der Fork liest die neue ID wie bei einem Einzelobjekt aus.

**Änderung:** Artikel einer konkreten Liste aus `GET /api/households/shopping/lists/{item_id}` und `listItems` lesen. Bei Artikel-POST `createdItems` auswerten und die tatsächliche ID zurückgeben. API-Fehler sichtbar lassen.

**Abnahme:** Liste A und B enthalten verschiedene Artikel; Abruf von A zeigt nur A. Ein erfolgreicher POST gibt die erzeugte Item-ID zurück und führt nicht wegen fehlerhafter Antwortverarbeitung zu einem zweiten POST.

**Dateien:** `src/mealie_mcp/{client,server}.py`, gezielte HTTP-Vertragstests. **Abhängigkeit:** keine.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
