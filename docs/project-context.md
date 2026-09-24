# Projektkontext

**Senast verifierad:** 2026-09-24

## Ansvar

Repositoryt innehåller ett Python-baserat verktyg för Docker-uppdatering och backup.

Huvudkomponenter:

- `src/entrypoint.py` — process-/scheduleringång
- `src/run.py` — orkestrerar vald körning
- `src/docker_update.py` — Docker update/recreation
- `src/backup.py` — backupflöde
- `src/config.py` — runtimekonfiguration
- `src/report.py` och `src/github_report.py` — status/rapportering

## Modes

`MODE` accepterar:

- `update`
- `backup`
- `both` (default)

Ogiltiga värden avvisas i `Config`.

## Updatevägar

### Compose

När `COMPOSE_FILE` är satt används Docker Compose. Valfri `COMPOSE_ENV_FILE` används om filen finns.

### Direkt Docker

Utan Compose-fil arbetar verktyget mot körande containers via Docker CLI/socket och recreatar containers vars running image-ID inte matchar den nyss pullade imagen.

## Dry-run

`DRY_RUN=true` ska beskriva avsedda uppdateringsoperationer utan att pull/up/recreate/prune muterar runtime.

Dry-run är en säkerhets- och driftinvariant och ska omfattas av tester när updatealgoritmen ändras.

## Backup

Backupkonfiguration läses från `/config/backup.conf` när filen finns.

Verifierade defaults i `Config`:

- source: `/data`
- destination: `gdrive:backups`
- katalognamn: `backup` / `backups`

Konfigurationen kan ändra source, destination och katalogurval.

## Scheduler/status

Default cron schedule är `0 3 * * *`. Statusfilen är `/config/status.json`.

## Container-recreation

Socket-läget bygger ett nytt `docker run` från `docker inspect` och bevarar bland annat relevanta:

- restart policy,
- network mode,
- user/workdir,
- environment,
- binds/volumes/tmpfs,
- port mappings,
- labels,
- capabilities/security options,
- devices/DNS,
- resource limits,
- log driver,
- stop signal,
- entrypoint/cmd.

Recreation använder ett backupnamn för originalcontainern och har best-effort rollback om den nya containern inte kan startas korrekt.

## Dokumentationsgräns

Repo-specifik implementation och runtime dokumenteras här. Organisationsgemensam CI/governance hör inte hemma som current-state i denna fil.

## Uppdateringskontrakt

Uppdatera dokumentationen vid förändringar i modes, updatealgoritm, inspect-preservation, rollback, backupmodell, scheduler eller statusrapportering.
