#!/usr/bin/env python3
"""script.md -> voice/sents.json (EP.14 voice/prep.py).

Shots are "### N name" headings; narration is the "旁白：" line. Each sentence
gets tts = text (+ "。" if it has no end mark) + "好。": the extra "好。" is a
throwaway tail that build.py cuts off, so the real last word keeps a natural
fall. params.json "subst" ([[from, to], ...]) replaces text in the TTS string
only; subtitles and words.json keep the script text. Per-sentence fixes go in
a jobs file for gen.py instead (EP.14 did that, see substitutions.md).

  python3 episodes/_shared/voice/prep.py --dir EPDIR
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

a, P = common.setup(__doc__)
L = open('../script.md', encoding='utf-8').read().split('\n')
shots = []; cur = None
for l in L:
    m = re.match(r'### (\w+) ([\w-]+)', l)
    if m: cur = dict(id=f"{int(re.match(r'\d+', m[1])[0]):02d}{re.sub(r'^\d+', '', m[1])}-{m[2]}", n=''); shots.append(cur)
    elif cur and l.startswith('旁白：'): cur['n'] = l[3:].strip()
R = [tuple(x) for x in P['subst']]
def tts(t):
    for a_, b in R: t = t.replace(a_, b)
    return t+('' if t[-1] in '。？！' else '。')+'好。'
out = []; pend = None
cnt = sum(len(re.sub(r'[，。？！：；、\s]', '', s['n'])) for s in shots)
for sh in shots:
    n = sh['n']
    if pend: n = pend['text']+n
    ss = [q for q in re.findall(r'[^。？！]+[。？！]?', n) if q.strip()]
    if not re.search(r'[。？！]$', n) and sh is not shots[-1]: pend = dict(text=n); continue
    for i, q in enumerate(ss):
        d = dict(id=f"{sh['id']}-{i+1}", shot=sh['id'], text=q, tts=tts(q))
        if pend and i == 0: d['spansShots'] = [shots[shots.index(sh)-1]['id'], sh['id']]; d['splitAt'] = pend['text']
        out.append(d)
    pend = None
json.dump(out, open('sents.json', 'w'), ensure_ascii=False, indent=1)
print(len(shots), 'shots', cnt, 'chars', len(out), 'sents')
for o in out: print(o['id'], o['tts'])
if any(o.get('spansShots') for o in out):
    print('WARNING: a shot narration does not end in 。？！; onsets.py cannot place a sentence that spans shots. End every shot with 。？！', file=sys.stderr)
