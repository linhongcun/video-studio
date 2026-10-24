#!/usr/bin/env python3
"""Picked takes -> ../voice.wav, voice/sentences/*.wav, voice/build.json (EP.14 voice/build.py).

Per sentence: cut the "好。" tail, trim, normalize to sentenceLufs (-21).
Lay out: lead 0.30 s, 0.35 s inside a shot, 0.70 s between shots (+ extraAfter[shot]),
tail 0.60 s. minShotFrames (225 = 7.5 s): a shot runs from its first sentence start
(floored to a frame; shot 1 from 0) to the next shot's start. When a shot is short,
silence is added after it, up to minShotFrames + 1 frame. Speech rate is not changed. Pad to a whole
frame, bring the track to trackLufs (-16), true-peak limit to tpCeilingDb (-1.4 dBTP,
4x oversampled). Writes 16-bit 48 kHz mono. Deterministic for the same takes and the
same ffmpeg (ebur128) build.

Inputs in EPDIR/voice: sents.json, picks.json ({"sid": "take"}, default "a"),
takes/{sid}-{take}.wav.

  python3 episodes/_shared/voice/build.py --dir EPDIR
"""
import json, os, re, wave, hashlib, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import load, lufs, cut

a, P = common.setup(__doc__)
SR = 48000; FPS = 30; GAP_IN = P['gapIn']; GAP_SHOT = P['gapShot']; LEAD = P['lead']; TAIL = P['tail']
EXTRA_AFTER = dict(P['extraAfter'])
S = json.load(open('sents.json')); PK = json.load(open('picks.json')) if os.path.exists('picks.json') else {}
rows = []; clips = {}
for s in S:
    k = PK.get(s['id'], 'a'); y, tail = cut(load(f"takes/{s['id']}-{k}.wav"))
    nz = np.where(np.abs(y) > 1e-4)[0]; y = y[:nz[-1]+1]; y *= 10**((P['sentenceLufs']-lufs(y))/20)
    clips[s['id']] = y; rows.append(dict(s, take=k, tailCut=round(tail, 2)))
MINF = P['minShotFrames']
def layout():
    pos = int(LEAD*SR); out = []
    for i, r in enumerate(rows):
        g = 0
        if i: g = GAP_IN if rows[i-1]['shot'] == r['shot'] else GAP_SHOT+EXTRA_AFTER.get(rows[i-1]['shot'], 0); pos += int(round(g*SR))
        out.append((pos, g)); pos += len(clips[r['id']])
    return out, pos+int(TAIL*SR)
for _ in range(30 if MINF else 0):
    L, end = layout(); st = {}
    for r, (p, g) in zip(rows, L): st.setdefault(r['shot'], p)
    ks = list(st); ch = False
    for j, k in enumerate(ks):
        a_ = 0 if j == 0 else int(np.floor(st[k]*FPS/SR)); b = int(np.floor(st[ks[j+1]]*FPS/SR)) if j+1 < len(ks) else int(np.ceil(end/(SR/FPS)))
        if b-a_ < MINF and j+1 < len(ks): EXTRA_AFTER[k] = round(EXTRA_AFTER.get(k, 0)+(MINF+1-(b-a_))/FPS, 4); ch = True
    if not ch: break
print('EXTRA_AFTER', EXTRA_AFTER)
L, end = layout(); parts = [np.zeros(int(LEAD*SR), np.float32)]; pos = int(LEAD*SR)
for i, (r, (p, g)) in enumerate(zip(rows, L)):
    if i: parts.append(np.zeros(p-pos, np.float32)); r['gapBefore'] = round(g, 4)
    y = clips[r['id']]; r['startSample'] = p; pos = p+len(y); r['endSample'] = pos; parts.append(y)
parts.append(np.zeros(int(TAIL*SR), np.float32)); tr = np.concatenate(parts)
N = int(np.ceil(len(tr)/(SR/FPS)))*SR//FPS; tr = np.pad(tr, (0, N-len(tr)))
g = 10**((P['trackLufs']-lufs(tr))/20); tr *= g
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d
def tp(x): return float(np.abs(resample_poly(x, 4, 1)).max())
CEIL = 10**(P['tpCeilingDb']/20)
for _ in range(8):
    if 20*np.log10(tp(tr)) <= P['tpStopDb']: break
    o = np.abs(resample_poly(tr, 4, 1)).reshape(-1, 4).max(1)[:len(tr)]
    gn = np.minimum(1.0, CEIL/np.maximum(o, 1e-9))
    gn = minimum_filter1d(gn, size=int(0.004*SR)+1)
    gn = uniform_filter1d(gn, size=int(0.003*SR)+1)
    gn = np.minimum(gn, minimum_filter1d(np.minimum(1.0, CEIL/np.maximum(o, 1e-9)), size=3))
    tr = (tr*gn).astype(np.float32); tr *= 10**((P['trackLufs']-lufs(tr))/20)
print('truepeak_dbtp_internal', round(20*np.log10(tp(tr)), 2))
os.makedirs('sentences', exist_ok=True)
for r in rows:
    y = tr[r['startSample']:r['endSample']]
    w = wave.open(f"sentences/{r['id']}.wav", 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1)*32767).astype('<i2').tobytes()); w.close()
    r['lufs'] = round(lufs(y), 2); r['startFrame'] = round(r['startSample']*FPS/SR, 2); r['endFrame'] = round(r['endSample']*FPS/SR, 2)
w = wave.open('../voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(tr, -1, 1)*32767).astype('<i2').tobytes()); w.close()
sp = [dict(pair=f"{a_['id']}->{b['id']}", lufs_diff=round(abs(a_['lufs']-b['lufs']), 2), gapFrames=round((b['startSample']-a_['endSample'])*FPS/SR, 1)) for a_, b in zip(rows, rows[1:])]
def edge(s): return float(np.abs(np.diff(tr[max(0, s-480):s+480])).max())
# pops: max sample-to-sample jump in 10 ms windows around every join
jump = max(max(edge(r['startSample']), edge(r['endSample'])) for r in rows)
# gaps inside sentences (>0.5 s silence = dropout)
inner = []
for r in rows:
    y = tr[r['startSample']:r['endSample']]; fr = np.abs(y[:len(y)//480*480]).reshape(-1, 480).max(1) > 0.005; run = 0; mx = 0
    for f in fr: run = 0 if f else run+1; mx = max(mx, run)
    r['maxInnerSilenceS'] = mx/100
    if mx >= 50: inner.append(r['id'])
summ = dict(extraAfter=EXTRA_AFTER, track_lufs=lufs(tr), peak=float(np.abs(tr).max()), max_neighbour_lufs_diff=max(q['lufs_diff'] for q in sp), max_join_sample_jump=jump, inner_dropouts=inner, samples=N, frames=N*FPS//SR, seconds=N/SR, sha=hashlib.sha256(open('../voice.wav', 'rb').read()).hexdigest())
json.dump(dict(summary=summ, sentences=rows, splices=sp), open('build.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False))
for r in rows: print(r['id'], r['startFrame'], r['endFrame'], r['lufs'], r['tailCut'], r['maxInnerSilenceS'])
