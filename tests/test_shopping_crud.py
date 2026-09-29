"""Structured shopping item and list edits preserve unrelated data."""

import json

import httpx
import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_rename_and_edit_item_preserve_existing_fields():
    requests = []

    def handle(request):
        requests.append(request)
        if request.method == "GET" and "/lists/" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "id": "list-a",
                    "name": "Alt",
                    "groupId": "group",
                    "userId": "user",
                    "listItems": [{"id": "other"}],
                },
            )
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": "item-a",
                    "shoppingListId": "list-a",
                    "quantity": 2,
                    "foodId": "food-a",
                    "unitId": "unit-a",
                    "checked": True,
                },
            )
        return httpx.Response(200, json={"id": "ok"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.rename_shopping_list("list-a", "Neu")
        await client.update_shopping_list_item("item-a", {"quantity": 3})

    renamed = json.loads(requests[1].content)
    changed = json.loads(requests[3].content)
    assert requests[1].method == "PUT"
    assert renamed["listItems"] == [{"id": "other"}]
    assert renamed["name"] == "Neu"
    assert changed["quantity"] == 3
    assert changed["checked"] is True
    assert changed["foodId"] == "food-a"


@pytest.mark.asyncio
async def test_create_structured_item_sends_food_and_unit_ids():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            201, json={"createdItems": [{"id": "item-a"}], "updatedItems": [], "deletedItems": []}
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await client.add_shopping_list_item(
            list_id="list-a", note="", quantity=2, food_id="food-a", unit_id="unit-a"
        )

    assert result["id"] == "item-a"
    assert json.loads(requests[0].content) == {
        "shoppingListId": "list-a",
        "note": "",
        "checked": False,
        "quantity": 2,
        "foodId": "food-a",
        "unitId": "unit-a",
    }


@pytest.mark.asyncio
async def test_delete_list_requires_the_inspected_name(monkeypatch):
    class FakeClient:
        async def get_shopping_list(self, _list_id):
            return {"id": "list-a", "name": "Einkauf", "listItems": [{"id": "item-a"}]}

        async def delete_shopping_list(self, _list_id):
            raise AssertionError("Delete must not run after a name mismatch")

    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")
    monkeypatch.setattr(server, "_client", lambda _ctx: FakeClient())
    tool = server.build_server()._tool_manager._tools["delete_shopping_list"].fn
    with pytest.raises(ValueError, match="inspect"):
        await tool(None, "list-a", "Falsche Liste")
