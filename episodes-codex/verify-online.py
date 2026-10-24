#!/usr/bin/env python3
"""Read-only served-file verification for the final EP01–14 deployment.

GETs canonical Pages URLs; media is hashed incrementally and never saved.
This verifies served files/HTML, not browser playback, animation, or listening.
Use --self-test without a version/output to run offline tests only.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import time
import urllib.error
import urllib.parse
import urllib.request

SITE = 'https://linhongcun.github.io/video-studio/'
GITHUB = 'https://github.com/linhongcun/video-studio'
SLUGS = ['http-request', 'https', 'dns', 'cookie-session', 'cdn',
         'load-balancing', 'browser-cache', 'server-cache', 'cache-consistency',
         'message-queue', 'rate-limit', 'idempotency', 'circuit-breaker', 'degradation']
CHUNK = 128 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            h.update(chunk)
    return h.hexdigest()


def text(value):
    return ' '.join(value.split())


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.links, self.chapter_sets = [], []
        self.visible, self.titles, self.headings = [], [], []
        self.hidden = 0
        self.in_title = False
        self.in_h1 = False
        self.feed(body.decode('utf-8', errors='strict'))
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style', 'template'):
            self.hidden += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'section' and attrs.get('id') == 'player' and 'data-chapters' in attrs:
            chapters = json.loads(attrs['data-chapters'])
            require(isinstance(chapters, list) and chapters, 'empty/malformed data-chapters')
            seen, previous = set(), -1
            for chapter in chapters:
                require(isinstance(chapter, dict), 'malformed chapter row')
                cid, start = chapter.get('id'), chapter.get('start')
                require(isinstance(cid, str) and cid and cid not in seen, 'empty/duplicate chapter ID')
                require(isinstance(chapter.get('title'), str), 'missing chapter title')
                require(type(start) in (int, float) and math.isfinite(start)
                        and start >= 0 and start > previous, 'invalid chapter start')
                seen.add(cid)
                previous = start
            self.chapter_sets.append(chapters)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h1':
            self.in_h1 = False
        if tag in ('script', 'style', 'template'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if self.in_title:
            self.titles.append(value)
        if self.in_h1:
            self.headings.append(value)
        if not self.hidden and not self.in_title:
            self.visible.append(value)

    @property
    def title(self):
        return text(''.join(self.titles))

    @property
    def h1(self):
        return text(''.join(self.headings))

    @property
    def chapters(self):
        require(len(self.chapter_sets) == 1, 'expected exactly one player/data-chapters')
        return self.chapter_sets[0]

    def contains_version(self, version):
        return bool(re.search(r'(?<![\w.])' + re.escape(version) + r'(?![\w.])',
                              ' '.join(self.visible)))


def relative_asset(name):
    p = PurePosixPath(name)
    require(isinstance(name, str) and name and not p.is_absolute()
            and '..' not in p.parts and not urllib.parse.urlsplit(name).scheme
            and not any(c in name for c in '?#\\'), f'unsafe asset filename: {name!r}')
    return p.as_posix()


def stamp(frame, fps):
    ms = round(frame / fps * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}'


def frozen_vtt_and_chapters(sb):
    fps = sb['meta']['fps']
    require(fps == 30, 'expected frozen 30fps storyboard')
    at, cues, groups, previous = 0, [], [], None
    for scene in sb['scenes']:
        require(scene['from'] == at, 'scene start is not the actual shot boundary')
        same = previous and ((scene.get('chapterId') and scene.get('chapterId') == previous.get('chapterId'))
                             or (scene.get('title') and scene.get('title') == previous.get('title')))
        ids = {scene.get('chapterId', scene['id']), scene['id']}
        if same:
            groups[-1]['ids'].update(ids)
        else:
            groups.append({'ids': ids, 'start': at / fps})
        for shot in scene['shots']:
            duration, rows, last = shot['durationInFrames'], shot['subtitles'], -1
            require(shot['from'] == at and duration > 0 and rows, 'invalid frozen shot')
            for row in rows:
                a, b = row['from'], row['to']
                require(type(a) is int and type(b) is int and last < a <= b < duration,
                        'invalid frozen subtitle boundary')
                cues.append(f"{stamp(at + a, fps)} --> {stamp(at + b + 1, fps)}\n{row['text']}")
                last = b
            at += duration
        previous = scene
    require(at == sb['meta']['durationInFrames'], 'storyboard frame sum mismatch')
    return ('WEBVTT\n\n' + '\n\n'.join(cues) + '\n').encode(), groups, at


def load_episode(repo, slug):
    d, built = repo / 'episodes' / slug, repo / 'site/dist/episodes' / slug
    meta = json.loads((d / 'meta.json').read_text())
    require(meta['ep'] == SLUGS.index(slug) + 1 and meta['slug'] == slug, 'episode identity mismatch')
    require(not meta.get('draft') and not meta.get('legacy'), 'episode is still draft/legacy')
    source = f'episodes-codex/{slug}/remotion'
    require(meta.get('sourcePath') == source and (repo / source).is_dir(), 'current Codex sourcePath missing')
    source_url = f'{GITHUB}/tree/main/{source}'
    page = Page((built / 'index.html').read_bytes())
    require(page.h1 == text(meta['title']), 'build H1 differs from current episode title')
    require(source_url in page.links, 'build does not link current Codex source')
    sb = json.loads((d / 'storyboard.json').read_text())
    vtt, groups, frames = frozen_vtt_and_chapters(sb)
    require(meta['finalVideoFrames'] == frames, 'meta/frozen frame count mismatch')
    require((built / 'captions.vtt').read_bytes() == vtt, 'build VTT differs from frozen captions')
    chapters = page.chapters
    require(len(chapters) == len(groups), 'build chapter count differs from actual scene groups')
    for actual, group in zip(chapters, groups):
        require(actual['id'] in group['ids'] and abs(actual['start'] - group['start']) < 1e-6,
                'build chapter ID/time differs from frozen frame boundary')
    assets = {}
    for kind, name in [('video', meta['video']), ('poster', meta['poster'])]:
        name = relative_asset(name)
        production, output = d / name, built / name
        expected = digest(production)
        require(output.stat().st_size == production.stat().st_size and digest(output) == expected,
                f'{kind}: site/dist is stale relative to episodes')
        assets[kind] = {'name': name, 'sha256': expected, 'byteLength': production.stat().st_size}
    assets['captions'] = {'name': 'captions.vtt', 'sha256': hashlib.sha256(vtt).hexdigest(), 'byteLength': len(vtt)}
    return {'ep': meta['ep'], 'slug': slug, 'frames': frames, 'seconds': frames / 30,
            'sourceURL': source_url, 'title': page.title, 'h1': page.h1,
            'chapters': chapters, 'assets': assets, '_vtt': vtt}


def read_get(url, timeout, capture_limit=0, opener=urllib.request.urlopen):
    """One GET, full incremental SHA; only small text may be retained in memory."""
    start = time.monotonic()
    deadline = start + timeout
    request = urllib.request.Request(url, method='GET', headers={
        'User-Agent': 'codex-ep01-14-online-verifier/1.0', 'Cache-Control': 'no-cache',
        'Accept-Encoding': 'identity'})
    h, count, body, retained = hashlib.sha256(), 0, [], 0
    with opener(request, timeout=timeout) as response:
        status = response.status
        require(status == 200, f'GET expected HTTP 200, got {status}')
        require(response.geturl() == url, f'unexpected canonical URL redirect: {response.geturl()}')
        require(response.headers.get('Content-Encoding', 'identity').lower() in ('', 'identity'),
                'unexpected encoded HTTP body despite Accept-Encoding: identity')
        declared = response.headers.get('Content-Length')
        read_chunk = getattr(response, 'read1', response.read)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('single-request total deadline exceeded')
            # urllib exposes the connected socket through HTTPResponse.fp.raw.
            # Refresh its read timeout so trickling chunks do not reset the deadline.
            raw = getattr(getattr(response, 'fp', None), 'raw', None)
            sock = getattr(raw, '_sock', None)
            if sock is not None:
                sock.settimeout(min(timeout, remaining))
            chunk = read_chunk(CHUNK)
            if not chunk:
                break
            h.update(chunk)
            count += len(chunk)
            if retained < capture_limit:
                piece = chunk[:capture_limit - retained]
                body.append(piece)
                retained += len(piece)
        require(time.monotonic() <= deadline, 'single-request total deadline exceeded')
        require(declared is None or int(declared) == count, 'incomplete Content-Length body')
        return {'url': url, 'status': status, 'finalURL': response.geturl(),
                'sha256': h.hexdigest(), 'byteLength': count, 'bodyComplete': True,
                'contentType': response.headers.get('Content-Type'),
                'elapsedSeconds': round(time.monotonic() - start, 3)}, b''.join(body)


def fetch_verify(url, evaluator, timeout, attempts, capture_limit=0):
    history, result = [], None
    for number in range(1, attempts + 1):
        try:
            result, body = read_get(url, timeout, capture_limit)
            errors, checks = evaluator(result, body)
            result.update(passed=not errors, errors=errors, checks=checks)
        except Exception as exc:
            result = {'url': url, 'passed': False, 'bodyComplete': False,
                      'errors': [f'{type(exc).__name__}: {exc}']}
        result['attempt'] = number
        history.append(dict(result))
        if result['passed']:
            break
        if number < attempts:
            time.sleep(min(2, .5 * 2 ** (number - 1)))
    result['attempts'] = history
    return result


def blob_evaluator(expected, exact=None):
    def evaluate(result, body):
        checks = {'fullSHA256': result['sha256'] == expected['sha256'],
                  'byteLength': result['byteLength'] == expected['byteLength']}
        if exact is not None:
            checks['byteForByte'] = result['byteLength'] == len(exact) and body == exact
        return [key + ' mismatch' for key, ok in checks.items() if not ok], checks
    return evaluate


def chapter_equal(actual, expected):
    return len(actual) == len(expected) and all(
        a['id'] == e['id'] and a['title'] == e['title'] and abs(a['start'] - e['start']) < 1e-6
        for a, e in zip(actual, expected))


def episode_html_evaluator(expected):
    def evaluate(result, body):
        require(len(body) == result['byteLength'], 'HTML exceeds in-memory capture limit')
        page = Page(body)
        checks = {'title': page.title == expected['title'], 'h1': page.h1 == expected['h1'],
                  'currentCodexSource': expected['sourceURL'] in page.links,
                  'chapterIDsTitlesAndTimes': chapter_equal(page.chapters, expected['chapters'])}
        return [key + ' mismatch' for key, ok in checks.items() if not ok], dict(
            checks, actualTitle=page.title, actualH1=page.h1, actualChapters=page.chapters)
    return evaluate


def verify_episode(expected, timeout, attempts):
    slug = expected['slug']
    base = SITE + 'episodes/' + slug + '/'
    assets = {}
    for kind in ('video', 'poster', 'captions'):
        asset = expected['assets'][kind]
        exact = expected['_vtt'] if kind == 'captions' else None
        assets[kind] = fetch_verify(base + urllib.parse.quote(asset['name'], safe='/'),
            blob_evaluator(asset, exact), timeout, attempts, len(exact) + 1 if exact is not None else 0)
    assets['html'] = fetch_verify(base, episode_html_evaluator(expected), timeout, attempts, 4 * 1024 * 1024)
    return {'ep': expected['ep'], 'slug': slug, 'passed': all(x['passed'] for x in assets.values()),
            'expected': {k: v for k, v in expected.items() if not k.startswith('_')}, 'checks': assets}


def verify_version_page(name, version, timeout, attempts):
    url = SITE if name == 'home' else SITE + 'changelog/'
    def evaluate(result, body):
        require(len(body) == result['byteLength'], 'HTML exceeds in-memory capture limit')
        page = Page(body)
        checks = {'visibleReleaseVersion': page.contains_version(version)}
        if name == 'changelog':
            checks['releaseTagLink'] = f'{GITHUB}/releases/tag/{version}' in page.links
        return [key + ' missing' for key, ok in checks.items() if not ok], checks
    return {'name': name, **fetch_verify(url, evaluate, timeout, attempts, 4 * 1024 * 1024)}


def save_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def self_test():
    source = f'{GITHUB}/tree/main/episodes-codex/server-cache/remotion'
    chapters = [{'id': 'cache', 'title': '文章标题 & 分镜标题可以不同', 'start': 31.7}]
    markup = ('<title>实际标题 · IT小村</title><h1>实际标题</h1><section id="player" data-chapters="'
              + html.escape(json.dumps(chapters, ensure_ascii=False), quote=True)
              + '"></section><a href="' + source + '">源码</a><footer>v1.2.3</footer>'
              + '<script>v9.9.9</script>')
    page = Page(markup.encode())
    require(page.chapters == chapters and page.contains_version('v1.2.3')
            and not page.contains_version('v9.9.9') and not page.contains_version('v1.2'), 'parser/version self-test')
    expected = {'title': page.title, 'h1': page.h1, 'sourceURL': source, 'chapters': chapters}
    evaluate = episode_html_evaluator(expected)
    require(not evaluate({'byteLength': len(markup.encode())}, markup.encode())[0], 'HTML self-test')
    changed = markup.replace('31.7', '31.8').encode()
    require(bool(evaluate({'byteLength': len(changed)}, changed)[0]), 'chapter mismatch was accepted')
    raw = b'no remote media is written\n' * 20000
    requests = []
    class Response(io.BytesIO):
        status = 200
        headers = {'Content-Length': str(len(raw)), 'Content-Type': 'video/mp4'}
        def geturl(self):
            return SITE + 'self-test.mp4'
    def opener(request, timeout):
        requests.append((request.get_method(), timeout))
        return Response(raw)
    result, captured = read_get(SITE + 'self-test.mp4', 5, 17, opener)
    require(requests == [('GET', 5)] and result['sha256'] == hashlib.sha256(raw).hexdigest()
            and result['byteLength'] == len(raw) and captured == raw[:17], 'full-stream/capture self-test')
    vtt = b'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\ntext\n'
    evaluator = blob_evaluator({'sha256': hashlib.sha256(vtt).hexdigest(), 'byteLength': len(vtt)}, vtt)
    require(not evaluator({'sha256': hashlib.sha256(vtt).hexdigest(), 'byteLength': len(vtt)}, vtt)[0], 'VTT equality self-test')
    require(bool(evaluator({'sha256': hashlib.sha256(vtt).hexdigest(), 'byteLength': len(vtt)}, vtt.replace(b'\n', b'\r\n'))[0]), 'VTT byte mismatch was accepted')
    print('OFFLINE self-test PASS: HTML entities/title/source/chapters, version boundaries, full streaming SHA, byte-exact VTT; no network used.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', help='Final published Release tag, e.g. v0.47.0')
    parser.add_argument('--out', type=Path, help='Result JSON path under /tmp')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--slugs', nargs='+', choices=SLUGS, default=SLUGS,
                        help='Episodes to verify (default: all 14 episodes)')
    parser.add_argument('--timeout', type=float, default=30, help='Single-request deadline, 0 < seconds <= 30 (default 30)')
    parser.add_argument('--attempts', type=int, choices=(1, 2, 3), default=3, help='Maximum GET attempts, including semantic mismatch retries')
    parser.add_argument('--self-test', action='store_true', help='Offline synthetic tests only; never fetch a URL')
    parser.add_argument('--check-local', action='store_true', help='Local episodes/dist preflight only; never verify deployment')
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.slugs))
    if args.self_test:
        self_test()
        return 0
    if not args.version or not re.fullmatch(r'v\d+\.\d+\.\d+', args.version) or args.out is None:
        parser.error('--version vX.Y.Z and --out /tmp/PATH are required')
    if not 0 < args.timeout <= 30:
        parser.error('--timeout must be greater than 0 and at most 30 seconds')
    output = args.out.resolve()
    if not output.is_relative_to(Path('/tmp').resolve()):
        parser.error('--out must be under /tmp; repository/production files are never written')
    repo = args.repo.resolve()
    report = {'scope': 'local-only' if args.check_local else 'canonical-served-files-only',
              'browserPlaybackReview': False, 'remoteMediaWrittenToDisk': False,
              'releaseVersion': args.version, 'repo': str(repo), 'site': SITE,
              'selectedSlugs': selected,
              'startedAtUTC': datetime.now(timezone.utc).isoformat(), 'concurrency': 2,
              'singleRequestTimeoutSeconds': args.timeout, 'maximumAttempts': args.attempts,
              'preflightErrors': [], 'episodes': [], 'pages': [], 'onlineVerified': False}
    expected = []
    try:
        version = 'v' + json.loads((repo / 'site/package.json').read_text())['version']
        require(version == args.version, f'package version {version} differs from {args.version}')
        require(Page((repo / 'site/dist/index.html').read_bytes()).contains_version(args.version),
                'local homepage build is stale relative to the requested version')
    except Exception as exc:
        report['preflightErrors'].append(str(exc))
    for slug in selected:
        try:
            expected.append(load_episode(repo, slug))
        except Exception as exc:
            report['preflightErrors'].append(f'{slug}: {type(exc).__name__}: {exc}')
    if report['preflightErrors'] or args.check_local:
        report['localPreflightPassed'] = not report['preflightErrors']
        report['passed'] = report['localPreflightPassed'] if args.check_local else False
        report['episodes'] = [{k: v for k, v in e.items() if not k.startswith('_')} for e in expected]
        report['finishedAtUTC'] = datetime.now(timezone.utc).isoformat()
        save_report(output, report)
        print('LOCAL ONLY; deployment has NOT been verified.', flush=True)
        for error in report['preflightErrors']:
            print('PREFLIGHT FAIL:', error, flush=True)
        print(f'{len(expected)}/{len(selected)} local episode expectations loaded; JSON: {output}', flush=True)
        return 0 if report['passed'] else 1
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = {executor.submit(verify_episode, e, args.timeout, args.attempts): ('episode', e['slug']) for e in expected}
        jobs.update({executor.submit(verify_version_page, name, args.version, args.timeout, args.attempts): ('page', name)
                     for name in ('home', 'changelog')})
        for future in as_completed(jobs):
            kind, name = jobs[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {'name': name, 'slug': name, 'passed': False, 'error': f'{type(exc).__name__}: {exc}'}
            report['episodes' if kind == 'episode' else 'pages'].append(result)
            if kind == 'episode':
                video = result.get('checks', {}).get('video', {})
                print(f"EP{SLUGS.index(name)+1:02d} {name}: {'PASS' if result['passed'] else 'FAIL'} "
                      f"full video SHA256={video.get('sha256', 'unavailable')}", flush=True)
            else:
                print(f"{name}: {'PASS' if result['passed'] else 'FAIL'} {args.version}", flush=True)
    report['episodes'].sort(key=lambda e: SLUGS.index(e['slug']))
    report['localPreflightPassed'] = True
    report['passed'] = len(report['episodes']) == len(selected) and len(report['pages']) == 2 and all(
        row['passed'] for row in report['episodes'] + report['pages'])
    report['onlineVerified'] = report['passed']
    report['finishedAtUTC'] = datetime.now(timezone.utc).isoformat()
    save_report(output, report)
    print(f"Canonical served-file verification {'PASS' if report['passed'] else 'FAIL'}; JSON: {output}", flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
