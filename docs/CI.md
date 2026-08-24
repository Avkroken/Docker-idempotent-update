# CI och branchflöde

`main` är den enda långlivade arbetsgrenen. Varje ändring görs på en kortlivad branch och går via PR till `main`. Auto-merge får aktiveras på PR:er; när alla required checks och eventuella reviewkrav är uppfyllda mergar GitHub automatiskt. **Squash merge är den enda tillåtna merge-metoden.** Head-branchen raderas automatiskt efter merge.

PR-CI körs på `pull_request`. Push-verifiering, publicering och schemalagda kontroller körs där de behövs på `main`; samma arbetscommit ska inte få onödig dubbel-CI.

Repot är huvudsakligen Python med separata Docker-/paketeringsdelar. Python lint/test behåller stabila required check-namn. Docker- och paketeringsjobb filtrerar påverkan där det är säkert, medan required checks inte filtreras bort på workflow-nivå om det kan lämna dem i `Expected/Pending`.

Code Scanning-identiteter ska vara stabila. Dokumentation/processmetadata ska inte starta dyr Docker-CI, medan okänd kod/config ska fail-open till mer verifiering.
