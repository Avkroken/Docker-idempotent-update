# Plex Clear Watchlist

[![CI](https://github.com/Avkroken/Docker-idempotent-update/actions/workflows/ci.yml/badge.svg)](https://github.com/Avkroken/Docker-idempotent-update/actions/workflows/ci.yml)
[![Image](https://ghcr-badge.egpl.dev/avkroken/plex-clear-watchlist/size?color=blue&label=image)](https://github.com/orgs/Avkroken/packages/container/package/plex-clear-watchlist)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Delete all items from your Plex Watchlist via the Plex API.

## Setup

Get your Plex token from plex.tv → Settings → Account → Security.

## Docker Compose

```bash
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --dry-run
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --limit 10
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --keep 5
```

Or put `PLEX_TOKEN=your-token` in a `.env` file and just run:

```bash
docker compose run --rm plex-clear-watchlist --dry-run
```

## Docker

```bash
docker run --rm -e PLEX_TOKEN=your-token ghcr.io/avkroken/plex-clear-watchlist --dry-run
```

## Python

```bash
export PLEX_TOKEN="your-token-here"
pip3 install -r requirements.txt
python3 plex_clear_watchlist.py --dry-run
```

## Options

| Flag | Description |
|---|---|
| `--dry-run` | Show what would be deleted without deleting |
| `--limit N` | Delete at most N items |
| `--keep N` | Keep the N most recently added items |