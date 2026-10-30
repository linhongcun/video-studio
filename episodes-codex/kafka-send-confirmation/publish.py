#!/usr/bin/env python3
"""Install this episode's reviewed production bytes into the site's input tree.

This does not render, approve quality, bump versions, commit, or publish remotely.
Call after final-media review to stage the local build; article/player review
must pass before remote publication.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import shutil

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
SLUG = 'kafka-send-confirmation'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def timestamp(value):
    date = datetime.fromisoformat(value)
    if date.tzinfo is None:
        raise argparse.ArgumentTypeError('An explicit timezone is required')
    return date.isoformat(timespec='seconds')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--created-at', required=True, type=timestamp)
    parser.add_argument('--published-at', required=True, type=timestamp)
    parser.add_argument('--release', required=True, help='Actual planned first Release tag, e.g. v0.96.0')
    args = parser.parse_args()
    config = read(D / 'episode-config.json')
    result = read(D / 'render-result.json')
    receipt = read(D / 'reference-appendix.json')
    media = read(D / 'reference-appendix-media-check.json')
    if config['slug'] != SLUG or config['ep'] != 44 or config['series'] != 'message-queue':
        raise ValueError('Unexpected episode identity; inspect current production metadata')
    video_sha = sha(D / 'video.mp4')
    if result['sha256'] != video_sha or receipt['outputSHA256'] != video_sha:
        raise ValueError('Final video differs from the actual render/appendix receipt')
    if media.get('passed') is not True or media.get('outputSHA256') != video_sha:
        raise ValueError('Final media verification is missing or stale')
    publication = result['publicationMetadata']
    if publication['finalVideoFrames'] != receipt['finalVideoFrames']:
        raise ValueError('Final frame count differs from the appendix receipt')
    manifest = read(D / 'source-sha256.json')
    for relative, expected in manifest.items():
        path = D / relative
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f'Frozen production input is missing or changed: {relative}')
    required = ['video.mp4', 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg',
                'article.mdx', 'script.md', 'storyboard.json', 'words.json',
                'captions.srt', 'research.md', 'pronunciation.md', 'references.json',
                'reference-appendix.json', 'reference-appendix-media-check.json',
                'render-result.json', 'cover-style.json']
    optional = ['article-sources.json', 'knoll-props.md']
    for name in required:
        if not (D / name).is_file():
            raise FileNotFoundError(D / name)
    images = [p for p in (D / 'article').rglob('*') if p.is_file()] if (D / 'article').exists() else []
    if not any(path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.svg', '.webp', '.avif', '.gif'} for path in images):
        raise ValueError('Generate and review the article figures before installation')
    dest = ROOT / 'episodes' / SLUG
    old_meta = read(dest / 'meta.json') if (dest / 'meta.json').exists() else None
    # Cover generation stages an exact identity-only record before final media exists.
    identity_fields = {'slug', 'ep', 'title', 'series', 'draft', 'episodePart', 'sourcePath'}
    if old_meta and set(old_meta) == identity_fields:
        if (old_meta['slug'], old_meta['ep'], old_meta['title'], old_meta['series'], old_meta['episodePart'], old_meta['sourcePath'], old_meta['draft']) != (SLUG, 44, config['title'], 'message-queue', config['episodePart'], 'episodes-codex/kafka-send-confirmation/remotion', False):
            raise ValueError('Unexpected temporary cover identity')
        old_meta = None
    if old_meta:
        if old_meta.get('slug') != SLUG or old_meta.get('ep') != 44:
            raise ValueError('Existing site metadata belongs to a different episode')
        if old_meta.get('createdAt') and old_meta['createdAt'] != args.created_at:
            raise ValueError('Do not reset the existing creation time')
        if not old_meta.get('draft', False) and old_meta.get('publishedAt') != args.published_at:
            raise ValueError('Do not reset an already published identity')
    meta = {
        'slug': SLUG, 'ep': 44, 'title': config['title'],
        'summary': '区分send调用返回、生产端成功结果与业务处理完成，再对照确认不可得时的未知结果和确定未发出的本地错误。',
        'tags': ['后端', 'Kafka', '消息队列', '发送确认'], 'series': 'message-queue',
        'episodePart': config['episodePart'],
        'createdAt': args.created_at, 'updatedAt': args.created_at,
        'publishedAt': args.published_at, 'firstRelease': args.release,
        'video': 'video.mp4', 'poster': 'cover-16x9.jpg', 'draft': False,
        'related': ['message-queue', 'kafka-log-replay'], 'platforms': {},
        'description': '沿同一业务事件区分生产者调用返回、日志实际追加和Future/回调观察到的结果；正常确认、结果未知与本地确定未发送分别说明，成功确认不等于消费者业务完成。',
        'sourcePath': 'episodes-codex/kafka-send-confirmation/remotion',
        'targetDuration': result['seconds'], 'burnedInCaptions': True,
        **publication,
    }
    if old_meta:
        for key in ('createdAt', 'publishedAt', 'firstRelease'):
            if old_meta.get(key):
                meta[key] = old_meta[key]
    dest.mkdir(parents=True, exist_ok=True)
    files = [D / name for name in required + optional if (D / name).is_file()] + images
    installed = {}
    for source in files:
        relative = source.relative_to(D)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if sha(source) != sha(target):
            raise ValueError(f'Copy differs: {relative}')
        installed[str(relative)] = sha(target)
    (dest / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    installed['meta.json'] = sha(dest / 'meta.json')
    record = {'installedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
              'scope': 'Local site-input installation only; no remote publishing or quality approval.',
              'production': str(D.relative_to(ROOT)), 'destination': str(dest.relative_to(ROOT)),
              'release': args.release, 'files': installed}
    (D / 'publication-files.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(f'Installed {len(installed)} verified files into {dest.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
