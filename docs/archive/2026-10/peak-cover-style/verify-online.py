#!/usr/bin/env python3
"""Prepare/verify four peak-series covers with 23 full canonical HTTPS GETs.

--prepare is local-only. Live GETs require the exact merge SHA, run ID, and full
successful workflow_dispatch status. No publish/deploy/issue/Git mutations occur.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import subprocess
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path('/workspace/video-studio')
OUT = Path('/workspace/work/peak-online')
BASE = 'https://linhongcun.github.io/video-studio/'
RAW = 'https://raw.githubusercontent.com/linhongcun/video-studio/'
RELEASE = 'v0.90.1'  # Planned patch, confirmed by root before final prepare.
SERIES = 'peak'
SERIES_TITLE = '高并发、高可用、高性能'
CATALOG = ROOT / 'episodes-codex/_shared/peak-covers/catalog.json'
DELIVERY = 'design/peak-covers-20261029/'
IDENTITIES = {'rate-limit': {'ep': 11,
                'title': '抢票时，为什么总提示系统繁忙？',
                'sourcePath': 'episodes-codex/rate-limit/remotion',
                'metaSha256': '329b394328c81357b49217f153d5affe6fc4ed964dc4256b601a3576133082ed',
                'videoBytes': 5906509,
                'videoSha256': '3997c12894779f1bcdb4eb4d05dae6a4fcbe96da358122198dcc675da9d34850'},
 'idempotency': {'ep': 12,
                 'title': '手一抖点了两次支付，为什么只扣一次钱？',
                 'sourcePath': 'episodes-codex/idempotency/remotion',
                 'metaSha256': '5e58f9709aa10878f85403fa5d716f995bcee95df02e703b65d3a1d35e5475d3',
                 'videoBytes': 5174712,
                 'videoSha256': '2a35f643f8a668fec1deb22ec8a8bdbef8b7eb463676b2b7d27730737834754d'},
 'circuit-breaker': {'ep': 13,
                     'title': '一个服务出故障，为什么整个网站没跟着崩？',
                     'sourcePath': 'episodes-codex/circuit-breaker/remotion',
                     'metaSha256': '2d3c44f2edb4265b21fece88b36a899eb012359f1f52f368b1f450c2c20488e8',
                     'videoBytes': 8695484,
                     'videoSha256': 'ee4635aae02795ad3f09e00a1b74bb85e516a8b6a3fc690bf16a2295770ef1c6'},
 'degradation': {'ep': 14,
                 'title': '搜索页和结算页，为什么两个价不一样？',
                 'sourcePath': 'episodes-codex/degradation/remotion',
                 'metaSha256': 'e3d7ae41e96f73c35cfb630dd91258aafa0ab4ffd063609fa8835b720f6c699d',
                 'videoBytes': 5131104,
                 'videoSha256': '2c1fb1a8c60e8150f654aef4ed4d1cbc1ed6b42993e8c2651f928e99a1fe67f2'}}
SLUGS = sorted(IDENTITIES)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


class PageEvidence(HTMLParser):
    """Read the actual flat series->episode HTML; no old direction hierarchy."""
    def __init__(self):
        super().__init__()
        self.all_episodes = set()
        self.series_cards = set()
        self.series_section = set()
        self.sections = []
        self.anchor_hrefs = []
        self.canonicals = []
        self.robots = []
        self.script_parts = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.sections.append(attrs.get('id'))
        if tag == 'script':
            self.in_script = True
        if tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            self.canonicals.append(attrs.get('href', ''))
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            self.robots.append(attrs.get('content', '').lower())
        if tag != 'a':
            return
        self.anchor_hrefs.append(attrs.get('href', ''))
        path = urllib.parse.urlsplit(attrs.get('href', '')).path
        match = re.fullmatch(r'/video-studio/episodes/([a-z0-9-]+)/', path)
        if not match:
            return
        slug = match.group(1)
        self.all_episodes.add(slug)
        if attrs.get('data-series') == SERIES:
            self.series_cards.add(slug)
        if SERIES in self.sections:
            self.series_section.add(slug)

    def handle_endtag(self, tag):
        if tag == 'section' and self.sections:
            self.sections.pop()
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.script_parts.append(data)


def check_page(job, text):
    evidence = {'missing': [value for value in job['contains'] if value not in text]}
    parsed = PageEvidence()
    parsed.feed(text)
    for field, values in [('episodeSet', parsed.all_episodes),
                          ('seriesCardSet', parsed.series_cards),
                          ('seriesSectionSet', parsed.series_section)]:
        if field in job:
            evidence[field] = sorted(values)
            evidence[field + 'Matches'] = sorted(values) == job[field]
    if 'legacyRedirectTo' in job:
        expected = urllib.parse.urljoin(BASE, job['legacyRedirectTo'])
        canonical_targets = [urllib.parse.urljoin(BASE, value) for value in parsed.canonicals]
        scripts = '\n'.join(parsed.script_parts)
        target_match = re.search(r"\b(?:const|let|var)\s+target\s*=\s*([\"'])([^\"']+)\1", scripts)
        script_target = urllib.parse.urljoin(BASE, target_match.group(2)) if target_match else None
        compact = re.sub(r'\s+', '', scripts)
        preserves = 'window.location.replace(target+window.location.search+window.location.hash)' in compact
        fallback = expected in [urllib.parse.urljoin(BASE, value) for value in parsed.anchor_hrefs]
        robots = any({'noindex', 'follow'} <= set(re.split(r'[\s,]+', value)) for value in parsed.robots)
        contract = {'target': expected, 'canonicalTargets': canonical_targets,
                    'canonicalMatches': canonical_targets == [expected],
                    'scriptTarget': script_target, 'scriptTargetMatches': script_target == expected,
                    'replacementPreservesSearchAndHash': preserves,
                    'fallbackLinkMatches': fallback, 'robotsNoindexFollow': robots,
                    'scope': 'complete GET of legacy HTML and its literal JS/canonical/fallback contract; no browser execution'}
        contract['passed'] = all(contract[key] for key in ['canonicalMatches', 'scriptTargetMatches',
                                  'replacementPreservesSearchAndHash', 'fallbackLinkMatches', 'robotsNoindexFollow'])
        evidence['legacyRedirect'] = contract
    evidence['passed'] = not evidence['missing'] and all(
        evidence.get(field + 'Matches', True)
        for field in ['episodeSet', 'seriesCardSet', 'seriesSectionSet']) and evidence.get('legacyRedirect', {}).get('passed', True)
    return evidence


def local_jobs():
    package = json.loads((ROOT / 'site/package.json').read_text())
    assert package['version'] == RELEASE.removeprefix('v'), 'local version differs from requested release'
    series = json.loads((ROOT / 'site/src/content/series.json').read_text())
    assert series[SERIES]['title'] == SERIES_TITLE
    published = {}
    for p in (ROOT / 'episodes').glob('*/meta.json'):
        m = json.loads(p.read_text())
        if m.get('series') == SERIES and not m.get('draft'):
            published[m['slug']] = m
    assert sorted(published) == SLUGS, 'published peak set changed'
    catalog = json.loads(CATALOG.read_text())
    assert catalog['series'] == SERIES
    assert sorted(ep['slug'] for ep in catalog['episodes']) == SLUGS
    entries = {ep['slug']: ep for ep in catalog['episodes']}
    jobs = []
    for slug, identity in IDENTITIES.items():
        prefix = 'episodes/' + slug + '/'
        meta_path = ROOT / prefix / 'meta.json'
        meta = published[slug]
        assert digest(meta_path) == identity['metaSha256'], 'cover-only task changed meta: ' + slug
        assert meta['ep'] == identity['ep'] and meta['title'] == identity['title']
        assert meta['sourcePath'] == identity['sourcePath']
        assert meta['video'] == 'video.mp4' and meta['poster'] == 'cover-16x9.jpg'
        assert entries[slug]['ep'] == identity['ep'] and entries[slug]['sourceTitle'] == identity['title']
        video = ROOT / prefix / 'video.mp4'
        assert video.stat().st_size == identity['videoBytes'] and digest(video) == identity['videoSha256'], 'cover-only task changed video: ' + slug
        for name in ['video.mp4', 'cover-16x9.jpg', 'captions.vtt']:
            built = ROOT / 'site/dist' / prefix / name
            local = built if name == 'captions.vtt' else ROOT / prefix / name
            expected = digest(local)
            assert digest(built) == expected, 'built publication asset differs: ' + slug + '/' + name
            jobs.append({'path': prefix + name, 'sha256': expected,
                         'localPath': str(local), 'kind': 'bytes', 'surface': 'pages'})
    assert len(jobs) == 12
    pages = []
    for slug, identity in IDENTITIES.items():
        prefix = 'episodes/' + slug + '/'
        pages.append({'path': prefix, 'contains': [identity['title'], SERIES_TITLE,
                      RELEASE, 'series/peak/', prefix + 'cover-16x9.jpg', identity['sourcePath']]})
    titles = [identity['title'] for identity in IDENTITIES.values()]
    pages.extend([
        {'path': 'series/peak/', 'contains': [SERIES_TITLE, RELEASE] + titles,
         'episodeSet': SLUGS},
        {'path': '', 'contains': [SERIES_TITLE, RELEASE, 'series/peak/', 'series-peak',
                                 IDENTITIES['rate-limit']['title']]},
        {'path': 'learn/', 'contains': ['学习系列与全部内容已合并。', '前往学习内容', 'data-pagefind-ignore="all"'],
         'legacyRedirectTo': 'library/'},
        {'path': 'library/', 'contains': [SERIES_TITLE, RELEASE, 'value="peak"', 'data-series="peak"',
                      'id="learning-series"', 'id="all-content"', 'series/peak/'] + titles,
         'seriesCardSet': SLUGS},
        {'path': 'changelog/', 'contains': [RELEASE,
          'https://github.com/linhongcun/video-studio/releases/tag/' + RELEASE]},
    ])
    assert len(pages) == 9
    for page in pages:
        job = dict(page, kind='page', surface='pages')
        local_text = (ROOT / 'site/dist' / job['path'] / 'index.html').read_text()
        if job['path'] != 'changelog/':
            evidence = check_page(job, local_text)
            assert evidence['passed'], 'local HTML evidence missing: ' + (job['path'] or '/') + ' ' + json.dumps(evidence, ensure_ascii=False)
        jobs.append(job)
    assert len(jobs) == 21
    for name in ['peak-covers.zip', 'peak-preview.png']:
        local = ROOT / DELIVERY / name
        jobs.append({'path': DELIVERY + name, 'sha256': digest(local),
                     'localPath': str(local), 'kind': 'bytes', 'surface': 'github-raw'})
    assert len(jobs) == 23 and len({(j['surface'], j['path']) for j in jobs}) == 23
    return jobs


def fetch(job):
    result = {'url': job['url'], 'path': job['path'], 'kind': job['kind'],
              'surface': job['surface']}
    try:
        # Preserve urllib's inherited proxy/CA and standard TLS verification.
        # No Range, query/cache-busting argument, custom route or TLS bypass.
        request = urllib.request.Request(job['url'], headers={
            'User-Agent': 'video-studio-peak-cover-release-verification'})
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
            evidence = check_page(job, b''.join(retained).decode('utf-8'))
            result['pageEvidence'] = evidence
            result['passed'] = result['status'] == 200 and evidence['passed']
        if job['kind'] == 'bytes' and job['path'].endswith(('.jpg', '.png')):
            target = OUT / 'fetched' / job['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b''.join(retained))
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
    local_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepare:
        plan = {'preparedAt': now().isoformat(), 'release': RELEASE,
                'localHead': local_head, 'catalogSha256': digest(CATALOG),
                'seriesTitle': SERIES_TITLE, 'originalIdentities': IDENTITIES,
                'entryContract': 'library/ unified canonical content; learn/ legacy JS replacement preserves search/hash',
                'pagesRequests': 21, 'pagesByteRequests': 12,
                'pagesPageRequests': 9, 'rawRequests': 2, 'requestCount': 23,
                'jobs': jobs, 'networkRequestsExecuted': 0,
                'changelogLocalCheck': 'Deferred until actual Release; live page must show the exact release and its real GitHub tag URL.'}
        target = OUT / 'expected-assets.json'
        target.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'prepared': True, 'networkRequestsExecuted': 0,
                          'requestsPlanned': 23, 'plan': str(target)}))
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
    assert prepared['release'] == RELEASE and prepared['requestCount'] == 23
    assert prepared['catalogSha256'] == digest(CATALOG), 'catalog changed since preparation'
    assert prepared['originalIdentities'] == IDENTITIES, 'original identities changed since preparation'
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
              'localHeadAtVerification': local_head, 'expectedPlanSha256': digest(prepared_path),
              'requests': results, 'passed': all(result['passed'] for result in results),
              'requestCount': len(results), 'pagesRequestCount': 21,
              'pagesByteRequestCount': 12, 'pagesPageRequestCount': 9,
              'rawRequestCount': 2, 'totalBytes': sum(result.get('bytes', 0) for result in results)}
    target = OUT / ('report-' + finished.strftime('%Y%m%dT%H%M%SZ') + '.json')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if report['passed']:
        (OUT / 'online-verification.json').write_text(target.read_text())
    print(json.dumps({'passed': report['passed'], 'requests': len(results),
                      'bytes': report['totalBytes'], 'failed': [result for result in results if not result['passed']],
                      'report': str(target)}, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
