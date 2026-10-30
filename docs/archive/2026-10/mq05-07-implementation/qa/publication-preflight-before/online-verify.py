#!/usr/bin/env python3
"""Verify complete canonical assets and actual Release after its successful deployment."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release', required=True)
    ap.add_argument('--out', type=Path, default=HERE / 'online-verification.json')
    args = ap.parse_args()
    assert not args.out.exists(), 'Preserve any earlier attempt; choose a new explicit output path'
    info = read(HERE / 'episodes.json')
    report = {'status': 'in-progress', 'release': args.release,
              'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              'transport': 'Canonical urllib complete GET with inherited proxy and verified TLS',
              'retryCount': 0, 'rangeRequests': False, 'cacheBusting': False,
              'requests': [], 'episodes': [], 'browserChecks': 'Separate native Chromium reports'}

    def save():
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def fetch(path, local=None):
        url = path if path.startswith('https://') else BASE + path
        row = {'url': url}
        report['requests'].append(row)
        try:
            digest = hashlib.sha256()
            chunks = []
            size = 0
            with urllib.request.urlopen(url, timeout=60) as response:
                assert response.status == 200
                while True:
                    block = response.read(262144)
                    if not block:
                        break
                    digest.update(block)
                    size += len(block)
                    if local is None:
                        chunks.append(block)
                row.update(status=response.status, finalURL=response.url, bytes=size, sha256=digest.hexdigest())
            if local is not None:
                row['expectedSHA256'] = sha(local)
                assert row['sha256'] == row['expectedSHA256'], (url, row)
            row['passed'] = True
            save()
            print('verified', url, flush=True)
            return b''.join(chunks).decode() if local is None else row
        except Exception as exc:
            row.update(passed=False, error=repr(exc))
            save()
            raise

    try:
        metas = []
        for expected in info['episodes']:
            slug = expected['slug']
            d = ROOT / 'episodes-codex' / slug
            p = ROOT / 'episodes' / slug
            m = read(p / 'meta.json')
            assert m['draft'] is False and m['firstRelease'] == args.release
            assert m['createdAt'] == info['startedAtBeijing']
            assert m['ep'] == expected['ep'] and m['title'] == expected['title']
            assert m['sourcePath'] == f'episodes-codex/{slug}/remotion'
            assert m.get('platforms') == {}
            assert datetime.fromisoformat(m['publishedAt']) >= datetime.fromisoformat(m['createdAt'])
            page = fetch(f'episodes/{slug}/')
            for token in [m['title'], m['sourcePath'], 'video.mp4', 'captions.vtt']:
                assert token in page, (slug, token)
            board = read(d / 'storyboard.json')
            chapters = list(dict.fromkeys(sc['chapterId'] for sc in board['scenes']))
            for chapter in chapters:
                assert f'id="{chapter}"' in page
            fetch(f'episodes/{slug}/video.mp4', p / 'video.mp4')
            fetch(f'episodes/{slug}/' + m['poster'], p / m['poster'])
            vtt = ROOT / 'site/dist/episodes' / slug / 'captions.vtt'
            fetch(f'episodes/{slug}/captions.vtt', vtt)
            cues = vtt.read_text().count(' --> ')
            assert cues == len(read(d / 'voice/sents.json'))
            figures = read(d / 'article-figure-plan.json')['figures']
            for fig in figures:
                fetch(f'episodes/{slug}/' + fig['file'], p / fig['file'])
            report['episodes'].append({'slug': slug, 'ep': m['ep'], 'videoSHA256': sha(p / 'video.mp4'),
                                       'frames': m['finalVideoFrames'], 'captionCues': cues,
                                       'chapters': len(chapters), 'figures': len(figures),
                                       'createdAt': m['createdAt'], 'publishedAt': m['publishedAt']})
            metas.append(m)
        series = fetch('series/message-queue/')
        all_slugs = []
        for f in (ROOT / 'episodes').glob('*/meta.json'):
            m = read(f)
            if m.get('series') == 'message-queue' and not m.get('draft') and not m.get('archived'):
                all_slugs.append(m['slug'])
        for slug in all_slugs:
            assert f'/video-studio/episodes/{slug}/' in series
        report['publishedMQTopics'] = len(all_slugs)
        for path in ['library/', '', 'learn/']:
            fetch(path)
        assert args.release in fetch('changelog/')
        rss = ET.fromstring(fetch('rss.xml'))
        for m in metas:
            items = [i for i in rss.findall('./channel/item') if i.findtext('link', '').endswith('/episodes/' + m['slug'] + '/')]
            assert len(items) == 1
            assert parsedate_to_datetime(items[0].findtext('pubDate')).timestamp() == datetime.fromisoformat(m['publishedAt']).timestamp()
        release = json.loads(fetch('https://api.github.com/repos/linhongcun/video-studio/releases/tags/' + args.release))
        assert release['tag_name'] == args.release and release['draft'] is False
        for m in metas:
            assert m['slug'] in release['body']
        report.update(status='passed', actualReleaseURL=release['html_url'])
        save()
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
        save()
        raise
    print(json.dumps({'status': 'passed', 'completeGETs': len(report['requests']), 'newEpisodes': len(metas), 'publishedMQTopics': len(all_slugs)}))


if __name__ == '__main__':
    main()
