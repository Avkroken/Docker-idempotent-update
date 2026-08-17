# docker-idempotent-update — AI Agent Guide

Daily Docker host maintenance in a single container. Pulls updated images, recreates changed containers, syncs backups via rclone, and sends an email summary only when something happened.

## Tech Stack

- Python 3.13
- Docker (socket or Compose)
- rclone for backups
- msmtp for email
- Internal cron daemon

## File Overview

```
src/entrypoint.py   # Validates config, registers cron, execs crond
src/run.py          # Main daily job (update + backup + report + status)
src/docker_update.py# Docker pull + restart logic
src/backup.py       # Rclone sync logic
src/report.py       # Assembles and sends email summary
src/config.py       # Config class — reads env vars and backup.conf
backup.conf.template
msmtprc.template
```

## Conventions

- All secrets via environment variables — never hardcoded
- No third-party Python packages — stdlib only
- Test changes with `docker compose run --rm` before committing
- An unhandled exception in `run.py`'s `main()` calls
  `report_error_to_github()` (`src/github_report.py`, stdlib-only/urllib
  per the rule above) — best-effort, opens a `@claude`-tagged GitHub issue
  with secrets/emails/paths redacted if `GITHUB_ERROR_REPORT_TOKEN` is
  set, no-ops otherwise

## Versioner: flytande som standard

Pinna aldrig ett versionsnummer, en release-flavor eller en digest om det inte
är ett absolut måste. En pinne som ingen revideras sitter kvar långt efter att
den blivit fel: `debian:trixie-slim` följer inte Debians nästa stable, och en
basimage vars OS-generation ligger i taggnamnet kan Dependabot aldrig flytta —
den bumpar bara siffran inom samma taggfamilj.

Gäller basimager, pip- och npm-beroenden, och allt annat med en version.

**Om en pinne ändå är nödvändig** ska den dokumenteras på plats, i den här
filen och i README — med vad som är pinnat, varför, och vad som måste
kontrolleras för att kunna släppa den igen. En odokumenterad pinne är en bugg
som väntar.

### Nuvarande undantag

- **GitHub Actions pinnas till commit-SHA.** En tagg som `@v4` är föränderlig
  och kan pekas om till annan kod; en SHA kan den inte. Det är en
  leverantörskedjekontroll, inte versionshantering, och Dependabot bumpar dem
  ändå automatiskt.

## Allowed
- Committa på dev
- Modify code
- Run tests
- Open PRs

## Forbidden
- Push directly to main/master
- Merge PRs
- Skapa eller ta bort grenar (rulesetet blockerar det)
- Disable workflows
- Modify secrets
- Change GitHub org settings

## Requirements
- All tests must pass
- Keep PRs focused
- Never include unrelated changes
- Never commit credentials
- Never force push

## Svarsformat

Regeluppsättningen kommer från plugin:et `i-have-adhd`. Den laddas inte i
alla sessioner (t.ex. inte i Claude Code på webben), så den står här —
det här är källan som gäller oavsett var agenten kör.

Form:

- Led med åtgärden eller kommandot, inte med bakgrunden
- Numrera flerstegsprocesser, ett avgränsat steg per rad
- Max fem punkter per lista
- Hoppa över inledningar, sammanfattningar och avslutningsfraser
- Långa förklaringar bara på begäran

Innehåll:

- Säg uttryckligen vad som är gjort och vad som återstår
- Ange konkreta tidsuppskattningar
- Visa vad som fungerar efter en ändring, inte bara att den är gjord
- Vid fel: var, varför och hur det åtgärdas — kortfattat
- Avsluta med ett nästa steg som tar under två minuter
