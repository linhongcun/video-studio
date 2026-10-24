#!/usr/bin/env python3
"""Whole-track ASR of ../voice.wav vs the script -> voice/asr_full.json (QA only; EP.14 voice/asr_full.py).

  python3 episodes/_shared/voice/asr_full.py --dir EPDIR
"""
import json, os, re, difflib, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__)
q = P['asr']; m = common.whisper(P)
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', '../voice.wav', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
seg, _ = m.transcribe(x, language=q['language'], beam_size=q['beam'], condition_on_previous_text=False, initial_prompt=q['initialPrompt'])
h = ''.join(g.text for g in seg)
S = json.load(open('sents.json')); ref = ''.join(s['text'] for s in S)
norm = lambda t: re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', t).upper()
a_, b = norm(ref), norm(h)
sm = difflib.SequenceMatcher(None, a_, b, autojunk=False)
diffs = [(op, a_[i1:i2], b[j1:j2], a_[max(0, i1-4):i2+4]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal']
json.dump(dict(asr=h, ratio=sm.ratio(), diffs=diffs), open('asr_full.json', 'w'), ensure_ascii=False, indent=1)
print(h); print('ratio', round(sm.ratio(), 4), 'refchars', len(a_))
for d in diffs: print(d)
