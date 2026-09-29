# One-time ingredient migration

The scanner reads recipes and writes a local JSON preview. It never changes Mealie.

```bash
PYTHONPATH=src python scripts/preview_ingredient_migration.py exports/*.zip --output preview.json
# Or, with MEALIE_URL and MEALIE_API_TOKEN in the environment:
PYTHONPATH=src python scripts/preview_ingredient_migration.py --live --output preview.json
```

Review each `changes` row. The source text, index, proposed quantity, unit and
food name are included. `skipped` rows require manual decisions. A quantity
range uses its midpoint; a range of pieces rounds upward. The original note is
retained in `originalText` after an approved change. No food or unit is created
by this migration.

Only after separate approval, prepare a JSON manifest of **selected** rows with
verified existing Mealie food and unit IDs. For example:

```json
{
  "recipe-slug": [{
    "index": 0,
    "source": "400-500 g Nudeln",
    "quantity": 450,
    "food_id": "existing-food-id",
    "food_name": "Nudeln",
    "unit_id": "existing-unit-id",
    "unit_name": "g"
  }]
}
```

For an ingredient without a unit, omit both unit fields. The apply script
re-reads every selected recipe, checks the original note and structured state,
then updates only selected ingredient rows using the client's full-resource
GET/PUT. It reports successful recipes and skipped errors separately. Images,
steps and unselected rows remain part of the fetched recipe body. Run it only
on the approved live instance after reviewing the preview and manifest:

```bash
PYTHONPATH=src python scripts/apply_ingredient_migration.py \
  --approved-manifest selected.json --report result.json --apply
```

This is a one-time operator command, not a persistent MCP tool. A concurrent
recipe edit between GET and PUT is a remaining API limitation; schedule the
approved run while recipe edits are paused and review the result report.
