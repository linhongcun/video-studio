#!/usr/bin/env python3
"""Copy P05's body data and reference-bearing final delivery after approval.

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
from math import ceil
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[1]
SLUG = 'egg-drop'
SITE = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
FIRST_RELEASE = 'v0.67.0'
REVISION = 'binary-opening'
REVISION_DIR = PRODUCTION / 'revisions' / REVISION
QA_OUTPUT = PRODUCTION / 'out' / 'binary-opening-site'
PUBLIC_FILES = ('article.mdx', 'script.md', 'pronunciation.md', 'words.json',
                'storyboard.json', 'captions.srt', 'video.mp4', 'render-result.json',
                'mix-report.json', 'source-sha256.json', 'cover-16x9.jpg',
                'cover-4x3.jpg', 'cover-3x4.jpg', 'covers.json', 'references.json',
                'reference-appendix.json', 'reference-appendix-media-check.json')


def read_json(path):
    return json.loads(Path(path).read_text())


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(256 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def release_version(value):
    match = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', value)
    assert match, ('Expected an explicit three-part Release tag', value)
    return tuple(map(int, match.groups()))


def load_facts():
    """Derive every timing/text fact from the actual final production inputs."""
    config = read_json(PRODUCTION / 'episode-config.json')
    plan = read_json(PRODUCTION / 'plan.json')
    sb = read_json(PRODUCTION / 'storyboard.json')
    render = read_json(PRODUCTION / 'render-result.json')
    meta = read_json(SITE / 'meta.json')
    assert config['slug'] == meta['slug'] == SLUG
    assert config['episode'] == meta['ep'] == 33
    assert config['episodePart'] == meta['episodePart'] == '趣味推理 P05'
    assert config['title'] == meta['title']
    assert meta['series'] == 'puzzles'
    assert meta['firstRelease'] == FIRST_RELEASE, 'A revision must preserve the original debut'
    assert meta['sourcePath'] == 'episodes-codex/egg-drop/remotion'
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
    # The frozen storyboard and voice describe only the body. The approved
    # delivery additionally contains the independently generated reference card.
    assert frame == sb['meta']['durationInFrames'] == sb['meta']['finalVideoFrames']
    references = read_json(PRODUCTION / 'references.json')
    receipt = read_json(PRODUCTION / 'reference-appendix.json')
    media_check = read_json(PRODUCTION / 'reference-appendix-media-check.json')
    publication = render['publicationMetadata']
    appendix = publication['referenceAppendix']
    final_frames = publication['finalVideoFrames']
    assert references['schemaVersion'] == receipt['schemaVersion'] == 1
    assert references['episode'] == receipt['episode'] == SLUG
    assert frame == render['bodyFrames'] == receipt['bodyFrames'] == appendix['from']
    assert appendix == {'kind': 'references', 'from': frame,
                        'durationInFrames': receipt['appendix']['durationInFrames'],
                        'sources': 'references.json', 'manifest': 'reference-appendix.json'}
    assert appendix['durationInFrames'] > 0
    assert final_frames == render['frames'] == render['finalVideoFrames'] == receipt['finalVideoFrames']
    assert final_frames == frame + appendix['durationInFrames']
    assert render['referenceAppendix'] == appendix
    assert receipt['appendix']['kind'] == 'references' and receipt['appendix']['from'] == frame
    assert receipt['appendix']['sourceIds'] == [source['id'] for source in references['sources']]
    assert len(receipt['appendix']['pages']) * receipt['appendix']['framesPerPage'] == appendix['durationInFrames']
    assert receipt['inputs']['referencesSHA256'] == sha_file(PRODUCTION / 'references.json')
    assert receipt['outputSHA256'] == render['sha256'] == media_check['outputSHA256']
    assert media_check['passed'] is True
    assert media_check['bodySHA256'] == receipt['inputs']['bodySHA256']
    assert media_check['bodyFrames'] == frame and media_check['finalFrames'] == final_frames
    assert media_check['appendedFrames'] == appendix['durationInFrames']
    for key in ('bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual'):
        assert media_check[key] is True, key
    completed_at = datetime.fromisoformat(receipt['createdAtUTC'].replace('Z', '+00:00'))
    assert completed_at.tzinfo is not None
    completed_at_ms = completed_at.isoformat(timespec='milliseconds')
    assert Fraction(str(render['fps'])) == fps and render['width'] == 1920 and render['height'] == 1080
    assert Fraction(str(receipt['fps'])) == fps
    assert (PRODUCTION / 'video.mp4').stat().st_size == render['bytes']
    assert sha_file(PRODUCTION / 'video.mp4') == render['sha256']
    voice = read_json(PRODUCTION / 'voice/sents.json')
    assert [s['text'] for s in subtitles] == [s['text'] for s in voice]
    assert not any(term in ''.join(s['text'] for s in subtitles) for term in ('文章', '图文', '附录'))
    article = (PRODUCTION / 'article.mdx').read_text()
    frontmatter = article.split('---', 2)[1]
    headings = re.findall(r'\{ id: ([^,]+), title: ([^}]+) \}', frontmatter)
    assert headings == [(c['id'], c['title']) for c in chapters]
    for article_only in ('why-fourteen', 'bounds'):
        assert article_only not in [c['id'] for c in chapters]
        assert article.count('{#' + article_only + '}') == 1
    assert subtitles[-1]['to'] <= frame, 'Narrative captions must end before the reference appendix'
    return {'meta': meta, 'config': config, 'storyboard': sb, 'render': render,
            'frames': final_frames, 'body_frames': frame, 'fps': fps,
            'shots': shots, 'chapters': chapters, 'subtitles': subtitles,
            'appendix': appendix, 'references': references, 'reference_receipt': receipt,
            'reference_media_check': media_check,
            'appendix_completed_at': receipt['createdAtUTC'],
            'appendix_completed_at_ms': completed_at_ms}


def expected_vtt(facts):
    def stamp(frame, cue_end=False):
        seconds = frame / facts['fps']
        if cue_end and frame == facts['appendix']['from']:
            seconds = (ceil(seconds * 1000) - 1) / 1000
        return f'{int(seconds // 3600):02d}:{int(seconds % 3600 // 60):02d}:{seconds % 60:06.3f}'
    cues = [f"{stamp(s['from'])} --> {stamp(s['to'], True)}\n{s['text']}" for s in facts['subtitles']]
    return ('WEBVTT\n\n' + '\n\n'.join(cues) + '\n').encode()


def puzzle_slugs():
    metas = [read_json(p) for p in (ROOT / 'episodes').glob('*/meta.json')]
    return [m['slug'] for m in sorted(metas, key=lambda m: (m.get('ep', 0), m.get('lessonOrder', 0), m['slug']))
            if m.get('series') == 'puzzles' and not m.get('draft') and not m.get('archived')]


def check_local_delivery(facts, expected_release=None):
    meta = facts['meta']
    assert meta['draft'] is False and meta['finalVideoFrames'] == facts['frames']
    assert meta['referenceAppendix'] == facts['appendix']
    assert meta['updatedAt'] == facts['appendix_completed_at_ms']
    manifest = read_json(SITE / 'delivery-copy.json')
    assert set(manifest['filesSHA256']) == set(PUBLIC_FILES)
    assert manifest['firstRelease'] == meta['firstRelease'] == FIRST_RELEASE
    assert manifest['revision'] == REVISION
    assert manifest['bodyVideoFrames'] == facts['body_frames']
    assert manifest['referenceAppendix'] == facts['appendix']
    assert release_version(manifest['release']) > release_version(FIRST_RELEASE)
    if expected_release is not None:
        assert manifest['release'] == expected_release, 'Check the current delivery, not the debut manifest'
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
    parser.add_argument('--release', required=True,
                        help='Actual current delivery tag, selected after checking concurrent releases; debut stays v0.67.0.')
    args = parser.parse_args()
    assert release_version(args.release) > release_version(FIRST_RELEASE)
    facts = load_facts()
    assert len(PUBLIC_FILES) == 17
    for name in PUBLIC_FILES:
        assert (PRODUCTION / name).is_file(), ('Missing final artifact', name)
    # Prepare all checks before mutating the candidate delivery.
    hashes = {name: sha_file(PRODUCTION / name) for name in PUBLIC_FILES}
    for name in PUBLIC_FILES:
        shutil.copyfile(PRODUCTION / name, SITE / name)
        assert sha_file(SITE / name) == hashes[name]
    meta = facts['meta']
    assert meta['createdAt'] == meta['publishedAt'] == '2026-10-25'
    meta.update(draft=False, finalVideoFrames=facts['frames'],
                referenceAppendix=facts['appendix'], updatedAt=facts['appendix_completed_at_ms'])
    (SITE / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    manifest = {'source': str(PRODUCTION.relative_to(ROOT)), 'release': args.release,
                'firstRelease': FIRST_RELEASE, 'revision': REVISION,
                'copiedAtUTC': datetime.now(timezone.utc).isoformat(),
                'bodyVideoFrames': facts['body_frames'], 'finalVideoFrames': facts['frames'],
                'referenceAppendix': facts['appendix'],
                'appendixCompletedAtRaw': facts['appendix_completed_at'], 'filesSHA256': hashes}
    (SITE / 'delivery-copy.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'copied', 'release': args.release, 'firstRelease': FIRST_RELEASE,
                      'files': len(hashes), 'frames': facts['frames'],
                      'videoSha256': hashes['video.mp4']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
