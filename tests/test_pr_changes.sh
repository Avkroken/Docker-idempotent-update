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
    'ci.yml',
    'dependabot-automerge.yml',
    'docker-publish.yml',
    'labeler.yml',
    'pr-title.yml',
    'wiki-sync.yml',
}

ci = workflows['ci.yml']
assert ci['name'] == 'CI'
assert ci['permissions'] == {'contents': 'read'}
assert set(ci['jobs']) == {'dependency-review', 'python', 'docker'}
assert ci['jobs']['dependency-review']['name'] == 'Dependency review'
assert ci['jobs']['python']['name'] == 'Python'
assert ci['jobs']['docker']['name'] == 'Docker'

auto_assign = workflows['auto-assign.yml']
assert auto_assign['name'] == 'Auto assign issues and pull requests'
assign = auto_assign['jobs']['assign']
assert assign['permissions'] == {'issues': 'write', 'pull-requests': 'write'}
assert assign['runs-on'] == 'ubuntu-latest'
assert 'uses' not in assign
assert 'gh api' in assign['steps'][0]['run']

docker_publish = workflows['docker-publish.yml']
assert 'pull_request' not in docker_publish[True]
assert set(docker_publish[True]) == {'schedule', 'push'}

pr_title = workflows['pr-title.yml']
assert pr_title['name'] == 'PR title'
assert pr_title['permissions'] == {}
assert set(pr_title[True]) == {'pull_request'}
assert set(pr_title['jobs']) == {'conventional-title'}
title_job = pr_title['jobs']['conventional-title']
assert title_job['name'] == 'Conventional PR title'
assert title_job['runs-on'] == 'ubuntu-latest'
assert 'uses' not in title_job
assert all('uses' not in step for step in title_job['steps'])
assert not any('secrets.' in str(step) for step in title_job['steps'])

wiki_sync = workflows['wiki-sync.yml']
assert wiki_sync['name'] == 'Sync repository Wiki'
assert 'pull_request' not in wiki_sync[True]
assert set(wiki_sync[True]) == {'workflow_dispatch', 'push'}
assert wiki_sync['jobs']['sync']['permissions'] == {'contents': 'write'}

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
