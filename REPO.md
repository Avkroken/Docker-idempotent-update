# REPO.md

Förrådet sköter Docker-underhåll: hämtar images, återskapar ändrade containers, synkroniserar backups och rapporterar relevanta förändringar. `plex-clear-watchlist/` är ett separat engångsverktyg för Plex-underhåll.

## Invarians

- Hemligheter kommer från miljövariabler och får inte hårdkodas eller exponeras i rapporter eller loggar.
- Föredra Python-standardbiblioteket och befintliga projektmekanismer framför nya beroenden.
- Bevara redigering av känslig information i felrapporteringen i `src/github_report.py`.
- `plex-clear-watchlist --dry-run` får inte ha sidoeffekter.
- `PLEX_TOKEN` ska hållas utanför image och förråd.

## GitHub-styrning

- Kanonisk arbets- och reviewpolicy finns i `Avkroken/.github/AGENTS.md`.
- `main` skyddas av det ärvda organisationsrulesetet `main` och repo-rulesetet `required-ci`.
- Required checks på `main` är `CI / required` och `docker`.
- `dev` är integrationsgren när ett aktivt `dev-pilot`-ruleset finns. Lägg endast required status checks på `dev` när workflows bevisligen producerar exakt de check-namnen för PR mot `dev`.
- Organisationens CodeRabbit-UI är baslinje. Repository-lokal `.coderabbit.yaml` ska endast användas för uttryckligen repo-specifika overrides.

## Validering

Kör relevanta tester för ändrad Python-kod. Vid containerändringar, validera med Docker/Compose när det är relevant.
