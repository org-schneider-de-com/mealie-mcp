"""Contract checks for scalable Mealie ingredients and complete recipe updates."""

import httpx
import pytest

from mealie_mcp.client import MealieClient
from mealie_mcp.server import RecipeIngredientInput, _build_recipe_patch, _prepare_ingredients


@pytest.mark.asyncio
async def test_parsed_lines_have_amount_food_and_no_fixed_display():
    requests = []

    def handle(request):
        requests.append(request)
        assert request.url.path == "/api/parser/ingredients"
        return httpx.Response(
            200,
            json=[
                {
                    "input": "300 g Reis",
                    "ingredient": {
                        "quantity": 300,
                        "unit": {"id": "unit-id", "name": "g"},
                        "food": {"id": "food-id", "name": "Reis"},
                        "note": "",
                        "display": "300 g Reis",
                    },
                }
            ],
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        ingredients = await _prepare_ingredients(client, ["### Hauptgericht", "300 g Reis"])

    assert len(requests) == 1
    assert ingredients == [
        {"title": "Hauptgericht", "note": ""},
        {
            "quantity": 300,
            "unit": {"id": "unit-id", "name": "g"},
            "food": {"id": "food-id", "name": "Reis"},
            "note": "",
        },
    ]
    assert _build_recipe_patch(recipe_servings=3, ingredients=ingredients) == {
        "recipeServings": 3,
        "recipeIngredient": ingredients,
    }


def test_portion_label_is_recorded_as_numeric_servings():
    assert _build_recipe_patch(recipe_yield="3 Portionen") == {
        "recipeServings": 3,
        "recipeYield": "",
    }


@pytest.mark.asyncio
async def test_structured_ingredient_resolves_existing_unit_and_creates_food():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        if request.url.path == "/api/units":
            return httpx.Response(200, json={"items": [{"id": "u1", "name": "g"}]})
        if request.method == "GET":
            return httpx.Response(200, json={"items": []})
        return httpx.Response(201, json={"id": "f1", "name": "Frischkäse"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        ingredients = await _prepare_ingredients(
            client,
            [RecipeIngredientInput(quantity=200, unit="g", food="Frischkäse", create_missing=True)],
        )

    assert ingredients == [
        {
            "quantity": 200,
            "unit": {"id": "u1", "name": "g"},
            "food": {"id": "f1", "name": "Frischkäse"},
            "note": "",
        }
    ]
    assert calls == [("GET", "/api/units"), ("GET", "/api/foods"), ("POST", "/api/foods")]


@pytest.mark.asyncio
@pytest.mark.parametrize("line", ["400-500 g Nudeln", "400 bis 500 g Nudeln"])
async def test_range_rejected_before_any_api_write(line):
    class UnusedClient:
        async def parse_ingredients(self, lines):
            raise AssertionError("parser should not be called")

    with pytest.raises(ValueError, match="exact amount"):
        await _prepare_ingredients(UnusedClient(), [line])


@pytest.mark.asyncio
async def test_explicit_unit_must_not_be_lost_by_parser():
    class MissingUnitClient:
        async def parse_ingredients(self, lines):
            return [{"ingredient": {"quantity": 300, "food": {"id": "f1", "name": "Reis"}}}]

    with pytest.raises(ValueError, match="resolve the unit"):
        await _prepare_ingredients(MissingUnitClient(), ["300 g Reis"])


@pytest.mark.asyncio
async def test_update_keeps_existing_recipe_fields_and_clears_fixed_portion_label():
    payloads = []

    def handle(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "name": "Reispfanne",
                    "recipeYield": "3 Portionen",
                    "recipeServings": 3,
                    "image": "existing-image",
                    "recipeInstructions": [{"text": "Kochen"}],
                },
            )
        payloads.append(request.content)
        return httpx.Response(200, json={"slug": "reispfanne"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.update_recipe("reispfanne", {"recipeServings": 4})

    import json

    body = json.loads(payloads[0])
    assert body["recipeYield"] == ""
    assert body["recipeServings"] == 4
    assert body["image"] == "existing-image"
    assert body["recipeInstructions"] == [{"text": "Kochen"}]
