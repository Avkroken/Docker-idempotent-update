# AGENTS.md

- Läs [docs/project-context.md](docs/project-context.md), [docs/architecture.md](docs/architecture.md) och [docs/operations.md](docs/operations.md) före materiella ändringar.
- Följ Avkrokens centrala engineering- och dokumentationsstandard i `Avkroken/.github`.
- Arbeta i separat gren enligt `{agent}/{feature}/{YYYY-MM-DD}/{HH-mm}-{id}`.
- Förändringar i `src/docker_update.py` måste bevara rollback och verifierad recreation.
- Använd `DRY_RUN` för icke-muterande driftsverifiering när relevant.
- Utöka inte Docker-socket-, host- eller credentialbehörigheter för bekvämlighet.
- Lägg aldrig secrets eller credential-värden i repository eller dokumentation.
