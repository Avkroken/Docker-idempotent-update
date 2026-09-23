# Projektkontext

**Senast verifierad:** 2026-09-23

## Ansvar

`Docker-idempotent-update` kör återkommande Docker-underhåll och backup. Den aktuella Python-entrypointen är `src.run`.

Körningen:

1. läser runtime-konfiguration via `Config`,
2. utför containeruppdatering när `MODE` är `update` eller `both`,
3. utför rclone-backup när `MODE` är `backup` eller `both`,
4. skickar rapport när det finns relevanta förändringar/fel och e-post är konfigurerad,
5. skriver reducerad status till `/config/status.json`.

## Runtime-konfiguration

Verifierade miljövariabler:

- `MODE`: `update`, `backup` eller `both` (default `both`),
- `DRY_RUN`: `true` för icke-muterande körning,
- `EMAIL_TO`: mottagare för rapporter,
- `CRON_SCHEDULE`: schema; default `0 3 * * *`,
- `COMPOSE_FILE`: aktiverar Compose-vägen,
- `COMPOSE_ENV_FILE`: valfri env-fil för Compose.

Backupkonfiguration kan kompletteras via `/config/backup.conf` med `RCLONE_SRC`, `RCLONE_DST` och `BACKUP_DIRS`.

## Uppdateringsmodeller

### Docker Compose

När `COMPOSE_FILE` är satt:

- tjänster läses via `docker compose config --services`,
- images pullas sekventiellt med högst tre försök per service,
- `docker compose up -d --remove-orphans` applicerar state,
- före/efter-image-ID jämförs för att rapportera faktiskt uppdaterade services.

### Direkt Docker

Utan `COMPOSE_FILE`:

- images för körande containers pullas,
- container image-ID jämförs med senaste lokala image-ID,
- ändrade containers återskapas från `docker inspect`-state,
- originalcontainern stoppas och byter till ett temporärt backupnamn,
- ersättaren måste verifieras som `Running` innan backupcontainern tas bort,
- misslyckad recreation försöker återställa originalcontainern.

## Backup

`src/backup.py` söker backupkataloger under den konfigurerade källan och kör `rclone sync` med retries. Misslyckade kataloger samlas till körresultatet.

## Säkerhets- och driftsinvarianter

- `DRY_RUN` får inte göra mutationer.
- Container-recreation får inte ta bort rollback-kandidaten innan ersättaren är verifierad som körande.
- Runtime-optioner som mounts, ports, restart policy, capabilities och resource limits får inte tappas av misstag.
- Secrets hör hemma i runtime-konfiguration och ska inte dokumenteras med värden.
- Docker-socket-access är en stark host-behörighet och ska inte utökas utanför det faktiska underhållsbehovet.

## Uppdateringskontrakt

Uppdatera denna fil när körningsmodell, rollback, runtime-konfiguration, backupmodell eller rapportering ändras.
