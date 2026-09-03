# CI och merge

Repositoryts required status checks är `CI / required` och `docker`. Båda styrs av aktiva organization-level status-rulesets med strict latest-base-verifiering.

`CI / required` är ett stabilt aggregatjobb som verifierar både Ruff-jobbet `lint` och Python compile/test-jobbet `python`. `docker` är en stabil context som alltid skapas; när Docker-delen påverkas byggs baseline- och PR-image och HIGH/CRITICAL-fynd jämförs deterministiskt. Om påverkan inte kan avgöras säkert ska mer verifiering köras, inte mindre.

Organisationens `main`-ruleset kräver den centrala OSV-workflowen från `Avkroken/.github`. På vanliga pull requests kör den `scan-pr`; i merge queue kör den `scan-merge-group`. `scan-pr / osv-scan` är inte en separat organization-level required status check.

CodeQL merge protection, review-thread resolution, squash-only och övriga gemensamma merge-regler hanteras centralt av organisationens aktiva rulesets. Repositoryt använder merge queue.

CodeRabbit och Copilot Code Review är rådgivande. Deras tillgänglighet är inte en required status, men faktiska relevanta findings och review-trådar ska hanteras.
