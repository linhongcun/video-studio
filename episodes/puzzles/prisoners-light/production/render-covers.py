#!/usr/bin/env python3
"""Render and audit P10 only, preserving the current shared puzzle template."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.metadata
import json
import shutil
import subprocess

from PIL import Image
from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
SHARED = ROOT / 'episodes/_shared/puzzles-covers'
SIZES = {'16x9': (1920, 1080), '3x4': (1080, 1440), '4x3': (1440, 1080)}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Copy only P10 JPG/manifests to publication.')
    args = parser.parse_args()
    inputs = [D / n for n in ['render-covers.py', 'render-covers.mjs', 'covers.json']]
    inputs += [SHARED / n for n in ['template.mjs', 'diagrams.mjs', 'catalog.json', 'background.png', 'README.md']]
    binding = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    catalog = json.loads((SHARED / 'catalog.json').read_text())
    ep = next(e for e in catalog['episodes'] if e['slug'] == 'prisoners-light')
    config = json.loads((D / 'covers.json').read_text())
    metadata = json.loads((D.parent / 'publication/meta.json').read_text())
    assert metadata['slug'] == ep['slug'] and metadata['episodePart'] == ep['episodePart']
    assert metadata['ep'] == config['ep'] == 57 and metadata['title'] == ep['sourceTitle'] == config['sourceTitle']
    assert config['title'] == ep['title'] and config['question'] == ep['question']
    assert config['problem'] == {'people': 100, 'initialLight': 'known-off',
        'oneVisitorAtATime': True, 'privateMemoryAllowed': True,
        'noExtraMarksOrCommunication': True,
        'fairness': 'each person chosen infinitely often; no fixed visit bound'}
    assert config['diagram'] == {'peopleLabel': '100人', 'lightState': 'off',
        'showsProtocol': False, 'revealsAnswer': False, 'extraCommunication': False}
    subprocess.run(['node', str(D / 'render-covers.mjs')], check=True)
    report = {'schemaVersion': 1, 'scope': 'P10 only; no prior covers, media, QA or freezes rendered or installed.',
        'style': catalog['version'], 'episode': 'prisoners-light', 'checkedAt': datetime.now(timezone.utc).isoformat(),
        'sourceIdentity': {'ep': metadata['ep'], 'episodePart': ep['episodePart'], 'title': metadata['title']},
        'inputs': binding, 'images': [], 'visualReview': 'Separate actual-image review in qa/covers-review.md.'}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        report['runtime'] = {'chromium': browser.version, 'playwright': importlib.metadata.version('playwright')}
        page = browser.new_page(device_scale_factor=1)
        for size, (w, h) in SIZES.items():
            stem = D / f'cover-{size}'
            page.set_viewport_size({'width': w, 'height': h})
            page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#171326}svg{display:block}</style>' + stem.with_suffix('.svg').read_text())
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.fonts.check(\'24px "Noto Sans CJK SC"\')'), 'CJK font unavailable'
            bounds = page.evaluate('''() => [...document.querySelectorAll('text')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.element||'diagram-label',text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height}})''')
            groups = page.evaluate('''() => [...document.querySelectorAll('[data-group]')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height}})''')
            people = page.evaluate("""() => [...document.querySelectorAll('[data-person-number]')].map(e=>({number:Number(e.dataset.personNumber),representative:e.dataset.representative,text:e.textContent}))""")
            light = page.evaluate("""() => [...document.querySelectorAll('[data-light-state]')].map(e=>({state:e.dataset.lightState,text:e.textContent}))""")
            assert [p['number'] for p in people] == [1, 2, 100], ('representative identities', size, people)
            assert all(p['representative'] == 'true' for p in people)
            assert len(light) == 1 and light[0]['state'] == 'off' and '0 · 灭' in light[0]['text']
            assert page.locator('[data-people-ellipsis]').count() == 1
            all_text = ' '.join(b['text'] for b in bounds)
            assert '99' not in all_text and '计数员' not in all_text and '已发' not in all_text, 'Protocol revealed on cover'
            for b in bounds:
                assert b['width'] > 0 and b['height'] > 0, ('empty', size, b)
                assert b['x'] >= 0 and b['y'] >= 0 and b['x'] + b['width'] <= w + .1 and b['y'] + b['height'] <= h + .1, ('COPYFIT', size, b)
                if size == '4x3':
                    assert b['x'] >= 315 and b['x'] + b['width'] <= 1125 and b['y'] + b['height'] < 918, ('4x3 safety', b)
                if size == '16x9':
                    assert b['y'] + b['height'] < 918, ('16x9 control safety', b)
            for i, a in enumerate(bounds):
                for b in bounds[i + 1:]:
                    overlap_x = min(a['x'] + a['width'], b['x'] + b['width']) - max(a['x'], b['x'])
                    overlap_y = min(a['y'] + a['height'], b['y'] + b['height']) - max(a['y'], b['y'])
                    assert overlap_x <= .5 or overlap_y <= .5, ('Text overlap', size, a, b)
            identity = next(b for b in groups if b['id'] == 'identity')
            title = next(b for b in groups if b['id'] == 'title')
            question = next(b for b in bounds if b['id'] == 'question')
            gap = 9 if size == '4x3' else 12
            assert identity['y'] + identity['height'] + gap <= title['y'] and title['y'] + title['height'] + gap <= question['y'], ('title separation', size)
            if size == '4x3':
                for b in groups:
                    assert b['x'] >= 315 and b['x'] + b['width'] <= 1125 and b['y'] + b['height'] < 918, ('4x3 group safety', b)
            page.screenshot(path=str(stem.with_suffix('.png')), type='png')
            page.screenshot(path=str(stem.with_suffix('.jpg')), type='jpeg', quality=94)
            for ext in ['png', 'jpg']:
                with Image.open(stem.with_suffix('.' + ext)) as im:
                    assert im.size == (w, h)
            report['images'].append({'size': size, 'dimensions': [w, h],
                'svgSha256': sha(stem.with_suffix('.svg')), 'pngSha256': sha(stem.with_suffix('.png')),
                'jpgSha256': sha(stem.with_suffix('.jpg')), 'textBounds': bounds, 'groupBounds': groups,
                'personRepresentationAudit': people, 'initialLightAudit': light, 'textOverlaps': 0})
        browser.close()
    assert binding == {str(p.relative_to(ROOT)): sha(p) for p in inputs}, 'Inputs changed during cover render'
    (D / 'poster.jpg').write_bytes((D / 'cover-3x4.jpg').read_bytes())
    report['posterSha256'] = sha(D / 'poster.jpg')
    report['passed'] = True
    write_json(D / 'cover-render-report.json', report)
    manifest = {'style': catalog['version'], 'episodePart': ep['episodePart'], 'seriesSource': 'episodes/_shared/puzzles-covers',
        'generator': 'episodes/puzzles/prisoners-light/production/render-covers.py', 'sourceSha256': binding,
        'sitePoster': 'cover-16x9.jpg', 'portraitPoster': 'poster.jpg', 'posterSha256': report['posterSha256'],
        'covers': {i['size']: {k: i[k] for k in ['dimensions', 'svgSha256', 'jpgSha256', 'pngSha256']} for i in report['images']}}
    write_json(D / 'cover-style.json', manifest)
    if args.install:
        for name in ['cover-16x9.jpg', 'cover-3x4.jpg', 'cover-4x3.jpg', 'poster.jpg', 'cover-style.json', 'covers.json']:
            shutil.copyfile(D / name, D.parent / 'publication' / name)
    print('P10 three-ratio SVG/PNG/JPG audited; actual-image review is recorded separately.')


if __name__ == '__main__':
    main()
