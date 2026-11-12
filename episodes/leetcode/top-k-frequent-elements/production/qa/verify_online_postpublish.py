#!/usr/bin/env python3
"""Verify LC347 deployment with exact build-commit source links; default is an offline plan.

Run after the final site build and deployment:
  python3 .../qa/verify_online_postpublish.py --execute --version v0.106.0

Every network action is a full GET with a <=30-second total request deadline.
Remote media is streamed into SHA-256, never saved. This checks served bytes
and HTML semantics, not browser playback, human listening, or animation.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sys
import subprocess
from urllib.parse import quote

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
PUB = EP.parent / 'publication'
DIST = ROOT / 'site/dist'
SLUG = 'top-k-frequent-elements'
SITE = 'https://linhongcun.github.io/video-studio/'
GITHUB = 'https://github.com/linhongcun/video-studio'
HELPER = ROOT / 'scripts/verify-online.py'
FROZEN_VERIFIER = EP / 'scripts/verify_online.py'

# Reuse only the generic parser/streaming GET/check helpers. In particular,
# old.load_episode assumes EP01-14 identities and is never called here.
spec = importlib.util.spec_from_file_location('served_file_helpers', HELPER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
require = old.require


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return old.digest(path)


def asset_name(value):
    return old.relative_asset(value)


def parse_vtt(raw):
    text = raw.decode('utf-8', errors='strict')
    require(text.startswith('WEBVTT\n'), 'built captions are not WebVTT')
    blocks = re.split(r'\n\s*\n', text.strip())[1:]
    cues = []
    pattern = r'(\d{2,}):([0-5]\d):([0-5]\d)\.(\d{3})'
    def seconds(value):
        match = re.fullmatch(pattern, value)
        require(match is not None, f'invalid WebVTT timestamp: {value}')
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 1000
    previous = -1
    for block in blocks:
        lines = block.splitlines()
        require(len(lines) >= 2 and ' --> ' in lines[0], 'unexpected cue ID/settings/empty text')
        start, end = map(seconds, lines[0].split(' --> '))
        require(0 <= start < end and start >= previous, 'overlapping/invalid VTT cue')
        cues.append({'start': start, 'end': end, 'text': '\n'.join(lines[1:])})
        previous = end
    require(cues, 'built VTT has no cues')
    return cues


def validate_timing(sb, meta, vtt):
    fps = sb['meta']['fps']
    require(fps == 30, 'expected 30fps')
    body = sb['meta']['durationInFrames']
    card = sb['meta']['unvoicedEndCard']
    appendix = meta['referenceAppendix']
    final = meta['finalVideoFrames']
    require(card['kind'] == 'full-python-solution' and card['durationInFrames'] == 150,
            'missing five-second complete Python card')
    require(card['from'] + card['durationInFrames'] == body, 'Python card must end the body')
    require(appendix['from'] == body and appendix['durationInFrames'] == 150,
            'reference appendix must follow the full body including Python card')
    require(final == body + appendix['durationInFrames'],
            'final must include references; finalVideoFrames is not the storyboard body total')
    at, subtitle_rows, chapters = 0, [], []
    previous_scene = None
    for scene in sb['scenes']:
        require(scene['from'] == at, 'scene start does not equal real shot boundary')
        same = previous_scene and ((scene.get('chapterId') and scene.get('chapterId') == previous_scene.get('chapterId'))
                                  or (scene.get('title') and scene.get('title') == previous_scene.get('title')))
        if not same:
            chapters.append({'id': scene.get('chapterId', scene['id']), 'start': at / fps})
        for shot in scene['shots']:
            require(shot['from'] == at, 'shot start does not equal cumulative boundary')
            duration, last = shot['durationInFrames'], -1
            for row in shot['subtitles']:
                a, b = row['from'], row['to']
                require(type(a) is int and type(b) is int and last < a <= b < duration,
                        'invalid storyboard subtitle range')
                subtitle_rows.append({'startFrame': at + a, 'endFrame': at + b + 1, 'text': row['text']})
                last = b
            for voice in shot.get('voice', []):
                require(voice['wavEnd'] <= card['from'], 'voice enters Python card')
            at += duration
        previous_scene = scene
    require(at == body, 'storyboard cumulative frames differ from body total')
    cues = parse_vtt(vtt)
    require(len(cues) == len(subtitle_rows) == 32, 'expected exactly 32 sentence cues')
    for number, (cue, row) in enumerate(zip(cues, subtitle_rows), 1):
        require(cue['text'] == row['text'], f'cue {number}: text differs from storyboard sentence')
        require(abs(cue['start'] - row['startFrame'] / fps) <= .001,
                f'cue {number}: start differs from frame boundary')
        # The site intentionally moves an end coinciding with the first card
        # frame to the previous millisecond so a paused native cue is inactive.
        require(abs(cue['end'] - row['endFrame'] / fps) <= .0011,
                f'cue {number}: end differs from frame boundary')
        require(cue['end'] < card['from'] / fps, f'cue {number}: enters Python card')
    return {'fps': fps, 'bodyFrames': body, 'finalFrames': final,
            'pythonCardFrom': card['from'], 'referenceFrom': appendix['from'],
            'sentenceCues': len(cues), 'lastCueEnd': cues[-1]['end'],
            'captionsEndStrictlyBeforePythonCard': True}, chapters


def expected_source_links(source, expected_commit):
    require(re.fullmatch(r'[a-f0-9]{40}', expected_commit) is not None,
            'expected source commit must be a complete lowercase 40-character SHA')
    publication = PUB.relative_to(ROOT).as_posix()
    return {
        'sourcePath': f'{GITHUB}/tree/{expected_commit}/{source}',
        'scriptPinnedLink': f'{GITHUB}/blob/{expected_commit}/{publication}/script.md',
        'storyboardPinnedLink': f'{GITHUB}/blob/{expected_commit}/{publication}/storyboard.json',
        'scriptRawPinnedLink': f'https://raw.githubusercontent.com/linhongcun/video-studio/{expected_commit}/{publication}/script.md',
        'storyboardRawPinnedLink': f'https://raw.githubusercontent.com/linhongcun/video-studio/{expected_commit}/{publication}/storyboard.json',
    }


def check_source_links(page, source, expected_commit):
    expected = expected_source_links(source, expected_commit)
    checks = {name: value in page.links for name, value in expected.items()}
    publication = PUB.relative_to(ROOT).as_posix()
    selected = set()
    for link in page.links:
        is_source = re.fullmatch(re.escape(GITHUB) + r'/tree/[^/]+/' + re.escape(source), link)
        is_blob = re.fullmatch(re.escape(GITHUB) + r'/blob/[^/]+/' + re.escape(publication) + r'/(?:script\.md|storyboard\.json)', link)
        is_raw = re.fullmatch(r'https://raw\.githubusercontent\.com/linhongcun/video-studio/[^/]+/' + re.escape(publication) + r'/(?:script\.md|storyboard\.json)', link)
        if is_source or is_blob or is_raw:
            selected.add(link)
    checks['allEpisodeSourceLinksUseExactExpectedCommit'] = selected == set(expected.values())
    return checks


def local_expected(version, expected_commit):
    meta = read_json(PUB / 'meta.json')
    require(meta['slug'] == SLUG and meta['ep'] == 58 and meta['problemNumber'] == 347,
            'LC347/EP58 identity mismatch')
    require(not meta.get('draft') and not meta.get('legacy'), 'publication is still draft/legacy')
    source = str((EP / 'remotion').relative_to(ROOT))
    require(meta.get('sourcePath') == source and (ROOT / source).is_dir(), 'incorrect sourcePath')
    built = DIST / 'episodes' / SLUG
    vtt = (built / 'captions.vtt').read_bytes()
    timing, chapter_rows = validate_timing(read_json(PUB / 'storyboard.json'), meta, vtt)
    page = old.Page((built / 'index.html').read_bytes())
    source_url = expected_source_links(source, expected_commit)['sourcePath']
    require(page.h1 == old.text(meta['title']), 'built episode H1 differs from title')
    require(all(check_source_links(page, source, expected_commit).values()),
            'built episode source/script/storyboard links differ from exact expected commit')
    require(page.contains_version(version), 'built episode footer has wrong release version')
    require(len(page.chapters) == len(chapter_rows), 'built chapter count differs from storyboard')
    for actual, expected in zip(page.chapters, chapter_rows):
        require(actual['id'] == expected['id'] and abs(actual['start'] - expected['start']) < 1e-6,
                'built chapter ID/start differs from storyboard')
    assets = []
    for kind, name in [('video', meta['video']), ('poster', meta['poster'])]:
        name = asset_name(name)
        source_path, built_path = PUB / name, built / name
        require(sha(source_path) == sha(built_path), f'{kind}: built/publication SHA mismatch')
        assets.append((kind, f'episodes/{SLUG}/{name}', source_path, None))
    images = sorted(p for p in (PUB / 'article').rglob('*') if p.is_file()
                    and p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.svg', '.gif', '.webp', '.avif'))
    require(images, 'no publication article images')
    for image in images:
        name = image.relative_to(PUB).as_posix()
        require(sha(image) == sha(built / name), f'{name}: built/publication SHA mismatch')
        assets.append(('article-image', f'episodes/{SLUG}/{name}', image, None))
    assets.append(('captions', f'episodes/{SLUG}/captions.vtt', built / 'captions.vtt', vtt))
    for kind, relative in [('episode-html', f'episodes/{SLUG}/'), ('home', ''), ('changelog', 'changelog/')]:
        path = DIST / relative / 'index.html'
        markup = old.Page(path.read_bytes())
        require(markup.contains_version(version), f'{kind}: built visible release version missing')
        if kind == 'changelog':
            require(f'{GITHUB}/releases/tag/{version}' in markup.links, 'built changelog lacks release link')
        assets.append((kind, relative, path, path.read_bytes()))
    return meta, page, source_url, timing, assets


def evaluate_asset(kind, path, exact, episode, source_url, version, expected_commit):
    expected = {'sha256': sha(path), 'byteLength': path.stat().st_size}
    blob = old.blob_evaluator(expected, exact)
    def evaluate(result, body):
        errors, checks = blob(result, body)
        if kind in ('episode-html', 'home', 'changelog'):
            page = old.Page(body)
            checks['visibleReleaseVersion'] = page.contains_version(version)
            if kind == 'episode-html':
                checks.update(title=page.title == episode.title, h1=page.h1 == episode.h1,
                              chapterIDsTitlesAndStarts=old.chapter_equal(page.chapters, episode.chapters))
                checks.update(check_source_links(page, (EP / 'remotion').relative_to(ROOT).as_posix(), expected_commit))
            elif kind == 'changelog':
                checks['releaseTagLink'] = f'{GITHUB}/releases/tag/{version}' in page.links
            errors = [name + ' mismatch' for name, passed in checks.items() if not passed]
        return errors, checks
    return expected, evaluate


def plan(version, expected_commit):
    meta = read_json(PUB / 'meta.json')
    paths = [f'episodes/{SLUG}/video.mp4', f"episodes/{SLUG}/{meta.get('poster', 'cover-16x9.jpg')}",
             f'episodes/{SLUG}/article/01.jpg', f'episodes/{SLUG}/captions.vtt',
             f'episodes/{SLUG}/', '', 'changelog/']
    return {'status': 'plan-only', 'networkExecuted': False, 'version': version,
            'site': SITE, 'urls': [SITE + quote(path, safe='/') for path in paths],
            'expectedBuildCommit': expected_commit,
            'expectedSourceLinks': expected_source_links((EP / 'remotion').relative_to(ROOT).as_posix(), expected_commit),
            'localPreflight': 'Requires final publication metadata, storyboard and final Release-aware site/dist build.',
            'expectedFrameRelationship': 'body 5654, references 150, final 5804; load actual metadata rather than equating body and final.',
            'reportOnExecution': str(EP / 'qa/online-verification.json')}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--execute', action='store_true', help='Run local preflight, then canonical full GET verification')
    mode.add_argument('--check-local', action='store_true', help='Final local preflight only; no network')
    ap.add_argument('--version', default='v0.106.0', help='Final released version tag')
    ap.add_argument('--expected-commit', help='Exact complete build/deployment commit SHA; default is git origin/main at invocation')
    ap.add_argument('--timeout', type=float, default=30, help='Per-request total deadline, 0 < seconds <=30')
    ap.add_argument('--attempts', type=int, choices=(1, 2, 3), default=2)
    ap.add_argument('--out', type=Path, default=EP / 'qa/online-verification.json')
    args = ap.parse_args()
    expected_commit = args.expected_commit or subprocess.check_output(
        ['git', 'rev-parse', '--verify', 'origin/main'], cwd=ROOT, text=True).strip()
    if re.fullmatch(r'[a-f0-9]{40}', expected_commit) is None:
        ap.error('--expected-commit must be a complete lowercase 40-character commit SHA')
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        ap.error('--version must be a vX.Y.Z tag')
    if not 0 < args.timeout <= 30:
        ap.error('--timeout must be greater than zero and at most 30 seconds')
    if not (args.execute or args.check_local):
        print(json.dumps(plan(args.version, expected_commit), ensure_ascii=False, indent=2))
        return 0
    report = {'episode': SLUG, 'ep': 58, 'version': args.version, 'site': SITE,
              'startedAtUTC': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'networkExecuted': False, 'scope': 'canonical-full-GET-bytes-and-HTML-semantics' if args.execute else 'local-only',
              'browserPlaybackReview': False, 'semanticListeningReview': False,
              'remoteMediaWrittenToDisk': False, 'checks': [],
              'scriptSHA256': sha(Path(__file__)), 'helperSHA256': sha(HELPER),
              'frozenVerifierSHA256': sha(FROZEN_VERIFIER),
              'expectedBuildCommit': expected_commit,
              'expectedCommitSource': 'explicit --expected-commit' if args.expected_commit else 'git rev-parse --verify origin/main'}
    try:
        meta, page, source_url, timing, assets = local_expected(args.version, expected_commit)
        report.update(localPreflightPassed=True, timing=timing, sourceURL=source_url,
                      expectedChapters=page.chapters,
                      expectedSourceLinks=expected_source_links((EP / 'remotion').relative_to(ROOT).as_posix(), expected_commit))
        for kind, relative, path, exact in assets:
            expected, evaluator = evaluate_asset(kind, path, exact, page, source_url, args.version, expected_commit)
            row = {'kind': kind, 'url': SITE + quote(relative, safe='/'),
                   'expectedLocalFile': str(path.relative_to(ROOT)), 'expected': expected}
            if args.execute:
                report['networkExecuted'] = True
                row.update(old.fetch_verify(row['url'], evaluator, args.timeout, args.attempts,
                                             len(exact) + 1 if exact is not None else 0))
            report['checks'].append(row)
            old.save_report(args.out, report)
        report['status'] = ('passed' if all(row['passed'] for row in report['checks']) else 'failed') if args.execute else 'local-preflight-passed'
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    report['finishedAtUTC'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    old.save_report(args.out, report)
    print(json.dumps({'status': report['status'], 'networkExecuted': report['networkExecuted'],
                      'report': str(args.out), 'error': report.get('error')}, ensure_ascii=False))
    return 0 if report['status'] in ('passed', 'local-preflight-passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
