# Mealie: vollständige Funktionsprüfung für den Familienalltag

Stand: 29. September 2026. Verglichen wurden der bereitgestellte `openapi.json`-Export (`nightly`, 182 Pfade, 266 HTTP-Operationen), der Quellcode der vier genannten Repositories und drei Rezept-ZIP-Exporte. Die fünf Tabellen prüfen **60 einzelne Familienfunktionen**. **Statische Prüfung:** Es gab keine Verbindung zur Mealie-Instanz des Nutzers. Ein vorhandener MCP-Aufruf ist daher kein Nachweis eines erfolgreichen Ende-zu-Ende-Ablaufs. `better-mealie-mcp` generiert Werkzeuge aus einer eingebauten v3.28.0-OpenAPI mit denselben 266 Methoden/Pfad-Kombinationen; Gleichheit aller Schemata und Kompatibilität mit der laufenden Instanz sind offen.

## Leseschlüssel

| Zeichen | Bedeutung |
| --- | --- |
| ✓ | Direktes MCP-Werkzeug oder klarer, aus dem Code nachvollziehbarer Aufruf; nicht live verifiziert. |
| ~ | Nur Teilfelder, mehrere manuelle Aufrufe oder ein wesentliches Verhaltensrisiko. |
| ! | Konkreter Widerspruch zur gelieferten OpenAPI oder zur erwarteten Antwortform. |
| — | Kein entsprechendes MCP-Werkzeug; die API kann die Funktion trotzdem besitzen. |
| R | Rohes generiertes API-Werkzeug in `better-mealie-mcp`, sofern die passende Tag-Gruppe aktiviert ist. Kein zusammengesetzter Familienablauf. |

Spalten: **Fork** = `org-schneider-de-com/mealie-mcp` mit den Änderungen im Entwurfs-PR #1 (29 Werkzeuge); **TS** = `counterbeing/mealie-mcp-ts` (27); **Cometto** = `cometto2007/mealie-mcp-server` (21); **Better** = `djwmarcx/better-mealie-mcp` (266 OpenAPI-Operationen, abhängig von Tag-Filtern). Die Zahlen zählen Werkzeuge, nicht funktionierende Familienabläufe. Fehlende Werkzeugnamen in einer Zelle bedeuten ausdrücklich keine versteckte Implementierung.

## A. Rezepte finden, anlegen und verlässlich skalieren

API-Basis: `GET/POST /api/recipes`, `GET/PUT/PATCH/DELETE /api/recipes/{slug}`, `POST /api/parser/ingredients`, `GET/POST /api/foods`, `GET/POST /api/units` sowie die genannten Spezialrouten.

