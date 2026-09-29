"""Meal-plan API contracts for pagination and in-place edits."""

import json

import httpx
import pytest

from mealie_mcp import server
from mealie_mcp.client import MealieClient


@pytest.mark.asyncio
async def test_page_two_and_update_preserve_required_entry_fields():
    requests = []

    def handle(request):
        requests.append(request)
        if request.method == "GET" and request.url.path.endswith("/mealplans"):
            return httpx.Response(200, json={"items": [], "page": 2, "totalPages": 3})
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": 10,
                    "groupId": "group",
                    "userId": "user",
                    "date": "2026-10-01",
                    "entryType": "lunch",
                    "recipeId": "recipe",
                    "text": "",
                },
            )
        return httpx.Response(200, json={"id": 10})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        page = await client.list_meal_plan("2026-09-28", "2026-10-04", page=2, per_page=50)
        await client.update_meal_plan_entry(
            10, {"entryType": "snack", "recipeId": None, "text": "Obst"}
        )

    assert page["totalPages"] == 3
    assert requests[0].url.params["page"] == "2"
    assert requests[0].url.params["perPage"] == "50"
    assert requests[1].url.path == "/api/households/mealplans/10"
    assert requests[2].method == "PUT"
    body = json.loads(requests[2].content)
    assert body["groupId"] == "group"
    assert body["userId"] == "user"
    assert body["entryType"] == "snack"
    assert body["recipeId"] is None
    assert body["text"] == "Obst"


@pytest.mark.asyncio
async def test_mcp_tools_create_drink_and_edit_dessert_text(monkeypatch):
    calls = []

    class FakeClient:
        async def create_meal_plan_entry(self, **fields):
            calls.append(("create", fields))
            return {"id": 10, **fields}

        async def update_meal_plan_entry(self, entry_id, patch):
            calls.append(("update", entry_id, patch))
            return {"id": entry_id, **patch}

    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "dummy")
    monkeypatch.setattr(server, "_client", lambda _ctx: FakeClient())
    tools = server.build_server()._tool_manager._tools
    await tools["create_meal_plan_entry"].fn(
        None, "2026-10-01", "drink", title="Saft", text="Ohne Zucker"
    )
    await tools["update_meal_plan_entry"].fn(
        None, 10, entry_type="dessert", text="Obst", clear_recipe=True
    )

    assert calls[0][1]["entry_type"] == "drink"
    assert calls[0][1]["text"] == "Ohne Zucker"
    assert calls[1] == ("update", 10, {"entryType": "dessert", "text": "Obst", "recipeId": None})
