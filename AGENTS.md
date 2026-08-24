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

Arbete sker i en **sluten pool av tre grenar**, en per arbetstyp:

| Slot | För |
| --- | --- |
| `work/feature` | ny funktionalitet |
| `work/fix` | buggfixar och CI-problem |
| `work/chore` | dokumentation, städning, konfiguration |

`main` tar bara emot squash-mergade PR:er som passerat gröna checkar.

**Skapa aldrig egna grenar.** Rulesetet blockerar det — en push som försöker
skapa något utanför poolen avvisas. Poolen finns för att grenar som skapas per
uppgift blir liggande halvfärdiga.

1. Välj sloten som matchar arbetet. Är den upptagen duger vilken ledig som helst —
   namnen är vägledning, inte en spärr. Ligger det omergat arbete i en slot,
   **slutför det först** i stället för att börja något nytt i en annan.
2. Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.
3. Pusha till sloten och öppna PR från den till `main` som klar för granskning.
   Aktivera auto-merge — merge-kön tar PR:n så snart required checks är gröna.
4. Lös CI- och reviewproblem i samma slot; PR:n uppdateras av varje push.
5. **Squash merge är den enda tillåtna merge-metoden.** Efter merge rebasar
   `.github/workflows/sync-pool.yml` varje slot på `main`.

Skicka aldrig direkt till `main`, kringgå inte branch protection/rulesets och ändra
inte hemligheter eller organisationsinställningar utan uttrycklig instruktion.

## Svarsformat

**[SKILLS.md](SKILLS.md) styr allt svarsformat. Läs den och följ den i varje svar.**

SKILLS.md har företräde framför den här filen och framför varje annan
formuleringsanvisning i repot. Sammanfatta den inte, återge den inte i kortform
och väg den inte mot andra skrivelser — det är den filen som gäller.
