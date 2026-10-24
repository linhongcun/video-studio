#!/usr/bin/env python3
"""script.md + words.json + voice.wav + layout.json + covers.json -> storyboard.json (+ build-onsets.txt).

  python3 -B episodes/_shared/storyboard/build_sb.py --spec SPEC.py --episode-dir EPDIR [--inputs MAP.json] \\
      [--layout layout.json] [--covers covers.json] [--out storyboard.json] [--onsets-out build-onsets.txt]

Timeline: the whole voice.wav is laid out in place (no inserted pauses); shot n = words.json shots[n-1] start..end.
Onsets always come from episodes/_shared/onset_rule.py (via onset_check.py). A {"$cue": w, "d": n} frame becomes
max(1, floor(onsetLocal) - 2) + d with d in -3..+4 and is logged in cueLog/cueOnset; {"$timer": w, "d": n} and plain ints
are picture timing and go to timerLog. Subtitles always follow the script text.

Spec module (everything episode-specific):
  FPS, MIN, MAX, TR, WAVLEN, NSHOT       frame rate, shot length bounds, transition frames, total frames, shot count
  MAX_EXC   {shot: max frames}           per-shot length exceptions (EP.14: {1: 314})
  KNOLL     [(start, end), ...]          optional: absolute shot frames that words.json must match
  SHA       {input name: sha256 prefix}  input pinning (voice.wav, words.json, narration.py, voice/cues.json, ...)
  WORDS_SCRIPT_SHA / WORDS_AUDIO_SHA     optional prefixes words.json must declare
  NARRATION_FILE                          optional: module with tuple N == every 旁白 line of script.md
  PUNCT, SUB, SUB_MAX=22, SUB_MERGE=16    subtitle punctuation / subtitle element / chunk limits
  CHAPTERS [(id, title, accent)], ch_of(n) -> chapter id, NEWCOMP_FIELDS {component: [fields with frame specs]}
  meta(ctx) -> ordered meta dict, ASSETS -> assets dict     (ctx: see Ctx below)
Inputs by logical name: script.md, words.json, voice.wav (+ whatever SHA / NARRATION_FILE name)."""
import argparse, copy, json, math, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit
import onset_check as OC

SHOT_RE = r'^### (\d+) (\S+)（[^\n]*\nframe：(\w+)\n画面：(.*?)\n旁白：(.*?)$'


class Ctx:
    """What spec.meta(ctx) can use."""
    pass


def check_inputs(spec, inp):
    script = inp.text('script.md'); sha = {}
    for name, pre in getattr(spec, 'SHA', {}).items():
        sha[name] = kit.sha256(inp(name)); assert sha[name].startswith(pre), (name, sha[name], pre)
    for name in ('voice.wav', 'words.json'):
        if name not in sha: sha[name] = kit.sha256(inp(name))
    nf = getattr(spec, 'NARRATION_FILE', None)
    if nf:
        NARR = kit.load_spec(inp(nf), 'narr')
        assert re.findall(r'^旁白：(.*)$', script, re.M) == list(NARR.N), f'旁白与 {nf} 不一致'
    W = inp.json('words.json'); assert W['durationFrames'] == spec.WAVLEN, W['durationFrames']
    if getattr(spec, 'WORDS_SCRIPT_SHA', None): assert W['scriptSha256'].startswith(spec.WORDS_SCRIPT_SHA)
    if getattr(spec, 'WORDS_AUDIO_SHA', None): assert W['audioSha256'].startswith(spec.WORDS_AUDIO_SHA)
    return script, W, sha


