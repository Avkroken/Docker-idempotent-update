# CI och branchflöde

`main` är default branch och den enda långlivade arbetsgrenen. Varje ändring görs på en kortlivad branch och går via PR till `main`. Repositoryts aktiva branch-enforcement är rulesetet `main-protection`, som träffar default branch. Det har inga bypass actors, blockerar deletion och non-fast-forward/force push och kräver PR före merge.

## Mergepolicy

För PR:er mot `main` gäller:

- endast squash merge
- 0 generella required approvals
- ingen last-push-approval
- alla review-trådar måste vara resolved
- required status checks körs med strict/latest-base-policy, så PR:n måste verifieras mot aktuell `main`

Auto-merge får användas först när live-rulesetet är verifierat och samtliga obligatoriska gates för aktuell PR-HEAD är godkända.

## Required status checks

Rulesetet kräver exakt följande GitHub Actions-contexts:

- `CI / required`
- `docker`
- `scan-pr / osv-scan`

`CI / required` är ett stabilt aggregatjobb som alltid skapas på PR:er. Det använder `always()` och blir success endast när både Ruff-jobbet `lint` och Python compile/test-jobbet `python` är `success`.

`docker` är en stabil context som alltid skapas. Impact-detektionen får hoppa över själva imagebygget när Docker-delen säkert är opåverkad, men contexten försvinner inte. Om påverkan inte kan avgöras säkert ska mer verifiering köras, inte mindre.

För Docker-påverkande PR:er byggs både en baseline-image från PR:ens aktuella `main`-bas och PR-imagen i samma run. Trivy rapporterar alla relevanta severiteter till Code Scanning. Merge-gaten jämför sedan HIGH/CRITICAL-fynden och failar om PR-imagen introducerar ett nytt HIGH/CRITICAL-fynd eller om baseline-build, PR-build, scanner eller jämförelse misslyckas. Befintliga HIGH/CRITICAL-fynd på `main` förblir synliga i rapporteringen men gör inte varje efterföljande PR permanent omergebart.

`scan-pr / osv-scan` kör OSV-Scanner för PR:n och är en required gate. Det återanvändbara upstream-workflowet jämför bas och PR och failar på nya dependency-vulnerabilities.

## Code Scanning

CodeQL körs med GitHubs Default setup. Repositoryt har inget separat Advanced CodeQL-workflow; GitHub hanterar den genererade CodeQL-konfigurationen och analyskörningarna.

Rulesetet använder GitHubs Code Scanning merge protection för verktyget `CodeQL`:

- security alerts: `medium_or_higher`
- alerts: `errors_and_warnings`

CodeQL måste vara konfigurerat och färdiganalyserat för PR:n; träffar på eller över trösklarna blockerar merge.

Trivy ligger inte som ett separat required Code Scanning-tool i rulesetet. Containerfynd är inte tillförlitligt knutna till rader i PR-diffen och Trivy-analysen är endast relevant när Docker-delen påverkas. HIGH/CRITICAL-mergebeslutet verkställs därför deterministiskt av den alltid existerande `docker`-contexten, medan SARIF fortfarande laddas upp för observation och triage.

GitHub Code Quality är inte en merge-gate eftersom någon separat stabil Code Quality-check inte har verifierats för repositoryt.

## AI-review

CodeRabbit är best effort och är inte en required status check. Saknad, pending, rate-limited eller misslyckad CodeRabbit-status blockerar inte ensam merge. CodeRabbit får fortfarande göra automatiska och inkrementella reviews på nya pushes. Om tjänsten faktiskt lämnar relevanta findings eller review-trådar ska de verifieras mot aktuell kod; giltiga findings ska åtgärdas och relevanta trådar måste vara resolved före merge.

Copilot Code Review är rådgivande och inte en hård merge-gate. Rulesetet har `review_on_push: true` och granskar inte draft-PR:er. Quota-, policy- eller tillgänglighetsproblem hos Copilot blockerar därför inte ensam merge. Faktisk relevant feedback hanteras som annan review-feedback.

## Övrigt

Klassisk branch-protection-statuscheck-enforcement är inte aktiv; `main-protection` är den verkställande branchpolicyn. Repositoryt tillåter auto-merge, men merge får inte forceras eller användas för att kringgå required checks, Code Scanning eller review-thread-enforcement.
