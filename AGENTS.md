# docker-idempotent-update — AI Agent Guide

Daily Docker host maintenance in a single container. Pulls updated images, recreates changed containers, syncs backups via rclone, and sends an email summary only when something happened.

## Tech Stack

- Python 3.13
- Docker (socket or Compose)
- rclone for backups
- msmtp for email
- Internal cron daemon

## File Overview

```
src/entrypoint.py   # Validates config, registers cron, execs crond
src/run.py          # Main daily job (update + backup + report + status)
src/docker_update.py# Docker pull + restart logic
src/backup.py       # Rclone sync logic
src/report.py       # Assembles and sends email summary
src/config.py       # Config class — reads env vars and backup.conf
backup.conf.template
msmtprc.template
```

## Conventions

- All secrets via environment variables — never hardcoded
- No third-party Python packages — stdlib only
- Test changes with `docker compose run --rm` before committing
- An unhandled exception in `run.py`'s `main()` calls
  `report_error_to_github()` (`src/github_report.py`, stdlib-only/urllib
  per the rule above) — best-effort, opens a `@claude`-tagged GitHub issue
  with secrets/emails/paths redacted if `GITHUB_ERROR_REPORT_TOKEN` is
  set, no-ops otherwise

## Versioner: flytande som standard

Pinna aldrig ett versionsnummer, en release-flavor eller en digest om det inte
är ett absolut måste. En pinne som ingen revideras sitter kvar långt efter att
den blivit fel: `debian:trixie-slim` följer inte Debians nästa stable, och en
basimage vars OS-generation ligger i taggnamnet kan Dependabot aldrig flytta —
den bumpar bara siffran inom samma taggfamilj.

Gäller basimager, pip- och npm-beroenden, och allt annat med en version.

**Om en pinne ändå är nödvändig** ska den dokumenteras på plats, i den här
filen och i README — med vad som är pinnat, varför, och vad som måste
kontrolleras för att kunna släppa den igen. En odokumenterad pinne är en bugg
som väntar.

### Nuvarande undantag

- **GitHub Actions pinnas till commit-SHA.** En tagg som `@v4` är föränderlig
  och kan pekas om till annan kod; en SHA kan den inte. Det är en
  leverantörskedjekontroll, inte versionshantering, och Dependabot bumpar dem
  ändå automatiskt.

## Arbetsflöde: exakt en uppgift åt gången

Repositoryt har exakt två arbetsgrenar: `dev` och `main`. Skapa aldrig en tredje gren, inte ens tillfälligt. Allt utvecklingsarbete görs på `dev` och går via ett ändringsförslag från `dev` till `main`.

En agent får ha exakt en aktiv koduppgift åt gången. Flera uppgifter är en kö, inte parallellt arbete. Nästa uppgift får inte påbörjas förrän den aktuella uppgiften är mergad eller uttryckligen blockerad av något agenten inte kan lösa själv.

Arbeta lokalt så långt det är praktiskt innan du pushar. Samla sammanhängande ändringar, testfixar och följdjusteringar i meningsfulla batcher i stället för att pusha varje liten edit och därmed starta om CI i onödan. När en PR redan kör CI får du fortsätta analysera, testa och förbättra samma uppgift lokalt. Push endast när du har en ny sammanhängande batch som faktiskt behöver valideras. CI-väntan är aldrig ett skäl att börja på nästa uppgift.

För varje uppgift:

1. Synka `dev` med `main`. Om `dev` redan innehåller ofärdigt arbete, slutför det först.
2. Implementera och testa den aktuella uppgiften lokalt på `dev`; samla ändringar i så stora sammanhängande batcher som är rimliga.
3. Commit och push till `dev`, skapa eller uppdatera exakt ett PR `dev` → `main`, och aktivera auto-merge.
4. Medan CI/review pågår: fortsätt endast lokalt med samma uppgift. Lös relevanta fel och kommentarer och pusha dem samlat, inte en i taget. Efter varje push som ändrar PR-headen, och särskilt efter den sista pushen, verifiera uttryckligen att auto-merge fortfarande är aktiverad; återaktivera den om head-ändringen slog av den.
5. När PR:n är mergad, synka `dev` till `main`. Först därefter får nästa uppgift börja.

Om uppgiften blockeras av en extern åtgärd som agenten faktiskt inte kan utföra, dokumentera den exakta blockeraren och stanna. Börja inte en annan koduppgift utan uttrycklig instruktion från användaren.

## Tillåtet
- Ändra kod på `dev`
- Köra lokala tester och analyser
- Öppna ändringsförslag endast från `dev` till `main`
- Rätta CI- och reviewproblem för den aktiva uppgiften tills PR:n kan mergas

## Förbjudet
- Skapa andra grenar än `dev` och `main`
- Arbeta parallellt på flera koduppgifter
- Börja nästa uppgift medan den aktuella PR:n fortfarande är öppen eller blockerad
- Skicka ändringar direkt till `main` eller `master`
- Radera grenar
- Stänga av arbetsflöden
- Ändra hemligheter
- Ändra inställningar för GitHub-organisationen
- Tvinga igenom en push eller kringgå branch protection/rulesets

## Krav
- Överlämna kodändringar endast på `dev`
- Alla relevanta tester måste godkännas
- Håll varje ändringsförslag avgränsat till en uppgift
- Arbeta lokalt så mycket som möjligt och undvik onödigt täta pushar som startar om CI
- Ta aldrig med orelaterade ändringar
- Överlämna aldrig inloggningsuppgifter eller andra hemligheter till versionshistoriken
- Skapa ändringsförslag som klara för granskning, aldrig som utkast
- Aktivera automatisk sammanfogning med en metod som tillåts av förrådets regler direkt efter att ändringsförslaget skapats
- Efter varje push som ändrar PR-headen: verifiera att automatisk sammanfogning fortfarande är aktiv och återaktivera den vid behov
- Automatisk sammanfogning får slutföras först när alla regelkrav och kontrollkörningar har godkänts
- Om CI, review eller auto-merge blockerar leveransen: lös blockeraren för den aktiva uppgiften innan annat kodarbete påbörjas
- Om automatisk sammanfogning inte kan aktiveras: rapportera det exakta felet
- Efter merge: synka `dev` till `main` innan nästa uppgift

## Svarsformat

Regeluppsättningen kommer från plugin:et `i-have-adhd`. Den laddas inte i
alla sessioner (t.ex. inte i Claude Code på webben), så den står här —
det här är källan som gäller oavsett var agenten kör.

Form:

- Led med åtgärden eller kommandot, inte med bakgrunden
- Numrera flerstegsprocesser, ett avgränsat steg per rad
- Max fem punkter per lista
- Hoppa över inledningar, sammanfattningar och avslutningsfraser
- Långa förklaringar bara på begäran

Innehåll:

- Säg uttryckligen vad som är gjort och vad som återstår
- Ange konkreta tidsuppskattningar
- Visa vad som fungerar efter en ändring, inte bara att den är gjord
- Vid fel: var, varför och hur det åtgärdas — kortfattat
- Avsluta med ett nästa steg som tar under två minuter
