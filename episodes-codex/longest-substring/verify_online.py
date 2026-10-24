"""Verify the published episode with real GETs and complete media hashes.

Run from any directory after the Release-triggered Pages deployment succeeds.
Uses the inherited proxy/CA configuration. Does not save downloaded media.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
EP = Path(__file__).resolve().parent
SITE = ROOT / 'episodes/longest-substring'
DIST = ROOT / 'site/dist'
META = json.loads((SITE / 'meta.json').read_text())
SB = json.loads((SITE / 'storyboard.json').read_text())
BASE = 'https://linhongcun.github.io/video-studio/'
TAG = 'v' + json.loads((ROOT / 'site/package.json').read_text())['version']


def get(rel):
    url = BASE + rel + ('&' if '?' in rel else '?') + 'verify=' + TAG
    request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-release-verification'})
    with urllib.request.urlopen(request, timeout=90) as response:
        assert response.status == 200, (url, response.status)
        data = response.read()
    return data


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.ids, self.attributes, self.texts = set(), [], []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.ids.add(attributes['id'])
        self.attributes.append((tag, attributes))

    def handle_data(self, data):
        self.texts.append(data)


records = []
for filename in [META['video'], META['poster']]:
    rel = f'episodes/{META["slug"]}/{filename}'
    data = get(rel)
    expected = (SITE / filename).read_bytes()
    assert len(data) == len(expected) and sha(data) == sha(expected), rel
    records.append(dict(path=rel, bytes=len(data), sha256=sha(data), completeLocalMatch=True))

vtt_path = f'episodes/{META["slug"]}/captions.vtt'
vtt = get(vtt_path)
assert vtt == (DIST / vtt_path).read_bytes(), 'Published VTT differs from locally validated build'
assert vtt.decode().count('-->') == 36
records.append(dict(path=vtt_path, bytes=len(vtt), sha256=sha(vtt), completeLocalMatch=True))

body = get(f'episodes/{META["slug"]}/').decode()
page = Page(body)
text = ''.join(page.texts)
assert META['title'] in text and 'LC.3' in text and TAG in text
assert 'EP.23' not in text
assert META['sourcePath'] in body
assert {'goal', 'shrink', 'best', 'code'} <= page.ids
chapter_payloads = [json.loads(a['data-chapters']) for _, a in page.attributes if 'data-chapters' in a]
assert chapter_payloads, 'No published video chapter payload'
chapters = chapter_payloads[0]
expected_chapters = [(s['chapterId'], s['from']) for s in SB['scenes']]
assert [c['id'] for c in chapters] == [cid for cid, _ in expected_chapters]
for c, (_, frame) in zip(chapters, expected_chapters):
    assert abs(c['start'] - frame / SB['meta']['fps']) < 1e-9, c

series = get('series/leetcode/').decode()
assert META['slug'] in series and 'LC.3' in series
home = get('').decode()
assert META['slug'] in home and 'LeetCode' in home and TAG in home
rss = get('rss.xml').decode()
assert META['slug'] in rss and 'LC.3' in rss
changelog = get('changelog/').decode()
assert TAG in changelog and f'releases/tag/{TAG}' in changelog and f'/episodes/{META["slug"]}/' in changelog

report = dict(checkedAtUTC=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              version=TAG, slug=META['slug'], status='passed',
              method='Actual HTTPS GETs; full media bytes/SHA and VTT byte equality; HTML chapter anchors/payload, source entry, series, RSS, homepage and Release changelog.',
              records=records, captions=36, chapters=chapters,
              episodeLabel='LC.3', independentSeries=True,
              limitation='HTTP delivery and published document checks; not a claim of full human listening or measured learning outcomes.')
(EP / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
