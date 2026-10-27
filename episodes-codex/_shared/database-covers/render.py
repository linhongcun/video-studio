#!/usr/bin/env python3
"""Render and check the series SVG template with system Chromium, then optionally install."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SIZES = {'16x9': (1920, 1080), '3x4': (1080, 1440), '4x3': (1440, 1080)}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--install', action='store_true', help='Copy a previously checked render into production and publishing directories.')
    parser.add_argument('--repo', type=Path, default=REPO)
    args = parser.parse_args()
    out, repo = args.out_dir.resolve(), args.repo.resolve()
    catalog = json.loads((HERE/'catalog.json').read_text())
    episodes = catalog['episodes']
    actual = {}
    for p in (repo/'episodes').glob('*/meta.json'):
        meta = json.loads(p.read_text())
        if meta.get('series') == catalog['series'] and not meta.get('draft'):
            actual[meta['slug']] = meta
    if set(actual) != {e['slug'] for e in episodes}:
        raise ValueError('Catalog must cover every published database episode; update it before rendering.')
    for ep in episodes:
        m = actual[ep['slug']]
        if m.get('ep') != ep['ep'] or m['title'] != ep['sourceTitle']:
            raise ValueError('Catalog identity/title/method mismatch: '+ep['slug'])
    inputs = {name:sha(HERE/name) for name in ['template.mjs','diagrams.mjs','catalog.json','background.png','render.py','README.md']}
    report = {'schemaVersion': 1, 'style': catalog['version'], 'checkedAt': datetime.now(timezone.utc).isoformat(), 'episodeCount': len(episodes), 'inputs':inputs, 'images': [], 'installed': False}
    if args.install:
        prior = json.loads((out/'render-report.json').read_text())
        if prior.get('passed') is not True:
            raise ValueError('No successful checked render found.')
        if prior.get('inputs') != inputs or {(i['slug'],i['size']) for i in prior['images']} != {(e['slug'],s) for e in episodes for s in SIZES}:
            raise ValueError('Render inputs or episode/size set changed; render again before installing.')
        for image in prior['images']:
            for ext in ['png','jpg']:
                p = out/image['slug']/f"cover-{image['size']}.{ext}"
                if sha(p) != image[ext+'Sha256']:
                    raise ValueError('Checked artifact changed: '+str(p))
        for ep in episodes:
            src = out/ep['slug']
            for root in ['episodes-codex', 'episodes']:
                dst = repo/root/ep['slug']
                for size in SIZES:
                    for ext in (['png','jpg'] if root == 'episodes-codex' else ['jpg']):
                        shutil.copyfile(src/f'cover-{size}.{ext}', dst/f'cover-{size}.{ext}')
                shutil.copyfile(src/'cover-3x4.jpg',dst/'poster.jpg')
                manifest = {'style':catalog['version'],'ep':ep['ep'],'seriesSource':'episodes-codex/_shared/database-covers','sourceSha256':inputs,'sitePoster':'cover-16x9.jpg','portraitPoster':'poster.jpg','covers':{i['size']:{'dimensions':i['dimensions'],'jpgSha256':i['jpgSha256'],'pngSha256':i['pngSha256']} for i in prior['images'] if i['slug']==ep['slug']}}
                (dst/'cover-style.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        prior['installed'] = True
        prior['installedAt'] = datetime.now(timezone.utc).isoformat()
        (out/'render-report.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n')
        print(f'Installed {len(episodes)} checked cover sets; publishing poster remains cover-16x9.jpg.')
        return
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(['node',str(HERE/'template.mjs'),'--out-dir',str(out)],check=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        report['runtime'] = {'chromium':browser.version,'playwright':importlib.metadata.version('playwright')}
        page = browser.new_page(device_scale_factor=1)
        for ep in episodes:
            for size, (w,h) in SIZES.items():
                p = out/ep['slug']/f'cover-{size}'
                svg = p.with_suffix('.svg').read_text()
                page.set_viewport_size({'width':w,'height':h})
                page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#10211F}svg{display:block}</style>'+svg)
                page.evaluate('document.fonts.ready')
                bounds = page.evaluate('''() => Array.from(document.querySelectorAll('text')).map(e=>{
                  const r=e.getBoundingClientRect();return {id:e.dataset.element||'diagram-label',text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height};
                })''')
                for b in bounds:
                    if b['width'] <= 0 or b['height'] <= 0:
                        raise ValueError(f'Empty text: {ep["slug"]}/{size}/{b}')
                    if b['x'] < 0 or b['y'] < 0 or b['x']+b['width'] > w+0.1 or b['y']+b['height'] > h+0.1:
                        raise ValueError(f'COPYFIT: {ep["slug"]}/{size}/{b}')
                    if size == '4x3' and (b['x']<315 or b['x']+b['width']>1125 or b['y']+b['height']>=918):
                        raise ValueError(f'4:3 safe area: {ep["slug"]}/{b}')
                    if size == '16x9' and b['y']+b['height']>=918:
                        raise ValueError(f'16:9 player-control text safety: {ep["slug"]}/{b}')
                groups = page.evaluate('''() => Array.from(document.querySelectorAll('[data-group]')).map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height}})''')
                title = next(b for b in groups if b['id']=='title')
                identity = next(b for b in groups if b['id']=='identity')
                question = next(b for b in bounds if b['id']=='question')
                min_gap = 9 if size=='4x3' else 12
                if identity['y']+identity['height']+min_gap > title['y'] or title['y']+title['height']+min_gap > question['y']:
                    raise ValueError(f'Title/identity/question spacing: {ep["slug"]}/{size}')
                if size=='4x3' and any(b['x']<315 or b['x']+b['width']>1125 or b['y']+b['height']>=918 for b in groups):
                    raise ValueError(f'4:3 group out of safe area: {ep["slug"]}/{groups}')
                page.screenshot(path=str(p.with_suffix('.png')),type='png')
                page.screenshot(path=str(p.with_suffix('.jpg')),type='jpeg',quality=94)
                for ext in ['png','jpg']:
                    with Image.open(p.with_suffix('.'+ext)) as im:
                        if im.size != (w,h): raise ValueError('Wrong output size')
                report['images'].append({'slug':ep['slug'],'number':ep['number'],'size':size,'dimensions':[w,h],'svgSha256':sha(p.with_suffix('.svg')),'pngSha256':sha(p.with_suffix('.png')),'jpgSha256':sha(p.with_suffix('.jpg')),'textBounds':bounds,'groupBounds':groups})
        browser.close()
    sheet = Image.new('RGB',(1504,((len(episodes)+2)//3)*322+112),'#10211F')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',30)
    small = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19)
    draw.text((32,24),f'数据库  /  {len(episodes)} 期统一封面',font=font,fill='#E5E7EB')
    for i,ep in enumerate(episodes):
        x,y = 32+(i%3)*496,98+(i//3)*322
        with Image.open(out/ep['slug']/'cover-16x9.jpg') as im:
            sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+4,y+279),ep['number']+'  '+ep['title'],font=small,fill='#9CB7AE')
    sheet.save(out/'contact-sheet.jpg',quality=95)
    sheet.save(out/'contact-sheet.png')
    report['passed'] = True
    (out/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Rendered and checked {len(report["images"])} SVG / PNG / JPG sets, including 4:3 center and bottom safety.')

if __name__ == '__main__': main()
