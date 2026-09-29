"""Async HTTP client for the Mealie REST API."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

import httpx


class MealieError(RuntimeError):
    """Raised when the Mealie API returns an error response."""

    def __init__(self, status_code: int, message: str, payload: Any = None) -> None:
        super().__init__(f"Mealie API error {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload


class MealieClient:
    """Thin async wrapper around the Mealie HTTP API.

    Only the endpoints required by the MCP tools are exposed. Each method
    returns the parsed JSON body and raises ``MealieError`` on non-2xx
    responses.
    """

    def __init__(
        self,
        base_url: str,
        api_token: str,
        *,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Accept": "application/json",
            },
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> MealieClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        clean_params: dict[str, Any] | None = None
        if params is not None:
            clean_params = {k: v for k, v in params.items() if v is not None}

        response = await self._client.request(method, path, params=clean_params, json=json)
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("detail") if isinstance(payload, dict) else payload
            except ValueError:
                payload = response.text
                detail = response.text
            raise MealieError(response.status_code, str(detail), payload)

        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    # ---- Recipes -----------------------------------------------------------------

    async def search_recipes(
        self,
        *,
        query: str | None = None,
        tags: list[str] | None = None,
        categories: list[str] | None = None,
        foods: list[str] | None = None,
        cookbook: str | None = None,
        per_page: int = 25,
        page: int = 1,
    ) -> dict[str, Any]:
        """Search recipes. ``tags`` are matched by slug."""
        params: dict[str, Any] = {
            "search": query,
            "perPage": per_page,
            "page": page,
        }
        if tags:
            params["tags"] = tags
        if categories:
            params["categories"] = categories
        if foods:
            params["foods"] = foods
        if cookbook:
            params["cookbook"] = cookbook
        return await self._request("GET", "/api/recipes", params=params)

    async def get_recipe(self, slug: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/recipes/{slug}")

    async def create_recipe(self, name: str) -> str:
        """Create an empty recipe with the given name. Returns the new slug."""
        result = await self._request("POST", "/api/recipes", json={"name": name})
        if isinstance(result, str):
            return result
        if isinstance(result, dict) and "slug" in result:
            return result["slug"]
        raise MealieError(500, "Unexpected response from create_recipe", result)

    async def update_recipe(self, slug: str, patch: dict[str, Any]) -> dict[str, Any]:
        """Partially update a recipe. Mealie requires the full resource on PUT,
        so we fetch, merge, and send back.
        """
        current = await self.get_recipe(slug)
        if not isinstance(current, dict):
            raise MealieError(500, "Unexpected response from get_recipe", current)
        merged = {**current, **patch}
        if isinstance(current.get("nutrition"), dict) and isinstance(patch.get("nutrition"), dict):
            merged["nutrition"] = {**current["nutrition"], **patch["nutrition"]}
        if "recipeServings" in patch and "recipeYield" not in patch:
            old_yield = current.get("recipeYield") or ""
            if re.fullmatch(
                r"\s*\d+(?:[.,]\d+)?\s*(?:portion(?:en|s)?|person(?:en|s)?|servings?)\s*",
                old_yield,
                re.IGNORECASE,
            ):
                merged["recipeYield"] = ""
        return await self._request("PUT", f"/api/recipes/{slug}", json=merged)

    async def import_recipe_from_url(
        self, url: str, *, include_tags: bool = True
    ) -> dict[str, Any]:
        """Scrape a recipe from an external URL and save it to Mealie."""
        result = await self._request(
            "POST", "/api/recipes/create/url", json={"url": url, "includeTags": include_tags}
        )
        # Mealie returns the slug string; fetch the full recipe for a useful response.
        if isinstance(result, str):
            return await self.get_recipe(result)
        return result

    async def import_recipe_from_html_or_json(
        self, data: str, *, include_tags: bool = False, include_categories: bool = False
    ) -> dict[str, Any]:
        """Let Mealie import pasted structured data, then fetch the saved recipe."""
        slug = await self._request(
            "POST",
            "/api/recipes/create/html-or-json",
            json={
                "data": data,
                "includeTags": include_tags,
                "includeCategories": include_categories,
            },
        )
        if not isinstance(slug, str) or not slug:
            raise MealieError(500, "Unexpected HTML/JSON import response", slug)
        return await self.get_recipe(slug)

    async def delete_recipe(self, slug: str) -> None:
        await self._request("DELETE", f"/api/recipes/{slug}")

    async def parse_ingredients(
        self, ingredients: list[str], *, parser: str = "nlp"
    ) -> list[dict[str, Any]]:
        """Parse ingredient text with Mealie's own food and unit catalog."""
        return await self._request(
            "POST", "/api/parser/ingredients", json={"parser": parser, "ingredients": ingredients}
        )

    async def set_recipe_last_made(self, slug: str, timestamp: str) -> dict[str, Any]:
        return await self._request(
            "PATCH", f"/api/recipes/{slug}/last-made", json={"timestamp": timestamp}
        )

    # ---- Meal plans --------------------------------------------------------------

    async def get_todays_meal_plan(self) -> list[dict[str, Any]]:
        result = await self._request("GET", "/api/households/mealplans/today")
        if isinstance(result, list):
            return result
        return []

    async def list_meal_plan(
        self, start_date: str, end_date: str, *, page: int = 1, per_page: int = 1000
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/households/mealplans",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "page": page,
                "perPage": per_page,
            },
        )

    async def get_meal_plan_entry(self, entry_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/households/mealplans/{entry_id}")

    async def update_meal_plan_entry(self, entry_id: int, patch: dict[str, Any]) -> dict[str, Any]:
        current = await self.get_meal_plan_entry(entry_id)
        if not isinstance(current, dict):
            raise MealieError(500, "Unexpected meal plan entry response", current)
        return await self._request(
            "PUT", f"/api/households/mealplans/{entry_id}", json={**current, **patch}
        )

    async def create_meal_plan_entry(
        self,
        *,
        date: str,
        entry_type: str,
        recipe_id: str | None = None,
        title: str | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"date": date, "entryType": entry_type}
        if recipe_id is not None:
            body["recipeId"] = recipe_id
        if title is not None:
            body["title"] = title
        if text is not None:
            body["text"] = text
        return await self._request("POST", "/api/households/mealplans", json=body)

    async def delete_meal_plan_entry(self, entry_id: str) -> None:
        await self._request("DELETE", f"/api/households/mealplans/{entry_id}")

    # ---- Organizers: Tags --------------------------------------------------------

    async def list_tags(self, *, per_page: int = 1000) -> dict[str, Any]:
        return await self._request("GET", "/api/organizers/tags", params={"perPage": per_page})

    async def create_tag(self, name: str) -> dict[str, Any]:
        return await self._request("POST", "/api/organizers/tags", json={"name": name})

    async def get_tag(self, tag_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/organizers/tags/{tag_id}")

    async def update_tag(self, tag_id: str, name: str) -> dict[str, Any]:
        return await self._request("PUT", f"/api/organizers/tags/{tag_id}", json={"name": name})

    async def delete_tag(self, tag_id: str) -> None:
        await self._request("DELETE", f"/api/organizers/tags/{tag_id}")

    async def get_or_create_tag(self, name: str) -> dict[str, Any]:
        """Return existing tag by name (case-insensitive) or create it."""
        result = await self.list_tags()
        items = result.get("items") if isinstance(result, dict) else result
        for tag in items or []:
            if isinstance(tag, dict) and tag.get("name", "").lower() == name.lower():
                return tag
        return await self.create_tag(name)

    # ---- Organizers: Categories --------------------------------------------------

    async def list_categories(self, *, per_page: int = 1000) -> dict[str, Any]:
        return await self._request(
            "GET", "/api/organizers/categories", params={"perPage": per_page}
        )

    async def create_category(self, name: str) -> dict[str, Any]:
        return await self._request("POST", "/api/organizers/categories", json={"name": name})

    async def get_or_create_category(self, name: str) -> dict[str, Any]:
        """Return existing category by name (case-insensitive) or create it."""
        result = await self.list_categories()
        items = result.get("items") if isinstance(result, dict) else result
        for cat in items or []:
            if isinstance(cat, dict) and cat.get("name", "").lower() == name.lower():
                return cat
        return await self.create_category(name)

    # ---- Organizers: Tools (equipment) ------------------------------------------

    async def list_recipe_tools(self, *, per_page: int = 1000) -> dict[str, Any]:
        return await self._request("GET", "/api/organizers/tools", params={"perPage": per_page})

    async def create_recipe_tool(self, name: str) -> dict[str, Any]:
        return await self._request("POST", "/api/organizers/tools", json={"name": name})

    async def get_or_create_recipe_tool(self, name: str) -> dict[str, Any]:
        """Return existing tool by name (case-insensitive) or create it."""
        result = await self.list_recipe_tools()
        items = result.get("items") if isinstance(result, dict) else result
        for tool in items or []:
            if isinstance(tool, dict) and tool.get("name", "").lower() == name.lower():
                return tool
        return await self.create_recipe_tool(name)

    # ---- Images ------------------------------------------------------------------

    _EXT_MAP = {"image/png": "png", "image/gif": "gif", "image/webp": "webp"}

    async def _upload_recipe_image(self, slug: str, content: bytes, content_type: str) -> Any:
        ext = self._EXT_MAP.get(content_type, "jpg")
        response = await self._client.put(
            f"/api/recipes/{slug}/image",
            files={"image": (f"image.{ext}", content, content_type)},
            data={"extension": ext},
        )
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("detail") if isinstance(payload, dict) else payload
            except ValueError:
                payload = response.text
                detail = response.text
            raise MealieError(response.status_code, str(detail), payload)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def upload_recipe_image_from_url(self, slug: str, url: str) -> Any:
        """Download an image from *url* and upload it to the recipe."""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as dl:
            resp = await dl.get(url)
            if resp.status_code >= 400:
                raise MealieError(resp.status_code, f"Failed to download image from {url}")
            content = resp.content
            content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return await self._upload_recipe_image(slug, content, content_type)

    async def upload_recipe_image_from_base64(
        self, slug: str, b64_data: str, content_type: str
    ) -> Any:
        """Decode a base64 image string and upload it to the recipe."""
        import base64

        try:
            content = base64.b64decode(b64_data, validate=True)
            if not content:
                raise ValueError("empty image")
        except Exception as exc:
            raise MealieError(400, f"Invalid base64 data: {exc}") from exc
        return await self._upload_recipe_image(slug, content, content_type)

    async def delete_recipe_image(self, slug: str) -> None:
        await self._request("DELETE", f"/api/recipes/{slug}/image")

    # ---- Shopping lists ----------------------------------------------------------

    async def create_shopping_list(self, name: str) -> dict[str, Any]:
        return await self._request("POST", "/api/households/shopping/lists", json={"name": name})

    async def list_shopping_lists(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/households/shopping/lists",
            params={"perPage": 1000},
        )

    async def list_shopping_recipe_references(self, list_id: str) -> list[dict[str, Any]]:
        result = await self._request("GET", f"/api/households/shopping/lists/{list_id}")
        if not isinstance(result, dict) or not isinstance(result.get("recipeReferences"), list):
            raise MealieError(500, "Unexpected shopping list response", result)
        return result["recipeReferences"]

    async def add_recipe_to_shopping_list(
        self, list_id: str, recipe_id: str, *, factor: float = 1
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
            json={"recipeIncrementQuantity": factor},
        )

    async def add_recipes_to_shopping_list(
        self, list_id: str, recipes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/households/shopping/lists/{list_id}/recipe", json=recipes
        )

    async def remove_recipe_from_shopping_list(
        self, list_id: str, recipe_id: str, *, factor: float = 1
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}/delete",
            json={"recipeDecrementQuantity": factor},
        )

    async def get_shopping_list(self, list_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/households/shopping/lists/{list_id}")

    async def rename_shopping_list(self, list_id: str, name: str) -> dict[str, Any]:
        current = await self.get_shopping_list(list_id)
        if not isinstance(current, dict):
            raise MealieError(500, "Unexpected shopping list response", current)
        return await self._request(
            "PUT", f"/api/households/shopping/lists/{list_id}", json={**current, "name": name}
        )

    async def delete_shopping_list(self, list_id: str) -> None:
        await self._request("DELETE", f"/api/households/shopping/lists/{list_id}")

    async def list_shopping_list_items(self, list_id: str) -> dict[str, Any]:
        result = await self._request("GET", f"/api/households/shopping/lists/{list_id}")
        if not isinstance(result, dict) or not isinstance(result.get("listItems"), list):
            raise MealieError(500, "Unexpected shopping list response", result)
        return {"items": result["listItems"]}

    async def add_shopping_list_item(
        self,
        *,
        list_id: str,
        note: str,
        quantity: float | None = None,
        food_id: str | None = None,
        unit_id: str | None = None,
    ) -> dict[str, Any]:
        body = {"shoppingListId": list_id, "note": note, "checked": False}
        if quantity is not None:
            body["quantity"] = quantity
        if food_id is not None:
            body["foodId"] = food_id
        if unit_id is not None:
            body["unitId"] = unit_id
        result = await self._request("POST", "/api/households/shopping/items", json=body)
        if isinstance(result, dict):
            for key in ("createdItems", "updatedItems"):
                items = result.get(key)
                if isinstance(items, list) and items and isinstance(items[0], dict):
                    return items[0]
        raise MealieError(500, "Unexpected shopping item response", result)

    async def get_shopping_list_item(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/households/shopping/items/{item_id}")

    async def update_shopping_list_item(
        self, item_id: str, patch: dict[str, Any]
    ) -> dict[str, Any]:
        current = await self.get_shopping_list_item(item_id)
        if not isinstance(current, dict):
            raise MealieError(500, "Unexpected shopping item response", current)
        return await self._request(
            "PUT", f"/api/households/shopping/items/{item_id}", json={**current, **patch}
        )

    async def check_off_shopping_item(
        self, item_id: str, *, checked: bool = True
    ) -> dict[str, Any]:
        """Toggle the checked state of a shopping list item."""
        return await self.update_shopping_list_item(item_id, {"checked": checked})

    async def delete_shopping_list_item(self, item_id: str) -> None:
        await self._request("DELETE", f"/api/households/shopping/items/{item_id}")

    # ---- Foods -------------------------------------------------------------------

    async def list_foods(self, *, query: str | None = None, per_page: int = 50) -> dict[str, Any]:
        params: dict[str, Any] = {"perPage": per_page}
        if query:
            params["search"] = query
        return await self._request("GET", "/api/foods", params=params)

    async def list_units(self, *, query: str | None = None, per_page: int = 50) -> dict[str, Any]:
        return await self._request(
            "GET", "/api/units", params={"search": query, "perPage": per_page}
        )

    async def resolve_ingredient_entity(
        self,
        kind: str,
        name: str,
        *,
        create_missing: bool = False,
        confirmed_similar_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Reuse exact catalog entries; suggest similar ones before creation."""
        if kind not in {"foods", "units"}:
            raise ValueError("Only foods and units can be resolved")
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            listing = await self._request(
                "GET", f"/api/{kind}", params={"perPage": 1000, "page": page}
            )
            if not isinstance(listing, dict) or not isinstance(listing.get("items"), list):
                raise MealieError(500, f"Unexpected {kind} listing", listing)
            items.extend(listing["items"])
            if page >= listing.get("totalPages", 1):
                break
            page += 1
        for item in items:
            names = [item.get("name", ""), item.get("abbreviation", "")]
            names += [alias.get("name", "") for alias in item.get("aliases") or []]
            if any(candidate.casefold() == name.casefold() for candidate in names):
                return item
        similar = [
            item
            for item in items
            if SequenceMatcher(None, name.casefold(), (item.get("name") or "").casefold()).ratio()
            >= 0.7
        ]
        if not create_missing or {item["id"] for item in similar} != set(
            confirmed_similar_ids or []
        ):
            candidates = ", ".join(f"{item['name']} ({item['id']})" for item in similar[:5])
            raise ValueError(
                f"Unknown {kind} entry '{name}'. Candidates: {candidates or 'none'}. "
                "Select an existing name, or confirm all candidate IDs with "
                "create_missing=true and confirmed_similar_ids."
            )
        created = await self._request("POST", f"/api/{kind}", json={"name": name})
        if not isinstance(created, dict) or not created.get("id"):
            raise MealieError(500, f"Unexpected response creating {kind}: {name}", created)
        return created

    # ---- Cookbooks ---------------------------------------------------------------

    async def list_cookbooks(self) -> dict[str, Any]:
        return await self._request("GET", "/api/households/cookbooks", params={"perPage": 1000})

    async def create_cookbook(
        self,
        name: str,
        *,
        description: str = "",
        public: bool = False,
        query_filter_string: str = "",
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/api/households/cookbooks",
            json={
                "name": name,
                "description": description,
                "public": public,
                "queryFilterString": query_filter_string,
            },
        )

    async def get_cookbook(self, cookbook_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/households/cookbooks/{cookbook_id}")

    async def update_cookbook(self, cookbook_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        current = await self.get_cookbook(cookbook_id)
        if not isinstance(current, dict):
            raise MealieError(500, "Unexpected cookbook response", current)
        return await self._request(
            "PUT", f"/api/households/cookbooks/{cookbook_id}", json={**current, **patch}
        )

    async def delete_cookbook(self, cookbook_id: str) -> None:
        await self._request("DELETE", f"/api/households/cookbooks/{cookbook_id}")
