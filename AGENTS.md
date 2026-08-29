# AGENTS.md

Root-`AGENTS.md` är den auktoritativa källan för repositoryövergripande agentpolicy. En mer specifik `AGENTS.md` längre ned i katalogträdet får lägga till regler för sitt subtree men får inte motsäga reglerna här.

<!-- AVKROKEN-COMMON:START -->

## Arbetsprincip

Gör minsta kompletta ändring som löser uppgiften. Läs relevant implementation, tester, konfiguration och närmaste `AGENTS.md` innan du ändrar kod. Bevara befintlig arkitektur och repository-specifika konventioner om det inte finns ett konkret skäl att ändra dem.

## Pre-PR quality gate

Innan en ready PR skapas eller uppdateras:

1. Granska hela diffen mot PR:ns base branch.
2. Kör relevanta tester samt tillämplig lint, typecheck och build från repositoryts faktiska konfiguration.
3. Lägg till eller uppdatera tester när beteende ändras och det är praktiskt testbart.
4. Kontrollera att inga secrets, credentials, debugrester eller oavsiktliga filer har lagts till.
5. Fixa legitima egna findings före extern review.

Efter varje ny commit ska påverkad validering köras igen. Om full lokal validering inte är möjlig ska begränsningen beskrivas konkret i PR:n.

## Review-signal

Prioritera korrekthet, säkerhet, tillförlitlighet, kompatibilitet, tester och underhållbarhet framför redaktionell puts. Rapportera prose-fel endast när de påverkar teknisk betydelse, säkerhet, korrekthet eller instruktioner som ska köras eller kopieras bokstavligt.

## Reviewnivå och eskalering

Använd lägsta reviewnivå som ger tillräcklig säkerhet. Höj nivån för auth/access control, credentials/secrets, persistent data, concurrency/idempotency, integrationskontrakt, releaseflöden, privilegierad infrastruktur och stora refactors. Bygg inte nya AI-router-workflows när befintlig GitHub/Copilot-native delegering räcker.

## Pull request och merge

Pusha aldrig direkt till `main`. Följ repositoryts branchmodell och öppna en ready PR efter pre-PR-gaten.

Aktivera auto-merge omedelbart efter att PR:n skapats när repositoryt stöder det, även medan obligatorisk CI eller review fortfarande väntar. Direkt eller manuell merge används endast om repositoryägaren uttryckligen begär det och repositoryts regler tillåter det.

Required checks/CI och relevanta olösta review-trådar är merge-blockerare. Läs och utvärdera alla review-kommentarer. Om ett fynd är relevant ska det åtgärdas i samma PR innan tråden markeras resolved.

Efter varje ny commit ska aktuell HEAD, required checks/CI, mergeability och review-status kontrolleras igen. Auto-merge ska förbli armerad medan gates väntar.

Repositoryts aktuella ruleset, branch protection, merge queue och repositoryinställningar bestämmer tillåtna merge-metoder och övriga gates. Kringgå aldrig dessa. Om PR:n inte auto-mergas trots gröna required checks och lösta relevanta review-trådar ska exakt kvarvarande blockerare identifieras och rapporteras.

## Credentials och AI-infrastruktur

Committa eller exponera aldrig secrets, tokens, privata nycklar eller andra credentials. Lägg inte till `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` eller annan extern AI-provider-credential i repository, Actions secrets eller organisationskonfiguration utan uttryckligt godkännande från repository- eller organisationsägaren.

## Definition of done

En ändring är klar först när implementationen är färdig och avgränsad, relevant validering är genomförd eller en konkret begränsning dokumenterad, review-feedback är utvärderad och vid behov åtgärdad, CI och review-status är återkontrollerade efter senaste committen och auto-merge är armerad. Om merge fortfarande blockeras ska den faktiska repository-regeln eller annan blockerare vara identifierad.

<!-- AVKROKEN-COMMON:END -->

## Repository-specifika instruktioner

Dagligt Docker-underhåll i en container: hämtar images, återskapar ändrade containers, synkar backup via rclone och skickar rapport när något faktiskt hänt.

### Teknik och struktur

- Python 3.13, Docker/Compose, rclone, msmtp och intern cron.
- `src/run.py` är huvudjobbet; Docker-, backup-, rapport- och konfigurationslogik ligger i separata moduler under `src/`.
- Hemligheter kommer från miljövariabler. Hårdkoda aldrig credentials.
- Projektet använder i normalfallet bara Python-standardbiblioteket.
- Oväntade fel kan rapporteras best-effort via `src/github_report.py` om token finns; känsliga värden ska alltid redigeras bort.

### Versioner

Undvik versionspinnar om de inte behövs. Nödvändiga pinnar ska dokumenteras med orsak och villkor för att kunna tas bort. GitHub Actions är undantaget: pinna actions till commit-SHA och låt Dependabot uppdatera dem.

### Branch- och automationskontrakt

Arbete sker via tillfälliga arbetsgrenar och pull requests till `main`. Grennamn ska beskriva arbetet; återanvändbara `work/*`-grenar är tillåtna men inte obligatoriska eller särskilt ruleset-skyddade.

Kör relevanta tester före push; för containerändringar verifiera med Docker/Compose när det är praktiskt.

`.github/workflows/pr-watchdog.yml` bevakar lokala branches utom `main`, merge-köns `gh-readonly-queue/*`, state-branchen `automation/pr-watchdog-state` och uttryckliga permanenta undantag. Efter mer än 60 minuter på samma observerade HEAD utan öppen PR skapar den en ready PR till `main` och armerar auto-merge. Den avgör inte mergebarhet; CI och review-gates gör det.

Säkerhetsremediation använder en separat `automation/codex-issue-<nummer>`-branch per issue och öppnar PR till `main`; den är inte beroende av en permanent branchpool.

### Plex-subtree

`plex-clear-watchlist/AGENTS.md` innehåller subtree-specifika regler, bland annat `dev`-flödet. Repositoryövergripande merge- och reviewpolicy kommer från root-filen.

### Svarsformat

`SKILLS.md` styr repositoryts svarsformat och ska läsas av agenter som arbetar här.
