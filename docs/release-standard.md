# Release- och versionsstandard

**Senast verifierad:** 2026-09-30

Det här dokumentet gäller **Docker-idempotent-update**. Repositoryts egna workflows, taggar och GitHub Releases äger release- och containerpubliceringskontraktet.

## Versionsankare

Repositoryreleases använder immutable SemVer-taggar:

```text
vMAJOR.MINOR.PATCH
```

GitHub Release och den versionsmärkta GHCR-imagen använder samma tagg. `latest` och `nightly` är rörliga distributionskanaler och är inte releaseversioner.

## PR-titlar och merge queue

PR-titlar ska följa Conventional Commits:

```text
<type>[optional scope][!]: <description>
```

Tillåtna typer är `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore` och `revert`.

`.github/workflows/pr-title.yml` validerar pull requests och rapporterar samma required-check-context på `merge_group`. Workflown använder inga secrets och har `permissions: {}`.

## SemVer

Automatisk versionsberäkning följer:

- breaking change -> **major**;
- `feat` -> **minor**;
- `fix`, `perf` och `revert` -> **patch**;
- `refactor`, `docs`, `test`, `build`, `ci` och `chore` skapar normalt ingen release ensamma;
- `Release-As: major|minor|patch|none` kan klassificera en icke-breaking ändring;
- breaking change kan aldrig sänkas under major av `Release-As`.

## Automatiskt releaseflöde

`.github/workflows/release.yml` äger releaseprocessen lokalt:

```text
PR
  -> Conventional Commit-kompatibel PR-titel
  -> ordinarie CI/review
  -> merge till main
  -> Python + Docker verifierar samma main-SHA
  -> SemVer + genererade release notes
  -> immutable GitHub Release/tagg
  -> samma target-SHA byggs som versionsmärkt GHCR-image
```

Releasejobbet kör bara på `main`, använder full Git-historik, kräver checks i `.github/release-required-checks` och vägrar divergerande/stale versionshistorik.

## Required release checks

En release-target måste ha `success` från följande repo-lokala verifieringar:

- `Python`;
- `Docker`;
- `CodeQL (actions)`;
- `CodeQL (python)`.

Releasegaten bedömer endast dessa uttryckligen required checks. PR-only eller underhållsspecifika jobb, exempelvis `Dependency review`, Dependabot-automerge eller andra sidoworkflows, får inte oavsiktligt blockera en versionerad release på en redan verifierad `main`-SHA.

Gaten väntar på exakt release-target SHA, kräver att samtliga namn faktiskt observeras och accepterar endast `success` för dem. Releasejobbet serialiseras av GitHub Actions native `concurrency` med `cancel-in-progress: false`; det använder inte ett eget API-pollande lås vars synlighet kan drabbas av eventual consistency. En befintlig SemVer-tagg får bara användas som releaseankare om motsvarande GitHub Release finns och inte är draft.

## Containerpublicering

`.github/workflows/docker-publish.yml` har tre separata roller:

- push till `main` publicerar `latest`;
- schemakörning publicerar `nightly`;
- releaseworkflown anropar samma workflow som reusable workflow och publicerar exakt release-taggen, exempelvis `v3.4.0`.

Den versionerade image-publiceringen är explicit kopplad till releasejobbet. Den förlitar sig inte på att en tagg skapad med `GITHUB_TOKEN` ska starta en ny fristående workflowkörning.

## Changelog

GitHub Releases är canonical changelog. Release notes genereras från repositoryts first-parent-historik och grupperas efter Conventional Commit-typ.

## Prerelease

Manuell `workflow_dispatch` kan skapa `vMAJOR.MINOR.PATCH-rc.N`. En RC publicerar motsvarande versionsmärkt GHCR-image. Promotion till stable pekar på den aktiva RC:ns commit och tar inte med senare `main`-commits implicit.

## Credentials och permissions

Canonical tagg- och GitHub Release-publication behöver ingen PAT och använder repositoryts `GITHUB_TOKEN` med least privilege:

- read för checks/status/history;
- `contents: write` för GitHub Release/tagg;
- `packages: write` endast i containerpubliceringsjobbet.

## Hotfix och rollback

Publicerade taggar flyttas inte. En korrigering går via vanlig PR, normal verifiering och en ny SemVer-release. Ingen force-push eller tag history rewrite används.

## Copilot-sammanfattning

Releaseflödet kör den SHA-pinnade `github/copilot-release-notes`-actionen i ett separat read-only-jobb med `contents: read` och `pull-requests: read`. Copilot CLI förinstalleras i exakt version `1.0.90` innan `COPILOT_GITHUB_TOKEN` exponeras, så actionen använder den redan installerade binären i stället för att hämta en flytande CLI-version.

`COPILOT_GITHUB_TOKEN` ska vara en least-privilege fine-grained PAT med `Copilot Requests: Read` och en tokenägare med aktiv Copilot-licens. Workflown skapar eller roterar ingen credential. Om secreten saknas eller Copilot-genereringen misslyckas påverkas inte releaseprocessen.

Copilot-resultatet publiceras endast i GitHub Actions run summary som rådgivande text. Det skrivs inte in i den kanoniska GitHub Release-body:n. SemVer, release-target, required checks och release notes i GitHub Release fortsätter därför att komma enbart från `semantic_release.py`; osäkra eller ofullständiga AI-resultat kan aldrig ändra canonical changelog.
