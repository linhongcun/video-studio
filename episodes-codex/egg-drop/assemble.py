#!/usr/bin/env python3
"""P05 wrapper around the shared sentence assembler; no timing algorithms."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import runpy
import sys


EPISODE = Path(__file__).resolve().parent
SHARED = EPISODE.parents[1] / 'episodes-codex/_shared/assemble_sentence_episode.py'

if __name__ == '__main__':
    previous_argv = sys.argv[:]
    try:
        sys.argv = [str(SHARED), str(EPISODE)]
        runpy.run_path(str(SHARED), run_name='__main__')
    finally:
        sys.argv = previous_argv
    # An integer relocation of identical PCM must preserve the original local
    # floating-point values too. Re-subtracting larger global floats can change
    # SVG state at the final bits despite the exact same physical frame.
    baseline = EPISODE / 'revisions/binary-opening/baseline/storyboard.json'
    original = json.loads(baseline.read_text())
    current = json.loads((EPISODE / 'storyboard.json').read_text())
    composition = json.loads((EPISODE / 'voice/binary-opening-composition.json').read_text())
    assert composition['all20ReusedSentencePCMExact']
    assert hashlib.sha256((EPISODE / 'voice.wav').read_bytes()).hexdigest() == composition['audioSHA256']
    old_shots = {q['id']: q for sc in original['scenes'] for q in sc['shots']}
    reused = []
    for scene in current['scenes']:
        for shot in scene['shots']:
            if shot['id'] in {'03', '04'}:
                continue
            old = old_shots[shot['id']]
            shift = 0 if int(shot['id']) < 3 else composition['deltaFrames']
            assert shot['from'] - old['from'] == shift
            for key in ['durationInFrames', 'narration', 'subtitles', 'cueFrames', 'visualType', 'chapterId']:
                assert shot[key] == old[key], (shot['id'], key)
            assert len(shot['voice']) == len(old['voice']) == 2
            for voice, previous in zip(shot['voice'], old['voice']):
                assert voice['id'] == previous['id']
                for key in ['wavStart', 'wavEnd']:
                    assert Decimal(str(voice[key])) - Decimal(str(previous[key])) == shift
                for key in ['localStart', 'localEnd']:
                    voice[key] = previous[key]
            reused.append(shot['id'])
    assert len(reused) == 10
    current['meta']['localTimingReuse'] = dict(
        method='Exact baseline local voice values after proven integer PCM relocation; shared global assembly unchanged.',
        baselineStoryboardSHA256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
        shots=reused, deltaFrames=composition['deltaFrames'])
    (EPISODE / 'storyboard.json').write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n')
    (EPISODE / 'revisions/binary-opening/qa-local-timing-reuse.json').write_text(
        json.dumps(current['meta']['localTimingReuse'], ensure_ascii=False, indent=2) + '\n')
    # Keep the shared output and the site-facing name byte-identical.
    (EPISODE / 'subtitles.srt').write_bytes((EPISODE / 'captions.srt').read_bytes())
