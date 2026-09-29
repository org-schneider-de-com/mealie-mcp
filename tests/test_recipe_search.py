"""Mealie recipe search forwards filters and exposes pagination metadata."""

import httpx
import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_search_forwards_filters_and_page_without_truncation():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "items": [{"slug": "reis", "name": "Reis"}],
                "page": 2,
                "total": 125,
                "totalPages": 3,
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        result = await client.search_recipes(
            query="Reis",
            tags=["familie"],
            categories=["abendessen"],
            foods=["reis"],
            cookbook="wochenplan",
            page=2,
            per_page=50,
        )

    params = requests[0].url.params
    assert params["search"] == "Reis"
    assert params.get_list("tags") == ["familie"]
    assert params.get_list("categories") == ["abendessen"]
    assert params.get_list("foods") == ["reis"]
    assert params["cookbook"] == "wochenplan"
    assert params["page"] == "2"
    assert params["perPage"] == "50"
    assert result["total"] == 125


@pytest.mark.asyncio
async def test_mcp_tool_preserves_total_and_next_page(monkeypatch):
    class FakeClient:
        async def search_recipes(self, **params):
            assert params["page"] == 2
            assert params["categories"] == ["abendessen"]
            return {
                "items": [{"slug": "reis", "name": "Reis"}],
                "page": 2,
                "total": 125,
                "totalPages": 3,
                "next": "page-3",
            }

    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")
    monkeypatch.setattr(server, "_client", lambda _ctx: FakeClient())
    tool = server.build_server()._tool_manager._tools["search_recipes"].fn
    result = await tool(None, page=2, categories=["abendessen"])

    assert result["total"] == 125
    assert result["totalPages"] == 3
    assert result["next"] == "page-3"
    assert result["items"][0]["slug"] == "reis"
