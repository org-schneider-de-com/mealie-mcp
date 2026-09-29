"""Apply a separately approved selection of legacy ingredient fixes."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from mealie_mcp.client import MealieClient
from mealie_mcp.migration import apply_selected_recipe


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="Required to enable API writes")
    args = parser.parse_args()
    if not args.apply:
        parser.error("No writes without --apply and a reviewed manifest")
    selections = json.loads(args.approved_manifest.read_text())
    if not isinstance(selections, dict):
        parser.error("Manifest must map recipe slugs to selected ingredient rows")
    results: list[dict[str, object]] = []
    async with MealieClient(os.environ["MEALIE_URL"], os.environ["MEALIE_API_TOKEN"]) as client:
        for slug, rows in selections.items():
            try:
                await apply_selected_recipe(client, slug, rows)
                results.append({"slug": slug, "updated": len(rows)})
            except Exception as exc:
                results.append({"slug": slug, "skipped": len(rows), "error": str(exc)})
    args.report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
