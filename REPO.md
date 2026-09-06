# REPO.md

Förrådet sköter Docker-underhåll: hämtar images, återskapar ändrade containers, synkroniserar backups och rapporterar relevanta förändringar. `plex-clear-watchlist/` är ett separat engångsverktyg för Plex-underhåll.

## Invarians

- Hemligheter kommer från miljövariabler och får inte hårdkodas eller exponeras i rapporter eller loggar.
- Föredra Python-standardbiblioteket och befintliga projektmekanismer framför nya beroenden.
- Bevara redigering av känslig information i felrapporteringen i `src/github_report.py`.
- `plex-clear-watchlist --dry-run` får inte ha sidoeffekter.
- `PLEX_TOKEN` ska hållas utanför image och förråd.

## Validering

Kör relevanta tester för ändrad Python-kod. Vid containerändringar, validera med Docker/Compose när det är relevant.
