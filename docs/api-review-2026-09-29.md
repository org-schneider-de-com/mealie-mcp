# Mealie API and MCP review — 29 September 2026

## Basis

- The supplied `openapi.json` identifies itself as Mealie `nightly` and contains
  182 paths, 266 HTTP operations, and 259 schemas. It is an API description,
  not proof of the version running on the user's server.
- The bundled v3.28.0 spec in `better-mealie-mcp` has the same 266
  method/path combinations as the supplied nightly spec. This comparison does
  not establish that every request and response schema is identical.
- The three supplied exports are full Mealie recipe exports. The two recipes
  written through this MCP have `recipe_servings: 3` but all 25 ingredient rows
  combined have `quantity: 0`, `unit: null`, and `food: null`. Their ingredient
  text appears in `note` and `display`. The manually authored example has
  `recipe_servings: 5`, six numbered ingredients with resolved foods and units,
  and a `original.webp` file in its ZIP.
- Primary source for the scaling behavior: [Mealie's FAQ on foods, units and
  scaling](https://mealie.io/documentation/getting-started/faq/#how-do-i-enable-smart-ingredient-handling).

## Findings in the fork

| Priority | Finding | Evidence and impact | Status in this change |
| --- | --- | --- | --- |
| P0 | Ingredient text was always saved as a note. | `_ingredient_from_line` returned only `{"note": line}`. Quantities did not scale and ingredients could not be combined in shopping lists. | Text now uses `POST /api/parser/ingredients`; explicit `quantity`, `unit`, `food`, and `note` objects are accepted. Unresolved numbered text fails visibly. |
| P0 | A count of portions was also copied into free text `recipeYield`. | Both MCP exports have `recipe_servings: 3` **and** `recipe_yield: "3 Portionen"`. The numeric servings were already saved correctly; the text label could stay at 3 when scaling to 4. | New numeric portion labels are stored as `recipeServings` and cleared from `recipeYield`; updating `recipeServings` clears an old numeric portion label. |
| P0 | New installs could select incompatible MCP SDK 2.x. | `mcp[cli]>=1.2.0` installed v2, which removed `mcp.server.fastmcp`. | Dependency pinned to `<2`; installation and tests verified with v1.30.0. |
| P1 | Existing note-only recipes cannot be silently converted without a quantity decision. | Examples include `400-500 g Nudeln`, `500-600 g Hähnchenbrust`, `100-150 ml Brühe`. A range needs a chosen number for deterministic scaling. | Ranges are rejected on new writes; existing recipes must be explicitly edited. |
| P1 | Shopping-list items are written only as free text. | `add_shopping_list_item` sends `note`, `isFood: false`, and `checked`; API also accepts `quantity`, `unit`, `food`, and food/unit IDs. | Open. |
| P1 | Recipe fields are a small subset of the API model. | Create/update omit `orgURL`, `recipeYieldQuantity`, `performTime`, `nutrition`, `settings`, and `extras`. | Open. |
| P1 | Partial edits use a full GET → merged PUT. | This preserves present fields but can overwrite changes made between the read and write. Mealie also offers PATCH for changed fields. | Open; ingredient array replacement still needs careful handling. |
| P2 | Other practical routes are not surfaced. | HTML/JSON import, recipe-to-shopping-list, exports, assets, duplicate recipe, last-made, and organizer/food/unit administration. | Open; read-only `list_units` and parser preview were added. |

Image upload from URL and base64 was already present in the fork. Image handling
is a separate call after recipe creation. The manual recipe's `original.webp`
shows the export includes media; the two MCP exports do not.

## Family planning comparison

The daily workflow is broader than recipe creation: find dishes, plan a week,
adapt servings, collect groceries, shop together, and reuse favourites. The
matrix checks **callable MCP tools**, not just features in Mealie's UI. `Yes`
means a direct tool or straightforward combination of tools exists; `Partly`
means a material field or step is missing; `Raw` means the OpenAPI-generated
server exposes the route but leaves the workflow to the agent. None of these
servers was tested against the user's live installation.

| Family task | Current fork after this PR | counterbeing TS | cometto2007 | better-mealie-mcp |
| --- | --- | --- | --- | --- |
| Find dishes by name and tags | Yes: search and tag filter | Partly: paginated list, no search input in `list_recipes` | Yes: text search | Raw: recipe search/filter and suggestions |
| Create a complete family recipe | Yes: name, steps, notes, tags, categories, tools, servings; picture separately | Partly: name, steps, text parsing and picture separately; no `recipeServings` input | Partly: create shell then update in another call | Raw: create then update; import routes |
| Scale from 3 to 5 people | Yes for exact structured amounts and numeric `recipeServings`; parser dependent for text | Partly: parses amounts, but create/update input lacks numeric `recipeServings` | Yes with explicit foods/units and `recipe_servings` on update; multiple calls | Raw: fields and parser routes exist |
| Import from URL or pasted recipe | URL import; no HTML/JSON tool | URL and HTML/JSON tools | URL import | Raw: URL, HTML/JSON, ZIP and AI routes |
| Plan and inspect the week | Yes: date range, today, add, delete | Yes: date range, today, add, delete | Partly: date range tool sends `startDate`/`endDate`, while supplied OpenAPI requires `start_date`/`end_date`; today/add/delete exist | Raw: list, today, create, edit and delete |
| Snack, drink and dessert slots | Partly: tool restricts type to breakfast/lunch/dinner/side; API has 7 types | Yes: all 7 types in schema | Yes: unrestricted string input | Raw: all 7 types |
| Edit an entry, recurring rules, random meals | No direct tools; delete and recreate an entry | No | No | Raw: PUT entry, meal-plan rules and random endpoint |
| Create and use shopping lists | Partly: create/list, free-text add and tick; `list_shopping_list_items` uses an undocumented filter and may include items from other lists; cannot rename/delete list or edit item quantity | Partly: list/get and item edit/tick/delete, but no create-list tool; item creation parses the API's collection response as a single item and may fail after the write | Partly: create/get/delete list and add item; no item tick/edit/delete | Raw: full list and item CRUD plus bulk creation |
| Transfer recipe ingredients to a shopping list | No direct tool | Yes for one recipe at a time | No | Raw: single and bulk recipe-to-list routes |
| Make one shopping list from the weekly plan | No end-to-end tool | Agent must loop over plan entries and add recipes individually | No | Agent must compose plan lookup and bulk recipe-to-list call |
| Nutrition and household diet organisation | Read full recipe, tag/category support; no nutrition edit | Recipe read projection omits nutrition; no nutrition write; tags/categories can be created but not assigned by recipe tools | Nutrition update and full recipe read; no tag/category management tools | Raw: nutrition, tags, categories and settings |
| Reuse favourites, ratings and cookbooks | List/create cookbooks; no favourites/ratings tools | No favourite/cookbook tools; read rating | No | Raw: favourites, ratings and full cookbook CRUD |
| Family members and shared preferences | No member/invitation/preferences tools | Current user/group lookup only | No | Raw: household members, invitations, permissions and preferences |
| Recipe photos and attachments | Image by URL/base64; no other assets tool | Image by base64; no assets tool | No image/asset tool | Raw: image and asset routes |

**Important boundaries:** The Mealie `foods` catalog is a set of ingredient
names, not a pantry with stock levels and expiry dates. The supplied API has
recipe suggestions from a caller-provided list of available foods, but no
general stock-management routes. There is no dedicated allergen field in the
examined recipe schema; tags can express dietary choices, but they do not
automatically verify ingredients for allergies or lactose intolerance. Mealie's
[FAQ](https://mealie.io/documentation/getting-started/faq/#how-do-i-enable-nutritional-values)
also says nutritional values remain static when servings or yield change.
Recipe cooking times can guide a busy week, but the supplied API has no
dedicated price/budget, leftover, expiry-date, or pantry inventory model.
Those concerns can be written into meal-plan text or tags, without becoming
validated calculations.

The fork uses a single configured Mealie API token behind its PocketID/OAuth
protected MCP endpoint. Its callers therefore act as the same Mealie account;
PocketID login alone does not map each family member to a separate Mealie user.
The other servers also configure one Mealie token (or one login) for their
backend. Household UI membership and per-person MCP attribution need a
separate design if they matter.

### Practical choice

| Server | Scope and operational fit |
| --- | --- |
| [Current fork](https://github.com/org-schneider-de-com/mealie-mcp) | 27 original tools, 29 after this PR. Keeps the already configured PocketID/OAuth flow and provides a coherent recipe creation call. Its largest daily gap is the link between weekly plan and shopping list. |
| [counterbeing/mealie-mcp-ts](https://github.com/counterbeing/mealie-mcp-ts) | 27 tools. Useful reference for ingredient repair and recipe-to-list. Missing numeric servings and list creation prevent a complete family workflow without modifications. No equivalent PocketID/OAuth resource handling was found in its HTTP entry point. |
| [cometto2007/mealie-mcp-server](https://github.com/cometto2007/mealie-mcp-server) | 21 tools. Foods/units and nutrition are useful, but recipe creation takes two calls, shopping items cannot be checked off through tools, and its weekly date filter does not match the supplied API. No equivalent PocketID/OAuth resource handling was found. |
| [djwmarcx/better-mealie-mcp](https://github.com/djwmarcx/better-mealie-mcp) | OpenAPI generated against v3.28.0, 266 operations in its bundled spec. Best route coverage, but no curated weekly-plan-to-shopping workflow. The agent must sequence low-level calls and handle data shapes. Its README estimates ~61k tokens for all tools in slim mode; groups can be filtered. No equivalent PocketID/OAuth resource handling was found. |

For this household, continue the existing fork and fill workflow gaps in order:

1. **Weekly plan → shared shopping list:** select planned recipes and desired
   servings, call the API's bulk recipe-to-list route, preserve existing manual
   items, and return a reviewable list.
2. **Shopping list editing:** structured amount/food/unit, change quantities,
   check items, and create/rename lists with clear deduplication behaviour.
3. **Meal-plan editing and all seven meal types:** change an entry in place,
   then add optional recurring rules and random suggestions only if useful.
4. **Recipe reuse:** favourites, cookbooks, filtered searches and nutrition
   fields as requested. Check user-specific access before enabling invitations
   or other household administration through MCP.

This order follows the actual everyday chain from planning to groceries.
More endpoint coverage can be added selectively without exposing hundreds of
administrative operations to the agent.

See [the operation-level family function audit](family-function-audit-2026-09-29.md)
for every relevant step, exact tool names, and API route groups. Its more
specific findings supersede a broad `Yes` in the summary above.

## Verification and limits

- Unit tests use Mealie-shaped HTTP mock responses for parser output,
  food/unit resolution and recipe updates. No request was made to the user's
  live Mealie instance and no existing recipe was modified.
- The supplied OpenAPI is labeled nightly. Test against the deployed instance's
  `/openapi.json` and a disposable recipe before rolling out, especially if the
  deployed version is older than the supplied specification.
- Mealie's NLP parser quality depends on the language and populated food/unit
  catalog. Explicit structured ingredient objects remain the reliable path.
- Automatic migration of the two existing recipes requires decisions for their
  ingredient ranges and optional seasonings.
