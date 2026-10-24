#!/usr/bin/env python3
"""Set voice/cues.json onsetFrame from episodes/_shared/onset_rule.py (EP.14 voice/cues_rule.py).

Imports the shared rule, does not copy it. Same occurrence as onsets.py
(first in the shot). The previous char is the previous char in words.json
order. Keeps the ASR onset in asrOnsetFrame and records onsetSource. It can be
rerun: it starts again from asrOnsetFrame.

  python3 episodes/_shared/voice/cues_rule.py --dir EPDIR
"""
import json, os, re, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
sys.path.insert(0, str(common.SHARED)); import onset_rule as R

a, P = common.setup(__doc__)
assert R.selftest()
w = wave.open('../voice.wav'); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64)/32767
rule = R.Rule(x, sr); W = json.load(open('../words.json')); SEN = [s for q in W['shots'] for s in q['sentences']]; S = {s['id']: s for s in SEN}
C = json.load(open('cues.json')); mx = 0
for c in C:
    if 'asrOnsetFrame' in c: c['onsetFrame'] = c['asrOnsetFrame']
    s = S[c['sentence']]; t = ''.join(ch['ch'] for ch in s['chars']); key = re.sub(r'[^\w]', '', c['cue'].replace('(last)', ''))
    i = (t.rfind if c['cue'].endswith('(last)') else t.find)(key); assert i >= 0, c; ch = s['chars'][i]
    assert abs(ch['startFrame']-c['onsetFrame']) < 0.01, (c, ch)
    if i: ps, pe = s['chars'][i-1]['startFrame'], s['chars'][i-1]['endFrame']
    else:
        k = SEN.index(s); ps, pe = (SEN[k-1]['chars'][-1]['startFrame'], SEN[k-1]['chars'][-1]['endFrame']) if k else (None, None)
    r = R.Rule.onset(rule, ch['startFrame'], ch['endFrame'], ps, pe)
    c['asrOnsetFrame'] = ch['startFrame']; c['onsetFrame'] = round(float(r['onset']), 2); c['onsetSource'] = 'onset_rule:'+str(r.get('source', ''))
    mx = max(mx, abs(c['onsetFrame']-c['asrOnsetFrame']))
json.dump(C, open('cues.json', 'w'), ensure_ascii=False, indent=1)
print(len(C), 'cues; max |rule-asr|', round(mx, 2))
for c in C:
    if abs(c['onsetFrame']-c['asrOnsetFrame']) > 0.01: print(' ', c['shot'], c['cue'], c['asrOnsetFrame'], '->', c['onsetFrame'], c['onsetSource'])
