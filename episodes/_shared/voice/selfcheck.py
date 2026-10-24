#!/usr/bin/env python3
"""Check the voice outputs (EP.14 voice/selfcheck.py, plus an exit code).

Prints the shot table (marks shots < minShotFrames), re-derives every cue onset
with episodes/_shared/onset_rule.py and checks cues.json is within -6..+2
frames, and lists sentence ASR mismatches for the listening pass. Exit 1 if
voice.wav length != words.json durationFrames, any cue is outside the window or
not found, or a shot other than the last is shorter than minShotFrames
(build.py does not lengthen the last shot either; it is still marked <MINF!). ASR mismatches do not fail;
a person or agent has to judge them.

  python3 episodes/_shared/voice/selfcheck.py --dir EPDIR
"""
import json, os, re, sys, difflib
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
sys.path.insert(0, str(common.SHARED)); import onset_rule as R

a, P = common.setup(__doc__)
MINF = P['minShotFrames'] or 0
print('onset_rule selftest', R.selftest())
x, sr = sf.read('../voice.wav'); W = json.load(open('../words.json')); C = json.load(open('cues.json')); B = json.load(open('build.json'))
print('frames', len(x)*30/sr, 'durationFrames', W['durationFrames'], 'sec', len(x)/sr)
rule = R.Rule(x, sr); S = {s['id']: s for q in W['shots'] for s in q['sentences']}
print('shot table:'); short = []
for q in W['shots']:
    if q['durationFrames'] < MINF and q is not W['shots'][-1]: short.append(q['id'])  # build.py exempts the last shot too
    print(f"  {q['id']:22s} {q['startFrame']:5d}-{q['endFrame']:5d} ({q['durationFrames']}f {q['durationFrames']/30:.2f}s){f'  <{MINF}!' if q['durationFrames'] < MINF else ''}")
bad = []; mx = 0
for c in C:
    s = S[c['sentence']]; ch = s['words']; txt = ''.join(w['w'] for w in ch)
    key = re.sub(r'[^\w]', '', c['cue']); i = txt.find(key)
    if i < 0: bad.append(('notfound', c['cue'])); continue
    p = ch[i-1] if i > 0 else None
    r = rule.onset(ch[i]['startFrame'], ch[i]['endFrame'], p['startFrame'] if p else None, p['endFrame'] if p else None)
    d = c['onsetFrame']-r['onset']; mx = max(mx, abs(d))
    if not (-6 <= d <= 2): bad.append((c['cue'], c['onsetFrame'], r['onset'], round(d, 2)))
print('cues', len(C), 'max |cue-rule|', round(mx, 2), 'outside -6..+2:', bad)
norm = lambda t: re.sub(r'[，。？、：“”,.?!\s]', '', t)
print('sentence ASR mismatches:')
for r in B['sentences']:
    a_ = norm(S[r['id']]['asr']); t = norm(r['text'])
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, t, a_, autojunk=False).get_opcodes():
        if op != 'equal': print('  ', r['id'], op, repr(t[i1:i2]), '->', repr(a_[j1:j2]))
ok = abs(len(x)*30/sr-W['durationFrames']) < 1e-6 and not bad and not short
print('selfcheck', 'ok' if ok else 'FAIL', 'short shots:', short)
sys.exit(0 if ok else 1)
