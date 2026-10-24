#!/usr/bin/env python3
"""build.json + asr.json + ../voice.wav -> ../words.json and voice/cues.json (EP.14 voice/onsets.py).

Script characters get times from ASR word timestamps aligned with difflib
(unmatched characters are interpolated). The first character of each sentence is
clamped to the energy onset (first 1/300 s block > 0.02). Shot slots: each shot
starts at its first sentence start, floored to a frame (shot 1 at 0), and ends at
the next shot's start. The last shot ends at durationFrames. Cue onsets come from
the cue word's own first character in its own shot; a cue that ends its sentence
is flagged. cues.json then goes through lastword_fix.py and cues_rule.py.

Known limit (unchanged from EP.14): a sentence that spans two shots
(prep.py spansShots) makes this script fail; end every shot with 。？！.

  python3 episodes/_shared/voice/onsets.py --dir EPDIR
"""
import json, re, difflib, hashlib, math, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a_, P = common.setup(__doc__)
FPS = 30; SR = 48000
B = json.load(open('build.json')); A = {r['id']: r for r in json.load(open('asr.json'))}
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', '../voice.wav', '-f', 's16le', '-'], capture_output=True).stdout, '<i2').astype(np.float32)/32767
def energy_onset(s, e):
    y = np.abs(x[s:e]); fr = y[:len(y)//160*160].reshape(-1, 160).max(1); i = np.argmax(fr > 0.02); return (s+i*160)/SR*FPS
isc = lambda c: bool(re.match(r'[\u4e00-\u9fffA-Za-z0-9.]', c))
def align(r):
    txt = r['text']; W = A[r['id']]['words']; ac = []; at = []
    for w in W:
        cs = [c for c in w['w'] if isc(c)]; n = max(1, len(cs))
        for k, c in enumerate(cs):
            ac.append(c.upper()); at.append((w['startFrame']+(w['endFrame']-w['startFrame'])*k/n, w['startFrame']+(w['endFrame']-w['startFrame'])*(k+1)/n))
    sc = [(i, c) for i, c in enumerate(txt) if isc(c)]; st = ''.join(c.upper() for _, c in sc)
    T = [None]*len(sc)
    for a, b, n in difflib.SequenceMatcher(None, st, ''.join(ac), autojunk=False).get_matching_blocks():
        for k in range(n): T[a+k] = at[b+k]
    # interpolate unmatched: half of the gap after the previous matched char
    for i in range(len(T)):
        if T[i] is None:
            p = next((T[j][1] for j in range(i-1, -1, -1) if T[j]), r['startFrame']); q = next((T[j][0] for j in range(i+1, len(T)) if T[j]), r['endFrame'])
            T[i] = (p, p+(q-p)/2)
    return [dict(ch=c, startFrame=round(t[0], 1), endFrame=round(t[1], 1)) for (_, c), t in zip(sc, T)]
def tokens(chars, txt):
    # group into words: consecutive latin/digits = one token, CJK char = one token
    out = []; buf = None
    for c in chars:
        if re.match(r'[A-Za-z0-9.]', c['ch']):
            if buf and re.match(r'[A-Za-z0-9.]', buf['w'][-1]): buf['w'] += c['ch']; buf['endFrame'] = c['endFrame']; continue
            buf = dict(w=c['ch'], startFrame=c['startFrame'], endFrame=c['endFrame']); out.append(buf)
        else: buf = dict(w=c['ch'], startFrame=c['startFrame'], endFrame=c['endFrame']); out.append(buf)
    return out
shots = {}; rows = B['sentences']
for r in rows:
    ch = align(r); on = energy_onset(r['startSample'], r['endSample'])
    # ASR word starts lag/lead the real onset slightly; clamp first char to the measured energy onset
    if ch: ch[0]['startFrame'] = round(on, 1)
    sent = dict(index=rows.index(r)+1, id=r['id'], text=r['text'], take=r['take'], startFrame=r['startFrame'], endFrame=r['endFrame'], onsetFrame=round(on, 1), asr=A[r['id']]['asr'], asrCoverage=A[r['id']]['cov'], chars=ch, words=tokens(ch, r['text']))
    if r.get('spansShots'): sent['spansShots'] = r['spansShots']; sent['splitAt'] = r['splitAt']
    shots.setdefault(r['shot'], []).append(sent)
S = []
for r in rows:
    if r.get('spansShots'):
        a, b = r['spansShots']; s = shots.pop(b)
        S.append(dict(id=a, sentences=s, note=f"与 {b} 连读一句；{b} 的起点取「{r['text'][len(r['splitAt']):][:2]}」字自身的时间"))
        S.append(dict(id=b, sentences=s, continuesFrom=a)); continue
    if r['shot'] not in [q['id'] for q in S]: S.append(dict(id=r['shot'], sentences=shots[r['shot']]))
def cue_onset(shot_id, cue, occ='first'):
    sh = next(q for q in S if q['id'] == shot_id)
    for s in sh['sentences']:
        t = re.sub(r'[^\w]', '', s['text'])
        key = re.sub(r'[^\w]', '', cue); i = (t.rfind if occ == 'last' else t.find)(key)
        if i < 0: continue
        c = s['chars'][i]; atEnd = (i+len(key) == len(t))
        on = c['startFrame']
        assert s['startFrame']-1 <= on < s['endFrame'], (shot_id, cue, on, s['startFrame'], s['endFrame'])
        return dict(shot=shot_id, cue=cue+('(last)' if occ == 'last' else ''), sentence=s['id'], onsetFrame=on, cueAtSentenceEnd=atEnd, flag='CHECK: cue is last word of sentence' if atEnd else '')
    raise KeyError((shot_id, cue))
tab = []
for q in S:
    if q.get('continuesFrom'):
        s = q['sentences'][0]; k = len(re.sub(r'[^\w]', '', s['splitAt'])); on = s['chars'][k]['startFrame']; src = f"「{s['chars'][k]['ch']}」字自身时间"
    else: s = q['sentences'][0]; on = s['onsetFrame']; src = '句首能量起点'
    q['onsetFrame'] = on; tab.append(dict(shot=q['id'], sentence=s['id'], onsetFrame=on, frameInt=int(round(on)), sec=round(on/FPS, 2), source=src))
sha = hashlib.sha256(open('../voice.wav', 'rb').read()).hexdigest()
pauses = f"句首{P['lead']:.2f}s、句间{P['gapIn']:.2f}s、镜间{P['gapShot']:.2f}s、片尾{P['tail']:.2f}s"
out = dict(script='script.md', scriptSha256=hashlib.sha256(open('../script.md', 'rb').read()).hexdigest(), fps=FPS, audio='voice.wav', audioSha256=sha, durationFrames=B['summary']['frames'], asrModel='faster-whisper '+P['asr']['model'],
           note=f'整片绝对帧(30fps)；分镜未出，按自然停顿拼接（{pauses}）；chars 为逐字时间（ASR 词时间对齐到脚本字），words 为英文缩写合并后的词；cue 起点用该词自身时间', shots=[dict(id=q['id'], onsetFrame=q['onsetFrame'], **({'continuesFrom': q['continuesFrom']} if q.get('continuesFrom') else {}), sentences=([] if q.get('continuesFrom') else q['sentences'])) for q in S], onsetTable=tab)
# per-shot frames (30 fps). speechStart/End = first sentence start / last sentence end;
# startFrame/endFrame = shot slot: each shot starts at its first sentence start (floor), shot 1 at 0, last shot ends at durationFrames
sh = out['shots']
for i, q in enumerate(sh):
    q['speechStartFrame'] = q['sentences'][0]['startFrame']; q['speechEndFrame'] = q['sentences'][-1]['endFrame']
    q['startFrame'] = 0 if i == 0 else math.floor(q['sentences'][0]['startFrame'])
for i, q in enumerate(sh):
    q['endFrame'] = sh[i+1]['startFrame'] if i+1 < len(sh) else out['durationFrames']; q['durationFrames'] = q['endFrame']-q['startFrame']
out['note'] += '；shots[].startFrame/endFrame 为镜头区间（每镜从其首句起点向下取整开始，镜1从0开始，末镜到 durationFrames 结束），speechStartFrame/speechEndFrame 为该镜语音起止'
json.dump(out, open('../words.json', 'w'), ensure_ascii=False, indent=1)
# cue self-test: last-word cues are flagged and stay inside their own sentence
tests = [tuple(t) for t in json.load(open('cue_tests.json'))]  # from cue_tests.py
print('# cue self-test')
CUES = [cue_onset(*t) for t in tests]
for c in CUES: print(c)
json.dump(CUES, open('cues.json', 'w'), ensure_ascii=False, indent=1)
for r in tab: print(r)
