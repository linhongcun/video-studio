#!/usr/bin/env python3
"""Validate frozen EA01 inputs and prepare only the approved site copy.

Validation is read-only by default. Run --publish only after final media review:
  python3 episodes-codex/consistent-hashing/sync_site.py --publish
No narration WAV, production PNG, Remotion source, or dependency is published.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import wave
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
ROOT = D.parents[1]
DESTINATION = ROOT / 'episodes' / 'consistent-hashing'
RELEASE = 'v0.70.0'
BODY_FRAMES = 5881
APPENDIX_FRAMES = 150
FILES = (
    'article.mdx', 'script.md', 'research.md', 'storyboard.json', 'video.mp4',
    'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg',
)


def read_json(file):
    return json.loads(file.read_text())


def sha(file):
    digest = hashlib.sha256()
    with file.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def validate(appendix_artifacts, body_render_result):
    manifest = read_json(D / 'source-sha256.json')
    failures = [relative for relative, expected in manifest.items()
                if not (D / relative).is_file() or sha(D / relative) != expected]
    assert not failures, ('Frozen production input changed', failures)
    sb = read_json(D / 'storyboard.json')
    words = read_json(D / 'words.json')
    build = read_json(D / 'voice/build.json')
    render = read_json(D / 'render-result.json')
    body_render = read_json(body_render_result)
    references = read_json(D / 'references.json')
    receipt_path = appendix_artifacts / 'reference-appendix.json'
    media_check_path = appendix_artifacts / 'reference-appendix-media-check.json'
    receipt = read_json(receipt_path)
    appendix_check = read_json(media_check_path)
    final_frames = receipt['finalVideoFrames']
    assert receipt['episode'] == references['episode'] == 'consistent-hashing'
    assert receipt['bodyFrames'] == body_render['frames'] == BODY_FRAMES
    assert receipt['appendix']['kind'] == 'references'
    assert receipt['appendix']['from'] == BODY_FRAMES
    assert receipt['appendix']['durationInFrames'] == APPENDIX_FRAMES
    assert receipt['appendix']['framesPerPage'] == APPENDIX_FRAMES
    assert len(receipt['appendix']['pages']) == 1
    assert final_frames == BODY_FRAMES + APPENDIX_FRAMES
    assert sha(D / 'references.json') == receipt['inputs']['referencesSHA256']
    assert len(references['sources']) == 2
    assert receipt['inputs']['bodySHA256'] == body_render['sha256'] == appendix_check['bodySHA256']
    body_path = Path(receipt['body'])
    assert sha(body_path) == body_render['sha256'], 'Retained encoded body changed'
    for page in receipt['appendix']['pages']:
        assert sha(appendix_artifacts / page['file']) == page['sha256']
    assert appendix_check['passed'] is True
    assert appendix_check['bodyFrames'] == BODY_FRAMES
    assert appendix_check['appendedFrames'] == APPENDIX_FRAMES
    assert appendix_check['finalFrames'] == final_frames
    for key in ['bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual']:
        assert appendix_check[key] is True, key
    original_meta = read_json(DESTINATION / 'meta.json')
    assert original_meta['slug'] == 'consistent-hashing'
    assert original_meta['ep'] == 38
    assert original_meta['series'] == 'engineering-algorithms'
    assert original_meta['sourcePath'] == 'episodes-codex/consistent-hashing/remotion'
    assert original_meta['createdAt'] and original_meta['updatedAt']
    assert sb['meta']['episode'] == 38 and sb['meta']['slug'] == original_meta['slug']
    assert sb['meta']['title'] == original_meta['title']
    assert sb['meta']['fps'] == 30
    assert sb['meta']['durationInFrames'] == sb['meta']['finalVideoFrames'] == BODY_FRAMES
    assert words['durationFrames'] == build['summary']['frames'] == BODY_FRAMES
    assert words['fps'] == 30
    assert sha(D / 'script.md') == words['scriptSha256']
    audio_sha = sha(D / 'voice.wav')
    assert audio_sha == words['audioSha256'] == build['summary']['sha']
    with wave.open(str(D / 'voice.wav'), 'rb') as audio:
        audio_info = {'channels': audio.getnchannels(), 'sampleRate': audio.getframerate(),
                      'samples': audio.getnframes()}
        assert audio.getframerate() == 48000
        assert audio.getnframes() == build['summary']['samples'] == BODY_FRAMES * 1600
    shots = [shot for scene in sb['scenes'] for shot in scene['shots']]
    captions = [subtitle for shot in shots for subtitle in shot['subtitles']]
    assert len(shots) == 14 and len(captions) == 28
    assert len(sb['scenes']) == 4
    assert [scene['chapterId'] for scene in sb['scenes']] == ['remap', 'ring', 'insert', 'vnodes']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json',
        str(D / 'video.mp4')], text=True))
    video = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    encoded_audio = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
    assert int(video['nb_frames']) == render['frames'] == final_frames
    assert (video['width'], video['height']) == (render['width'], render['height']) == (1920, 1080)
    assert video['r_frame_rate'] == render['fps'] == '30/1'
    assert encoded_audio['codec_name'] == render['audio'] == 'aac'
    assert int(encoded_audio['sample_rate']) == render['audioSampleRate'] == 48000
    assert abs(float(probe['format']['duration']) - final_frames / 30) < .1
    media_sha = sha(D / 'video.mp4')
    assert media_sha == render['sha256'] == receipt['outputSHA256'] == appendix_check['outputSHA256']
    assert (D / 'video.mp4').stat().st_size == render['bytes']
    file_sources = {name: D / name for name in FILES}
    file_sources.update({'references.json': D / 'references.json',
                         'reference-appendix.json': receipt_path,
                         'reference-appendix-media-check.json': media_check_path})
    files = {name: {'sha256': sha(source), 'bytes': source.stat().st_size,
                    'source': str(source.relative_to(D))} for name, source in file_sources.items()}
    return original_meta, {
        'frozenManifestSHA256': sha(D / 'source-sha256.json'),
        'frozenInputCount': len(manifest), 'scriptSHA256': words['scriptSha256'],
        'audioSHA256': audio_sha, 'audio': audio_info,
        'renderResultSHA256': sha(D / 'render-result.json'), 'videoSHA256': media_sha,
        'bodyRenderResult': str(body_render_result.relative_to(D)),
        'bodyRenderResultSHA256': sha(body_render_result),
        'bodyVideoSHA256': body_render['sha256'], 'bodyFrames': BODY_FRAMES,
        'referenceAppendix': {'kind': 'references', 'from': BODY_FRAMES, 'durationInFrames': APPENDIX_FRAMES,
                             'sources': 'references.json', 'manifest': 'reference-appendix.json'},
        'appendixArtifacts': str(appendix_artifacts.relative_to(D)),
        'frames': final_frames, 'fps': 30, 'captions': len(captions), 'chapters': len(sb['scenes']),
        'files': files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Write the site copy only after final media review')
    parser.add_argument('--published-at', help='Actual first-publication ISO timestamp with timezone; defaults to invocation time')
    parser.add_argument('--appendix-artifacts', type=Path, default=D / 'revisions/reference-endcards')
    parser.add_argument('--body-render-result', type=Path, default=D / 'revisions/reference-endcards/body-render-result.json')
    args = parser.parse_args()
    original_meta, verification = validate(args.appendix_artifacts.resolve(), args.body_render_result.resolve())
    if not args.publish:
        print(json.dumps({'status': 'read-only-validation-passed', **verification}, ensure_ascii=False, indent=2))
        return
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    first_publication = original_meta.get('publishedAt') or args.published_at or now
    parsed = datetime.fromisoformat(first_publication)
    assert parsed.tzinfo is not None, 'First publication must include a timezone'
    assert parsed >= datetime.fromisoformat(original_meta['createdAt'])
    assert parsed >= datetime.fromisoformat(original_meta['updatedAt'])
    metadata = {**original_meta, 'publishedAt': first_publication, 'firstRelease': RELEASE,
                'finalVideoFrames': verification['frames'], 'referenceAppendix': verification['referenceAppendix'], 'draft': False}
    assert metadata['createdAt'] == original_meta['createdAt']
    assert metadata['updatedAt'] == original_meta['updatedAt']
    assert not original_meta.get('firstRelease') or original_meta['firstRelease'] == RELEASE
    if args.published_at and original_meta.get('publishedAt'):
        assert args.published_at == original_meta['publishedAt'], 'Preserve the existing first-publication time'
    for name, detail in verification['files'].items():
        shutil.copyfile(D / detail['source'], DESTINATION / name)
        assert sha(DESTINATION / name) == verification['files'][name]['sha256']
    (DESTINATION / 'meta.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    assert set(path.name for path in DESTINATION.iterdir()) == {'meta.json', *verification['files']}, 'Unexpected files in published episode'
    verification['files']['meta.json'] = {
        'sha256': sha(DESTINATION / 'meta.json'), 'bytes': (DESTINATION / 'meta.json').stat().st_size,
    }
    report = {
        'status': 'site-copy-prepared', 'preparedAtBeijing': now,
        'publicationStatus': 'Publishable copy prepared; actual deployment availability is verified separately.',
        'firstRelease': RELEASE, 'destination': str(DESTINATION.relative_to(ROOT)),
        'source': str(D.relative_to(ROOT)),
        'metadataPreserved': {key: original_meta[key] for key in ['createdAt', 'updatedAt']},
        'metadata': metadata, **verification,
        'scope': 'Frozen inputs, narration identity and encoded-media summary verified; only a fixed site-file whitelist copied. Does not replace final-film review.',
        'exclusions': ['voice.wav', 'PNG production art', 'Remotion source', 'node_modules'],
    }
    (D / 'delivery-copy.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'files': len(report['files']),
                      'preserved': report['metadataPreserved'], 'publishedAt': first_publication,
                      'videoSHA256': verification['videoSHA256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
