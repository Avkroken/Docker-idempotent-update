---
title: "Keeping Recent Items (--keep)"
wiki_page_id: "page-keep"
---

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [plex_clear_watchlist.py](plex_clear_watchlist.py)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [docker-compose.yml](docker-compose.yml)
- [SECURITY.md](SECURITY.md)
</details>

# Keeping Recent Items (--keep)

The "Keep Recent Items" feature, controlled by the `--keep` command-line argument, allows users to selectively purge their Plex Watchlist while preserving a specified number of the most recently added items. This provides a mechanism for partial cleanup rather than a complete wipe of the watchlist.

Sources: [README.md:46](README.md#L46), [plex_clear_watchlist.py:112](plex_clear_watchlist.py#L112)

## Logic and Architecture

The preservation logic is implemented within the `main()` function of the application. It operates by manipulating the list of items retrieved from the Plex API before any deletion commands are issued. 

### Data Flow for Item Preservation

1.  **Retrieval**: The script fetches the entire watchlist using `get_watchlist()`. Items are requested with the parameter `sort=addedAt:asc`, meaning the oldest items appear at the beginning of the list and the newest at the end.
2.  **Filtering**: If the `--keep` flag is provided with a value $N$ (where $N > 0$), the script slices the list to exclude the last $N$ items.
3.  **Execution**: Only the remaining items (the older ones) are passed to the deletion loop.

Sources: [plex_clear_watchlist.py:38](plex_clear_watchlist.py#L38), [plex_clear_watchlist.py:127-128](plex_clear_watchlist.py#L127-L128)

### Logic Flow Diagram
This flowchart illustrates how the `--keep` argument affects the list of items targeted for deletion.

```mermaid
flowchart TD
    A[Start] --> B[Fetch All Items via API]
    B --> C{Is --keep > 0?}
    C -- Yes --> D{Is --keep < Total?}
    D -- Yes --> E[Slice List: items[:-keep]]
    D -- No --> F[Keep Original List]
    C -- No --> F
    E --> G{Is --limit > 0?}
    F --> G
    G -- Yes --> H[Apply Limit Slice]
    G -- No --> I[Proceed to Deletion]
    H --> I
```

Sources: [plex_clear_watchlist.py:124-135](plex_clear_watchlist.py#L124-L135)

## Configuration and Usage

The feature is accessible via various execution methods including Docker, Docker Compose, and direct Python execution.

### Command Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--keep` | Integer | 0 | The number of most recently added items to preserve in the watchlist. |
| `--dry-run` | Boolean | False | When used with `--keep`, it shows which items would be preserved vs deleted. |

Sources: [README.md:46](README.md#L46), [plex_clear_watchlist.py:112](plex_clear_watchlist.py#L112)

### Usage Examples

Users can invoke the keep logic through the following commands:

```bash
# Docker Compose usage to keep the 5 newest items
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --keep 5

# Python usage to keep the 10 newest items
python3 plex_clear_watchlist.py --keep 10
```

Sources: [README.md:28](README.md#L28), [AGENTS.md:14](AGENTS.md#L14), [CLAUDE.md:14](CLAUDE.md#L14)

## Implementation Details

The implementation relies on Python's negative list slicing. Because the Plex API returns items sorted by `addedAt:asc` (oldest first), the items at the end of the list represent the most recent additions.

```python
# plex_clear_watchlist.py:127-128
if args.keep > 0 and args.keep < total:
    items = items[:-args.keep]
```

### Constraints and Edge Cases
- **Validation**: If `--keep` is greater than or equal to the total number of items in the watchlist, the slicing logic is skipped, and no items are deleted (or the limit logic is subsequently applied to the full list).
- **Interoperability**: If both `--keep` and `--limit` are provided, the script first removes the "kept" items from the list and then applies the deletion limit to the remaining pool of older items.

Sources: [plex_clear_watchlist.py:127-132](plex_clear_watchlist.py#L127-L132)

## Summary

The `--keep` feature provides an essential safety and management layer for Plex users. By leveraging the `addedAt` metadata provided by the Plex API, the script ensures that recent interest (manifested as recent watchlist additions) is respected while allowing for the automated removal of older, potentially stale entries.

Sources: [README.md:46](README.md#L46), [plex_clear_watchlist.py:127-128](plex_clear_watchlist.py#L127-L128)
