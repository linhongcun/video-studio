#!/usr/bin/env python3
"""Render only P07 through the unchanged shared puzzle SVG template."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import importlib.metadata
from PIL import Image
from playwright.sync_api import sync_playwright

D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
SHARED=ROOT/'episodes/_shared/puzzles-covers'
SIZES={'16x9':(1920,1080),'3x4':(1080,1440),'4x3':(1440,1080)}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inputs=[D/'render-covers.py',D/'render-covers.mjs']+[SHARED/n for n in ['template.mjs','diagrams.mjs','catalog.json','background.png','README.md']]
    binding={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    catalog=json.loads((SHARED/'catalog.json').read_text())
    ep=next(e for e in catalog['episodes'] if e['slug']=='birthday-paradox')
    subprocess.run(['node',str(D/'render-covers.mjs')],check=True)
    report={'schemaVersion':1,'scope':'Only newly produced P07; no previous covers installed or regenerated.',
      'style':catalog['version'],'episode':'birthday-paradox','checkedAt':datetime.now(timezone.utc).isoformat(),
      'inputs':binding,'images':[],'visualReview':'pending'}
    with sync_playwright() as pw:
      browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      report['runtime']={'chromium':browser.version,'playwright':importlib.metadata.version('playwright')}
      page=browser.new_page(device_scale_factor=1)
      for size,(w,h) in SIZES.items():
        stem=D/f'cover-{size}'
        page.set_viewport_size({'width':w,'height':h})
        page.set_content('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#171326}svg{display:block}</style>'+stem.with_suffix('.svg').read_text())
        page.evaluate('document.fonts.ready')
        bounds=page.evaluate('''() => [...document.querySelectorAll('text')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.element||'diagram-label',text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height}})''')
        groups=page.evaluate('''() => [...document.querySelectorAll('[data-group]')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.group,x:r.x,y:r.y,width:r.width,height:r.height}})''')
        for b in bounds:
          assert b['width']>0 and b['height']>0,('empty',size,b)
          assert b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+.1 and b['y']+b['height']<=h+.1,('COPYFIT',size,b)
          if size=='4x3': assert b['x']>=315 and b['x']+b['width']<=1125 and b['y']+b['height']<918,('4x3 safety',b)
          if size=='16x9': assert b['y']+b['height']<918,('16x9 control safety',b)
        identity=next(b for b in groups if b['id']=='identity')
        title=next(b for b in groups if b['id']=='title')
        question=next(b for b in bounds if b['id']=='question')
        gap=9 if size=='4x3' else 12
        assert identity['y']+identity['height']+gap<=title['y'] and title['y']+title['height']+gap<=question['y'],('title separation',size)
        if size=='4x3':
          for b in groups: assert b['x']>=315 and b['x']+b['width']<=1125 and b['y']+b['height']<918,('4x3 group safety',b)
        page.screenshot(path=str(stem.with_suffix('.png')),type='png')
        page.screenshot(path=str(stem.with_suffix('.jpg')),type='jpeg',quality=94)
        for ext in ['png','jpg']:
          with Image.open(stem.with_suffix('.'+ext)) as im: assert im.size==(w,h)
        report['images'].append({'size':size,'dimensions':[w,h],'svgSha256':sha(stem.with_suffix('.svg')),'pngSha256':sha(stem.with_suffix('.png')),'jpgSha256':sha(stem.with_suffix('.jpg')),'textBounds':bounds,'groupBounds':groups})
      browser.close()
    (D/'poster.jpg').write_bytes((D/'cover-3x4.jpg').read_bytes())
    report['passed']=True
    (D/'cover-render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    manifest={'style':catalog['version'],'episodePart':ep['episodePart'],'seriesSource':'episodes/_shared/puzzles-covers',
      'generator':'episodes/puzzles/birthday-paradox/production/render-covers.py','sourceSha256':binding,
      'sitePoster':'cover-16x9.jpg','portraitPoster':'poster.jpg',
      'covers':{i['size']:{k:i[k] for k in ['dimensions','jpgSha256','pngSha256']} for i in report['images']}}
    (D/'cover-style.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('P07 three-ratio SVG/PNG/JPG checked; visual review remains separate.')

if __name__=='__main__': main()
