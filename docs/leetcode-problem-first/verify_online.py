"""Verify this repair against the current learning-site layout with real GETs."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://linhongcun.github.io/video-studio/'
TAG = 'v' + json.loads((ROOT/'site/package.json').read_text())['version']
SLUGS = ['container-most-water', 'longest-substring']

def get(path):
    req = urllib.request.Request(BASE + path + '?verify=' + TAG + '-problem-first',
                                 headers={'User-Agent': 'video-studio-release-verification'})
    with urllib.request.urlopen(req, timeout=90) as response:
        assert response.status == 200
        return response.read()

def sha(data):
    return hashlib.sha256(data).hexdigest()

class Page(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.ids, self.attrs, self.texts = set(), [], []
        self.feed(body)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        self.attrs.append(attrs)
    def handle_data(self, text):
        self.texts.append(text)

home = get('').decode()
library = get('library/').decode()
series = get('series/leetcode/').decode()
rss = get('rss.xml').decode()
changelog = get('changelog/').decode()
assert TAG in home and 'IT小村' in home and '/learn/' in home and '/library/' in home
assert f'releases/tag/{TAG}' in changelog, 'Actual Release entry is missing'
reports = []
for slug, count in zip(SLUGS, [44, 36]):
    D = ROOT/'episodes'/slug
    meta = json.loads((D/'meta.json').read_text())
    sb = json.loads((D/'storyboard.json').read_text())
    label = f"LC.{meta['problemNumber']}"
    records = []
    for filename in [meta['video'], meta['poster']]:
        rel = f'episodes/{slug}/{filename}'
        actual, expected = get(rel), (D/filename).read_bytes()
        assert actual == expected, rel
        records.append(dict(path=rel, bytes=len(actual), sha256=sha(actual), completeLocalMatch=True))
    rel = f'episodes/{slug}/captions.vtt'
    actual = get(rel)
    assert actual == (ROOT/'site/dist'/rel).read_bytes()
    assert actual.decode().count('-->') == count
    records.append(dict(path=rel, bytes=len(actual), sha256=sha(actual), completeLocalMatch=True))
    body = get(f'episodes/{slug}/').decode()
    page = Page(body)
    text = ''.join(page.texts)
    assert meta['title'] in text and label in text and TAG in text
    assert meta['sourcePath'] in body
    payloads = [json.loads(a['data-chapters']) for a in page.attrs if 'data-chapters' in a]
    assert payloads
    chapters = payloads[0]
    assert [c['id'] for c in chapters] == [s['chapterId'] for s in sb['scenes']]
    for c, scene in zip(chapters, sb['scenes']):
        assert c['id'] in page.ids
        assert abs(c['start'] - scene['from']/sb['meta']['fps']) < 1e-9
    for document in [library, series, rss, changelog]:
        assert f'/episodes/{slug}/' in document, slug
    assert label in series and label in rss
    report = dict(checkedAtUTC=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  version=TAG, slug=slug, status='passed', records=records,
                  captions=count, chapters=chapters, episodeLabel=label,
                  actualReleaseEntryConfirmed=True, learningSitePreserved=True,
                  method='Actual HTTPS GETs; complete media bytes/SHA, exact VTT, chapter payload/anchors, source entry, library/series/RSS, current learning homepage and actual Release entry.',
                  limitation='Delivery verification; no claim of full listening, ASR or measured learning outcomes.')
    (ROOT/'episodes-codex'/slug/'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    reports.append(report)
out = dict(status='passed', version=TAG, episodes=reports)
(Path(__file__).parent/'online-verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'status':'passed', 'version':TAG, 'slugs':SLUGS}, ensure_ascii=False))
