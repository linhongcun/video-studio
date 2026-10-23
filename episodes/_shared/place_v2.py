"""Place a voice track for Remotion.

--mode whole (default): EP.05 onward. The source wav is already the timeline
at frame 0. Check shots[].voice against it, then copy the bytes (a real file,
not a symlink).

--mode place: EP.02–04. Cut each sentence from wavStart..wavEnd and lay it at
from + localStart, then -16 LUFS and a tanh knee. Numerics match the legacy
cookie-v1 script.

  python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole
  python3 episodes/_shared/place_v2.py --dir EPDIR --mode place
  python3 episodes/_shared/place_v2.py --selftest
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 48000
FPS = 30


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _ensure_parent(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def copy_real(src, dest):
    """Copy bytes. An existing symlink is removed so dest is a regular file."""
    _ensure_parent(dest)
    if os.path.lexists(dest) and os.path.islink(dest):
        os.remove(dest)
    shutil.copyfile(src, dest)


def _shots(sb):
    return [x for sc in sb['scenes'] for x in sc['shots']]


def _voice_rows(sb):
    rows = []
    for sh in _shots(sb):
        for v in sh.get('voice') or []:
            rows.append((sh, v))
    return rows


def measure_lufs(samples):
    r = subprocess.run(
        ['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
         '-af', 'ebur128=peak=true', '-f', 'null', '-'],
        input=np.asarray(samples, np.float32).tobytes(), capture_output=True)
    text = r.stderr.decode()
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', text)[-1])


def _read_s16(path):
    w = wave.open(path)
    rate, ch, width, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    if rate != SR or ch != 1 or width != 2:
        return None, f'want 48 kHz mono s16, got {rate} Hz ch {ch} width {width}'
    samples = np.frombuffer(raw, '<i2').astype(np.float32) / 32767
    return samples, None


def place(sb_path, src_path, out_path, copy_to, report_path, lufs_target=-16.0, knee=0.7):
    sb = json.load(open(sb_path))
    TOT = sb['meta']['durationInFrames']
    src, err = _read_s16(src_path)
    if err:
        print(err)
        return 1
    rows = []
    shots = _shots(sb)
    for sh in shots:
        for v in sh.get('voice') or []:
            a = round(v['wavStart'] * SR / FPS)
            b = round(v['wavEnd'] * SR / FPS)
            x = src[a:b].copy()
            st = round((sh['from'] + v['localStart']) * SR / FPS)
            endShot = next(s for s in shots if s['id'] == v['spansInto']) if v.get('spansInto') else sh
            rows.append(dict(id=v['id'], shot=sh['id'], sbStart=sh['from'] + v['localStart'], sbEnd=sh['from'] + v['localEnd'],
                              start=st, end=st + len(x), x=x, shotEnd=endShot['from'] + endShot['durationInFrames']))
    N = TOT * SR // FPS
    tr = np.zeros(N, np.float32)
    bad = []
    gaps = []
    for a, b in zip(rows, rows[1:]):
        g = (b['start'] - a['end']) * FPS / SR
        gaps.append(g)
        if g < 0:
            bad.append(('overlap', a['id'], b['id'], round(g, 2)))
    for r in rows:
        if r['end'] > N:
            bad.append((r['id'], 'past end'))
        if r['end'] / 1600 > r['shotEnd'] + 0.5:
            bad.append((r['id'], 'past shot', round(r['end'] / 1600 - r['shotEnd'], 1)))
        tr[r['start']:r['end']] += r['x']
    g = 10 ** ((lufs_target - measure_lufs(tr)) / 20)
    tr *= g
    for _ in range(3):
        a = np.abs(tr)
        tr = np.where(a > knee, np.sign(tr) * (knee + 0.08 * np.tanh((a - knee) / 0.08)), tr).astype(np.float32)
        tr *= 10 ** ((lufs_target - measure_lufs(tr)) / 20)
    pk = float(np.abs(tr).max())
    jump = max(max(float(np.abs(np.diff(tr[max(0, r['start'] - 480):r['start'] + 480])).max()),
                   float(np.abs(np.diff(tr[r['end'] - 480:min(N, r['end'] + 480)])).max())) for r in rows)
    edge = max(max(abs(float(r['x'][0])), abs(float(r['x'][-1]))) for r in rows) * g
    _ensure_parent(out_path)
    w = wave.open(out_path, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(tr, -1, 1) * 32767).astype('<i2').tobytes())
    w.close()
    if copy_to:
        copy_real(out_path, copy_to)
    out = dict(
        storyboard=hashlib.sha256(open(sb_path, 'rb').read()).hexdigest()[:8],
        source=hashlib.sha256(open(src_path, 'rb').read()).hexdigest()[:8],
        frames=TOT, samples=N, gainDb=round(20 * np.log10(g), 3), lufs=measure_lufs(tr), peak=pk,
        minGapFrames=round(min(gaps), 2), violations=bad, maxSpliceJump=jump, clipEdgeAbs=edge,
        sha=hashlib.sha256(open(out_path, 'rb').read()).hexdigest(),
        sentences=[dict(id=r['id'], shot=r['shot'], start=round(r['start'] / 1600, 2), end=round(r['end'] / 1600, 2),
                         sbStart=r['sbStart'], sbEnd=r['sbEnd'], endDiff=round(r['end'] / 1600 - r['sbEnd'], 2)) for r in rows])
    _ensure_parent(report_path)
    json.dump(out, open(report_path, 'w'), ensure_ascii=False, indent=1)
    print({k: v for k, v in out.items() if k != 'sentences'}, len(rows), 'maxEndDiff', max(abs(s['endDiff']) for s in out['sentences']))
    return 0


def whole(sb_path, src_path, copy_to, report_path, tol=0.5):
    sb = json.load(open(sb_path))
    frames = sb['meta']['durationInFrames']
    w = wave.open(src_path)
    rate, ch, width, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    w.close()
    violations = []
    if rate != SR or ch != 1 or width != 2:
        violations.append({'id': 'track', 'kind': 'format', 'rate': rate, 'channels': ch, 'width': width})
    expected = frames * SR / FPS
    if n != expected:
        violations.append({'id': 'track', 'kind': 'length', 'samples': n, 'expected': expected})
    offsets = []
    prev = None
    for sh, v in _voice_rows(sb):
        off = sh['from'] + v['localStart'] - v['wavStart']
        offsets.append(abs(off))
        if abs(off) > tol:
            violations.append({'id': v['id'], 'kind': 'offset', 'frames': round(abs(off), 2)})
        if v['wavEnd'] > frames:
            violations.append({'id': v['id'], 'kind': 'wavEnd', 'wavEnd': v['wavEnd']})
        if prev is not None and v['wavStart'] < prev[0]:
            violations.append({'id': v['id'], 'kind': 'overlap', 'prev': prev[1]})
        prev = (v['wavEnd'], v['id'])
    if violations:
        for item in violations:
            print('violation', item.get('id'), item.get('kind'))
        return 1
    if copy_to:
        copy_real(src_path, copy_to)
        sha = _sha256(copy_to)
    else:
        sha = _sha256(src_path)
    out = dict(
        mode='whole',
        storyboard=_sha256(sb_path)[:8],
        source=_sha256(src_path)[:8],
        frames=frames,
        samples=n,
        maxOffsetFrames=round(max(offsets) if offsets else 0.0, 2),
        violations=[],
        sha=sha,
    )
    _ensure_parent(report_path)
    json.dump(out, open(report_path, 'w'), ensure_ascii=False, indent=1)
    print(out)
    return 0


def _write_wav(path, samples):
    w = wave.open(path, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
    w.close()


def selftest():
    d = tempfile.mkdtemp(prefix='place-v2-')
    frames = 120
    x = np.zeros(frames * SR // FPS, np.float32)
    voices = [
        dict(id='v1', wavStart=5.25, wavEnd=20.25, localStart=5, localEnd=20),
        dict(id='v2', wavStart=30.4, wavEnd=45.4, localStart=30, localEnd=45, spansInto='02-b'),
        dict(id='v3', wavStart=70.1, wavEnd=85.1, localStart=10, localEnd=25),
    ]
    for v in voices:
        a = round(v['wavStart'] * SR / FPS)
        b = round(v['wavEnd'] * SR / FPS)
        x[a:b] = 0.2
    src = os.path.join(d, 'voice.wav')
    _write_wav(src, x)
    sb = {
        'meta': {'durationInFrames': frames},
        'scenes': [{'shots': [
            {'id': '01-a', 'from': 0, 'durationInFrames': 60, 'voice': [voices[0], voices[1]]},
            {'id': '02-b', 'from': 60, 'durationInFrames': 60, 'voice': [voices[2]]},
        ]}],
    }
    sb_path = os.path.join(d, 'storyboard.json')
    json.dump(sb, open(sb_path, 'w'))
    link_target = os.path.join(d, 'link-target.wav')
    open(link_target, 'wb').write(b'not-the-audio')
    copy_to = os.path.join(d, 'public.wav')
    os.symlink(link_target, copy_to)
    report = os.path.join(d, 'whole.json')
    rc = main(['--dir', d, '--mode', 'whole', '--src', src, '--storyboard', sb_path, '--copy-to', copy_to, '--report', report])
    assert rc == 0, rc
    assert not os.path.islink(copy_to) and os.path.isfile(copy_to)
    assert open(copy_to, 'rb').read() == open(src, 'rb').read()
    assert open(link_target, 'rb').read() == b'not-the-audio'
    rep = json.load(open(report))
    assert rep['violations'] == [] and rep['mode'] == 'whole'
    assert rep['maxOffsetFrames'] == 0.4, rep
    bad_sb = json.loads(json.dumps(sb))
    bad_sb['scenes'][0]['shots'][0]['voice'][0]['localStart'] = 7
    bad_path = os.path.join(d, 'bad.json')
    json.dump(bad_sb, open(bad_path, 'w'))
    nowhere = os.path.join(d, 'no-write.wav')
    norep = os.path.join(d, 'no-write.json')
    rc = main(['--dir', d, '--mode', 'whole', '--src', src, '--storyboard', bad_path, '--copy-to', nowhere, '--report', norep])
    assert rc == 1, rc
    assert not os.path.exists(nowhere) and not os.path.exists(norep)
    if shutil.which('ffmpeg') is None:
        print('place selftest skipped: ffmpeg not on PATH')
        return True
    placed = os.path.join(d, 'placed.wav')
    preport = os.path.join(d, 'place.json')
    pcopy = os.path.join(d, 'placed-copy.wav')
    rc = main(['--dir', d, '--mode', 'place', '--src', src, '--storyboard', sb_path,
               '--out', placed, '--copy-to', pcopy, '--report', preport])
    assert rc == 0, rc
    pr = json.load(open(preport))
    assert pr['violations'] == [], pr['violations']
    assert abs(pr['lufs'] + 16) <= 0.1, pr['lufs']
    w = wave.open(placed)
    pcm = np.frombuffer(w.readframes(w.getnframes()), '<i2')
    w.close()
    expect = []
    for sh in sb['scenes'][0]['shots']:
        for v in sh['voice']:
            expect.append(round((sh['from'] + v['localStart']) * 1600))
    nz = np.flatnonzero(pcm)
    starts = [int(nz[0])]
    for i in range(1, len(nz)):
        if nz[i] != nz[i - 1] + 1:
            starts.append(int(nz[i]))
    assert starts == expect, (starts, expect)
    ov = {
        'meta': {'durationInFrames': frames},
        'scenes': [{'shots': [{
            'id': '01-a', 'from': 0, 'durationInFrames': frames,
            'voice': [
                dict(id='a', wavStart=5.25, wavEnd=20.25, localStart=10, localEnd=25),
                dict(id='b', wavStart=30.4, wavEnd=45.4, localStart=12, localEnd=27),
            ],
        }]}],
    }
    ov_path = os.path.join(d, 'overlap.json')
    json.dump(ov, open(ov_path, 'w'))
    ov_out = os.path.join(d, 'overlap.wav')
    ov_rep = os.path.join(d, 'overlap.json.report')
    rc = main(['--dir', d, '--mode', 'place', '--src', src, '--storyboard', ov_path,
               '--out', ov_out, '--no-copy', '--report', ov_rep])
    assert rc == 0, rc
    orep = json.load(open(ov_rep))
    assert any(item[0] == 'overlap' for item in orep['violations']), orep['violations']
    print('place selftest ok')
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='.')
    ap.add_argument('--mode', choices=('whole', 'place'), default='whole')
    ap.add_argument('--storyboard', default=None)
    ap.add_argument('--src', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--copy-to', default=None)
    ap.add_argument('--no-copy', action='store_true')
    ap.add_argument('--report', default=None)
    ap.add_argument('--lufs', type=float, default=-16.0)
    ap.add_argument('--knee', type=float, default=0.7)
    ap.add_argument('--tol', type=float, default=0.5)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    D = a.dir
    sb_path = a.storyboard or os.path.join(D, 'storyboard.json')
    src_path = a.src or os.path.join(D, 'voice.wav')
    report_path = a.report or os.path.join(D, 'voice', 'place_v2.json')
    copy_to = None if a.no_copy else (a.copy_to or os.path.join(D, 'remotion', 'public', 'audio', 'voice.wav'))
    if a.mode == 'whole':
        return whole(sb_path, src_path, copy_to, report_path, tol=a.tol)
    out_path = a.out or os.path.join(D, 'voice', 'placed.wav')
    return place(sb_path, src_path, out_path, copy_to, report_path, lufs_target=a.lufs, knee=a.knee)


if __name__ == '__main__':
    sys.exit(main())