| Notwendige Funktion | Fork | TS | Cometto | Better |
| --- | --- | --- | --- | --- |
| Rezeptliste mit Pagination | ~ `search_recipes`, nur erste bis 100 Ergebnisse | ✓ `list_recipes` mit Seite | ✓ `get_all_recipes` | R |
| Freitextsuche nach Rezept | ✓ `search_recipes(query)` | — `list_recipes` hat kein Suchfeld | ✓ `search_recipes` | R |
| Filter nach Tags/Kategorien/Lebensmitteln/Zeit | ~ nur Tag-Slugs | — keine Rezeptfilter | — | R, API hat Kategorien, Tags, Tools, Foods; Zeit nur indirekt/Query-Filter prüfen |
| Vollständiges Rezept lesen | ✓ `get_recipe` | ~ `get_recipe` gibt Projektion ohne Nährwerte aus | ✓ `get_recipe` | R |
| Neues Rezept mit Inhalt erstellen | ✓ `create_recipe`: Shell + PUT | ~ `create_recipe`: strukturierte Zutaten, aber ohne numerische Portionen, Tags/Kategorien | ~ `create_recipe` erstellt nur Namen; `update_recipe` nötig | R, Shell + Update durch Agenten |
| Name, Beschreibung, Zeiten, Schritte, Notizen pflegen | ~ Zeiten als Text, kein `performTime` | ~ reduzierte Felder | ~ Update hat Zeiten und Schritte, keine separaten Rezeptnotizen im Werkzeug | R |
| Zutaten in Menge/Einheit/Lebensmittel zerlegen | ~ neue strukturierte Eingabe und Mealie-Parser; Bereichsangaben werden abgelehnt | ✓ `create_recipe`/`update_recipe` parsen und lösen Foods/Units auf | ~ `parse_ingredients` plus `update_recipe` und Food/Unit-IDs | R, Parser und Rezept-Update separat |
| Bestehende Textzutaten nachträglich reparieren | ~ `get_recipe` + manuelles `update_recipe`; kein Reparaturwerkzeug | ~ `parse_recipe_ingredients` schreibt direkt; Bereichsangaben ohne Rückfrage riskant | ~ Parser + manuelles Update | R, manuelle Folge von Aufrufen |
| Numerische Rezeptportionen setzen | ✓ `recipe_servings` in Create/Update | — nur `recipeYield`-Text, kein `recipeServings`-Input | ✓ `update_recipe(recipe_servings)` nach Shell | R |
| Menge beim Anzeigen auf andere Personenzahl skalieren | ~ Mealie kann strukturierte Mengen anhand `recipeServings` skalieren; MCP hat kein eigenes Vorschauwerkzeug | ~ Zutaten strukturiert, Basisportionen nicht gezielt setzbar | ~ Portionen/Zutaten nach mehreren Aufrufen | R, API-Rezeptdaten; Skalierung in Mealie-Oberfläche |
| Portionen für einen konkreten Plan-Eintrag festhalten | — Plan-Create hat keinen Portionsfaktor | — | — | —, die gelieferte `CreatePlanEntry`-Struktur hat kein Portionsfeld |
| Lebensmittel/Einheiten suchen und anlegen | ~ `list_foods`, `list_units`; Anlage intern beim Rezeptschreiben, keine direkten Create-Werkzeuge | ~ `list_foods`, `create_food`; Einheiten intern | ✓ `get_foods`, `get_units`, `create_food`, `create_unit` | R |
| Rezept aus URL importieren / vorher testen | ~ `import_recipe_from_url`; kein Test-Scrape | ✓ `test_scrape_url`, `create_recipe_from_url` | ~ `import_recipe_url`, kein Vortest | R |
| HTML/JSON oder ZIP importieren | — | ~ HTML-Tool mit eigener JSON-LD-Ausweichlogik, kein ZIP-Tool | — | R |
| Rezeptbild hochladen/ersetzen/löschen | ~ URL/Base64 zu PUT; kein Löschen | ~ Base64-Upload, kein Löschen | — | R |
| Sonstige Anhänge zum Rezept | — | — | — | R: `/api/recipes/{slug}/assets` und `/assets/url` |
| Rezept duplizieren, exportieren, zuletzt gekocht | — | — | — | R: `/duplicate`, `/exports`, `/last-made` |
| Rezept löschen | ✓ `delete_recipe` | ✓ `delete_recipe` | ✓ `delete_recipe` | R |

**Exportbefund:** Die zwei über den Fork erzeugten Rezepte enthalten zusammen 25 Zutatenzeilen; alle haben `quantity: 0`, `unit: null`, `food: null`, während die Texte in `note`/`display` stehen. `recipe_servings` ist jeweils **3**; die Zahl wurde also gespeichert. Zusätzlich steht `recipe_yield: "3 Portionen"` als starrer Text. Das manuell angelegte Referenzrezept hat sechs strukturierte Zutaten, `recipe_servings: 5` und ein Bild. Der PR korrigiert die Neuerstellung mit exakten Mengen und entfernt einen numerischen Portions-Yield; er repariert bestehende Rezepte nicht automatisch. Bereiche wie `400–500 g` benötigen eine vom Nutzer gewählte Menge.

## B. Tages- und Wochenplanung

API-Basis: `/api/households/mealplans`, `/today`, `/{item_id}`, `/rules`, `/random` und `GET /api/recipes/suggestions`.

