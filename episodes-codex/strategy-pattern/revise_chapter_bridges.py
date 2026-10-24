#!/usr/bin/env python3
"""Revision orchestration: shared voice build, per-shot PCM reuse, local renders.

No TTS, trimming, onset, normalization or mixing algorithm is reimplemented here.
The published v0.52.0 Git tag supplies immutable reusable inputs.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
OUT = D / 'remotion/out/chapter-bridges'
BASE = OUT / 'base'
TAG = 'v0.52.0'
CHANGED = {'04', '11', '15'}
FPS, SR, SPF = 30, 48000, 1600


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def shots(sb):
    return [s for scene in sb['scenes'] for s in scene['shots']]


def pcm(path):
    with wave.open(str(path)) as f:
        assert (f.getframerate(), f.getnchannels(), f.getsampwidth()) == (SR, 1, 2)
        return f.readframes(f.getnframes())


def write_pcm(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(data)


def packet_hash(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
        '-map', '0:v:0', '-c:v', 'copy', '-f', 'hash', '-'], text=True).strip()


def archive():
    names = ['script.md', 'plan.json', 'episode-config.json', 'covers.json',
             'storyboard.json', 'words.json', 'voice.wav', 'voice/build.json',
             'voice/picks.json', 'voice/sents.json', 'voice/params.json',
             'source-sha256.json', 'video.mp4', 'remotion/src/Main.tsx',
             'remotion/src/motion.ts']
    entries = {}
    for name in names:
        path = BASE / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open('wb') as f:
                run(['git', 'show', f'{TAG}:episodes-codex/strategy-pattern/{name}'], cwd=ROOT, stdout=f)
        expected = subprocess.check_output(['git', 'show', f'{TAG}:episodes-codex/strategy-pattern/{name}'], cwd=ROOT)
        assert path.read_bytes() == expected, f'Baseline changed: {name}'
        entries[name] = sha(path)
    assert entries['video.mp4'] == 'c80f9e44ee8eb668fb702266170d4fd8773d14f120e315b568d6ed5d07c27431'
    original_unmixed = D / 'remotion/out/voice.mp4'
    equivalent = None
    if original_unmixed.exists() and not (OUT / 'render-complete.json').exists():
        equivalent = packet_hash(original_unmixed) == packet_hash(BASE / 'video.mp4')
        assert equivalent, 'Current unmixed source is not the published baseline picture stream'
    save(D / 'chapter-bridge-baseline.json', {'tag': TAG,
        'commit': subprocess.check_output(['git', 'rev-parse', TAG + '^{}'], cwd=ROOT, text=True).strip(),
        'recovery': 'Run this script with archive; inputs are read with git show from the immutable published tag.',
        'files': entries, 'unmixedVideoPacketsEqualPublishedVideoPackets': equivalent})
    print(f'Archived {len(entries)} immutable inputs from {TAG}')


def assemble():
    assert (BASE / 'voice.wav').exists(), 'Run archive first'
    picks_path = D / 'voice/chapter-bridge-picks.json'
    picks_new = read(picks_path)
    assert len(picks_new) == 6 and {k[:2] for k in picks_new} == CHANGED
    # prep is the sole source of sentence text and script/narration hashes.
    run([sys.executable, ROOT / 'episodes/_shared/voice/prep.py', '--dir', D], cwd=ROOT)
    sents = read(D / 'voice/sents.json')
    assert len(sents) == 32
    chosen = [r for r in sents if r['id'][:2] in CHANGED]
    assert len(chosen) == 6 and {r['id'] for r in chosen} == set(picks_new)
    old_build, old_sb = read(BASE / 'voice/build.json'), read(BASE / 'storyboard.json')
    old_shots = shots(old_sb)
    old_bytes = pcm(BASE / 'voice.wav')
    old_rows = {r['id']: r for r in old_build['sentences']}
    old_text = {r['id']: r['text'] for r in read(BASE / 'voice/sents.json')}
    assert all(r['text'] == old_text[r['id']] for r in sents if r['id'][:2] not in CHANGED)
    stage = OUT / 'shared-voice-stage'
    (stage / 'voice').mkdir(parents=True, exist_ok=True)
    take_link = stage / 'voice/takes'
    if not take_link.exists():
        take_link.symlink_to(D / 'voice/takes', target_is_directory=True)
    params = read(D / 'voice/params.json')
    # Use the shared builder's normal fades/gaps/normalization. Only new speech
    # is built here; a one-frame lead and normal shot gap retain a brief pause.
    params.update(lead=1 / FPS, tail=.70)
    save(stage / 'voice/params.json', params)
    save(stage / 'voice/sents.json', chosen)
    save(stage / 'voice/picks.json', picks_new)
    log = OUT / 'shared-voice-stage-build.log'
    with log.open('w') as f:
        run([sys.executable, ROOT / 'episodes/_shared/voice/build.py', '--dir', stage], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    built = read(stage / 'voice/build.json')
    new_bytes = pcm(stage / 'voice.wav')
    new_rows = {r['id']: r for r in built['sentences']}
    # Shared assembly starts a non-first shot at floor(first sentence). Drop
    # this isolated stage's leading frame instead of borrowing it from shot03.
    starts = [math.floor(built['sentences'][0]['startFrame'])]
    for sid in ['11', '15']:
        starts.append(math.floor(next(r['startFrame'] for r in built['sentences'] if r['id'].startswith(sid + '-'))))
    ends = starts[1:] + [built['summary']['frames']]
    stage_ranges = dict(zip(['04', '11', '15'], zip(starts, ends)))
    output, final_rows, mappings, cursor = [], [], [], 0
    for old in old_shots:
        sid = old['id']
        if sid in CHANGED:
            source_start, source_end = stage_ranges[sid]
            chunk = new_bytes[source_start * SPF * 2:source_end * SPF * 2]
            source_rows = new_rows
            origin = 'shared voice/build.py output for new chapter sentences'
        else:
            source_start, source_end = old['from'], old['from'] + old['durationInFrames']
            chunk = old_bytes[source_start * SPF * 2:source_end * SPF * 2]
            source_rows = old_rows
            origin = 'published v0.52.0 frame-aligned PCM, exact reuse'
        duration = source_end - source_start
        assert len(chunk) == duration * SPF * 2
        output.append(chunk)
        delta = cursor - source_start
        for sent in [s for s in sents if s['id'].startswith(sid + '-')]:
            row = copy.deepcopy(source_rows[sent['id']])
            row['startSample'] += delta * SPF
            row['endSample'] += delta * SPF
            # Keep the builder's own rounded frame envelope; integer offsets do
            # not alter an unmodified shot's local timing or audio.
            row['startFrame'] = round(row['startFrame'] + delta, 2)
            row['endFrame'] = round(row['endFrame'] + delta, 2)
            final_rows.append(row)
        mappings.append({'shot': sid, 'changed': sid in CHANGED, 'oldFrom': old['from'],
            'oldFrames': old['durationInFrames'], 'newFrom': cursor, 'newFrames': duration,
            'source': origin, 'pcmSHA256': hashlib.sha256(chunk).hexdigest()})
        cursor += duration
    final_pcm = b''.join(output)
    write_pcm(D / 'voice.wav', final_pcm)
    for row in final_rows:
        write_pcm(D / 'voice/sentences' / (row['id'] + '.wav'),
                  final_pcm[row['startSample'] * 2:row['endSample'] * 2])
    sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
    from common import lufs
    a = np.frombuffer(final_pcm, dtype='<i2').astype(np.float32) / 32767
    splices = [dict(pair=a_['id'] + '->' + b['id'],
                    lufs_diff=round(abs(a_['lufs'] - b['lufs']), 2),
                    gapFrames=round((b['startSample'] - a_['endSample']) / SPF, 2))
               for a_, b in zip(final_rows, final_rows[1:])]
    summary = {'frames': cursor, 'samples': len(final_pcm) // 2, 'seconds': cursor / FPS,
        'sha': sha(D / 'voice.wav'), 'track_lufs': lufs(a), 'peak': float(np.abs(a).max()),
        'max_neighbour_lufs_diff': max(x['lufs_diff'] for x in splices),
        'inner_dropouts': [r['id'] for r in final_rows if r.get('maxInnerSilenceS', 0) >= .5],
        'assemblyMethod': 'Per-shot exact PCM reuse; changed speech produced by shared build.py. No final normalization of reused voice PCM.'}
    save(D / 'voice/build.json', {'summary': summary, 'sentences': final_rows, 'splices': splices})
    picks = read(BASE / 'voice/picks.json')
    picks.update(picks_new)
    save(D / 'voice/picks.json', picks)
    for command in [
        [ROOT / 'episodes-codex/_shared/assemble_sentence_episode.py', D],
        [ROOT / 'episodes/_shared/place_v2.py', '--dir', D, '--mode', 'whole'],
        [ROOT / 'episodes/_shared/label_onset_strict.py', '--dir', D],
        [ROOT / 'episodes-codex/_shared/check_sentence_episode.py', D],
    ]:
        run([sys.executable, *command], cwd=ROOT)
    current_shots = {s['id']: s for s in shots(read(D / 'storyboard.json'))}
    for old, mapping in zip(old_shots, mappings):
        new = current_shots[old['id']]
        assert new['from'] == mapping['newFrom'] and new['durationInFrames'] == mapping['newFrames']
        if old['id'] not in CHANGED:
            assert old['subtitles'] == new['subtitles']
            assert old['cueFrames'] == new['cueFrames']
            assert old['narration'] == new['narration']
            assert old['durationInFrames'] == new['durationInFrames']
            # Voice local fields are derived from exact integer sample offsets;
            # compare after their two-decimal frame precision to avoid float noise.
            for a_, b in zip(old['voice'], new['voice']):
                assert round(a_['localStart'], 2) == round(b['localStart'], 2)
                assert round(a_['localEnd'], 2) == round(b['localEnd'], 2)
            fresh = final_pcm[new['from'] * SPF * 2:(new['from'] + new['durationInFrames']) * SPF * 2]
            original = old_bytes[old['from'] * SPF * 2:(old['from'] + old['durationInFrames']) * SPF * 2]
            assert fresh == original
    report = {'baseTag': TAG, 'baseVoiceSHA256': sha(BASE / 'voice.wav'),
        'newVoiceSHA256': sha(D / 'voice.wav'), 'oldFrames': old_sb['meta']['durationInFrames'],
        'newFrames': cursor, 'changedShots': sorted(CHANGED), 'reusedShots': 13,
        'reusedPCMExact': True, 'reusedLocalSubtitlesAndCuesExact': True,
        'newSharedBuild': str(log.relative_to(D)), 'mappings': mappings,
        'summary': summary, 'limitation': 'Sentence envelope and measured first-word cue only; not ASR or a claim of full human listening.'}
    save(D / 'chapter-bridge-assembly.json', report)
    print(json.dumps({k: report[k] for k in ['newFrames', 'changedShots', 'reusedShots', 'reusedPCMExact', 'reusedLocalSubtitlesAndCuesExact']}, ensure_ascii=False))


def render():
    run([sys.executable, D / 'freeze.py', '--verify'], cwd=ROOT)
    sb = read(D / 'storyboard.json')
    new_shots = {s['id']: s for s in shots(sb)}
    OUT.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR='/workspace/strategy-bridge-tmp')
    Path(env['TMPDIR']).mkdir(exist_ok=True)
    for sid in sorted(CHANGED):
        s = new_shots[sid]
        target = OUT / f'shot-{sid}.mp4'
        with (OUT / f'render-{sid}.log').open('w') as log:
            run(['flock', '/tmp/video-studio-render.lock', 'npx', 'remotion', 'render',
                 'src/index.ts', 'Main', target, '--codec=h264', '--crf=20', '--concurrency=2',
                 '--browser-executable=/usr/bin/chromium', '--bundle-cache=false', '--muted',
                 f"--frames={s['from']}-{s['from'] + s['durationInFrames'] - 1}"],
                cwd=D / 'remotion', env=env, stdout=log, stderr=subprocess.STDOUT)
    old_shots = shots(read(BASE / 'storyboard.json'))
    old = {s['id']: s for s in old_shots}
    segments = []
    start = 0
    for sid in sorted(CHANGED):
        s = old[sid]
        if s['from'] > start:
            segments.append({'kind': 'reused', 'source': BASE / 'video.mp4',
                             'start': start, 'frames': s['from'] - start})
        segments.append({'kind': 'local-render', 'source': OUT / f'shot-{sid}.mp4',
                         'start': 0, 'frames': new_shots[sid]['durationInFrames']})
        start = s['from'] + s['durationInFrames']
    total_old = read(BASE / 'storyboard.json')['meta']['durationInFrames']
    if start < total_old:
        segments.append({'kind': 'reused', 'source': BASE / 'video.mp4',
                         'start': start, 'frames': total_old - start})
    args = ['ffmpeg', '-v', 'error', '-y']
    filters = []
    for i, seg in enumerate(segments):
        if seg['kind'] == 'reused':
            args += ['-ss', f"{seg['start'] / FPS:.12f}", '-t', f"{seg['frames'] / FPS + .2:.12f}"]
        args += ['-i', seg['source']]
        filters.append(f"[{i}:v]trim=end_frame={seg['frames']},setpts=N/(30*TB)[v{i}]")
    audio_index = len(segments)
    args += ['-i', D / 'voice.wav']
    filters.append(''.join(f'[v{i}]' for i in range(len(segments))) + f'concat=n={len(segments)}:v=1:a=0[v]')
    args += ['-filter_complex', ';'.join(filters), '-map', '[v]', '-map', f'{audio_index}:a:0',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
             '-r', '30', '-video_track_timescale', '90000', '-c:a', 'aac', '-ar', '48000',
             '-b:a', '192k', '-movflags', '+faststart', D / 'remotion/out/voice.mp4']
    with (OUT / 'concat.log').open('w') as log:
        run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    run(['npm', 'run', 'render:mix'], cwd=D / 'remotion', env=env)
    shutil.copyfile(D / 'remotion/out/mix-report.json', D / 'mix-report.json')
    frames = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(D / 'video.mp4')]))['frames']
    assert len(frames) == sb['meta']['durationInFrames']
    for i, frame in enumerate(frames):
        assert abs(float(frame['best_effort_timestamp_time']) - i / FPS) < .000002
    report = {'renderedShots': sorted(CHANGED), 'reusedShots': 13,
        'sourceVideoSHA256': sha(BASE / 'video.mp4'), 'finalVideoSHA256': sha(D / 'video.mp4'),
        'frames': len(frames), 'continuousPTS': True,
        'pictureMethod': 'Only 3 shots rendered by Remotion; 13 published picture intervals decoded and precisely trimmed, then one whole-picture H264 transcode. Encoded packets are not claimed byte-identical.',
        'segments': [{**s, 'source': str(s['source'].relative_to(D))} for s in segments]}
    save(D / 'chapter-bridge-render.json', report)
    save(OUT / 'render-complete.json', report)
    run([sys.executable, ROOT / 'episodes-codex/_shared/check_encoded_episode.py', D], cwd=ROOT)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['archive', 'assemble', 'render'])
    action = p.parse_args().action
    {'archive': archive, 'assemble': assemble, 'render': render}[action]()
