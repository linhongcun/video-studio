#!/usr/bin/env python3
"""Measure P10 cover candidates in private copies; never edit shared or final assets."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import subprocess

from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
SHARED = ROOT / 'episodes/_shared/puzzles-covers'
SIZES = {'16x9': (1920, 1080), '3x4': (1080, 1440), '4x3': (1440, 1080)}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='cover-development-v1')
    args = parser.parse_args()
    assert args.name.replace('-', '').isalnum()
    out = D / 'qa/out' / args.name
    report_path = D / 'qa' / f'{args.name}.json'
    assert not out.exists() and not report_path.exists(), 'Use a new development-run name'
    out.mkdir(parents=True)
    originals = [SHARED / n for n in ['template.mjs', 'diagrams.mjs', 'catalog.json', 'background.png', 'README.md']]
    before = {str(p.relative_to(ROOT)): sha(p) for p in originals}
    spec = json.loads((D / 'covers.json').read_text())
    catalog = json.loads((SHARED / 'catalog.json').read_text())
    assert not any(e['slug'] == 'prisoners-light' for e in catalog['episodes']), 'Final shared entry already exists; no private development needed'
    candidate = (D / 'qa/cover-diagram-candidate.mjs.txt').read_text()
    source = (SHARED / 'diagrams.mjs').read_text()
    assert source.count('const DRAW = new Map([') == 1
    source = source.replace('const DRAW = new Map([', candidate + '\nconst DRAW = new Map([', 1)
    source = source.replace("  ['pirate-gold', pirateGold],", "  ['pirate-gold', pirateGold],\n  ['prisoners-light', prisonersLight],", 1)
    (out / 'diagrams.mjs').write_text(source)
    catalog['episodes'].append({'slug': 'prisoners-light', 'number': spec['number'], 'title': spec['title'],
        'question': spec['question'], 'sourceTitle': spec['sourceTitle'], 'episodePart': '趣味推理 P10'})
    (out / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    for name in ['template.mjs', 'background.png']:
        shutil.copyfile(SHARED / name, out / name)
    (out / 'render.mjs').write_text("import fs from 'node:fs';\nimport {catalog,cover,sizes} from './template.mjs';\nconst ep=catalog.episodes.find(e=>e.slug==='prisoners-light');\nfor(const size of Object.keys(sizes))fs.writeFileSync(`draft-${size}.svg`,cover(ep,size)+'\\n');\n")
    subprocess.run(['node', 'render.mjs'], cwd=out, check=True)
    report = {'status': 'DEVELOPMENT_ONLY_NOT_FINAL_ACCEPTANCE', 'checkedAt': datetime.now(timezone.utc).isoformat(),
        'scope': 'Private copies of current shared template/catalog/diagrams with P10 candidate. No final cover, shared file, old asset or frozen manifest is modified.',
        'sharedBeforeSHA256': before, 'images': [], 'violations': [], 'actualVisualReview': False}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        report['chromium'] = browser.version
        page = browser.new_page(device_scale_factor=1)
        for size, (w, h) in SIZES.items():
            page.set_viewport_size({'width': w, 'height': h})
            page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#171326}svg{display:block}</style>' + (out / f'draft-{size}.svg').read_text())
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.fonts.check(\'24px "Noto Sans CJK SC"\')')
            bounds = page.evaluate("""() => [...document.querySelectorAll('text')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.element||'diagram-label',text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height}})""")
            groups = page.evaluate("""() => [...document.querySelectorAll('[data-group]')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height}})""")
            violations = []
            for b in bounds:
                if b['width'] <= 0 or b['height'] <= 0 or b['x'] < 0 or b['y'] < 0 or b['x'] + b['width'] > w + .1 or b['y'] + b['height'] > h + .1:
                    violations.append({'kind': 'COPYFIT', 'text': b})
                if size == '4x3' and not(b['x'] >= 315 and b['x'] + b['width'] <= 1125 and b['y'] + b['height'] < 918):
                    violations.append({'kind': '4x3 text safety', 'text': b})
                if size == '16x9' and not(b['y'] + b['height'] < 918):
                    violations.append({'kind': '16x9 control safety', 'text': b})
            for i, a in enumerate(bounds):
                for b in bounds[i + 1:]:
                    ox = min(a['x'] + a['width'], b['x'] + b['width']) - max(a['x'], b['x'])
                    oy = min(a['y'] + a['height'], b['y'] + b['height']) - max(a['y'], b['y'])
                    if ox > .5 and oy > .5:
                        violations.append({'kind': 'text overlap', 'a': a, 'b': b})
            if size == '4x3':
                for b in groups:
                    if not(b['x'] >= 315 and b['x'] + b['width'] <= 1125 and b['y'] + b['height'] < 918):
                        violations.append({'kind': '4x3 group safety', 'group': b})
            png = out / f'draft-{size}.png'
            page.screenshot(path=str(png))
            report['images'].append({'size': size, 'dimensions': [w, h], 'file': str(png.relative_to(D)),
                'sha256': sha(png), 'textBounds': bounds, 'groupBounds': groups, 'violations': violations})
            report['violations'].extend({'size': size, **v} for v in violations)
        browser.close()
    after = {str(p.relative_to(ROOT)): sha(p) for p in originals}
    report['sharedAfterSHA256'] = after
    report['sharedFilesUnchanged'] = before == after
    report['geometryChecksPassed'] = not report['violations'] and before == after
    report['cannotServeAsFinalCoverAcceptance'] = True
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'geometryChecksPassed': report['geometryChecksPassed'],
        'violations': report['violations'], 'sharedFilesUnchanged': report['sharedFilesUnchanged']}))


if __name__ == '__main__':
    main()
