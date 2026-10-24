#!/usr/bin/env python3
"""Per take: ASR diff ops vs the script and 5-pt F0 of every 一/不 (EP.14 voice/take_sandhi.py).

Same ASR input as take_asr.py (ffmpeg 16 kHz, word timestamps); char timing
from difflib alignment of ASR chars to the script text; F0 in semitones re the
take's median. Use to pick takes and TTS respellings for tone sandhi.

  python3 episodes/_shared/voice/take_sandhi.py --dir EPDIR takes/02-not-bug-2-*.wav > ts_x.log
"""
import json, os, re, difflib, subprocess, sys, tempfile
import numpy as np, soundfile as sf, parselmouth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a_, P = common.setup(__doc__, lambda ap: ap.add_argument('takes', nargs='+'))
SR = 48000; q = P['asr']; m = common.whisper(P); tmp = os.path.join(tempfile.mkdtemp(), 'ts.wav')
S = {s['id']: s['text'] for s in json.load(open('sents.json'))}
for f in a_.takes:
    sid = re.sub(r'-[a-z0-9]+\.wav$', '', f.split('/')[-1]); y, _ = common.cut(common.load(f)); sf.write(tmp, y, 48000, subtype='FLOAT')
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', tmp, '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    x = np.concatenate([np.zeros(4800, np.float32), x, np.zeros(4800, np.float32)])
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
    ops = [(op, st_[i1:i2], ''.join(ac)[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, st_, ''.join(ac), autojunk=False).get_opcodes() if op != 'equal']
    snd = parselmouth.Sound(y.astype(np.float64), 48000); p = snd.to_pitch_ac(time_step=0.005, pitch_floor=120, pitch_ceiling=500)
    F = p.selected_array['frequency']; T = p.xs(); MED = np.median(F[F > 0])
    out = []
    for i, c in enumerate(st_):
        if c not in '一不' or not T_[i]: continue
        a, b = T_[i]; mm = (T >= a) & (T <= b) & (F > 0); s = 12*np.log2(F[mm]/MED)
        if len(s) < 3: out.append(f"{st_[max(0, i-1):i+2]}:无声"); continue
        n = len(s); five = [round(float(np.median(s[int(n*k/5):max(int(n*k/5)+1, int(n*(k+1)/5))])), 1) for k in range(5)]
        out.append(f"{st_[max(0, i-1):i+2]}:{five}Δ{five[-1]-five[0]:+.1f}")
    print(f.split('/')[-1], f'{len(y)/SR:.2f}s', 'ops=', ops, '|', ' ; '.join(out), '| ASR:', h, flush=True)
