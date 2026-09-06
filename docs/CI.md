# CI

`.github/workflows/ci.yml` producerar `CI / required`. Jobbet verifierar både Ruff-jobbet `lint` och Python compile/test-jobbet `python`.

`docker` är en stabil context som alltid skapas. När Docker-delen påverkas byggs baseline- och PR-image och HIGH/CRITICAL-fynd jämförs deterministiskt. Om påverkan inte kan avgöras säkert ska mer verifiering köras, inte mindre.
