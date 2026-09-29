"""Explicit BLS 4.0 lookup and conservative recipe nutrition calculation.

Source: Max Rubner-Institut (2025), Bundeslebensmittelschlüssel 4.0,
DOI 10.25826/Data20251217-134202-0, CC BY 4.0. Values are per 100 g.
"""

from __future__ import annotations

import gzip
import json
import math
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

SOURCE = (
    "Max Rubner-Institut, Bundeslebensmittelschlüssel 4.0 (2025), "
    "DOI 10.25826/Data20251217-134202-0, CC BY 4.0"
)
FIELDS = (
    "calories",
    "proteinContent",
    "fatContent",
    "carbohydrateContent",
    "fiberContent",
    "sugarContent",
    "sodiumContent",
)
UNITS = ("kcal", "g", "g", "g", "g", "g", "mg")


def _normal(name: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", name).casefold().split())


@lru_cache(maxsize=1)
def load_bls() -> list[list[Any]]:
    """Load the slim, attributed data snapshot shipped with the package."""
    path = Path(__file__).parent / "data" / "bls_4_0_2025_de.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as data:
        return json.load(data)


def find_food(name: str, *, limit: int = 10) -> dict[str, Any]:
    """Only an exact name or code is safe to select without human input."""
    query = _normal(name)
    if not query:
        raise ValueError("Provide a BLS code or food name")
    rows = load_bls()
    matches = [row for row in rows if query in (_normal(row[0]), _normal(row[1]))]
    candidates = matches or [row for row in rows if query in _normal(row[1])][:limit]
    return {
        "status": (
            "unique" if len(matches) == 1
            else "ambiguous" if len(candidates) > 1
            else "missing"
        ),
        "candidates": [{"code": row[0], "name": row[1]} for row in candidates[:limit]],
        "source": SOURCE,
    }


def _grams(row: dict[str, Any], override: float | None) -> tuple[float | None, str | None]:
    quantity = row.get("quantity")
    if not isinstance(quantity, (float, int)) or not math.isfinite(quantity) or quantity <= 0:
        return None, "missing positive quantity"
    if override is not None:
        if not math.isfinite(override) or override <= 0:
            raise ValueError("Gram weight must be positive and finite")
        return override, f"explicit weight: {override:g} g"
    unit = row.get("unit") or {}
    if isinstance(unit, dict):
        unit = unit.get("abbreviation") or unit.get("name") or ""
    unit = _normal(str(unit))
    if unit in ("g", "gramm", "gram"):
        return float(quantity), None
    if unit in ("kg", "kilogramm", "kilogram"):
        return float(quantity) * 1000, None
    return None, f"unit '{unit or 'piece/unspecified'}' needs an explicit gram weight"


def calculate(
    ingredients: list[dict[str, Any]],
    servings: float,
    *,
    selections: dict[int, str] | None = None,
    gram_weights: dict[int, float] | None = None,
) -> dict[str, Any]:
    """Calculate only complete, explicitly weighted rows; never infer density."""
    if not isinstance(servings, (float, int)) or not math.isfinite(servings) or servings <= 0:
        raise ValueError("Numeric recipe servings must be positive and finite")
    selections = selections or {}
    gram_weights = gram_weights or {}
    rows = load_bls()
    by_code = {row[0]: row for row in rows}
    totals = [0.0] * len(FIELDS)
    details = []
    complete = True
    for index, ingredient in enumerate(ingredients):
        if ingredient.get("title"):
            continue
        food = ingredient.get("food") or {}
        name = food.get("name", "") if isinstance(food, dict) else str(food)
        lookup = find_food(name) if name else {"status": "missing", "candidates": []}
        code = selections.get(index)
        if code and code not in by_code:
            raise ValueError(f"Unknown BLS code {code} for ingredient {index}")
        chosen = (
            by_code.get(code)
            if code
            else (
                by_code[lookup["candidates"][0]["code"]] if lookup["status"] == "unique" else None
            )
        )
        grams, assumption = _grams(ingredient, gram_weights.get(index))
        status = (
            "matched"
            if chosen and grams and all(isinstance(v, (float, int)) for v in chosen[2:])
            else "incomplete"
        )
        if status == "matched":
            totals = [
                total + value * grams / 100 for total, value in zip(totals, chosen[2:], strict=True)
            ]
        else:
            complete = False
        details.append(
            {
                "index": index,
                "food": name,
                "status": status,
                "matchStatus": "selected" if code else lookup["status"],
                "candidates": lookup["candidates"],
                "blsCode": chosen[0] if chosen else None,
                "grams": grams,
                "assumption": assumption,
            }
        )
    if not details:
        complete = False
    return {
        "complete": complete,
        "servings": servings,
        "ingredients": details,
        "totals": {
            field: {"amount": round(amount, 2), "unit": unit}
            for field, amount, unit in zip(FIELDS, totals, UNITS, strict=True)
        },
        "perServing": {
            field: {"amount": round(amount / servings, 2), "unit": unit}
            for field, amount, unit in zip(FIELDS, totals, UNITS, strict=True)
        },
        "source": SOURCE,
    }


def mealie_nutrition(result: dict[str, Any]) -> dict[str, str]:
    if not result["complete"]:
        raise ValueError("Incomplete BLS calculation cannot be saved")
    return {
        field: f"{value['amount']:g} {value['unit']}"
        for field, value in result["perServing"].items()
    }