| Notwendige Funktion | Fork | TS | Cometto | Better |
| --- | --- | --- | --- | --- |
| Heutige Mahlzeiten lesen | ✓ `get_todays_meal_plan` | ~ `get_todays_meal_plan`, Datumslabel in UTC berechnet | ✓ `get_today_meal_plan` | R |
| Zeitraum/Woche mit Datumsgrenzen lesen | ✓ `list_meal_plan` mit `start_date/end_date`; nur bis 1000 | ✓ `list_meal_plans` mit korrekten Querynamen, aber ohne weitere Seiten | ! `get_meal_plans` sendet `startDate/endDate`; OpenAPI verlangt `start_date/end_date` | R |
| Termin mit Rezept anlegen | ✓ `create_meal_plan_entry` löst Slug zu ID auf | ✓ `create_meal_plan` mit Rezept-ID | ✓ `create_meal_plan` mit Rezept-ID | R |
| Termin als freier Text ohne Rezept | ✓ `title` | ✓ `title/text` | — verlangt Rezept-ID | R |
| Frühstück, Mittag, Abend, Beilage, Snack, Getränk, Dessert | ~ Fork-Typ erlaubt nur vier der sieben OpenAPI-Werte | ✓ alle sieben Typen im Schema | ~ freier String, Docstring nennt vier; API entscheidet | R |
| Plan-Eintrag mit Beschreibung/Notiz | — `text` nur im internen Client, nicht im MCP-Tool | ✓ `text` | — | R |
| Plan-Eintrag ändern statt löschen/neuanlegen | — | — | — | R: `PUT /api/households/mealplans/{item_id}` |
| Plan-Eintrag löschen | ✓ `delete_meal_plan_entry` | ✓ `delete_meal_plan` | ✓ `delete_meal_plan` | R |
| Wiederkehrende Planregeln verwalten | — | — | — | R: `/api/households/mealplans/rules` CRUD |
| Rezeptvorschläge aus vorhandenen Lebensmitteln | — | — | — | R: `GET /api/recipes/suggestions`; Foods müssen vom Aufrufer kommen |
| Zufälligen Plan-Eintrag erzeugen | — | — | — | R: `POST /api/households/mealplans/random` |

Die gelieferte Plan-API enthält **keinen Personen-/Portionsfaktor je Planeintrag**. Für einen wöchentlichen Einkauf muss die gewünschte Rezeptmenge daher separat beim Hinzufügen zur Einkaufsliste über `recipeIncrementQuantity` bestimmt werden. Die Bedeutung dieses Faktors sollte gegen die konkrete Mealie-Version getestet werden; weder die drei kuratierten Server noch Better erledigen die Abstimmung von Plan, Portionswunsch und Einkauf als eigenen Ablauf.

## C. Einkaufslisten erstellen, füllen und gemeinsam abhaken

API-Basis: `/api/households/shopping/lists`, `/lists/{item_id}`, `/lists/{item_id}/recipe`, `/lists/{item_id}/recipe/{recipe_id}`, `/api/households/shopping/items` und `/{item_id}`.

