"""Catalog lookup asks before creating near-duplicate foods or units."""

import httpx
import pytest

from mealie_mcp.client import MealieClient
from mealie_mcp.server import RecipeIngredientInput, _prepare_ingredients


@pytest.mark.asyncio
async def test_similar_food_suggested_without_creating_a_duplicate():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        return httpx.Response(200, json={"items": [{"id": "f1", "name": "Frischkäse"}]})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        with pytest.raises(ValueError, match="Frischkäse"):
            await _prepare_ingredients(
                client, [RecipeIngredientInput(quantity=200, food="Frischkase")]
            )

    assert calls == [("GET", "/api/foods")]


@pytest.mark.asyncio
async def test_explicitly_confirmed_new_food_is_created_once():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        if request.method == "GET":
            return httpx.Response(200, json={"items": [], "totalPages": 1})
        return httpx.Response(201, json={"id": "f2", "name": "Neue Zutat"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await _prepare_ingredients(
            client,
            [
                RecipeIngredientInput(quantity=2, food="Neue Zutat", create_missing=True),
                RecipeIngredientInput(quantity=1, food="Neue Zutat", create_missing=True),
            ],
        )

    assert [item["food"]["id"] for item in result] == ["f2", "f2"]
    assert calls == [("GET", "/api/foods"), ("POST", "/api/foods")]


@pytest.mark.asyncio
async def test_similar_food_requires_candidate_id_even_with_create_missing():
    calls = []

    def handle(request):
        calls.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, json={"items": [{"id": "f1", "name": "Frischkäse"}]})
        return httpx.Response(201, json={"id": "f2", "name": "Frischkase"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        ingredient = RecipeIngredientInput(quantity=200, food="Frischkase", create_missing=True)
        with pytest.raises(ValueError, match="Frischkäse"):
            await _prepare_ingredients(client, [ingredient])
        ingredient.confirmed_similar_ids = {"foods": ["f1"]}
        result = await _prepare_ingredients(client, [ingredient])

    assert result[0]["food"]["id"] == "f2"
    assert calls == ["GET", "GET", "POST"]
