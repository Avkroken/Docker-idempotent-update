# Dokumentation

Navigationssida för Docker-idempotent-update.

## Hitta rätt

| Fråga | Dokument |
| --- | --- |
| Vilka modes och configvärden finns? | [Projektkontext](project-context.md) |
| Hur fungerar update, recreation, backup och rollback? | [Arkitektur](architecture.md) |
| Hur testar, kör och felsöker jag? | [Drift](operations.md) |
| Hur rapporteras säkerhetsproblem? | [SECURITY.md](../SECURITY.md) |

## Komponenter

```text
src/entrypoint.py
      |
      v
   src/run.py
   /       \
  v         v
update    backup
  |         |
  v         v
docker   rclone
update
```

Updateflödet ligger huvudsakligen i `src/docker_update.py`, konfiguration i `src/config.py`, backup i `src/backup.py` och rapportering i `src/report.py` / `src/github_report.py`.

## Två updatevägar

### Compose

När `COMPOSE_FILE` är satt läses services från Compose-konfigurationen, images snapshotas, services pullas sekventiellt med retries och stacken körs med `up -d --remove-orphans`.

### Docker socket

Utan Compose-fil inspekteras körande containers direkt. Nya images pullas och containers som kör äldre image-ID kan recreatas med inspect-derived runtime options.

## Ändringskarta

- env/config → project-context
- recreation/runtime options → architecture + tests
- backup/rclone → architecture + operations
- scheduler/status/reporting → operations
- CI/workflows → tests och relevant GitHub-dokumentation

## Wiki

Om GitHub Wiki används kan den fungera som navigationsyta för dessa ämnen. Versionsstyrd Markdown här är det tekniska underlaget; repositoryt gör inget antagande om aktuell Wiki-setting.
