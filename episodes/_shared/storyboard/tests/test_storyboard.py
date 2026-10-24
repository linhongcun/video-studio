"""Self-tests for episodes/_shared/storyboard (synthetic fixture only, no real voice/video).
  python3 -B episodes/_shared/storyboard/tests/test_storyboard.py
Good path: layout -> make_covers -> build_sb -> validate passes, and a rebuild is byte-identical.
Bad paths (each must be rejected): a cue moved off its onset, a text box in the subtitle band, a cover element in the
bottom 15%, narration that disagrees with the script, a storyboard whose subtitle text drifted from the script."""
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; SB = HERE.parent; FX = HERE / 'fixtures' / 'tiny'
sys.path.insert(0, str(HERE)); import make_fixture
PY = [sys.executable, '-B']


def run(script, *args):
    return subprocess.run(PY + [str(SB / script), *map(str, args)], capture_output=True, text=True)


def ok(r, what):
    assert r.returncode == 0, f'{what} failed:\n{r.stdout}\n{r.stderr}'
    return r


def bad(r, what, needle):
    out = r.stdout + r.stderr
    assert r.returncode != 0, f'{what} was accepted:\n{out}'
    assert needle in out, f'{what}: rejected but without「{needle}」:\n{out}'
    print(f'ok  rejected: {what}')


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pipeline(ep, out, layout_spec='layout_spec.py', covers_spec='covers_spec.py'):
    out.mkdir(parents=True, exist_ok=True)
    r1 = run('layout.py', '--spec', FX / layout_spec, '--episode-dir', ep, '--out', out / 'layout.json')
    if r1.returncode: return r1
    r2 = run('make_covers.py', '--spec', FX / covers_spec, '--out', out / 'covers.json')
    if r2.returncode: return r2
    return run('build_sb.py', '--spec', FX / 'build_spec.py', '--episode-dir', ep, '--layout', out / 'layout.json',
               '--covers', out / 'covers.json', '--out', out / 'storyboard.json')


def validate(ep, out, sb=None):
    return run('validate.py', '--spec', FX / 'validate_spec.py', '--episode-dir', ep, '--storyboard', sb or out / 'storyboard.json',
               '--covers', out / 'covers.json')


def main():
    with tempfile.TemporaryDirectory(prefix='sb-selftest-') as td:
        td = Path(td); ep = make_fixture.make(td / 'ep')
        a, b = td / 'a', td / 'b'
        ok(pipeline(ep, a), 'good pipeline'); r = ok(validate(ep, a), 'validate (good)')
        assert '错误 0' in r.stdout and '失败 0' in r.stdout, r.stdout
        print('ok  good fixture:', r.stdout.strip().splitlines()[-1])
        ok(pipeline(ep, b), 'rebuild')
        for f in ('layout.json', 'covers.json', 'storyboard.json', 'build-onsets.txt'):
            assert sha(a / f) == sha(b / f), f'{f} not deterministic'
        print('ok  rebuild byte-identical (layout/covers/storyboard/build-onsets)')
        # --inputs map + --input override resolve the same files
        m = td / 'inputs.json'; m.write_text(json.dumps({'_note': 'test', 'voice.wav': str(ep / 'voice.wav')}))
        c = td / 'c'; c.mkdir()
        ok(run('layout.py', '--spec', FX / 'layout_spec.py', '--episode-dir', ep, '--inputs', m, '--input', f'words.json={ep / "words.json"}',
               '--out', c / 'layout.json'), 'layout via --inputs/--input')
        assert sha(c / 'layout.json') == sha(a / 'layout.json'); print('ok  --inputs / --input resolve to the same layout')

        # bad 1: a cue frame moved 6 frames after its onset
        d = json.loads((a / 'storyboard.json').read_text())
        e = next(e for sc in d['scenes'] for s in sc['shots'] for e in s['elements'] if e['id'] == 'hello'); e['appearFrame'] += 6
        p = td / 'bad-cue.json'; p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
        bad(validate(ep, a, p), 'cue appearFrame +6 after onset', 'FAIL')
        # bad 2: subtitle drifted from the script
        d = json.loads((a / 'storyboard.json').read_text()); d['scenes'][0]['shots'][0]['subtitles'][0]['text'] = '你好地球。'
        p = td / 'bad-sub.json'; p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
        bad(validate(ep, a, p), 'subtitle text differs from script', '字幕非逐字')
        # bad 3: layout puts a text box into the subtitle band
        e3 = td / 'e3'; ok(pipeline(ep, e3, layout_spec='layout_bad_spec.py'), 'bad-layout build')
        bad(validate(ep, e3), 'element in subtitle band', '进字幕带')
        # bad 4: cover element in the bottom 15% -> make_covers refuses, no covers.json
        e4 = td / 'e4'; e4.mkdir()
        bad(run('make_covers.py', '--spec', FX / 'covers_bad_spec.py', '--out', e4 / 'covers.json'), 'cover in bottom 15%', 'AssertionError')
        assert not (e4 / 'covers.json').exists()
        # bad 5: narration.py disagrees with script.md -> build_sb refuses
        (ep / 'narration.py').write_text("N = ('你好世界。', '再见。')\n")
        bad(pipeline(ep, td / 'e5'), 'narration.py != script 旁白', '旁白')
    print('storyboard selftest ok')


if __name__ == '__main__':
    main()
