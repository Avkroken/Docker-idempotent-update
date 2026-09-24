#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
from pathlib import Path
import yaml

workflow_dir = Path('.github/workflows')
workflows = {path.name: yaml.safe_load(path.read_text()) for path in workflow_dir.glob('*.yml')}
assert set(workflows) == {
    'auto-assign.yml',
    'dependabot-automerge.yml',
    'docker-publish.yml',
    'labeler.yml',
    'python-app.yml',
    'repository-policy.yml',
}

auto_assign = workflows['auto-assign.yml']
assert auto_assign['name'] == 'Auto assign issues and pull requests'
assert auto_assign[True]['issues']['types'] == ['opened', 'reopened']
assert auto_assign[True]['pull_request_target']['types'] == ['opened', 'reopened']
assert auto_assign['permissions'] == {}
assign = auto_assign['jobs']['assign']
assert assign['permissions'] == {'issues': 'write', 'pull-requests': 'write'}
assert assign['runs-on'] == 'ubuntu-latest'
assert 'uses' not in assign
assert 'gh api' in assign['steps'][0]['run']

policy = workflows['repository-policy.yml']
assert policy['name'] == 'Repository policy'
assert policy['permissions'] == {'contents': 'read'}
assert set(policy['jobs']) == {'dependency-review', 'python', 'docker', 'policy'}
assert policy['jobs']['policy']['name'] == 'Repository policy'

assert not Path('.github/rulesets/main.json').exists()

for workflow in workflows.values():
    for job in workflow['jobs'].values():
        if 'uses' in job:
            ref = job['uses'].rsplit('@', 1)[1]
            assert len(ref) == 40 and all(char in '0123456789abcdef' for char in ref)
        for step in job.get('steps', []):
            if 'uses' in step:
                ref = step['uses'].rsplit('@', 1)[1]
                assert len(ref) == 40 and all(char in '0123456789abcdef' for char in ref)
            if step.get('uses', '').startswith('actions/checkout@'):
                assert step.get('with', {}).get('persist-credentials') is False
PY

python3 -m compileall -q src plex-clear-watchlist
