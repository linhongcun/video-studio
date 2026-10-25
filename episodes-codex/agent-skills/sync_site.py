#!/usr/bin/env python3
"""Validate frozen Skills artifacts, then explicitly copy their public subset.

Importing this module never writes files. Only --publish with the parent's
locked release/date creates a live delivery; preview timing is rejected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SLUG = 'agent-skills'
SITE = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
CHAPTER_IDS = ['problem', 'loading', 'resources', 'boundaries']
RETIRED_SLUGS = ['agent-intro', 'agent-tool-execution']
PUBLIC_FILES = ('article.mdx', 'script.md', 'pronunciation.md', 'research.md',
                'words.json', 'storyboard.json', 'captions.srt', 'video.mp4',
                'render-result.json', 'mix-report.json', 'source-sha256.json',
                'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'covers.json')


def read_json(path):
    return json.loads(Path(path).read_text())


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_facts():
    """Read actual final timings and check every frozen source before delivery."""
    config = read_json(PRODUCTION / 'episode-config.json')
    plan = read_json(PRODUCTION / 'plan.json')
    sb = read_json(PRODUCTION / 'storyboard.json')
    render = read_json(PRODUCTION / 'render-result.json')
    assert config['slug'] == sb['meta']['slug'] == SLUG
    assert config['episode'] == sb['meta']['episode'] == 31
    assert config['title'] == sb['meta']['title']
    assert sb['meta']['fps'] == 30
    assert not sb['meta'].get('provisionalTiming') and not sb['meta'].get('pendingAudio')
    frozen = read_json(PRODUCTION / 'source-sha256.json')
    assert frozen and 'storyboard.json' in frozen and 'article.mdx' in frozen
    for name, digest in frozen.items():
        assert sha_file(PRODUCTION / name) == digest, ('Frozen source changed', name)
    fps, frame = sb['meta']['fps'], 0
    shots, chapters, subtitles = [], [], []
    for scene in sb['scenes']:
        chapter_id = scene['chapterId']
        if not chapters or chapters[-1]['id'] != chapter_id:
            title = next(row['chapterTitle'] for row in plan if row['chapterId'] == chapter_id)
            chapters.append({'id': chapter_id, 'title': title, 'frame': frame, 'start': frame / fps})
        for shot in scene['shots']:
            assert shot['chapterId'] == chapter_id
            duration = shot['durationInFrames']
            shots.append({'id': shot['id'], 'chapterId': chapter_id, 'from': frame, 'durationInFrames': duration})
            last_end = -1
            for sub in shot['subtitles']:
                assert isinstance(sub['from'], int) and isinstance(sub['to'], int)
                assert last_end < sub['from'] <= sub['to'] < duration
                subtitles.append({'text': sub['text'], 'from': frame + sub['from'], 'to': frame + sub['to'] + 1})
                last_end = sub['to']
            frame += duration
    assert len(shots) == config['shotCount'] == len(plan)
    assert [(s['id'], s['chapterId']) for s in shots] == [(s['id'], s['chapterId']) for s in plan]
    assert frame == sb['meta']['durationInFrames']
    frames = sb['meta']['finalVideoFrames']
    assert frames >= frame and render['frames'] == frames
    assert Fraction(str(render['fps'])) == fps and (render['width'], render['height']) == (1920, 1080)
    assert (PRODUCTION / 'video.mp4').stat().st_size == render['bytes']
    assert sha_file(PRODUCTION / 'video.mp4') == render['sha256']
    assert [s['text'] for s in subtitles] == [s['text'] for s in read_json(PRODUCTION / 'voice/sents.json')]
    article = (PRODUCTION / 'article.mdx').read_text()
    fm = yaml.safe_load(article.split('---', 2)[1])
    assert [c['id'] for c in chapters] == CHAPTER_IDS
    assert fm['chapters'] == [{key: c[key] for key in ('id', 'title')} for c in chapters]
    for chapter in chapters:
        assert article.count('{#' + chapter['id'] + '}') == 1
    assert fm['title'] == config['title']
    for slug in RETIRED_SLUGS:
        assert not (ROOT / 'episodes' / slug).exists(), ('Retired episode restored', slug)
    return {'config': config, 'storyboard': sb, 'render': render, 'frontmatter': fm,
            'frames': frames, 'fps': fps, 'shots': shots, 'chapters': chapters,
            'subtitles': subtitles, 'frozenInputCount': len(frozen)}


def expected_vtt(facts):
    def stamp(frame):
        seconds = frame / facts['fps']
        return f'{int(seconds // 3600):02d}:{int(seconds % 3600 // 60):02d}:{seconds % 60:06.3f}'
    cues = [f"{stamp(s['from'])} --> {stamp(s['to'])}\n{s['text']}" for s in facts['subtitles']]
    return ('WEBVTT\n\n' + '\n\n'.join(cues) + '\n').encode()


def agent_slugs():
    metas = [read_json(p) for p in (ROOT / 'episodes').glob('*/meta.json')]
    return [m['slug'] for m in sorted(metas, key=lambda m: (m.get('lessonOrder', 0), m.get('ep', 0), m['slug']))
            if m.get('series') == 'agent' and not m.get('draft') and not m.get('archived')]


def check_local_delivery(facts):
    meta = read_json(SITE / 'meta.json')
    assert meta['slug'] == SLUG and meta['ep'] == 31 and meta['series'] == 'agent'
    assert meta['sourcePath'] == 'episodes-codex/agent-skills/remotion'
    assert meta['title'] == facts['config']['title'] and meta['draft'] is False
    assert meta['lessonOrder'] == 0 and meta['finalVideoFrames'] == facts['frames']
    manifest = read_json(SITE / 'delivery-copy.json')
    assert set(manifest['filesSHA256']) == set(PUBLIC_FILES)
    assert manifest['release'] == meta['firstRelease']
    for name in PUBLIC_FILES:
        assert sha_file(PRODUCTION / name) == sha_file(SITE / name) == manifest['filesSHA256'][name], name
    for name in (meta['video'], meta['poster']):
        assert sha_file(SITE / name) == sha_file(DIST / 'episodes' / SLUG / name), ('Built copy changed', name)
    assert (DIST / 'episodes' / SLUG / 'captions.vtt').read_bytes() == expected_vtt(facts)
    assert not [p for p in SITE.rglob('*') if p.is_file() and p.suffix.lower() in {'.wav', '.png'}]
    return meta, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', required=True)
    parser.add_argument('--release', required=True, help='The release version locked by the parent, e.g. v0.62.0.')
    parser.add_argument('--date', required=True, help='Publication date in Asia/Shanghai, YYYY-MM-DD.')
    args = parser.parse_args()
    assert re.fullmatch(r'v\d+\.\d+\.\d+', args.release)
    datetime.strptime(args.date, '%Y-%m-%d')
    assert 'v' + read_json(ROOT / 'site/package.json')['version'] == args.release
    facts = load_facts()
    hashes = {name: sha_file(PRODUCTION / name) for name in PUBLIC_FILES}
    meta = {'slug': SLUG, 'ep': 31, 'episodePart': facts['config']['episodePart'],
            'title': facts['config']['title'], 'summary': facts['frontmatter']['summary'],
            'description': '以接口兼容审查为例，解释Agent Skills的可发现方法包、渐进加载、参考资料读取与脚本经工具执行两条路径，以及上下文和宿主支持的边界。',
            'tags': ['人工智能', 'Agent'], 'series': 'agent', 'lessonOrder': 0,
            'publishedAt': args.date, 'firstRelease': args.release, 'draft': False,
            'video': 'video.mp4', 'poster': 'cover-16x9.jpg', 'platforms': {}, 'related': [],
            'sourcePath': 'episodes-codex/agent-skills/remotion', 'finalVideoFrames': facts['frames']}
    SITE.mkdir(parents=True, exist_ok=True)
    for name, digest in hashes.items():
        shutil.copyfile(PRODUCTION / name, SITE / name)
        assert sha_file(SITE / name) == digest
    (SITE / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    manifest = {'source': str(PRODUCTION.relative_to(ROOT)), 'release': args.release,
                'copiedAtUTC': datetime.now(timezone.utc).isoformat(),
                'finalVideoFrames': facts['frames'], 'filesSHA256': hashes}
    (SITE / 'delivery-copy.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'copied', 'files': len(hashes), 'frames': facts['frames'],
                      'release': args.release, 'videoSHA256': hashes['video.mp4']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
