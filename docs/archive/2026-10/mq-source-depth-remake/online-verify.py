#!/usr/bin/env python3
"""Complete canonical GET/SHA checks after the Release-following deployment."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import urllib.request

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'
SLUGS = ['message-queue', 'kafka-consumer-groups', 'kafka-log-replay', 'kafka-send-confirmation']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    report = {'status': 'in-progress', 'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              'release': args.release, 'retryCount': 0, 'rangeRequests': False,
              'cacheBusting': False, 'transport': 'Canonical urllib GET with inherited proxy and verified TLS',
              'requests': [], 'episodes': [], 'browserChecks': 'Separate native Chromium reports'}

    def save():
        (HERE / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def fetch(path, local=None):
        url = path if path.startswith('https://') else BASE + path
        row = {'url': url}
        report['requests'].append(row)
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                assert response.status == 200
                digest = hashlib.sha256()
                blocks = []
                size = 0
                while True:
                    block = response.read(262144)
                    if not block:
                        break
                    digest.update(block)
                    size += len(block)
                    if local is None:
                        blocks.append(block)
                row.update(status=response.status, finalURL=response.url, bytes=size, sha256=digest.hexdigest())
            if local is not None:
                row['expectedSHA256'] = sha(local)
                assert row['sha256'] == row['expectedSHA256'], (url, row)
            row['passed'] = True
            save()
            print('verified', url, flush=True)
            return b''.join(blocks).decode() if local is None else row
        except Exception as exc:
            row.update(passed=False, error=repr(exc))
            save()
            raise

    try:
        before = read(HERE / 'publication-before.json')
        for slug in SLUGS:
            d = ROOT / 'episodes-codex' / slug / 'revisions/source-depth-v2'
            p = ROOT / 'episodes' / slug
            m = read(p / 'meta.json')
            assert m['sourcePath'] == str((d / 'remotion').relative_to(ROOT))
            for key in ['ep', 'title', 'createdAt', 'publishedAt', 'firstRelease', 'platforms']:
                assert m.get(key) == before[slug].get(key), (slug, key)
            page = fetch(f'episodes/{slug}/')
            for token in [m['title'], m['sourcePath'], 'video.mp4', 'captions.vtt']:
                assert token in page, (slug, 'missing page token', token)
            board = read(d / 'storyboard.json')
            chapters = list(dict.fromkeys(s['chapterId'] for s in board['scenes']))
            for chapter in chapters:
                assert f'id="{chapter}"' in page
            fetch(f'episodes/{slug}/video.mp4', p / 'video.mp4')
            fetch(f'episodes/{slug}/' + m['poster'], p / m['poster'])
            vtt = ROOT / 'site/dist/episodes' / slug / 'captions.vtt'
            fetch(f'episodes/{slug}/captions.vtt', vtt)
            cues = vtt.read_text().count(' --> ')
            assert cues == sum(len(s['sentences']) for s in read(d / 'words.json')['shots'])
            figures = read(d / 'article-figure-plan.json')['figures']
            for fig in figures:
                fetch(f'episodes/{slug}/' + fig['file'], p / fig['file'])
            report['episodes'].append({'slug': slug, 'videoSHA256': sha(p / 'video.mp4'),
                                       'frames': m['finalVideoFrames'], 'chapters': len(chapters),
                                       'captionCues': cues, 'figures': len(figures),
                                       'identityPreserved': True})
        series = fetch('series/message-queue/')
        for slug in SLUGS:
            assert f'/video-studio/episodes/{slug}/' in series
        for path in ['library/', '', 'learn/']:
            fetch(path)
        changelog = fetch('changelog/')
        assert args.release in changelog
        release = json.loads(fetch('https://api.github.com/repos/linhongcun/video-studio/releases/tags/' + args.release))
        assert release['tag_name'] == args.release and release['draft'] is False
        for slug in SLUGS:
            assert slug in release['body']
        report.update(status='passed', actualReleaseURL=release['html_url'])
        save()
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
        save()
        raise
    print(json.dumps({'status': report['status'], 'completeGETs': len(report['requests']), 'episodes': 4}))


if __name__ == '__main__':
    main()
