#!/usr/bin/env python3
"""Render Redis covers, check geometry and real fonts, then install checked outputs."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SIZES = {'16x9': (1920, 1080), '3x4': (1080, 1440), '4x3': (1440, 1080)}
INPUTS = ['template.mjs', 'diagrams.mjs', 'catalog.json', 'style-v1.json',
          'plan-layout.json', 'background.png', 'render.py', 'README.md',
          '../middleware-identity/redis-original.svg', '../middleware-identity/LICENSE.txt',
          '../middleware-identity/source.json', '../middleware-identity/NOTICE.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_inputs():
    bindings = []
    for family in ('Noto Sans CJK SC', 'DejaVu Sans'):
        for weight in ('regular', 'bold'):
            actual = subprocess.check_output(['fc-match', '-f', '%{family}\n%{style}\n%{file}\n', f'{family}:weight={weight}'], text=True).splitlines()
            assert len(actual) == 3 and family.casefold() in [part.strip().casefold() for part in actual[0].split(',')], ('Required font unavailable', family, actual)
            bindings.append({'family': family, 'weight': weight, 'actualFamily': actual[0], 'actualStyle': actual[1], 'file': actual[2], 'sha256': sha(Path(actual[2]))})
    return bindings


def inspect(page, path, size):
    w, h = SIZES[size]
    page.set_viewport_size({'width': w, 'height': h})
    page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#EEF1F5}svg{display:block}</style>' + path.read_text())
    page.evaluate('document.fonts.ready')
    assert page.evaluate('document.fonts.check(\'600 36px "Noto Sans CJK SC"\')'), 'Noto font unavailable'
    bounds = page.evaluate('''() => Array.from(document.querySelectorAll('text')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.element,text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    groups = page.evaluate('''() => Array.from(document.querySelectorAll('[data-group]')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    ink = page.evaluate('''() => Array.from(document.querySelectorAll('[data-ink]')).map(e=>{
      const r=e.getBoundingClientRect();const s=parseFloat(getComputedStyle(e).strokeWidth)||0;
      const m=e.getScreenCTM();const p=s/2*Math.max(Math.hypot(m.a,m.b),Math.hypot(m.c,m.d));
      return {id:e.dataset.ink,x:r.x-p,y:r.y-p,width:r.width+2*p,height:r.height+2*p};
    })''')
    for b in bounds:
        assert b['width'] > 0 and b['height'] > 0, ('empty text', path, b)
    for b in bounds + ink + groups:
        assert b['x'] >= 0 and b['y'] >= 0 and b['x']+b['width'] <= w+.1 and b['y']+b['height'] <= h+.1, ('COPYFIT', path, b)
        if size == '16x9':
            assert b['y']+b['height'] < 918, ('horizontal bottom safety', path, b)
        if size == '4x3':
            assert b['x'] >= 315 and b['x']+b['width'] <= 1125 and b['y']+b['height'] < 918, ('4:3 content safety', path, b)
    by_id = {b['id']: b for b in groups}
    gap = 9 if size == '4x3' else 12
    for first, second in [('header', 'identity'), ('identity', 'title'), ('title', 'question')]:
        a, b = by_id[first], by_id[second]
        assert a['y']+a['height']+gap <= b['y'], ('group vertical spacing', path, first, second, a, b)
    if size != '16x9':
        a, b = by_id['question'], by_id['diagram']
        assert a['y']+a['height']+gap <= b['y'], ('question/diagram spacing', path)
    else:
        right = max(by_id[k]['x']+by_id[k]['width'] for k in ['identity', 'title', 'question'])
        assert right+24 <= by_id['diagram']['x'], ('text/diagram spacing', path)
    return bounds, groups, ink


def frozen_paths(repo):
    """Protect flat and nested tracked manifests, including modern repo-root inputs."""
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z', '**/source-sha256.json']).decode().split('\0')
    result = set()
    def resolve(manifest, name):
        path = Path(name)
        if path.is_absolute(): return path.resolve()
        if name.startswith(('episodes/', 'episodes-codex/', 'docs/', 'site/', 'design/')): return (repo/path).resolve()
        return (manifest.parent/path).resolve()
    def visit(manifest, value):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, str) and len(child) == 64 and all(c in '0123456789abcdefABCDEF' for c in child):
                    result.add(resolve(manifest, key))
                if key == 'path' and isinstance(child, str) and any(isinstance(value.get(k), str) and len(value[k]) == 64 for k in ('sha256','SHA256')):
                    result.add(resolve(manifest, child))
                if isinstance(child, (dict,list)): visit(manifest, child)
        elif isinstance(value, list):
            for child in value: visit(manifest, child)
    for name in filter(None, names):
        manifest = repo/name
        visit(manifest, json.loads(manifest.read_text()))
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--repo', type=Path, default=REPO)
    args = parser.parse_args()
    out, repo = args.out_dir.resolve(), args.repo.resolve()
    catalog = json.loads((HERE/'catalog.json').read_text())
    catalog_episodes = catalog['episodes']
    preserved = set(catalog.get('preservedEpisodes', []))
    episodes = [ep for ep in catalog_episodes if ep['slug'] not in preserved]
    actual = {}
    for p in (repo/'episodes').glob('*/meta.json'):
        m = json.loads(p.read_text())
        if m.get('series') == catalog['series'] and not m.get('draft'):
            actual[m['slug']] = m
    assert set(actual) == {e['slug'] for e in catalog_episodes}, 'Catalog must cover every published Redis episode'
    for ep in catalog_episodes:
        m = actual[ep['slug']]
        assert m['ep'] == ep['ep'] and m['title'] == ep['sourceTitle'] and ep['number'] == f"EP.{m['ep']:02d}", 'EP/title mismatch'
        production = (repo/ep['productionRoot']).resolve()
        assert production.is_relative_to(repo/'episodes-codex') and production.is_dir(), 'Invalid production root'
        assert m['sourcePath'] == ep['productionRoot']+'/remotion', 'Catalog must bind exact current sourcePath'
        assert m['poster'] == 'cover-16x9.jpg', 'Review another site poster convention before installing'
    inputs = {name: sha(HERE/name) for name in INPUTS}
    fonts = font_inputs()
    if args.install:
        prior = json.loads((out/'render-report.json').read_text())
        assert prior['passed'] and prior['inputs'] == inputs, 'Checked render inputs changed'
        assert prior['fontInputs'] == fonts, 'Checked actual fonts changed'
        assert {(i['slug'], i['size']) for i in prior['images']} == {(e['slug'], s) for e in episodes for s in SIZES}
        for i in prior['images']:
            for ext in ['svg', 'png', 'jpg']:
                assert sha(out/i['slug']/f"cover-{i['size']}.{ext}") == i[ext+'Sha256'], 'Checked artifact changed'
        operations = []
        for ep in episodes:
            source = out/ep['slug']
            for dest, exts in [(repo/ep['installationRoot'], ['png', 'jpg']), (repo/'episodes'/ep['slug'], ['jpg'])]:
                for size in SIZES:
                    for ext in exts:
                        operations.append((source/f'cover-{size}.{ext}', dest/f'cover-{size}.{ext}'))
                operations.append((source/'cover-3x4.jpg', dest/'poster.jpg'))
        protected = frozen_paths(repo)
        targets = {p.resolve() for _, p in operations}
        targets.update((repo/ep['installationRoot']/'cover-style.json').resolve() for ep in episodes)
        targets.update((repo/'episodes'/ep['slug']/'cover-style.json').resolve() for ep in episodes)
        assert not targets.intersection(protected), 'Install would overwrite a frozen input; use an independent cover-only destination'
        for source, dest in operations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        for ep in episodes:
            images = [i for i in prior['images'] if i['slug'] == ep['slug']]
            manifest = {'style': catalog['version'], 'ep': ep['ep'], 'number': ep['number'],
                        'productionRoot': ep['installationRoot'], 'currentRemotionRoot': ep['productionRoot'], 'seriesSource': 'episodes-codex/_shared/redis-covers-v2',
                        'sourceSha256': inputs, 'fontInputs': fonts, 'sitePoster': 'cover-16x9.jpg', 'portraitPoster': 'poster.jpg',
                        'covers': {i['size']: {'dimensions': i['dimensions'], 'jpgSha256': i['jpgSha256'], 'pngSha256': i['pngSha256']} for i in images}}
            for dest in [repo/ep['installationRoot'], repo/'episodes'/ep['slug']]:
                (dest/'cover-style.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
        prior.update(installed=True, installedAt=datetime.now(timezone.utc).isoformat(), installedImages=len(operations), frozenTargetIntersection=0)
        (out/'render-report.json').write_text(json.dumps(prior, ensure_ascii=False, indent=2)+'\n')
        print(f'Installed {len(operations)} checked cover images and {len(episodes)*2} manifests')
        return
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['node', str(HERE/'template.mjs'), '--out-dir', str(out)], check=True)
    report = {'schemaVersion': 1, 'style': catalog['version'], 'checkedAt': datetime.now(timezone.utc).isoformat(),
              'inputs': inputs, 'fontInputs': fonts, 'images': [], 'plannedTypography': [], 'preservedEpisodes': sorted(preserved), 'installed': False}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        report['runtime'] = {'chromium': browser.version, 'playwright': importlib.metadata.version('playwright')}
        page = browser.new_page(device_scale_factor=1)
        for ep in episodes:
            for size, dimensions in SIZES.items():
                p = out/ep['slug']/f'cover-{size}'
                bounds, groups, ink = inspect(page, p.with_suffix('.svg'), size)
                page.screenshot(path=str(p.with_suffix('.png')), type='png')
                page.screenshot(path=str(p.with_suffix('.jpg')), type='jpeg', quality=94)
                for ext in ['png', 'jpg']:
                    with Image.open(p.with_suffix('.'+ext)) as im:
                        assert im.size == dimensions, 'Unexpected image dimensions'
                report['images'].append({'slug': ep['slug'], 'number': ep['number'], 'size': size, 'dimensions': list(dimensions),
                                         **{ext+'Sha256': sha(p.with_suffix('.'+ext)) for ext in ['svg', 'png', 'jpg']},
                                         'textBounds': bounds, 'groupBounds': groups, 'inkBounds': ink})
                print(f'Candidate image ready: {p.with_suffix(".png")}', flush=True)
        for p in sorted((out/'typography-only').glob('*.svg')):
            size = p.stem.rsplit('-', 1)[1]
            bounds, groups, ink = inspect(page, p, size)
            report['plannedTypography'].append({'name': p.name, 'size': size, 'passed': True,
                                                 'textBounds': bounds, 'groupBounds': groups, 'inkBounds': ink,
                                                 'scope': 'Typography only, not a future episode or mechanism illustration'})
        browser.close()
    ep = episodes[0]
    with Image.open(out/ep['slug']/'cover-16x9.jpg') as im:
        preview = Image.new('RGB', (1024, 660), '#EEF1F5')
        preview.paste(im.resize((960, 540), Image.Resampling.LANCZOS), (32, 88))
        font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 30)
        ImageDraw.Draw(preview).text((32, 24), 'Redis · '+ep['number']+' / 系列统一封面', font=font, fill='#182737')
        preview.save(out/'preview.png')
        preview.save(out/'preview.jpg', quality=95)
    report['passed'] = True
    (out/'render-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"Checked {len(report['images'])} covers and {len(report['plannedTypography'])} typography-only layouts")


if __name__ == '__main__':
    main()
