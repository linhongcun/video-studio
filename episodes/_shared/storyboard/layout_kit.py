"""Element helpers for layout specs (ported verbatim from the EP.14 degradation-v1 layout.py).
Frame values in a layout are one of:
  {"$cue": word, "d": n[, "occ": "last"]}   onset-driven (build_sb resolves via onset_rule.py),
  {"$timer": word, "d": n, "why": ...}      picture-timing, counted from that word,
  a plain int                               picture-timing, shot-local frame.
ripples[].bornFrame "@" = the frame of the state it sits in. All coordinates are 1920x1080 canvas coordinates."""
import math, unicodedata


def wid(t, fs):
    """Text width estimate used for box sizing (W/F/A = 1 em, full-width space = 1 em, else .62 em)."""
    return sum(1 if unicodedata.east_asian_width(c) in 'WFA' and c not in '\u3000' or c == '\u3000' else .62 for c in t)*fs


def C(cue, d=0, occ=None):
    r = {'$cue': cue, 'd': d}
    if occ: r['occ'] = occ
    return r


def TM(after, d, why): return {'$timer': after, 'd': d, 'why': why}


def W(id_, comp, x, y, w, h, z=1, cue=None, **kw):
    d = {'id': id_, 'type': 'rect', 'component': comp, 'x': x, 'y': y, 'w': w, 'h': h, 'z': z, 'cueText': cue}; d.update(kw)
    if comp is None: del d['component']
    return d


def T(id_, text, x, y, fs, z=4, cue=None, color='#E5E7EB', comp=None, w=None, h=None, **kw):
    """Text element sized so every text it ever shows fits at the original font size (no renderer shrink)."""
    w = w or math.ceil(max(wid(l, fs) for l in text.split('\n'))) + 40; h = h or math.ceil(fs*1.25*len(text.split('\n'))) + 12
    d = {'id': id_, 'type': 'text', 'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'fontSize': fs, 'color': color, 'align': 'center', 'z': z, 'cueText': cue}
    if comp: d['component'] = comp
    d.update(kw)
    for c_ in d.get('stateCues') or []:
        if c_.get('text'): d['w'] = max(d['w'], math.ceil(max(wid(l, fs) for l in c_['text'].split('\n'))) + 40)
    if comp == 'CalloutTag':   # 12 px horizontal slack
        d['w'] = max(d['w'], math.ceil(max(wid(l, fs) for l in text.split('\n'))) + 40 + 12)
        d['h'] = max(d['h'], math.ceil(fs*1.2*len(text.split('\n'))) + 23)
    if comp == 'CornerBadge':
        d['w'] = max(d['w'], math.ceil(wid(text, fs)) + 32 + 12); d['h'] = max(d['h'], math.ceil(fs*1.2) + 16)
    return d


def S(*pairs):
    """State cues: (cue-or-frame-spec, state name[, {changed fields}]) ..."""
    return [{'cueText': c, 'state': s, **(extra[0] if extra else {})} for c, s, *extra in pairs]


PUN = '，。：；？！、,.:;?! '


class LayoutCtx:
    """Per-run context handed to spec.build(ctx): words.json lookups and part() registration."""
    def __init__(self, words, nshot, browser, boxshots):
        self.WJ = words; self.L = {}; self.nshot = nshot
        self.browser = tuple(browser); self.boxshots = tuple(boxshots)
        self.FRAMES = {n: ('browser' if n in self.browser else 'canvas') for n in range(1, nshot + 1)}
        self.SHOT0 = {int(x['id'][:2]): x['startFrame'] for x in words['shots']}
        self.SHOTLEN = {int(x['id'][:2]): x['endFrame'] - x['startFrame'] for x in words['shots']}

    def part(self, k, direction, els, box=False):
        assert box == (k in self.boxshots), k
        self.L[str(k)] = {'direction': direction, 'box': box, 'elements': els, 'frame': self.FRAMES[k]}

    def _chars(self, n):
        return [c for x in self.WJ['shots'] if int(x['id'][:2]) == n for s_ in x['sentences'] for c in s_['chars']]

    def reveal(self, n, text, pun=PUN):
        """readAlong frames: each char at max(1, floor(ASR start - shot start) - 2)."""
        chars = self._chars(n)
        narr = ''.join(c['ch'] for c in chars); needle = ''.join(ch for ch in text if ch not in pun)
        i0 = narr.find(needle[:min(8, len(needle))]); assert i0 >= 0, (n, text[:20])
        fr = []; j = i0
        for ch in text:
            if ch in pun: fr.append(fr[-1] if fr else 1); continue
            assert chars[j]['ch'] == ch, (n, ch, chars[j]['ch'], j)
            fr.append(max(1, math.floor(chars[j]['startFrame'] - self.SHOT0[n]) - 2)); j += 1
        return {'mode': 'readAlong', 'source': 'words.json chars（脚本原字对齐）', 'frames': fr}

    def cue0(self, n, word):
        chars = self._chars(n)
        t = ''.join(c['ch'] for c in chars); i = t.index(word); return chars[i]['startFrame'] - self.SHOT0[n]

    def done(self):
        assert set(self.L) == {str(i) for i in range(1, self.nshot + 1)}, sorted(self.L)
        return self.L
