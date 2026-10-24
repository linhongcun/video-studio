#!/usr/bin/env python3
"""Join a shared-build tail to the byte-preserved first 17 shots of P01.

This revision helper does not synthesize, trim, normalize, place, or detect
onsets. Generate and build the tail with the repository's shared voice tools,
then run this helper, shared assemble_sentence_episode/place/check, and verify.
The old full WAV must match the recorded baseline SHA; it may be restored
from the baseline Git revision when the external working copy is absent.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import wave

import numpy as np

EPISODE = Path(__file__).resolve().parent
ROOT = EPISODE.parents[1]
BEFORE = EPISODE / 'revisions/self-contained-ending/before'
PREFIX_FRAMES = 5875
PREFIX_SAMPLES = 9_400_000
SR, FPS, SAMPLES_PER_FRAME = 48000, 30, 1600
BASE_WAV_SHA = '2af8c739a08c2cf9c1972b22a0c31e1dd30cb6260fc92af749dd987a693def66'
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import lufs


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_pcm(path):
    with wave.open(str(path)) as audio:
        assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (SR, 1, 2)
        return audio.readframes(audio.getnframes())


def expected_sentences():
    text = (EPISODE / 'script.md').read_text()
    out = []
    for n, slug, body in re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', text, re.S):
        narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
        sentences = re.findall(r'[^。？！]+[。？！]', narration)
        assert len(sentences) == 2 and ''.join(sentences) == narration
        out.extend((f'{int(n):02d}-{slug}-{i+1}', sentence) for i, sentence in enumerate(sentences))
    return out


def audit_prefix(baseline_pcm, final_pcm):
    prefix_bytes = PREFIX_SAMPLES * 2
    assert baseline_pcm[:prefix_bytes] == final_pcm[:prefix_bytes], 'Preserved PCM prefix changed'
    rows = load(BEFORE / 'voice/build.json')['sentences'][:34]
    comparisons = []
    for row in rows:
        a, b = row['startSample'] * 2, row['endSample'] * 2
        assert baseline_pcm[a:b] == final_pcm[a:b], row['id']
        comparisons.append(dict(id=row['id'], startSample=row['startSample'], endSample=row['endSample'],
                                sha256=hashlib.sha256(final_pcm[a:b]).hexdigest(), exact=True))
    return dict(frames=PREFIX_FRAMES, samples=PREFIX_SAMPLES,
                sha256=hashlib.sha256(final_pcm[:prefix_bytes]).hexdigest(),
                preservedSentences=comparisons, all34SentencePCMExact=True)


def merge(tail_dir, baseline_wav):
    assert sha(baseline_wav) == BASE_WAV_SHA, 'Unexpected baseline WAV'
    provenance = load(tail_dir / 'voice/input-provenance.json')
    assert provenance['mainScriptSHA256'] == sha(EPISODE / 'script.md'), 'Frozen script changed'
    assert provenance['mainPlanSHA256'] == sha(EPISODE / 'plan.json'), 'Frozen plan changed'
    old_pcm, tail_pcm = read_pcm(baseline_wav), read_pcm(tail_dir / 'voice.wav')
    old_build, tail_build = load(BEFORE / 'voice/build.json'), load(tail_dir / 'voice/build.json')
    old_sents, tail_sents = load(BEFORE / 'voice/sents.json')[:34], load(tail_dir / 'voice/sents.json')
    expected = expected_sentences()
    assert [(s['id'], s['text']) for s in old_sents + tail_sents] == expected
    assert [(s['id'], s['text']) for s in tail_build['sentences']] == expected[34:]
    assert len(tail_pcm) == tail_build['summary']['frames'] * SAMPLES_PER_FRAME * 2
    rows = copy.deepcopy(old_build['sentences'][:34])
    for row in tail_build['sentences']:
        new = copy.deepcopy(row)
        new['startSample'] += PREFIX_SAMPLES
        new['endSample'] += PREFIX_SAMPLES
        new['startFrame'] = round(new['startSample'] * FPS / SR, 2)
        new['endFrame'] = round(new['endSample'] * FPS / SR, 2)
        if len(rows) == 34:
            new['gapBefore'] = round((new['startSample'] - rows[-1]['endSample']) / SR, 4)
        rows.append(new)
    assert int(rows[34]['startFrame']) == PREFIX_FRAMES
    pcm = old_pcm[:PREFIX_SAMPLES * 2] + tail_pcm
    prefix_audit = audit_prefix(old_pcm, pcm)
    with wave.open(str(EPISODE / 'voice.wav'), 'wb') as audio:
        audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(SR); audio.writeframes(pcm)
    signal = np.frombuffer(pcm, '<i2').astype(np.float32) / 32767
    splices = [dict(pair=f"{a['id']}->{b['id']}",
                    lufs_diff=round(abs(a['lufs'] - b['lufs']), 2),
                    gapFrames=round((b['startSample'] - a['endSample']) * FPS / SR, 1))
               for a, b in zip(rows, rows[1:])]
    def edge(sample):
        return float(np.abs(np.diff(signal[max(0, sample-480):sample+480])).max())
    frames = PREFIX_FRAMES + tail_build['summary']['frames']
    summary = dict(extraAfter={**old_build['summary'].get('extraAfter', {}),
                               **tail_build['summary'].get('extraAfter', {})},
                   track_lufs=lufs(signal), peak=float(np.abs(signal).max()),
                   max_neighbour_lufs_diff=max(s['lufs_diff'] for s in splices),
                   max_join_sample_jump=max(max(edge(s['startSample']), edge(s['endSample'])) for s in rows),
                   inner_dropouts=[s['id'] for s in rows if s['maxInnerSilenceS'] >= .5],
                   samples=len(signal), frames=frames, seconds=frames/FPS, sha=sha(EPISODE/'voice.wav'))
    assert len(signal) == frames * SAMPLES_PER_FRAME
    voice = EPISODE / 'voice'
    save(voice / 'build.json', dict(summary=summary, sentences=rows, splices=splices,
                                  assembly='Shared-build tail plus unchanged baseline PCM prefix; no full-track rescale.'))
    save(voice / 'sents.json', old_sents + tail_sents)
    old_picks, new_picks = load(BEFORE/'voice/picks.json'), load(tail_dir/'voice/picks.json')
    save(voice/'picks.json', {**{s['id']:old_picks.get(s['id'],'a') for s in old_sents}, **new_picks})
    for source in (tail_dir/'voice/takes').iterdir():
        if source.is_file(): shutil.copy2(source, voice/'takes'/source.name)
    for name in ['params.json','build.json','sents.json','sents-first-pass.json','picks.json','jobs_a.json','jobs_b.json',
                 'input-provenance.json','input-provenance-first-pass.json','qa-takes.json']:
        if (tail_dir/'voice'/name).exists(): shutil.copy2(tail_dir/'voice'/name, voice/f'ending-{name}')
    if (tail_dir/'script-first-pass.md').exists():
        shutil.copy2(tail_dir/'script-first-pass.md', voice/'ending-script-first-pass.md')
    provenance = dict(method='Shared tail build then exact PCM concatenation at a frame boundary.',
                      scriptSHA256=sha(EPISODE/'script.md'), planSHA256=sha(EPISODE/'plan.json'),
                      baselineWavSHA256=BASE_WAV_SHA, prefix=prefix_audit,
                      tailWavSHA256=sha(tail_dir/'voice.wav'), tailFrames=tail_build['summary']['frames'],
                      tailLeadSeconds=load(tail_dir/'voice/params.json')['lead'],
                      fullWavSHA256=summary['sha'], frames=frames,
                      noWholeTrackNormalization=True,
                      limitation='No interior word alignment, automatic transcript verification, or full human listening.')
    save(voice/'ending-composition.json', provenance)
    if (voice/'input-provenance.json').exists() and not (voice/'original-input-provenance.json').exists():
        shutil.copy2(voice/'input-provenance.json', voice/'original-input-provenance.json')
    save(voice/'input-provenance.json', dict(scriptSHA256=sha(EPISODE/'script.md'),
         planSHA256=sha(EPISODE/'plan.json'), sentenceCount=len(rows),
         method='34 old sentences preserved as PCM; 16 new sentences built with shared implementation.',
         preservedPrefixSource='original-input-provenance.json',
         tailSource='ending-input-provenance.json', composition='ending-composition.json'))
    print(json.dumps({k:summary[k] for k in ['frames','seconds','track_lufs','inner_dropouts','sha']}, ensure_ascii=False))


def verify(baseline_wav):
    assert sha(baseline_wav) == BASE_WAV_SHA
    report = audit_prefix(read_pcm(baseline_wav), read_pcm(EPISODE/'voice.wav'))
    old_words, words = load(BEFORE/'words.json'), load(EPISODE/'words.json')
    assert words['shots'][:17] == old_words['shots'][:17], 'First 17 word/timing objects changed'
    old_shots = [s for c in load(BEFORE/'storyboard.json')['scenes'] for s in c['shots']][:17]
    shots = [s for c in load(EPISODE/'storyboard.json')['scenes'] for s in c['shots']]
    keys = ['id','from','durationInFrames','narration','subtitles','voice','cueFrames']
    for old, new in zip(old_shots, shots[:17]):
        for key in keys: assert old[key] == new[key], (old['id'], key)
    assert shots[17]['from'] == PREFIX_FRAMES
    report.update(first17WordObjectsExact=True, first17ShotTimingAndCaptionsExact=True,
                  newTailFrom=shots[17]['from'], frames=words['durationFrames'],
                  audioSHA256=sha(EPISODE/'voice.wav'))
    save(EPISODE/'voice/ending-preservation.json', report)
    print('Preserved all 34 sentence PCM spans and 17 shot timing objects exactly.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tail-dir', type=Path, default=Path('/workspace/horse-ending-tail'))
    parser.add_argument('--baseline-wav', type=Path, default=Path('/workspace/horse-ending-before/voice.wav'))
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify: verify(args.baseline_wav)
    else: merge(args.tail_dir, args.baseline_wav)
