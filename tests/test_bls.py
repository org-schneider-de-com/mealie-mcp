"""BLS source, exact matching, assumptions, completeness and Mealie write guards."""

import httpx
import pytest

from mealie_mcp import bls, server
from mealie_mcp.client import MealieClient


def test_bls_exact_ambiguous_and_missing_matches():
    exact = bls.find_food("Hafer Flocken")
    assert exact["status"] == "unique"
    assert exact["candidates"] == [{"code": "C133000", "name": "Hafer Flocken"}]
    assert bls.find_food("C133000")["status"] == "unique"
    assert bls.find_food("Hafer")["status"] == "ambiguous"
    assert bls.find_food("Hafer")["candidates"]
    assert bls.find_food("unbekanntes fantasieprodukt")["candidates"] == []
    with pytest.raises(ValueError):
        bls.find_food(" ")
    assert "Max Rubner-Institut" in bls.SOURCE
    assert len(bls.load_bls()) == 7140


def test_two_portions_get_calculated_from_100g_without_densities():
    result = bls.calculate(
        [{"quantity": 200, "unit": {"abbreviation": "g"}, "food": {"name": "Hafer Flocken"}}],
        2,
    )
    assert result["complete"]
    assert result["totals"]["calories"] == {"amount": 696, "unit": "kcal"}
    assert result["perServing"]["calories"] == {"amount": 348, "unit": "kcal"}
    assert bls.mealie_nutrition(result)["calories"] == "348 kcal"


def test_missing_or_ambiguous_food_and_piece_weight_are_incomplete():
    ingredients = [
        {"quantity": 2, "unit": {"name": "Stück"}, "food": {"name": "Hafer Flocken"}},
        {"quantity": 100, "unit": {"name": "g"}, "food": {"name": "Hafer"}},
    ]
    incomplete = bls.calculate(ingredients, 2)
    assert not incomplete["complete"]
    assert "explicit gram" in incomplete["ingredients"][0]["assumption"]
    assert incomplete["ingredients"][1]["matchStatus"] == "ambiguous"
    with pytest.raises(ValueError, match="Incomplete"):
        bls.mealie_nutrition(incomplete)
    complete = bls.calculate(ingredients, 2, selections={1: "C131000"}, gram_weights={0: 80})
    assert complete["complete"]
    assert complete["ingredients"][0]["assumption"] == "explicit weight: 80 g"
    assert complete["ingredients"][1]["blsCode"] == "C131000"


@pytest.mark.parametrize(
    "servings,weights,selections",
    [
        (0, {}, {}),
        (float("inf"), {}, {}),
        (2, {0: -5}, {}),
        (2, {}, {0: "fake-code"}),
    ],
)
def test_implausible_servings_weights_or_code_rejected(servings, weights, selections):
    with pytest.raises(ValueError):
        bls.calculate(
            [{"quantity": 100, "unit": "g", "food": "Hafer Flocken"}],
            servings,
            gram_weights=weights,
            selections=selections,
        )


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")
    return {name: tool.fn for name, tool in server.build_server()._tool_manager._tools.items()}


@pytest.mark.asyncio
async def test_calculation_previews_before_saving_and_never_overwrites_silently(monkeypatch, tools):
    class Client:
        def __init__(self):
            self.patches = []

        async def get_recipe(self, _slug):
            return {
                "recipeServings": 2,
                "recipeIngredient": [{"quantity": 200, "unit": "g", "food": "Hafer Flocken"}],
                "nutrition": {"calories": "old"},
            }

        async def update_recipe(self, slug, patch, **kwargs):
            self.patches.append((slug, patch, kwargs))

    client = Client()
    monkeypatch.setattr(server, "_client", lambda _: client)
    preview = await tools["calculate_recipe_nutrition"](None, "porridge")
    assert preview["complete"] and not preview["saved"]
    with pytest.raises(ValueError, match="replace_existing"):
        await tools["calculate_recipe_nutrition"](None, "porridge", save=True)
    assert client.patches == []
    saved = await tools["calculate_recipe_nutrition"](
        None, "porridge", save=True, replace_existing=True
    )
    assert saved["saved"]
    assert client.patches[0][2] == {"replace_nutrition": True}


@pytest.mark.asyncio
async def test_incomplete_calculation_cannot_write(monkeypatch, tools):
    class Client:
        async def get_recipe(self, _slug):
            return {"recipeServings": 2, "recipeIngredient": [{"note": "1 Apfel"}]}

        async def update_recipe(self, *_args, **_kwargs):
            pytest.fail("Incomplete value must not reach Mealie")

    monkeypatch.setattr(server, "_client", lambda _: Client())
    with pytest.raises(ValueError, match="Incomplete"):
        await tools["calculate_recipe_nutrition"](None, "fruit", save=True)


@pytest.mark.asyncio
async def test_creation_survives_bls_failure(monkeypatch, tools):
    class Client:
        async def create_recipe(self, _name):
            return "reis"

        async def update_recipe(self, _slug, _patch):
            return {"slug": "reis"}

    monkeypatch.setattr(server, "_client", lambda _: Client())
    monkeypatch.setattr(bls, "load_bls", lambda: (_ for _ in ()).throw(OSError("data unavailable")))
    result = await tools["create_recipe"](
        None,
        "Reis",
        recipe_servings=2,
        calculate_bls_nutrition=True,
    )
    assert result["slug"] == "reis"
    assert not result["blsNutrition"]["complete"]


@pytest.mark.asyncio
async def test_creation_calculates_once_and_keeps_explicit_nutrition(monkeypatch, tools):
    class Client:
        def __init__(self):
            self.patches = []

        async def resolve_ingredient_entity(self, kind, name, **_kwargs):
            return {"id": kind, "name": name, "abbreviation": name}

        async def create_recipe(self, _name):
            return "porridge"

        async def update_recipe(self, _slug, patch):
            self.patches.append(patch)
            return {"slug": "porridge"}

    client = Client()
    monkeypatch.setattr(server, "_client", lambda _: client)
    ingredient = server.RecipeIngredientInput(quantity=200, unit="g", food="Hafer Flocken")
    result = await tools["create_recipe"](
        None,
        "Porridge",
        recipe_yield="2 Personen",
        ingredients=[ingredient],
        calculate_bls_nutrition=True,
    )
    assert result["blsNutrition"]["complete"]
    assert client.patches[0]["nutrition"]["calories"] == "348 kcal"
    assert client.patches[0]["recipeServings"] == 2

    await tools["create_recipe"](
        None,
        "Porridge",
        recipe_servings=2,
        ingredients=[ingredient],
        nutrition={"calories": "manual"},
        calculate_bls_nutrition=True,
    )
    assert client.patches[1]["nutrition"] == {"calories": "manual"}


@pytest.mark.asyncio
async def test_replacing_nutrition_removes_stale_fields():
    requests = []

    def handler(request):
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(
                200, json={"name": "Reis", "nutrition": {"cholesterolContent": "stale"}}
            )
        return httpx.Response(200, json={})

    client = MealieClient(
        "https://mealie.test",
        "token",
        client=httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url="https://mealie.test"
        ),
    )
    await client.update_recipe(
        "reis", {"nutrition": {"calories": "300 kcal"}}, replace_nutrition=True
    )
    assert b"stale" not in requests[-1].content
    assert b"300 kcal" in requests[-1].content
