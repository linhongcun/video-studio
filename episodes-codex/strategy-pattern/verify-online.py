"""Verify canonical published artifacts with ordinary HTTP GET requests.

Reads the environment's normal HTTPS proxy and CA trust through urllib.
Streams the entire video into SHA-256 without saving a remote media file.
Run only after the Release-following Pages deployment has completed.
"""
import hashlib
import html
import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / 'episodes/strategy-pattern'
DIST = ROOT / 'site/dist'
BASE = 'https://linhongcun.github.io/video-studio/'
SLUG = 'strategy-pattern'
META = json.loads((EP / 'meta.json').read_text())
SB = json.loads((EP / 'storyboard.json').read_text())
VERSION = json.loads((ROOT / 'site/package.json').read_text())['version']
FPS = SB['meta'].get('fps', 30)
PAGE_URL = BASE + 'episodes/' + SLUG + '/'
assert re.fullmatch(r'\d+\.\d+\.\d+', VERSION)
assert META['firstRelease'] == 'v0.52.0'
assert META['draft'] is False
assert META['sourcePath'] == 'episodes-codex/strategy-pattern/remotion'
vtt_path = DIST / 'episodes/strategy-pattern/captions.vtt'
if vtt_path.is_dir():
    vtt_path = vtt_path / 'index.html'

def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(256 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

results = []
context = ssl.create_default_context()

def get(name, url, *, expected_sha=None, keep_body=True):
    request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-site-check/1.0'})
    digest = hashlib.sha256()
    chunks = []
    count = 0
    with urllib.request.urlopen(request, timeout=90, context=context) as response:
        assert response.status == 200, (name, response.status)
        assert response.geturl() == url, (name, 'unexpected redirect', response.geturl())
        record = {'name': name, 'url': url, 'method': 'GET', 'status': response.status,
                  'contentType': response.headers.get('Content-Type'),
                  'etag': response.headers.get('ETag'),
                  'age': response.headers.get('Age'),
                  'cacheControl': response.headers.get('Cache-Control')}
        for chunk in iter(lambda: response.read(256 * 1024), b''):
            count += len(chunk)
            digest.update(chunk)
            if keep_body:
                chunks.append(chunk)
    record.update(bytes=count, sha256=digest.hexdigest())
    if expected_sha:
        record['expectedSha256'] = expected_sha
        assert digest.hexdigest() == expected_sha, (name, 'SHA mismatch', digest.hexdigest(), expected_sha)
        record['exactBytesMatch'] = True
    results.append(record)
    return b''.join(chunks) if keep_body else None

try:
    video_url = PAGE_URL + META['video']
    poster_url = PAGE_URL + META['poster']
    captions_url = PAGE_URL + 'captions.vtt'
    get('video', video_url, expected_sha=sha_file(EP / META['video']), keep_body=False)
    get('poster', poster_url, expected_sha=sha_file(EP / META['poster']), keep_body=False)
    get('captions', captions_url, expected_sha=sha_file(vtt_path))
    page = get('episode', PAGE_URL).decode('utf-8')
    chapters = json.loads(html.unescape(re.search(r'data-chapters="([^"]+)"', page).group(1)))
    expected_chapters = []
    offset = 0
    for scene in SB['scenes']:
        if not expected_chapters or expected_chapters[-1]['id'] != scene['chapterId']:
            expected_chapters.append({'id': scene['chapterId'], 'frame': offset, 'start': offset / FPS})
        offset += sum(shot['durationInFrames'] for shot in scene['shots'])
    assert len(chapters) == len(expected_chapters) == 4
    for actual, expected in zip(chapters, expected_chapters):
        assert actual['id'] == expected['id']
        assert actual['start'] == expected['start']
        assert ('id="' + expected['id'] + '"') in page
        assert ('data-seek="' + expected['id'] + '"') in page
    source_url = 'https://github.com/linhongcun/video-studio/tree/main/' + META['sourcePath']
    assert source_url in html.unescape(page)
    assert META['title'] in page
    assert 'EP.23 · 设计模式 D01' in page
    assert 'id="course-directory"' in page
    directory = re.search(r'<nav[^>]*aria-label="设计模式课程目录"[^>]*>(.*?)</nav>', page, re.S).group(1)
    current_lesson = re.search(r'<a\b(?=[^>]*href="/video-studio/episodes/strategy-pattern/")(?=[^>]*aria-current="page")[^>]*>', directory)
    assert current_lesson, 'current lesson missing from design patterns directory'
    assert 'aria-label="上一课 / 下一课"' not in page
    assert offset == META['finalVideoFrames']
    ld_text = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S).group(1)
    ld = json.loads(html.unescape(ld_text))
    assert ld['name'] == META['title']
    assert ld['contentUrl'] == video_url
    assert ld['embedUrl'] == PAGE_URL
    home = get('home', BASE).decode('utf-8')
    assert '/video-studio/episodes/strategy-pattern/' in home
    assert 'data-series="design-patterns"' in home
    assert VERSION in home
    series = get('series', BASE + 'series/design-patterns/').decode('utf-8')
    assert '/video-studio/episodes/strategy-pattern/' in series and META['title'] in series
    rss = get('rss', BASE + 'rss.xml').decode('utf-8')
    assert PAGE_URL in rss and META['title'] in rss
    changelog = get('changelog', BASE + 'changelog/').decode('utf-8')
    assert 'https://github.com/linhongcun/video-studio/releases/tag/v' + VERSION in changelog
    checked_at = datetime.now(timezone.utc)
    report = {'status': 'passed', 'checkedAtUTC': checked_at.isoformat(),
              'checkedAtBeijing': checked_at.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
              'executedBy': 'Codex strategy website verification',
              'release': 'v' + VERSION, 'canonicalQueriesAdded': False,
              'remoteMediaSaved': False, 'fullVideoStreamHashed': True,
              'results': results, 'chapters': expected_chapters,
              'finalVideoFrames': offset, 'durationSeconds': offset / FPS,
              'sourceUrl': source_url,
              'scope': 'Published artifact byte equality, exact chapter and anchor data, source link, series, RSS and Release entry; browser behavior is recorded separately.'}
    (EP / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'canonicalGetCount': len(results), 'release': 'v' + VERSION,
                      'videoSha256': results[0]['sha256'], 'report': str(EP / 'online-verification.json')}, ensure_ascii=False, indent=2))
except Exception as exc:
    print(json.dumps({'status': 'failed', 'completedGetCount': len(results),
                      'error': str(exc), 'results': results}, ensure_ascii=False, indent=2))
    raise