| Notwendige Funktion | Fork | TS | Cometto | Better |
| --- | --- | --- | --- | --- |
| Einkaufslisten auflisten | ✓ `list_shopping_lists`, bis 1000 | ✓ `list_shopping_lists` mit Seiten | ✓ `get_shopping_lists` | R |
| Liste erstellen | ✓ `create_shopping_list` | — | ✓ `create_shopping_list` | R |
| Eine Liste samt ihren Artikeln lesen | ! `list_shopping_list_items` nutzt `shoppingListId` als GET-Query; nicht im API-Vertrag, Ergebnis kann ungefiltert sein | ✓ `get_shopping_list` über Listen-ID und `listItems` | ✓ `get_shopping_list` über Listen-ID | R |
| Liste umbenennen/löschen | — / — | — / — | — / ✓ `delete_shopping_list` | R |
| Manuellen Artikel als Text hinzufügen | ~ `add_shopping_list_items`: schreibt, interpretiert `createdItems` aber nicht und meldet `id: null` | ! `add_shopping_list_item` parst Collection-Antwort als Einzelartikel; kann nach erfolgreichem POST fehlschlagen | ✓ `add_item_to_shopping_list` gibt API-Antwort unverändert zurück | R |
| Artikel mit Menge, Food und Unit hinzufügen | — nur Freitext | ! Schema erlaubt Menge/Unit/Food, aber dieselbe Antwortform ist defekt; Objekte nur mit `name` sind gesondert zu prüfen | ~ Menge + `unit` als String, kein Food; API-Modell erwartet strukturierte Unit oder `unitId` | R |
| Menge/Notiz eines Artikels ändern | — | ✓ `update_shopping_list_item` mit GET + PUT | — | R |
| Artikel abhaken/zurücksetzen | ✓ `check_off_shopping_item` mit GET + PUT | ✓ `update_shopping_list_item(checked)` | — | R |
| Artikel löschen | ✓ `delete_shopping_list_item` | ✓ `delete_shopping_list_item` | — | R |
| Zutaten eines Rezepts zur Liste hinzufügen | — | ✓ `add_recipe_to_shopping_list` mit `recipeIncrementQuantity` | — | R |
| Mehrere Rezepte in einem API-Aufruf hinzufügen | — | —, Agent muss einzelne Aufrufe wiederholen | — | R: `POST /lists/{item_id}/recipe` |
| Rezeptbezug/Mengenbeitrag aus Liste entfernen | — | — | — | R: `/recipe/{recipe_id}/delete` |
| Artikel in großer Zahl anlegen/ändern/löschen | — | — | — | R: `/items/create-bulk`, `PUT/DELETE /items` |
| Wocheneinkauf aus Plan + Portionswünschen | — | ~ Agent liest Plan und addiert Rezepte einzeln; keine Portionszuordnung pro Planeintrag | — | ~ Agent kombiniert Plan-GET mit Bulk-Rezept-POST; kein eigener Workflow |
| Listenlabels/Reihenfolge und Sortierung | — | — | — | R: Listen-Label-Einstellungen und Artikelfelder `labelId`, `position` |

**Konkreter API-Vertragsfehler im Fork:** `GET /api/households/shopping/items` bietet laut OpenAPI `queryFilter`, `page`, `perPage`, aber keinen `shoppingListId`-Queryparameter. Für die Artikel einer bestimmten Liste ist `GET /api/households/shopping/lists/{item_id}` mit `listItems` der naheliegende, dokumentierte Weg. Das Ausmaß des Fehlers hängt davon ab, ob Mealie unbekannte Parameter ignoriert; ohne Live-Test wird es als Risiko statt als nachgewiesenes Falschergebnis bezeichnet.

**Konkreter Antwortformfehler:** `POST /api/households/shopping/items` antwortet laut OpenAPI mit `ShoppingListItemsCollectionOut` (`createdItems`, `updatedItems`, `deletedItems`), nicht einem einzelnen Einkaufsartikel. Der Fork schreibt zwar, verliert aber die erzeugte ID in seiner Ausgabe. TS validiert die Collection als `shoppingListItemSchema`; dadurch kann ein erfolgreich angelegter Artikel dem Aufrufer als Fehler erscheinen und bei blindem Wiederholen dupliziert werden. Cometto gibt die rohe Collection zurück.

## D. Wiederfinden, Organisation und Austausch

