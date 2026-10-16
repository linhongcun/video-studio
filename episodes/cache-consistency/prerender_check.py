"""Validate storyboard structure, assets, and the generated v9 voice track."""
import json
from pathlib import Path
import sys
import wave

from build_voice import read_narration

HERE = Path(__file__).resolve().parent


def asset_references(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ('asset', 'file', 'png') and isinstance(child, str) and child.startswith('assets/'):
                yield child
            yield from asset_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from asset_references(child)


def check():
    storyboard = json.loads((HERE / 'storyboard.json').read_text())
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    total = storyboard['meta']['durationInFrames']
    fps = storyboard['meta']['fps']
    assert (storyboard['meta']['width'], storyboard['meta']['height'], fps) == (1920, 1080, 30)
    assert len({shot['id'] for shot in shots}) == len(shots), 'Duplicate shot IDs'
    cursor = 0
    cards = []
    for shot in shots:
        assert shot['from'] == cursor, f"Noncontiguous shot: {shot['id']} at {shot['from']}, expected {cursor}"
        duration = shot['durationInFrames']
        assert isinstance(duration, int) and duration > 0, shot['id']
        cursor += duration
        if shot.get('chapterCard'):
            cards.append(shot)
        elif shot['chapterId'] != 'ending':
            assert duration <= 330, f"Shot too long: {shot['id']} ({duration} frames)"
        for element in shot['elements']:
            assert element['type'] in {'rect', 'image', 'text', 'line'}, f"Unsupported element: {element}"
            if element['type'] == 'image':
                assert element['asset'].startswith('assets/') and element['asset'].endswith('.svg'), element
    assert total == cursor, f'Storyboard total {total} != shot sum {cursor}'
    colored = [shot for shot in cards if shot['chapterCard']['gray'] is False]
    gray = [shot for shot in cards if shot['chapterCard']['gray'] is True]
    assert len(colored) == 5 and len(gray) == 2 and len(cards) == 7, 'Expected 5 colored and 2 gray cards'
    for shot in cards:
        expected = 45 if shot['chapterCard']['gray'] else 78
        assert shot['durationInFrames'] == shot['chapterCard']['holdFrames'] == expected, shot['id']
        dots = [element for element in shot['elements'] if element['id'].startswith('pi')]
        assert (not dots) if shot['chapterCard']['gray'] else bool(dots), shot['id']
    assert [shot['background'] for shot in colored] == ['#2563EB', '#EA580C', '#DC2626', '#7C3AED', '#0D9488'], 'Unexpected chapter colors'
    references = set(asset_references(storyboard))
    for reference in references:
        asset = (HERE / reference).resolve()
        assert asset.is_relative_to(HERE / 'assets') and asset.is_file(), f'Missing asset: {reference}'
    timing = json.loads((HERE / 'remotion/src/timing.json').read_text())
    assert set(timing) == {shot['id'] for shot in shots}, 'Stale Remotion timing; run node sync_assets.mjs'
    for shot in shots:
        assert timing[shot['id']]['from'] == shot['from'] and timing[shot['id']]['duration'] == shot['durationInFrames'], f"Stale timing: {shot['id']}"
    holds = json.loads((HERE / 'holds_applied.json').read_text())
    assert len(holds) == len(cards) + 1, 'Expected seven card holds and one tail'
    params, narration, digest = read_narration()
    sr = params.framerate
    stride = params.nchannels * params.sampwidth
    with wave.open(str(HERE / 'remotion/public/audio/voice.wav'), 'rb') as voice:
        assert (voice.getframerate(), voice.getnchannels(), voice.getsampwidth()) == (sr, params.nchannels, params.sampwidth)
        voice_samples = voice.getnframes()
        pcm = voice.readframes(voice_samples)
    previous = 0
    inserted = 0
    for shot, hold in zip(cards, holds[:-1]):
        assert (hold['shot'], hold['before'], hold['frames']) == (shot['id'], shot['chapterCard']['insertBeforeSentence'], shot['durationInFrames'])
        position = hold['orig_sample']
        assert previous <= position <= params.nframes
        assert hold['samples'] == round(hold['frames'] * sr / fps)
        assert hold['output_sample'] == position + inserted
        assert pcm[(previous + inserted) * stride:(position + inserted) * stride] == narration[previous * stride:position * stride], 'Narration altered'
        assert not any(pcm[(position + inserted) * stride:(position + inserted + hold['samples']) * stride]), 'Card hold is not silent'
        inserted += hold['samples']
        previous = position
    tail = holds[-1]
    assert tail['before'] == 'end' and tail['samples'] >= 0
    assert tail['narration_sha256'] == digest and tail['narration_samples'] == params.nframes
    assert tail['output_sample'] == params.nframes + inserted
    assert abs(tail['frames'] - tail['samples'] * fps / sr) < 1e-6
    assert pcm[(previous + inserted) * stride:(params.nframes + inserted) * stride] == narration[previous * stride:], 'Narration ending altered'
    assert not any(pcm[(params.nframes + inserted) * stride:]), 'Tail is not silent'
    assert voice_samples == params.nframes + inserted + tail['samples'], 'Narration + holds + tail != voice samples'
    voice_frames = voice_samples * fps / sr
    assert abs(total - voice_frames) <= 1, f'Storyboard {total} != voice {voice_frames:.6f} frames'
    print(f'PASS: {len(shots)} contiguous shots, {total} frames, voice {voice_frames:.6f} frames, 5×78 + 2×45 cards, {len(references)} asset files')


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, OSError, ValueError, KeyError, TypeError, wave.Error) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
