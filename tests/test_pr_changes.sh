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
assert set(workflows) == {
    'dependabot-automerge.yml',
    'dependency-review.yml',
    'docker-publish.yml',
    'labeler.yml',
    'python-app.yml',
}

for filename in ('dependency-review.yml', 'docker-publish.yml', 'python-app.yml'):
    workflow = workflows[filename]
    permissions = workflow['permissions'] if 'permissions' in workflow else workflow['jobs']['build']['permissions']
    assert permissions['contents'] == 'read', filename
    assert 'pull_request' in workflow[True], filename
    assert workflow[True]['pull_request']['branches'] == ['main'], filename

automerge = workflows['dependabot-automerge.yml']
assert automerge['name'] == 'Dependabot auto-merge'
assert automerge[True] == 'pull_request'
assert automerge['permissions'] == {'contents': 'write', 'pull-requests': 'write'}
assert set(automerge['jobs']) == {'dependabot'}
assert not any('uses' in step for step in automerge['jobs']['dependabot']['steps'])

labeler = workflows['labeler.yml']
assert labeler['name'] == 'Pull Request Labeler'
assert labeler[True]['pull_request_target']['types'] == ['opened', 'synchronize', 'reopened']
assert labeler['permissions'] == {
    'contents': 'read',
    'issues': 'write',
    'pull-requests': 'write',
}
assert set(labeler['jobs']) == {'triage'}

assert workflows['python-app.yml']['name'] == 'Python application'
assert set(workflows['python-app.yml']['jobs']) == {'build'}
assert workflows['dependency-review.yml']['name'] == 'Dependency review'
assert set(workflows['dependency-review.yml']['jobs']) == {'dependency-review'}
assert workflows['docker-publish.yml']['name'] == 'Docker'
assert set(workflows['docker-publish.yml']['jobs']) == {'build', 'publish'}
build = workflows['docker-publish.yml']['jobs']['build']
publish = workflows['docker-publish.yml']['jobs']['publish']
assert build['permissions'] == {'contents': 'read'}
assert publish['permissions'] == {'contents': 'read', 'packages': 'write'}
assert workflows['docker-publish.yml']['env']['IMAGE_NAME'] == 'avkroken/plex-clear-watchlist'
assert {step['uses'] for step in build['steps'] if 'uses' in step} == {
    'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1',
    'docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e',
    'docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a',
}
assert {step['uses'] for step in publish['steps'] if 'uses' in step} == {
    'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1',
    'docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e',
    'docker/login-action@dbcb813823bdd20940b903addbd779551569679f',
    'docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302',
    'docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a',
}

with Path('.github/dependabot.yml').open() as stream:
    dependabot = yaml.safe_load(stream)
assert dependabot['version'] == 2
assert {(item['package-ecosystem'], item['directory']) for item in dependabot['updates']} == {
    ('pip', '/plex-clear-watchlist'),
    ('docker', '/plex-clear-watchlist'),
    ('docker-compose', '/plex-clear-watchlist'),
    ('github-actions', '/'),
}

with Path('.github/labeler.yml').open() as stream:
    labeler_config = yaml.safe_load(stream)
assert set(labeler_config) == {'python', 'tests', 'docker', 'dependencies', 'github_actions'}

with Path('.github/rulesets/main.json').open() as stream:
    ruleset = json.load(stream)
assert ruleset['target'] == 'branch'
assert ruleset['conditions']['ref_name']['include'] == ['~DEFAULT_BRANCH']
assert [rule['type'] for rule in ruleset['rules']] == ['required_status_checks']
contexts = ruleset['rules'][0]['parameters']['required_status_checks']
assert [item['context'] for item in contexts] == [
    'build',
    'dependency-review',
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
