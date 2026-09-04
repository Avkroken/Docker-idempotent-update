# Changelog

## [3.3.0](https://github.com/Avkroken/Docker-idempotent-update/compare/v3.2.1...v3.3.0) (2026-09-04)


### Features

* enable metadata-only AI issue triage ([#396](https://github.com/Avkroken/Docker-idempotent-update/issues/396)) ([2f1c6c1](https://github.com/Avkroken/Docker-idempotent-update/commit/2f1c6c105ba0dc84e2095277af390778b399dfc5))


### Fixes

* avoid invalid reusable-workflow variable context ([#407](https://github.com/Avkroken/Docker-idempotent-update/issues/407)) ([77f34d9](https://github.com/Avkroken/Docker-idempotent-update/commit/77f34d9289fd23296310387db4588f8d79d4ec50))
* **ci:** attach Trivy SARIF to PR head commit ([7c52b09](https://github.com/Avkroken/Docker-idempotent-update/commit/7c52b09ee7f7f8ef9887a96ba3c57522f3dc1a59))
* complete Avkroken migration references ([#285](https://github.com/Avkroken/Docker-idempotent-update/issues/285)) ([e0f1d4f](https://github.com/Avkroken/Docker-idempotent-update/commit/e0f1d4f739a1f687e01307bb201509ff9a6138a0))
* complete PR metadata reconciliation ([#405](https://github.com/Avkroken/Docker-idempotent-update/issues/405)) ([8b87330](https://github.com/Avkroken/Docker-idempotent-update/commit/8b873306d0f5079f9a6c90608ba1f74e9005c813))
* continue PR reconciliation after assignment errors ([8b87330](https://github.com/Avkroken/Docker-idempotent-update/commit/8b873306d0f5079f9a6c90608ba1f74e9005c813))
* let metadata reconciliation finish ([#410](https://github.com/Avkroken/Docker-idempotent-update/issues/410)) ([720d976](https://github.com/Avkroken/Docker-idempotent-update/commit/720d9761449d746a9f9fc1df781a2e0120edf9d1))
* preserve queued metadata events ([#409](https://github.com/Avkroken/Docker-idempotent-update/issues/409)) ([4cd50b9](https://github.com/Avkroken/Docker-idempotent-update/commit/4cd50b9b04c8bf2c06f7529ff76ef5ff2a8a6f60))
* propagate metadata reconciliation failures ([#404](https://github.com/Avkroken/Docker-idempotent-update/issues/404)) ([cd67394](https://github.com/Avkroken/Docker-idempotent-update/commit/cd6739487862a14cb53a14d8afd9ba1f1835eb04))
* propagate PR reconciliation listing failures ([cd67394](https://github.com/Avkroken/Docker-idempotent-update/commit/cd6739487862a14cb53a14d8afd9ba1f1835eb04))
* reconcile Dependabot outside PR events ([#402](https://github.com/Avkroken/Docker-idempotent-update/issues/402)) ([29fed93](https://github.com/Avkroken/Docker-idempotent-update/commit/29fed93aa131f1755000a4a0e0d49754ad40acf2))
* schedule PR metadata reconciliation ([#403](https://github.com/Avkroken/Docker-idempotent-update/issues/403)) ([96940ba](https://github.com/Avkroken/Docker-idempotent-update/commit/96940ba9257ef2acf93419e781ab9f6da71f12ef))
* **security:** require patched idna ([#172](https://github.com/Avkroken/Docker-idempotent-update/issues/172)) ([2fbd2fb](https://github.com/Avkroken/Docker-idempotent-update/commit/2fbd2fb1166bea15c2ea075e764ab6d892830e01))
* serialize issue metadata routing ([#408](https://github.com/Avkroken/Docker-idempotent-update/issues/408)) ([e2a7104](https://github.com/Avkroken/Docker-idempotent-update/commit/e2a71047109f7b58c53efabe59b18f9b38f54d46))
* serialize PR metadata reconciliation ([#406](https://github.com/Avkroken/Docker-idempotent-update/issues/406)) ([4e21c8a](https://github.com/Avkroken/Docker-idempotent-update/commit/4e21c8a123d110ffaa369a337ff9bac9de872a08))
* use centrally resolved Gamnacken client ID ([77f34d9](https://github.com/Avkroken/Docker-idempotent-update/commit/77f34d9289fd23296310387db4588f8d79d4ec50))


### Refactoring

* use central metadata orchestrator ([#411](https://github.com/Avkroken/Docker-idempotent-update/issues/411)) ([2ec9bb9](https://github.com/Avkroken/Docker-idempotent-update/commit/2ec9bb9511595f2ea27ce1b66104ad7a8e520854))


### Documentation

* align AGENTS merge policy ([#156](https://github.com/Avkroken/Docker-idempotent-update/issues/156)) ([6bf8eb9](https://github.com/Avkroken/Docker-idempotent-update/commit/6bf8eb96270a9ab8cf78cb3a74459b03cf19b9e2))
* align AGENTS merge policy with repository settings ([6bf8eb9](https://github.com/Avkroken/Docker-idempotent-update/commit/6bf8eb96270a9ab8cf78cb3a74459b03cf19b9e2))
* align CI merge policy ([#157](https://github.com/Avkroken/Docker-idempotent-update/issues/157)) ([df3d48e](https://github.com/Avkroken/Docker-idempotent-update/commit/df3d48e13f55ce9064f4142805dfc856797f59a4))
* align governance and CI documentation ([#400](https://github.com/Avkroken/Docker-idempotent-update/issues/400)) ([9877485](https://github.com/Avkroken/Docker-idempotent-update/commit/9877485fa0a0b018b5b4bac46079b4a08cd2e52c))
* centralize agent policy ([#399](https://github.com/Avkroken/Docker-idempotent-update/issues/399)) ([e8a987f](https://github.com/Avkroken/Docker-idempotent-update/commit/e8a987fa18aeda4a46fb02a5c17022484eda511c))
* frys PR-scope efter öppning ([c12c06a](https://github.com/Avkroken/Docker-idempotent-update/commit/c12c06a6a630f01881606f015491c52852c181af))
* rätta agent-reglerna som motsade praktiken ([a782e77](https://github.com/Avkroken/Docker-idempotent-update/commit/a782e775a9399dcabe08d4dd0e73559bbd31ff61))
* rätta agent-reglerna som motsade praktiken ([#142](https://github.com/Avkroken/Docker-idempotent-update/issues/142)) ([8746d86](https://github.com/Avkroken/Docker-idempotent-update/commit/8746d8633711cb8d75f6914420de6cef4813b993))
* skärp PR-gates och auto-merge ([#173](https://github.com/Avkroken/Docker-idempotent-update/issues/173)) ([cf0860f](https://github.com/Avkroken/Docker-idempotent-update/commit/cf0860ffcd1fff4e57a49f1f9df8eaa1d2984339))
* skriv in svarsformatet från i-have-adhd i AGENTS.md ([a0af29b](https://github.com/Avkroken/Docker-idempotent-update/commit/a0af29b1f31c69a0f9cef477b0757928b54441c7))
* skriv in svarsformatet från i-have-adhd i AGENTS.md ([#141](https://github.com/Avkroken/Docker-idempotent-update/issues/141)) ([2ee5687](https://github.com/Avkroken/Docker-idempotent-update/commit/2ee5687ba3456ad10184c9442695a5eca3d82fa7))
* standardize bug issue form ([743a2f0](https://github.com/Avkroken/Docker-idempotent-update/commit/743a2f0ec5bbb9ed9e600e8736284457f0b9e403))
* unify community health files ([#401](https://github.com/Avkroken/Docker-idempotent-update/issues/401)) ([743a2f0](https://github.com/Avkroken/Docker-idempotent-update/commit/743a2f0ec5bbb9ed9e600e8736284457f0b9e403))
