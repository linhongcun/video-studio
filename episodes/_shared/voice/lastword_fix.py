#!/usr/bin/env python3
"""Move a late last character to the energy valley; rewrites ../words.json (EP.14 voice/lastword_fix.py).

Whisper often puts the LAST character of a sentence late (start near the speech
end). If a sentence's last char starts within 3 frames of speech end, or on
near-silence (RMS <= 0.02 over its first 3 frames), its start moves to the
deepest energy valley between previous char start + 2 f and speech end - 3 f.
Logged in words.json lastWordFix. Run once, right after onsets.py.

  python3 episodes/_shared/voice/lastword_fix.py --dir EPDIR
"""
import json, os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__)
w = wave.open('../voice.wav'); x = np.frombuffer(w.readframes(w.getnframes()), '<i2')/32767
W = json.load(open('../words.json')); log = []
def env(a, b):
    s = x[int(a*1600):int(b*1600)]; s = s[:len(s)//160*160].reshape(-1, 160); e = np.sqrt((s**2).mean(1))
    return np.convolve(e, np.ones(3)/3, 'same')  # 1/300 s hop, smoothed
for sh in W['shots']:
    for s in sh['sentences']:
        c = s['chars']; lw, pw = c[-1], c[-2]
        seg = np.abs(x[int(s['startFrame']*1600):int(s['endFrame']*1600)]); fr = seg[:len(seg)//480*480].reshape(-1, 480).max(1)
        spEnd = round(s['startFrame']+np.where(fr > 0.01)[0][-1]*0.3+0.3, 1)
        s0 = x[int(lw['startFrame']*1600):int((lw['startFrame']+3)*1600)]; r = float(np.sqrt((s0**2).mean()))
        if lw['startFrame'] < spEnd-3 and r > 0.02: continue
        a_ = pw['startFrame']+2; b = spEnd-3
        if b <= a_: continue
        e = env(a_, b); i = int(np.argmin(e)); new = round(a_+i*160/1600, 1)
        log.append(dict(id=s['id'], ch=lw['ch'], old=lw['startFrame'], new=new, speechEnd=spEnd))
        lw['startFrame'] = new; pw['endFrame'] = new; lw['endFrame'] = max(spEnd, new+1)
        for t in s['words']:
            if t['w'] == lw['ch'] and t is s['words'][-1]: t['startFrame'] = new; t['endFrame'] = lw['endFrame']
            if t is s['words'][-2] and t['w'].endswith(pw['ch']): t['endFrame'] = new
W['note'] += '；句末最后一字若 ASR 起点落在语音结束前 3 帧内或静音上，改用前一字与语音结束之间的能量谷（voice/lastword_fix.py）'
W['lastWordFix'] = log
json.dump(W, open('../words.json', 'w'), ensure_ascii=False, indent=1)
for l in log: print(l)
