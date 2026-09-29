"""Shopping-list requests follow the supplied Mealie OpenAPI contract."""

import httpx
import pytest

from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_list_items_reads_the_requested_list():
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "list-a",
                "listItems": [{"id": "item-a", "shoppingListId": "list-a", "note": "Milch"}],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await client.list_shopping_list_items("list-a")

    assert [(r.method, r.url.path, r.url.query) for r in requests] == [
        ("GET", "/api/households/shopping/lists/list-a", b"")
    ]
    assert result == {"items": [{"id": "item-a", "shoppingListId": "list-a", "note": "Milch"}]}


@pytest.mark.asyncio
async def test_add_item_extracts_id_from_mealie_collection():
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            201,
            json={
                "createdItems": [
                    {"id": "item-a", "shoppingListId": "list-a", "note": "Milch"}
                ],
                "updatedItems": [],
                "deletedItems": [],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await client.add_shopping_list_item(list_id="list-a", note="Milch")

    assert len(requests) == 1
    assert requests[0].url.path == "/api/households/shopping/items"
    assert result["id"] == "item-a"


@pytest.mark.asyncio
async def test_add_item_returns_id_when_mealie_combines_with_existing_item():
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "createdItems": [],
                "updatedItems": [
                    {"id": "existing-item", "shoppingListId": "list-a", "note": "Milch"}
                ],
                "deletedItems": [],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await client.add_shopping_list_item(list_id="list-a", note="Milch")

    assert result["id"] == "existing-item"
