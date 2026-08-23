# docker-idempotent-update — AI Agent Guide

Dagligt Docker-underhåll i en container: hämtar images, återskapar ändrade containers, synkar backup via rclone och skickar rapport när något faktiskt hänt.

## Teknik och struktur

- Python 3.13, Docker/Compose, rclone, msmtp och intern cron.
- `src/run.py` är huvudjobbet; Docker-, backup-, rapport- och konfigurationslogik ligger i separata moduler under `src/`.
- Hemligheter kommer från miljövariabler. Hårdkoda aldrig credentials.
- Projektet använder i normalfallet bara Python-standardbiblioteket.
- Oväntade fel kan rapporteras best-effort via `src/github_report.py` om token finns; känsliga värden ska alltid redigeras bort.

## Versioner

Undvik versionspinnar om de inte behövs. Nödvändiga pinnar ska dokumenteras med orsak och villkor för att kunna tas bort. GitHub Actions är undantaget: pinna actions till commit-SHA och låt Dependabot uppdatera dem.

## GitHub-arbetsflöde

`main` är den enda långlivade arbetsgrenen. `dev` används inte.

1. Skapa en kortlivad branch från aktuell `main` för varje uppgift.
2. Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.
3. Öppna PR från arbetsbranchen till `main`. PR:n ska vara avgränsad och klar för granskning. Aktivera inte auto-merge.
4. Lös CI- och reviewproblem på samma branch tills required checks är gröna och review-trådar är lösta.
5. Merge sker med **squash merge**. Använd inte merge commits eller rebase merge. Head-branchen får raderas efter merge.

Skicka inte direkt till `main`, force-pusha inte förbi regler och kringgå inte branch protection/rulesets. Ändra inte hemligheter eller organisationsinställningar utan uttrycklig instruktion.

## Svarsformat

Led med nästa åtgärd eller resultat, numrera flerstegsarbete, håll listor korta och ange konkret orsak/fix vid fel.
