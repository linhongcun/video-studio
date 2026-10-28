#!/usr/bin/env python3
"""Normalize preserved Redis body to limited BT.709 and append matching bibliography.

Old redis-style sources, manifest, body and final movie are immutable inputs.
Default prints a plan. Freeze, render and read-only verify are separate stages.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'episodes-codex/redis-skiplist/revisions/redis-style'
NEW = ROOT / 'episodes-codex/redis-skiplist/revisions/redis-style-bt709'
REFERENCES = ROOT / 'episodes-codex/redis-skiplist/revisions/height-choice/redis-skiplist/references.json'
spec = importlib.util.spec_from_file_location('redis_bt709_refs', HERE / 'references.py')
refs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refs)
engine = refs.engine


def read(path):
    return json.loads(path.read_text())


def relative(path):
    return str(path.resolve().relative_to(ROOT))


def versions():
    return {'python': sys.version, 'ffmpeg': engine.run(['ffmpeg', '-version']).splitlines()[0],
            'ffprobe': engine.run(['ffprobe', '-version']).splitlines()[0]}


def command():
    return ['ffmpeg', '-v', 'error', '-n', '-i', relative(OLD / 'body.mp4'),
            '-map', '0:v:0', '-map', '0:a:0',
            '-vf', 'scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-threads', '4',
            '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709',
            '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-fps_mode', 'passthrough', '-video_track_timescale', '90000',
            '-c:a', 'copy', '-map_metadata', '-1', '-movflags', '+faststart',
            '-metadata', 'comment=video-studio-redis-bt709-body:v1:redis-skiplist', relative(NEW / 'body.mp4')]


def input_bindings():
    prior = read(OLD / 'source-sha256.json')
    files = {**prior['inputs'], **prior['externalInputs']}
    for path in [OLD / name for name in ('source-sha256.json', 'body.mp4', 'video.mp4', 'render-result.json',
                 'reference-appendix.json', 'reference-appendix-media-check.json', 'baseline-audio-check.json')] \
            + [HERE / name for name in ('render.py', 'references.py', 'README.md')]:
        files[relative(path)] = engine.sha(path)
    baseline = prior['baseline']
    files[baseline['path']] = baseline['sha256']
    return files


def verify_inputs():
    manifest = read(NEW / 'source-sha256.json')
    if manifest['inputs'] != input_bindings() or manifest['command'] != command() or manifest['versions'] != versions():
        raise ValueError('Frozen color-normalization input/command/version identity differs')
    for name, expected in manifest['inputs'].items():
        path = Path(name) if Path(name).is_absolute() else ROOT / name
        if not path.is_file() or engine.sha(path) != expected:
            raise ValueError(f'Normalization input changed: {name}')
    return manifest


def freeze():
    manifest = NEW / 'source-sha256.json'
    if manifest.exists():
        verify_inputs()
        return {'status': 'already-frozen-read-only', 'manifest': relative(manifest)}
    if any((NEW / name).exists() for name in ('body.mp4', 'video.mp4', 'render-result.json')):
        raise ValueError('Media already exists without freeze; choose a fresh independent revision')
    for name, expected in input_bindings().items():
        path = Path(name) if Path(name).is_absolute() else ROOT / name
        if engine.sha(path) != expected:
            raise ValueError(f'Original frozen input differs: {name}')
    value = {'schemaVersion': 1, 'episode': 'redis-skiplist', 'visualRevision': 'redis-style-bt709-v1',
             'createdAtUTC': datetime.now(timezone.utc).isoformat(), 'inputs': input_bindings(),
             'timeline': {'width': 1920, 'height': 1080, 'fps': 30, 'bodyFrames': 4557, 'finalVideoFrames': 4707},
             'command': command(), 'workingDirectory': '.', 'versions': versions(),
             'inputColorEncoding': {'pix_fmt': 'yuvj420p', 'color_range': 'pc', 'color_space': 'bt470bg'},
             'outputColorEncoding': refs.COLOR,
             'policy': 'Independent color normalization; old frozen redis-style input, outputs and all historical evidence remain unchanged.'}
    engine.dump(manifest, value)
    verify_inputs()
    return {'status': 'frozen', 'manifest': relative(manifest), 'inputCount': len(value['inputs'])}


def pts(path):
    video = engine.stream(engine.probe(path), 'video')
    raw = json.loads(engine.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_packets',
                    '-show_entries', 'packet=pts,duration', '-of', 'json', str(path)]))['packets']
    frames = sorted([[int(packet['pts']), int(packet['duration'])] for packet in raw])
    if len(frames) != int(video['nb_frames']) or video['time_base'] != '1/90000' \
            or any(row != [index * 3000, 3000] for index, row in enumerate(frames)):
        raise ValueError('Expected one H.264 MP4 packet/frame and exact continuous 30fps presentation timeline')
    return {'time_base': video['time_base'], 'frames': frames}


def normalization_check():
    source, output = OLD / 'body.mp4', NEW / 'body.mp4'
    before, after = pts(source), pts(output)
    if before != after or len(after['frames']) != 4557:
        raise ValueError('Normalization changed video PTS, duration or frame count')
    video = engine.stream(engine.probe(output), 'video')
    for key, expected in {**refs.COLOR, 'codec_name': 'h264', 'width': 1920, 'height': 1080,
                          'r_frame_rate': '30/1', 'avg_frame_rate': '30/1'}.items():
        if video.get(key) != expected:
            raise ValueError(f'Normalized body lacks {key}={expected}')
    prior = read(OLD / 'source-sha256.json')
    baseline = ROOT / prior['baseline']['path']
    packets, normalized = engine.audio_packets(baseline), engine.audio_packets(output)
    pcm, normalized_pcm = engine.audio_hash(baseline), engine.audio_hash(output)
    if packets != normalized or pcm != normalized_pcm:
        raise ValueError('Normalization changed baseline AAC packets/timing or decoded PCM')
    return {'passed': True, 'sourceSHA256': engine.sha(source), 'outputSHA256': engine.sha(output),
            'baselineSHA256': engine.sha(baseline), 'videoFrames': 4557,
            'allVideoPTSAndDurationsEqual': True, 'timelineBasis': 'All H.264 MP4 packet PTS/durations sorted by presentation time; one packet/frame and exact continuous 30fps asserted. Appendix verifier additionally fully decodes body/final frames and PTS.', 'videoPTSAndDurationsSHA256': engine.sequence_hash(after),
            'audioPacketCount': len(packets), 'audioPacketPayloadAndTimingSHA256': engine.sequence_hash(packets),
            'audioPacketsAndTimingEqual': True, 'decodedAudioPCM': pcm,
            'colorEncoding': refs.COLOR,
            'scope': 'Lossy color-normalized pictures; all video PTS/durations and complete baseline AAC packets/PCM preserved. Browser color/legibility checked independently.'}


def append_args():
    return SimpleNamespace(body=NEW / 'body.mp4', output=NEW / 'video.mp4', references=REFERENCES,
                           artifacts=NEW / 'references', seconds=5, font=refs.DEFAULT_FONT, bold_font=refs.DEFAULT_BOLD)


def render():
    manifest = verify_inputs()
    if (NEW / 'video.mp4').exists():
        raise ValueError('Final color-normalized movie already exists; use --verify')
    subprocess.run(command(), cwd=ROOT, check=True)
    verify_inputs()
    audio = normalization_check()
    engine.dump(NEW / 'normalization-check.json', audio)
    receipt = refs.append(append_args())
    verify_inputs()
    final = NEW / 'video.mp4'
    final_pts = pts(final)
    if len(final_pts['frames']) != 4707 or final_pts != pts(OLD / 'video.mp4') \
            or final_pts['frames'][:4557] != pts(NEW / 'body.mp4')['frames']:
        raise ValueError('Final normalized video PTS differ from the preserved 4707-frame movie')
    publication = {'finalVideoFrames': 4707, 'referenceAppendix': {'kind': 'references', 'from': 4557,
                   'durationInFrames': 150, 'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    result = {'visualRevision': 'redis-style-bt709-v1', 'createdAtUTC': datetime.now(timezone.utc).isoformat(),
              'episode': 'redis-skiplist', 'width': 1920, 'height': 1080, 'fps': '30/1',
              'frames': 4707, 'bodyFrames': 4557, 'seconds': 156.9, 'bytes': final.stat().st_size,
              'sha256': engine.sha(final), 'audio': 'aac', 'audioSampleRate': 48000,
              **publication, 'publicationMetadata': publication, 'presentation': 'title-author',
              'bibliographyOnly': True, 'newProductionManifest': relative(NEW / 'source-sha256.json'),
              'newProductionManifestSHA256': engine.sha(NEW / 'source-sha256.json'),
              'sourceInputsVerified': len(manifest['inputs']), 'baselineAudioPreserved': audio,
              'colorEncoding': refs.COLOR,
              'bodyProvenance': 'The preserved redis-style body was independently normalized from full-range BT.601 to limited-range BT.709, with exact video timeline and complete baseline AAC retained; original frozen render and historical evidence are unchanged.',
              'loudnessBasis': 'Complete AAC packet/timing and decoded PCM identity to the published baseline; no remix.',
              'reviewScope': 'New normalization, all video PTS/durations, full baseline audio and appended decoded body-frame preservation; actual browser colors and legibility require independent review.'}
    engine.dump(NEW / 'render-result.json', result)
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        shutil.copyfile(NEW / 'references' / name, NEW / name)
    return {'status': 'rendered', 'sha256': result['sha256'], **publication}


def verify():
    manifest = verify_inputs()
    actual = normalization_check()
    if pts(NEW / 'video.mp4') != pts(OLD / 'video.mp4'):
        raise ValueError('Final video PTS differ from the preserved 4707-frame movie')
    if actual != read(NEW / 'normalization-check.json'):
        raise ValueError('Recorded normalization check differs')
    refs.verify(append_args())
    result = read(NEW / 'render-result.json')
    if result['sha256'] != engine.sha(NEW / 'video.mp4') or result['newProductionManifestSHA256'] != engine.sha(NEW / 'source-sha256.json'):
        raise ValueError('Result identity differs')
    return {'status': 'verified-read-only', 'sha256': result['sha256'], 'inputCount': len(manifest['inputs'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    for name in ('freeze', 'render', 'verify'):
        group.add_argument('--' + name, action='store_true')
    args = parser.parse_args()
    result = freeze() if args.freeze else render() if args.render else verify() if args.verify else \
             {'status': 'plan-only', 'sourceBody': relative(OLD / 'body.mp4'), 'revision': relative(NEW), 'command': command()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
