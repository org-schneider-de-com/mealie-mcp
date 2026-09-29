"""Public MCP tools compose Mealie calls without changing unrelated data."""

import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieError


class ScenarioClient:
    def __init__(self, replies=None, failure=None):
        self.calls = []
        self.replies = replies or {}
        self.failure = failure

    def __getattr__(self, method):
        async def call(*args, **kwargs):
            self.calls.append((method, args, kwargs))
            if method == self.failure:
                raise MealieError(422, "invalid", {"detail": "invalid"})
            return self.replies.get(method)

        return call


@pytest.fixture
def tool_env(monkeypatch):
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")

    def build(client):
        monkeypatch.setattr(server, "_client", lambda _ctx: client)
        return {name: tool.fn for name, tool in server.build_server()._tool_manager._tools.items()}

    return build


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name,args,kwargs,method,reply",
    [
        ("get_recipe", ("reis",), {}, "get_recipe", {"slug": "reis"}),
        ("list_shopping_recipe_references", ("list-a",), {}, "list_shopping_recipe_references", []),
        ("get_tag", ("tag-a",), {}, "get_tag", {"id": "tag-a"}),
        ("create_tag", ("Neu",), {}, "create_tag", {"id": "tag-a"}),
        ("rename_tag", ("tag-a", "Neu"), {}, "update_tag", {"id": "tag-a"}),
        ("get_meal_plan_entry", (10,), {}, "get_meal_plan_entry", {"id": 10}),
        ("get_shopping_list", ("list-a",), {}, "get_shopping_list", {"id": "list-a"}),
        ("rename_shopping_list", ("list-a", "Neu"), {}, "rename_shopping_list", {"id": "list-a"}),
        ("get_shopping_list_item", ("item-a",), {}, "get_shopping_list_item", {"id": "item-a"}),
        (
            "check_off_shopping_item",
            ("item-a",),
            {"checked": False},
            "check_off_shopping_item",
            {"checked": False},
        ),
        ("get_cookbook", ("book-a",), {}, "get_cookbook", {"id": "book-a"}),
        ("delete_recipe_image", ("reis",), {}, "delete_recipe_image", None),
        ("delete_recipe", ("reis",), {}, "delete_recipe", None),
        ("delete_meal_plan_entry", ("10",), {}, "delete_meal_plan_entry", None),
        ("create_shopping_list", ("Familie",), {}, "create_shopping_list", {"id": "list-a"}),
        (
            "set_recipe_image_from_url",
            ("reis", "https://example.test/a.png"),
            {},
            "upload_recipe_image_from_url",
            {},
        ),
        (
            "set_recipe_image_from_base64",
            ("reis", "YWJj"),
            {},
            "upload_recipe_image_from_base64",
            {},
        ),
        (
            "import_recipe_from_url",
            ("https://example.test/recipe",),
            {},
            "import_recipe_from_url",
            {"slug": "reis"},
        ),
        (
            "create_cookbook",
            ("Familie",),
            {"query_filter_string": "tags IN familie"},
            "create_cookbook",
            {"id": "book-a"},
        ),
    ],
)
async def test_simple_tools_call_only_the_expected_native_method(
    tool_env, tool_name, args, kwargs, method, reply
):
    client = ScenarioClient({method: reply})
    result = await tool_env(client)[tool_name](None, *args, **kwargs)
    assert [call[0] for call in client.calls] == [method]
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name,args,method",
    [
        ("get_recipe", ("reis",), "get_recipe"),
        ("get_tag", ("tag-a",), "get_tag"),
        ("get_cookbook", ("book-a",), "get_cookbook"),
        ("get_shopping_list", ("list-a",), "get_shopping_list"),
        ("delete_recipe_image", ("reis",), "delete_recipe_image"),
    ],
)
async def test_mealie_failures_remain_visible(tool_env, tool_name, args, method):
    client = ScenarioClient(failure=method)
    with pytest.raises(RuntimeError, match="422.*invalid"):
        await tool_env(client)[tool_name](None, *args)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name,args,kwargs",
    [
        ("rename_tag", ("tag-a", "  "), {}),
        ("rename_shopping_list", ("list-a", ""), {}),
        ("add_structured_shopping_item", ("list-a", -1, "food-a"), {}),
        ("update_shopping_list_item", ("item-a",), {"quantity": 0}),
        ("update_cookbook", ("book-a",), {}),
        ("list_meal_plan", ("2026-10-01", "2026-10-07"), {"page": 0}),
        ("search_recipes", (), {"page": 0}),
    ],
)
async def test_implausible_input_is_rejected_before_api_call(tool_env, tool_name, args, kwargs):
    client = ScenarioClient()
    with pytest.raises(ValueError):
        await tool_env(client)[tool_name](None, *args, **kwargs)
    assert client.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name,args,kwargs,reply,expected",
    [
        (
            "search_recipes",
            (),
            {"tags": ["vegan"], "page": 2},
            {
                "items": [{"slug": "r", "name": "Reis", "tags": [{"name": "vegan"}]}],
                "totalPages": 3,
            },
            {
                "items": [
                    {
                        "slug": "r",
                        "name": "Reis",
                        "description": None,
                        "tags": ["vegan"],
                        "categories": [],
                    }
                ],
                "totalPages": 3,
            },
        ),
        (
            "list_meal_plan",
            ("2026-09-29", "2026-10-05"),
            {"page": 2},
            {"items": [{"entryType": "dinner"}], "totalPages": 3},
            {"items": [{"entryType": "dinner"}], "totalPages": 3},
        ),
        (
            "list_shopping_lists",
            (),
            {},
            {"items": [{"id": "l", "name": "Familie", "private": True}]},
            [{"id": "l", "name": "Familie"}],
        ),
        ("list_shopping_list_items", ("l",), {}, {"items": [{"id": "i"}]}, [{"id": "i"}]),
        (
            "list_tags",
            (),
            {},
            {"items": [{"id": "t", "name": "Vegan", "slug": "vegan"}]},
            [{"id": "t", "name": "Vegan", "slug": "vegan"}],
        ),
        (
            "list_categories",
            (),
            {},
            {"items": [{"id": "c", "name": "Dinner", "slug": "dinner"}]},
            [{"id": "c", "name": "Dinner", "slug": "dinner"}],
        ),
        (
            "list_recipe_tools",
            (),
            {},
            {"items": [{"id": "t", "name": "Ofen", "slug": "ofen"}]},
            [{"id": "t", "name": "Ofen", "slug": "ofen"}],
        ),
        (
            "list_cookbooks",
            (),
            {},
            {"items": [{"id": "c", "name": "Familie", "slug": "familie"}]},
            [{"id": "c", "name": "Familie", "slug": "familie"}],
        ),
        (
            "list_foods",
            (),
            {"query": "Reis", "limit": 9999},
            {"items": [{"id": "f"}]},
            [{"id": "f"}],
        ),
        ("list_units", (), {"limit": -5}, {"items": [{"id": "u"}]}, [{"id": "u"}]),
    ],
)
async def test_read_tools_keep_pagination_and_identity(
    tool_env, tool_name, args, kwargs, reply, expected
):
    client = ScenarioClient({tool_name: reply})
    assert await tool_env(client)[tool_name](None, *args, **kwargs) == expected
    assert len(client.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tool_name,args,read_method,delete_method,identity",
    [
        ("delete_tag", ("t", "Vegan"), "get_tag", "delete_tag", {"name": "Vegan"}),
        (
            "delete_cookbook",
            ("c", "Familie"),
            "get_cookbook",
            "delete_cookbook",
            {"name": "Familie"},
        ),
        (
            "delete_shopping_list",
            ("l", "Familie"),
            "get_shopping_list",
            "delete_shopping_list",
            {"name": "Familie"},
        ),
        (
            "delete_shopping_list_item",
            ("i", "l", "Reis"),
            "get_shopping_list_item",
            "delete_shopping_list_item",
            {"shoppingListId": "l", "note": "Reis"},
        ),
    ],
)
async def test_destructive_tools_verify_inspected_identity(
    tool_env, tool_name, args, read_method, delete_method, identity
):
    client = ScenarioClient({read_method: identity})
    assert (await tool_env(client)[tool_name](None, *args))["status"] == "deleted"
    assert [call[0] for call in client.calls] == [read_method, delete_method]
    client = ScenarioClient({read_method: {**identity, next(iter(identity)): "changed"}})
    with pytest.raises(ValueError, match="changed"):
        await tool_env(client)[tool_name](None, *args)
    assert [call[0] for call in client.calls] == [read_method]


