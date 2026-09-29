# Einkaufslisten und Artikel über native Mealie-CRUD-Werkzeuge bearbeiten

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Feature. **WSJF:** `(8 + 5 + 3) / 3 = 5,33`.

**Kontext:** Der Fork kann Listen anlegen/auflisten und Artikel als Freitext hinzufügen, abhaken/löschen. Umbenennen/Löschen einer Liste sowie Menge/Food/Unit eines Artikels bearbeiten fehlen.

**Änderung:** Dokumentierte List- und Item-CRUD-Operationen einschließlich strukturierter Artikelmenge und Unit/Food anbieten. Bestehende manuelle und abgehakte Artikel nur auf ausdrückliche Änderung hin mutieren. Für Löschungen Objekt und Folgen vor Bestätigung zeigen.

**Abnahme:** Liste umbenennen; strukturierten Artikel anlegen und Menge ändern; abhaken/zurücksetzen. Andere Artikel bleiben unverändert. Löschziel ist vor dem Aufruf eindeutig.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** Issue 1.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
