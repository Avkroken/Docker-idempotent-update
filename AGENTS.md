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

`main` tar bara emot squash-mergade PR:er som passerat alla merge-gates.

**Skapa aldrig egna grenar.** Rulesetet blockerar det. Välj lämplig ledig slot och slutför omergat arbete innan nytt parallellt arbete startas.

1. Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.
2. Pusha till sloten och öppna PR till `main` som klar för granskning.
3. **Aktivera auto-merge omedelbart efter att PR:n skapats**, även medan CI eller review fortfarande pågår.
4. Required CI-checkar och olösta review-trådar är merge-blockerare. Läs och utvärdera alltid alla review-kommentarer; relevanta fynd åtgärdas i samma PR. Markera inte en tråd resolved förrän den är utvärderad och eventuell fix är pushad.
5. Efter varje ny commit, kontrollera CI och review-status igen. När required checks är gröna och alla review-trådar är resolved ska den redan armerade auto-merge-funktionen föra PR:n vidare. Om den inte gör det, identifiera exakt kvarvarande blockerare. **Squash merge är den enda tillåtna merge-metoden.**

Efter merge rebasar `.github/workflows/sync-pool.yml` varje slot på `main`.

Skicka aldrig direkt till `main`, kringgå inte branch protection/rulesets och ändra inte hemligheter eller organisationsinställningar utan uttrycklig instruktion.

## Svarsformat

**[SKILLS.md](SKILLS.md) styr allt svarsformat. Läs den och följ den i varje svar.**

SKILLS.md har företräde framför den här filen och framför varje annan formuleringsanvisning i repot. Sammanfatta den inte, återge den inte i kortform och väg den inte mot andra skrivelser — det är den filen som gäller.
