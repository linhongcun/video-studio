"""Verify the four middleware-identity viewing copies against final production outputs."""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import hashlib
import html
import json
import re
import subprocess
import urllib.request

P = argparse.ArgumentParser()
P.add_argument('--live', action='store_true')
P.add_argument('--report', required=True)
A = P.parse_args()
R = Path(__file__).resolve().parents[2]
INDEX = json.loads((Path(__file__).parent / 'index.json').read_text())
VERSION = json.loads((R / 'site/package.json').read_text())['version']
BASE = 'https://linhongcun.github.io/video-studio/'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def get(relative):
    if not A.live:
        return (R / 'site/dist' / relative).read_bytes()
    req = urllib.request.Request(BASE + relative, headers={
        'User-Agent': 'video-studio-middleware-identity-release-check', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=60) as response:
        assert response.status == 200
        return response.read()

def page(relative):
    return get(relative + ('' if A.live else 'index.html')).decode()

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.chapters = None
        self.videos = []
        self.chapter_links = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if 'data-chapters' in attrs:
            self.chapters = json.loads(attrs['data-chapters'])
        if tag == 'video':
            self.videos.append(attrs)
        if tag == 'a' and 'data-id' in attrs and 'data-start' in attrs:
            self.chapter_links[attrs['data-id']] = attrs

rows = []
for slug in INDEX['selected']:
    M = json.loads((R / 'episodes' / slug / 'meta.json').read_text())
    D = (R / M['sourcePath']).parent
    old = json.loads(subprocess.check_output([
        'git', 'show', f"{INDEX['baselineCommit']}:episodes/{slug}/meta.json"], cwd=R))
    for key in ['slug', 'ep', 'title', 'series', 'episodePart', 'lessonOrder',
                'firstRelease', 'publishedAt', 'learningGuide', 'platforms', 'sourcePath']:
        assert M.get(key) == old.get(key), (slug, key)
    SB = json.loads((D / 'storyboard.json').read_text())
    E = json.loads((D / 'render-result.json').read_text())
    prefix = 'episodes/' + slug + '/'
    movie = get(prefix + 'video.mp4')
    assert sha(movie) == E['sha256'] and len(movie) == E['bytes'], slug
    assert get(prefix + 'cover-16x9.jpg') == (D / 'cover-16x9.jpg').read_bytes()
    raw = page(prefix)
    body = html.unescape(raw)
    parsed = Document(raw)
    assert M['title'] in body and VERSION in body, slug
    assert 'https://github.com/linhongcun/video-studio/tree/main/' + M['sourcePath'] in body
    assert len(parsed.videos) == 1 and 'controls' in parsed.videos[0]
    assert parsed.chapters is not None and len(parsed.chapters) == len(SB['scenes'])
    for chapter, scene in zip(parsed.chapters, SB['scenes']):
        chapter_id = scene.get('chapterId', scene['id'])
        assert chapter['id'] == chapter_id
        assert abs(chapter['start'] - scene['from'] / SB['meta']['fps']) < .001
        link = parsed.chapter_links[chapter_id]
        assert abs(float(link['data-start']) - chapter['start']) < .001
        expected_target = chapter_id if chapter_id in parsed.ids else 'player'
        assert link['href'] == '#' + expected_target and expected_target in parsed.ids
    fps = SB['meta']['fps']
    seconds = E['frames'] / fps
    minutes, remainder = int(seconds // 60), int(seconds % 60)
    assert f'视频 {minutes}:{remainder:02}' in body
    assert f'PT{minutes}M{remainder}S' in body
    vtt = get(prefix + 'captions.vtt').decode()
    actual = re.findall(r'(\d\d):(\d\d):(\d\d\.\d+) --> (\d\d):(\d\d):(\d\d\.\d+)\n([^\n]+)', vtt)
    expected = [(float(s['from'] + q['from']) / fps,
                 float(s['from'] + q['to'] + 1) / fps, q['text'])
                for c in SB['scenes'] for s in c['shots'] for q in s['subtitles']]
    assert len(actual) == len(expected), slug
    for q, e in zip(actual, expected):
        start = int(q[0]) * 3600 + int(q[1]) * 60 + float(q[2])
        end = int(q[3]) * 3600 + int(q[4]) * 60 + float(q[5])
        assert abs(start-e[0]) < .001 and abs(end-e[1]) < .001 and q[6] == e[2], (slug, e)
    rows.append({'slug': slug, 'sha256': E['sha256'], 'bytes': len(movie),
                 'frames': E['frames'], 'captions': len(expected),
                 'chapters': len(parsed.chapters), 'posterMatched': True,
                 'nativeControls': True, 'historicalMetadataPreserved': True})

if A.live:
    changelog = page('changelog/')
    assert 'releases/tag/v' + VERSION in changelog
    for row in rows:
        assert row['sha256'] in changelog
result = {'status': 'passed', 'scope': 'canonical live HTTP' if A.live else 'built site',
          'version': VERSION, 'episodes': rows,
          'totalCaptions': sum(row['captions'] for row in rows),
          'totalChapters': sum(row['chapters'] for row in rows),
          'actualReleaseInChangelog': A.live}
Path(A.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
