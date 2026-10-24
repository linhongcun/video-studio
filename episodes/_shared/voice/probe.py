#!/usr/bin/env python3
"""Key-word acoustic probe on ../voice.wav (EP.14 voice/probe.py).

stdin lines: "<label> <sentenceId> <substring> <occurrence 0-based>", e.g.
"降级 11-term-degrade-1 降级 0". Prints aligned chars, voiced runs (5-pt F0 in
semitones re track median, F1/F2 at 25/50/75 %, intensity nuclei) and unvoiced
>3 kHz frication runs. For listening verdicts only.

  python3 episodes/_shared/voice/probe.py --dir EPDIR < voice/probe.in > voice/probe.log
"""
import json, os, sys
import numpy as np, parselmouth, scipy.signal as ss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a_, P = common.setup(__doc__)
snd = parselmouth.Sound('../voice.wav'); x = snd.values[0]; sr = snd.sampling_frequency
p = snd.to_pitch_ac(time_step=0.005, pitch_floor=120, pitch_ceiling=500); fo = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5, maximum_formant=5500)
it = snd.to_intensity(minimum_pitch=120, time_step=0.005); hi = ss.sosfilt(ss.butter(6, 3000, 'hp', fs=sr, output='sos'), x)
F = p.selected_array['frequency']; T = p.xs(); MED = float(np.median(F[F > 0]))
W = json.load(open('../words.json')); S = {s['id']: s for q in W['shots'] for s in q['sentences']}
for line in sys.stdin:
    if not line.strip(): continue
    lab, sid, sub, occ = line.split(); C = S[sid]['chars']; t = ''.join(c['ch'] for c in C); i = -1
    for _ in range(int(occ)+1): i = t.find(sub, i+1)
    cs = C[i:i+len(sub)]; a = (cs[0]['startFrame']-3)/30; b = (cs[-1]['endFrame']+3)/30
    print(f"## {lab} {sid} 「{sub}」 chars:"+' '.join(f"{c['ch']}{c['startFrame']:.0f}" for c in cs)+f" end{cs[-1]['endFrame']:.0f}")
    idx = np.where((T >= a) & (T < b) & (F > 0))[0]; runs = [r for r in np.split(idx, np.where(np.diff(idx) > 1)[0]+1) if len(r) >= 3] if len(idx) else []
    ev = []
    for r in runs:
        t0, t1 = T[r[0]], T[r[-1]]; st = 12*np.log2(F[r]/MED); n = len(st)
        five = [round(float(np.median(st[int(n*k/5):max(int(n*k/5)+1, int(n*(k+1)/5))])), 1) for k in range(5)]
        tt = np.arange(t0, t1, 0.005); I = np.nan_to_num(np.array([it.get_value(q) for q in tt]))
        pk, _ = ss.find_peaks(np.convolve(I, np.ones(5)/5, 'same'), prominence=2, distance=14) if len(tt) > 5 else ([], 0)
        fm = lambda q: (int(fo.get_value_at_time(1, q)), int(fo.get_value_at_time(2, q)))
        ev.append((t0, f"  V f{t0*30:.1f}-{t1*30:.1f} ({(t1-t0)*1000:.0f}ms) 5pt={five} F1F2@25/50/75={fm(t0+(t1-t0)*.25)},{fm(t0+(t1-t0)*.5)},{fm(t0+(t1-t0)*.75)} nuclei={len(pk)}"))
    q = a; cur = None
    while q < b+0.005:
        s = hi[int(q*sr):int((q+0.005)*sr)]; db = 20*np.log10(np.sqrt(np.mean(s**2))+1e-9) if len(s) else -99; v = p.get_value_at_time(q+0.0025)
        if db > -40 and not v == v: cur = cur or [q, q, []]; cur[1] = q; cur[2].append(db)
        else:
            if cur and cur[1]-cur[0] >= 0.02: ev.append((cur[0], f"  N f{cur[0]*30:.1f}-{cur[1]*30:.1f} ({(cur[1]-cur[0])*1000:.0f}ms) peak {max(cur[2]):.0f}dB"))
            cur = None
        q += 0.005
    for _, e in sorted(ev): print(e)
