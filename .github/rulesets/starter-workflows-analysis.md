# Starter-workflow-analys för rulesets

## Aktuell repo-yta och observerad tidigare CI

Repositoryt innehåller Python-baserad underhållskod samt den containeriserade underkatalogen `plex-clear-watchlist/`.

Före ändring verifierades senaste `main`-körningen för den egna CI:n. Jobbet `CI / required` var grönt och körde Python 3.13.15, Ruff, compileall och repositoryts shellbaserade testharness; harnessens resultat var 59 godkända och 0 misslyckade kontroller. Den senaste Docker-körningen var också grön och byggde/publicerade imagen samt körde Trivy/SARIF. GitHubs dynamiska CodeQL/default setup var grön på samma `main`-commit.

## Valda standardmallar

- `actions/starter-workflows/ci/docker-image.yml`, ifylld för `main` och Dockerfile/context under `plex-clear-watchlist/`.
- `actions/starter-workflows/code-scanning/dependency-review.yml`, ifylld för `main`.
- `actions/starter-workflows/.github/dependabot.yml`, ifylld för repositoryts GitHub Actions-, pip-, Docker- och Docker Compose-manifest.

Action-referenser i workflow-filerna är SHA-pinnade till motsvarande versioner från standardmallarna för att följa repositoryts Actions-policy utan att lägga till egen workflow-logik.

## CodeQL

Ingen lokal Advanced CodeQL-workflow läggs till. GitHubs dynamiska/default CodeQL är redan aktiv och verifierades grön på aktuell `main`.

## Required checks

Det befintliga repo-rulesetet kräver `CI / required` och `docker`. Dessa namn kommer från de borttagna egna workflow-filerna och ska inte överföras genom antagande. Rulesetet uppdateras först när de nya starter-workflows faktiskt har producerat observerbara checknamn på denna PR-branch.

## Funktioner som standardmallarna inte täcker

Repositoryts shellbaserade testharness, Ruff/compileall-kedja och dess stabila `CI / required`-namn har ingen direkt standardmall som kan bevaras utan egen CI-logik. De dokumenteras därför som täckningsgap och byggs inte om.

Den tidigare Docker-workflowens GHCR-publicering, differential Trivy-skanning, SARIF-upload och blockering av nya HIGH/CRITICAL-fynd ligger utanför den valda Docker Image CI-standardmallen och byggs inte om som egen workflow-logik.

Cleanup av gamla GHCR-paket, organisationens Release Please-wrapper och tidigare OSV-workflow ersätts inte med egna lösningar när direkt motsvarande starter-workflow saknas. Security-alert-specifika issue- eller PR-mallar skapas inte om motsvarande mall saknas i `actions/starter-workflows`.
