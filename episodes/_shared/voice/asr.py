#!/usr/bin/env python3
"""Sentence ASR: voice/sentences/*.wav -> voice/asr.json (EP.14 voice/asr.py).

faster-whisper (default medium, cpu, float32, 8 threads), zh, beam 5,
word timestamps, prompt "以下是普通话的句子。". Each sentence is padded with
0.3 s of silence; word times are shifted back and converted to absolute
30 fps frames using build.json startSample. First run downloads the model
(Systran/faster-whisper-medium, about 1.5 GB) from Hugging Face.

  python3 episodes/_shared/voice/asr.py --dir EPDIR
"""
import json, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__)
q = P['asr']; m = common.whisper(P)
B = json.load(open('build.json')); out = []
for r in B['sentences']:
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f"sentences/{r['id']}.wav", '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    pad = 4800; x = np.concatenate([np.zeros(pad, np.float32), x, np.zeros(pad, np.float32)])
    seg, _ = m.transcribe(x, language=q['language'], beam_size=q['beam'], condition_on_previous_text=False, word_timestamps=True, initial_prompt=q['initialPrompt'])
    W = []; h = ''
    for g in seg:
        h += g.text
        for w in g.words:
            s0 = max(0, w.start-.3); e0 = max(0, w.end-.3)
            W.append(dict(w=w.word.strip(), startFrame=round(r['startSample']/48000*30+s0*30, 1), endFrame=round(r['startSample']/48000*30+e0*30, 1)))
    t = re.sub(r'[^\u4e00-\u9fff]', '', r['text']); hh = re.sub(r'[^\u4e00-\u9fff]', '', h)
    cov = sum(c in hh for c in t)/max(1, len(t))
    out.append(dict(id=r['id'], asr=h, cov=round(cov, 2), words=W)); print(r['id'], cov, h, flush=True)
json.dump(out, open('asr.json', 'w'), ensure_ascii=False, indent=1)
