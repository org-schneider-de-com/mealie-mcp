"""Contract tests for Mealies native recipe shopping-list operations."""

import json

import httpx
import pytest

from mealie_mcp.client import MealieClient
from mealie_mcp.server import _check_recipe_addition, _positive_factor


def test_existing_recipe_requires_explicit_confirmation_before_addition():
    refs = [{"recipeId": "r1", "recipeQuantity": 1}]
    with pytest.raises(ValueError, match="already linked"):
        _check_recipe_addition(refs, ["r1"], allow_existing=False)
    _check_recipe_addition(refs, ["r1"], allow_existing=True)


def test_duplicate_bulk_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        _check_recipe_addition([], ["r1", "r1"], allow_existing=False)


@pytest.mark.parametrize("factor", [0, -1, float("nan"), float("inf")])
def test_recipe_quantity_factor_must_be_positive_and_finite(factor):
    with pytest.raises(ValueError, match="positive and finite"):
        _positive_factor(factor)


@pytest.mark.asyncio
async def test_read_references_and_add_single_recipe_with_factor():
    calls = []

    def handle(request):
        calls.append(
            (
                request.method,
                request.url.path,
                json.loads(request.content) if request.content else None,
            )
        )
        if request.method == "GET":
            return httpx.Response(200, json={"id": "list-a", "recipeReferences": []})
        return httpx.Response(
            200,
            json={
                "id": "list-a",
                "recipeReferences": [{"recipeId": "r1", "recipeQuantity": 4 / 3}],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        assert await client.list_shopping_recipe_references("list-a") == []
        result = await client.add_recipe_to_shopping_list("list-a", "r1", factor=4 / 3)

    assert result["recipeReferences"][0]["recipeQuantity"] == 4 / 3
    assert calls == [
        ("GET", "/api/households/shopping/lists/list-a", None),
        (
            "POST",
            "/api/households/shopping/lists/list-a/recipe/r1",
            {"recipeIncrementQuantity": 4 / 3},
        ),
    ]


@pytest.mark.asyncio
async def test_bulk_add_and_remove_use_mealie_endpoints():
    calls = []

    def handle(request):
        calls.append((request.url.path, json.loads(request.content)))
        return httpx.Response(200, json={"id": "list-a", "listItems": [{"id": "manual"}]})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.add_recipes_to_shopping_list(
            "list-a", [{"recipeId": "r1", "recipeIncrementQuantity": 2}]
        )
        result = await client.remove_recipe_from_shopping_list("list-a", "r1", factor=2)

    assert result["listItems"] == [{"id": "manual"}]
    assert calls == [
        (
            "/api/households/shopping/lists/list-a/recipe",
            [{"recipeId": "r1", "recipeIncrementQuantity": 2}],
        ),
        ("/api/households/shopping/lists/list-a/recipe/r1/delete", {"recipeDecrementQuantity": 2}),
    ]
