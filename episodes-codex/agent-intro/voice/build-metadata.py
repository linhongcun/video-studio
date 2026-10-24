"""Write sentence-level timing from the shared build output and acoustic Rule.

This does not synthesize, cut, place, or change audio. Interior character entries
are explicit sentence envelopes for checker compatibility, not word alignment.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from onset_rule import Rule


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


build = json.loads((D / 'voice/build.json').read_text())
raw_plan = json.loads((D / 'content-plan.json').read_text())
plan = raw_plan if isinstance(raw_plan, list) else raw_plan['shots']
plan_by_number = {int(str(p['id']).split('-')[0]): p for p in plan}
with wave.open(str(D / 'voice.wav')) as stream:
    sr = stream.getframerate()
    assert sr == 48000 and stream.getnchannels() == 1 and stream.getsampwidth() == 2
    samples = np.frombuffer(stream.readframes(stream.getnframes()), '<i2').astype(float) / 32767
assert len(samples) == build['summary']['frames'] * 1600
rule = Rule(samples, sr)
shots = []
for row in build['sentences']:
    if not shots or shots[-1]['id'] != row['shot']:
        shots.append(dict(id=row['shot'], sentences=[]))
    onset = rule.onset(row['startFrame'], min(row['endFrame'], row['startFrame'] + 30))
    assert onset['source'] == 'pause', (row['id'], onset)
    text = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9.]', '', row['text'])
    chars = [dict(ch=ch, startFrame=onset['onset'], endFrame=row['endFrame'],
                  timingUnit='sentence envelope', measuredOnset=(i == 0),
                  source='TTS sentence boundary; no interior character alignment')
             for i, ch in enumerate(text)]
    shots[-1]['sentences'].append(dict(
        id=row['id'], text=row['text'], take=row['take'],
        startFrame=row['startFrame'], endFrame=row['endFrame'], onsetFrame=onset['onset'],
        acousticOnset=onset, asr='', asrCoverage=None, chars=chars,
        words=[dict(w=text, startFrame=onset['onset'], endFrame=row['endFrame'])],
        note='Only sentence onset is measured; character entries are full-sentence envelopes.'))
assert len(shots) == len(plan)
for i, shot in enumerate(shots):
    first, last = shot['sentences'][0], shot['sentences'][-1]
    shot.update(onsetFrame=first['onsetFrame'], speechStartFrame=first['startFrame'],
                speechEndFrame=last['endFrame'],
                startFrame=0 if i == 0 else math.floor(first['startFrame']))
for i, shot in enumerate(shots):
    shot['endFrame'] = shots[i + 1]['startFrame'] if i + 1 < len(shots) else build['summary']['frames']
    shot['durationFrames'] = shot['endFrame'] - shot['startFrame']
words = dict(
    script='script.md', scriptSha256=sha(D / 'script.md'), fps=30,
    audio='voice.wav', audioSha256=sha(D / 'voice.wav'), durationFrames=build['summary']['frames'],
    asrModel='none', wordAlignment=False,
    timingMethod='Measured TTS sentence boundaries and shared acoustic onset Rule; not ASR.',
    shots=shots,
    onsetTable=[dict(shot=s['id'], sentence=q['id'], onsetFrame=q['onsetFrame'],
                     source='acoustic sentence onset') for s in shots for q in s['sentences']])
save(D / 'words.json', words)
cues = []
for shot in shots:
    number = int(shot['id'].split('-')[0])
    shot['cueFrames'] = dict(sentences=[q['onsetFrame'] - shot['startFrame'] for q in shot['sentences']], labels={})
    for cfg in plan_by_number[number].get('cues', []):
        sentence = shot['sentences'][cfg['sentence']]
        term = cfg['term']
        assert sentence['text'].startswith(term), (shot['id'], term, sentence['text'])
        local_onset = sentence['onsetFrame'] - shot['startFrame']
        shot['cueFrames']['labels'][term] = max(1, math.floor(local_onset) - 2)
        cues.append(dict(shot=shot['id'], cue=term, sentence=sentence['id'],
                         onsetFrame=sentence['onsetFrame']))
save(D / 'voice/cues.json', cues)
save(D / 'voice/cue_tests.json', [[q['shot'], q['cue']] for q in cues])
save(D / 'voice/shot_frames.json', dict(fps=30, durationFrames=words['durationFrames'],
                                      audioSha256=words['audioSha256'], shots=shots))
print(json.dumps(dict(shots=len(shots), sentences=len(build['sentences']),
                      frames=words['durationFrames'], cues=len(cues),
                      audioSha256=words['audioSha256'], scriptSha256=words['scriptSha256'])))
