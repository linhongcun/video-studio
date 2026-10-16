"""Validate storyboard structure, assets, and the generated v9 voice track."""
import json
from pathlib import Path
import sys
import wave

from build_voice import read_sentence

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
    assert len(holds) == 50, f'Expected 50 placed sentences, got {len(holds)}'
    sr = 48000
    with wave.open(str(HERE / 'remotion/public/audio/voice.wav'), 'rb') as voice:
        assert (voice.getframerate(), voice.getnchannels(), voice.getsampwidth()) == (sr, 1, 2)
        voice_samples = voice.getnframes()
        pcm = voice.readframes(voice_samples)
    assert voice_samples == round(total * sr / fps), 'Voice length != storyboard'
    starts = {}
    for shot in shots:
        for sub in shot.get('subtitles', []):
            if 'src' in sub:
                starts.setdefault((shot['id'], sub['src']), shot['from'] + sub['voiceFrom'])
                starts[(shot['id'], sub['src'])] = min(starts[(shot['id'], sub['src'])], shot['from'] + sub['voiceFrom'])
    prev_end = 0
    for h in holds:
        assert h['startFrame'] == starts[(h['shot'], h['id'])], f"Stale placement: {h['id']}"
        assert h['startSample'] == round(h['startFrame'] * sr / fps) and h['startSample'] >= prev_end, h['id']
        sent = read_sentence(h['id'])
        assert pcm[h['startSample'] * 2:h['endSample'] * 2] == sent, f"Sentence audio mismatch: {h['id']}"
        assert not any(pcm[prev_end * 2:h['startSample'] * 2]), f"Gap before {h['id']} not silent"
        prev_end = h['endSample']
    assert not any(pcm[prev_end * 2:]), 'Tail not silent'
    voice_frames = voice_samples * fps / sr
    print(f'PASS: {len(shots)} contiguous shots, {total} frames, voice {voice_frames:.6f} frames, 50 sentences at voiceFrom, 5×78 + 2×45 cards, {len(references)} asset files')


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, OSError, ValueError, KeyError, TypeError, wave.Error) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
