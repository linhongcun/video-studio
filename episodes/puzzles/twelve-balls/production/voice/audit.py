#!/usr/bin/env python3
"""Record this episode's measured signal facts; import shared cut and onset."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from onset_rule import Rule

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
write = lambda p, obj: p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
parser = argparse.ArgumentParser(__doc__)
parser.add_argument('--takes-only', action='store_true')
args = parser.parse_args()
voice = D / 'voice'
sents = read(voice / 'sents.json')
picks = read(voice / 'picks.json')
count = read(D / 'episode-config.json')['shotCount']
assert len(sents) == 2 * count == len({s['id'] for s in sents})
narrations = re.findall(r'^旁白：(.*)$', (D / 'script.md').read_text(), re.M)
assert ''.join(s['text'] for s in sents) == ''.join(narrations)
rows, flags = [], []
for sentence in sents:
    sid = sentence['id']
    take = picks[sid]
    path = voice / 'takes' / f'{sid}-{take}.wav'
    raw = path.with_name(path.stem + '.raw.wav')
    request = path.with_suffix('.txt.json')
    assert path.is_file() and raw.is_file() and read(request) == sentence['tts']
    source, sr = sf.read(path)
    assert sr == 48000 and source.ndim == 1
    clipped, tail = common.cut(common.load(str(path)))
    active = np.flatnonzero(np.abs(clipped) > .01)
    assert len(active)
    quiet = np.max(np.abs(clipped[:len(clipped)//480*480].reshape(-1, 480)), axis=1) <= .005
    runs = re.findall('1+', ''.join('1' if q else '0' for q in quiet))
    inner = max(map(len, runs), default=0) / 100
    risks = []
    if tail < .25:
        risks.append('throwaway tail below250ms')
    if inner >= .5:
        risks.append('source sentence silence at least500ms; review cue only')
    if np.any(np.abs(source) >= .9999):
        risks.append('source clipped sample')
    row = dict(id=sid, take=take, takeSHA256=sha(path), rawSHA256=sha(raw),
               requestSHA256=sha(request), sourceSamples=len(source), sourceRate=sr,
               sharedCutSamples=len(clipped), tailAfterLastGapSeconds=float(tail),
               cutLeadingAbove01Seconds=float(active[0]/sr),
               cutTrailingBelow01Seconds=float((len(clipped)-1-active[-1])/sr),
               cutMaxSilenceAt005Seconds=inner,
               sourcePeak=float(np.max(np.abs(source))), flags=risks)
    rows.append(row)
    if risks:
        flags.append(dict(id=sid, take=take, flags=risks))

report = dict(executor='Codex P06 voice producer',
              checkedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              stage='selected-takes' if args.takes_only else 'selected-takes-and-whole-track',
              exactNarrationAndRequestText=True, sentences=rows, flags=flags,
              sharedToolSHA256={str(p.relative_to(ROOT)): sha(p) for p in [
                  ROOT/'episodes/_shared/voice/common.py',
                  ROOT/'episodes/_shared/voice/build.py',
                  ROOT/'episodes/_shared/onset_rule.py']},
              asrModel='none', wordAlignment=False, fullSemanticListening=False,
              limitations=[
                  'Shared cut/onset are imported without copying their algorithms.',
                  'Signal checks do not establish spoken word or tone correctness. No ASR, phoneme alignment or complete semantic listening was performed.',
                  'Long internal silence is a review cue, not an established dropout.'])

if not args.takes_only:
    build = read(voice/'build.json')
    words = read(D/'words.json')
    board = read(D/'storyboard.json')
    audio, sr = sf.read(D/'voice.wav')
    assert sr == 48000 and audio.ndim == 1
    assert len(audio) == build['summary']['samples'] == build['summary']['frames']*1600
    assert sha(D/'voice.wav') == build['summary']['sha'] == words['audioSha256']
    assert words['scriptSha256'] == sha(D/'script.md')
    assert words['asrModel'] == 'none' and words['wordAlignment'] is False
    assert len(build['sentences']) == len(sents)
    assert len(words['shots']) == count
    assert all(len(s['sentences']) == 2 for s in words['shots'])
    assert [s['id'] for sh in words['shots'] for s in sh['sentences']] == [s['id'] for s in sents]
    public = D/'remotion/public/audio/voice.wav'
    assert not public.is_symlink() and (D/'voice.wav').read_bytes() == public.read_bytes()
    for sentence, built in zip(sents, build['sentences']):
        assert (sentence['id'], sentence['text'], sentence['tts'], picks[sentence['id']]) == (built['id'], built['text'], built['tts'], built['take'])
        fragment, rate = sf.read(voice/'sentences'/f"{sentence['id']}.wav")
        assert rate == sr and np.array_equal(audio[built['startSample']:built['endSample']], fragment)
    built = build['sentences']
    assert all(0 <= r['startSample'] < r['endSample'] <= len(audio) for r in built)
    assert all(x['endSample'] <= y['startSample'] for x, y in zip(built, built[1:]))
    gaps = [(0, built[0]['startSample'])] + [(x['endSample'], y['startSample']) for x, y in zip(built, built[1:])] + [(built[-1]['endSample'], len(audio))]
    assert all(0 <= a <= b <= len(audio) for a, b in gaps)
    assert all(np.max(np.abs(audio[a:b]), initial=0) == 0 for a, b in gaps)
    shots = [s for scene in board['scenes'] for s in scene['shots']]
    assert len(shots) == count and sum(s['durationInFrames'] for s in shots) == words['durationFrames']
    # Assembly uses exact int16 / 32767; reproduce the shared Rule input exactly.
    pcm, pcm_sr = sf.read(D/'voice.wav', dtype='int16')
    rule = Rule(pcm.astype(float)/32767, pcm_sr)
    onsets, timings = [], []
    for shot, ws in zip(shots, words['shots']):
        assert shot['from'] == ws['startFrame']
        for i, sentence in enumerate(ws['sentences']):
            measured = rule.onset(sentence['startFrame'], min(sentence['endFrame'], sentence['startFrame']+30))
            assert measured['source'] == 'pause' and abs(measured['onset']-sentence['onsetFrame']) < 1e-6
            cue = shot['from'] + shot['cueFrames']['sentences'][i]
            difference = cue - measured['onset']
            assert -6 <= difference <= 2
            onsets.append(dict(id=sentence['id'], onsetFrame=measured['onset'], cueAbsoluteFrame=cue,
                               cueMinusOnsetFrames=difference, rule=measured['source']+'/'+measured['kind']))
        timings.append(dict(id=shot['id'], slug=ws['id'], **{'from':shot['from']},
                            durationInFrames=shot['durationInFrames'], sentenceCueLocalFrames=shot['cueFrames']['sentences'],
                            sentenceOnsetLocalFrames=[s['onsetFrame']-shot['from'] for s in ws['sentences']],
                            sentenceLocalEndFrames=[s['localEnd'] for s in shot['voice']]))
    assert len(onsets) == len(sents)
    report.update(voiceSHA256=sha(D/'voice.wav'), scriptSHA256=sha(D/'script.md'),
                  wordsSHA256=sha(D/'words.json'), storyboardSHA256=sha(D/'storyboard.json'),
                  frames=build['summary']['frames'], samples=len(audio), seconds=len(audio)/sr,
                  actualIntegratedLUFS=common.lufs(audio.astype(np.float32)),
                  actualTruePeakDBTP=float(20*np.log10(np.max(np.abs(resample_poly(audio,4,1))))),
                  publicVoiceCopyByteIdentical=True, selectedSentencePCMMatchesWholeTrack=True,
                  silentGapPCMZero=True, silentIntervals=len(gaps), sentenceOnsets=onsets,
                  shotTimings=timings, sharedBuildFlags=build['summary']['inner_dropouts'],
                  declaredLabelCues=sum(len(s['elements']) for s in shots))

report['status'] = 'signal-flags-require-review' if flags else 'passed-signal-screening'
out = voice / ('selected-takes-audit.json' if args.takes_only else 'producer-audit.json')
write(out, report)
print(json.dumps(dict(status=report['status'], sentences=len(rows), flags=flags,
                      frames=report.get('frames'), report=str(out.relative_to(ROOT))), ensure_ascii=False))
