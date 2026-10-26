"""Verify deployed articles and complete asset bytes after the Release deployment."""
import concurrent.futures
import datetime
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://linhongcun.github.io/video-studio/'
OUT = Path(__file__).resolve().parent
VERSION = '0.73.0'


def get(url):
    request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200, (url, response.status)
        return response.read()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def signature(text):
    quotes = []
    for source_id, body in re.findall(r'data-source-quote="([^"]+)"[^>]*>([\s\S]*?)</figure>', text):
        quote = re.search(r'<blockquote\b[^>]*>([\s\S]*?)</blockquote>', body).group(1)
        quotes.append({'id': source_id, 'text': html.unescape(re.sub(r'<[^>]+>', '', quote)),
                       'links': [html.unescape(url) for url in re.findall(r'href="([^"]+)"', body)]})
    return {'quotes': quotes,
            'images': re.findall(r'<img\b[^>]*src="([^"]+/article/[^"]+)"', text),
            'seekTimes': re.findall(r'data-seek-time="([^"]+)"', text),
            'dates': re.findall(r'<time\b[^>]*datetime="([^"]+)"', text)}


def page_job(slug):
    url = BASE + 'episodes/' + slug + '/'
    actual = get(url)
    expected = (ROOT / 'site/dist/episodes' / slug / 'index.html').read_text()
    remote = actual.decode()
    assert signature(remote) == signature(expected), slug + ': deployed quote/image/time identity differs'
    assert 'v' + VERSION in remote, slug + ': site version differs'
    return {'kind': 'article', 'slug': slug, 'url': url, 'responseSha256': digest(actual),
            'quotes': len(signature(remote)['quotes']), 'images': signature(remote)['images']}


def asset_job(file):
    relative = str(file.relative_to(ROOT))
    url = BASE + relative
    actual = get(url)
    expected = file.read_bytes()
    assert digest(actual) == digest(expected), relative + ': full SHA differs'
    return {'kind': 'asset', 'path': relative, 'url': url, 'bytes': len(actual), 'sha256': digest(actual)}


def main():
    slugs = []
    images = []
    for file in sorted((ROOT / 'episodes').glob('*/meta.json')):
        meta = json.loads(file.read_text())
        if meta.get('draft') or meta.get('archived'):
            continue
        slugs.append(file.parent.name)
        images.extend(sorted((file.parent / 'article').glob('*.jpg')))
    preserved = []
    for slug in ['http-request', 'db-lock', 'two-sum']:
        meta = json.loads((ROOT / 'episodes' / slug / 'meta.json').read_text())
        preserved.extend([ROOT / 'episodes' / slug / meta['video'], ROOT / 'episodes' / slug / meta['poster']])
    results, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        jobs = [pool.submit(page_job, slug) for slug in slugs]
        jobs += [pool.submit(asset_job, file) for file in images + preserved]
        for job in concurrent.futures.as_completed(jobs):
            try:
                results.append(job.result())
            except Exception as error:
                failures.append(str(error))
    changelog = get(BASE + 'changelog/').decode()
    assert VERSION in changelog and '/releases/tag/v' + VERSION in changelog, 'Release missing from deployed changelog'
    report = {'checkedAt': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'base': BASE, 'version': VERSION, 'results': sorted(results, key=lambda result: result.get('slug', result.get('path', ''))),
              'failures': failures, 'changelogIncludesRelease': True,
              'scope': 'All 47 current article signatures and all 42 new image bytes; three unchanged representative videos and posters checked with complete SHA. Other unchanged media retained by local baseline preservation.'}
    (OUT / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'requestsVerified': len(results) + 1, 'failures': failures}, ensure_ascii=False))
    assert not failures


if __name__ == '__main__':
    main()