@pytest.mark.asyncio
async def test_recipe_organizer_replacement_preserves_only_requested_relation(tool_env):
    for tool_name, names, resolver, relation in [
        ("set_recipe_tags", ["Vegan"], "get_or_create_tag", "tags"),
        ("set_recipe_categories", ["Dinner"], "get_or_create_category", "recipeCategory"),
        ("set_recipe_tools", ["Ofen"], "get_or_create_recipe_tool", "tools"),
    ]:
        client = ScenarioClient({resolver: {"id": "existing"}, "update_recipe": {"slug": "reis"}})
        await tool_env(client)[tool_name](None, "reis", names)
        assert client.calls[-1] == ("update_recipe", ("reis", {relation: [{"id": "existing"}]}), {})


@pytest.mark.asyncio
async def test_meal_plan_recipe_link_uses_id_and_free_text_needs_content(tool_env):
    client = ScenarioClient({"get_recipe": {"id": "uuid"}, "create_meal_plan_entry": {"id": 42}})
    result = await tool_env(client)["create_meal_plan_entry"](
        None, "2026-10-01", "dinner", recipe_slug="reis"
    )
    assert result == {"id": 42}
    assert client.calls[-1][2]["recipe_id"] == "uuid"
    with pytest.raises(ValueError, match="Provide"):
        await tool_env(client)["create_meal_plan_entry"](None, "2026-10-01", "dinner")
    assert len(client.calls) == 2
    client = ScenarioClient({"get_recipe": {"slug": "reis"}})
    with pytest.raises(RuntimeError, match="no id"):
        await tool_env(client)["create_meal_plan_entry"](
            None, "2026-10-01", "dinner", recipe_slug="reis"
        )


