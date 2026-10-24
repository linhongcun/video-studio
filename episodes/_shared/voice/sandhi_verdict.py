#!/usr/bin/env python3
"""Per 一/不: F0 inside its own aligned span next to the tone sandhi expected from the next char (EP.14 voice/sandhi_verdict.py).

The expected tone comes from a small character list (EP.14's): 一 before
件项个页段遍次步样定下 -> yí, otherwise yì; 不 before 算太再会去是 -> bú,
otherwise bù; 能不能 -> neutral. Extend the lists for a new script. Output is
for a listening verdict.

  python3 episodes/_shared/voice/sandhi_verdict.py --dir EPDIR > voice/sandhi_verdict.log
"""
import json, os, sys
import numpy as np, parselmouth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__)
snd = parselmouth.Sound('../voice.wav'); p = snd.to_pitch_ac(time_step=0.005, pitch_floor=120, pitch_ceiling=500)
T = p.xs(); F = p.selected_array['frequency']; MED = float(np.median(F[F > 0]))
W = json.load(open('../words.json'))
for sh in W['shots']:
    for s in sh['sentences']:
        C = s['chars']
        for i, c in enumerate(C):
            if c['ch'] not in '一不': continue
            nx = C[i+1]['ch'] if i+1 < len(C) else ''
            pv = C[i-1]['ch'] if i else ''
            if c['ch'] == '不' and pv == '能' and nx == '能': exp = 'bu 轻声'
            elif c['ch'] == '不' and nx == '一': exp = 'bù 去声（后字「一」读 yí）'
            elif c['ch'] == '一': exp = 'yí 升' if nx in '件项个页段遍次步样定下' else 'yì 降'
            else: exp = 'bú 升' if nx in '算太再会去是' else 'bù 降'
            a_, b = c['startFrame']/30, c['endFrame']/30; m = (T >= a_) & (T <= b) & (F > 0); st = 12*np.log2(F[m]/MED)
            ctx = ''.join(x['ch'] for x in C[max(0, i-2):i+3])
            if len(st) < 3: print(f"{s['id']:22s} {ctx:6s} f{c['startFrame']:.0f}-{c['endFrame']:.0f} 期望 {exp}: 有声段不足"); continue
            n = len(st); five = [round(float(np.median(st[int(n*k/5):max(int(n*k/5)+1, int(n*(k+1)/5))])), 1) for k in range(5)]
            d = five[-1]-five[0]; pk = int(np.argmax(st)); tr = int(np.argmin(st))
            print(f"{s['id']:22s} {ctx:6s} f{c['startFrame']:.0f}-{c['endFrame']:.0f} {n*5}ms 期望 {exp:14s} 5pt={five} Δ={d:+.1f} max@{pk/n:.0%} min@{tr/n:.0%}")
