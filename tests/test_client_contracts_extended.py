"""HTTP-level contracts for family planning and catalog workflows."""

import httpx
import pytest

from mealie_mcp.client import MealieClient, MealieError


@pytest.fixture
def api():
    requests = []

    def handler(request):
        requests.append(request)
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"id": "x", "items": [], "slug": "reis"})

    transport = httpx.MockTransport(handler)
    return MealieClient(
        "https://mealie.test",
        "secret",
        client=httpx.AsyncClient(transport=transport, base_url="https://mealie.test"),
    ), requests


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action,args,kwargs,method,path",
    [
        ("get_recipe", ("reis",), {}, "GET", "/api/recipes/reis"),
        ("delete_recipe", ("reis",), {}, "DELETE", "/api/recipes/reis"),
        ("parse_ingredients", (["2 g Reis"],), {}, "POST", "/api/parser/ingredients"),
        (
            "set_recipe_last_made",
            ("reis", "2026-09-29"),
            {},
            "PATCH",
            "/api/recipes/reis/last-made",
        ),
        ("list_meal_plan", ("2026-09-29", "2026-10-05"), {}, "GET", "/api/households/mealplans"),
        (
            "create_meal_plan_entry",
            (),
            {"date": "2026-09-29", "entry_type": "dinner", "recipe_id": "r"},
            "POST",
            "/api/households/mealplans",
        ),
        ("delete_meal_plan_entry", ("42",), {}, "DELETE", "/api/households/mealplans/42"),
        ("get_tag", ("t",), {}, "GET", "/api/organizers/tags/t"),
        ("create_tag", ("Familie",), {}, "POST", "/api/organizers/tags"),
        ("update_tag", ("t", "Neu"), {}, "PUT", "/api/organizers/tags/t"),
        ("delete_tag", ("t",), {}, "DELETE", "/api/organizers/tags/t"),
        ("list_categories", (), {}, "GET", "/api/organizers/categories"),
        ("create_category", ("Abendessen",), {}, "POST", "/api/organizers/categories"),
        ("list_recipe_tools", (), {}, "GET", "/api/organizers/tools"),
        ("create_recipe_tool", ("Ofen",), {}, "POST", "/api/organizers/tools"),
        ("delete_recipe_image", ("reis",), {}, "DELETE", "/api/recipes/reis/image"),
        ("create_shopping_list", ("Familie",), {}, "POST", "/api/households/shopping/lists"),
        ("list_shopping_lists", (), {}, "GET", "/api/households/shopping/lists"),
        (
            "add_recipe_to_shopping_list",
            ("l", "r"),
            {"factor": 1.5},
            "POST",
            "/api/households/shopping/lists/l/recipe/r",
        ),
        (
            "remove_recipe_from_shopping_list",
            ("l", "r"),
            {},
            "POST",
            "/api/households/shopping/lists/l/recipe/r/delete",
        ),
        ("get_shopping_list", ("l",), {}, "GET", "/api/households/shopping/lists/l"),
        ("delete_shopping_list", ("l",), {}, "DELETE", "/api/households/shopping/lists/l"),
        ("get_shopping_list_item", ("i",), {}, "GET", "/api/households/shopping/items/i"),
        ("delete_shopping_list_item", ("i",), {}, "DELETE", "/api/households/shopping/items/i"),
        ("list_foods", (), {"query": "Reis"}, "GET", "/api/foods"),
        ("list_units", (), {"query": "g"}, "GET", "/api/units"),
        ("list_cookbooks", (), {}, "GET", "/api/households/cookbooks"),
        ("create_cookbook", ("Familie",), {}, "POST", "/api/households/cookbooks"),
        ("get_cookbook", ("c",), {}, "GET", "/api/households/cookbooks/c"),
        ("delete_cookbook", ("c",), {}, "DELETE", "/api/households/cookbooks/c"),
    ],
)
async def test_native_endpoint_method_and_path(api, action, args, kwargs, method, path):
    client, calls = api
    await getattr(client, action)(*args, **kwargs)
    assert len(calls) == 1
    assert (calls[0].method, calls[0].url.path) == (method, path)


@pytest.mark.asyncio
async def test_http_errors_preserve_json_and_non_json_payload():
    for response, detail in [
        (httpx.Response(422, json={"detail": "invalid amount"}), "invalid amount"),
        (httpx.Response(503, text="offline"), "offline"),
    ]:
        client = MealieClient(
            "https://mealie.test",
            "t",
            client=httpx.AsyncClient(
                transport=httpx.MockTransport(lambda _, response=response: response),
                base_url="https://mealie.test",
            ),
        )
        with pytest.raises(MealieError, match=detail) as error:
            await client.get_recipe("reis")
        assert error.value.status_code == response.status_code


