#!/usr/bin/env python3
"""Render Kafka series covers, validate real typography, then install checked artifacts."""
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
SIZES = {'16x9': (1920,1080), '3x4': (1080,1440), '4x3': (1440,1080)}
INPUTS = ['template.mjs','diagrams.mjs','catalog.json','style-v1.json','plan-layout.json',
          'background.png','render.py','README.md',
          '../middleware-identity/apachekafka-original.svg','../middleware-identity/LICENSE.txt',
          '../middleware-identity/source.json','../middleware-identity/NOTICE.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def inspect(page, path, size):
    w,h = SIZES[size]
    page.set_viewport_size({'width':w,'height':h})
    page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#211D1B}svg{display:block}</style>'+path.read_text())
    page.evaluate('document.fonts.ready')
    bounds = page.evaluate('''() => Array.from(document.querySelectorAll('text')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.element,text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    groups = page.evaluate('''() => Array.from(document.querySelectorAll('[data-group]')).map(e=>{
      const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height};
    })''')
    for b in bounds:
        assert b['width']>0 and b['height']>0, ('empty text',path,b)
        assert b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+.1 and b['y']+b['height']<=h+.1, ('COPYFIT',path,b)
        if size=='16x9': assert b['y']+b['height']<918, ('bottom margin',path,b)
    if size=='4x3':
        for b in bounds+groups:
            assert b['x']>=315 and b['x']+b['width']<=1125 and b['y']+b['height']<918, ('4:3 content safety',path,b)
    title = next(b for b in groups if b['id']=='title')
    identity = next(b for b in groups if b['id']=='identity')
    question = next(b for b in bounds if b['id']=='question')
    gap = 9 if size=='4x3' else 12
    assert identity['y']+identity['height']+gap<=title['y'], ('identity/title spacing',path)
    assert title['y']+title['height']+gap<=question['y'], ('title/question spacing',path)
    return bounds,groups

def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    parser.add_argument('--install',action='store_true')
    parser.add_argument('--slug',action='append',help='Render/install only these catalog slugs; omitted means all published episodes')
    parser.add_argument('--repo',type=Path,default=REPO)
    args=parser.parse_args()
    out,repo=args.out_dir.resolve(),args.repo.resolve()
    catalog=json.loads((HERE/'catalog.json').read_text())
    episodes=catalog['episodes']
    actual={}
    for p in (repo/'episodes').glob('*/meta.json'):
        m=json.loads(p.read_text())
        if m.get('series')==catalog['series'] and not m.get('draft'): actual[m['slug']]=m
    assert set(actual)=={e['slug'] for e in episodes}, 'Catalog must cover all published series episodes'
    if args.slug:
        assert set(args.slug).issubset({e['slug'] for e in episodes}), 'Unknown selected Kafka episode'
        episodes=[e for e in episodes if e['slug'] in args.slug]
    for ep in episodes:
        m=actual[ep['slug']]
        assert m['ep']==ep['ep'] and m['title']==ep['sourceTitle'], 'Published identity/title mismatch'
        production=(repo/ep['productionRoot']).resolve()
        assert production.is_relative_to(repo/'episodes-codex') and production.is_dir(), 'Invalid production root'
    inputs={name:sha(HERE/name) for name in INPUTS}
    if args.install:
        prior=json.loads((out/'render-report.json').read_text())
        assert prior['passed'] and prior['inputs']==inputs, 'Checked render inputs changed'
        assert {(i['slug'],i['size']) for i in prior['images']}=={(e['slug'],s) for e in episodes for s in SIZES}
        for ep in episodes:
            m=actual[ep['slug']]
            assert m['sourcePath']==ep['productionRoot']+'/remotion' and m['episodePart']==ep['episodePart'], 'Install only after matching Kafka media metadata is integrated'
        for i in prior['images']:
            for ext in ['svg','png','jpg']: assert sha(out/i['slug']/f"cover-{i['size']}.{ext}")==i[ext+'Sha256'], 'Checked artifact changed'
        for ep in episodes:
            images=[i for i in prior['images'] if i['slug']==ep['slug']]
            manifest={'style':catalog['version'],'ep':ep['ep'],'number':ep['number'],
                      'planningIssue':ep['planningIssue'],'productionRoot':ep['productionRoot'],
                      'seriesSource':'episodes-codex/_shared/kafka-covers','sourceSha256':inputs,
                      'sitePoster':'cover-16x9.jpg','portraitPoster':'poster.jpg',
                      'covers':{i['size']:{'dimensions':i['dimensions'],'jpgSha256':i['jpgSha256'],'pngSha256':i['pngSha256']} for i in images}}
            for dest,exts in [(repo/ep['productionRoot'],['png','jpg']),(repo/'episodes'/ep['slug'],['jpg'])]:
                for size in SIZES:
                    for ext in exts: shutil.copyfile(out/ep['slug']/f'cover-{size}.{ext}',dest/f'cover-{size}.{ext}')
                shutil.copyfile(out/ep['slug']/'cover-3x4.jpg',dest/'poster.jpg')
                (dest/'cover-style.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        prior.update(installed=True,installedAt=datetime.now(timezone.utc).isoformat())
        (out/'render-report.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n')
        print(f'Installed {len(episodes)} verified Kafka cover sets')
        return
    out.mkdir(parents=True,exist_ok=True)
    subprocess.run(['node',str(HERE/'template.mjs'),'--out-dir',str(out)],check=True)
    report={'selectedSlugs':[e['slug'] for e in episodes],'schemaVersion':1,'style':catalog['version'],'checkedAt':datetime.now(timezone.utc).isoformat(),'inputs':inputs,'images':[],'plannedTypography':[],'installed':False}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        report['runtime']={'chromium':browser.version,'playwright':importlib.metadata.version('playwright')}
        page=browser.new_page(device_scale_factor=1)
        for ep in episodes:
            for size,dimensions in SIZES.items():
                p=out/ep['slug']/f'cover-{size}'
                bounds,groups=inspect(page,p.with_suffix('.svg'),size)
                page.screenshot(path=str(p.with_suffix('.png')),type='png')
                page.screenshot(path=str(p.with_suffix('.jpg')),type='jpeg',quality=94)
                for ext in ['png','jpg']:
                    with Image.open(p.with_suffix('.'+ext)) as im: assert im.size==dimensions
                report['images'].append({'slug':ep['slug'],'number':ep['number'],'size':size,'dimensions':list(dimensions),**{ext+'Sha256':sha(p.with_suffix('.'+ext)) for ext in ['svg','png','jpg']},'textBounds':bounds,'groupBounds':groups})
        for p in sorted((out/'typography-only').glob('*.svg')):
            size=p.stem.rsplit('-',1)[1]
            bounds,groups=inspect(page,p,size)
            report['plannedTypography'].append({'name':p.name,'size':size,'passed':True,'textBounds':bounds,'scope':'Typography only; not produced or published episode art'})
        browser.close()
    ep=episodes[0]
    with Image.open(out/ep['slug']/'cover-16x9.jpg') as im:
        preview=Image.new('RGB',(1024,660),'#211D1B')
        preview.paste(im.resize((960,540),Image.Resampling.LANCZOS),(32,88))
        font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',30)
        ImageDraw.Draw(preview).text((32,24),'Kafka · '+ep['number']+' / 系列统一封面',font=font,fill='#FFF1E8')
        preview.save(out/'preview.png');preview.save(out/'preview.jpg',quality=95)
    report['passed']=True
    (out/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"Checked {len(report['images'])} covers and {len(report['plannedTypography'])} typography-only layouts")

if __name__=='__main__': main()
