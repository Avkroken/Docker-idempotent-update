# DOCKER-IDEMPOTENT-UPDATE.md

This is the repository governance document for `Avkroken/Docker-idempotent-update`. Binding AI coding-agent policy is defined only in `Avkroken/.github/AGENTS.md`. This document records repository-specific technical contracts, invariants, validation requirements, and operational context required by that policy; it must not define, supplement, narrow, or override agent policy.

## Repository

This repository performs daily Docker maintenance inside a container: it pulls images, recreates changed containers, synchronizes backups through rclone and reports only when something actually happened.

### Technology and structure

- Python 3.13, Docker/Compose, rclone, msmtp and internal cron.
- `src/run.py` is the main job; Docker, backup, reporting and configuration logic live in separate modules under `src/`.
- Secrets come from environment variables; never hardcode credentials.
- The project normally relies only on the Python standard library.
- Unexpected failures may be reported best-effort through `src/github_report.py` when a token is configured; sensitive values must remain redacted.

### Versioning and validation

Avoid dependency pins unless they are needed. A necessary pin must document the reason and the condition for removal. GitHub Actions are the exception: pin third-party Actions to full commit SHAs and let Dependabot advance those immutable references.

For container changes, validate with Docker/Compose when practical in addition to the repository's relevant tests.

Repository workflows should remain small and single-purpose around Python CI, Docker/Trivy, OSV and package cleanup. Preserve the live check-context names when changing required workflows.

## `plex-clear-watchlist/`

This subtree deletes items from a Plex Watchlist through the Plex API and runs as a one-shot Docker container.

### Tech stack

- Python 3.14
- Plex API using `PLEX_TOKEN`
- Docker / Docker Compose

### Usage

```bash
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --dry-run
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --limit 10
PLEX_TOKEN=your-token docker compose run --rm plex-clear-watchlist --keep 5
```

### Key files

```text
plex_clear_watchlist.py     # main script
requirements.txt            # Python dependencies
Dockerfile
docker-compose.yml
```

### Conventions

- `PLEX_TOKEN` is always supplied through the environment and is never hardcoded.
- `--dry-run` must remain side-effect free.
- Keep the script simple and single-purpose.

### Subtree branch rule

- Code changes for this subtree are handed over on `dev`, with the change proposal opened from `dev` to the repository default branch.
- Do not start a new code task while a proposal from `dev` remains open; finish or close it first.
- Open proposals ready for review, not as drafts.
- Keep each proposal limited to one task and require its tests to pass.
- Never force-push, delete branches, disable workflows or modify GitHub organization settings as part of this subtree flow.

## Response format

Read and follow `SKILLS.md` when working in this repository.