| Notwendige Funktion (API) | Fork | TS | Cometto | Better |
| --- | --- | --- | --- | --- |
| Tags auflisten, bei Bedarf erstellen, Rezept zuordnen (`/organizers/tags`, Rezept-Update) | ✓ `list_tags`, `set_recipe_tags`, Create intern | ~ `list_tags`, `create_tag`; keine Tag-Zuordnung im Rezept-Input | — | R |
| Kategorien auflisten, erstellen, Rezept zuordnen (`/organizers/categories`) | ✓ `list_categories`, `set_recipe_categories`, Create intern | ~ `list_categories`, `create_category`; keine Zuordnung | — | R |
| Küchengeräte pflegen und Rezepten zuordnen (`/organizers/tools`) | ~ Liste und Zuordnung, Create intern | — | — | R |
| Foods/Units korrigieren, zusammenführen oder löschen (`/foods`, `/units`) | — als direkte Werkzeuge | — | ~ nur Anlegen/Lesen | R |
| Kochbücher auflisten, erstellen, öffnen, ändern, löschen (`/households/cookbooks`) | ~ `list_cookbooks`, `create_cookbook`; kein Detail/Update/Delete | — | — | R |
| Persönliche Favoriten setzen/entfernen/auflisten (`/users/{id}/favorites/{slug}`, `/users/self/favorites`) | — | — | — | R |
| Bewertungen setzen/lesen (`/users/{id}/ratings/{slug}`, `/users/self/ratings`) | — | ~ Rezeptprojektion zeigt vorhandene Bewertung, keine Bewertungswerkzeuge | — | R |
| Kommentare lesen/erstellen/ändern/löschen (`/comments`, `/recipes/{slug}/comments`) | ~ volle Rezeptantwort kann Kommentare enthalten, keine Kommentarwerkzeuge | — | — | R |
| Rezept per Freigabelink teilen/verwalten (`/shared/recipes`, `/recipes/shared/{token_id}`) | — | — | — | R |
| Rezeptlisten exportieren/als ZIP sichern (`/recipes/bulk-actions/export`, `/recipes/{slug}/exports`) | — | — | — | R |

Für Ernährung in der Familie wichtig: `get_recipe` im Fork und Cometto erlaubt Lesen von Rezept-Nährwerten, aber nur Cometto hat ein dediziertes `update_recipe`-Eingabefeld für Nährwerte. Der Fork kann Kategorien/Tags als Hinweise verwenden; solche Labels **validieren keine Allergene**. Die OpenAPI enthält Nährwertfelder, aber kein eigenes Inventar mit Vorräten, Ablaufdaten, Preisen oder Restemengen. Vorschläge nach Foods setzen eine extern geführte Liste vorhandener Zutaten voraus. Mealie hält Nährwerte bei Portionsänderung laut eigener FAQ statisch.

## E. Haushalt, Benutzer und Automatisierung

| Notwendige Funktion (API) | Fork | TS | Cometto | Better |
| --- | --- | --- | --- | --- |
| Angemeldetes Mealie-Konto/Haushalt ansehen (`/users/self`, `/households/self`) | — | ~ `get_current_user` | — | R |
| Mitglieder und Rechte lesen/setzen (`/households/members`, `/permissions`) | — | — | — | R |
| Haushaltspräferenzen lesen/ändern (`/households/preferences`) | — | — | — | R |
| Einladungen verwalten (`/households/invitations`) | — | — | — | R |
| Benachrichtigungen, Rezeptaktionen, Webhooks (`/households/events/notifications`, `/recipe-actions`, `/webhooks`) | — | — | — | R |
| Zeitstrahl/Ereignisse zu Rezepten (`/recipes/timeline/events`) | — | — | — | R |

Der Fork schützt seinen MCP-Zugang per PocketID/OAuth, verwendet für Mealie aber ein festes Backend-API-Token. Daher erscheinen alle Aufrufe gegenüber Mealie als **ein** Benutzer. Auch die anderen Implementierungen benutzen eine Server-Identität für Mealie. Mitgliederrechte, persönliche Favoriten, Bewertungen und Autoreninformationen sind bei einem gemeinsamen Token nicht zuverlässig pro Familienmitglied getrennt. Die rohen Benutzer- und Administrationsendpunkte von Better schaffen diese Zuordnung ebenfalls nicht von allein. Solche Verwaltungswerkzeuge sollten nur nach einem eigenen Identitäts- und Berechtigungskonzept freigegeben werden.

## Prioritäten für den bestehenden Fork

