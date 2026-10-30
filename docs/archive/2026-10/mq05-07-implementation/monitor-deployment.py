#!/usr/bin/env python3
"""Read-only deployment observer; retain failed reads and resume after interruption."""
from pathlib import Path
import datetime
import json
import subprocess
import time

A = Path(__file__).resolve().parent
Q = A / 'deployment-monitor'
Q.mkdir(exist_ok=True)
REPO = 'repos/linhongcun/video-studio'
SHA = 'dcaafde2e30c7fde688e0744d45f2e4e1131c46e'
history = Q / 'observations.json'
events = json.loads(history.read_text()) if history.exists() else []


def read(path, n, label):
    row = {'atUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'path': path}
    try:
        r = subprocess.run(['gh', 'api', path], capture_output=True, text=True, timeout=35)
        row.update(clientExit=r.returncode, stderr=r.stderr)
        try:
            row['response'] = json.loads(r.stdout)
        except json.JSONDecodeError:
            row['responseParseError'] = True
    except subprocess.TimeoutExpired:
        row['clientTimeout'] = True
    (Q / f'{n:03d}-{label}.json').write_text(json.dumps(row, ensure_ascii=False, indent=2) + '\n')
    return row.get('response') if row.get('clientExit') == 0 else None


start = max((int(p.name.split('-')[0]) for p in Q.glob('[0-9]*-run.json')), default=0) + 1
for n in range(start, start + 60):
    run = read(REPO + '/actions/runs/41100736996', n, 'run')
    checks = read(REPO + '/check-suites/111416124100/check-runs', n, 'checks')
    deps = read(REPO + '/deployments?environment=github-pages&per_page=1', n, 'deployments')
    statuses = None
    if isinstance(deps, list) and deps and deps[0]['sha'] == SHA:
        statuses = read(deps[0]['statuses_url'], n, 'deployment-statuses')
    jobs = checks.get('check_runs', []) if isinstance(checks, dict) else []
    detail = {'attempt': n, 'atUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'run': {k: run.get(k) for k in ['status', 'conclusion']} if run else None,
              'checks': [{k: j.get(k) for k in ['name', 'status', 'conclusion']} for j in jobs],
              'deploymentLatestState': statuses[0].get('state') if statuses else None}
    events.append(detail)
    history.write_text(json.dumps(events, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(detail), flush=True)
    workflow_ok = run and run.get('conclusion') == 'success'
    direct_ok = (jobs and all(j.get('status') == 'completed' and j.get('conclusion') == 'success' for j in jobs)
                 and statuses and statuses[0]['state'] == 'success')
    if workflow_ok or direct_ok:
        assert run and run['head_sha'] == SHA
        detail.update(passed=True, acceptance='Post-Release workflow success' if workflow_ok
                      else 'All concrete workflow checks and matching Pages deployment successful; high-level run may lag')
        (Q / 'accepted.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2) + '\n')
        break
    assert not any(j.get('conclusion') in ['failure', 'timed_out', 'action_required'] for j in jobs), 'Actual check failed'
    assert not run or run.get('conclusion') not in ['failure', 'timed_out', 'cancelled', 'action_required'], 'Actual target run failed'
    time.sleep(30)
else:
    raise RuntimeError('Observation window elapsed; no success claimed')
