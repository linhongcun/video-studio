"""Validate-side onset checker. The rule itself is episodes/_shared/onset_rule.py (imported, never copied).
Events: appear(cueText) / disappear(disappearCueText) / stateKeyframes(cueText) / cueLog(frame - d, and the cueLog value
must equal the field it points at) / moves(cueText).
If a cue occurs several times in the shot's sentences the occurrence whose diff is closest to -2 is used; the "previous char"
of a sentence-initial char is the last char of the previous sentence in words.json order.
Ported from the EP.14 degradation-v1 episode script; only the import path changed."""
import json, re, sys, wave
from pathlib import Path
import numpy as np
SHARED = str(Path(__file__).resolve().parents[1])   # episodes/_shared
if SHARED not in sys.path: sys.path.insert(0, SHARED)
import onset_rule
LO, HI = -6, 2
norm = lambda t: re.sub(r'[^\u4e00-\u9fffA-Za-z0-9.]', '', t).upper()
class Checker:
    def __init__(self, wav, words):
        assert onset_rule.selftest()
        w = wave.open(str(wav)); self.sr = w.getframerate()
        X = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32767
        self.rule = onset_rule.Rule(X, self.sr)
        W = json.loads(open(words).read()); self.SEN = [s for sh in W['shots'] for s in sh['sentences']]; self.S = {s['id']: s for s in self.SEN}
        self._c = {}
    def prev(self, sid, i):
        s = self.S[sid]; c = s['chars']
        if i > 0: return c[i-1]['startFrame'], c[i-1]['endFrame']
        k = self.SEN.index(s); return (self.SEN[k-1]['chars'][-1]['startFrame'], self.SEN[k-1]['chars'][-1]['endFrame']) if k else (None, None)
    def occ(self, sid, cue):
        key = (sid, cue)
        if key in self._c: return self._c[key]
        s = self.S[sid]; t = ''.join(c['ch'].upper() for c in s['chars']); cn = norm(cue); out = []; i = t.find(cn)
        while i >= 0:
            ch = s['chars'][i]; ps, pe = self.prev(sid, i); r = self.rule.onset(ch['startFrame'], ch['endFrame'], ps, pe)
            out.append(dict(sid=sid, i=i, asr=ch['startFrame'], atEnd=i+len(cn) == len(t), **r)); i = t.find(cn, i+1)
        self._c[key] = out; return out
    @staticmethod
    def events(e):
        evs = [('appear', e.get('appearFrame'), e['cueText'])] if e.get('cueText') else []
        if e.get('disappearCueText'): evs.append(('disappear', e['disappearFrame'], e['disappearCueText']))
        evs += [('state:'+k['state'], k['frame'], k['cueText']) for k in e.get('stateKeyframes', []) if k.get('cueText')]
        mism = []
        for c in e.get('cueLog', []):
            o = e
            for p in re.findall(r'(\w+)(?:\[(\d+)\])?', c['path']):
                o = o[p[0]]; o = o[int(p[1])] if p[1] else o
            if o != c['frame']: mism.append((c['path'], o, c['frame']))
            evs.append(('cue:'+c['path'], o - c.get('d', 0), c['cueText']))
        for m in e.get('moves', []) or []:
            if m.get('cueText'): evs.append(('move', m['frame'], m['cueText']))
        return evs, mism
    def check(self, sb, extra_sources=None):
        shots = [x for sc in sb['scenes'] for x in sc['shots']]
        place = {v['id']: (sh, v) for sh in shots for v in sh['voice']}
        rows = []
        for sh in shots:
            sids = [v['id'] for v in sh['voice']]
            for e in sh['elements']:
                if e.get('role') == 'subtitle': continue
                evs, mism = self.events(e)
                for path, o, f in mism: rows.append(dict(shot=sh['id'], el=e['id'], kind='cueLog '+path, cue='', at=None, ok=False, msg=f'cueLog 值 {f} 与字段 {o} 不一致'))
                for kind, fr, cue in evs:
                    best = None
                    for sid in sids:
                        for r in self.occ(sid, cue):
                            psh, v = place[sid]; off = psh['from'] + v['localStart'] - v['wavStart']; g = sh['from'] + fr; d = g - (r['onset'] + off)
                            if best is None or abs(d+2) < abs(best[0]+2): best = (d, r, r['onset'] + off, g, r['asr'] + off)
                    if best is None:
                        rows.append(dict(shot=sh['id'], el=e['id'], kind=kind, cue=cue, at=sh['from']+fr, ok=False, msg='旁白里找不到')); continue
                    d, r, on, g, asr = best
                    rows.append(dict(shot=sh['id'], el=e['id'], kind=kind, cue=cue, at=g, asr=asr, onset=on, rawOnset=r['onset'], diff=d, ok=LO <= d <= HI,
                                     src=f"{r['source']}/{r['kind']}", breaths=r['breaths'], atEnd=r['atEnd']))
        return rows
def fmt(r):
    if 'diff' not in r: return f"{r['shot']}/{r['el']} {r['kind']}「{r['cue']}」 {r['msg']} FAIL"
    b = f" 跳过换气 {r['breaths']}" if r.get('breaths') else ''
    return f"{r['shot']}/{r['el']} {r['kind']}「{r['cue']}」| at {r['at']} ASR {r['asr']:.2f} 开口 {r['onset']:.2f} 差 {r['diff']:+.2f} {'OK' if r['ok'] else 'FAIL'} · {r['src']}{b}{' ·句末词' if r['atEnd'] else ''}"
