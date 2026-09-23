# Drift

## Före ändring

Verifiera:

- vilket `MODE` som används,
- om deploymenten använder `COMPOSE_FILE` eller direkt Docker-socket,
- backupkälla/-mål,
- om e-postrapportering är konfigurerad,
- relevanta tester för ändrad kodväg.

## Säker verifiering

Använd `DRY_RUN=true` när en förändring först ska observeras utan container- eller backupmutation.

För container-recreation ska tester särskilt täcka:

- mounts och volumes,
- portbindningar,
- restart policy,
- network mode,
- capabilities/security options,
- resource limits,
- entrypoint/Cmd,
- rollback när ny container inte startar.

## Scheduler

`CRON_SCHEDULE` styr den återkommande körningen. Default är `0 3 * * *`. Ändra inte produktionsschema enbart som bieffekt av kod- eller dokumentationsarbete.

## Backup

Backup använder `rclone sync`. Ett fel efter retries markeras i körresultatet. Kontrollera destination och scope innan en faktisk backupkörning eftersom sync-semantiken kan ta bort destinationsobjekt som inte längre finns i källan.

## Status och rapportering

Senaste reducerade state skrivs till `/config/status.json`. E-post skickas endast när mottagare och msmtp-konfiguration finns och det finns containerförändringar eller backupfel.

## Incidentprincip

Vid osäker containerstate: prioritera bevarad/återställd originalcontainer framför fortsatt automatisk recreation. Ta inte bort rollback-kandidater manuellt innan aktuell containerstate är verifierad.
