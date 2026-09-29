# Rezeptzutaten über Mealie zur Einkaufsliste hinzufügen und entfernen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(8 + 8 + 5) / 3 = 7,00`.

**Kontext:** Der Fork bietet Mealies Rezept-zu-Liste-Endpunkte nicht als MCP-Werkzeuge. Gewünscht ist ein bestehender Listenname, Auswahl geplanter Rezepte und eine beim Einkauf abgefragte positive Portionszahl, ohne eigene Plan-/Listen-Datenbank.

**Änderung:** Natives Einzel-/Bulk-Add und Entfernen von Rezeptbeiträgen anbieten; vorhandene Rezeptverknüpfungen lesbar machen. `recipeIncrementQuantity` nur nach Prüfung seiner Semantik in der laufenden Mealie-Version aus gewünschter Portionenzahl ableiten. Vor erneutem Hinzufügen fragt der Assistent.

**Abnahme:** Rezept mit strukturierten Zutaten erscheint mit Rezeptbezug und korrektem Mealie-Mengenfaktor auf gewählter Liste. Manuelle Einträge bleiben erhalten; ein schon verknüpftes Rezept wird nicht still erneut addiert; Entfernen eines Beitrags erhält andere Bezüge.

**Dateien:** `src/mealie_mcp/{client,server}.py`, HTTP-Vertragstests. **Abhängigkeit:** Issues 1 und 2.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
