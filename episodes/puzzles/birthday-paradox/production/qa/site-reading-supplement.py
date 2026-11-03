#!/usr/bin/env python3
"""Capture P07 conclusion/references and actual touch scrolling, using the local built site."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, functools, hashlib, http.server, importlib.util, json, threading
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]
R=next(p for p in D.parents if (p/'AGENTS.md').is_file()and(p/'site/package.json').is_file())
spec=importlib.util.spec_from_file_location('p07_site',D/'qa/site-independent.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-url');ap.add_argument('--out',type=Path,default=D/'qa/site-local-reading');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'pass':False,'checks':[],'screenshots':[],'visualReviewed':False,'scope':'Chromium desktop and mobile touch simulation; no physical phone. Explicit reading-position captures and touch-scrolling of overflowing source panels.','sourceInputsUnchanged':None}
 before={n:hashlib.sha256((D/n).read_bytes()).hexdigest()for n in ['script.md','article.mdx','references.json','math-verification.json']}
 server=None
 if a.base_url:base=a.base_url.rstrip('/')
 else:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(module.RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 report['base']=base
 def snap(p,name):
  f=out/(name+'.png');p.screenshot(path=str(f));report['screenshots'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);report['browserVersion']=b.version
   for w,h in [(1440,1000),(390,844)]:
    c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600);p=c.new_page();p.goto(base+'/episodes/birthday-paradox/',wait_until='domcontentloaded');p.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
    for theme in ['light','dark']:
     p.locator('.theme-trigger').click();p.locator(f'[data-theme-opt="{theme}"]').click();assert p.evaluate('document.documentElement.dataset.theme')==theme
     for title,name in [('小结','conclusion'),('参考资料','references')]:
      heading=p.locator('.prose h2').filter(has_text=title).first;heading.evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})');p.wait_for_timeout(200);rect=heading.bounding_box();assert rect and rect['y']>=0 and rect['y']<200;assert not p.evaluate('document.documentElement.scrollWidth>innerWidth');snap(p,f'{name}-{theme}-{w}');report['checks'].append({'name':'reading heading visible without overflow','heading':title,'theme':theme,'width':w,'bounds':rect,'pass':True})
     if w<600:
      for sid in ['R1','R2']:
       tr=p.locator(f'[data-source-trigger="{sid}"]');tr.scroll_into_view_if_needed();tr.tap();panel=p.locator(f'[data-source-panel="{sid}"]');p.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);before_scroll=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');rect=panel.bounding_box();assert rect
       if before_scroll['scrollHeight']>before_scroll['height']:
        cdp=c.new_cdp_session(p);x=rect['x']+rect['width']*.7;start=rect['y']+rect['height']*.8;end=rect['y']+rect['height']*.2;cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':start}]})
        for k in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':start+(end-start)*k/8}]});p.wait_for_timeout(25)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).scrollTop>0',arg=sid)
       after=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');snap(p,f'quote-{sid}-touch-end-{theme}-{w}');report['checks'].append({'name':'source panel actual touch scroll when overflowing','theme':theme,'width':w,'source':sid,'before':before_scroll,'after':after,'pass':True});p.keyboard.press('Escape');p.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid)
    c.close()
   b.close()
  report['pass']=True
 finally:
  report['sourceInputsUnchanged']=all(hashlib.sha256((D/n).read_bytes()).hexdigest()==d for n,d in before.items());report['pass']=report['pass']and report['sourceInputsUnchanged'];report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if server:server.shutdown();server.server_close()
 print(json.dumps({'pass':report['pass'],'checks':len(report['checks']),'out':str(out)}))
if __name__=='__main__':main()
