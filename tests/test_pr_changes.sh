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
}

# Pull-request gates are organization rulesets. Local CI remains only for
# post-merge validation and publishing.
python_app = workflows['python-app.yml']
assert python_app['name'] == 'Python application'
assert python_app['permissions'] == {'contents': 'read'}
assert python_app[True] == {'push': {'branches': ['main']}}
assert set(python_app['jobs']) == {'build'}

docker_publish = workflows['docker-publish.yml']
assert docker_publish['name'] == 'Docker'
assert 'pull_request' not in docker_publish[True]
assert set(docker_publish[True]) == {'schedule', 'push'}
assert set(docker_publish['jobs']) == {'publish'}
publish = docker_publish['jobs']['publish']
assert publish['permissions'] == {'contents': 'read', 'packages': 'write'}
assert docker_publish['env']['IMAGE_NAME'] == 'avkroken/plex-clear-watchlist'
assert {step['uses'] for step in publish['steps'] if 'uses' in step} == {
    'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1',
    'docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e',
    'docker/login-action@dbcb813823bdd20940b903addbd779551569679f',
    'docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302',
    'docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a',
}

automerge = workflows['dependabot-automerge.yml']
assert automerge['name'] == 'Dependabot auto-merge'
assert automerge[True] == 'pull_request'
assert automerge['permissions'] == {'contents': 'write', 'pull-requests': 'write'}
assert set(automerge['jobs']) == {'dependabot'}
assert not any('uses' in step for step in automerge['jobs']['dependabot']['steps'])

labeler = workflows['labeler.yml']
assert labeler['name'] == 'Pull Request Labeler'
assert labeler[True]['pull_request_target']['types'] == [
    'opened',
    'synchronize',
    'reopened',
    'ready_for_review',
]
assert labeler['permissions'] == {
    'contents': 'read',
    'issues': 'write',
    'pull-requests': 'write',
}
assert set(labeler['jobs']) == {'triage'}

auto_assign = workflows['auto-assign.yml']
assert auto_assign['name'] == 'Auto assign issues and pull requests'
assert auto_assign[True]['issues']['types'] == ['opened', 'reopened']
assert auto_assign[True]['pull_request_target']['types'] == ['opened', 'reopened']
assert auto_assign['permissions'] == {}
assert set(auto_assign['jobs']) == {'assign'}
assign = auto_assign['jobs']['assign']
assert assign['permissions'] == {'issues': 'write'}
assert assign['uses'] == (
    'Avkroken/.github/.github/workflows/reusable-auto-assign.yml'
    '@960eec40fe1d6e5be88da27f7b6b75adff64f4fb'
)

# Ruleset policy is organization-level and must not be shadowed by a stale
# repository-local JSON export.
assert not Path('.github/rulesets/main.json').exists()

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
assert set(labeler_config) == {'documentation', 'enhancement'}

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
