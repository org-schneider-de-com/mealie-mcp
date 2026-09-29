"""Pasted recipe import uses Mealie once and reports ingredient structure."""

import httpx
import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieClient, MealieError


@pytest.mark.asyncio
async def test_import_posts_data_then_fetches_full_recipe():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        if request.method == "POST":
            assert request.url.path == "/api/recipes/create/html-or-json"
            assert (
                request.read()
                == b'{"data":"<script>recipe</script>","includeTags":true,"includeCategories":true}'
            )
            return httpx.Response(201, json="recipe-slug")
        return httpx.Response(
            200,
            json={
                "slug": "recipe-slug",
                "recipeIngredient": [
                    {"quantity": 300, "food": {"id": "food"}, "unit": {"id": "unit"}},
                ],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        recipe = await client.import_recipe_from_html_or_json(
            "<script>recipe</script>", include_tags=True, include_categories=True
        )
    assert recipe["recipeIngredient"][0]["quantity"] == 300
    assert calls == [
        ("POST", "/api/recipes/create/html-or-json"),
        ("GET", "/api/recipes/recipe-slug"),
    ]


@pytest.mark.asyncio
async def test_import_failure_does_not_create_an_empty_shell():
    calls = []

    def handle(request):
        calls.append(request.url.path)
        return httpx.Response(422, json={"detail": "Invalid recipe data"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        with pytest.raises(MealieError, match="Invalid recipe data"):
            await client.import_recipe_from_html_or_json("invalid")
    assert calls == ["/api/recipes/create/html-or-json"]


def test_imported_note_only_ingredients_are_reported():
    warnings = server._unstructured_ingredients(
        {
            "recipeIngredient": [
                {"quantity": 0, "food": None, "note": "300 g Reis"},
                {"quantity": 100, "food": {"id": "food"}},
            ]
        }
    )
    assert warnings == [{"index": 0, "note": "300 g Reis"}]
