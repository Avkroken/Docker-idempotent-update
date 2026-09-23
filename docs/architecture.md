# Arkitektur

## Flöde

```text
cron / entrypoint
      |
      v
   src.run
   /    \
  v      v
update  backup
  |      |
Docker  rclone
  \      /
   v    v
  report + status.json
```

## Komponenter

- `src/entrypoint.py` — etablerar schemalagd körning från `CRON_SCHEDULE`.
- `src/run.py` — orkestrerar update, backup, rapport och status.
- `src/config.py` — validerar och exponerar runtime-konfiguration.
- `src/docker_update.py` — Compose- och socket-baserad containeruppdatering samt rollback.
- `src/backup.py` — rclone-baserad backup.
- `src/report.py` — e-postrapport via msmtp när konfigurerat.
- `src/github_report.py` — felrapportering för okontrollerade körfel.
- `tests/` — beteendetester för kritiska uppdateringsvägar.

## Failure model

Ett ohanterat fel i huvudkörningen loggas, rapporteras via GitHub-integrationen och återkastas. Backupfel samlas separat så att rapporten kan visa partiella fel. Compose-pull har retries; direct-container recreation har rollback till den tidigare containern när ersättaren inte kan skapas eller inte förblir körande.

## State

Canonical runtime-state ligger i Docker/Compose och backupmålet. `/config/status.json` är senaste reducerade körstatus, inte en separat source of truth.
