# plex_clear_watchlist — Claude Code Guide

Deletes all items from a Plex Watchlist via the Plex API. Runs as a one-shot Docker container.

## Tech Stack

- Python 3.14
- Plex API (`PLEX_TOKEN`)
- Docker / Docker Compose

## Usage

```bash
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --dry-run
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --limit 10
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --keep 5
```

## Key Files

```
plex_clear_watchlist.py     # Main script
requirements.txt            # Python deps
Dockerfile
docker-compose.yml
```

## Conventions

- `PLEX_TOKEN` is always provided via environment variable — never hardcoded
- `--dry-run` must be safe to run without side effects
- Keep the script simple and single-purpose