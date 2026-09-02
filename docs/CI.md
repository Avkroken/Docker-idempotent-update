# CI och branchflöde

`main` är default branch och den enda långlivade arbetsgrenen. Varje ändring görs på en kortlivad branch och går via PR till `main`. Live-rulesets är auktoritativa för branch- och mergekrav.

## Mergepolicy

För PR:er mot `main` gäller:

- endast squash merge
- merge queue krävs av repositoryts aktiva `Merge queue`-ruleset
- 0 generella required approvals
- ingen last-push-approval
- alla review-trådar måste vara resolved
- required status checks körs med strict/latest-base-policy, så både PR-HEAD och mergegruppen måste verifieras mot aktuell `main`

Auto-merge får användas när live-rulesetet är verifierat; GitHub ska därefter låta merge queue och övriga obligatoriska gates styra själva mergingen.

## Required status checks

Live-rulesets kräver följande GitHub Actions-contexts för repositoryt:

- `CI / required`
- `docker`
- `scan-pr / osv-scan`

`CI / required` är ett stabilt jobb som kör samma verifiering på både `pull_request` och `merge_group`, så merge queue får en check för den syntetiska mergegruppens SHA.

`docker` är en stabil context som också kör på `merge_group`. PR-specifik baselinejämförelse körs endast på `pull_request`; mergegruppen bygger och skannar den faktiska köade SHA:n utan att publicera image.

För Docker-påverkande PR:er byggs både en baseline-image från PR:ens aktuella `main`-bas och PR-imagen i samma PR-run. Trivy rapporterar alla relevanta severiteter till Code Scanning. PR-gaten jämför sedan HIGH/CRITICAL-fynden och failar om PR-imagen introducerar ett nytt HIGH/CRITICAL-fynd eller om baseline-build, PR-build, scanner eller jämförelse misslyckas. Befintliga HIGH/CRITICAL-fynd på `main` förblir synliga i rapporteringen men gör inte varje efterföljande PR permanent omergebart.

`scan-pr / osv-scan` är fortfarande en live required status context. Organisationens centrala required OSV-workflow ligger i `Avkroken/.github` och har separat `merge_group`-stöd.

## Code Scanning

CodeQL körs med GitHubs Default setup. Repositoryt har inget separat Advanced CodeQL-workflow; GitHub hanterar den genererade CodeQL-konfigurationen och analyskörningarna.

Rulesetet använder GitHubs Code Scanning merge protection för verktyget `CodeQL`:

- security alerts: `medium_or_higher`
- alerts: `errors_and_warnings`

CodeQL måste vara konfigurerat och färdiganalyserat för PR:n; träffar på eller över trösklarna blockerar merge.

Trivy ligger inte som ett separat required Code Scanning-tool i rulesetet. Containerfynd är inte tillförlitligt knutna till rader i PR-diffen och Trivy-analysen är endast relevant när Docker-delen påverkas. HIGH/CRITICAL-mergebeslutet verkställs därför deterministiskt av den alltid existerande `docker`-contexten, medan SARIF fortfarande laddas upp för observation och triage.

GitHub Code Quality är inte en separat dokumenterad repository-statuscheck här; live rulesets avgör eventuell Code Quality-enforcement.

## AI-review

CodeRabbit är best effort och är inte en required status check. Saknad, pending, rate-limited eller misslyckad CodeRabbit-status blockerar inte ensam merge. CodeRabbit får fortfarande göra automatiska och inkrementella reviews på nya pushes. Om tjänsten faktiskt lämnar relevanta findings eller review-trådar ska de verifieras mot aktuell kod; giltiga findings ska åtgärdas och relevanta trådar måste vara resolved före merge.

Copilot Code Review är rådgivande utöver vad live rulesets uttryckligen verkställer. Faktisk relevant feedback hanteras som annan review-feedback.

## Övrigt

Repositoryts aktiva organisation- och repository-rulesets är den verkställande policyn. Merge får inte forceras eller användas för att kringgå required checks, Code Scanning, review-thread-enforcement eller merge queue.
