#!/usr/bin/env python3
"""Voice-step tests. No network, no TTS, no whisper model.

synthetic(): a made-up 2-shot script run through prep, cue_tests, gen (with a
local stand-in for mimo_say.py that writes tone-burst "takes", each with a
"好" tail after 300 ms of silence), build, a fake asr.json, onsets,
lastword_fix, cues_rule, shot_frames, selfcheck.
Needs ffmpeg, scipy and soundfile; skipped when any is missing.

regression(): EP.14 degradation, from the repo voice.wav + script.md and the
frozen fixtures in tests/golden/degradation/voice/ (build.json, asr.json,
cue_tests.json; the picked takes are not in the repo, so build.py and ASR are
not rerun). Checks sents.json, words.json, cues.json, shot_frames.json and
selfcheck against EP.14. Set VOICE_REG_TAKES=/path/to/takes (EP.14 picked
takes) to also rebuild voice.wav and require sha 9e70470c. Never writes into
the episode.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'episodes/_shared/voice'
G = ROOT / 'episodes/_shared/tests/golden/degradation/voice'
EP = ROOT / 'episodes/degradation'
WAV_SHA = '9e70470c096c4198f679eceb5323b0cd9f90323784e7dad284dc43c47265468b'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(script, d, *extra):
    r = subprocess.run([sys.executable, str(V / script), '--dir', str(d), *extra], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, (script, r.stdout[-2000:], r.stderr[-2000:])
    return r.stdout


def have(*mods):
    if not shutil.which('ffmpeg'): return False
    try:
        for m in mods: __import__(m)
    except ImportError:
        return False
    return True


SCRIPT = """# 合成测试
### 1 alpha
画面：标题「甲乙」出现。
旁白：甲乙丙丁。戊己庚。
### 2 beta
画面：「辛壬」高亮，「不在旁白」不算。
旁白：辛壬癸子。
"""


STUB = r"""
import argparse, re, numpy as np, soundfile as sf
ap = argparse.ArgumentParser(); ap.add_argument('--text'); ap.add_argument('--out'); ap.add_argument('--style'); a = ap.parse_args()
sr = 24000; n = len(re.sub(r'[^\w]', '', a.text)) - 1; t = np.arange(int(.22*sr))/sr; env = np.minimum(1, np.minimum(t, t[::-1])/.02)
parts = [np.zeros(int(.1*sr))]
for k in range(n): parts += [0.3*env*np.sin(2*np.pi*(180+20*k)*t), np.zeros(int(.04*sr))]
parts += [np.zeros(int(.26*sr)), 0.3*env*np.sin(2*np.pi*150*t), np.zeros(int(.2*sr))]
sf.write(a.out, np.concatenate(parts).astype(np.float32), sr)
"""


def synthetic():
    if not have('numpy', 'scipy', 'soundfile'):
        print('skip voice synthetic test, needs ffmpeg + numpy + scipy + soundfile'); return
    import numpy as np, soundfile as sf
    d = Path(tempfile.mkdtemp(prefix='voice-syn-')); (d / 'script.md').write_text(SCRIPT, encoding='utf-8')
    run('prep.py', d)
    S = json.loads((d / 'voice/sents.json').read_text(encoding='utf-8'))
    assert [s['id'] for s in S] == ['01-alpha-1', '01-alpha-2', '02-beta-1'], S
    assert S[0]['tts'] == '甲乙丙丁。好。' and S[2]['shot'] == '02-beta'
    run('cue_tests.py', d)
    T = json.loads((d / 'voice/cue_tests.json').read_text(encoding='utf-8'))
    assert T == [['01-alpha', '甲乙'], ['02-beta', '辛壬']], T
    # takes via gen.py, with a stand-in for mimo_say.py (params.json tts.script): one 0.22 s tone burst
    # per char, 40 ms gaps, then 300 ms silence + a "好" burst; written at 24 kHz so gen.py's resample runs
    stub = d / 'stub_say.py'; stub.write_text(STUB, encoding='utf-8')
    (d / 'voice/params.json').write_text(json.dumps({'tts': {'script': str(stub)}}), encoding='utf-8')
    run('gen.py', d)
    for s in S:
        f = d / f"voice/takes/{s['id']}-a.wav"; assert sf.info(str(f)).samplerate == 48000, f
        assert json.loads(f.with_suffix('.txt.json').read_text(encoding='utf-8')) == s['tts']
    (d / 'voice/params.json').unlink()
    run('build.py', d)
    B = json.loads((d / 'voice/build.json').read_text(encoding='utf-8')); m = B['summary']
    info = sf.info(str(d / 'voice.wav'))
    assert info.samplerate == 48000 and info.channels == 1 and info.subtype == 'PCM_16'
    assert m['samples'] == info.frames and m['samples'] % 1600 == 0 and m['frames'] == m['samples']//1600
    assert abs(m['track_lufs']+16) < 0.6, m
    assert m['sha'] == sha(d / 'voice.wav')
    assert m['extraAfter'].get('01-alpha', 0) > 0, m   # alpha is far shorter than 225 frames
    # fake ASR: one word per char, 0.26 s apart from the sentence start (cut keeps 30 ms lead)
    A = []
    for r in B['sentences']:
        f0 = r['startSample']/1600; W = []
        for k, c in enumerate(r['text'].rstrip('。')):
            W.append(dict(w=c, startFrame=round(f0+0.9+k*7.8, 1), endFrame=round(f0+0.9+k*7.8+6.6, 1)))
        A.append(dict(id=r['id'], asr=r['text'], cov=1.0, words=W))
    (d / 'voice/asr.json').write_text(json.dumps(A, ensure_ascii=False, indent=1), encoding='utf-8')
    run('onsets.py', d); run('lastword_fix.py', d); run('cues_rule.py', d); run('shot_frames.py', d)
    W = json.loads((d / 'words.json').read_text(encoding='utf-8'))
    sh = W['shots']; assert [q['id'] for q in sh] == ['01-alpha', '02-beta']
    assert sh[0]['startFrame'] == 0 and sh[0]['endFrame'] == sh[1]['startFrame'] and sh[1]['endFrame'] == W['durationFrames'] == m['frames']
    assert sh[0]['durationFrames'] >= 225, sh[0]
    for q in sh:
        for s in q['sentences']:
            st = [c['startFrame'] for c in s['chars']]; assert st == sorted(st) and s['startFrame']-1 <= st[0] < s['endFrame'], s['id']
    C = json.loads((d / 'voice/cues.json').read_text(encoding='utf-8'))
    assert [c['cue'] for c in C] == ['甲乙', '辛壬'] and all(c['onsetSource'].startswith('onset_rule') for c in C), C
    sys.path.insert(0, str(V)); import shot_frames
    F = json.loads((d / 'voice/shot_frames.json').read_text(encoding='utf-8'))
    assert F == shot_frames.derive(W) and F['shots'][1]['startFrame'] == sh[1]['startFrame']
    out = run('selfcheck.py', d); assert 'selfcheck ok' in out, out
    shutil.rmtree(d)
    print('voice synthetic ok')


def regression():
    need = [EP / 'script.md', EP / 'words.json', EP / 'remotion/public/audio/voice.wav', G / 'build.json', G / 'asr.json', G / 'cue_tests.json']
    if not all(p.exists() for p in need) or not have('numpy', 'soundfile'):
        print('skip voice regression, missing EP.14 files, ffmpeg or soundfile'); return
    wav = EP / 'remotion/public/audio/voice.wav'; assert sha(wav) == WAV_SHA
    d = Path(tempfile.mkdtemp(prefix='voice-reg-')); (d / 'voice').mkdir()
    shutil.copy(EP / 'script.md', d); shutil.copy(wav, d / 'voice.wav')
    for f in ('build.json', 'asr.json', 'cue_tests.json', 'picks.json'): shutil.copy(G / f, d / 'voice')
    run('prep.py', d); assert (d / 'voice/sents.json').read_bytes() == (G / 'sents.json').read_bytes()
    tk = os.environ.get('VOICE_REG_TAKES')
    if tk:
        os.symlink(tk, d / 'voice/takes'); run('build.py', d)
        assert sha(d / 'voice.wav') == WAV_SHA and (d / 'voice/build.json').read_bytes() == (G / 'build.json').read_bytes()
        print('voice build regression ok (VOICE_REG_TAKES)')
    run('onsets.py', d); run('lastword_fix.py', d); run('cues_rule.py', d); run('shot_frames.py', d)
    got = json.loads((d / 'words.json').read_text(encoding='utf-8')); exp = json.loads((EP / 'words.json').read_text(encoding='utf-8'))
    exp['scriptSha256'] = got['scriptSha256']   # repo script.md differs from EP.14's only in 画面 lines
    assert got == exp, 'words.json differs from episodes/degradation/words.json'
    for f in ('cues.json', 'shot_frames.json'):
        assert (d / 'voice' / f).read_bytes() == (G / f).read_bytes(), f
    out = run('selfcheck.py', d); assert 'selfcheck ok' in out, out
    shutil.rmtree(d)
    print('voice regression ok (EP.14 words/cues/shot_frames)')


if __name__ == '__main__':
    synthetic()
    regression()
