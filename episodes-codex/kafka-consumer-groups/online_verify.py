#!/usr/bin/env python3
"""Ordinary canonical GET identity checks after the Release-following Pages deploy.

No Range, cache bypass, modified request headers, silent retry, or browser claims.
Remote media is hashed in full. Actual player/figure/citation UI review is separate.
"""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import urllib.request

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
SLUG = 'kafka-consumer-groups'
BASE = 'https://linhongcun.github.io/video-studio/'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    episode = ROOT / 'episodes' / SLUG
    meta = read(episode / 'meta.json')
    result = read(D / 'render-result.json')
    assert meta['firstRelease'] == args.release and meta['draft'] is False
    assert sha(episode / 'video.mp4') == result['sha256']
    rows = []
    report = {'status': 'in-progress', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
              'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              'release': args.release, 'page': BASE + 'episodes/' + SLUG + '/',
              'transport': 'ordinary canonical urllib GET using inherited proxy and CA trust',
              'retryCount': 0, 'rangeRequests': False, 'cacheBusting': False, 'requests': rows}
    def save():
        (D / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    def fetch(relative, local=None):
        url = relative if relative.startswith('https://') else BASE + relative
        row = {'url': url, 'checkedAtUTC': datetime.now(timezone.utc).isoformat()}
        rows.append(row)
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                row.update(status=response.status, finalURL=response.url)
                assert response.status == 200, (url, response.status)
                digest = hashlib.sha256()
                count = 0
                blocks = []
                while True:
                    block = response.read(256 * 1024)
                    if not block:
                        break
                    digest.update(block)
                    count += len(block)
                    if local is None:
                        blocks.append(block)
                row.update(bytes=count, sha256=digest.hexdigest())
            if local is not None:
                row.update(localFile=str(local.relative_to(ROOT)), expectedSHA256=sha(local))
                assert row['sha256'] == row['expectedSHA256'], row
            row['passed'] = True
            save()
            print('verified', url, flush=True)
            return b''.join(blocks).decode('utf-8') if local is None else row
        except Exception as exc:
            row.update(passed=False, error=repr(exc))
            save()
            raise
    try:
        page = fetch('episodes/' + SLUG + '/')
        for token in [meta['title'], 'Kafka MQ02', meta['sourcePath'], 'video.mp4', 'captions.vtt']:
            assert token in page, ('page missing', token)
        storyboard = read(D / 'storyboard.json')
        chapter_ids = list(dict.fromkeys(scene['chapterId'] for scene in storyboard['scenes']))
        for chapter in chapter_ids:
            assert ('id="' + chapter + '"') in page, ('chapter missing', chapter)
        fetch('episodes/' + SLUG + '/video.mp4', episode / 'video.mp4')
        fetch('episodes/' + SLUG + '/' + meta['poster'], episode / meta['poster'])
        caption_file = ROOT / 'site/dist/episodes' / SLUG / 'captions.vtt'
        fetch('episodes/' + SLUG + '/captions.vtt', caption_file)
        caption_text = caption_file.read_text()
        cue_count = caption_text.count(' --> ')
        assert cue_count == sum(len(shot['sentences']) for shot in read(D / 'words.json')['shots']), ('cue count', cue_count)
        for path in sorted((episode / 'article').rglob('*')):
            if path.is_file() and path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.svg', '.webp', '.avif'}:
                fetch('episodes/' + SLUG + '/' + str(path.relative_to(episode)), path)
        lesson = '/video-studio/episodes/' + SLUG + '/'
        for relative in ['series/message-queue/', 'library/', '']:
            html = fetch(relative)
            assert lesson in html, (relative, 'lesson link missing')
        learn = fetch('learn/')
        assert '/video-studio/library/' in learn, 'Legacy learn entry must lead to the content library'
        changelog = fetch('changelog/')
        release_url = 'https://github.com/linhongcun/video-studio/releases/tag/' + args.release
        assert release_url in changelog, ('actual Release link missing', args.release)
        release = json.loads(fetch('https://api.github.com/repos/linhongcun/video-studio/releases/tags/' + args.release))
        assert release['tag_name'] == args.release and release['html_url'] == release_url
        assert release['draft'] is False and release['prerelease'] is False and release['published_at']
        assert report['page'] in release['body'], 'Release does not link this actual episode'
        report.update(status='passed', requestCount=len(rows), chapterCount=len(chapter_ids),
                      captionCueCount=cue_count, frames=result['frames'], mediaSHA256=result['sha256'],
                      note='Canonical HTTP/content identity checks only; browser review is reported separately.')
        save()
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
        save()
        raise


if __name__ == '__main__':
    main()
