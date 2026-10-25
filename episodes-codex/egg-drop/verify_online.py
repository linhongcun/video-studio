#!/usr/bin/env python3
"""Verify P05 after its Release-following Pages deployment has succeeded.

Uses ordinary canonical GETs with the inherited proxy and default CA trust.
Hashes complete remote media streams without saving or retaining their bodies.
No cache-busting query, Range, forced-cache headers, retries, or UI claims.
Optional connector evidence replaces only the Release API HTTP GET, retaining
the actual provenance and reporting nine site GETs plus one independent read.
"""
from __future__ import annotations

import argparse
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

from sync_site import load_facts, check_local_delivery, expected_vtt, puzzle_slugs


BASE = 'https://linhongcun.github.io/video-studio/'
REPO_URL = 'https://github.com/linhongcun/video-studio'
SLUG = 'egg-drop'
FIRST_RELEASE = 'v0.67.0'
RELEASE = 'v0.67.0'
PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SITE = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
PAGE_URL = BASE + 'episodes/' + SLUG + '/'
RELEASE_URL = REPO_URL + '/releases/tag/' + RELEASE
RELEASE_API_URL = 'https://api.github.com/repos/linhongcun/video-studio/releases/tags/' + RELEASE


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_release(release):
    assert release['tag_name'] == RELEASE and release['html_url'] == RELEASE_URL
    assert release['draft'] is False and release['prerelease'] is False and release.get('published_at')
    assert PAGE_URL in release['body'], 'The published Release must identify the delivered lesson'


