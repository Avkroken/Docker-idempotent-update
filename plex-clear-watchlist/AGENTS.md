# plex_clear_watchlist — AI Agent Guide

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

## Tillåtet
- Ändra kod
- Köra tester
- Öppna ändringsförslag från `dev` till standardgrenen

## Förbjudet
- Skicka ändringar direkt till `main` eller `master`
- Radera grenar
- Stänga av arbetsflöden
- Ändra hemligheter
- Ändra inställningar för GitHub-organisationen

## Krav
- Överlämna kodändringar endast på `dev`
- Alla tester måste godkännas
- Håll varje ändringsförslag avgränsat till en uppgift
- Starta inte en ny koduppgift medan ett ändringsförslag från `dev` är öppet; slutför eller stäng det först
- Ta aldrig med orelaterade ändringar
- Överlämna aldrig inloggningsuppgifter eller andra hemligheter till versionshistoriken
- Tvinga aldrig igenom en skickning
- Skapa ändringsförslag som klara för granskning, aldrig som utkast
- Aktivera automatisk sammanfogning med en metod som tillåts av förrådets regler direkt efter att ändringsförslaget skapats
- Automatisk sammanfogning får slutföras först när alla regelkrav och kontrollkörningar har godkänts
- Om automatisk sammanfogning inte kan aktiveras: rapportera det exakta felet
