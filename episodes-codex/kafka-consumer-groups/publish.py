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
SLUG = 'kafka-consumer-groups'


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
    parser.add_argument('--release', required=True, help='Actual planned first Release tag, e.g. v0.93.0')
    args = parser.parse_args()
    config = read(D / 'episode-config.json')
    result = read(D / 'render-result.json')
    receipt = read(D / 'reference-appendix.json')
    media = read(D / 'reference-appendix-media-check.json')
    if config['slug'] != SLUG or config['ep'] != 42 or config['series'] != 'message-queue':
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
    if not images:
        raise ValueError('Generate and review the article figures before installation')
    dest = ROOT / 'episodes' / SLUG
    old_meta = read(dest / 'meta.json') if (dest / 'meta.json').exists() else None
    if old_meta and (old_meta.get('createdAt') != args.created_at or old_meta.get('publishedAt') != args.published_at):
        raise ValueError('Existing content dates differ; do not reset a published identity')
    meta = {
        'slug': SLUG, 'ep': 42, 'title': config['title'],
        'summary': '用同一批订单事件对照同组分工与跨组独立订阅，理解消费组、分区和组内实例的关系。',
        'tags': ['后端', 'Kafka', '消息队列', '消费组'], 'series': 'message-queue',
        'episodePart': config['episodePart'],
        'createdAt': args.created_at, 'updatedAt': args.created_at,
        'publishedAt': args.published_at, 'firstRelease': args.release,
        'video': 'video.mp4', 'poster': 'cover-16x9.jpg', 'draft': False,
        'related': ['message-queue'], 'platforms': {},
        'description': '通知与积分都需要完整订单事件：从误放同一消费组的各收一半，到两个独立组各收四条，再比较通知组两个实例按分区分工；固定传统消费组、稳定分配和相同保留输入。',
        'sourcePath': 'episodes-codex/kafka-consumer-groups/remotion',
        'targetDuration': result['seconds'], 'burnedInCaptions': True,
        **publication,
    }
    if old_meta:
        for key in ('createdAt', 'publishedAt', 'firstRelease'):
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
