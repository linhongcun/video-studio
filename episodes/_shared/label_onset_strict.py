"""Strict label-onset checker. Window -6..+2 is applied here; onset maths stay in onset_rule.py.

Usage:
  python3 episodes/_shared/label_onset_strict.py --dir EPDIR [--exc 06,18] [--out FILE]
  python3 episodes/_shared/label_onset_strict.py --dir EPDIR --words 红包,降级
  python3 episodes/_shared/label_onset_strict.py --selftest
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onset_rule as R


def main(argv=None, default_output="label-onset-strict.txt"):
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='.')
    ap.add_argument('--exc', default='')
    ap.add_argument('--words', default='')
    ap.add_argument('--out', default=None)
    ap.add_argument('--wav', default=None)
    ap.add_argument('--words-json', default=None)
    ap.add_argument('--storyboard', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        print('selftest ok')
        return 0
    D = a.dir
    sb_path = a.storyboard or f'{D}/storyboard.json'
    if not a.words and not os.path.exists(sb_path):
        ap.error('list mode without storyboard.json requires --words')
    assert R.selftest()
    wav_path = a.wav or (f'{D}/voice.wav' if os.path.exists(f'{D}/voice.wav') else f'{D}/remotion/public/audio/voice.wav')
    words_path = getattr(a, 'words_json') or f'{D}/words.json'
    sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
    W = json.load(open(words_path))
    w = wave.open(wav_path)
    sr = w.getframerate()
    X = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32767
    w.close()
    rule = R.Rule(X, sr)
    SEN = [s for sh in W['shots'] for s in sh['sentences']]
    S = {s['id']: s for s in SEN}
    norm = lambda t: re.sub(r'[^\u4e00-\u9fffA-Za-z0-9.]', '', t).upper()

    def ctx(sid, i):
        s = S[sid]
        c = s['chars']
        if i > 0:
            return c[i - 1]['startFrame'], c[i - 1]['endFrame']
        k = SEN.index(s)
        return (SEN[k - 1]['chars'][-1]['startFrame'], SEN[k - 1]['chars'][-1]['endFrame']) if k else (None, None)

    def find(sids, cue):
        out = []
        for sid in sids:
            t = ''.join(c['ch'].upper() for c in S[sid]['chars'])
            cn = norm(cue)
            i = t.find(cn)
            while i >= 0:
                ch = S[sid]['chars'][i]
                ps, pe = ctx(sid, i)
                r = rule.onset(ch['startFrame'], ch['endFrame'], ps, pe)
                out.append(dict(sid=sid, i=i, asr=ch['startFrame'], atEnd=i + len(cn) == len(t), **r))
                i = t.find(cn, i + 1)
        return out

    hdr = f"# Nolan onset rule (onset_rule.py) on voice {sha(wav_path)} / words {sha(words_path)}"
    lines = [hdr]
    fail = 0
    if a.words:
        lines.append('word | sentence | words.json ASR start | rule onset | rule-ASR | source | pause | breaths skipped')
        for wd in a.words.split(','):
            for r in find([s['id'] for s in SEN], wd):
                lines.append(f"{wd} | {r['sid']} | {r['asr']:.2f} | {r['onset']:.2f} | {r['onset'] - r['asr']:+.2f} | {r['source']}/{r['kind']} | {r['pause']} | {r['breaths'] or '-'}{'  (sentence-end word)' if r['atEnd'] else ''}")
    else:
        EXC = set(x for x in a.exc.split(',') if x)
        sb = json.load(open(sb_path))
        lines[0] += f" / storyboard {sha(sb_path)}, window -6..+2"
        shots = [x for sc in sb['scenes'] for x in sc['shots']]
        place = {v['id']: (sh, v) for sh in shots for v in sh['voice']}
        cands = lambda sh: [v['id'] for v in sh['voice']] + [v['id'] for o in shots for v in o['voice'] if v.get('spansInto') == sh['id']]
        fail = exc = 0
        rows = []
        for sh in shots:
            for e in sh['elements']:
                if e.get('role') == 'subtitle':
                    continue
                evs = [('appear', e.get('appearFrame'), e['cueText'])] if e.get('cueText') else []
                if e.get('disappearCueText'):
                    evs.append(('disappear', e['disappearFrame'], e['disappearCueText']))
                evs += [('state:' + k['state'], k['frame'], k['cueText']) for k in e.get('stateKeyframes', []) if k.get('cueText')]
                for c in e.get('cueLog', []):
                    if not c.get('cueText'):
                        continue
                    o = e
                    for p in re.findall(r'(\w+)(?:\[(\d+)\])?', c['path']):
                        o = o[p[0]]
                        o = o[int(p[1])] if p[1] else o
                    if o != c['frame']:
                        rows.append(f"{sh['id']}/{e['id']} cueLog {c['path']} value {o} != logged {c['frame']} MISMATCH")
                        fail += 1
                    evs.append(('map:' + c['path'], o - c.get('d', 0), c['cueText']))
                for kind, fr, cue in evs:
                    best = None
                    for r in find(cands(sh), cue):
                        psh, v = place[r['sid']]
                        off = psh['from'] + v['localStart'] - v['wavStart']
                        g = sh['from'] + fr
                        d = g - (r['onset'] + off)
                        if best is None or abs(d + 2) < abs(best[0] + 2):
                            best = (d, r, r['onset'] + off, g)
                    if best is None:
                        rows.append(f"{sh['id']}/{e['id']} {kind}「{cue}」 NOT FOUND")
                        fail += 1
                        continue
                    d, r, on, g = best
                    ok = -6 <= d <= 2
                    tag = 'OK' if ok else ('EXCEPTION' if sh['id'][:2] in EXC else 'FAIL')
                    fail += tag == 'FAIL'
                    exc += tag == 'EXCEPTION'
                    rows.append(f"{sh['id']}/{e['id']} {kind}「{cue}」 at {g} onset {on:.2f} ({r['source']}/{r['kind']}) diff {d:+.2f} {tag}{'  FLAG:sentence-end cue' if r['atEnd'] else ''}")
        lines += rows + ['', f"{len(rows)} cues, {fail} fail, {exc} approved exceptions"]
    txt = '\n'.join(lines) + '\n'
    open(a.out or f'{D}/{default_output}', 'w').write(txt)
    print(txt, end='')
    return int(fail > 0)


def _write_wav(path, samples):
    w = wave.open(path, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(48000)
    w.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
    w.close()


def _read_rule(path):
    w = wave.open(path)
    x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32767
    sr = w.getframerate()
    w.close()
    return R.Rule(x, sr)


def selftest():
    assert R.selftest()
    d = tempfile.mkdtemp(prefix='label-onset-')
    sr = 48000
    n = 120 * 1600
    x = np.zeros(n, np.float64)
    t = np.arange(n) / sr

    def burst(f0, f1):
        a, b = int(f0 * 1600), int(f1 * 1600)
        x[a:b] = 0.2 * np.sin(2 * np.pi * 150 * t[a:b])

    burst(30, 50)
    burst(90, 110)
    wav = os.path.join(d, 'voice.wav')
    _write_wav(wav, x)
    rule = _read_rule(wav)
    r_hong = rule.onset(30, 45, None, None)
    r_bao = rule.onset(90, 105, 30, 45)
    ok_frame = r_hong['onset'] - 2
    fail_frame = r_bao['onset'] + 5
    words = {
        'shots': [{
            'sentences': [{
                'id': 's1',
                'chars': [
                    {'ch': '红', 'startFrame': 30, 'endFrame': 45},
                    {'ch': '包', 'startFrame': 90, 'endFrame': 105},
                ],
            }],
        }],
    }
    sb = {
        'scenes': [{
            'shots': [{
                'id': '01-lab',
                'from': 0,
                'voice': [{'id': 's1', 'wavStart': 0, 'localStart': 0, 'wavEnd': 120, 'localEnd': 120}],
                'elements': [
                    {'id': 'zz-sub', 'role': 'subtitle', 'cueText': '没有这个', 'appearFrame': 999},
                    {
                        'id': 'ok',
                        'cueText': '红',
                        'appearFrame': ok_frame,
                        'cueLog': [
                            {'path': 'appearFrame', 'frame': 1, 'd': 0, 'cueText': '红'},
                            {'path': 'appearFrame', 'frame': ok_frame, 'd': 0},
                        ],
                    },
                    {'id': 'bad', 'cueText': '包', 'appearFrame': fail_frame},
                    {'id': 'miss', 'cueText': '没有这个', 'appearFrame': 10},
                ],
            }],
        }],
    }
    json.dump(words, open(os.path.join(d, 'words.json'), 'w'), ensure_ascii=False)
    json.dump(sb, open(os.path.join(d, 'storyboard.json'), 'w'), ensure_ascii=False)
    out = os.path.join(d, 'label-onset-strict.txt')
    code = main(['--dir', d, '--out', out])
    text = open(out).read()
    assert code == 1, text
    assert text.splitlines()[0].endswith('/ storyboard ' + hashlib.sha256(open(os.path.join(d, 'storyboard.json'), 'rb').read()).hexdigest()[:8] + ', window -6..+2')
    assert '01-lab/zz-sub' not in text
    assert 'MISMATCH' in text
    assert 'NOT FOUND' in text
    assert any(ln.startswith('01-lab/ok appear') and ln.split()[-1].rstrip() and ' OK' in ln for ln in text.splitlines())
    bad = [ln for ln in text.splitlines() if ln.startswith('01-lab/bad ')]
    assert len(bad) == 1 and ' FAIL' in bad[0] and 'EXCEPTION' not in bad[0], bad
    assert '5 cues, 3 fail, 0 approved exceptions' in text, text
    out2 = os.path.join(d, 'exc.txt')
    code2 = main(['--dir', d, '--exc', '01', '--out', out2])
    text2 = open(out2).read()
    assert code2 == 1, text2
    bad2 = [ln for ln in text2.splitlines() if ln.startswith('01-lab/bad ')]
    assert len(bad2) == 1 and ' EXCEPTION' in bad2[0] and ' FAIL' not in bad2[0], bad2
    assert '5 cues, 2 fail, 1 approved exceptions' in text2, text2
    listed = os.path.join(d, 'list.txt')
    assert main(['--dir', d, '--words', '红', '--out', listed]) == 0
    assert '红 | s1 |' in open(listed).read()
    empty = tempfile.mkdtemp(prefix='label-onset-empty-')
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            main(['--dir', empty])
    except SystemExit as e:
        assert e.code == 2, e.code
    else:
        raise AssertionError('missing storyboard without --words must error')
    assert '--words' in err.getvalue()
    return True


if __name__ == '__main__':
    sys.exit(main())
