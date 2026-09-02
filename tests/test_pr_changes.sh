#!/usr/bin/env bash
# Tests for PR-changed configuration and documentation files.
# Validates YAML syntax, JSON structure, GitHub workflow fields, and Markdown content.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

assert_contains() {
    local file="$1" pattern="$2" label="$3"
    if grep -qF -- "$pattern" "$file"; then pass "$label"; else fail "$label (pattern not found: $pattern)"; fi
}

assert_not_contains() {
    local file="$1" pattern="$2" label="$3"
    if ! grep -qF -- "$pattern" "$file"; then pass "$label"; else fail "$label (unexpected pattern found: $pattern)"; fi
}

assert_yaml_field() {
    local file="$1" py_expr="$2" expected="$3" label="$4" actual
    if ! actual="$(python3 -c "import yaml; data = yaml.safe_load(open('$file')); result = $py_expr; print(str(result))" 2>/dev/null)"; then
        fail "$label (YAML/Python evaluation failed)"
        return
    fi
    if [ "$actual" = "$expected" ]; then pass "$label"; else fail "$label (expected '$expected', got '$actual')"; fi
}

echo "=== YAML syntax validation ==="
for f in \
    ".github/ISSUE_TEMPLATE/bug_report.yml" \
    ".github/ISSUE_TEMPLATE/config.yml" \
    ".github/ISSUE_TEMPLATE/feature_request.yml" \
    ".github/workflows/ci.yml"
do
    full="$REPO_ROOT/$f"
    if python3 -c "import yaml; yaml.safe_load(open('$full'))" 2>/dev/null; then pass "$f is valid YAML"; else fail "$f is valid YAML"; fi
done

echo "=== bug_report.yml: GitHub issue form structure ==="
BUG="$REPO_ROOT/.github/ISSUE_TEMPLATE/bug_report.yml"
assert_yaml_field "$BUG" "data['name']" "Bug report" "bug_report: name is 'Bug report'"
assert_yaml_field "$BUG" "data['title']" "bug: " "bug_report: title prefix is 'bug: '"
assert_yaml_field "$BUG" "data['labels'][0]" "bug" "bug_report: first label is 'bug'"
assert_yaml_field "$BUG" "str([f['id'] for f in data['body'] if f.get('type')=='textarea'])" "['description', 'steps', 'expected', 'environment']" "bug_report: textarea field IDs are description, steps, expected, environment"
assert_yaml_field "$BUG" "str([f['id'] for f in data['body'] if f.get('validations', {}).get('required')])" "['description', 'steps', 'expected']" "bug_report: required fields are description, steps, expected"
assert_yaml_field "$BUG" "str(any(f.get('validations', {}).get('required') for f in data['body'] if f.get('id')=='environment'))" "False" "bug_report: environment field is optional (not required)"
assert_contains "$BUG" "1." "bug_report: steps placeholder starts numbered list"

echo "=== config.yml: issue template config ==="
CONFIG="$REPO_ROOT/.github/ISSUE_TEMPLATE/config.yml"
assert_yaml_field "$CONFIG" "data['blank_issues_enabled']" "False" "config: blank_issues_enabled is false"
assert_yaml_field "$CONFIG" "str(data['contact_links'])" "[]" "config: contact_links is empty list"

echo "=== feature_request.yml: GitHub issue form structure ==="
FEAT="$REPO_ROOT/.github/ISSUE_TEMPLATE/feature_request.yml"
assert_yaml_field "$FEAT" "data['name']" "Feature request" "feature_request: name is 'Feature request'"
assert_yaml_field "$FEAT" "data['title']" "feat: " "feature_request: title prefix is 'feat: '"
assert_yaml_field "$FEAT" "data['labels'][0]" "enhancement" "feature_request: first label is 'enhancement'"
assert_yaml_field "$FEAT" "str([f['id'] for f in data['body'] if f.get('validations', {}).get('required')])" "['problem', 'proposal']" "feature_request: required fields are problem and proposal"
assert_yaml_field "$FEAT" "str(any(f.get('id')=='alternatives' for f in data['body']))" "True" "feature_request: alternatives field exists"
assert_yaml_field "$FEAT" "str(any(f.get('validations', {}).get('required') for f in data['body'] if f.get('id')=='alternatives'))" "False" "feature_request: alternatives field is optional"

echo "=== pull_request_template.md: required sections and checklist ==="
PRTEMPLATE="$REPO_ROOT/.github/pull_request_template.md"
assert_contains "$PRTEMPLATE" "## Summary" "pr_template: has Summary section"
assert_contains "$PRTEMPLATE" "## Testing" "pr_template: has Testing section"
assert_contains "$PRTEMPLATE" "## Checklist" "pr_template: has Checklist section"
assert_contains "$PRTEMPLATE" "Tests pass locally" "pr_template: has 'Tests pass locally' checklist item"
assert_contains "$PRTEMPLATE" "PR is focused and isolated" "pr_template: has 'PR is focused and isolated' checklist item"
assert_contains "$PRTEMPLATE" "No unrelated changes are included" "pr_template: has 'No unrelated changes are included' checklist item"
assert_contains "$PRTEMPLATE" "No credentials or secrets are committed" "pr_template: has 'No credentials or secrets are committed' checklist item"
assert_contains "$PRTEMPLATE" "- [ ]" "pr_template: uses unchecked task list syntax"
assert_contains "$PRTEMPLATE" "-" "pr_template: Summary section has content placeholder"

