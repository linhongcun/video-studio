#!/usr/bin/env python3
"""take_asr.py logs -> voice/score.json: cut duration and diff ops vs the script text per take (EP.14 voice/score.py).

An empty ops list means ASR heard the script text. Homophones (页→业 etc.)
show up as ops too; judge them by ear or with sandhi.py / probe.py, then write
the chosen take per sentence into voice/picks.json ({"sid": "take"}).

  python3 episodes/_shared/voice/score.py --dir EPDIR take_asr.log [...]
"""
import json, os, re, difflib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__, lambda ap: ap.add_argument('logs', nargs='+'))
SR = 48000
S = {s['id']: s for s in json.load(open('sents.json'))}
norm = lambda t: re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', t)
res = {}
for f in a.logs:
    for l in open(f):
        k, h = l.split(' ', 1); sid, t = re.match(r'(.*)-([a-z0-9]+)\.wav', k).groups()
        y, _ = common.cut(common.load(f'takes/{k}')); d = len(y)/SR
        ref = norm(S[sid]['text']); hh = norm(h)
        ops = [(op, ref[i1:i2], hh[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref, hh, autojunk=False).get_opcodes() if op != 'equal']
        res.setdefault(sid, {})[t] = dict(dur=round(d, 2), ops=ops, asr=h.strip())
json.dump(res, open('score.json', 'w'), ensure_ascii=False, indent=1)
for sid in S:
    for t, r in sorted(res.get(sid, {}).items()): print(sid, t, r['dur'], r['ops'])
