# Mealie API and MCP review — 29 September 2026

## Basis

- The supplied `openapi.json` identifies itself as Mealie `nightly` and contains
  182 paths, 266 HTTP operations, and 259 schemas. It is an API description,
  not proof of the version running on the user's server.
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

## Comparison with the requested servers

Counts are tool registrations observed in the checked-out default branches,
not a quality score or a count of Mealie API endpoints. A tool may call several
endpoints; a generated tool may expose only one endpoint.

| Server | Tools / API reach | Ingredient and recipe behavior | Remote access fit |
| --- | --- | --- | --- |
| [Current fork](https://github.com/org-schneider-de-com/mealie-mcp) | 27 original tools; 29 with the two inspection tools here | Previously note-only. This change parses text, accepts structured input and resolves foods/units. Good combined create workflow. | Streamable HTTP and existing PocketID/OAuth resource handling in the fork. |
| [counterbeing/mealie-mcp-ts](https://github.com/counterbeing/mealie-mcp-ts) | 27 registrations | Parses `originalText` during create/update, resolves or creates foods and units, offers `parse_recipe_ingredients` for existing recipes. Also offers recipe-to-shopping-list and HTML import. This has the strongest ready-made ingredient workflow of the alternatives. | Streamable HTTP; no equivalent PocketID/OAuth resource implementation found in its HTTP entry point. |
| [cometto2007/mealie-mcp-server](https://github.com/cometto2007/mealie-mcp-server) | 21 registrations | Exposes parser, foods and units; recipe update accepts explicit food/unit IDs and fetches full objects before PUT. Its `create_recipe` creates only a named shell, requiring another call for content. | Streamable HTTP; no equivalent PocketID/OAuth resource implementation found. |
| [djwmarcx/better-mealie-mcp](https://github.com/djwmarcx/better-mealie-mcp) | OpenAPI generated, targets Mealie v3.28.0; approximately 259 tools in its bundled spec | Most complete endpoint reach, including the parser, but each call exposes a raw API operation. An agent must orchestrate create, parsing, lookup and update correctly. | Streamable HTTP and group filters. No equivalent PocketID/OAuth resource implementation found. All tools together have substantial schema/context cost; its README estimates about 61k tokens in default slim mode. |

For this deployment, extending the existing fork is the smallest compatible
change. The TypeScript server is a useful implementation reference for ingredient
repair and shopping-list workflows. The OpenAPI generated server is a useful API
coverage reference, but raw endpoint coverage alone does not guarantee a
correct recipe workflow.

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
