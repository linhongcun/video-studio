#!/usr/bin/env python3
"""Copy only P02's fourteen public artifacts after the final render is approved.

Importing this module only exposes fact/byte checks; it never copies files.
The explicit --publish action also changes this episode's metadata to live.
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

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SLUG = 'bridge-torch'
SITE = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
PUBLIC_FILES = ('article.mdx', 'script.md', 'pronunciation.md', 'words.json',
                'storyboard.json', 'captions.srt', 'video.mp4', 'render-result.json',
                'mix-report.json', 'source-sha256.json', 'cover-16x9.jpg',
                'cover-4x3.jpg', 'cover-3x4.jpg', 'covers.json')


def read_json(path):
    return json.loads(Path(path).read_text())


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_facts():
    """Derive every timing/text fact from the actual final production inputs."""
    config = read_json(PRODUCTION / 'episode-config.json')
    plan = read_json(PRODUCTION / 'plan.json')
    sb = read_json(PRODUCTION / 'storyboard.json')
    render = read_json(PRODUCTION / 'render-result.json')
    meta = read_json(SITE / 'meta.json')
    assert config['slug'] == meta['slug'] == SLUG
    assert config['episode'] == meta['ep'] == 29
    assert config['episodePart'] == meta['episodePart'] == '趣味推理 P02'
    assert config['title'] == meta['title']
    assert meta['series'] == 'puzzles'
    assert meta['sourcePath'] == 'episodes-codex/bridge-torch/remotion'
    fps = sb['meta']['fps']
    assert fps == 30 and not sb['meta'].get('pendingAudio') and not sb['meta'].get('provisionalTiming')
    shots, chapters, subtitles = [], [], []
    frame = 0
    for scene in sb['scenes']:
        chapter_id = scene['chapterId']
        if not chapters or chapters[-1]['id'] != chapter_id:
            title = next(s['chapterTitle'] for s in plan if s['chapterId'] == chapter_id)
            chapters.append({'id': chapter_id, 'title': title, 'frame': frame, 'start': frame / fps})
        for shot in scene['shots']:
            assert shot['chapterId'] == chapter_id
            shots.append({'id': shot['id'], 'chapterId': chapter_id, 'from': frame,
                          'durationInFrames': shot['durationInFrames']})
            last_end = -1
            for sub in shot['subtitles']:
                assert isinstance(sub['from'], int) and isinstance(sub['to'], int)
                assert last_end < sub['from'] <= sub['to'] < shot['durationInFrames']
                subtitles.append({'text': sub['text'], 'from': frame + sub['from'], 'to': frame + sub['to'] + 1})
                last_end = sub['to']
            frame += shot['durationInFrames']
    assert len(shots) == config['shotCount'] == len(plan)
    assert [(s['id'], s['chapterId']) for s in shots] == [(s['id'], s['chapterId']) for s in plan]
    assert frame == sb['meta']['durationInFrames'] == sb['meta']['finalVideoFrames'] == render['frames']
    assert Fraction(str(render['fps'])) == fps and render['width'] == 1920 and render['height'] == 1080
    assert (PRODUCTION / 'video.mp4').stat().st_size == render['bytes']
    assert sha_file(PRODUCTION / 'video.mp4') == render['sha256']
    voice = read_json(PRODUCTION / 'voice/sents.json')
    assert [s['text'] for s in subtitles] == [s['text'] for s in voice]
    assert not any(term in ''.join(s['text'] for s in subtitles) for term in ('证明', '文章', '图文'))
    article = (PRODUCTION / 'article.mdx').read_text()
    frontmatter = article.split('---', 2)[1]
    headings = re.findall(r'\{ id: ([^,]+), title: ([^}]+) \}', frontmatter)
    assert headings == [(c['id'], c['title']) for c in chapters]
    assert 'optimality' not in [c['id'] for c in chapters]
    assert article.count('{#optimality}') == 1
    return {'meta': meta, 'config': config, 'storyboard': sb, 'render': render,
            'frames': frame, 'fps': fps, 'shots': shots, 'chapters': chapters, 'subtitles': subtitles}


def expected_vtt(facts):
    def stamp(frame):
        seconds = frame / facts['fps']
        return f'{int(seconds // 3600):02d}:{int(seconds % 3600 // 60):02d}:{seconds % 60:06.3f}'
    cues = [f"{stamp(s['from'])} --> {stamp(s['to'])}\n{s['text']}" for s in facts['subtitles']]
    return ('WEBVTT\n\n' + '\n\n'.join(cues) + '\n').encode()


def puzzle_slugs():
    metas = [read_json(p) for p in (ROOT / 'episodes').glob('*/meta.json')]
    return [m['slug'] for m in sorted(metas, key=lambda m: (m.get('ep', 0), m.get('lessonOrder', 0), m['slug']))
            if m.get('series') == 'puzzles' and not m.get('draft') and not m.get('archived')]


def check_local_delivery(facts):
    meta = facts['meta']
    assert meta['draft'] is False and meta['finalVideoFrames'] == facts['frames']
    manifest = read_json(SITE / 'delivery-copy.json')
    assert set(manifest['filesSHA256']) == set(PUBLIC_FILES)
    assert manifest['release'] == meta['firstRelease']
    for name in PUBLIC_FILES:
        assert sha_file(PRODUCTION / name) == sha_file(SITE / name) == manifest['filesSHA256'][name], name
    # Astro deliberately serves only the selected video and poster; the other
    # public repository artifacts remain accessible through their source links.
    for name in (meta['video'], meta['poster']):
        assert sha_file(SITE / name) == sha_file(DIST / 'episodes' / SLUG / name), ('built copy', name)
    assert (DIST / 'episodes' / SLUG / 'captions.vtt').read_bytes() == expected_vtt(facts)
    forbidden = [p.name for p in SITE.rglob('*') if p.is_file() and (p.suffix.lower() in {'.wav', '.png'} or 'remotion' in p.parts)]
    assert not forbidden, ('Unexpected production source in publication', forbidden)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', required=True,
                        help='Use only after the parent has approved the complete formal render.')
    args = parser.parse_args()
    facts = load_facts()
    assert len(PUBLIC_FILES) == 14
    for name in PUBLIC_FILES:
        assert (PRODUCTION / name).is_file(), ('Missing final artifact', name)
    # Prepare all checks before mutating the candidate delivery.
    hashes = {name: sha_file(PRODUCTION / name) for name in PUBLIC_FILES}
    for name in PUBLIC_FILES:
        shutil.copyfile(PRODUCTION / name, SITE / name)
        assert sha_file(SITE / name) == hashes[name]
    meta = facts['meta']
    meta.update(draft=False, finalVideoFrames=facts['frames'])
    (SITE / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    manifest = {'source': str(PRODUCTION.relative_to(ROOT)), 'release': meta['firstRelease'],
                'copiedAtUTC': datetime.now(timezone.utc).isoformat(),
                'finalVideoFrames': facts['frames'], 'filesSHA256': hashes}
    (SITE / 'delivery-copy.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'copied', 'files': len(hashes), 'frames': facts['frames'],
                      'videoSha256': hashes['video.mp4']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