echo "=== dependabot.yml: Dependabot configuration ==="
DEPENDABOT="$REPO_ROOT/.github/dependabot.yml"
if python3 -c "import yaml; yaml.safe_load(open('$DEPENDABOT'))" 2>/dev/null; then pass "dependabot.yml is valid YAML"; else fail "dependabot.yml is valid YAML"; fi
assert_yaml_field "$DEPENDABOT" "data['version']" "2" "dependabot.yml: version is 2"
assert_yaml_field "$DEPENDABOT" "str('github-actions' in [u['package-ecosystem'] for u in data['updates']])" "True" "dependabot.yml: github-actions ecosystem present"
assert_yaml_field "$DEPENDABOT" "str(all('schedule' in u and 'interval' in u['schedule'] for u in data['updates']))" "True" "dependabot.yml: all updates have schedule.interval"

echo "=== ci.yml: GitHub Actions workflow structure ==="
CI="$REPO_ROOT/.github/workflows/ci.yml"
assert_yaml_field "$CI" "data['name']" "CI" "ci.yml: workflow name is CI"
assert_yaml_field "$CI" "str('pull_request' in data[True])" "True" "ci.yml: triggered on pull_request"
assert_yaml_field "$CI" "str('merge_group' in data[True])" "True" "ci.yml: triggered for merge queue checks"
assert_yaml_field "$CI" "str(data[True]['push']['branches'])" "['main']" "ci.yml: push trigger limited to main branch"
assert_yaml_field "$CI" "data['permissions']['contents']" "read" "ci.yml: permissions.contents is read"
assert_yaml_field "$CI" "str(set(data['jobs']) == {'required'})" "True" "ci.yml: defines only required job"
assert_yaml_field "$CI" "data['jobs']['required']['name']" "CI / required" "ci.yml: required context is stable"
assert_yaml_field "$CI" "data['jobs']['required']['runs-on']" "ubuntu-latest" "ci.yml: required job runs on ubuntu-latest"
assert_yaml_field "$CI" "str(any('ruff check src/' in str(s.get('run','')) and 'plex-clear-watchlist/' not in str(s.get('run','')) for s in data['jobs']['required']['steps']))" "True" "ci.yml: Ruff preserves established root src scope"
assert_yaml_field "$CI" "str(any('python -m compileall -q src plex-clear-watchlist' in str(s.get('run','')) for s in data['jobs']['required']['steps']))" "True" "ci.yml: compiles both Python trees"
assert_yaml_field "$CI" "str(any('bash tests/test_pr_changes.sh' in str(s.get('run','')) for s in data['jobs']['required']['steps']))" "True" "ci.yml: runs repository test harness"

echo "=== AGENTS.md: authoritative managed policy ==="
AGENTS="$REPO_ROOT/AGENTS.md"
PLEX_AGENTS="$REPO_ROOT/plex-clear-watchlist/AGENTS.md"
assert_contains "$AGENTS" "<!-- AVKROKEN-COMMON:START -->" "AGENTS.md: has managed common start marker"
assert_contains "$AGENTS" "<!-- AVKROKEN-COMMON:END -->" "AGENTS.md: has managed common end marker"
assert_contains "$AGENTS" "## Pre-PR quality gate" "AGENTS.md: has pre-PR quality gate"
assert_contains "$AGENTS" "## Review-signal" "AGENTS.md: has review signal policy"
assert_contains "$AGENTS" "## Pull request och merge" "AGENTS.md: has pull request and merge policy"
assert_contains "$AGENTS" 'Pusha aldrig direkt till `main`' "AGENTS.md: forbids direct pushes to main"
assert_contains "$AGENTS" "required checks/CI" "AGENTS.md: requires CI gate verification"
assert_contains "$AGENTS" "review-trådar" "AGENTS.md: requires review-thread verification"
assert_contains "$AGENTS" "Repositoryts aktuella ruleset" "AGENTS.md: live configuration selects merge method"
assert_contains "$AGENTS" "OPENAI_API_KEY" "AGENTS.md: protects external AI provider credentials"
assert_not_contains "$AGENTS" "MERGE_POLICY.md" "AGENTS.md: does not depend on a parallel merge policy file"

assert_contains "$PLEX_AGENTS" 'Repositoryövergripande arbets-, review-, säkerhets-, eskalerings- och mergepolicy finns i `/AGENTS.md`' "plex AGENTS: points to root policy"
assert_contains "$PLEX_AGENTS" 'Kodändringar för detta subtree överlämnas på `dev`' "plex AGENTS: keeps subtree dev rule"
assert_contains "$PLEX_AGENTS" 'Mergebeslut, review-gates, auto-merge och tillåten merge-metod styrs enbart av root `/AGENTS.md`' "plex AGENTS: does not duplicate global merge policy"
assert_not_contains "$PLEX_AGENTS" "Aktivera automatisk sammanfogning direkt" "plex AGENTS: legacy immediate auto-merge rule removed"
assert_not_contains "$AGENTS" "Ownership Map" "AGENTS.md: lacks ownership map"

echo "=== CLAUDE.md: pointer contract ==="
CLAUDEMD="$REPO_ROOT/CLAUDE.md"
assert_contains "$CLAUDEMD" "Läs [AGENTS.md](AGENTS.md)" "CLAUDE.md: points to authoritative AGENTS.md"
assert_contains "$CLAUDEMD" "bara en pekare" "CLAUDE.md: remains a pointer file"
assert_contains "$CLAUDEMD" "All projektvägledning står där" "CLAUDE.md: delegates project guidance to AGENTS.md"
assert_not_contains "$CLAUDEMD" "## Tech Stack" "CLAUDE.md: does not duplicate project guidance"

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then exit 1; fi