1. **P0: Einkaufslistenvertrag korrigieren.** Für eine Liste `GET /lists/{id}` statt ungestütztem `shoppingListId`-Filter verwenden; nach Artikel-POST `createdItems` auswerten. Mit API-geformten Antworten testen und doppelte Einträge bei Wiederholungen vermeiden.
2. **P0: Skalierung Ende zu Ende prüfen.** Auf einer Wegwerf-Rezeptkopie strukturierte Mengen, `recipeServings`, Anzeige für 3/4 Personen und Übernahme mit `recipeIncrementQuantity` testen. Bestehende Textzutaten nur mit bestätigten Einzelmengen umwandeln.
3. **P1: Wochenplan in Einkaufsliste überführen.** Zeitraum lesen, einzelne Rezept-IDs und gewünschte Mengen sammeln, doppelte Rezepte konsolidieren, Bulk-Rezept-Endpunkt nutzen, vorhandene manuelle Artikel bewahren und Ergebnis mit dem Nutzer prüfen. Die API speichert keine Portionszahl am Plan-Eintrag: sie muss im Ablauf abgefragt oder als eigene Zusatzinformation geführt werden.
4. **P1: Einkauf vollständig editierbar machen.** Strukturierte Foods/Units/Mengen, Artikeländerung/Löschen, Liste lesen/umbenennen/löschen, Rezeptbezüge entfernen und Einkaufslisten-Labels.
5. **P1: Plan vollständig editierbar machen.** Alle sieben `PlanEntryType`-Werte, Freitext, In-place-Update und Pagination; Regeln/Zufall/Suggestions als gezielte Ergänzungen.
6. **P2: Rezept- und Haushaltspflege.** Nährwerte/Quelle/Zubehör/Anhänge, Kochbuch-CRUD, Favoriten/Bewertungen/Kommentare und Exporte. Einladungen/Rechte erst mit dem gewählten Benutzerkonzept.

**Entscheidungshilfe:** Better hat die weiteste API-Oberfläche, liefert aber rohe Operationen und benötigt sorgfältige Authentifizierung, Rechtebegrenzung und Ablaufsteuerung. TS demonstriert Rezept-zu-Einkauf und strukturierte Zutaten, hat aber weder numerische Rezeptportionen noch Listenanlage und weist den belegten Artikel-Antwortfehler auf. Cometto bietet einige Rezeptfelder und Food/Unit-Verwaltung, aber der Datumsfilter ist API-widrig und die Einkaufsliste kaum bearbeitbar. Der bestehende Fork passt zur vorhandenen OAuth-Einbindung; seine konkreten P0-Einkaufsfehler und der fehlende Plan→Einkauf-Ablauf sind vor einer Aussage über Alltagstauglichkeit zu beheben.

## Prüfbarkeit und Grenzen

Quellen im Checkout: `upload/openapi.json`; `mealie-mcp/src/mealie_mcp/{server,client}.py`; `mealie-mcp-ts/src/{tools,types,api}.ts`; `mealie-mcp-server/src/tools/{recipes,mealplans,shopping,foods_units}.py`; `better-mealie-mcp/{MEALIE_VERSION,server.py,TOOLS.md}` sowie die drei ZIP-Exporte. Die Statusangaben beziehen sich auf diese konkreten Code-Stände. API-Schema und vorhandener Code belegen weder Live-Berechtigungen noch Laufzeitverhalten eines bestimmten Mealie-Releases. Besonders deutsche NLP-Zerlegung, Mengenbereiche, Antwortschemata und die v3.28.0/nightly-Unterschiede sind gegen die tatsächlich laufende Instanz zu prüfen.

Quellstände: Fork-Basis `53364d772aa9c6482855ec071127c5d90eb04a91` plus Entwurfs-PR #1; TS `6a3ab3be05836cac9bc0108a0101d61867a74931`; Cometto `4d2d384fa8041bdf2ae14a86e3bcd3fb2c4911d0`; Better `4d16206c843cf17154f49259b7608d901b4e3c56`.
