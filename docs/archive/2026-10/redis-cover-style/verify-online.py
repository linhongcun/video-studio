#!/usr/bin/env python3
"""Prepare/verify Redis EP40 cover release using 11 full canonical HTTPS GETs.

--prepare is local-only. Live verification requires the exact merge SHA and a
completed/success workflow_dispatch run status JSON. This script never publishes,
triggers deployment, updates issues, or changes repository content.
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
OUT = Path('/workspace/work/redis-online')
BASE = 'https://linhongcun.github.io/video-studio/'
RAW = 'https://raw.githubusercontent.com/linhongcun/video-studio/'
RELEASE = 'v0.86.1'  # Planned patch; root confirms final version before prepare.
SLUG = 'redis-skiplist'
PREFIX = 'episodes/' + SLUG + '/'
META = ROOT / PREFIX / 'meta.json'
CATALOG = ROOT / 'episodes-codex/_shared/redis-covers/catalog.json'
SOURCE_PATH = 'episodes-codex/redis-skiplist/revisions/height-choice/redis-skiplist/remotion'
TITLE = 'Redis 跳表：怎样跳过一段，找到插入位置？'
VIDEO_SHA256 = '0edf23150bb3a3a00950ebb99547e09e9ede6ba9326e22d46e73d5e2e50f24f9'
VIDEO_BYTES = 7304711
DELIVERY = 'design/redis-covers-20261028/'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def local_jobs():
    meta = json.loads(META.read_text())
    catalog = json.loads(CATALOG.read_text())
    package = json.loads((ROOT / 'site/package.json').read_text())
    assert package['version'] == RELEASE.removeprefix('v'), 'local package version differs from requested release'
    assert meta['slug'] == SLUG and meta['ep'] == 40 and meta['series'] == 'redis'
    assert meta['sourcePath'] == SOURCE_PATH and meta['title'] == TITLE and meta['draft'] is False
    assert meta['poster'] == 'cover-16x9.jpg' and meta['video'] == 'video.mp4'
    assert catalog['series'] == 'redis' and len(catalog['episodes']) == 1
    assert catalog['episodes'][0]['slug'] == SLUG and catalog['episodes'][0]['ep'] == 40
    assert catalog['episodes'][0]['sourceTitle'] == TITLE
    video = ROOT / PREFIX / 'video.mp4'
    assert video.stat().st_size == VIDEO_BYTES and digest(video) == VIDEO_SHA256, 'cover-only task must preserve original video bytes'
    jobs = []
    for name in ['video.mp4', 'cover-16x9.jpg', 'captions.vtt']:
        built = ROOT / 'site/dist' / PREFIX / name
        local = built if name == 'captions.vtt' else ROOT / PREFIX / name
        expected = digest(local)
        assert digest(built) == expected, 'built publication asset differs: ' + name
        jobs.append({'path': PREFIX + name, 'sha256': expected,
                     'localPath': str(local), 'kind': 'bytes', 'surface': 'pages'})
    assert len(jobs) == 3
    pages = [
        (PREFIX, [TITLE, RELEASE, 'series/redis/', PREFIX + 'cover-16x9.jpg', SOURCE_PATH]),
        ('series/redis/', ['Redis', TITLE, RELEASE, PREFIX]),
        ('', ['Redis', TITLE, RELEASE, 'track-redis']),
        ('learn/', ['Redis', TITLE, RELEASE, 'series/redis/', 'id="redis"']),
        ('library/', ['Redis', TITLE, RELEASE, 'value="redis"', 'data-series="redis"']),
        ('changelog/', ['Redis', RELEASE,
                        'https://github.com/linhongcun/video-studio/releases/tag/' + RELEASE]),
    ]
    for path, contains in pages:
        local_page = ROOT / 'site/dist' / path / 'index.html'
        local_text = local_page.read_text()
        if path != 'changelog/':
            assert all(value in local_text for value in contains), 'local page evidence missing: ' + (path or '/')
        jobs.append({'path': path, 'contains': contains,
                     'kind': 'page', 'surface': 'pages'})
    assert len(jobs) == 9
    for name in ['redis-covers.zip', 'redis-preview.png']:
        local = ROOT / DELIVERY / name
        jobs.append({'path': DELIVERY + name, 'sha256': digest(local),
                     'localPath': str(local), 'kind': 'bytes', 'surface': 'github-raw'})
    assert len(jobs) == 11 and len({(j['surface'], j['path']) for j in jobs}) == 11
    return jobs


def fetch(job):
    result = {'url': job['url'], 'path': job['path'], 'kind': job['kind'],
              'surface': job['surface']}
    try:
        # Keep configured urllib proxy/CA and standard TLS verification. No Range,
        # query/cache-busting parameter, verification bypass or alternate route.
        request = urllib.request.Request(job['url'], headers={
            'User-Agent': 'video-studio-redis-cover-release-verification'})
        retained = []
        h = hashlib.sha256()
        size = 0
        keep = job['kind'] == 'page' or job['path'].endswith(('.jpg', '.png'))
        with urllib.request.urlopen(request, timeout=90) as response:
            while block := response.read(1024 * 1024):
                h.update(block)
                size += len(block)
                if keep:
                    retained.append(block)
            result.update(status=response.status, bytes=size,
                          sha256=h.hexdigest(), finalUrl=response.url)
        if job['kind'] == 'bytes':
            result['expectedSha256'] = job['sha256']
            result['passed'] = result['status'] == 200 and h.hexdigest() == job['sha256']
        else:
            text = b''.join(retained).decode('utf-8')
            result['missing'] = [value for value in job['contains'] if value not in text]
            result['passed'] = result['status'] == 200 and not result['missing']
        if job['kind'] == 'bytes' and job['path'].endswith(('.jpg', '.png')):
            dest = OUT / 'fetched' / job['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b''.join(retained))
    except Exception as exc:
        result.update(passed=False, error=f'{type(exc).__name__}: {exc}')
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
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
                'localHead': local_head, 'metaSha256': digest(META),
                'catalogSha256': digest(CATALOG), 'sourcePath': SOURCE_PATH,
                'coverOnlyOriginalVideoSha256': VIDEO_SHA256,
                'pagesRequests': 9, 'pagesByteRequests': 3,
                'pagesPageRequests': 6, 'rawRequests': 2, 'requestCount': 11,
                'jobs': jobs, 'networkRequestsExecuted': 0,
                'changelogLocalCheck': 'Deferred until Release exists; live verification requires Redis, exact release and actual release tag URL.'}
        target = OUT / 'expected-assets.json'
        target.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'prepared': True, 'networkRequestsExecuted': 0,
                          'requestsPlanned': 11, 'plan': str(target)}))
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
    assert prepared['release'] == RELEASE and prepared['requestCount'] == 11
    assert prepared['metaSha256'] == digest(META), 'publication meta changed since preparation'
    assert prepared['catalogSha256'] == digest(CATALOG), 'cover catalog changed since preparation'
    assert prepared['sourcePath'] == SOURCE_PATH
    assert prepared['jobs'] == jobs, 'local publication inputs changed; prepare a new explicit plan'
    for job in jobs:
        assert '?' not in job['path'] and '#' not in job['path'] and '..' not in job['path']
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
              'requests': results, 'passed': all(result['passed'] for result in results),
              'requestCount': len(results), 'pagesRequestCount': 9,
              'pagesByteRequestCount': 3, 'pagesPageRequestCount': 6,
              'rawRequestCount': 2, 'totalBytes': sum(result.get('bytes', 0) for result in results)}
    path = OUT / ('report-' + finished.strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if report['passed']:
        (OUT / 'online-verification.json').write_text(path.read_text())
    print(json.dumps({'passed': report['passed'], 'requests': len(results),
                      'bytes': report['totalBytes'], 'failed': [result for result in results if not result['passed']],
                      'report': str(path)}, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
