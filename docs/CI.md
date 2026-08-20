# CI och branchflöde

Repositoryt använder endast `dev` och `main`. Arbete görs på `dev`, PR går `dev → main`, och efter merge fast-forwardar `.github/workflows/sync-dev.yml` automatiskt `dev` till `main` utan force-push. Om `dev` innehåller omergat arbete ska synken avbryta.

Vanlig CI ska inte verifiera samma arbetscommit både som `push` till `dev` och `pull_request`. PR-CI körs på PR; push-verifiering/publicering körs på `main`.

Repot är huvudsakligen Python med separata Docker-/paketeringsdelar. Därför används inte en generell fler-språksmotor. Python lint/test behåller stabila required check-namn, medan Docker/paketeringsjobb får fil-/komponentfilter där beroendet är tydligt. Required checks får inte filtreras bort på workflow-nivå om det kan lämna dem i `Expected/Pending`.

Code Scanning-identiteter ska vara stabila över namnbyten. Dokumentation/processmetadata ska inte starta dyr Docker-/paketerings-CI, medan okänd kod/config ska fail-open till mer verifiering.