"""Image upload rejects bad bytes and deletion follows the Mealie route."""

import httpx
import pytest

from mealie_mcp.client import MealieClient, MealieError


@pytest.mark.asyncio
async def test_invalid_base64_never_reaches_image_upload():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        with pytest.raises(MealieError, match="Invalid base64"):
            await client.upload_recipe_image_from_base64("reis", "!!!!", "image/png")
    assert requests == []


@pytest.mark.asyncio
async def test_delete_image_then_read_recipe_without_one():
    calls = []

    def handle(request):
        calls.append((request.method, request.url.path))
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"slug": "reis", "image": None})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handle), base_url="https://mealie.test"
    ) as http:
        client = MealieClient("https://mealie.test", "token", client=http)
        await client.delete_recipe_image("reis")
        recipe = await client.get_recipe("reis")

    assert recipe["image"] is None
    assert calls == [
        ("DELETE", "/api/recipes/reis/image"), ("GET", "/api/recipes/reis")
    ]
