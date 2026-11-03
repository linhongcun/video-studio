#!/usr/bin/env python3
"""Read-only sentence cue check using the shared acoustic onset implementation."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import wave
import numpy as np

P = Path(__file__).resolve().parents[1]
ROOT = next(p for p in P.parents if (p/'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT/'episodes/_shared'))
from onset_rule import Rule

with wave.open(str(P/'voice.wav')) as source:
    rate = source.getframerate()
    samples = np.frombuffer(source.readframes(source.getnframes()), '<i2').astype(float)/32767
rule = Rule(samples, rate)
words = json.loads((P/'words.json').read_text())
board = json.loads((P/'storyboard.json').read_text())
shots = [shot for scene in board['scenes'] for shot in scene['shots']]
rows = []
for timed, shot in zip(words['shots'], shots):
    for index, sentence in enumerate(timed['sentences']):
        measured = rule.onset(sentence['startFrame'], min(sentence['endFrame'], sentence['startFrame']+30))
        assert measured['source'] == 'pause'
        assert abs(measured['onset']-sentence['onsetFrame']) < 1e-8
        target = shot['from']+shot['cueFrames']['sentences'][index]
        difference = target-measured['onset']
        assert -6 <= difference <= 2, (sentence['id'], difference)
        rows.append({'id':sentence['id'], 'shot':shot['id'], 'startFrame':sentence['startFrame'],
                     'endFrame':sentence['endFrame'], 'onsetFrame':measured['onset'],
                     'rule':measured['source']+'/'+measured['kind'],
                     'declaredSentenceCueAbsoluteFrame':target, 'cueMinusOnsetFrames':difference,
                     'withinMinus6Plus2':True})
assert len(rows) == 28
report = {
    'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'executor':'Codex P09 voice producer',
    'voiceSHA256':hashlib.sha256((P/'voice.wav').read_bytes()).hexdigest(),
    'wordsSHA256':hashlib.sha256((P/'words.json').read_bytes()).hexdigest(),
    'storyboardSHA256':hashlib.sha256((P/'storyboard.json').read_bytes()).hexdigest(),
    'sharedOnsetModuleSHA256':hashlib.sha256((ROOT/'episodes/_shared/onset_rule.py').read_bytes()).hexdigest(),
    'sentenceOnsets':len(rows), 'status':'passed-acoustic-sentence-cues', 'declaredTermLabels':0,
    'rows':rows,
    'limitations':[
        'All 28 acoustic sentence onsets and declared storyboard sentence cues were checked with the unchanged shared Rule.',
        'No interior word alignment, ASR, phonetic/semantic listening, or verification of actual rendered animation labels is claimed.',
        'label_onset_strict reports 0 declared term labels; this does not constitute 28 term-label checks.'
    ]
}
(P/'qa/voice-acoustic-onsets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sentences':len(rows), 'minCueMinusOnsetFrames':min(row['cueMinusOnsetFrames'] for row in rows),
                  'maxCueMinusOnsetFrames':max(row['cueMinusOnsetFrames'] for row in rows)}))
