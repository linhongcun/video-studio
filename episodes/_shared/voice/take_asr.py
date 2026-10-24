#!/usr/bin/env python3
"""ASR on cut takes, same settings as asr.py (EP.14 voice/take_check2.py).

Prints "<take file> <hypothesis>" per take; redirect to a log for score.py.

  python3 episodes/_shared/voice/take_asr.py --dir EPDIR takes/01-hook-1-a.wav ... > take_asr.log
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__, lambda ap: ap.add_argument('takes', nargs='+'))
q = P['asr']; m = common.whisper(P); tmp = os.path.join(tempfile.mkdtemp(), 'tc2.wav')
for f in a.takes:
    y, tail = common.cut(common.load(f)); sf.write(tmp, y, 48000, subtype='FLOAT')
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', tmp, '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    x = np.concatenate([np.zeros(4800, np.float32), x, np.zeros(4800, np.float32)])
    seg, _ = m.transcribe(x, language=q['language'], beam_size=q['beam'], condition_on_previous_text=False, word_timestamps=True, initial_prompt=q['initialPrompt'])
    print(f.split('/')[-1], ''.join(g.text for g in seg), flush=True)
