"""Native cookbook and tag operations retain Mealie filter configuration."""

import json

import httpx
import pytest

from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_cookbook_filter_creation_and_rename():
    requests = []

    def handle(request):
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": "book-a",
                    "name": "Alt",
                    "queryFilterString": "tags IN familie",
                    "description": "Familie",
                    "public": False,
                },
            )
        return httpx.Response(200, json={"id": "book-a"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.create_cookbook("Familie", query_filter_string="tags IN familie")
        await client.update_cookbook("book-a", {"name": "Neu"})
        await client.delete_cookbook("book-a")

    assert json.loads(requests[0].content)["queryFilterString"] == "tags IN familie"
    assert requests[1].url.path == "/api/households/cookbooks/book-a"
    updated = json.loads(requests[2].content)
    assert updated["name"] == "Neu"
    assert updated["queryFilterString"] == "tags IN familie"
    assert requests[3].method == "DELETE"


@pytest.mark.asyncio
async def test_tag_read_rename_and_delete_use_organizer_routes():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        return httpx.Response(200, json={"id": "tag-a", "name": "Neu"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.get_tag("tag-a")
        await client.update_tag("tag-a", "Neu")
        await client.delete_tag("tag-a")

    assert calls == [
        ("GET", "/api/organizers/tags/tag-a"),
        ("PUT", "/api/organizers/tags/tag-a"),
        ("DELETE", "/api/organizers/tags/tag-a"),
    ]
