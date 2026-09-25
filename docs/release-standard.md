# Release- och versionsstandard

**Senast verifierad:** 2026-09-25

Det här dokumentet gäller **Avkroken/Docker-idempotent-update**. Repositoryts egna workflows och dokumentation äger release- och containerpubliceringskontraktet.

## Nuvarande versionsmodell

Repositoryt har ingen verifierad canonical package-/appversionsfil på current `main`.

Inför inte `version.txt` eller annan lokal versionfil enbart för releaseautomation.

För versionerade releases används SemVer-taggen som versionsankare:

```text
vMAJOR.MINOR.PATCH
```

Exempel:

```text
v1.4.2
```

GitHub Release ska referera samma tagg.

## Befintlig containerpublicering

`.github/workflows/docker-publish.yml` är current source of truth för GHCR-publicering.

Verifierat beteende:

- push till `main` publicerar image-taggen `latest`;
- schemalagd körning publicerar `nightly`;
- push av tagg som matchar `v*.*.*` publicerar taggbaserad image;
- registry är `ghcr.io`;
- image är `avkroken/plex-clear-watchlist`.

Det innebär att **deployment/image publication och GitHub Release inte är samma operation**. Main kan publicera `latest` utan att skapa en versionerad release.

En versionerad release ska använda samma SemVer-tag som containerpubliceringen så att GitHub Release och GHCR-taggen går att korrelera.

## PR-titlar och squash commits

Pull request-titlar ska följa Conventional Commits:

```text
<type>[optional scope][!]: <description>
```

Tillåtna typer:

- `feat`
- `fix`
- `perf`
- `refactor`
- `docs`
- `test`
- `build`
- `ci`
- `chore`
- `revert`

Scope är valfri, exempelvis `docker`, `backup`, `scheduler`, `reporting` eller `deps`.

`!` markerar breaking change:

```text
feat(docker)!: replace recreation contract
```

Workflow `.github/workflows/pr-title.yml` validerar titeln på `pull_request`. Det använder inga secrets, checkar inte ut repositoryt och har `permissions: {}`.

Aktuell Dependabot-historik använder redan kompatibla titlar som `build(deps): ...`.

## SemVer

Vid versionerad release:

- breaking change → **major**;
- `feat` → normalt **minor**;
- `fix` → normalt **patch**;
- `docs`, `test`, `chore`, `ci` och `build` → normalt ingen release ensamma;
- `perf` och `refactor` bedöms efter faktisk användar-/drifteffekt.

Releaseversionen är inte samma sak som image-publiceringsfrekvensen. `latest` och `nightly` är rörliga distributionskanaler, inte SemVer-versioner.

## När release ska ske

En versionerad release är motiverad när exempelvis:

- update-/recreationbeteende får en användarrelevant funktion;
- en fix bör få ett stabilt versionsankare;
- backup-/scheduler-/configkontrakt ändras på ett sätt konsumenter behöver kunna referera;
- en breaking ändring kräver ny major-version.

Release sker kuraterat och inte automatiskt på varje main-push.

## Releaseflöde

Målflödet är:

```text
main changes
  -> Conventional Commit-historik
  -> release-PR
  -> release notes + vald SemVer
  -> ordinarie CI
  -> merge
  -> vMAJOR.MINOR.PATCH tag
  -> befintlig docker-publish publicerar taggad image
  -> GitHub Release på samma tagg
```

`latest` kan fortsatt publiceras av normal main-push oberoende av releaseflödet.

## Verifiering vid release

Minst repositoryts verifierade gate ska vara grön:

```bash
python3 -m compileall -q src plex-clear-watchlist
python3 -m pytest -q
bash tests/test_pr_changes.sh
```

Docker-builden i repository-CI ska också vara grön.

För ändringar i update/recreation ska relevanta dry-run- och rollbackinvariants verifieras enligt [operations.md](operations.md).

## Releaseautomation — current state

Targeted current-main-verifiering hittade ingen Release Please- eller `action-gh-release`-workflow.

Release Please kan tekniskt skapa release-PR/tagg/GitHub Release från Conventional Commits, men är inte aktiverat här. Med standard-`GITHUB_TOKEN` triggar bot-skapade PR:er/taggar inte efterföljande Actions-workflows, vilket skulle bryta kravet på normal CI på release-PR.

Upstreamreferens: `https://github.com/googleapis/release-please-action#other-actions-on-release-please-prs`.

Följande används inte som genväg:

- ny PAT utan separat credentialbeslut;
- bredare write-permissions för befintlig read-only integration;
- lättade CI-/review-/repositoryskydd;
- release-PR som mergas utan normal verifiering.

Full releaseautomation förblir blockerad tills en least-privilege CI-kompatibel write-identitet eller annan säker modell är vald.

## CHANGELOG och release notes

Det finns ingen verifierad root `CHANGELOG.md` i den aktuella releaseinventeringen.

GitHub Releases är den officiella versionerade releasehistoriken för Portalens Changelog. En framtida versionsstyrd changelog får införas av samma release-PR-process, men ska genereras från commit-/releasehistorik i stället för att bli en separat manuellt underhållen sanning.

## Prerelease

Prerelease används endast med konkret behov, exempelvis:

```text
v2.0.0-rc.1
```

Kontrollera att container-taggingens faktiska workflowmatchning stödjer den avsedda taggen innan en prerelease används. Nuvarande trigger är `v*.*.*`; ändra inte publiceringskontraktet utan separat verifiering.

## Hotfix och rollback

Hotfix utgår normalt från aktuell `main` och använder `fix:` när ändringen är bakåtkompatibel.

Publicerade tags flyttas inte. Vid felaktig release:

1. korrigera eller revert:a via vanlig PR;
2. kör full relevant verifiering;
3. skapa en ny SemVer-version/tagg;
4. skapa ny GitHub Release;
5. verifiera den taggade GHCR-imagen.

Ingen force-push eller tag history rewrite används.

## Kvarvarande blocker

Full releaseautomation är separat arbete. Den får inte lösas genom nya onödiga credentials, write-permission på Skvallerbyttan eller kringgående av repositoryts CI.
