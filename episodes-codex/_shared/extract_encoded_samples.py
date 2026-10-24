from pathlib import Path
import json, subprocess, sys
import numpy as np
from PIL import Image

assert len(sys.argv) == 2, 'Usage: extract_encoded_samples.py EPDIR'
D = Path(sys.argv[1]).resolve()
out = D / 'remotion/out/qa-encoded'
out.mkdir(exist_ok=True)
source = json.loads((D / 'qa-motion-samples.json').read_text())
samples = source.get('records', source.get('samples'))
assert samples and not source.get('hideSubtitles', False), 'Use final captioned previews'
for sample in samples:
    assert Path(sample['file']).is_file(), sample['file']
total = json.loads((D / 'storyboard.json').read_text())['meta']['durationInFrames']
frames = sorted({q['frame'] for q in samples} | {0, total - 1})
encoded = {}
for batch in range(0, len(frames), 40):
    group = frames[batch:batch + 40]
    expression = '+'.join(f'eq(n\\,{n})' for n in group)
    pattern = str(out / f'b{batch:03}-%04d.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(D / 'video.mp4'),
                    '-vf', f'select={expression},scale=960:540', '-vsync', '0', pattern], check=True)
    for i, frame in enumerate(group, 1):
        encoded[frame] = str(out / f'b{batch:03}-{i:04}.png')
comparisons = []
for sample in samples:
    expected = np.array(Image.open(sample['file']).convert('RGB'), dtype=float)
    actual = np.array(Image.open(encoded[sample['frame']]).convert('RGB'), dtype=float)
    assert actual.shape == expected.shape
    error = float(np.abs(actual - expected).mean())
    assert error < 8, (sample['frame'], error)
    comparisons.append(dict(shot=sample['shot'], frame=sample['frame'],
                            meanAbsoluteRGBDifference=error, file=encoded[sample['frame']]))
report = dict(coverage='Actual encoded MP4 samples; image fidelity only, not animation pedagogy scoring.',
              uniqueFrames=len(frames), previewComparisons=len(comparisons),
              maxMeanAbsoluteRGBDifference=max(q['meanAbsoluteRGBDifference'] for q in comparisons),
              encodedFrames=encoded, comparisons=comparisons)
(D / 'qa-media-samples.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['uniqueFrames','previewComparisons','maxMeanAbsoluteRGBDifference']}, indent=2))
