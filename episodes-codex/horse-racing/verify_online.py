#!/usr/bin/env python3
"""Verify P01 after its Release-following Pages deployment has succeeded.

Uses ordinary canonical GETs with the inherited proxy and default CA trust.
Hashes complete remote media streams without saving or retaining their bodies.
No cache-busting query, Range, forced-cache headers, retries, or UI claims.
"""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


BASE = 'https://linhongcun.github.io/video-studio/'
REPO_URL = 'https://github.com/linhongcun/video-studio'
SLUG = 'horse-racing'
FIRST_RELEASE = 'v0.55.0'
RELEASE = 'v0.56.5'
PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SITE = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
PAGE_URL = BASE + 'episodes/' + SLUG + '/'
RELEASE_URL = REPO_URL + '/releases/tag/' + RELEASE


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def descendants(self):
        for child in self.children:
            if isinstance(child, Element):
                yield child
                yield from child.descendants()

    def find_all(self, tag=None, **attrs):
        return [node for node in self.descendants()
                if (tag is None or node.tag == tag)
                and all(node.attrs.get(key) == value for key, value in attrs.items())]

    def text(self):
        return ''.join(child.text() if isinstance(child, Element) else child
                       for child in self.children)


class Page(HTMLParser):
    """Small HTML tree used to check a specific directory or Release entry."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, body: str):
        super().__init__(convert_charrefs=True)
        self.root = Element('__root__')
        self.stack = [self.root]
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def one(nodes, label):
    assert len(nodes) == 1, (label, 'expected exactly one element', len(nodes))
    return nodes[0]


def has_class(node, name):
    return name in (node.attrs.get('class') or '').split()


def version_tuple(value):
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', value)
    assert match, ('Invalid three-part version', value)
    return tuple(map(int, match.groups()))


def deployed_site_version(root):
    footer = one(root.find_all('footer'), 'site footer')
    bottom = one([node for node in footer.find_all('div') if has_class(node, 'footer-bottom')], 'footer version area')
    value = one([node for node in bottom.find_all('span') if has_class(node, 'num')], 'deployed site version').text().strip()
    version_tuple(value)
    return value


def check_episode(page, meta, expected_chapters, expected_frames, fps):
    root = page.root
    assert one(root.find_all('title'), 'page title').text() == meta['title'] + ' · IT小村'
    assert one(root.find_all('h1'), 'lesson heading').text() == meta['title']
    assert 'EP.24 · 趣味推理 P01' in root.text()
    source_url = REPO_URL + '/tree/main/' + meta['sourcePath']
    assert root.find_all('a', href=source_url), 'Missing current production source link'
    player = one(root.find_all('section', id='player'), 'player')
    chapters = json.loads(player.attrs['data-chapters'])
    assert len(chapters) == len(expected_chapters) and expected_chapters
    assert all(chapter['id'] != 'lower-bound' for chapter in chapters), 'Article-only proof leaked into video chapters'
    assert len(root.find_all('h2', id='lower-bound')) == 1, 'The complete article proof must remain available'
    assert not root.find_all('a', **{'data-seek': 'lower-bound'}), 'Article proof must not seek to a removed video chapter'
    for actual, expected in zip(chapters, expected_chapters):
        assert actual['id'] == expected['id']
        assert actual['start'] == expected['frame'] / fps
        assert root.find_all(id=expected['id']), ('Missing article anchor', expected['id'])
        assert root.find_all('a', **{'data-seek': expected['id']}), ('Missing article seek action', expected['id'])
        controls = player.find_all('a', **{'data-id': expected['id']})
        assert controls and all(float(control.attrs['data-start']) == expected['start']
                                for control in controls)
    directory = one(root.find_all('nav', **{'aria-label': '趣味推理课程目录'}), 'P01 course directory')
    links = directory.find_all('a')
    assert len(links) == 1, 'Do not advertise the other nine unproduced puzzles'
    assert links[0].attrs['href'] == '/video-studio/episodes/horse-racing/'
    assert links[0].attrs.get('aria-current') == 'page'
    assert not root.find_all(**{'aria-label': '上一课 / 下一课'}), 'P01 must not inherit an unrelated prerequisite'
    video = one(player.find_all('video'), 'video element')
    assert 'controls' in video.attrs
    assert one(video.find_all('source'), 'video source').attrs['src'] == '/video-studio/episodes/horse-racing/' + meta['video']
    assert one(video.find_all('track'), 'caption track').attrs['src'] == '/video-studio/episodes/horse-racing/captions.vtt'
    ld = json.loads(one(root.find_all('script', type='application/ld+json'), 'VideoObject').text())
    assert ld['name'] == meta['title']
    assert ld['contentUrl'] == PAGE_URL + meta['video']
    assert ld['embedUrl'] == PAGE_URL
    assert ld['duration'] == f'PT{int(expected_frames / fps) // 60}M{int(expected_frames / fps) % 60}S'
    return source_url


def main():
    meta = json.loads((SITE / 'meta.json').read_text())
    storyboard = json.loads((SITE / 'storyboard.json').read_text())
    config = json.loads((PRODUCTION / 'episode-config.json').read_text())
    plan = json.loads((PRODUCTION / 'plan.json').read_text())
    voice_sentences = json.loads((PRODUCTION / 'voice/sents.json').read_text())
    render = json.loads((PRODUCTION / 'render-result.json').read_text())
    version = json.loads((ROOT / 'site/package.json').read_text())['version']
    # P01's debut remains fixed, while this check targets the ending revision.
    # Concurrent courses may advance the deployment-wide version independently.
    assert version_tuple(version) >= version_tuple(RELEASE), ('Local baseline predates P01', version)
    assert meta['firstRelease'] == FIRST_RELEASE and meta['draft'] is False
    assert meta['slug'] == SLUG and meta['ep'] == 24
    assert meta['series'] == 'puzzles' and meta['episodePart'] == '趣味推理 P01'
    assert meta['sourcePath'] == 'episodes-codex/horse-racing/remotion'
    fps = storyboard['meta']['fps']
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    assert len(shots) == config['shotCount'] == len(plan)
    assert [shot['id'] for shot in shots] == [shot['id'] for shot in plan]
    assert [shot['chapterId'] for shot in shots] == [shot['chapterId'] for shot in plan]
    expected_chapters, expected_subtitles = [], []
    offset = 0
    for scene in storyboard['scenes']:
        chapter_id = scene['chapterId']
        if not expected_chapters or expected_chapters[-1]['id'] != chapter_id:
            expected_chapters.append({'id': chapter_id, 'frame': offset, 'start': offset / fps})
        for shot in scene['shots']:
            expected_subtitles.extend(sub['text'] for sub in shot['subtitles'])
            offset += shot['durationInFrames']
    assert offset == meta['finalVideoFrames'] == storyboard['meta']['finalVideoFrames'] == render['frames']
    assert offset == storyboard['meta']['durationInFrames'] and fps == 30
    planned_chapters = list(dict.fromkeys(shot['chapterId'] for shot in plan))
    assert [chapter['id'] for chapter in expected_chapters] == planned_chapters
    assert 'lower-bound' not in planned_chapters and planned_chapters[-1] == 'answer'
    assert expected_subtitles == [sentence['text'] for sentence in voice_sentences]
    assert not any(term in ''.join(expected_subtitles) for term in ('证明', '文章', '图文')), 'Removed proof or article handoff remains in the video narration'
    subtitle_count = len(expected_subtitles)
    assert subtitle_count > 0
    assert sha_file(SITE / meta['video']) == render['sha256'], 'Video differs from final render report'
    vtt_path = DIST / 'episodes' / SLUG / 'captions.vtt'
    if vtt_path.is_dir():
        vtt_path = vtt_path / 'index.html'
    expected_vtt = vtt_path.read_bytes()
    assert expected_vtt.decode('utf-8').count('-->') == subtitle_count
    cue_texts = [block.split('\n', 1)[1]
                 for block in expected_vtt.decode('utf-8').strip().split('\n\n')[1:]]
    assert cue_texts == expected_subtitles, 'Local built VTT must match all frozen narration sentences'
    for filename in (meta['video'], meta['poster']):
        assert sha_file(SITE / filename) == sha_file(PRODUCTION / filename), ('Local source/copy mismatch', filename)
        assert sha_file(SITE / filename) == sha_file(DIST / 'episodes' / SLUG / filename), ('Local build mismatch', filename)
    results = []
    context = ssl.create_default_context()

    def get(name, url, *, expected_sha=None, expected_size=None, keep_body=True):
        parsed = urlsplit(url)
        assert parsed.scheme == 'https' and not parsed.query and not parsed.fragment
        request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-canonical-verification/1.0'}, method='GET')
        digest, chunks, count = hashlib.sha256(), [], 0
        with urllib.request.urlopen(request, timeout=30, context=context) as response:
            assert response.status == 200, (name, response.status)
            assert response.geturl() == url, (name, 'unexpected redirect', response.geturl())
            record = {'name': name, 'url': url, 'method': 'GET', 'status': response.status,
                      'contentType': response.headers.get('Content-Type'),
                      'etag': response.headers.get('ETag'), 'age': response.headers.get('Age'),
                      'cacheControl': response.headers.get('Cache-Control')}
            for chunk in iter(lambda: response.read(256 * 1024), b''):
                digest.update(chunk)
                count += len(chunk)
                if keep_body:
                    chunks.append(chunk)
        record.update(bytes=count, sha256=digest.hexdigest())
        if expected_sha is not None:
            record['expectedSha256'] = expected_sha
            assert record['sha256'] == expected_sha, (name, 'complete SHA mismatch', record['sha256'], expected_sha)
            record['exactBytesMatch'] = True
        if expected_size is not None:
            assert count == expected_size, (name, 'byte count mismatch', count, expected_size)
        results.append(record)
        return b''.join(chunks) if keep_body else None

    try:
        for name, filename in (('video', meta['video']), ('poster', meta['poster'])):
            get(name, PAGE_URL + filename, expected_sha=sha_file(SITE / filename),
                expected_size=(SITE / filename).stat().st_size, keep_body=False)
        captions = get('captions', PAGE_URL + 'captions.vtt',
                       expected_sha=sha_file(vtt_path), expected_size=len(expected_vtt))
        assert captions == expected_vtt and captions.decode('utf-8').count('-->') == subtitle_count
        episode = Page(get('episode', PAGE_URL).decode('utf-8'))
        source_url = check_episode(episode, meta, expected_chapters, offset, fps)
        home = Page(get('home', BASE).decode('utf-8')).root
        assert home.find_all('a', href='/video-studio/learn/#puzzles'), 'Missing homepage puzzle direction'
        assert home.find_all('a', href='/video-studio/episodes/horse-racing/'), 'Missing homepage P01 lesson'
        deployed_version = deployed_site_version(home)
        assert version_tuple(deployed_version) >= version_tuple(RELEASE), ('Deployed site predates P01', deployed_version)
        series = Page(get('series', BASE + 'series/puzzles/').decode('utf-8')).root
        assert '趣味推理' in series.text() and meta['title'] in series.text()
        assert series.find_all('a', href='/video-studio/episodes/horse-racing/')
        learn = Page(get('learn', BASE + 'learn/').decode('utf-8')).root
        puzzle_track = one(learn.find_all(id='puzzles'), 'Puzzle learning direction')
        assert '趣味推理' in puzzle_track.text()
        assert puzzle_track.find_all('a', href='/video-studio/series/puzzles/')
        lesson_lists = [node for node in puzzle_track.find_all('ol') if has_class(node, 'chapter-lessons')]
        assert len(lesson_lists) == 1
        lesson_links = lesson_lists[0].find_all('a')
        assert len(lesson_links) == 1 and lesson_links[0].attrs['href'] == '/video-studio/episodes/horse-racing/'
        rss = get('rss', BASE + 'rss.xml').decode('utf-8')
        assert PAGE_URL in rss and meta['title'] in rss and '趣味推理 P01' in rss
        release = json.loads(get('github-release', 'https://api.github.com/repos/linhongcun/video-studio/releases/tags/' + RELEASE))
        assert release['tag_name'] == RELEASE and release['html_url'] == RELEASE_URL
        assert release['draft'] is False and release['prerelease'] is False and release.get('published_at')
        assert PAGE_URL in release['body'], 'The published Release must identify the delivered lesson'
        changelog = Page(get('changelog', BASE + 'changelog/').decode('utf-8')).root
        entries = [node for node in changelog.find_all('li')
                   if node.find_all('a', href=RELEASE_URL)]
        entry = one(entries, f'Actual {RELEASE} changelog entry')
        assert meta['title'] in entry.text() and '趣味推理 P01' in entry.text()
        assert entry.find_all('a', href='/video-studio/episodes/horse-racing/')
        assert any(has_class(node, 'k-fix') and node.text() == '修正' for node in entry.find_all('span'))
        checked_at = datetime.now(timezone.utc)
        report = {'status': 'passed', 'checkedAtUTC': checked_at.isoformat(),
                  'checkedAtBeijing': checked_at.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
                  'executedBy': 'Codex P01 canonical delivery verification',
                  'release': RELEASE, 'p01FirstRelease': FIRST_RELEASE,
                  'localCandidateSiteVersion': 'v' + version, 'deployedSiteVersion': deployed_version,
                  'versionScope': 'P01 debut, the verified ending-revision Release, and the deployment-wide version are separate identities; all P01 bytes, current sentence/chapter facts and directory assertions remain exact.',
                  'canonicalQueriesAdded': False, 'remoteMediaSaved': False,
                  'fullVideoStreamHashed': True, 'captionsExactBytesMatch': True,
                  'subtitleCount': subtitle_count, 'shotCount': len(shots),
                  'results': results, 'chapters': expected_chapters,
                  'finalVideoFrames': offset, 'durationSeconds': offset / fps,
                  'sourceUrl': source_url, 'independentSeries': 'puzzles',
                  'githubRelease': {'id': release['id'], 'tag': release['tag_name'],
                                    'url': release['html_url'], 'publishedAt': release['published_at']},
                  'scope': 'Canonical HTTP delivery, complete media hashes, exact VTT and chapter data, anchors, source, series, directory, RSS and actual Release entry. Browser behavior is recorded separately; no claim of full human listening or measured learning outcomes.'}
        for directory in (PRODUCTION, SITE):
            (directory / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'passed', 'canonicalGetCount': len(results), 'release': RELEASE,
                          'deployedSiteVersion': deployed_version,
                          'videoSha256': results[0]['sha256'],
                          'report': str(PRODUCTION / 'online-verification.json')}, ensure_ascii=False))
    except Exception as error:
        failure = {'status': 'failed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
                   'release': RELEASE, 'p01FirstRelease': FIRST_RELEASE,
                   'error': str(error), 'completedGetCount': len(results),
                   'canonicalQueriesAdded': False, 'remoteMediaSaved': False, 'results': results}
        failure_path = PRODUCTION / 'online-verification-failed.json'
        failure_path.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'failed', 'completedGetCount': len(results),
                          'error': str(error), 'report': str(failure_path)}, ensure_ascii=False))
        raise


if __name__ == '__main__':
    main()
