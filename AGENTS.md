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

`dev` är den enda skrivbara grenen. `main` tar bara emot squash-mergade PR:er
som passerat gröna checkar.

**Skapa aldrig egna grenar.** Allt arbete sker på `dev`. Det är en hård regel, inte
en rekommendation: grenar som skapas per uppgift blir liggande halvfärdiga, och det
är hela anledningen till att modellen ser ut så här.

1. Utgå från aktuell `dev`. Ligger det osynkat arbete där, bygg vidare på det i
   stället för att börja om någon annanstans.
2. Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.
3. Pusha till `dev` och öppna PR från `dev` till `main` som klar för granskning.
   Aktivera auto-merge — merge-kön tar PR:n så snart required checks är gröna.
4. Lös CI- och reviewproblem på `dev`; PR:n uppdateras automatiskt av varje push.
5. **Squash merge är den enda tillåtna merge-metoden.** Efter merge återställs `dev` till
   `main` automatiskt av `.github/workflows/sync-dev.yml`.

Skicka aldrig direkt till `main`, kringgå inte branch protection/rulesets och ändra
inte hemligheter eller organisationsinställningar utan uttrycklig instruktion.

## Svarsformat

**[SKILLS.md](SKILLS.md) styr allt svarsformat. Läs den och följ den i varje svar.**

SKILLS.md har företräde framför den här filen och framför varje annan
formuleringsanvisning i repot. Sammanfatta den inte, återge den inte i kortform
och väg den inte mot andra skrivelser — det är den filen som gäller.
