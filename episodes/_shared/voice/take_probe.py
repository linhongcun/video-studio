#!/usr/bin/env python3
"""Probe one substring inside individual takes (EP.14 voice/take_probe.py).

Whisper word timestamps on the cut take (decimated 48k->16k by [::3], as in
EP.14), difflib-aligned to the script chars, then 5-pt F0 (semitones re take
median) and F2 of the voiced runs around SUBSTRING. Use for words ASR keeps
mishearing (EP.14: 卫衣→唯一, 架构/加购).

  python3 episodes/_shared/voice/take_probe.py --dir EPDIR 卫衣 takes/01-hook-1-*.wav > tp_x.log
"""
import json, os, re, difflib, sys
import numpy as np, parselmouth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

def args(ap):
    ap.add_argument('sub'); ap.add_argument('takes', nargs='+')
A, P = common.setup(__doc__, args)
q = P['asr']; m = common.whisper(P)
S = {s['id']: s['text'] for s in json.load(open('sents.json'))}; sub = A.sub
for f in A.takes:
    sid = re.sub(r'-[a-z0-9]+\.wav$', '', f.split('/')[-1]); y, _ = common.cut(common.load(f))
    x = np.concatenate([np.zeros(4800, np.float32), y[::3], np.zeros(4800, np.float32)])
    seg, _ = m.transcribe(x, language=q['language'], beam_size=q['beam'], condition_on_previous_text=False, word_timestamps=True, initial_prompt=q['initialPrompt'])
    ac = []; at = []; h = ''
    for g in seg:
        h += g.text
        for w in g.words:
            cs = [c for c in w.word.strip() if re.match(r'[\u4e00-\u9fffA-Za-z0-9]', c)]; n = max(1, len(cs))
            for k, c in enumerate(cs): ac.append(c); at.append((w.start-.3+(w.end-w.start)*k/n, w.start-.3+(w.end-w.start)*(k+1)/n))
    st_ = re.sub(r'[^\u4e00-\u9fff]', '', S[sid]); T_ = [None]*len(st_)
    for a, b, n in difflib.SequenceMatcher(None, st_, ''.join(ac), autojunk=False).get_matching_blocks():
        for k in range(n): T_[a+k] = at[b+k]
    i = st_.find(sub); span = [t for t in T_[i:i+len(sub)] if t]
    if not span:
        pre = [t for t in T_[:i] if t]; post = [t for t in T_[i+len(sub):] if t]   # digits: locate by neighbours
        if pre and post: span = [(pre[-1][1], pre[-1][1]), (post[0][0], post[0][0])]
        else: print(f.split('/')[-1], 'not aligned |', h, flush=True); continue
    a, b = span[0][0]-0.1, span[-1][1]+0.1
    snd = parselmouth.Sound(y.astype(np.float64), 48000); p = snd.to_pitch_ac(time_step=0.005, pitch_floor=120, pitch_ceiling=500); fo = snd.to_formant_burg(time_step=0.005, max_number_of_formants=5, maximum_formant=5500)
    F = p.selected_array['frequency']; T = p.xs(); MED = np.median(F[F > 0])
    idx = np.where((T >= a) & (T < b) & (F > 0))[0]; runs = [r for r in np.split(idx, np.where(np.diff(idx) > 1)[0]+1) if len(r) >= 3] if len(idx) else []
    out = []
    for r in runs:
        st = 12*np.log2(F[r]/MED); n = len(st); five = [round(float(np.median(st[int(n*k/5):max(int(n*k/5)+1, int(n*(k+1)/5))])), 1) for k in range(5)]
        f2 = [int(fo.get_value_at_time(2, T[r[0]]+(T[r[-1]]-T[r[0]])*q_)) for q_ in (.25, .5, .75)]
        out.append(f"V{T[r[0]]:.2f}-{T[r[-1]]:.2f} {five} F2={f2}")
    print(f.split('/')[-1], f'「{sub}」 win {a:.2f}-{b:.2f}', '|', ' ; '.join(out), '| ASR:', h, flush=True)
