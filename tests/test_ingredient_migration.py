"""Migration preview never writes and preserves ambiguous source text."""

import json
import zipfile

import pytest

from mealie_mcp.migration import (
    apply_selected_recipe,
    preview_all_recipes,
    preview_recipe,
    read_recipe_export,
)


def test_ranges_get_midpoint_and_piece_counts_round_up():
    recipe = {
        "slug": "test",
        "recipeIngredient": [
            {"quantity": 0, "food": None, "note": "400-500 g Nudeln"},
            {"quantity": 0, "food": None, "note": "2-3 Paprika"},
            {"quantity": 0, "food": None, "note": "ca. 300 g TK-Erbsen"},
            {"quantity": 300, "food": {"name": "Reis"}, "note": ""},
        ],
    }
    preview = preview_recipe(recipe)
    assert preview["changes"][0]["quantity"] == 450
    assert preview["changes"][0]["unit_name"] == "g"
    assert preview["changes"][0]["food_name"] == "Nudeln"
    assert preview["changes"][1]["quantity"] == 3
    assert preview["changes"][1]["source"] == "2-3 Paprika"
    assert preview["changes"][2]["quantity"] == 300
    assert preview["unchanged"] == [3]


def test_zip_export_can_be_scanned_without_rewriting_it(tmp_path):
    path = tmp_path / "recipe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "recipe.json",
            json.dumps(
                {
                    "slug": "test",
                    "recipe_ingredient": [
                        {"quantity": 0, "food": None, "note": "300 g Reis"},
                    ],
                }
            ),
        )
    before = path.read_bytes()
    result = preview_recipe(read_recipe_export(path))
    assert result["changes"][0]["quantity"] == 300
    assert path.read_bytes() == before


@pytest.mark.asyncio
async def test_live_scan_pages_through_every_recipe_without_writing():
    class ReadOnlyClient:
        def __init__(self):
            self.pages = []

        async def search_recipes(self, *, page, per_page):
            self.pages.append(page)
            return {"items": [{"slug": f"recipe-{page}"}], "totalPages": 2}

        async def get_recipe(self, slug):
            return {
                "slug": slug,
                "recipeIngredient": [
                    {"quantity": 0, "food": None, "note": "300 g Reis"},
                ],
            }

    client = ReadOnlyClient()
    report = await preview_all_recipes(client)
    assert client.pages == [1, 2]
    assert [r["slug"] for r in report] == ["recipe-1", "recipe-2"]


@pytest.mark.asyncio
async def test_selected_update_preserves_recipe_fields_and_other_rows():
    class FakeClient:
        def __init__(self):
            self.patch = None

        async def get_recipe(self, _slug):
            return {
                "slug": "test",
                "image": "picture",
                "recipeInstructions": [{"text": "Kochen"}],
                "recipeIngredient": [
                    {"quantity": 0, "food": None, "note": "400-500 g Nudeln"},
                    {"quantity": 2, "food": {"id": "f2"}, "note": ""},
                ],
            }

        async def update_recipe(self, _slug, patch):
            self.patch = patch
            return {"slug": "test"}

    client = FakeClient()
    await apply_selected_recipe(
        client,
        "test",
        [
            {
                "index": 0,
                "source": "400-500 g Nudeln",
                "quantity": 450,
                "food_id": "food-a",
                "food_name": "Nudeln",
                "unit_id": "unit-g",
                "unit_name": "g",
            }
        ],
    )
    assert client.patch["recipeIngredient"][0]["quantity"] == 450
    assert client.patch["recipeIngredient"][0]["originalText"] == "400-500 g Nudeln"
    assert client.patch["recipeIngredient"][1]["quantity"] == 2
    assert "image" not in client.patch


@pytest.mark.asyncio
async def test_changed_source_blocks_update():
    class FakeClient:
        async def get_recipe(self, _slug):
            return {"recipeIngredient": [{"quantity": 0, "note": "anders"}]}

        async def update_recipe(self, _slug, _patch):
            raise AssertionError("No write after source mismatch")

    with pytest.raises(ValueError, match="changed"):
        await apply_selected_recipe(
            FakeClient(),
            "test",
            [
                {
                    "index": 0,
                    "source": "400-500 g Nudeln",
                    "quantity": 450,
                    "food_id": "food-a",
                    "food_name": "Nudeln",
                    "unit_id": "unit-g",
                    "unit_name": "g",
                }
            ],
        )
