#!/usr/bin/env python3
"""PSOLA pitch edit of one take inside given windows (EP.14 voice/pitch_edit.py).

Only F0 changes, and only inside the windows; durations and timbre are kept.
EDITS is JSON [[a, b, [[t, semitones], ...]], ...] with times in CUT-take
seconds (after cut() trims leading silence) and targets in semitones relative
to BASE_HZ (the take's median F0). Writes float32 wav. Follow with
splice_edit.py so the take stays sample-identical outside the edit. EP.14 used
this for 01-hook-1 m→mps and 16-two-prices-1 s→sps (see substitutions.md).

  python3 episodes/_shared/voice/pitch_edit.py --dir EPDIR DST EDITS_JSON SRC BASE_HZ
"""
import json, os, sys
import numpy as np, parselmouth, soundfile as sf
from parselmouth.praat import call
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

def args(ap):
    for n in ('dst', 'edits', 'src', 'base'): ap.add_argument(n)
a, P = common.setup(__doc__, args)
SR = 48000
x = common.load(a.src)
fr = np.abs(x[:len(x)//480*480]).reshape(-1, 480).max(1) > 0.01; off = max(0, np.where(fr)[0][0]*480-int(.03*SR))/SR  # cut() start
BASE = float(a.base); hz = lambda st: BASE*2**(st/12)
EDITS = json.loads(a.edits)
snd = parselmouth.Sound(x.astype(np.float64), SR)
man = call(snd, 'To Manipulation', 0.005, 120, 500); pt = call(man, 'Extract pitch tier')
for a_, b, pts in EDITS:
    call(pt, 'Remove points between', off+a_, off+b)
    for t, st in pts: call(pt, 'Add point', off+t, hz(st))
call([pt, man], 'Replace pitch tier'); out = call(man, 'Get resynthesis (overlap-add)')
y = out.values[0].astype(np.float32); sf.write(a.dst, y, SR, subtype='FLOAT')
print('offset', round(off, 3), 'written', a.dst)
