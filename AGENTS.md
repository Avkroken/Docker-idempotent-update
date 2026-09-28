# AGENTS.md

- Läs [docs/project-context.md](docs/project-context.md), [docs/architecture.md](docs/architecture.md) och [docs/operations.md](docs/operations.md) före materiella ändringar.
- PR-titlar, SemVer-taggar och releasearbete följer [docs/release-standard.md](docs/release-standard.md); inför inte en ny versionsfil utan ett separat versionsarkitekturbeslut.
- Repositoryts egna README, `docs/`, AGENTS-instruktioner och versionerade konfiguration är auktoritativa för repositoryts tekniska arbete.
- Extern GitHub-governance är provider-state. Anta inte organization-scope eller andra org-funktioner utan live-verifiering.
- Arbeta i separat gren enligt `{agent}/{feature}/{YYYY-MM-DD}`.
- Commits ska använda Conventional Commits eller motsvarande tydlig typ, exempelvis `feat:`, `fix:`, `docs:`, `chore:`, `ci:` eller `test:`.
- Läs hela PR-review-state före merge, inklusive kommentarer och trådar som GitHub markerar som `outdated`; verifiera att grundproblemet faktiskt är löst.
- Förändringar i `src/docker_update.py` måste bevara rollback och verifierad recreation.
- Använd `DRY_RUN` för icke-muterande driftsverifiering när relevant.
- Utöka inte Docker-socket-, host- eller credentialbehörigheter för bekvämlighet.
- Lägg aldrig secrets eller credential-värden i repository eller dokumentation.
