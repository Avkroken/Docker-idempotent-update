# Docker-idempotent-update

Docker-idempotent-update automatiserar säkra Docker-uppdateringar och backup i två körlägen: Docker Compose eller direkt mot redan körande containers. Verktyget försöker bevara befintlig runtimekonfiguration vid container-recreation och rapporterar vad som faktiskt ändrades.

## Snabbstart för utveckling

```bash
python3 -m compileall -q src plex-clear-watchlist
python3 -m pytest -q
bash tests/test_pr_changes.sh
```

## Dokumentation

Börja i **[dokumentationsöversikten](docs/index.md)**.

- [Projektkontext](docs/project-context.md) — modes, konfiguration och invariants
- [Arkitektur](docs/architecture.md) — update-/backupflöden och rollbackmodell
- [Drift](docs/operations.md) — verifiering, dry-run, scheduler och incidenter
- [SECURITY.md](SECURITY.md) — säkerhetsrapportering

README är en ingång; detaljerad teknisk information ligger under `docs/`.

## Viktiga invariants

- `DRY_RUN=true` får inte mutera containers.
- Compose-läget och socket-läget har olika updatealgoritmer.
- socket-recreation måste bevara relevant inspect-derived runtimekonfiguration och återställa originalet om recreation misslyckas.
