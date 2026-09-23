# Docker-idempotent-update

Automatiserat underhåll för Docker-miljöer. Projektet kan uppdatera körande containers, synkronisera backupkataloger med rclone och rapportera förändringar/fel.

## Vad tjänsten gör

- kör i läget `update`, `backup` eller `both`,
- stöder Docker Compose och direkt Docker-socket-baserad uppdatering,
- har `DRY_RUN=true` för verifiering utan mutation,
- försöker bevara relevanta runtime-inställningar när en fristående container återskapas,
- håller den gamla containern som rollback-kandidat tills ersättaren verifierats som körande,
- synkroniserar definierade backupkataloger med rclone,
- skriver senaste körstatus till `/config/status.json`,
- kan skicka e-postrapport när containerstate ändrats eller backup misslyckats.

## Dokumentation

- [Projektkontext](docs/project-context.md)
- [Arkitektur](docs/architecture.md)
- [Drift](docs/operations.md)
- [Avkrokens dokumentationsstandard](https://github.com/Avkroken/.github/blob/main/docs/documentation-standard.md)

## Utveckling och verifiering

Koden ligger i `src/` och tester i `tests/`. Repositoryts CI använder Python, pytest och flake8.

Verifiera alltid ändringar mot relevanta tester innan merge. Ändringar i container-recreation måste även bedömas mot rollback-flödet och inspect-baserad återuppbyggnad av runtime-optioner.

## Issues och säkerhet

Använd GitHub Issues för reproducerbara fel eller förbättringsförslag. Rapportera inte sårbarheter eller hemligheter i publika issues; följ [SECURITY.md](SECURITY.md) för privat rapportering.
