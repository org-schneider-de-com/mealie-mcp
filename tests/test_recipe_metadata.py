"""Explicit recipe metadata survives full-resource updates."""

import json

import httpx
import pytest

from mealie_mcp.client import MealieClient
from mealie_mcp.server import _build_recipe_patch


def test_metadata_patch_contains_only_explicit_values():
    assert _build_recipe_patch(
        org_url="https://example.test/recipe",
        perform_time="PT20M",
        recipe_yield_quantity=2,
        nutrition={"calories": "300 kcal"},
    ) == {
        "orgURL": "https://example.test/recipe",
        "performTime": "PT20M",
        "recipeYieldQuantity": 2,
        "nutrition": {"calories": "300 kcal"},
    }
    assert "nutrition" not in _build_recipe_patch(ingredients=[])


@pytest.mark.asyncio
async def test_ingredient_edit_preserves_existing_nutrition_and_source():
    requests = []

    def handle(request):
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "name": "Reis",
                    "orgURL": "https://example.test/recipe",
                    "nutrition": {"calories": "300 kcal", "proteinContent": "10 g"},
                },
            )
        return httpx.Response(200, json={"slug": "reis"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.update_recipe("reis", {"recipeIngredient": []})
        await client.update_recipe("reis", {"nutrition": {"calories": "400 kcal"}})

    first = json.loads(requests[1].content)
    second = json.loads(requests[3].content)
    assert first["nutrition"] == {"calories": "300 kcal", "proteinContent": "10 g"}
    assert first["orgURL"] == "https://example.test/recipe"
    assert second["nutrition"] == {"calories": "400 kcal", "proteinContent": "10 g"}
