# Rezeptquelle, Zeiten und explizite Nährwerte bearbeiten

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(5 + 3 + 2) / 2 = 5,00`.

**Kontext:** Der Fork deckt nur einen Teil des Mealie-Rezeptmodells ab. Quelle, `performTime` und Nährwertfelder fehlen in Create/Update, obwohl sie für die Rezeptpflege gewünscht sind.

**Änderung:** `orgURL`, Zeitfelder und explizit gelieferte Nutrition-/Anzeige-Felder über Mealie speichern und zurücklesen. Keine automatische Nährwertberechnung in diesem Issue; Werte sind bei Mealie statisch.

**Abnahme:** Quelle, Zeiten und ein ausdrücklich übergebener Nährwert sind nach GET erhalten. Änderung von Zutaten überschreibt Nährwerte nicht still; fehlende Werte werden nicht erfunden.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Rezept-Vertragstests. **Abhängigkeit:** Issue 2; Voraussetzung für BLS-Issue 14.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
