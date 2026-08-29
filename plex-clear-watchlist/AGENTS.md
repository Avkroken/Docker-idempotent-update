# plex_clear_watchlist — AI Agent Guide

Repositoryövergripande arbets-, review-, säkerhets-, eskalerings- och mergepolicy finns i `/AGENTS.md` och gäller även här. Den här filen lägger endast till regler för `plex-clear-watchlist/`.

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

```text
plex_clear_watchlist.py     # Main script
requirements.txt            # Python deps
Dockerfile
docker-compose.yml
```

## Conventions

- `PLEX_TOKEN` is always provided via environment variable — never hardcoded.
- `--dry-run` must be safe to run without side effects.
- Keep the script simple and single-purpose.

## Subtree-specifik branchregel

- Kodändringar för detta subtree överlämnas på `dev` och ändringsförslag öppnas från `dev` till repositoryts standardgren.
- Starta inte en ny koduppgift medan ett ändringsförslag från `dev` är öppet; slutför eller stäng det först.
- Skapa ändringsförslag som klara för granskning, aldrig som utkast.
- Alla tester måste godkännas och varje ändringsförslag ska vara avgränsat till en uppgift.
- Ta aldrig med orelaterade ändringar, credentials eller andra hemligheter.
- Tvinga aldrig igenom en push, radera grenar, stäng av workflows eller ändra GitHub-organisationsinställningar.

Mergebeslut, review-gates, auto-merge och tillåten merge-metod styrs enbart av root `/AGENTS.md` tillsammans med repositoryts live-konfiguration.
