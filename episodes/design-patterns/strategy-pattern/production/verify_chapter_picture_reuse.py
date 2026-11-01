"""Read-only frame correspondence check after local-shot replacement.

H264 is decoded and reencoded during concatenation, so compare representative
decoded pictures instead of claiming packet byte identity for the final file.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np

D = Path(__file__).resolve().parent
BASE = D / 'remotion/out/chapter-bridges/base'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame(path, n):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{n / 30:.12f}',
        '-i', str(path), '-map', '0:v:0', '-frames:v', '1', '-vf', 'scale=960:540',
        '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    assert len(data) == 960 * 540 * 3, (path, n, len(data))
    return np.frombuffer(data, dtype=np.uint8).astype(np.float32)


mapping = json.loads((D / 'chapter-bridge-assembly.json').read_text())
rows = []
for m in mapping['mappings']:
    if m['changed']:
        continue
    local = m['oldFrames'] // 2
    old = frame(BASE / 'video.mp4', m['oldFrom'] + local)
    new = frame(D / 'video.mp4', m['newFrom'] + local)
    error = float(np.abs(old - new).mean())
    assert error < 3, (m['shot'], error)
    rows.append({'shot': m['shot'], 'localFrame': local,
        'oldFrame': m['oldFrom'] + local, 'newFrame': m['newFrom'] + local,
        'meanAbsoluteRGBDifference': error})
report = {'status': 'passed', 'baseVideoSHA256': sha(BASE / 'video.mp4'),
    'finalVideoSHA256': sha(D / 'video.mp4'), 'representativeCorrespondences': rows,
    'maxMeanAbsoluteRGBDifference': max(r['meanAbsoluteRGBDifference'] for r in rows),
    'scope': '13 representative decoded-frame comparisons only; not a pixel identity assertion, a full-frame scan, or a teaching/listening verdict.'}
(D / 'chapter-bridge-picture-reuse.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['status', 'maxMeanAbsoluteRGBDifference']}, indent=2))
