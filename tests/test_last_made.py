"""Only explicitly confirmed cooking events update Mealie lastMade."""

import httpx
import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_client_patches_timestamp_to_native_mealie_route():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"slug": "reis", "lastMade": "2026-09-29T18:00:00+02:00"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.set_recipe_last_made("reis", "2026-09-29T18:00:00+02:00")

    assert requests[0].method == "PATCH"
    assert requests[0].url.path == "/api/recipes/reis/last-made"
    assert requests[0].read() == b'{"timestamp":"2026-09-29T18:00:00+02:00"}'


@pytest.mark.asyncio
async def test_tool_refuses_unconfirmed_or_timezone_free_date(monkeypatch):
    class FakeClient:
        async def set_recipe_last_made(self, _slug, _timestamp):
            raise AssertionError("No write without a confirmed timezone-aware timestamp")

    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")
    monkeypatch.setattr(server, "_client", lambda _ctx: FakeClient())
    tool = server.build_server()._tool_manager._tools["set_recipe_last_made"].fn
    with pytest.raises(ValueError, match="confirmation"):
        await tool(None, "reis", "2026-09-29T18:00:00+02:00", confirmed=False)
    with pytest.raises(ValueError, match="timezone"):
        await tool(None, "reis", "2026-09-29T18:00:00", confirmed=True)
