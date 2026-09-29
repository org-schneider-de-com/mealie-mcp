# Bestehende Textzutaten nach Vorschau einmalig korrigieren

> Draft work item. Implementation is not present in this branch yet. Do not merge until the acceptance criteria are met.

**Typ:** Einmalige Aufgabe, kein dauerhaftes MCP-Tool. **WSJF:** `(8 + 5 + 8) / 5 = 4,20`.

**Kontext:** Alte Rezepte mit `quantity: 0` und Textnote skalieren nicht. Der gesamte Bestand soll geprüft werden; bisher gibt es mindestens zwei betroffene Exporte.

**Änderung:** Read-only-Scan aller Rezepte und Vorschau pro Zutat. Bereiche als Mittelwert, unteilbare Stückwerte aufgerundet. Food/Unit-Zuordnung und Originaltext nachvollziehbar festhalten. Erst nach gesonderter Freigabe die ausgewählten Rezepte aktualisieren.

**Abnahme:** Vorschau nennt alle vorgeschlagenen Änderungen; `400–500 g` wird als `450 g` vorgeschlagen. Kein Schreibzugriff vor Freigabe. Schritte/Bilder und nicht betroffene Zutaten bleiben erhalten; Ergebnisbericht listet geänderte und übersprungene Zeilen.

**Dateien:** separates einmaliges Skript/Prüfbericht, kein dauerhaftes Werkzeug in `server.py`. **Abhängigkeit:** Issues 2 und 4, Klärung des Live-Testorts.

## Kontext
[Vereinbarter MCP-Zuschnitt](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/mcp-scope-and-implementation-2026-09-29.md) · [WSJF-Backlog](https://github.com/org-schneider-de-com/mealie-mcp/blob/fix/scalable-recipe-ingredients-api-audit/docs/feature-backlog-wsjf-2026-09-29.md)
