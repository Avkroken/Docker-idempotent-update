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
    'agent-automerge.yml',
    'auto-assign.yml',
    'ci.yml',
    'codeql.yml',
    'dependabot-automerge.yml',
    'docker-publish.yml',
    'labeler.yml',
    'pr-title.yml',
    'release.yml',
    'wiki-sync.yml',
}

ci = workflows['ci.yml']
assert ci['name'] == 'CI'
assert ci['permissions'] == {'contents': 'read'}
assert set(ci['jobs']) == {'dependency-review', 'python', 'docker'}
assert ci['jobs']['dependency-review']['name'] == 'Dependency review'
assert ci['jobs']['python']['name'] == 'Python'
assert ci['jobs']['docker']['name'] == 'Docker'

codeql = workflows['codeql.yml']
assert codeql['name'] == 'CodeQL'
assert codeql['permissions'] == {
    'contents': 'read',
    'security-events': 'write',
    'actions': 'read',
}
analyze = codeql['jobs']['analyze']
assert analyze['runs-on'] == 'ubuntu-latest'
assert set(analyze['strategy']['matrix']['language']) == {'actions', 'python'}

agent_automerge = workflows['agent-automerge.yml']
assert agent_automerge['name'] == 'Agent auto-merge'
assert set(agent_automerge[True]) == {
    'pull_request',
    'pull_request_review',
    'pull_request_review_comment',
    'check_run',
    'push',
    'schedule',
    'workflow_dispatch',
}
assert agent_automerge[True]['check_run']['types'] == ['completed']
assert agent_automerge['permissions'] == {}
agent_job = agent_automerge['jobs']['agent-auto-merge']
assert agent_job['permissions'] == {
    'checks': 'read',
    'contents': 'write',
    'pull-requests': 'write',
}
assert agent_job['uses'] == 'Avkroken/.github/.github/workflows/agent-automerge-policy.yml@e853bde6e0e8c88e8d8df2709cf3e2d61ddc396c'

auto_assign = workflows['auto-assign.yml']
assert auto_assign['name'] == 'Auto assign issues and pull requests'
assign = auto_assign['jobs']['assign']
assert assign['permissions'] == {'issues': 'write', 'pull-requests': 'write'}
assert assign['runs-on'] == 'ubuntu-latest'
assert 'uses' not in assign
assert 'gh api' in assign['steps'][0]['run']

docker_publish = workflows['docker-publish.yml']
assert 'pull_request' not in docker_publish[True]
assert set(docker_publish[True]) == {'schedule', 'push', 'workflow_call'}

pr_title = workflows['pr-title.yml']
assert pr_title['name'] == 'PR title'
assert pr_title['permissions'] == {}
assert set(pr_title[True]) == {'merge_group', 'pull_request'}
assert set(pr_title['jobs']) == {'conventional-title'}
title_job = pr_title['jobs']['conventional-title']
assert title_job['name'] == 'Conventional PR title'
assert title_job['runs-on'] == 'ubuntu-latest'
assert 'uses' not in title_job
assert all('uses' not in step for step in title_job['steps'])
assert not any('secrets.' in str(step) for step in title_job['steps'])

release = workflows['release.yml']
assert release['name'] == 'Release'
assert release['permissions'] == {'contents': 'read'}
assert set(release[True]) == {'pull_request', 'push', 'workflow_dispatch'}
assert set(release['jobs']) == {'validate', 'release', 'publish-container'}
assert release['jobs']['validate']['name'] == 'Validate semantic release'
release_job = release['jobs']['release']
assert release_job['name'] == 'Semantic release'
assert release_job['permissions'] == {
    'actions': 'read',
    'checks': 'read',
    'contents': 'write',
    'statuses': 'read',
}
assert release_job['concurrency'] == {
    'group': "${{ format('semantic-release-{0}', github.repository) }}",
    'cancel-in-progress': False,
}
assert release_job['steps'][0]['name'] == 'Checkout repository'
assert all(step.get('name') != 'Wait for release turn' for step in release_job['steps'])

wiki_sync = workflows['wiki-sync.yml']
assert wiki_sync['name'] == 'Sync repository Wiki'
assert 'pull_request' not in wiki_sync[True]
assert set(wiki_sync[True]) == {'workflow_dispatch', 'push'}
assert wiki_sync['jobs']['sync']['permissions'] == {'contents': 'write'}

for workflow in workflows.values():
    for job in workflow['jobs'].values():
        if 'uses' in job:
            uses = job['uses']
            if uses.startswith('./.github/workflows/'):
                assert '@' not in uses
            else:
                ref = uses.rsplit('@', 1)[1]
                assert len(ref) == 40 and all(char in '0123456789abcdef' for char in ref)
        for step in job.get('steps', []):
            if 'uses' in step:
                ref = step['uses'].rsplit('@', 1)[1]
                assert len(ref) == 40 and all(char in '0123456789abcdef' for char in ref)
            if step.get('uses', '').startswith('actions/checkout@'):
                assert step.get('with', {}).get('persist-credentials') is False
PY

python3 -m compileall -q src plex-clear-watchlist
