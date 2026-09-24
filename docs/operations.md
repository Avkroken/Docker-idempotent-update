# Drift

## Lokal verifiering

```bash
python3 -m compileall -q src plex-clear-watchlist
python3 -m pytest -q
bash tests/test_pr_changes.sh
```

`test_pr_changes.sh` verifierar även viktiga workflowinvariants och att Actions används med immutabla revisionsreferenser där testet kräver det.

## Dry-run

Sätt:

```text
DRY_RUN=true
```

Dry-run ska användas när en ändring i updatealgoritmen behöver valideras utan container mutation.

Verifiera att output beskriver avsedda operationer och att inga `pull`, `up`, recreation- eller prune-effekter sker.

## Modes

```text
MODE=update
MODE=backup
MODE=both
```

Default är `both`.

## Compose-drift

När `COMPOSE_FILE` används:

1. kontrollera att filen kan renderas med `docker compose config`;
2. kontrollera serviceslistan;
3. kontrollera eventuell env-fil;
4. kör dry-run vid ändrad updatekod;
5. följ faktisk pull/up-körning och slutrapport.

## Socket-drift

Socket-läge har större ansvar för att rekonstruera runtimekonfiguration.

Efter ändringar i recreationlogiken ska tester täcka minst:

- environment,
- mounts,
- ports,
- restart/network,
- entrypoint/cmd,
- resource/security options som berörs,
- rollback vid startfel.

## Backup

`/config/backup.conf` kan ange backup source/destination och katalogurval.

Verifiera alltid:

- sourcepath,
- destination,
- credential/config för backupverktyget,
- att exkludering/urval ger förväntat dataset.

## Scheduler

Default är `0 3 * * *` via `CRON_SCHEDULE`.

När schedulerlogik ändras ska man skilja på:

- schemaläggning,
- själva update-/backupkörningen,
- statusrapportering.

## Status och rapportering

Statusfilen ligger i `/config/status.json`. Rapportering får inte maskera det ursprungliga update-/backupfelet.

## Incidenter

### Container startar inte efter recreation

1. kontrollera loggad `docker run`-relaterad failure;
2. verifiera om originalcontainern återställdes;
3. jämför inspect-derived options med originalet;
4. ändra inte eller radera backupcontainern innan state är förstått.

### Compose pull misslyckas

Kontrollera vilken service som misslyckades och om retries uttömdes. Undvik att behandla övriga services som automatiskt felaktiga.

### Docker state kan inte läsas

Om `docker ps` inte kan köras ska update inte fortsätta på antagen state.

## Dokumentationsunderhåll

När update-/backupbeteende ändras ska README hållas kort och dessa driftdetaljer uppdateras här.
