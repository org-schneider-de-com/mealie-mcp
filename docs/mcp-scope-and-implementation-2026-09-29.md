# Vereinbarter Zuschnitt des Mealie-MCP-Servers

Stand: 29. September 2026. Dieses Dokument hält die Entscheidungen aus der anschließenden Fragerunde fest. Die [60-Punkte-Funktionsprüfung](family-function-audit-2026-09-29.md) beschreibt vorhandene und fehlende Fähigkeiten der vier Server; sie ist **keine** Liste von 60 Funktionen, die der Fork nachbauen soll.

## Grundsatz

Der MCP-Server stellt die für Rezepte, Wochenplan, Einkauf, Kochbücher und Tags nötigen **Mealie-Funktionen** mit korrekten Parametern, Antworten und begrenzten Hilfen für Mealie-typische Mehrschritt-Aufrufe bereit. Mealie bleibt die Quelle für Rezepte, Mengen, Plan, Einkaufsfortschritt und die Zusammenfassung strukturierter Zutaten. Der Assistent kann mehrere MCP-Werkzeuge nacheinander nutzen; dafür entsteht kein eigener persistenter Wochenplan- oder Einkaufs-Synchronisationsdienst.

Das entspricht Mealies dokumentierter [Zutatenskalierung und Einkaufs-Zusammenfassung](https://mealie.io/documentation/getting-started/faq/#how-do-i-enable-smart-ingredient-handling) sowie den vorhandenen [Plan-, Einkaufslisten- und Kochbuchfunktionen](https://mealie.io/documentation/getting-started/features/).

| Zuständigkeit | Konkrete Grenze |
| --- | --- |
| Mealie | Rezepte und Grundportionen speichern; strukturierte Foods/Units skalieren; Rezeptzutaten in Einkaufslisten verknüpfen und zusammenfassen; Einkaufshäkchen und Labels verwalten. |
| MCP-Server | Passende API-Operationen korrekt anbieten, z. B. Rezept-Shell und Inhalt in einem Werkzeug anlegen, Listenartikel aus dem dokumentierten Antwortformat lesen, Rezeptbeiträge hinzufügen/entfernen. |
| Assistent im Gespräch | Zeitraum wählen, Portionen beim Einkauf abfragen, freitextliche Plan-Einträge zeigen, vorhandene Rezeptverknüpfungen vor erneutem Hinzufügen erkennen und die passenden Werkzeuge aufrufen. |
| Begrenzte Ausnahme | Ein optionaler BLS-Abgleich für Nährwerte bei Rezept-Neuanlage und später auf Nachfrage. Er ist keine eigenständige Rezept- oder Vorratsdatenbank. |
| Einmalige Arbeit | Bestehende Textzutaten nach Vorschau korrigieren; dafür kein dauerhaftes MCP-Migrationswerkzeug. |

## Verhalten der Mealie-Werkzeuge

### Rezept und Zutaten

- Neue Rezepte haben strukturierte `quantity`, `unit` und `food` sowie numerische `recipeServings`; ein Text wie „3 Portionen“ wird nicht zusätzlich als starres `recipeYield` gespeichert. Nicht eindeutig zerlegbare Mengen werden dem Nutzer zur Entscheidung vorgelegt. Zutaten ohne feste Menge bleiben als Text erhalten.
- Die in Mealie gespeicherte Grundportionenzahl bleibt bestehen. „Heute für vier Personen“ skaliert nur die aktuelle Ansicht beziehungsweise den Rezeptbeitrag zur Einkaufsliste. Der MCP implementiert weder eigene Mengenrundung noch eigene Food-/Unit-Konsolidierung.
- Unbekannte Food-/Unit-Begriffe: ähnliche vorhandene Einträge zeigen, bevor ein neuer Katalogeintrag angelegt wird. Bei Rezepten aus Chat, URL oder eingefügtem Text dürfen uneindeutige Zutaten nicht still als nicht skalierbare Mengennotiz enden.
- Im ersten Ausbau: manuelle Anlage, URL- und Text/HTML/JSON-Import, Quelle, Vorbereitungs-/Koch-/Gesamtzeit, explizite Nährwertfelder und Rezeptbild setzen/ersetzen/löschen. ZIP-Import, sonstige Anhänge, Teilen und Export bleiben späteren Ausbaustufen vorbehalten.

### Wochenplan und Einkauf

- Planeinträge können gelesen, angelegt, geändert und gelöscht werden, mit freien Texten und allen sieben in der gelieferten OpenAPI enthaltenen Mahlzeittypen. „Diese/nächste Woche“ bedeutet Montag bis Sonntag in `Europe/Berlin`. Regeln, Zufallsvorschläge und Benachrichtigungen sind nicht Bestandteil des ersten Ausbaus.
- Die gewünschte Portionszahl wird **beim Übertragen in die Einkaufsliste** je geplanter Rezeptmahlzeit abgefragt; sie wird nicht zusätzlich im Planeintrag gespeichert. Positive Dezimalwerte sind erlaubt, soweit der tatsächlich eingesetzte Mealie-Endpunkt sie annimmt. Ein mehrfach geplanter Kochvorgang zählt mehrfach; als Resteverwertung bezeichnete Freitext-Einträge werden vor dem Einkauf besprochen.
- Eine vorhandene Einkaufsliste wird ausgewählt. Der Assistent verwendet Mealies Einzel- oder Bulk-Rezept-zu-Liste-Endpunkte. Er erfindet keine Zutaten für reine Freitext-Mahlzeiten, sondern fragt nach. Bereits verknüpfte Rezepte werden vor erneutem Hinzufügen gezeigt und nicht still dupliziert.
- Mealie bleibt für die Zusammenfassung kompatibler Zutaten, Mengenanzeige und Einkaufshäkchen verantwortlich. Vorhandene manuelle oder bereits abgehakte Artikel werden nicht durch ein „Liste neu aufbauen“ gelöscht. Es gibt **keinen automatischen Dauerabgleich** zwischen Plan und Liste; Änderungen werden bei der nächsten ausdrücklichen Einkaufsaktion mit Mealies vorhandenen Rezeptbezügen besprochen.
- Der MCP bietet korrekte Listen- und Artikeloperationen, einschließlich Anlegen/Lesen/Bearbeiten/Abhaken/Löschen sowie Rezeptbezüge hinzufügen/entfernen. Der bereits dokumentierte undokumentierte `shoppingListId`-GET-Filter und die fehlerhafte Auswertung von `createdItems` im Fork sind zu korrigieren.

### Organisation und Identität

- Kochbücher und Tags werden über die Mealie-API lesbar und bearbeitbar. „Zuletzt gekocht“ wird erst nach einer Bestätigung im Chat über Mealies `last-made`-Endpunkt gesetzt; es gibt keinen Scheduler und keine Signal-Erinnerung.
- Der vorhandene PocketID/OAuth-Zugang zum MCP bleibt; dahinter wird Mealie vorerst mit einem gemeinsamen Backend-Konto bedient. Persönliche Favoriten/Bewertungen und Haushaltsadministration (Mitglieder, Einladungen, Rechte, Präferenzen) sind nicht Teil dieser Ausbaustufe. Der MCP führt keine Unverträglichkeitsprüfung und keine Vorratsverwaltung durch.
- Vor einer Löschung wird das konkret aufgelöste Objekt samt Folgen angezeigt und die ausdrückliche Bestätigung eingeholt. Destruktive Mealie-API-Routen werden nicht als vermeintlich harmlose Lesefunktionen beschrieben.

## Begrenzte BLS-Ergänzung

Der Nutzer möchte automatische Nährwerte **im MCP**. Das bleibt die bewusst gewählte Ausnahme vom schmalen Adapter:

1. Bei der Neuanlage und später auf Nachfrage werden die strukturierten Zutaten gegen den lokal vorliegenden deutschen [Bundeslebensmittelschlüssel 4.0](https://blsdb.de/download) geprüft. Dessen Daten sind unter CC BY 4.0 verfügbar; die Namensnennung des Max Rubner-Instituts ist einzuplanen.
2. Uneindeutige Lebensmittel werden als Auswahl gezeigt. Für Stück- und Volumenangaben sind sichtbare, korrigierbare Standardgewichte als **Schätzung** zulässig. Fehlende Zuordnungen dürfen nicht als vollständig berechnete Rezeptsumme ausgegeben werden.
3. Ein BLS-Fehler blockiert die Rezeptanlage nicht. Das Rezept wird mit seinen strukturierten Zutaten gespeichert; fehlende Nährwerte werden benannt. Ein späterer Neuberechnungsvorschlag ersetzt gespeicherte Werte erst nach Bestätigung.
4. Die BLS-Ergänzung führt keinen eigenen Rezeptbestand, keine Hintergrund-Synchronisation und keinen automatischen Rechenlauf bei jeder Rezeptänderung. Mealie speichert [Nährwerte statisch](https://mealie.io/documentation/getting-started/faq/#how-do-i-enable-nutritional-values); die Ausgabe muss Bezug auf Grundportionen und mögliche Schätzungen deutlich machen.

Eine detaillierte BLS-Zuordnung und das Datenformat sind eine eigene, nachgelagerte technische Untersuchung. Eine externe Datenquelle ist prinzipiell erlaubt, BLS lokal wird zuerst geprüft.

## Einmalige Korrektur vorhandener Rezepte

Der gesamte Rezeptbestand wird zunächst **nur gelesen** und auf Textzutaten geprüft. Eine Vorschau zeigt Rezept, ursprüngliche Zeile, vorgeschlagene Menge, Food und Unit. Für Bereiche wie `400–500 g` gilt der Mittelwert (`450 g`); bei unteilbaren Stückzutaten wird der Mittelwert aufgerundet. Erst eine geprüfte Freigabe schreibt Änderungen. Originaltext und getroffene Umwandlung sollen nachvollziehbar bleiben. Das ist ein einmaliger Migrationsablauf, kein dauerhaftes MCP-Werkzeug und kein stiller Automatismus. Mealies bestehende Parser-Oberfläche bleibt eine Alternative für Einzelfälle.

## Kleine PRs und Nachweise

| Reihenfolge | Ergebnis | Abnahme anhand von Mealie-Verhalten |
| --- | --- | --- |
| 1. Bestehender Entwurfs-PR #1 | Strukturierte Zutaten und numerische Grundportionen; vorhandenen Food-/Unit-Autocreate mit der gewählten Treffer-Vorschau abgleichen. | Ein Testrezept mit exakten Mengen lässt sich in Mealie von 3 auf 4 Portionen anzeigen; unklare Mengen werden vor dem Speichern geklärt. Bestehende Rezepte bleiben bis zur Migration unangetastet. |
| 2. Einkaufs-API korrigieren | Dokumentierten Listen-Detail-Endpunkt und Collection-Antwort `createdItems` korrekt verarbeiten; native Artikel- und Rezeptbeitrags-Operationen anbieten. | Liste, Artikel, Häkchen und Rezeptverknüpfungen werden ohne fremde Listenartikel oder doppelten POST nach Antwortfehler bedient. |
| 3. Wochenplan vervollständigen | Alle sieben Typen, Freitext und In-place-Update; korrekt paginierte Abfrage. | Ein Wochenbereich mit Rezept- und Freitextterminen ist vollständig les- und bearbeitbar. Assistent kann die nativen Einkaufstools danach kombinieren, ohne eigene Synchronisationsdaten. |
| 4. Rezeptpflege und Organisation | Quelle, Zeiten, Bildoperationen, explizite Nährwertfelder; Importwege; Kochbuch- und Tag-Pflege. | Mealie liest die gespeicherten Felder korrekt zurück; importierte Zutaten werden auf Struktur geprüft. |
| 5. BLS-Zusatz | Optionale Berechnung bei Neuanlage und auf Nachfrage, mit sichtbarer Quellen-/Schätzangabe und Bestätigung vor Überschreiben. | Eindeutiger, uneindeutiger und fehlender Food-Treffer werden getrennt behandelt; ein BLS-Ausfall verhindert kein Rezept. |
| 6. Einmalige Migration | Vorschau aller betroffenen Rezepte, bestätigte Umwandlung und nachvollziehbarer Änderungsbericht. | Keine Schreibänderung ohne Freigabe; Bereiche und Stückrundung entsprechen den vereinbarten Regeln; bestehende Bilder/Schritte bleiben erhalten. |

Die Reihenfolge ist eine Arbeitsplanung, keine Aussage, dass alle Schritte schon implementiert sind. PR #1 ist ein Entwurf und enthält derzeit **nicht** die später vereinbarte Vorschau für ähnliche Foods/Units. Auch die Einkaufsfehler sind dort nur analysiert, noch nicht behoben.

## Noch offen vor echten Integrationstests

Die gelieferte OpenAPI meldet `nightly`; die Version der laufenden Mealie-Instanz und ihre tatsächlichen Antwortformen müssen vor dem Rollout geprüft werden. Auf die Frage nach einem Testort kam keine Auswahl. Bis dieser Punkt geklärt ist, werden keine schreibenden Live-Tests auf der Mealie-Instanz angenommen oder ausgeführt. Mock-Tests allein belegen die Live-Kompatibilität nicht.
