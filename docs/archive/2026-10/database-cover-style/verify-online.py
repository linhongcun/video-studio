#!/usr/bin/env python3
"""Complete canonical GET verification for the four published database covers.

--prepare writes a local-only expected-asset plan and makes no network requests.
Actual verification requires a successful workflow_dispatch status JSON bound to
the exact merge commit. All output remains under /workspace/work.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path('/workspace/video-studio')
OUT = Path('/workspace/work/database-online')
BASE = 'https://linhongcun.github.io/video-studio/'
RAW = 'https://raw.githubusercontent.com/linhongcun/video-studio/'
RELEASE = 'v0.81.1'
CATALOG = ROOT / 'episodes-codex/_shared/database-covers/catalog.json'
DELIVERY = 'design/database-covers-20261027/'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def local_jobs():
    catalog = json.loads(CATALOG.read_text())
    episodes = catalog['episodes']
    assert len(episodes) == 4 and {e['slug'] for e in episodes} == {'db-index', 'db-transaction', 'db-lock', 'db-replication'}
    jobs = []
    for ep in episodes:
        slug = ep['slug']
        assert re.fullmatch(r'[a-z0-9-]+', slug)
        prefix = 'episodes/' + slug + '/'
        for name in ['cover-16x9.jpg', 'video.mp4']:
            local = ROOT / prefix / name
            jobs.append({'path': prefix + name, 'sha256': digest(local),
                         'localPath': str(local), 'kind': 'bytes', 'surface': 'pages'})
        local = ROOT / 'site/dist' / prefix / 'captions.vtt'
        # A missing VTT is an error; never silently reduce the requested scope.
        jobs.append({'path': prefix + 'captions.vtt', 'sha256': digest(local),
                     'localPath': str(local), 'kind': 'bytes', 'surface': 'pages'})
        jobs.append({'path': prefix, 'contains': [prefix + 'cover-16x9.jpg'],
                     'kind': 'page', 'surface': 'pages'})
    jobs.append({'path': 'series/database/',
                 'contains': ['episodes/' + e['slug'] + '/' for e in episodes],
                 'kind': 'page', 'surface': 'pages'})
    jobs.append({'path': 'changelog/', 'contains': [RELEASE],
                 'kind': 'page', 'surface': 'pages'})
    assert len(jobs) == 18
    for name in ['database-covers-4-episodes.zip', 'database-covers-preview.png']:
        local = ROOT / DELIVERY / name
        jobs.append({'path': DELIVERY + name, 'sha256': digest(local),
                     'localPath': str(local), 'kind': 'bytes', 'surface': 'github-raw'})
    assert len(jobs) == 20
    return jobs


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def fetch(job):
    result = {'url': job['url'], 'path': job['path'], 'kind': job['kind'],
              'surface': job['surface']}
    try:
        request = urllib.request.Request(job['url'], headers={
            'User-Agent': 'video-studio-database-cover-verification'})
        retained = []
        h = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(request, timeout=90) as response:
            while block := response.read(1024 * 1024):
                h.update(block)
                size += len(block)
                if job['kind'] == 'page' or job['path'].endswith('.jpg'):
                    retained.append(block)
            result.update(status=response.status, bytes=size,
                          sha256=h.hexdigest(), finalUrl=response.url)
        if job['kind'] == 'bytes':
            result['expectedSha256'] = job['sha256']
            result['passed'] = result['status'] == 200 and h.hexdigest() == job['sha256']
        else:
            text = b''.join(retained).decode('utf-8')
            result['missing'] = [x for x in job['contains'] if x not in text]
            result['passed'] = result['status'] == 200 and not result['missing']
        if job['path'].endswith('.jpg'):
            dest = OUT / Path(job['path']).parent.name
            dest.mkdir(exist_ok=True)
            (dest / 'cover-16x9.jpg').write_bytes(b''.join(retained))
    except Exception as exc:
        result.update(passed=False, error=f'{type(exc).__name__}: {exc}')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--merge-sha')
    parser.add_argument('--run-id', type=int)
    parser.add_argument('--deployment-status-file', type=Path)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    jobs = local_jobs()
    local_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                         text=True).strip()
    if args.prepare:
        plan = {'preparedAt': now().isoformat(), 'release': RELEASE,
                'localHead': local_head, 'catalogSha256': digest(CATALOG),
                'pagesRequests': 18, 'rawRequests': 2, 'requestCount': 20,
                'jobs': jobs, 'networkRequestsExecuted': 0}
        target = OUT / 'expected-assets.json'
        target.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'prepared': True, 'networkRequestsExecuted': 0,
                          'requestsPlanned': 20, 'plan': str(target)}))
        return
    if not args.merge_sha or not re.fullmatch('[0-9a-f]{40}', args.merge_sha):
        parser.error('--merge-sha must be the exact 40-character merged commit SHA')
    if not args.run_id or not args.deployment_status_file:
        parser.error('--run-id and --deployment-status-file are required')
    deployment = json.loads(args.deployment_status_file.read_text())
    assert deployment['headSha'] == args.merge_sha, 'deployment HEAD mismatch'
    assert deployment['event'] == 'workflow_dispatch', 'not the requested manual deployment'
    assert deployment['status'] == 'completed' and deployment['conclusion'] == 'success', 'deployment not successful'
    assert deployment['databaseId'] == args.run_id, 'deployment ID mismatch'
    prepared_path = OUT / 'expected-assets.json'
    prepared = json.loads(prepared_path.read_text())
    assert prepared['catalogSha256'] == digest(CATALOG), 'catalog changed since preparation'
    assert prepared['jobs'] == jobs, 'local publication inputs changed; prepare a new explicit plan'
    for job in jobs:
        job['url'] = (BASE if job['surface'] == 'pages' else RAW + args.merge_sha + '/') + job['path']
    started = now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, jobs))
    finished = now()
    report = {'checkedAt': finished.isoformat(), 'startedAt': started.isoformat(),
              'checkedAtAsiaShanghai': finished.astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'method': 'complete canonical HTTPS GET with default TLS verification; no range or cache-busting query',
              'release': RELEASE, 'deploymentRunId': args.run_id,
              'deploymentHead': args.merge_sha, 'deployment': deployment,
              'localHeadAtVerification': local_head,
              'expectedPlanSha256': digest(prepared_path),
              'requests': results, 'passed': all(r['passed'] for r in results),
              'requestCount': len(results), 'pagesRequestCount': 18,
              'rawRequestCount': 2, 'totalBytes': sum(r.get('bytes', 0) for r in results)}
    path = OUT / ('report-' + finished.strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if report['passed']:
        (OUT / 'online-verification.json').write_text(path.read_text())
    print(json.dumps({'passed': report['passed'], 'requests': len(results),
                      'bytes': report['totalBytes'], 'failed': [r for r in results if not r['passed']],
                      'report': str(path)}, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
