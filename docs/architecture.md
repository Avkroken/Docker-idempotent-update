# Arkitektur

## Översikt

```text
entrypoint.py
    |
    v
  run.py
  |   |
  |   +----------------------+
  v                          v
docker_update.py          backup.py
  |                          |
  +--> Docker CLI            +--> backup source
  |      |
  |      +--> Compose            --> destination
  |      +--> socket mode
  |
  +--> report/status
```

## Updatefasens gemensamma modell

`run_update()` tar en Docker-processsnapshot före och efter körningen. Först därefter beräknas förändringen.

Prune körs endast när:

- förändringar faktiskt identifierades, och
- körningen inte är dry-run.

## Compose-läge

Flödet är:

1. `docker compose config --services`
2. snapshot av service → image-ID
3. sekventiell `pull` per service
4. upp till tre pullförsök per service
5. `up -d --remove-orphans`
6. ny image snapshot
7. jämförelse för att identifiera uppdaterade services

Att pulla sekventiellt begränsar felpåverkan och gör retries service-specifika.

## Socket-läge

Flödet är:

1. lista images från körande containers;
2. pulla varje unik image;
3. jämför körande container image-ID med aktuell image;
4. inspektera containers som behöver recreation;
5. bygg ett nytt `docker run` med relevanta runtime options;
6. stoppa och döp om originalet;
7. starta ersättaren;
8. återställ originalet best-effort om recreation misslyckas.

## Runtime preservation

`_append_runtime_options()` bevarar runtimeegenskaper från `docker inspect`. När ny Docker-funktionalitet börjar användas måste man uttryckligen bedöma om ytterligare HostConfig/Config-fält behöver bevaras.

Det är inte säkert att anta att en container kan recreatas enbart från image + ports.

## Processkonfiguration

Entrypoint och Cmd behöver återges i rätt ordning efter imageargumentet. Förändringar i denna logik ska ha regressionstester.

## Rollback

Originalcontainern byter namn innan ersättaren tar originalnamnet. Vid fel försöker `_restore_original()`:

1. ta bort den misslyckade ersättaren;
2. döpa tillbaka backupcontainern;
3. starta originalet.

Rollback är best-effort: fel ska loggas tydligt så att operatören kan se om automatisk återställning inte lyckades.

## Backupgräns

Backup är ett separat flöde från container update. `MODE` avgör om update, backup eller båda ska köras.

## Failure model

- `docker ps`-fel är hårda fel eftersom current state inte kan etableras.
- enskilda image pulls kan loggas som failures enligt respektive updateväg.
- recreationfel ska inte lämna originalcontainern tyst borttagen.
- dry-run får inte göra mutationsoperationer.
