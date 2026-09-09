#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
import json
from pathlib import Path

import yaml

workflow_dir = Path('.github/workflows')
workflows = {path.name: yaml.safe_load(path.read_text()) for path in workflow_dir.glob('*.yml')}
assert set(workflows) == {'dependency-review.yml', 'docker-publish.yml', 'python-app.yml'}

for filename, workflow in workflows.items():
    permissions = workflow['permissions'] if 'permissions' in workflow else workflow['jobs']['build']['permissions']
    assert permissions['contents'] == 'read', filename
    assert 'pull_request' in workflow[True], filename
    assert workflow[True]['pull_request']['branches'] == ['main'], filename

assert workflows['python-app.yml']['name'] == 'Python application'
assert set(workflows['python-app.yml']['jobs']) == {'build'}
assert workflows['dependency-review.yml']['name'] == 'Dependency review'
assert set(workflows['dependency-review.yml']['jobs']) == {'dependency-review'}
assert workflows['docker-publish.yml']['name'] == 'Docker'
assert set(workflows['docker-publish.yml']['jobs']) == {'build', 'publish'}
assert workflows['docker-publish.yml']['jobs']['build']['permissions'] == {'contents': 'read'}
assert workflows['docker-publish.yml']['jobs']['publish']['permissions'] == {
    'contents': 'read',
    'packages': 'write',
    'id-token': 'write',
}
assert workflows['docker-publish.yml']['env']['IMAGE_NAME'] == 'avkroken/plex-clear-watchlist'

with Path('.github/dependabot.yml').open() as stream:
    dependabot = yaml.safe_load(stream)
assert dependabot['version'] == 2
assert {(item['package-ecosystem'], item['directory']) for item in dependabot['updates']} == {
    ('pip', '/plex-clear-watchlist'),
    ('docker', '/plex-clear-watchlist'),
    ('github-actions', '/'),
}

with Path('.github/rulesets/main.json').open() as stream:
    ruleset = json.load(stream)
assert ruleset['target'] == 'branch'
assert ruleset['conditions']['ref_name']['include'] == ['~DEFAULT_BRANCH']
assert [rule['type'] for rule in ruleset['rules']] == ['required_status_checks']
contexts = ruleset['rules'][0]['parameters']['required_status_checks']
assert [item['context'] for item in contexts] == [
    'Python application / build',
    'Dependency review / dependency-review',
]

for workflow in workflows.values():
    for job in workflow['jobs'].values():
        for step in job.get('steps', []):
            if 'uses' in step:
                ref = step['uses'].rsplit('@', 1)[1]
                assert len(ref) == 40 and all(char in '0123456789abcdef' for char in ref)
            if step.get('uses', '').startswith('actions/checkout@'):
                assert step.get('with', {}).get('persist-credentials') is False
PY

python3 -m compileall -q src plex-clear-watchlist