def load_release_evidence(path):
    """Read the parent's actual connector response, never synthesize a GET."""
    raw = path.read_bytes()
    envelope = json.loads(raw)
    release = envelope['payload']
    assert isinstance(release, dict), 'Connector evidence payload must be the actual Release object'
    provenance = {key: value for key, value in envelope.items() if key != 'payload'}
    assert provenance, 'Connector evidence must retain its retrieval provenance'
    validate_release(release)
    return release, {'transport': 'independent-github-connector-evidence',
                     'evidenceFile': str(path.resolve()),
                     'evidenceFileSHA256': hashlib.sha256(raw).hexdigest(),
                     'provenance': provenance,
                     'connectorCallPerformedByVerifier': False}


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
    assert f"EP.{meta['ep']:02d} · {meta['episodePart']}" in root.text()
    source_url = REPO_URL + '/tree/main/' + meta['sourcePath']
    assert root.find_all('a', href=source_url), 'Missing current production source link'
    player = one(root.find_all('section', id='player'), 'player')
    chapters = json.loads(player.attrs['data-chapters'])
    assert len(chapters) == len(expected_chapters) and expected_chapters
    for article_only in ('why-fourteen', 'bounds'):
        assert article_only not in [chapter['id'] for chapter in chapters]
        assert len(root.find_all('h2', id=article_only)) == 1, ('Keep article-only section', article_only)
        assert not root.find_all('a', **{'data-seek': article_only}), ('Article-only section must not seek the video', article_only)
    for actual, expected in zip(chapters, expected_chapters):
        assert actual['id'] == expected['id'] and actual['title'] == expected['title']
        assert actual['start'] == expected['frame'] / fps
        assert root.find_all(id=expected['id']), ('Missing article anchor', expected['id'])
        assert root.find_all('a', **{'data-seek': expected['id']}), ('Missing article seek action', expected['id'])
        controls = player.find_all('a', **{'data-id': expected['id']})
        assert controls and all(float(control.attrs['data-start']) == expected['start']
                                for control in controls)
    directory = one(root.find_all('nav', **{'aria-label': '趣味推理课程目录'}), 'P05 course directory')
    links = directory.find_all('a')
    expected_links = ['/video-studio/episodes/' + slug + '/' for slug in puzzle_slugs()]
    assert [link.attrs['href'] for link in links] == expected_links, 'Exact live puzzle directory; no unproduced questions'
    current = one([link for link in links if link.attrs.get('aria-current') == 'page'], 'current puzzle')
    assert current.attrs['href'] == '/video-studio/episodes/egg-drop/'
    pager = one(root.find_all('nav', **{'aria-label': '上一课 / 下一课'}), 'within-puzzle pager')
    assert all(link.attrs['href'] in expected_links for link in pager.find_all('a')), 'Unrelated prerequisite in P05'
    assert pager.find_all('a', href='/video-studio/episodes/monty-hall/'), 'P05 must follow P04'
    video = one(player.find_all('video'), 'video element')
    assert 'controls' in video.attrs
    assert one(video.find_all('source'), 'video source').attrs['src'] == '/video-studio/episodes/egg-drop/' + meta['video']
    assert one(video.find_all('track'), 'caption track').attrs['src'] == '/video-studio/episodes/egg-drop/captions.vtt'
    ld = json.loads(one(root.find_all('script', type='application/ld+json'), 'VideoObject').text())
    assert ld['name'] == meta['title']
    assert ld['contentUrl'] == PAGE_URL + meta['video']
    assert ld['embedUrl'] == PAGE_URL
    assert ld['duration'] == f'PT{int(expected_frames / fps) // 60}M{int(expected_frames / fps) % 60}S'
    return source_url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-api-json', type=Path,
                        help='Parent-recorded GitHub connector envelope with actual payload and retrieval provenance.')
    args = parser.parse_args()
    release_from_connector, release_evidence = (None, None)
    if args.release_api_json is not None:
        # Validate the supplied independent evidence before making any site GET.
        release_from_connector, release_evidence = load_release_evidence(args.release_api_json)
    facts = load_facts()
    check_local_delivery(facts)
    meta = facts['meta']
    expected_chapters, expected_subtitles = facts['chapters'], facts['subtitles']
    offset, fps, shots = facts['frames'], facts['fps'], facts['shots']
    subtitle_count = len(expected_subtitles)
    version = json.loads((ROOT / 'site/package.json').read_text())['version']
    # The debut tag identifies P05; concurrent courses may advance the whole site.
    assert version_tuple(version) >= version_tuple(RELEASE)
    assert meta['firstRelease'] == FIRST_RELEASE and meta['draft'] is False
    vtt_path = DIST / 'episodes' / SLUG / 'captions.vtt'
    expected_vtt_bytes = expected_vtt(facts)
    assert vtt_path.read_bytes() == expected_vtt_bytes
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
                       expected_sha=sha_file(vtt_path), expected_size=len(expected_vtt_bytes))
        assert captions == expected_vtt_bytes and captions.decode('utf-8').count('-->') == subtitle_count
        episode = Page(get('episode', PAGE_URL).decode('utf-8'))
        source_url = check_episode(episode, meta, expected_chapters, offset, fps)
        home = Page(get('home', BASE).decode('utf-8')).root
        assert home.find_all('a', href='/video-studio/learn/#puzzles'), 'Missing homepage puzzle direction'
        assert home.find_all('a', href='/video-studio/episodes/egg-drop/'), 'Missing homepage P05 lesson'
        deployed_version = deployed_site_version(home)
        assert version_tuple(deployed_version) >= version_tuple(RELEASE), ('Deployed site predates P05', deployed_version)
        series = Page(get('series', BASE + 'series/puzzles/').decode('utf-8')).root
        assert '趣味推理' in series.text() and meta['title'] in series.text()
        series_cards = [node.attrs['href'] for node in series.find_all('a') if has_class(node, 'lesson')]
        assert sorted(series_cards) == sorted('/video-studio/episodes/' + slug + '/' for slug in puzzle_slugs())
        learn = Page(get('learn', BASE + 'learn/').decode('utf-8')).root
        puzzle_track = one(learn.find_all(id='puzzles'), 'Puzzle learning direction')
        assert '趣味推理' in puzzle_track.text()
        assert puzzle_track.find_all('a', href='/video-studio/series/puzzles/')
        lesson_lists = [node for node in puzzle_track.find_all('ol') if has_class(node, 'chapter-lessons')]
        assert len(lesson_lists) == 1
        lesson_links = lesson_lists[0].find_all('a')
        expected_links = ['/video-studio/episodes/' + slug + '/' for slug in puzzle_slugs()]
        assert [link.attrs['href'] for link in lesson_links] == expected_links
        rss = get('rss', BASE + 'rss.xml').decode('utf-8')
        assert PAGE_URL in rss and meta['title'] in rss and '趣味推理 P05' in rss
        release = release_from_connector if release_evidence is not None else json.loads(get('github-release', RELEASE_API_URL))
        validate_release(release)
        changelog = Page(get('changelog', BASE + 'changelog/').decode('utf-8')).root
        entries = [node for node in changelog.find_all('li')
                   if node.find_all('a', href=RELEASE_URL)]
        entry = one(entries, f'Actual {RELEASE} changelog entry')
        assert meta['title'] in entry.text() and '趣味推理 P05' in entry.text()
        assert entry.find_all('a', href='/video-studio/episodes/egg-drop/')
        assert any(has_class(node, 'k-add') and node.text() == '新增' for node in entry.find_all('span'))
        checked_at = datetime.now(timezone.utc)
        report = {'status': 'passed', 'checkedAtUTC': checked_at.isoformat(),
                  'checkedAtBeijing': checked_at.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
                  'executedBy': 'Codex P05 canonical delivery verification',
                  'release': RELEASE, 'firstRelease': FIRST_RELEASE,
                  'localCandidateSiteVersion': 'v' + version, 'deployedSiteVersion': deployed_version,
                  'versionScope': 'The P05 debut Release and deployment-wide version are separate identities; all P05 bytes, current sentence/chapter facts and exact live puzzle directory remain strict.',
                  'canonicalQueriesAdded': False, 'remoteMediaSaved': False,
                  'canonicalGetCount': len(results), 'siteCanonicalGetCount': 9,
                  'directReleaseApiGetCount': 0 if release_evidence is not None else 1,
                  'independentConnectorReleaseReadCount': 1 if release_evidence is not None else 0,
                  'releaseApiTransport': 'independent-github-connector-evidence' if release_evidence is not None else 'direct-canonical-http-get',
                  'releaseApiEvidence': release_evidence,
                  'fullVideoStreamHashed': True, 'captionsExactBytesMatch': True,
                  'subtitleCount': subtitle_count, 'shotCount': len(shots),
                  'results': results, 'chapters': expected_chapters,
                  'finalVideoFrames': offset, 'durationSeconds': offset / fps,
                  'sourceUrl': source_url, 'independentSeries': 'puzzles',
                  'githubRelease': {'id': release['id'], 'tag': release['tag_name'],
                                    'url': release['html_url'], 'publishedAt': release['published_at']},
                  'scope': 'Canonical HTTP delivery, complete media hashes, exact VTT and chapter data, anchors, source, series, directory, RSS and actual Release entry. Browser behavior is recorded separately; no claim of full human listening or measured learning outcomes.'}
        assert len(results) == (9 if release_evidence is not None else 10), 'Unexpected first-attempt canonical GET count'
        for directory in (PRODUCTION, SITE):
            (directory / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'passed', 'canonicalGetCount': len(results), 'release': RELEASE,
                          'independentConnectorReleaseReadCount': 1 if release_evidence is not None else 0,
                          'releaseApiTransport': report['releaseApiTransport'],
                          'deployedSiteVersion': deployed_version,
                          'videoSha256': results[0]['sha256'],
                          'report': str(PRODUCTION / 'online-verification.json')}, ensure_ascii=False))
    except Exception as error:
        failure = {'status': 'failed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
                   'release': RELEASE, 'firstRelease': FIRST_RELEASE,
                   'error': str(error), 'completedGetCount': len(results),
                   'releaseApiTransport': 'independent-github-connector-evidence' if release_evidence is not None else 'direct-canonical-http-get',
                   'releaseApiEvidence': release_evidence,
                   'canonicalQueriesAdded': False, 'remoteMediaSaved': False, 'results': results}
        failure_path = PRODUCTION / 'online-verification-failed.json'
        failure_path.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'failed', 'completedGetCount': len(results),
                          'error': str(error), 'report': str(failure_path)}, ensure_ascii=False))
        raise


if __name__ == '__main__':
    main()
