"""Read-only preview of legacy note-only recipe ingredients."""

from __future__ import annotations

import json
import math
import re
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any

_AMOUNT = re.compile(
    r"^\s*(?:ca\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:(?:-|–|bis)\s*(\d+(?:[.,]\d+)?))?"
    r"\s*(?:(kg|g|ml|l|EL|TL)\b\s*)?(.+?)\s*$",
    re.IGNORECASE,
)


def read_recipe_export(path: Path) -> dict[str, Any]:
    """Load the JSON from one Mealie ZIP export without altering the archive."""
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".json")]
        if len(names) != 1:
            raise ValueError(f"Expected exactly one recipe JSON in {path}")
        return json.loads(archive.read(names[0]))


def preview_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    """Propose quantities while retaining original rows for review and traceability."""
    rows = recipe.get("recipeIngredient", recipe.get("recipe_ingredient", []))
    result: dict[str, Any] = {
        "slug": recipe.get("slug"),
        "changes": [],
        "skipped": [],
        "unchanged": [],
    }
    for index, row in enumerate(rows):
        if row.get("quantity") or row.get("food") or row.get("title"):
            result["unchanged"].append(index)
            continue
        source = (row.get("note") or row.get("display") or "").strip()
        match = _AMOUNT.fullmatch(source)
        if not match:
            result["skipped"].append(
                {
                    "index": index,
                    "source": source,
                    "reason": "No unambiguous numeric amount and food",
                }
            )
            continue
        lower, upper, unit, food = match.groups()
        lower_value = float(lower.replace(",", "."))
        upper_value = float(upper.replace(",", ".")) if upper else lower_value
        if upper_value < lower_value:
            result["skipped"].append(
                {"index": index, "source": source, "reason": "Reversed quantity range"}
            )
            continue
        quantity = (lower_value + upper_value) / 2
        if not unit and upper:
            quantity = math.ceil(quantity)
        result["changes"].append(
            {
                "index": index,
                "source": source,
                "original": row,
                "quantity": quantity,
                "unit_name": unit,
                "food_name": food,
            }
        )
    return result


async def preview_all_recipes(client: Any) -> list[dict[str, Any]]:
    """Read every page and recipe from Mealie; no mutation method is called."""
    report: list[dict[str, Any]] = []
    page = 1
    while True:
        listing = await client.search_recipes(page=page, per_page=100)
        for summary in listing.get("items", []):
            report.append(preview_recipe(await client.get_recipe(summary["slug"])))
        if page >= listing.get("totalPages", 1):
            return report
        page += 1


async def apply_selected_recipe(
    client: Any, slug: str, selections: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply explicitly reviewed rows after re-reading and checking their source."""
    if not selections:
        raise ValueError("No ingredient rows selected")
    current = await client.get_recipe(slug)
    rows = deepcopy(current["recipeIngredient"])
    if len({choice["index"] for choice in selections}) != len(selections):
        raise ValueError("Duplicate ingredient index")
    for choice in selections:
        index = choice["index"]
        if not isinstance(index, int) or not 0 <= index < len(rows):
            raise ValueError("Selected ingredient index is out of bounds")
        row = rows[index]
        if row.get("quantity") or row.get("food") or row.get("note") != choice["source"]:
            raise ValueError(f"Ingredient {index} changed since preview; scan again")
        if choice["quantity"] <= 0 or not choice.get("food_id") or not choice.get("food_name"):
            raise ValueError(f"Ingredient {index} needs a positive quantity and selected food")
        if bool(choice.get("unit_id")) != bool(choice.get("unit_name")):
            raise ValueError(f"Ingredient {index} needs both unit ID and name")
        row.update(
            {
                "quantity": choice["quantity"],
                "food": {"id": choice["food_id"], "name": choice["food_name"]},
                "unit": {"id": choice["unit_id"], "name": choice["unit_name"]}
                if choice.get("unit_id")
                else None,
                "originalText": choice["source"],
                "note": "",
            }
        )
        row.pop("display", None)
    return await client.update_recipe(slug, {"recipeIngredient": rows})
