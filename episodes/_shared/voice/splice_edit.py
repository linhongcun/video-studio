#!/usr/bin/env python3
"""Keep ORIG bit-for-bit outside [A, B] seconds, use EDITED inside, 5 ms linear crossfades (EP.14 voice/splice_edit.py).

Pick A and B inside consonant closures or silence. Both inputs must have the same length.

  python3 episodes/_shared/voice/splice_edit.py --dir EPDIR ORIG EDITED A B OUT
"""
import os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

def args(ap):
    for n in ('orig', 'edited', 'a', 'b', 'out'): ap.add_argument(n)
A, P = common.setup(__doc__, args)
o, sr = sf.read(A.orig, dtype='float32'); e, _ = sf.read(A.edited, dtype='float32'); a, b = int(float(A.a)*sr), int(float(A.b)*sr); r = int(.005*sr)
assert len(o) == len(e)
y = o.copy(); w = np.ones(b-a, np.float32); w[:r] = np.linspace(0, 1, r); w[-r:] = np.linspace(1, 0, r)
y[a:b] = o[a:b]*(1-w)+e[a:b]*w; sf.write(A.out, y, sr, subtype='FLOAT')
print('spliced', A.out, 'window', A.a, A.b, 'max|o| at edges', float(np.abs(o[a-r:a+r]).max()), float(np.abs(o[b-r:b+r]).max()))
