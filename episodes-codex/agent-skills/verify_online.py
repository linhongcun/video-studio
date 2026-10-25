#!/usr/bin/env python3
"""Verify a published Skills release with ordinary canonical HTTPS GETs.

No cache-busters, credentials, browser automation, or remote writes. Timing and
VTT expectations come from sync_site; HTTP checks do not prove video playback.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SLUG = 'agent-skills'
RETIRED_SLUGS = ('agent-intro', 'agent-tool-execution')
REPRESENTATIVE_SLUGS = ('water-jug', 'observer-pattern')


class PageFacts(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    handle_startendtag = handle_starttag

    @property
    def links(self):
        return [a['href'] for tag, a in self.elements if tag == 'a' and a.get('href')]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True,
                        help='Canonical HTTPS site root, including its deployment path.')
    parser.add_argument('--release', required=True, help='Expected release, e.g. v0.62.0.')
    parser.add_argument('--out', required=True, type=Path, help='Local JSON report path.')
    args = parser.parse_args()
    parts = urlsplit(args.base)
    if (parts.scheme != 'https' or not parts.netloc or parts.username or parts.password
            or parts.query or parts.fragment or not parts.path.endswith('/')):
        parser.error('--base must be a canonical HTTPS root ending in /, without credentials/query/fragment')
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.release):
        parser.error('--release must be an explicit vMAJOR.MINOR.PATCH version')
    return args


def request_once(check):
    """HTTPError is a response too: a retired resource is expected to be 404."""
    result = {'name': check['name'], 'url': check['url'],
              'expectedStatus': check.get('status', 200)}
    try:
        request = Request(check['url'], headers={
            'User-Agent': 'video-studio-canonical-verifier/1.0',
            'Accept-Encoding': 'identity',
        })
        try:
            with urlopen(request, timeout=45) as response:
                status, final_url, body = response.status, response.url, response.read()
        except HTTPError as response:
            with response:
                status, final_url, body = response.code, response.url, response.read()
        result.update(actualStatus=status, finalUrl=final_url, bytes=len(body),
                      actualSHA256=digest(body))
        errors = []
        if status != result['expectedStatus']:
            errors.append(f"HTTP {status}, expected {result['expectedStatus']}")
        if 'sha256' in check:
            result['expectedSHA256'] = check['sha256']
            result['completeBytesMatch'] = digest(body) == check['sha256']
            if not result['completeBytesMatch']:
                errors.append('Complete response SHA-256 differs from the local release artifact')
        if 'bytes' in check:
            result['expectedBytes'] = check['bytes']
            if len(body) != check['bytes']:
                errors.append('Complete response byte count differs from the local release artifact')
        if 'validate' in check and status == 200:
            assertions = check['validate'](body)
            result['assertions'] = assertions
            errors.extend(name for name, passed in assertions.items() if not passed)
        result.update(passed=not errors, errors=errors)
    except Exception as error:
        result.update(passed=False, errors=[f'{type(error).__name__}: {error}'])
    return result


def main():
    args = parse_args()
    report = {
        'checkedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'timeZone': 'Asia/Shanghai', 'base': args.base, 'release': args.release,
        'method': 'Ordinary canonical HTTPS GET; default urllib proxy and TLS trust; no cache-buster.',
        'scope': 'Published artifacts, response bytes, static chapter/link metadata, navigation and retained examples.',
        'limitations': [
            'No browser playback, seek, rendering, audio listening or client-side search behavior is claimed.',
            'Representative retained media checks do not claim that every other remote course was downloaded.',
        ],
        'localPreflight': {}, 'results': [], 'errors': [], 'skippedRepresentatives': [],
    }
    try:
        # Import is deliberately after --help handling. The existing producer is
        # the sole owner of frame/timestamp and expected-VTT construction.
        from sync_site import load_facts, expected_vtt, sha_file
        facts = load_facts()
        site = ROOT / 'episodes' / SLUG
        meta = json.loads((site / 'meta.json').read_text())
        assert meta['slug'] == SLUG and meta['firstRelease'] == args.release
        assert meta['ep'] == facts['config']['episode'] == 31
        assert meta['series'] == 'agent' and meta['draft'] is False
        assert meta['sourcePath'] == str(PRODUCTION.relative_to(ROOT)) + '/remotion'
        assert all(Path(meta[key]).name == meta[key] for key in ('video', 'poster'))
        assert meta['finalVideoFrames'] == facts['frames']
        assert meta['title'] == facts['config']['title']
        assert len(facts['chapters']) == 4
        page_url = urljoin(args.base, f'episodes/{SLUG}/')
        video_url = urljoin(page_url, meta['video'])
        poster_url = urljoin(page_url, meta['poster'])
        vtt_url = urljoin(page_url, 'captions.vtt')
        source_url = 'https://github.com/linhongcun/video-studio/tree/main/' + meta['sourcePath']
        wanted_chapters = [{key: c[key] for key in ('id', 'title', 'start')}
                           for c in facts['chapters']]
        expected_caption_bytes = expected_vtt(facts)
        assert sha_file(site / meta['video']) == facts['render']['sha256']
        assert sha_file(site / meta['poster']) == sha_file(PRODUCTION / meta['poster'])
        report['localPreflight'] = {
            'passed': True, 'episode': meta['ep'], 'title': meta['title'],
            'frames': facts['frames'], 'fps': facts['fps'],
            'frozenInputCount': facts['frozenInputCount'],
            'chapterExpectations': wanted_chapters,
            'vttCues': len(facts['subtitles']), 'expectedVttSHA256': digest(expected_caption_bytes),
        }

        def has_new_link(body):
            page = PageFacts(body.decode('utf-8'))
            links = {urljoin(args.base, href) for href in page.links}
            return {'newCourseLinkPresent': page_url in links,
                    'retiredCourseLinksAbsent': all(
                        not any(urlsplit(href).path.startswith(urlsplit(args.base).path + f'episodes/{old}/')
                                for href in links) for old in RETIRED_SLUGS)}

        def validate_page(body):
            page = PageFacts(body.decode('utf-8'))
            ids = {attrs.get('id') for _, attrs in page.elements}
            players = [attrs for _, attrs in page.elements if attrs.get('id') == 'player']
            actual_chapters = json.loads(players[0]['data-chapters']) if len(players) == 1 else []
            assertions = {
                'onePlayerWithExactFourChapterMetadata': actual_chapters == wanted_chapters,
                'allFourArticleAnchorsPresent': all(c['id'] in ids for c in wanted_chapters),
                'sourceEntryMatchesPublishedMeta': source_url in page.links,
                'videoSourceMatchesPublishedMeta': any(
                    tag in ('video', 'source') and urljoin(args.base, attrs.get('src', '')) == video_url
                    for tag, attrs in page.elements),
                'posterMatchesPublishedMeta': any(
                    tag == 'video' and urljoin(args.base, attrs.get('poster', '')) == poster_url
                    for tag, attrs in page.elements),
                'captionTrackMatchesExpectedRoute': any(
                    tag == 'track' and urljoin(args.base, attrs.get('src', '')) == vtt_url
                    for tag, attrs in page.elements),
            }
            for chapter in wanted_chapters:
                anchors = [attrs for tag, attrs in page.elements
                           if tag == 'a' and attrs.get('data-id') == chapter['id']]
                assertions['chapterLinkAndStart:' + chapter['id']] = bool(anchors) and all(
                    attrs.get('href') == '#' + chapter['id']
                    and abs(float(attrs.get('data-start', 'nan')) - chapter['start']) < 1e-9
                    for attrs in anchors)
            return assertions

        def validate_vtt(body):
            return {'allCaptionTextAndFrameDerivedTimesExact': body == expected_caption_bytes}

        def validate_feed(body):
            text = body.decode('utf-8')
            return {'newCourseCanonicalUrlPresent': page_url in text,
                    'retiredCanonicalUrlsAbsent': all(
                        urljoin(args.base, f'episodes/{old}/') not in text for old in RETIRED_SLUGS)}

        def validate_learn(body):
            result = has_new_link(body)
            result['publishedAgentDirectionVisible'] = any(
                attrs.get('id') == 'agent' for _, attrs in PageFacts(body.decode('utf-8')).elements)
            return result

        def validate_changelog(body):
            result = has_new_link(body)
            result['expectedReleaseVisible'] = args.release in body.decode('utf-8')
            return result

        checks = [
            {'name': 'new-course-page', 'url': page_url, 'validate': validate_page},
            {'name': 'new-complete-video', 'url': video_url,
             'sha256': sha_file(site / meta['video']), 'bytes': (site / meta['video']).stat().st_size},
            {'name': 'new-complete-poster', 'url': poster_url,
             'sha256': sha_file(site / meta['poster']), 'bytes': (site / meta['poster']).stat().st_size},
            {'name': 'new-exact-captions', 'url': vtt_url,
             'sha256': digest(expected_caption_bytes), 'bytes': len(expected_caption_bytes),
             'validate': validate_vtt},
        ]
        for name, relative, validate in [
            ('home-entry', '', has_new_link), ('learn-entry', 'learn/', validate_learn),
            ('library-entry', 'library/', has_new_link),
            ('agent-series-entry', 'series/agent/', has_new_link),
            ('rss-entry', 'rss.xml', validate_feed),
            ('sitemap-course-entry', 'sitemap-0.xml', validate_feed),
            ('changelog-release-entry', 'changelog/', validate_changelog),
        ]:
            checks.append({'name': name, 'url': urljoin(args.base, relative), 'validate': validate})
        checks.append({'name': 'sitemap-index-entry', 'url': urljoin(args.base, 'sitemap-index.xml'),
                       'validate': lambda body: {'sitemapDataUrlPresent':
                           urljoin(args.base, 'sitemap-0.xml') in body.decode('utf-8')}})
        for slug in RETIRED_SLUGS:
            for suffix in ('', 'video.mp4'):
                checks.append({'name': f'retired-{slug}-' + ('page' if not suffix else 'video'),
                               'url': urljoin(args.base, f'episodes/{slug}/' + suffix), 'status': 404})
        for slug in REPRESENTATIVE_SLUGS:
            meta_path = ROOT / 'episodes' / slug / 'meta.json'
            if not meta_path.exists():
                report['skippedRepresentatives'].append({'slug': slug, 'reason': 'No current local published meta.'})
                continue
            retained_meta = json.loads(meta_path.read_text())
            assert not retained_meta.get('draft'), ('Representative is not published', slug)
            for kind in ('video', 'poster'):
                local = meta_path.parent / retained_meta[kind]
                checks.append({'name': f'retained-{slug}-{kind}',
                               'url': urljoin(args.base, f'episodes/{slug}/' + retained_meta[kind]),
                               'sha256': sha_file(local), 'bytes': local.stat().st_size})
        with ThreadPoolExecutor(max_workers=4) as pool:
            report['results'] = list(pool.map(request_once, checks))
        report['errors'] = [f"{row['name']}: {message}"
                            for row in report['results'] for message in row['errors']]
    except Exception as error:
        report['localPreflight'].update(passed=False, error=f'{type(error).__name__}: {error}')
        report['errors'].append('Local preflight failed; no passing publication verdict is available.')
    report['passed'] = bool(report['results']) and not report['errors']
    report['completedAt'] = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'requests': len(report['results']),
                      'errors': report['errors'], 'report': str(args.out)}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