@pytest.mark.asyncio
async def test_meal_plan_edit_can_clear_link_or_replace_recipe(tool_env):
    client = ScenarioClient({"update_meal_plan_entry": {"id": 42}, "get_recipe": {"id": "new-id"}})
    tools = tool_env(client)
    await tools["update_meal_plan_entry"](None, 42, clear_recipe=True, title="Pasta")
    assert client.calls[-1][1] == (42, {"title": "Pasta", "recipeId": None})
    await tools["update_meal_plan_entry"](None, 42, recipe_slug="pasta", entry_type="dinner")
    assert client.calls[-1][1] == (42, {"entryType": "dinner", "recipeId": "new-id"})
    with pytest.raises(ValueError):
        await tools["update_meal_plan_entry"](None, 42, recipe_slug="pasta", clear_recipe=True)


@pytest.mark.asyncio
async def test_shopping_recipe_links_refuse_duplicates_and_nonfinite_factors(tool_env):
    client = ScenarioClient(
        {
            "list_shopping_recipe_references": [{"recipeId": "r"}],
            "add_recipe_to_shopping_list": {"ok": True},
        }
    )
    tools = tool_env(client)
    with pytest.raises(ValueError, match="already linked"):
        await tools["add_recipe_to_shopping_list"](None, "l", "r")
    assert [call[0] for call in client.calls] == ["list_shopping_recipe_references"]
    await tools["add_recipe_to_shopping_list"](None, "l", "r", factor=1.5, allow_existing=True)
    assert client.calls[-1][2] == {"factor": 1.5}
    with pytest.raises(ValueError, match="finite"):
        await tools["remove_recipe_from_shopping_list"](None, "l", "r", factor=float("inf"))


@pytest.mark.asyncio
async def test_bulk_shopping_items_continue_after_one_api_error(tool_env):
    class PartialClient(ScenarioClient):
        async def add_shopping_list_item(self, *, list_id, note):
            self.calls.append((list_id, note))
            if note == "ungültig":
                raise MealieError(422, "bad item")
            return {"id": "new"}

    client = PartialClient()
    result = await tool_env(client)["add_shopping_list_items"](
        None, "l", [" Reis ", "  ", "ungültig", "Milch"]
    )
    assert result["added"] == [{"id": "new", "note": "Reis"}, {"id": "new", "note": "Milch"}]
    assert len(result["errors"]) == 1
    assert client.calls == [("l", "Reis"), ("l", "ungültig"), ("l", "Milch")]


@pytest.mark.asyncio
async def test_import_flags_rows_that_cannot_scale(tool_env):
    recipe = {"recipeIngredient": [{"note": "2-3 Eier"}, {"quantity": 2, "food": {"id": "egg"}}]}
    client = ScenarioClient({"import_recipe_from_html_or_json": recipe})
    result = await tool_env(client)["import_recipe_from_html_or_json"](
        None, "<html>recipe</html>", include_tags=True
    )
    assert result["unstructuredIngredients"] == [{"index": 0, "note": "2-3 Eier"}]
    assert client.calls[0][2]["include_tags"] is True
    with pytest.raises(ValueError):
        await tool_env(client)["import_recipe_from_html_or_json"](None, "  ")


