#!/usr/bin/env python3
"""Build annotated contact sheets from retained actual review PNGs; no episode writes."""
from pathlib import Path
import argparse
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--report', type=Path, required=True)
ap.add_argument('--out-dir', type=Path, required=True)
a = ap.parse_args()
out = a.out_dir.resolve()
assert out.is_relative_to(HERE) and out != HERE and not out.exists(), 'Use a fresh QA child directory'
report = json.loads(a.report.read_text())
samples = report['samples']
out.mkdir(parents=True)
font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 19)
files = []
for start in range(0, len(samples), 8):
    group = samples[start:start + 8]
    image = Image.new('RGB', (1920, math.ceil(len(group) / 2) * 586), '#182737')
    draw = ImageDraw.Draw(image)
    for index, sample in enumerate(group):
        source = Path(sample.get('file') or sample['retainedFile'])
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == sample['sha256']
        x, y = index % 2 * 960, index // 2 * 586
        image.paste(Image.open(source).convert('RGB').resize((960, 540)), (x, y))
        label = sample.get('label') or ','.join(sample.get('reasons', []))
        draw.text((x + 8, y + 542), f"frame {sample['frame']} {label}"[:74], font=font, fill='white')
    file = out / f'contact-{start // 8 + 1:02d}.jpg'
    image.save(file, quality=95)
    files.append({'file': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
(out / 'contacts.json').write_text(json.dumps({'sourceReport': str(a.report.resolve()),
    'sourceReportSHA256': hashlib.sha256(a.report.read_bytes()).hexdigest(),
    'files': files, 'visualReviewed': False}, indent=2) + '\n')
print(json.dumps({'contacts': len(files), 'out': str(out)}))
