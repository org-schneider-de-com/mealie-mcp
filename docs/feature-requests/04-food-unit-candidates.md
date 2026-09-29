# Vor Food-/Unit-Neuanlage ähnliche Mealie-Einträge vorschlagen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(5 + 5 + 8) / 3 = 6,00`.

**Kontext:** Der Code in PR #1 kann unbekannte Foods/Units direkt anlegen. Ähnliche Namen sollen vor neuer Katalogmutation gezeigt werden, um Dubletten zu vermeiden.

**Änderung:** Vor Neuanlage vorhandene Mealie-Foods/Units durchsuchen und Kandidaten zurückgeben. Bei Mehrdeutigkeit Nutzerentscheidung abwarten; ausdrücklich neue Begriffe danach anlegen. Keine zweite Food-Datenbank.

**Abnahme:** Ähnlicher bestehender Food-Name erzeugt Auswahl statt stiller Dublette. Neu bestätigter Eintrag wird genau einmal angelegt und im Rezept referenziert.

**Dateien:** `src/mealie_mcp/{client,server}.py`, gezielte Katalogtests. **Abhängigkeit:** mit PR #1 abstimmen.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
