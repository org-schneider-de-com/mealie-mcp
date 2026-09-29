# „Zuletzt gekocht“ erst nach Chat-Bestätigung setzen

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(2 + 2 + 1) / 2 = 2,50`.

**Kontext:** Ein Planeintrag beweist nicht, dass ein Rezept gekocht wurde. Der Nutzer möchte Bestätigung im Chat, keine automatische Nachtverarbeitung oder Signal-Nachricht.

**Änderung:** Mealies `PATCH /api/recipes/{slug}/last-made` als kleines Werkzeug anbieten. Assistent fragt bei offenem geplantem Rezept nach, bevor das Datum geändert wird.

**Abnahme:** Nur ein bestätigtes Rezept erhält das angegebene Kochdatum; bloße Planung oder vergangener Termin verändert `lastMade` nicht.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstest. **Abhängigkeit:** keine.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
