#!/usr/bin/env python3
"""script.md -> voice/cue_tests.json: the visual cues onsets.py times.

For each shot, every 「…」 quoted in its 画面 line whose text (punctuation
dropped) occurs in that shot's 旁白 becomes [shotId, quote], in order of
appearance, once per normalized text. The EP.14 extractor was not saved; this
rule reproduces EP.14's voice/cue_tests.json (65 cues) exactly from the
script it was made from (sha256 629b5042). The script was edited after the voice froze (94a2e143,
same narration, new 画面 lines), and from that version the rule gives 74 cues.
Run it on the script you voice and freeze the output with the voice.

  python3 episodes/_shared/voice/cue_tests.py --dir EPDIR
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common


def extract(text):
    shots = []; cur = None
    for l in text.split('\n'):
        m = re.match(r'### (\w+) ([\w-]+)', l)
        if m:
            cur = dict(id=f"{int(re.match(r'\d+', m[1])[0]):02d}{re.sub(r'^\d+', '', m[1])}-{m[2]}", n='', v=[]); shots.append(cur)
        elif cur and l.startswith('旁白：'): cur['n'] = l[3:].strip()
        elif cur and l.startswith('画面：'): cur['v'].append(l[3:])
    out = []
    for s in shots:
        n = re.sub(r'[^\w]', '', s['n']); seen = set()
        for v in s['v']:
            for q in re.findall(r'「([^」]+)」', v):
                k = re.sub(r'[^\w]', '', q)
                if k and k in n and k not in seen: seen.add(k); out.append([s['id'], q])
    return out


if __name__ == '__main__':
    a, P = common.setup(__doc__)
    T = extract(open('../script.md', encoding='utf-8').read())
    json.dump(T, open('cue_tests.json', 'w'), ensure_ascii=False)
    print(len(T), 'cues')
