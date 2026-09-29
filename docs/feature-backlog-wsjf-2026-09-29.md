# Mealie-MCP: WSJF-Backlog und GitHub Issues

Stand: 29. September 2026. Grundlage ist der [vereinbarte MCP-Zuschnitt](mcp-scope-and-implementation-2026-09-29.md), nicht die vollständige 60-Punkte-API-Inventur. Die 14 GitHub Issues [#15–#28](https://github.com/org-schneider-de-com/mealie-mcp/issues) sind jetzt angelegt und jeweils mit einem Draft-PR verknüpft. PR #1 enthält bereits Code für skalierbare Zutaten; PRs #2–#14 enthalten derzeit die Aufgabenbeschreibung, noch keine Implementierung.

## Methode

`WSJF = (Business Value + Time Criticality + Risk Reduction / Opportunity Enablement) / Job Size`. Alle vier Werte sind **relative Schätzungen** aus `1, 2, 3, 5, 8` für den Fünf-Personen-Haushalt und den beobachteten Fork. `8` bedeutet im Vergleich zu den anderen Einträgen hoch, keine Stunden-/Euroangabe. Time Criticality meint hier die Dringlichkeit, den gegenwärtigen täglichen Ablauf zu reparieren, nicht eine erfundene externe Deadline. Auf zwei Dezimalstellen angezeigte Quotienten sind Sortierhilfen, keine Messgenauigkeit. Technische Abhängigkeiten gehen vor der Zahlenreihenfolge; ein bereits laufender PR wird nicht künstlich gestoppt.

| Rang | Issue | Draft-PR | Typ | Feature / Fehler | BV | TC | RR/OE | Größe | WSJF | Stand / Abhängigkeit |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | [#15](https://github.com/org-schneider-de-com/mealie-mcp/issues/15) | [#2](https://github.com/org-schneider-de-com/mealie-mcp/pull/2) | Bug | Einkaufsartikel lesen und POST-Antwort korrekt auswerten | 8 | 8 | 8 | 2 | **12,00** | Grundlage für Artikelbearbeitung |
| 2 | [#16](https://github.com/org-schneider-de-com/mealie-mcp/issues/16) | [#1](https://github.com/org-schneider-de-com/mealie-mcp/pull/1) | Feature | Strukturierte Zutaten und numerische Portionen | 8 | 8 | 8 | 3 | **8,00** | Entwurfs-PR #1 in Arbeit |
| 3 | [#17](https://github.com/org-schneider-de-com/mealie-mcp/issues/17) | [#3](https://github.com/org-schneider-de-com/mealie-mcp/pull/3) | Feature | Native Rezept-zu-Einkaufsliste-Endpunkte | 8 | 8 | 5 | 3 | **7,00** | Strukturierte Zutaten, Einkaufsvertrag |
| 4 | [#18](https://github.com/org-schneider-de-com/mealie-mcp/issues/18) | [#4](https://github.com/org-schneider-de-com/mealie-mcp/pull/4) | Feature | Food-/Unit-Treffer vor Neuanlage zeigen | 5 | 5 | 8 | 3 | **6,00** | Ergänzt PR #1 |
| 5 | [#19](https://github.com/org-schneider-de-com/mealie-mcp/issues/19) | [#5](https://github.com/org-schneider-de-com/mealie-mcp/pull/5) | Feature | Rezeptsuche mit Filtern und Pagination | 5 | 3 | 3 | 2 | **5,50** | Unabhängig |
| 6 | [#20](https://github.com/org-schneider-de-com/mealie-mcp/issues/20) | [#6](https://github.com/org-schneider-de-com/mealie-mcp/pull/6) | Feature | Wochenplan mit sieben Typen, Text und Update | 8 | 5 | 3 | 3 | **5,33** | Für Chat-Ablauf Plan → Einkauf |
| 7 | [#21](https://github.com/org-schneider-de-com/mealie-mcp/issues/21) | [#7](https://github.com/org-schneider-de-com/mealie-mcp/pull/7) | Feature | Listen und Artikel mit nativer API bearbeiten | 8 | 5 | 3 | 3 | **5,33** | Bug aus Rang 1 zuerst |
| 8 | [#22](https://github.com/org-schneider-de-com/mealie-mcp/issues/22) | [#8](https://github.com/org-schneider-de-com/mealie-mcp/pull/8) | Feature | Quelle, Zeiten und explizite Nährwerte pflegen | 5 | 3 | 2 | 2 | **5,00** | Grundlage für BLS-Speicherung |
| 9 | [#23](https://github.com/org-schneider-de-com/mealie-mcp/issues/23) | [#9](https://github.com/org-schneider-de-com/mealie-mcp/pull/9) | Einmalige Aufgabe | Textzutaten im Altbestand geprüft migrieren | 8 | 5 | 8 | 5 | **4,20** | PR #1, API-Verifikation, Freigabe |
| 10 | [#24](https://github.com/org-schneider-de-com/mealie-mcp/issues/24) | [#10](https://github.com/org-schneider-de-com/mealie-mcp/pull/10) | Feature | Eingefügtes HTML/JSON importieren | 5 | 3 | 3 | 3 | **3,67** | Strukturprüfung aus Rang 2 |
| 11 | [#25](https://github.com/org-schneider-de-com/mealie-mcp/issues/25) | [#11](https://github.com/org-schneider-de-com/mealie-mcp/pull/11) | Feature | Rezeptbilder setzen, ersetzen und entfernen | 3 | 2 | 2 | 2 | **3,50** | Vorhandenen Upload ergänzen |
| 12 | [#26](https://github.com/org-schneider-de-com/mealie-mcp/issues/26) | [#12](https://github.com/org-schneider-de-com/mealie-mcp/pull/12) | Feature | Kochbücher und Tags vollständig pflegen | 5 | 3 | 2 | 3 | **3,33** | Vorhandene List/Create-Tools ergänzen |
| 13 | [#27](https://github.com/org-schneider-de-com/mealie-mcp/issues/27) | [#13](https://github.com/org-schneider-de-com/mealie-mcp/pull/13) | Feature | „Zuletzt gekocht“ nach Bestätigung setzen | 2 | 2 | 1 | 2 | **2,50** | Kein Scheduler, keine automatische Ableitung |
| 14 | [#28](https://github.com/org-schneider-de-com/mealie-mcp/issues/28) | [#14](https://github.com/org-schneider-de-com/mealie-mcp/pull/14) | Feature | BLS-Nährwerte bei Neuanlage/auf Nachfrage | 8 | 3 | 5 | 8 | **2,00** | Rezeptfelder, lokaler BLS, Datenzuordnung |

Die Tabellenreihenfolge ist eine **WSJF-Sortierung**, keine starre Commit-Reihenfolge. Insbesondere läuft PR #1 bereits; die Einkaufsfunktionen brauchen dessen strukturierte Zutaten. Der BLS-Eintrag hat trotz hohem persönlichen Nutzen einen niedrigeren Quotienten, weil Matching, Einheiten und Datenaufbereitung erheblichen Aufwand verursachen. Kein Ticket verlangt, Mealies Skalierungs- und Einkaufs-Konsolidierungslogik nachzubauen.

## Issue 1 — Einkaufslistenartikel über dokumentierte Mealie-Antworten lesen und anlegen

**Typ:** Bug. **WSJF:** `(8 + 8 + 8) / 2 = 12,00`.

**Kontext:** Der Fork sendet bei `GET /api/households/shopping/items` den nicht dokumentierten Queryparameter `shoppingListId`. `POST /api/households/shopping/items` liefert laut gelieferter OpenAPI `ShoppingListItemsCollectionOut` mit `createdItems`; der Fork liest die neue ID wie bei einem Einzelobjekt aus.

**Änderung:** Artikel einer konkreten Liste aus `GET /api/households/shopping/lists/{item_id}` und `listItems` lesen. Bei Artikel-POST `createdItems` auswerten und die tatsächliche ID zurückgeben. API-Fehler sichtbar lassen.

**Abnahme:** Liste A und B enthalten verschiedene Artikel; Abruf von A zeigt nur A. Ein erfolgreicher POST gibt die erzeugte Item-ID zurück und führt nicht wegen fehlerhafter Antwortverarbeitung zu einem zweiten POST.

**Dateien:** `src/mealie_mcp/{client,server}.py`, gezielte HTTP-Vertragstests. **Abhängigkeit:** keine.

## Issue 2 — Rezepte mit strukturierten Zutaten und numerischen Portionen speichern

**Typ:** Feature, bereits teilweise in [Entwurfs-PR #1](https://github.com/org-schneider-de-com/mealie-mcp/pull/1). **WSJF:** `(8 + 8 + 8) / 3 = 8,00`.

**Kontext:** Die zwei MCP-Exporte enthalten 25 Zutaten ohne strukturierte Menge, Food oder Unit. `recipeServings` ist 3; zusätzlich steht ein starrer Portions-Yield im Rezept.

**Änderung:** Mealie-Parser oder explizite `quantity`/`unit`/`food`-Objekte verwenden. `recipeServings` numerisch speichern; keinen zweiten starren Text für Personenzahl. Unklare Mengen vor dem Schreiben klären. Einmaliges Skalieren ändert das Grundrezept nicht; Mealie übernimmt die Rechnung.

**Abnahme:** Testrezept mit drei Grundportionen und 300 g einer Zutat zeigt in Mealie bei vier Portionen 400 g. Export enthält Menge, Food und Unit. Mehrdeutiger Bereich führt zu Rückfrage. Bestehende Rezepte bleiben bis zur getrennten Migration unangetastet.

**Dateien:** `src/mealie_mcp/{client,server}.py`, `tests/test_recipe_ingredients.py`. **Abhängigkeit:** PR #1 weiterführen, nicht doppelt implementieren.

## Issue 3 — Rezeptzutaten über Mealie zur Einkaufsliste hinzufügen und entfernen

**Typ:** Feature. **WSJF:** `(8 + 8 + 5) / 3 = 7,00`.

**Kontext:** Der Fork bietet Mealies Rezept-zu-Liste-Endpunkte nicht als MCP-Werkzeuge. Gewünscht ist ein bestehender Listenname, Auswahl geplanter Rezepte und eine beim Einkauf abgefragte positive Portionszahl, ohne eigene Plan-/Listen-Datenbank.

**Änderung:** Natives Einzel-/Bulk-Add und Entfernen von Rezeptbeiträgen anbieten; vorhandene Rezeptverknüpfungen lesbar machen. `recipeIncrementQuantity` nur nach Prüfung seiner Semantik in der laufenden Mealie-Version aus gewünschter Portionenzahl ableiten. Vor erneutem Hinzufügen fragt der Assistent.

**Abnahme:** Rezept mit strukturierten Zutaten erscheint mit Rezeptbezug und korrektem Mealie-Mengenfaktor auf gewählter Liste. Manuelle Einträge bleiben erhalten; ein schon verknüpftes Rezept wird nicht still erneut addiert; Entfernen eines Beitrags erhält andere Bezüge.

**Dateien:** `src/mealie_mcp/{client,server}.py`, HTTP-Vertragstests. **Abhängigkeit:** Issues 1 und 2.

## Issue 4 — Vor Food-/Unit-Neuanlage ähnliche Mealie-Einträge vorschlagen

**Typ:** Feature. **WSJF:** `(5 + 5 + 8) / 3 = 6,00`.

**Kontext:** Der Code in PR #1 kann unbekannte Foods/Units direkt anlegen. Ähnliche Namen sollen vor neuer Katalogmutation gezeigt werden, um Dubletten zu vermeiden.

**Änderung:** Vor Neuanlage vorhandene Mealie-Foods/Units durchsuchen und Kandidaten zurückgeben. Bei Mehrdeutigkeit Nutzerentscheidung abwarten; ausdrücklich neue Begriffe danach anlegen. Keine zweite Food-Datenbank.

**Abnahme:** Ähnlicher bestehender Food-Name erzeugt Auswahl statt stiller Dublette. Neu bestätigter Eintrag wird genau einmal angelegt und im Rezept referenziert.

**Dateien:** `src/mealie_mcp/{client,server}.py`, gezielte Katalogtests. **Abhängigkeit:** mit PR #1 abstimmen.

## Issue 5 — Rezeptsuche mit Mealie-Filtern und Pagination erweitern

**Typ:** Feature. **WSJF:** `(5 + 3 + 3) / 2 = 5,50`.

**Kontext:** `search_recipes` liefert derzeit höchstens die erste Seite mit bis zu 100 Treffern; die API unterstützt weitere Filter.

**Änderung:** `page`, `perPage`, Gesamtzahl/nächste Seite und ausgewählte Mealie-Filter für Text, Tags, Kategorien, Foods und Kochbuch anbieten. Keine eigene Suchdatenbank oder errechnete Zeitfilter.

**Abnahme:** Mehr als 100 Treffer sind seitenweise erreichbar. Kombination aus Text, Tag und Kategorie wird korrekt an die Mealie-API gesendet; Antwort zeigt Pagination.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Parametertests. **Abhängigkeit:** keine.

## Issue 6 — Wochenplan mit allen Mealie-Typen und Eintragsänderung bedienen

**Typ:** Feature. **WSJF:** `(8 + 5 + 3) / 3 = 5,33`.

**Kontext:** Der Fork erlaubt vier von sieben `PlanEntryType`-Werten; `text` und In-place-Update fehlen als MCP-Eingaben. Große Zeiträume benötigen Pagination.

**Änderung:** Sieben Typen, Text, GET/PUT eines Eintrags und seitenweise Zeitraumabfrage bieten. „Diese/nächste Woche“ interpretiert der Assistent Montag bis Sonntag in `Europe/Berlin`. Kein eigenes Portionsfeld oder Scheduler.

**Abnahme:** Snack, Getränk und Dessert lassen sich anlegen/ändern. Ein Rezepttermin und ein freier Texttermin bleiben nach Änderung korrekt. Alle Seiten eines gewählten Zeitraums sind erreichbar.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** keine; für vollständigen Chat-Einkauf mit Issue 3 kombinieren.

## Issue 7 — Einkaufslisten und Artikel über native Mealie-CRUD-Werkzeuge bearbeiten

**Typ:** Feature. **WSJF:** `(8 + 5 + 3) / 3 = 5,33`.

**Kontext:** Der Fork kann Listen anlegen/auflisten und Artikel als Freitext hinzufügen, abhaken/löschen. Umbenennen/Löschen einer Liste sowie Menge/Food/Unit eines Artikels bearbeiten fehlen.

**Änderung:** Dokumentierte List- und Item-CRUD-Operationen einschließlich strukturierter Artikelmenge und Unit/Food anbieten. Bestehende manuelle und abgehakte Artikel nur auf ausdrückliche Änderung hin mutieren. Für Löschungen Objekt und Folgen vor Bestätigung zeigen.

**Abnahme:** Liste umbenennen; strukturierten Artikel anlegen und Menge ändern; abhaken/zurücksetzen. Andere Artikel bleiben unverändert. Löschziel ist vor dem Aufruf eindeutig.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** Issue 1.

## Issue 8 — Rezeptquelle, Zeiten und explizite Nährwerte bearbeiten

**Typ:** Feature. **WSJF:** `(5 + 3 + 2) / 2 = 5,00`.

**Kontext:** Der Fork deckt nur einen Teil des Mealie-Rezeptmodells ab. Quelle, `performTime` und Nährwertfelder fehlen in Create/Update, obwohl sie für die Rezeptpflege gewünscht sind.

**Änderung:** `orgURL`, Zeitfelder und explizit gelieferte Nutrition-/Anzeige-Felder über Mealie speichern und zurücklesen. Keine automatische Nährwertberechnung in diesem Issue; Werte sind bei Mealie statisch.

**Abnahme:** Quelle, Zeiten und ein ausdrücklich übergebener Nährwert sind nach GET erhalten. Änderung von Zutaten überschreibt Nährwerte nicht still; fehlende Werte werden nicht erfunden.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Rezept-Vertragstests. **Abhängigkeit:** Issue 2; Voraussetzung für BLS-Issue 14.

## Issue 9 — Bestehende Textzutaten nach Vorschau einmalig korrigieren

**Typ:** Einmalige Aufgabe, kein dauerhaftes MCP-Tool. **WSJF:** `(8 + 5 + 8) / 5 = 4,20`.

**Kontext:** Alte Rezepte mit `quantity: 0` und Textnote skalieren nicht. Der gesamte Bestand soll geprüft werden; bisher gibt es mindestens zwei betroffene Exporte.

**Änderung:** Read-only-Scan aller Rezepte und Vorschau pro Zutat. Bereiche als Mittelwert, unteilbare Stückwerte aufgerundet. Food/Unit-Zuordnung und Originaltext nachvollziehbar festhalten. Erst nach gesonderter Freigabe die ausgewählten Rezepte aktualisieren.

**Abnahme:** Vorschau nennt alle vorgeschlagenen Änderungen; `400–500 g` wird als `450 g` vorgeschlagen. Kein Schreibzugriff vor Freigabe. Schritte/Bilder und nicht betroffene Zutaten bleiben erhalten; Ergebnisbericht listet geänderte und übersprungene Zeilen.

**Dateien:** separates einmaliges Skript/Prüfbericht, kein dauerhaftes Werkzeug in `server.py`. **Abhängigkeit:** Issues 2 und 4, Klärung des Live-Testorts.

## Issue 10 — Eingefügtes HTML oder JSON über Mealie importieren

**Typ:** Feature. **WSJF:** `(5 + 3 + 3) / 3 = 3,67`.

**Kontext:** URL-Import existiert, aber eingefügte HTML-/JSON-Rezepte bei blockiertem Seitenabruf haben kein MCP-Werkzeug.

**Änderung:** Mealies `/api/recipes/create/html-or-json` sicher exponieren; importiertes Rezept und seine Zutaten zurückgeben, um Struktur/Portionen zu prüfen. Keine eigenständige Scraper-Plattform bauen.

**Abnahme:** Ein gültiger HTML/JSON-Rezeptauszug erzeugt ein Rezept; fehlende strukturierte Mengen werden gemeldet. Ein fehlerhafter Import liefert eine verständliche API-Fehlermeldung ohne leeres Doppelrezept.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Mocks. **Abhängigkeit:** Issue 2.

## Issue 11 — Rezeptbilder über Mealie setzen, ersetzen und entfernen

**Typ:** Feature. **WSJF:** `(3 + 2 + 2) / 2 = 3,50`.

**Kontext:** Der Fork unterstützt Bild-Upload aus URL/Base64, aber kein ausdrückliches Löschen; im manuellen Referenzexport liegt ein Bild vor.

**Änderung:** Vorhandene Upload-Aufrufe mit Mealies DELETE-Bildroute vervollständigen und Ergebnis/Fehler klar zurückgeben. Sonstige Assets und Videos bleiben außerhalb des ersten Ausbaus.

**Abnahme:** Ein Wegwerf-Rezept erhält ein Bild, wird ersetzt und danach ohne Bild aus Mealie gelesen. Ungültige Bilddaten führen nicht zu einer Erfolgsmeldung.

**Dateien:** `src/mealie_mcp/{client,server}.py`, Bild-Vertragstests. **Abhängigkeit:** keine.

## Issue 12 — Kochbücher und Tags mit Mealie-Werkzeugen vollständig pflegen

**Typ:** Feature. **WSJF:** `(5 + 3 + 2) / 3 = 3,33`.

**Kontext:** Der Fork listet/erstellt Kochbücher und kann Tags auflisten/Rezepte zuordnen. Details, Bearbeiten/Löschen von Kochbüchern und gezielte Tag-Pflege fehlen.

**Änderung:** Mealies Cookbook- und Tag-CRUD ergänzen, inklusive Such-/Filterbezügen. Kein eigener Sammlungs- oder Favoritenzustand; gemeinsame Backend-Identität bleibt bestehen.

**Abnahme:** Kochbuch mit Filter anlegen, lesen, umbenennen, wieder löschen; Tag bearbeiten und einer Rezeptsuche zuordnen. Persönliche Favoriten/Bewertungen sind ausdrücklich nicht enthalten.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstests. **Abhängigkeit:** Issue 5 für komfortable gefilterte Rezeptliste, CRUD technisch unabhängig.

## Issue 13 — „Zuletzt gekocht“ erst nach Chat-Bestätigung setzen

**Typ:** Feature. **WSJF:** `(2 + 2 + 1) / 2 = 2,50`.

**Kontext:** Ein Planeintrag beweist nicht, dass ein Rezept gekocht wurde. Der Nutzer möchte Bestätigung im Chat, keine automatische Nachtverarbeitung oder Signal-Nachricht.

**Änderung:** Mealies `PATCH /api/recipes/{slug}/last-made` als kleines Werkzeug anbieten. Assistent fragt bei offenem geplantem Rezept nach, bevor das Datum geändert wird.

**Abnahme:** Nur ein bestätigtes Rezept erhält das angegebene Kochdatum; bloße Planung oder vergangener Termin verändert `lastMade` nicht.

**Dateien:** `src/mealie_mcp/{client,server}.py`, API-Vertragstest. **Abhängigkeit:** keine.

## Issue 14 — BLS-Nährwerte bei Rezeptanlage und auf Nachfrage berechnen

**Typ:** Feature, begrenzte Ausnahme vom Mealie-Adapter. **WSJF:** `(8 + 3 + 5) / 8 = 2,00`.

**Kontext:** Mealie speichert Nährwerte statisch. Gewünscht ist ein lokal geprüfter Bundeslebensmittelschlüssel 4.0 (CC BY 4.0, Namensnennung) im MCP, einmal bei Neuanlage und später ausdrücklich auf Nachfrage.

**Änderung:** Strukturierte Rezeptzutaten lokal BLS-Einträgen zuordnen; Mehrdeutigkeit als Auswahl, Stück-/Volumengewichte als sichtbare korrigierbare Schätzung. Berechnung mit Quellen- und Vollständigkeitsstatus zeigen. Vor Überschreiben vorhandener Mealie-Nährwerte bestätigen; kein eigener Rezeptbestand oder Hintergrundsync. BLS-Ausfall blockiert Rezeptanlage nicht.

**Abnahme:** Eindeutiger, mehrdeutiger und fehlender Treffer sind unterscheidbar. Eine unvollständige Summe wird nicht als vollständiger Rezeptwert gespeichert. Rezept wird bei BLS-Fehler trotzdem angelegt. Berechnete Werte enthalten Grundportionen und Schätzannahmen; Quelle wird genannt.

**Dateien:** separates BLS-Modul/Datenimport, `src/mealie_mcp/{client,server}.py`, fachliche Rechenfälle und API-Vertragstests. **Abhängigkeit:** Issues 2 und 8 sowie technische Prüfung des BLS-Datenformats.

## Verknüpfungen und Stand

Jeder Abschnitt oben ist als eigenständiges GitHub Issue veröffentlicht. Die Rangtabelle verlinkt Issue und zugehörigen Draft-PR. Erst wenn der jeweilige Code implementiert und die Abnahmekriterien erfüllt sind, kann ein PR zur Prüfung bereitgestellt werden. **Kein PR wird allein wegen einer abgeschlossenen Aufgabenbeschreibung gemergt.**