def run(spec, inp, layout_path, covers_path, out, onsets_out):
    import hashlib
    PUNCT = spec.PUNCT; NSHOT = spec.NSHOT; MAX_EXC = getattr(spec, 'MAX_EXC', {})
    SUB_MAX = getattr(spec, 'SUB_MAX', 22); SUB_MERGE = getattr(spec, 'SUB_MERGE', 16)
    NEWCOMP_FIELDS = getattr(spec, 'NEWCOMP_FIELDS', {})
    script, W, SHA = check_inputs(spec, inp)
    SCRIPT_SHA = hashlib.sha256(script.encode()).hexdigest(); WAV_SHA = SHA['voice.wav']; WORDS_SHA = SHA['words.json']
    CHK = OC.Checker(inp('voice.wav'), inp('words.json'))
    SENT = {s['id']: s for sh in W['shots'] for s in sh['sentences']}
    WSHOT = {int(sh['id'][:2]): sh for sh in W['shots']}
    if getattr(spec, 'KNOLL', None) is not None:
        assert [(WSHOT[n]['startFrame'], WSHOT[n]['endFrame']) for n in range(1, NSHOT+1)] == list(spec.KNOLL), 'words.json 镜头区间 ≠ 定稿绝对帧'
    shots_md = re.findall(SHOT_RE, script, re.M | re.S)
    assert len(shots_md) == NSHOT, len(shots_md)
    SMD = {k: (nm.strip(), fr, v.strip(), t.strip()) for k, nm, fr, v, t in shots_md}
    CH_OF = {n: spec.ch_of(n) for n in range(1, NSHOT+1)}
    LAYOUT = json.loads(Path(layout_path).read_text()); assert set(LAYOUT) == set(SMD)
    PARTS = []
    for k, (nm, fr, vis, narr) in SMD.items():
        n = int(k); ss = [s['id'] for s in WSHOT[n]['sentences']]
        assert WSHOT[n]['id'] == f'{n:02d}-{nm}', (k, nm)
        assert ''.join(SENT[x]['text'] for x in ss).replace(' ', '') == narr.replace(' ', ''), (k, narr)
        assert LAYOUT[k]['frame'] == fr, (k, fr, LAYOUT[k]['frame'])
        PARTS.append((k, n, ss, narr))

    def strip(t): return ''.join(c for c in t if c not in PUNCT)

    def char_at(sent_ids, narr, cue, occ=None):
        pos = narr.rindex(cue) if occ == 'last' else narr.index(cue); base = 0
        for sid in sent_ids:
            t = SENT[sid]['text']
            if pos < base + len(t): return sid, len(strip(t[:pos-base]))
            base += len(t)
        raise ValueError(cue)

    def sub_chunks(t):
        out = []
        for part in re.findall(r'[^，。：；？！]*[，。：；？！]?', t):
            if not part: continue
            while len(part) > SUB_MAX: out.append(part[:SUB_MAX]); part = part[SUB_MAX:]
            out.append(part)
        out2 = []
        for p in out:
            if out2 and not strip(p): out2[-1] += p
            else: out2.append(p)
        m = []
        for p in out2:
            if m and len(m[-1]) + len(p) <= SUB_MERGE: m[-1] += p
            else: m.append(p)
        return m

    scenes = {}; order = []; g = 0; ONSETS = []
    for i, (key, n, ss, narr) in enumerate(PARTS):
        ws = WSHOT[n]; bw = ws['startFrame']; L = ws['endFrame'] - bw
        assert bw == g and spec.MIN <= L <= MAX_EXC.get(n, spec.MAX), (key, bw, g, L)
        sid = ws['id']
        voice = []
        for x in ss:
            s_ = SENT[x]; ls = round(s_['startFrame'] - bw)
            voice.append({'id': x, 'wavStart': s_['startFrame'], 'wavEnd': s_['endFrame'], 'localStart': ls, 'localEnd': ls + math.ceil(s_['endFrame'] - s_['startFrame'])})
        VL = {v['id']: v for v in voice}

        def cue_local(cue, occ=None):
            assert cue in narr, (key, cue)
            sid_, ci = char_at(ss, narr, cue, occ)
            r = next(o for o in CHK.occ(sid_, cue) if o['i'] == ci)
            loc = r['onset'] - VL[sid_]['wavStart'] + VL[sid_]['localStart']
            ONSETS.append((key, cue, r['asr'], r['onset'], r['source'], r['kind'], r['breaths']))
            return sid_, r, loc

        def cframe(cue, d=0, occ=None):
            assert -3 <= d <= 4, (key, cue, d)
            sid_, r, loc = cue_local(cue, occ); return max(1, math.floor(loc) - 2) + d, sid_, r, loc

        def fspec(v, path, log, tlog):
            """frame spec -> (frame, cueText or None, onsetLocal or None)."""
            if isinstance(v, str): v = {'$cue': v, 'd': 0}
            if isinstance(v, dict) and '$cue' in v:
                f, sid_, r, loc = cframe(v['$cue'], v.get('d', 0), v.get('occ'))
                log.append({'path': path, 'cueText': v['$cue'], 'd': v.get('d', 0), 'sentence': sid_, 'onsetLocal': round(loc, 2), 'frame': f, **({'occ': v['occ']} if v.get('occ') else {})}); return f, v['$cue'], loc
            if isinstance(v, dict) and '$timer' in v:
                f0, sid_, r, loc = cframe(v['$timer']); f = f0 + v['d']
                tlog.append({'path': path, 'after': v['$timer'], 'd': v['d'], 'frame': f, 'why': v.get('why', '计时器驱动')}); return f, None, None
            assert isinstance(v, int), (key, path, v)
            tlog.append({'path': path, 'frame': v, 'why': '画面计时/节奏驱动（不对旁白）'}); return v, None, None

        def resolve(obj, path, log, tlog):
            if isinstance(obj, dict):
                if '$cue' in obj or '$timer' in obj: return fspec(obj, path, log, tlog)[0]
                return {k: resolve(v, f'{path}.{k}' if path else k, log, tlog) for k, v in obj.items()}
            if isinstance(obj, list): return [resolve(v, f'{path}[{j}]', log, tlog) for j, v in enumerate(obj)]
            return obj

        lay = LAYOUT[key]; els = []; anims = []
        for e0 in lay['elements']:
            e = copy.deepcopy(e0); cue = e.pop('cueText', None); cd = 0
            if isinstance(cue, dict) and '$cue' in cue: cue, cd = cue['$cue'], cue.get('d', 0)
            if isinstance(cue, dict) and '$timer' in cue:
                tl0 = []; f, _, _ = fspec(cue, 'appearFrame', [], tl0)
                e.update(appearFrame=f, timingRole='timer', cueText=''); e.setdefault('timingReason', tl0[0]['why']); e['appearTimer'] = tl0[0]
            elif cue is None:
                e.update(appearFrame=0, timingRole='structural', cueText=''); e.setdefault('timingReason', '画面底座，先于旁白存在')
            else:
                f, sid_, r, loc = cframe(cue, cd)
                e['appearFrame'] = f; e['cueText'] = cue
                e['cueOnset'] = {'sentence': sid_, 'asrFrame': round(r['asr'] - VL[sid_]['wavStart'] + VL[sid_]['localStart'], 2), 'onsetLocal': round(loc, 2),
                                 'rule': f"{r['source']}/{r['kind']}", 'delay': cd}
            if isinstance(e.get('reveal'), dict):   # readAlong: first char = appear frame, then never earlier, never backwards
                fr = [max(e['appearFrame'], f) for f in e['reveal']['frames']]; fr[0] = e['appearFrame']
                e['reveal']['frames'] = [max(fr[:i+1]) for i in range(len(fr))]
            if isinstance(e.get('dimFrom'), dict):
                dl = []; e['dimFrom'] = fspec(e['dimFrom'], 'dimFrom', dl, [])[0]
                if dl: e['dimFromCue'] = dl[0]
            dc = e.pop('disappearCue', None)
            if dc:
                f, sid_, r, loc = cframe(dc); e['disappearFrame'] = f; e['disappearCueText'] = dc
            tlog_e = []; clog_e = []
            sc_ = e.pop('stateCues', None)
            if sc_:
                kf = [{'frame': e['appearFrame'], 'state': e.get('state', 'initial')}]
                for j, s2 in enumerate(sc_):
                    s2 = dict(s2); c2 = s2.pop('cueText')
                    f, ct, loc = fspec(c2, f'stateKeyframes[{j+1}].frame', [], tlog_e)
                    k2 = dict(s2, frame=f)
                    if ct: k2.update(cueText=ct, onsetLocal=round(loc, 2))
                    else: k2['timerDriven'] = True
                    kf.append(k2)
                for k2 in kf:   # ripple bornFrame '@' = the frame of its state
                    for rp in k2.get('ripples') or []:
                        if rp.get('bornFrame') == '@': rp['bornFrame'] = k2['frame']
                e['stateKeyframes'] = sorted(kf, key=lambda k: k['frame'])
            an = e.pop('anims', None)
            if an:
                for a in an:
                    ks = []
                    for j, (fv, val) in enumerate(a['keys']):
                        ml = []; f, ct, loc = fspec(fv, f"anim.{a['property']}[{j}]", ml, tlog_e); ks.append({'frame': f, 'value': val})
                        if ct:   # cue-driven animation key: recorded in moves, cueLog points at moves[k].frame
                            mv = e.setdefault('moves', []); mv.append({'property': a['property'], 'keyIndex': j, 'frame': f, 'cueText': ct, 'd': ml[0]['d']})
                            clog_e.append(dict(ml[0], path=f'moves[{len(mv)-1}].frame'))
                    anims.append({'elementId': e['id'], 'property': a['property'], 'easing': a.get('easing', 'linear'), 'keyframes': ks, 'timerDriven': not any(isinstance(fv, dict) and '$cue' in fv for fv, _ in a['keys'])})
            if e.get('component') in NEWCOMP_FIELDS:
                log = []
                for fld in NEWCOMP_FIELDS[e['component']]:
                    if fld in e: e[fld] = resolve(e[fld], fld, log, tlog_e)
                clog_e = log + clog_e
            if clog_e: e['cueLog'] = clog_e
            if tlog_e: e['timerLog'] = tlog_e
            e.setdefault('z', 2); e.setdefault('type', 'rect')
            els.append(e)
        for e in els:
            if e.get('timingRole') == 'structural': continue
            f = e['appearFrame']
            if 'dimFrom' in e:   # dimmed placeholder dimFrom..appearFrame at dimOpacity, then 4 frames to full
                anims.append({'elementId': e['id'], 'property': 'opacity', 'easing': 'linear', 'keyframes': [{'frame': f, 'value': e['dimOpacity']}, {'frame': f+4, 'value': 1}]})
                continue
            anims.append({'elementId': e['id'], 'property': 'opacity', 'easing': 'linear', 'keyframes': [{'frame': f, 'value': 0}, {'frame': f+4, 'value': 1}]})
            anims.append({'elementId': e['id'], 'property': 'scale', 'easing': 'linear', 'keyframes': [{'frame': f, 'value': 0.9}, {'frame': f+4, 'value': 1}]})
        subs = []; pos = 0
        for j, ch in enumerate(sub_chunks(narr)):
            if j == 0: st = 0
            else:
                k0 = pos + next(ii for ii, c in enumerate(ch) if c not in PUNCT); base = 0
                for x in ss:
                    t = SENT[x]['text']
                    if k0 < base + len(t): af = SENT[x]['chars'][len(strip(t[:k0-base]))]['startFrame']; break
                    base += len(t)
                st = max(round(af - bw), subs[-1]['from'] + 1)
            if subs: subs[-1]['to'] = st - 1
            subs.append({'text': ch, 'from': st, 'to': L - 1}); pos += len(ch)
        hold = round(L - max(v['localEnd'] for v in voice))

        def FRAME_OF(lay, els, g):
            fr = lay['frame']
            if isinstance(fr, str): return fr
            E = {e['id']: e for e in els}
            return [{'from': g + (E[eid]['appearFrame'] if eid else 0), 'frame': f_, **({'switchElement': eid} if eid else {})} for f_, eid in fr]
        sh = {'id': sid, 'scriptShot': n, 'part': None, 'chapterId': CH_OF[n], 'from': g, 'durationInFrames': L, 'narration': narr,
              'subtitles': subs, 'voice': voice,
              'timing': {'source': f'voice.wav {WAV_SHA[:8]} + words.json {WORDS_SHA[:8]}', 'wavFrom': bw, 'wavTo': bw + L, 'holdFrames': 0, 'tailAfterSpeech': hold, 'holdReason': None},
              'camera': None, 'boxShot': bool(lay['box']), 'mapShot': False, 'frame': FRAME_OF(lay, els, g), 'direction': lay['direction'], 'scriptVisual': SMD[key][2],
              'elements': [dict(spec.SUB)] + els, 'animations': anims, 'transition': {'type': 'fade', 'durationInFrames': spec.TR}}
        c = CH_OF[n]
        if c not in scenes:
            t_, a_ = next((t, a) for i_, t, a in spec.CHAPTERS if i_ == c)
            scenes[c] = {'id': c, 'chapterId': c, 'title': t_, 'accent': a_, 'from': g, 'durationInFrames': 0, 'shots': []}; order.append(c)
        scenes[c]['shots'].append(sh); scenes[c]['durationInFrames'] += L; g += L
    assert g == spec.WAVLEN
    COVERS = json.loads(Path(covers_path).read_text()) if covers_path and Path(covers_path).exists() else {}
    BOXP = [s['id'] for c in order for s in scenes[c]['shots'] if s['boxShot']]
    ctx = Ctx()
    ctx.__dict__.update(WAV_SHA=WAV_SHA, WORDS_SHA=WORDS_SHA, SCRIPT_SHA=SCRIPT_SHA, SHA=SHA, g=g, FPS=spec.FPS, MAX=spec.MAX, MAX_EXC=MAX_EXC,
                        BOXP=BOXP, COVERS=COVERS, scenes=scenes, order=order,
                        chapters=[{'id': c, 'title': scenes[c]['title'], 'accent': scenes[c]['accent'], 'from': scenes[c]['from'], 'startSec': round(scenes[c]['from']/spec.FPS, 2)} for c in order])
    d = {'meta': spec.meta(ctx), 'assets': spec.ASSETS, 'scenes': [scenes[c] for c in order]}
    kit.write_json(out, d, 2)
    Path(onsets_out).write_text('# build 用到的开口（_shared/onset_rule.py）：镜 词 ASR起帧 规则开口 来源 跳过换气\n' + '\n'.join(sorted(set(f'{a} {b} {c:.2f} {o:.2f} {s}/{k} {br or "-"}' for a, b, c, o, s, k, br in ONSETS), key=lambda x: (int(x.split()[0]), x))) + '\n')
    print('frames', g, 'shots', sum(len(s['shots']) for s in d['scenes']), 'box', len(BOXP), BOXP)
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    kit.add_input_args(ap)
    ap.add_argument('--layout', help='default <episode-dir>/layout.json'); ap.add_argument('--covers', help='default <episode-dir>/covers.json (missing file -> meta.covers = {})')
    ap.add_argument('--out', help='default <episode-dir>/storyboard.json'); ap.add_argument('--onsets-out', help='default <out dir>/build-onsets.txt')
    a = ap.parse_args(argv)
    out = Path(a.out or kit.default_out(a, 'storyboard.json'))
    run(kit.load_spec(a.spec, 'build'), kit.inputs_from(a), a.layout or kit.default_out(a, 'layout.json'), a.covers or kit.default_out(a, 'covers.json'),
        out, a.onsets_out or out.parent / 'build-onsets.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
