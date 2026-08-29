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

Arbete sker via tillfälliga arbetsgrenar och pull requests till `main`. Arbetsgrenar får använda repo- eller agentvalda namn som `claude/*`, `codex/*`, `feature/*`, `fix/*` eller motsvarande; de återanvändbara `work/feature`, `work/fix` och `work/chore` får fortfarande användas men är inte obligatoriska.

1. Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.
2. Pusha arbetsgrenen och öppna en ready PR till `main`.
3. **Aktivera auto-merge omedelbart efter att PR:n skapats**, även medan CI eller review fortfarande pågår.
4. Required CI-checkar och olösta review-trådar är merge-blockerare. Läs och utvärdera alltid alla review-kommentarer; relevanta fynd åtgärdas i samma PR. Markera inte en tråd resolved förrän den är utvärderad och eventuell fix är pushad.
5. Efter varje ny commit, kontrollera CI och review-status igen. När required checks är gröna och alla review-trådar är resolved ska den redan armerade auto-merge-funktionen föra PR:n vidare. Om den inte gör det, identifiera exakt kvarvarande blockerare. **Squash merge är den enda tillåtna merge-metoden.**

`.github/workflows/pr-watchdog.yml` bevakar alla lokala branches utom `main`, merge-köns `gh-readonly-queue/*`, den interna permanenta state-branchen `automation/pr-watchdog-state` och uttryckliga permanenta undantag. När en branch med unika commits först observeras utan öppen PR sparas `firstSeen` beständigt på state-branchen för den aktuella HEAD-SHA:n. Om HEAD ändras startar en ny observationsperiod; statusen nollställs också när en öppen PR finns eller branchen inte längre har unika commits mot `main`. Efter mer än 60 minuter på samma observerade HEAD skapas en ready PR till `main` och squash auto-merge armeras. Exakt samma HEAD öppnas inte på nytt om den redan har behandlats i en stängd PR. Watchdoggen avgör inte om arbetet är önskvärt eller mergebart; CI, review och merge-gates gör det.

`.github/workflows/sync-pool.yml` får fortsätta synka de uttryckliga återanvändbara `work/*`-slotsen men får aldrig resetta godtyckliga agent- eller arbetsgrenar.

Skicka aldrig direkt till `main`, kringgå inte branch protection/rulesets, required checks, review resolution eller merge queue och ändra inte hemligheter eller organisationsinställningar utan uttrycklig instruktion.

## Svarsformat

**[SKILLS.md](SKILLS.md) styr allt svarsformat. Läs den och följ den i varje svar.**

SKILLS.md har företräde framför den här filen och framför varje annan formuleringsanvisning i repot. Sammanfatta den inte, återge den inte i kortform och väg den inte mot andra skrivelser — det är den filen som gäller.
