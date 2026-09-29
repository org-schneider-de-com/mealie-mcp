"""Read-only ingredient migration preview for ZIP exports or a Mealie instance."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from mealie_mcp.client import MealieClient
from mealie_mcp.migration import preview_all_recipes, preview_recipe, read_recipe_export


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="*", type=Path, help="Mealie recipe ZIP exports")
    parser.add_argument("--live", action="store_true", help="Read every recipe from Mealie")
    parser.add_argument("--output", type=Path, required=True, help="JSON preview path")
    args = parser.parse_args()
    if args.live == bool(args.exports):
        parser.error("Choose either ZIP exports or --live")
    if args.live:
        url, token = os.environ["MEALIE_URL"], os.environ["MEALIE_API_TOKEN"]
        async with MealieClient(url, token) as client:
            report = await preview_all_recipes(client)
    else:
        report = [preview_recipe(read_recipe_export(path)) for path in args.exports]
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
