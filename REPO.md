# REPO.md

This repository performs Docker maintenance: pull images, recreate changed containers, synchronize backups and report meaningful changes. `plex-clear-watchlist/` is a small one-shot Plex maintenance tool in the same repository.

## Invariants

- Secrets come from environment variables; never hardcode credentials or expose them in reports/logs.
- Prefer the Python standard library and existing project mechanisms over new dependencies.
- Preserve best-effort error reporting redaction in `src/github_report.py`.
- The `plex-clear-watchlist` tool's `--dry-run` mode must remain side-effect free and `PLEX_TOKEN` must remain external to the image/repository.
- Use the normal short-lived branch + pull-request flow from the central policy for all code in this repository; no permanent `dev` handoff branch is required.

## Validation

Run the relevant tests for changed Python code. For container changes, validate with Docker/Compose when practical.

The live repository rules currently require `CI / required` and `docker`. Do not rename a required check without updating and verifying the live ruleset in the same migration.

Pin third-party GitHub Actions to full commit SHAs.
