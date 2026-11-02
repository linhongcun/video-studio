#!/usr/bin/env python3
"""Bounded read-only RGB-reference investigation; original FAIL/PNG/video/thresholds stay unchanged."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

Q = Path(__file__).resolve().parent
ROOT = next(p for p in Q.parents if (p / 'AGENTS.md').is_file())
A = ROOT / 'docs/archive/2026-11/mq05-consumer-replay'
D = ROOT / 'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2'
VIDEO = D / 'video.mp4'
S = A / 'site-local'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
target = Q / 'report.json'
assert not target.exists() and not (Q / 'rgb').exists(), 'Preserve earlier raw color attempts'
before = {str(p.relative_to(ROOT)): sha(p) for p in [VIDEO, D / 'source-sha256.json',
    A / 'qa/compare-browser-video.py', A / 'qa/local-native-color.json', S / 'report.machine-only.json']}
native = read(S / 'report.machine-only.json')
final = read(D / 'qa-final-independent/encoded-independent.json')
original = read(A / 'qa/local-native-color.json')
assert native['pass'] and final['machinePass'] and original['pass'] is False
assert sha(VIDEO) == native['videoSha256'] == final['videoSHA256'] == original['videoSHA256']
thresholds = original['thresholds']
assert thresholds == {'meanAbsoluteChannelErrorMax': 1.5, 'p95AbsoluteChannelErrorMax': 3, 'backgroundPointChannelErrorMax': 3}
frames = sorted({x['frame'] for x in native['exactFrames']})
out = Q / 'rgb'
out.mkdir()
selection = '+'.join(f'eq(n,{n})' for n in frames)
vf = (f"select='{selection}',"
      'scale=iw:ih:in_range=tv:out_range=pc:in_color_matrix=bt709:flags=accurate_rnd+full_chroma_int,format=rgb24')
command = ['ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-filter_threads', '1',
           '-i', str(VIDEO), '-map', '0:v:0', '-vf', vf, '-fps_mode', 'vfr', str(out / 'frame-%03d.png')]
run = subprocess.run(command, capture_output=True, text=True)
(Q / 'accurate-decode.stderr.txt').write_text(run.stderr)
(Q / 'accurate-decode-attempt.json').write_text(json.dumps({'command': command, 'exit': run.returncode,
    'stderr': run.stderr, 'videoSHA256': sha(VIDEO)}, indent=2) + '\n')
assert run.returncode == 0 and not run.stderr
pngs = sorted(out.glob('frame-*.png'))
assert len(pngs) == len(frames)
lookup = dict(zip(frames, pngs))
old = {(x['width'], x['frame'], x['browserPNG']): x for x in original['checks']}
references = {x['frame']: x for x in final['samples']}
corners = [(50, 400), (1870, 400), (50, 900), (1870, 900)]
rows = []
for observation in native['exactFrames']:
    n = observation['frame']
    canvas = S / observation['file']
    fast = D / references[n]['retainedFile']
    accurate = lookup[n]
    assert sha(canvas) == observation['sha256'] and sha(fast) == references[n]['sha256']
    x, y, z = [np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) for p in (fast, canvas, accurate)]
    delta = np.abs(z - y)
    mean, p95 = float(delta.mean()), float(np.percentile(delta, 95))
    bg = max(int(delta[yy, xx].max()) for xx, yy in corners)
    baseline = old[(observation['width'], n, canvas.relative_to(ROOT).as_posix())]
    rows.append({'width': observation['width'], 'frame': n, 'pts': observation['pts'],
        'browserPNG': canvas.relative_to(ROOT).as_posix(), 'browserSHA256': sha(canvas),
        'defaultFinalPNG': fast.relative_to(ROOT).as_posix(), 'defaultFinalSHA256': sha(fast),
        'accuratePNG': accurate.relative_to(ROOT).as_posix(), 'accurateSHA256': sha(accurate),
        'originalMean': baseline['meanAbsoluteChannelError'],
        'meanAbsoluteChannelError': mean, 'p95AbsoluteChannelError': p95,
        'maxBackgroundPointChannelError': bg,
        'backgroundPoints': [{'xy': [xx, yy], 'defaultRGB': x[yy, xx].tolist(),
            'canvasRGB': y[yy, xx].tolist(), 'accurateRGB': z[yy, xx].tolist()} for xx, yy in corners],
        'passWithOriginalThresholds': mean <= 1.5 and p95 <= 3 and bg <= 3})

# Native YUV planes, no RGB conversion: an independent matrix check in uniform BG patches.
n = frames[0]
raw_path = Q / f'native-yuv420p-n{n}.yuv'
raw_command = ['ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-i', str(VIDEO),
               '-map', '0:v:0', '-vf', f'select=eq(n\\,{n})', '-frames:v', '1',
               '-pix_fmt', 'yuv420p', '-f', 'rawvideo', str(raw_path)]
raw_run = subprocess.run(raw_command, capture_output=True, text=True)
(Q / 'native-yuv.stderr.txt').write_text(raw_run.stderr)
assert raw_run.returncode == 0 and not raw_run.stderr
data = np.frombuffer(raw_path.read_bytes(), dtype=np.uint8)
w, height = 1920, 1080
assert data.size == w * height * 3 // 2
y_plane = data[:w * height].reshape(height, w)
u_plane = data[w * height:w * height + w * height // 4].reshape(height // 2, w // 2)
v_plane = data[w * height + w * height // 4:].reshape(height // 2, w // 2)
kr, kb = .2126, .0722
kg = 1 - kr - kb
ys, cs = 255 / 219, 255 / 112
coefficients = {'Yscale': ys, 'R_Cr': cs * (1 - kr), 'G_Cb': -cs * kb * (1 - kb) / kg,
                'G_Cr': -cs * kr * (1 - kr) / kg, 'B_Cb': cs * (1 - kb)}
canvas0 = np.asarray(Image.open(S / next(x['file'] for x in native['exactFrames'] if x['frame'] == n)).convert('RGB'))
fast0 = np.asarray(Image.open(D / references[n]['retainedFile']).convert('RGB'))
accurate0 = np.asarray(Image.open(lookup[n]).convert('RGB'))
math_points = []
for xx, yy in corners:
    y, u, v = int(y_plane[yy, xx]), int(u_plane[yy // 2, xx // 2]), int(v_plane[yy // 2, xx // 2])
    yf, uf, vf = y - 16, u - 128, v - 128
    rgb = [ys * yf + coefficients['R_Cr'] * vf,
           ys * yf + coefficients['G_Cb'] * uf + coefficients['G_Cr'] * vf,
           ys * yf + coefficients['B_Cb'] * uf]
    rounded = np.floor(np.clip(rgb, 0, 255) + .5).astype(np.uint8).tolist()
    math_points.append({'xy': [xx, yy], 'nativeY_Cb_Cr': [y, u, v], 'calculatedRGBFloat': rgb,
        'calculatedNearestRGB': rounded, 'canvasRGB': canvas0[yy, xx].tolist(),
        'accurateRGB': accurate0[yy, xx].tolist(), 'defaultRGB': fast0[yy, xx].tolist(),
        'lumaPatchUniform': bool(np.ptp(y_plane[yy - 2:yy + 3, xx - 2:xx + 3]) == 0),
        'chromaPatchUniform': bool(np.ptp(u_plane[yy // 2 - 1:yy // 2 + 2, xx // 2 - 1:xx // 2 + 2]) == 0
                                  and np.ptp(v_plane[yy // 2 - 1:yy // 2 + 2, xx // 2 - 1:xx // 2 + 2]) == 0)})
assert all(sha(ROOT / rel) == digest for rel, digest in before.items())
report = {'kind': 'same-integer-native-color-accurate-reference-crosscheck',
    'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'executor': '/root/mq_publication',
    'passWithOriginalThresholds': all(x['passWithOriginalThresholds'] for x in rows),
    'videoSHA256': sha(VIDEO), 'originalFailSHA256': before[str((A / 'qa/local-native-color.json').relative_to(ROOT))],
    'originalThresholdsUnchanged': thresholds, 'readOnlyInputSHA256': before,
    'accurateRGBDecode': {'command': command, 'exit': run.returncode, 'uniqueIntegerFrames': len(frames)},
    'observations': rows, 'comparisons': len(rows),
    'worstMean': max(x['meanAbsoluteChannelError'] for x in rows),
    'worstP95': max(x['p95AbsoluteChannelError'] for x in rows),
    'worstBackground': max(x['maxBackgroundPointChannelError'] for x in rows),
    'nativeYUVIndependentMath': {'frame': n, 'command': raw_command, 'rawSHA256': sha(raw_path),
        'formula': "BT.709 nonlinear RGB from limited8-bit YCbCr: Yscale=255/219, chromascale=255/112, Kr=.2126, Kb=.0722, nearest integer; uniform BG avoids interpolation assumptions.",
        'coefficients': coefficients, 'points': math_points},
    'inputsUnchanged': True,
    'limits': ['New QA reference PNGs only; original FAIL, original decoded PNGs, frozen script and final video are untouched.',
        'All22 current ChromeCanvas observations use the same video and actual integer n; only FFmpeg RGB reference conversion is changed here.',
        'The analytic check is limited to native uniform-background YCbCr samples; it does not claim a formula for text-edge chroma interpolation.',
        'Independent interpretation is required before concluding QA reference mismatch versus production colorspace error; no threshold increase or media re-render was performed.']}
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passWithOriginalThresholds': report['passWithOriginalThresholds'], 'comparisons': len(rows),
    'uniqueFrames': len(frames), 'worstMean': report['worstMean'], 'worstP95': report['worstP95'],
    'worstBackground': report['worstBackground'], 'nativeMathPoints': math_points, 'report': str(target)}))
