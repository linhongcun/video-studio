#!/usr/bin/env python3
"""P01 short ending: copy source PCM through frame 5580 and append silence.

No TTS, trimming algorithm, normalization, or onset algorithm is implemented
here. After this one revision operation, run the shared sentence assembler,
whole placement and checks, then --verify to audit preserved input sections.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import wave

import numpy as np

EPISODE = Path(__file__).resolve().parent
REVISION = EPISODE / 'revisions/short-ending'
ROOT = EPISODE.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import lufs


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path)) as audio:
        assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2)
        return audio.readframes(audio.getnframes())


def expected_sentences():
    script = (EPISODE / 'script.md').read_text()
    rows = []
    for number, slug, body in re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S):
        narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
        sentences = re.findall(r'[^。？！]+[。？！]', narration)
        assert len(sentences) == 2 and ''.join(sentences) == narration
        rows.extend((f'{int(number):02d}-{slug}-{i+1}', text) for i, text in enumerate(sentences))
    assert len(rows) == 32
    return rows


def preservation(baseline, current):
    source = load(REVISION / 'source.json')
    prefix_samples, final_samples = source['prefixFrames'] * 1600, source['frames'] * 1600
    assert current[:prefix_samples*2] == baseline[:prefix_samples*2]
    assert current[prefix_samples*2:] == bytes((final_samples-prefix_samples)*2)
    sentences = []
    for row in load(REVISION/'before-build.json')['sentences'][:32]:
        a, b = row['startSample']*2, row['endSample']*2
        assert b <= prefix_samples*2 and current[a:b] == baseline[a:b]
        sentences.append(dict(id=row['id'], startSample=row['startSample'], endSample=row['endSample'],
                              sha256=hashlib.sha256(current[a:b]).hexdigest(), exact=True))
    return dict(prefixFrames=source['prefixFrames'], prefixSamples=prefix_samples,
                prefixSHA256=hashlib.sha256(current[:prefix_samples*2]).hexdigest(),
                addedSilentFrames=source['holdFrames'], addedSilentSamples=final_samples-prefix_samples,
                prefixPCMExact=True, all32SentencePCMExact=True, sentences=sentences)


def shorten(baseline_wav):
    source = load(REVISION / 'source.json')
    assert sha(baseline_wav) == source['voiceSHA256'], 'Unexpected source WAV'
    assert source['prefixFrames'] + source['holdFrames'] == source['frames'] == 5618
    voice = EPISODE / 'voice'
    sents = load(voice/'sents.json')[:32]
    rows = copy.deepcopy(load(REVISION/'before-build.json')['sentences'][:32])
    expected = expected_sentences()
    assert [(s['id'],s['text']) for s in sents] == expected
    assert [(s['id'],s['text']) for s in rows] == expected
    baseline = pcm(baseline_wav)
    cutoff = source['prefixFrames'] * 1600
    result = baseline[:cutoff*2] + bytes(source['holdFrames']*1600*2)
    report = preservation(baseline, result)
    with wave.open(str(EPISODE/'voice.wav'),'wb') as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(48000); output.writeframes(result)
    signal = np.frombuffer(result,'<i2').astype(np.float32) / 32767
    splices = [dict(pair=f"{a['id']}->{b['id']}", lufs_diff=round(abs(a['lufs']-b['lufs']),2),
                    gapFrames=round((b['startSample']-a['endSample'])*30/48000,1))
               for a,b in zip(rows,rows[1:])]
    def edge(sample):
        return float(np.abs(np.diff(signal[max(0,sample-480):sample+480])).max())
    summary = dict(extraAfter={}, track_lufs=lufs(signal), peak=float(np.abs(signal).max()),
                   max_neighbour_lufs_diff=max(s['lufs_diff'] for s in splices),
                   max_join_sample_jump=max(max(edge(s['startSample']),edge(s['endSample'])) for s in rows),
                   inner_dropouts=[s['id'] for s in rows if s['maxInnerSilenceS'] >= .5],
                   samples=len(signal),frames=source['frames'],seconds=source['frames']/30,
                   sha=sha(EPISODE/'voice.wav'))
    assert len(signal) == source['frames']*1600
    save(voice/'build.json',dict(summary=summary,sentences=rows,splices=splices,
                               assembly='Original PCM prefix plus 37 silent frames; no TTS or normalization.'))
    save(voice/'sents.json',sents)
    picks=load(voice/'picks.json');save(voice/'picks.json',{s['id']:picks[s['id']] for s in sents})
    old_provenance=voice/'input-provenance.json'
    if old_provenance.exists() and not (voice/'proof-ending-input-provenance.json').exists():
        (voice/'proof-ending-input-provenance.json').write_bytes(old_provenance.read_bytes())
    save(old_provenance,dict(scriptSHA256=sha(EPISODE/'script.md'),planSHA256=sha(EPISODE/'plan.json'),
         sentenceCount=32,method='Keep the first 32 sentence PCM spans unchanged; cut at frame 5581 and append 37 silent frames.',
         sourceVoiceSHA256=source['voiceSHA256'],sourceVersion=source['version'],
         originalGeneration='original-input-provenance.json',operation='shorten_voice.py'))
    report.update(sourceVoiceSHA256=source['voiceSHA256'],audioSHA256=summary['sha'],
                  frames=source['frames'],samples=len(signal),noNewTTS=True,noNormalization=True,
                  finalTailSeconds=(len(signal)-rows[-1]['endSample'])/48000)
    save(voice/'short-ending-composition.json',report)
    print(json.dumps(summary,ensure_ascii=False))


def verify(baseline_wav):
    source=load(REVISION/'source.json');assert sha(baseline_wav)==source['voiceSHA256']
    report=preservation(pcm(baseline_wav),pcm(EPISODE/'voice.wav'))
    words,old_words=load(EPISODE/'words.json'),load(REVISION/'before-words.json')
    assert len(words['shots'])==16 and words['durationFrames']==5618
    assert words['shots'][:15]==old_words['shots'][:15]
    assert words['shots'][15]['sentences']==old_words['shots'][15]['sentences']
    assert (words['shots'][15]['startFrame'],words['shots'][15]['endFrame'],words['shots'][15]['durationFrames'])==(5204,5618,414)
    flatten=lambda obj:[s for scene in obj['scenes'] for s in scene['shots']]
    shots,old_shots=flatten(load(EPISODE/'storyboard.json')),flatten(load(REVISION/'before-storyboard.json'))
    for old,new in zip(old_shots[:15],shots[:15]):
        for key in ['id','from','durationInFrames','narration','subtitles','voice','cueFrames']:
            assert old[key]==new[key],(old['id'],key)
    assert (shots[15]['from'],shots[15]['durationInFrames'])==(5204,414)
    assert shots[15]['voice']==old_shots[15]['voice']
    report.update(first15WordObjectsExact=True,first15ShotTimingAndCaptionsExact=True,
                  all32SentenceTimingAndPCMExact=True,lastShotFrom=5204,lastShotFrames=414,
                  frames=5618,audioSHA256=sha(EPISODE/'voice.wav'))
    save(EPISODE/'voice/short-ending-preservation.json',report)
    print('All 32 sentence PCM spans and timing retained; first 15 shots retained exactly.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-wav',type=Path,default=Path('/workspace/horse-short-before/voice.wav'))
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.verify:verify(args.baseline_wav)
    else:shorten(args.baseline_wav)