@pytest.mark.asyncio
async def test_patch_uses_existing_resources_and_keeps_other_fields(api):
    client, calls = api
    await client.update_recipe("reis", {"name": "Neuer Reis"})
    await client.update_meal_plan_entry(42, {"title": "Neu"})
    await client.update_shopping_list_item("i", {"checked": True})
    await client.update_cookbook("c", {"name": "Neu"})
    assert [call.method for call in calls] == ["GET", "PUT"] * 4
    assert b'"slug":"reis"' in calls[1].content
    assert b'"checked":true' in calls[5].content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,args",
    [
        ("update_recipe", ("reis", {"name": "Neu"})),
        ("update_meal_plan_entry", (42, {"title": "Neu"})),
        ("rename_shopping_list", ("l", "Neu")),
        ("update_shopping_list_item", ("i", {"checked": True})),
        ("update_cookbook", ("c", {"name": "Neu"})),
    ],
)
async def test_unexpected_read_payload_blocks_overwrite(method, args):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=[])

    client = MealieClient(
        "https://mealie.test",
        "t",
        client=httpx.AsyncClient(
            transport=httpx.MockTransport(handler), base_url="https://mealie.test"
        ),
    )
    with pytest.raises(MealieError, match="Unexpected"):
        await getattr(client, method)(*args)
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_catalog_reuses_case_insensitive_names_without_creating(api):
    client, _ = api

    async def existing():
        return {"items": [{"id": "one", "name": "Familie"}]}

    client.list_tags = existing
    client.list_categories = existing
    client.list_recipe_tools = existing
    assert (await client.get_or_create_tag("familie"))["id"] == "one"
    assert (await client.get_or_create_category("FAMILIE"))["id"] == "one"
    assert (await client.get_or_create_recipe_tool("Familie"))["id"] == "one"


@pytest.mark.asyncio
async def test_image_upload_rejects_empty_or_bad_base64_before_network(api):
    client, calls = api
    for value in ("", "%%"):
        with pytest.raises(MealieError, match="Invalid base64"):
            await client.upload_recipe_image_from_base64("reis", value, "image/png")
    assert calls == []
    await client.upload_recipe_image_from_base64("reis", "aW1hZ2U=", "image/png")
    assert calls[0].url.path == "/api/recipes/reis/image"
    assert b"image.png" in calls[0].content


@pytest.mark.asyncio
async def test_import_fetches_saved_recipe_and_rejects_missing_slug():
    calls = []

    def handler(request):
        calls.append(request)
        if request.method == "POST":
            return httpx.Response(200, json="imported-reis")
        return httpx.Response(200, json={"slug": "imported-reis"})

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://mealie.test")
    client = MealieClient("https://mealie.test", "t", client=http)
    assert (await client.import_recipe_from_url("https://example.test/recipe"))[
        "slug"
    ] == "imported-reis"
    assert (await client.import_recipe_from_html_or_json("<script>json-ld</script>"))[
        "slug"
    ] == "imported-reis"
    assert [r.url.path for r in calls] == [
        "/api/recipes/create/url",
        "/api/recipes/imported-reis",
        "/api/recipes/create/html-or-json",
        "/api/recipes/imported-reis",
    ]

    bad = MealieClient(
        "https://mealie.test",
        "t",
        client=httpx.AsyncClient(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})),
            base_url="https://mealie.test",
        ),
    )
    with pytest.raises(MealieError, match="Unexpected HTML/JSON"):
        await bad.import_recipe_from_html_or_json("content")


@pytest.mark.asyncio
async def test_shopping_item_api_extracts_created_item_and_rejects_unknown_response():
    for payload, valid in [
        ({"createdItems": [{"id": "new"}]}, True),
        ({"updatedItems": [{"id": "merged"}]}, True),
        ({"createdItems": []}, False),
    ]:
        calls = []

        def handler(request, calls=calls, payload=payload):
            calls.append(request)
            return httpx.Response(200, json=payload)

        client = MealieClient(
            "https://mealie.test",
            "t",
            client=httpx.AsyncClient(
                transport=httpx.MockTransport(handler), base_url="https://mealie.test"
            ),
        )
        if valid:
            assert "id" in await client.add_shopping_list_item(
                list_id="l", note="Reis", quantity=2, food_id="f", unit_id="u"
            )
        else:
            with pytest.raises(MealieError, match="Unexpected shopping item"):
                await client.add_shopping_list_item(list_id="l", note="Reis")
        assert calls[0].url.path == "/api/households/shopping/items"
        assert b'"shoppingListId":"l"' in calls[0].content
