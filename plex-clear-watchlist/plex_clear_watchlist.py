#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from urllib.parse import quote

# --- Configuration ---
PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "")
if not PLEX_TOKEN:
    print("❌ Error: PLEX_TOKEN environment variable not set", file=sys.stderr)
    print("   Run: export PLEX_TOKEN='your-plex-token'", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://plex.tv"
WATCHLIST_URL = f"{BASE_URL}/api/v2/user/watchlist"
HEADERS = {
    "X-Plex-Token": PLEX_TOKEN,
    "Accept": "application/json"
}
REQUEST_TIMEOUT = 30

# --- Functions ---


def _parse_watchlist_page(data: object, collected_count: int) -> tuple[list[dict], int | None]:
    if not isinstance(data, dict):
        raise requests.RequestException(
            "Plex API-svaret är inte ett JSON-objekt — avbryter fail-closed."
        )

    container = data.get("MediaContainer")
    if not isinstance(container, dict):
        raise requests.RequestException(
            "Plex API-svaret saknar MediaContainer — avbryter fail-closed."
        )

    page_items = container.get("Metadata", [])
    if not isinstance(page_items, list):
        raise requests.RequestException(
            "Plex API-svaret har ogiltig Metadata — avbryter fail-closed."
        )

    raw_total_size = container.get("totalSize")
    if raw_total_size is None:
        return page_items, None

    try:
        total_size = int(raw_total_size)
    except (TypeError, ValueError) as exc:
        raise requests.RequestException(
            "Plex API-svaret har ogiltig totalSize — avbryter fail-closed."
        ) from exc

    if total_size < 0:
        raise requests.RequestException(
            "Plex API-svaret har negativ totalSize — avbryter fail-closed."
        )
    if collected_count + len(page_items) > total_size:
        raise requests.RequestException(
            "Plex API returnerade fler poster än totalSize — avbryter fail-closed."
        )

    return page_items, total_size


def get_watchlist() -> list[dict]:
    """Hämta alla items från Plex Watchlist med paginering."""
    items = []
    page = 1
    page_size = 100

    while True:
        params = {"page": page, "pageSize": page_size, "sort": "addedAt:asc"}
        response = requests.get(WATCHLIST_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code == 404:
            if page == 1:
                return items
            # 404 mitt i pagineringen är sannolikt ett API-glapp, inte en
            # äkta tom lista (den var ju inte tom på föregående sida) - om vi
            # tystbara returnerade `items` här skulle anroparen tro att den
            # FULLSTÄNDIGA listan hämtats och radera bara den delmängden,
            # och lämna resten av watchlisten kvar utan varning.
            raise requests.HTTPError(
                f"Plex API returnerade 404 på sida {page} efter att {len(items)} "
                "item(er) redan samlats in - avbryter istället för att riskera "
                "en ofullständig radering.",
                response=response,
            )
        response.raise_for_status()
        data = response.json()
        page_items, total_size = _parse_watchlist_page(data, len(items))
        items.extend(page_items)

        if total_size is not None:
            if len(items) == total_size:
                break
            if not page_items:
                raise requests.RequestException(
                    f"Plex API tog slut efter {len(items)} av {total_size} poster — "
                    "avbryter istället för att riskera en ofullständig radering."
                )
        elif not page_items:
            break

        page += 1

    return items


def _normalize_rating_key(value: object) -> str | None:
    if value is None:
        return None
    rating_key = str(value).strip()
    return rating_key or None


def delete_from_watchlist(rating_key: str, title: str = "") -> bool:
    """Ta bort ett item från Watchlist."""
    normalized_key = _normalize_rating_key(rating_key)
    if normalized_key is None:
        print("  ⚠️  Failed to delete item: missing ratingKey", file=sys.stderr)
        return False

    url = f"{WATCHLIST_URL}/{quote(normalized_key, safe='')}"
    response = requests.delete(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

    label = title or normalized_key
    if response.status_code in (200, 204):
        print(f"  🗑️  Deleted: {label}")
        return True

    print(f"  ⚠️  Failed to delete {label}: HTTP {response.status_code}", file=sys.stderr)
    return False


def get_item_title(item: dict) -> str:
    """Hämta titel från ett watchlist-item."""
    return item.get("title", item.get("guid", "Unknown"))


def _select_items(items: list[dict], keep: int, limit: int) -> list[dict]:
    selected = items
    if keep > 0 and keep < len(selected):
        selected = selected[:-keep]
    if limit > 0 and limit < len(selected):
        selected = selected[:limit]
    return selected


def _process_items(items: list[dict], dry_run: bool) -> tuple[int, int]:
    success = 0
    failed = 0

    for item in items:
        title = get_item_title(item)
        rating_key = _normalize_rating_key(item.get("ratingKey"))
        if rating_key is None:
            print(f"  ⚠️  Skipping item without ratingKey: {title}", file=sys.stderr)
            failed += 1
            continue

        if dry_run:
            print(f"  [DRY RUN] Would delete: {title}")
            success += 1
        elif delete_from_watchlist(rating_key, title):
            success += 1
        else:
            failed += 1

    return success, failed


def _parse_args():
    parser = argparse.ArgumentParser(description="Clear your Plex Watchlist")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of items to delete (0 = all)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=0,
        help="Keep the N most recent items",
    )
    return parser.parse_args()


def main():
    """Parse arguments and delete items from the Plex Watchlist."""
    args = _parse_args()
    print("📋 Fetching Plex Watchlist...")

    try:
        items = get_watchlist()
    except requests.RequestException as exc:
        print(f"❌ Failed to fetch watchlist: {exc}", file=sys.stderr)
        sys.exit(1)

    total = len(items)
    if total == 0:
        print("✅ Watchlist is already empty!")
        return

    selected = _select_items(items, args.keep, args.limit)
    delete_count = len(selected)
    if args.dry_run:
        print(f"🔍 DRY RUN: {delete_count} of {total} items would be deleted")
    else:
        print(f"🗑️  Deleting {delete_count} of {total} items...")

    success, failed = _process_items(selected, args.dry_run)
    print(f"\n✅ Done! Deleted: {success}, Failed: {failed}")


if __name__ == "__main__":
    main()