@pytest.mark.asyncio
async def test_recipe_creation_stores_scalable_ingredients_servings_and_metadata(tool_env):
    client = ScenarioClient(
        {
            "resolve_ingredient_entity": {"id": "catalog-id", "name": "Reis"},
            "create_recipe": "reis",
            "get_or_create_tag": {"id": "tag-id"},
            "get_or_create_category": {"id": "category-id"},
            "get_or_create_recipe_tool": {"id": "tool-id"},
            "update_recipe": {"slug": "reis", "name": "Reis", "tags": [{"name": "Abendessen"}]},
        }
    )
    tools = tool_env(client)
    result = await tools["create_recipe"](
        None,
        "Reis",
        recipe_yield="3 Personen",
        recipe_servings=3,
        description="Familienessen",
        prep_time="10 min",
        cook_time="20 min",
        total_time="30 min",
        perform_time="5 min",
        org_url="https://example.test",
        recipe_yield_quantity=1,
        nutrition={"calories": "300 kcal"},
        ingredients=[
            server.RecipeIngredientInput(title="Basis"),
            server.RecipeIngredientInput(quantity=300, unit="g", food="Reis"),
        ],
        instructions=["### Kochen", "Reis kochen"],
        notes=["Mit Gemüse"],
        tags=["Abendessen"],
        categories=["Dinner"],
        tools=["Topf"],
    )
    assert result["slug"] == "reis"
    patch = client.calls[-1][1][1]
    assert patch["recipeServings"] == 3
    assert patch["recipeYield"] == ""
    assert patch["recipeIngredient"][1]["quantity"] == 300
    assert patch["recipeIngredient"][1]["food"]["id"] == "catalog-id"
    assert patch["recipeInstructions"] == [{"title": "Kochen", "text": ""}, {"text": "Reis kochen"}]
    assert patch["nutrition"] == {"calories": "300 kcal"}
    assert patch["tags"] == [{"id": "tag-id"}]
    assert patch["recipeCategory"] == [{"id": "category-id"}]
    assert patch["tools"] == [{"id": "tool-id"}]
    assert client.calls[0][0] == "resolve_ingredient_entity"
    assert [call[0] for call in client.calls].index("create_recipe") < [
        call[0] for call in client.calls
    ].index("update_recipe")


@pytest.mark.asyncio
async def test_recipe_validation_precedes_creating_shell(tool_env):
    client = ScenarioClient()
    tools = tool_env(client)
    with pytest.raises(ValueError, match="range"):
        await tools["create_recipe"](None, "Reis", ingredients=["2-3 Eier"])
    with pytest.raises(ValueError, match="Unsupported nutrition"):
        await tools["create_recipe"](None, "Reis", nutrition={"invented": "12"})
    assert client.calls == []


@pytest.mark.asyncio
async def test_recipe_update_replaces_requested_fields_only(tool_env):
    client = ScenarioClient({"update_recipe": {"slug": "reis", "name": "Neu"}})
    tools = tool_env(client)
    result = await tools["update_recipe"](
        None, "reis", name="Neu", recipe_servings=4, notes=["Hallo"], tags=[]
    )
    assert result["name"] == "Neu"
    assert client.calls == [
        (
            "update_recipe",
            (
                "reis",
                {
                    "name": "Neu",
                    "recipeServings": 4,
                    "notes": [{"title": "", "text": "Hallo"}],
                    "tags": [],
                },
            ),
            {},
        )
    ]
    with pytest.raises(ValueError, match="at least one"):
        await tools["update_recipe"](None, "reis")


@pytest.mark.asyncio
async def test_recipe_shell_failure_and_partial_update_failure_are_explained(tool_env):
    client = ScenarioClient(failure="create_recipe")
    with pytest.raises(RuntimeError, match="422"):
        await tool_env(client)["create_recipe"](None, "Reis")
    client = ScenarioClient({"create_recipe": "reis"}, failure="update_recipe")
    with pytest.raises(RuntimeError, match="created but update failed"):
        await tool_env(client)["create_recipe"](None, "Reis", description="Neu")


@pytest.mark.asyncio
async def test_data_uri_image_mime_is_passed_to_upload(tool_env):
    client = ScenarioClient({"upload_recipe_image_from_base64": {}})
    result = await tool_env(client)["set_recipe_image_from_base64"](
        None, "reis", "data:image/png;base64,aW1hZ2U="
    )
    assert result["status"] == "image updated"
    assert client.calls[0][1] == ("reis", "aW1hZ2U=", "image/png")
