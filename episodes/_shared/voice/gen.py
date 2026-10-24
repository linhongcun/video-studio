#!/usr/bin/env python3
"""TTS takes: voice/takes/{sid}-{take}.wav (48 kHz mono) + .txt.json (EP.14 voice/gen2.py).

Jobs file: [[sid, take, text|null, style?], ...]; null text = sents.json tts.
No jobs file = take "a" for every sentence. Existing takes are skipped.
Calls the repo's episodes/_shared/tts/mimo_say.py (needs MIMO_API_KEY in the
environment, or the --env file mimo_say.py defaults to). TTS output is not
deterministic: a rerun gives different takes.

  python3 episodes/_shared/voice/gen.py --dir EPDIR [--jobs voice/jobs_b.json]
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__, lambda ap: ap.add_argument('--jobs', help='jobs json (path relative to EPDIR/voice, or absolute)'))
SAY = str(common.ROOT / P['tts']['script'])
S = {s['id']: s for s in json.load(open('sents.json'))}
J = json.load(open(a.jobs)) if a.jobs else [[k, 'a', None] for k in S]
os.makedirs('takes', exist_ok=True)
def run(j):
    sid, t, txt = j[:3]; sty = j[3] if len(j) > 3 else None; txt = txt or S[sid]['tts']; b = f'takes/{sid}-{t}'
    if os.path.exists(b+'.wav'): return
    r = subprocess.run([sys.executable, SAY, '--text', txt, '--out', b+'.raw.wav']+(['--style', sty] if sty else []), capture_output=True, text=True)
    if r.returncode: print('FAIL', b, r.stdout[-200:], r.stderr[-200:]); return
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', b+'.raw.wav', '-ar', '48000', '-ac', '1', b+'.wav'], check=True)
    json.dump(txt, open(b+'.txt.json', 'w'), ensure_ascii=False)
with ThreadPoolExecutor(P['tts']['threads']) as ex: list(ex.map(run, J))
print('done')
