#!/usr/bin/env python3
"""Capture P08 conclusion/references and actual touch scrolling, using the local built site."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, functools, hashlib, http.server, importlib.util, json, threading, traceback
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]
R=next(p for p in D.parents if (p/'AGENTS.md').is_file()and(p/'site/package.json').is_file())
spec=importlib.util.spec_from_file_location('p08_site',D/'qa/site-independent.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-url');ap.add_argument('--out',type=Path,default=D/'qa/site-local-reading');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists(), 'Preserve earlier reports and use a fresh --out'
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'pass':False,'checks':[],'screenshots':[],'visualReviewed':False,'scope':'Chromium desktop and mobile touch simulation; no physical phone. Explicit reading-position captures and touch-scrolling of overflowing source panels.','sourceInputsUnchanged':None,'readingObservations':[]}
 before={n:hashlib.sha256((D/n).read_bytes()).hexdigest()for n in ['script.md','article.mdx','references.json','model-verification.json']}
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
    c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600);p=c.new_page();p.goto(base+'/episodes/hat-parity/',wait_until='domcontentloaded');p.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
    for theme in ['light','dark']:
     p.locator('.theme-trigger').click();p.locator(f'[data-theme-opt="{theme}"]').click();assert p.evaluate('document.documentElement.dataset.theme')==theme
     for title,name in [('小结','conclusion'),('参考资料','references')]:
      heading=p.locator('.prose h2').filter(has_text=title).first
      observation=heading.evaluate(r'''async e=>{
       await document.fonts.ready;e.scrollIntoView({block:'start',behavior:'instant'});
       let prior='',stable=0;
       for(let i=0;i<120&&stable<4;i++){await new Promise(requestAnimationFrame);const r=e.getBoundingClientRect();const value=[scrollY,r.x,r.y,r.width,r.height].join(',');stable=value===prior?stable+1:0;prior=value;}
       const r=e.getBoundingClientRect(),n=e.nextElementSibling.getBoundingClientRect(),v=document.querySelector('video').getBoundingClientRect(),header=document.querySelector('header').getBoundingClientRect(),hit=document.elementFromPoint(r.x+Math.min(120,r.width)/2,r.y+r.height/2);
       const rect=b=>({x:b.x,y:b.y,width:b.width,height:b.height,bottom:b.bottom,right:b.right});
       return{scrollTop:scrollY,scrollHeight:document.documentElement.scrollHeight,viewport:{width:innerWidth,height:innerHeight},heading:rect(r),nextBlock:rect(n),header:rect(header),player:rect(v),stableFrames:stable,headingHitBelongsToHeading:hit===e||e.contains(hit),overlapsPlayer:r.left<v.right&&r.right>v.left&&r.top<v.bottom&&r.bottom>v.top};
      }''')
      observation.update({'headingTitle':title,'theme':theme,'width':w});report['readingObservations'].append(observation);snap(p,f'{name}-{theme}-{w}');rect=observation['heading'];next_rect=observation['nextBlock']
      assert observation['stableFrames']>=4 and observation['headingHitBelongsToHeading'] and not observation['overlapsPlayer'], observation
      assert rect['y']>=observation['header']['bottom']-1 and rect['bottom']<=h+1 and rect['x']>=0 and rect['right']<=w+1, observation
      assert next_rect['y']>=rect['bottom'] and next_rect['bottom']<=h+1, observation
      assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
      report['checks'].append({'name':'stable reading heading and next content fully visible below header, without player occlusion or horizontal overflow','heading':title,'theme':theme,'width':w,'bounds':rect,'pass':True})
     if w<600:
      for sid in ['R1','R2']:
       tr=p.locator(f'[data-source-trigger="{sid}"]');tr.scroll_into_view_if_needed();tr.tap();panel=p.locator(f'[data-source-panel="{sid}"]');p.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);prior_scroll=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');panel.evaluate('(e)=>e.scrollTop=0');before_scroll=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');assert before_scroll['top']==0;rect=panel.bounding_box();assert rect
       gesture_executed=before_scroll['scrollHeight']>before_scroll['height']
       if gesture_executed:
        cdp=c.new_cdp_session(p);x=rect['x']+rect['width']*.7;start=rect['y']+rect['height']*.8;end=rect['y']+rect['height']*.2;cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':start}]})
        for k in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':start+(end-start)*k/8}]});p.wait_for_timeout(25)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).scrollTop>0',arg=sid)
       after=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');assert not gesture_executed or after['top']>before_scroll['top'];snap(p,f'quote-{sid}-touch-end-{theme}-{w}');report['checks'].append({'name':'source panel actual touch scroll when overflowing','theme':theme,'width':w,'source':sid,'priorPositionBeforeQAReset':prior_scroll,'qaResetScrollTopToZero':True,'before':before_scroll,'after':after,'touchScrollDelta':after['top']-before_scroll['top'],'scrollGestureExecuted':gesture_executed,'scope':'Actual touch gesture and changed scrollTop if overflowing; otherwise fully fitting panel and no scrolling claimed.','pass':True});p.keyboard.press('Escape');p.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid)
    c.close()
   b.close()
  report['pass']=True
 except Exception as error:
  report['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
  raise
 finally:
  report['sourceInputsUnchanged']=all(hashlib.sha256((D/n).read_bytes()).hexdigest()==d for n,d in before.items());report['pass']=report['pass']and report['sourceInputsUnchanged'];report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if server:server.shutdown();server.server_close()
 print(json.dumps({'pass':report['pass'],'checks':len(report['checks']),'out':str(out)}))
if __name__=='__main__':main()
