#!/usr/bin/env python3
"""List F0 (5 points, semitones re track median) and F2 for every 一 or 不 (EP.14 voice/sandhi_ch.py).

For each occurrence of CH: voiced runs from its aligned start - 5 f to the next
char end + 3 f. Output is for a listening verdict, not a pass/fail.

  python3 episodes/_shared/voice/sandhi.py --dir EPDIR [一|不] > voice/sandhi_yi.log
"""
import json, os, sys
import numpy as np, parselmouth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__, lambda ap: ap.add_argument('ch', nargs='?', default='一'))
CH = a.ch
snd = parselmouth.Sound('../voice.wav'); p = snd.to_pitch_ac(time_step=0.005, pitch_floor=120, pitch_ceiling=500)
fo = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5, maximum_formant=5500)
T = p.xs(); F = p.selected_array['frequency']; MED = float(np.median(F[F > 0]))
W = json.load(open('../words.json'))
for sh in W['shots']:
    for s in sh['sentences']:
        C = s['chars']
        for i, c in enumerate(C):
            if c['ch'] != CH: continue
            nx = C[i+1] if i+1 < len(C) else None; ctx = ''.join(x['ch'] for x in C[max(0, i-2):i+3])
            a_ = (c['startFrame']-5)/30; b = ((nx or c)['endFrame']+3)/30
            idx = np.where((T >= a_) & (T <= b) & (F > 0))[0]
            runs = [r for r in np.split(idx, np.where(np.diff(idx) > 1)[0]+1) if len(r) >= 4] if len(idx) else []
            out = []
            for r in runs:
                st = 12*np.log2(F[r]/MED); n = len(st); five = [round(float(np.median(st[int(n*k/5):max(int(n*k/5)+1, int(n*(k+1)/5))])), 1) for k in range(5)]
                f2 = [int(fo.get_value_at_time(2, T[r[0]]+(T[r[-1]]-T[r[0]])*q)) for q in (.3, .5, .7)]
                out.append(f"f{T[r[0]]*30:.0f}-{T[r[-1]]*30:.0f} 5pt={five} F2={f2}")
            print(f"{s['id']:22s} {ctx:6s} {CH}@f{c['startFrame']:.0f} || "+' || '.join(out))
