#!/usr/bin/env python3
"""Inspect P10 article and complete source panels using actual input gestures."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, functools, hashlib, http.server, importlib.util, json, threading, traceback
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]
R=next(p for p in D.parents if (p/'AGENTS.md').is_file()and(p/'site/package.json').is_file())
spec=importlib.util.spec_from_file_location('p10_site',D/'qa/site-independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PANEL_STATE=r'''async e=>{
 await document.fonts.ready;let prior=-1,stable=0;
 for(let i=0;i<120&&stable<4;i++){await new Promise(requestAnimationFrame);stable=Math.abs(e.scrollTop-prior)<.01?stable+1:0;prior=e.scrollTop;}
 const p=e.getBoundingClientRect(),keys=['blockquote','.source-translation','.source-support','cite a','.source-identity','.source-location','.source-access'];
 return{top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight,contentWidth:e.clientWidth,scrollWidth:e.scrollWidth,stableFrames:stable,panel:{x:p.x,y:p.y,width:p.width,height:p.height},
 blocks:keys.map(selector=>{const n=e.querySelector(selector);if(!n)return null;const r=n.getBoundingClientRect();
 return{selector,text:n.innerText,height:r.height,visibleStart:Math.max(0,p.top-r.top),visibleEnd:Math.min(r.height,p.bottom-r.top)};}).filter(Boolean)};
}'''
def covered_height(intervals):
 end=total=0.0
 for start,stop in sorted(intervals):
  if stop>max(end,start):total+=stop-max(end,start)
  end=max(end,stop)
 return total
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base-url');ap.add_argument('--out',type=Path,default=D/'qa/site-local-reading');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);assert not(out/'report.json').exists(),'Preserve prior evidence; choose a fresh --out'
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'pass':False,'checks':[],'screenshots':[],'visualReviewed':False,'readingObservations':[],'sourcePanelObservations':[],'scope':'Current Chromium desktop/mobile simulation. Complete panel coverage uses actual wheel/touch gestures only when overflowing. No physical-phone, legacy-browser or semantic-audio claim.'}
 before={n:sha(D/n)for n in ['script.md','article.mdx','references.json','model-verification.json','storyboard.json']};report['sourceInputSHA256']=before
 receipt=json.loads((D/'reference-appendix.json').read_text());assert sha(D/'video.mp4')==sha(D.parent/'publication/video.mp4')==receipt['outputSHA256'];report['videoSHA256']=receipt['outputSHA256']
 if not a.base_url:assert sha(R/'site/dist/episodes/prisoners-light/video.mp4')==receipt['outputSHA256']
 sources={r['id']:r for r in json.loads((D/'references.json').read_text())['sources']};server=None
 if a.base_url:base=a.base_url.rstrip('/')
 else:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 report['base']=base
 def snap(p,name):
  f=out/(name+'.png');p.screenshot(path=str(f));report['screenshots'].append({'file':f.name,'sha256':sha(f)})
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);report['browserVersion']=b.version
   for w,h in [(1440,1000),(390,844)]:
    c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600);p=c.new_page();p.goto(base+'/episodes/prisoners-light/',wait_until='domcontentloaded');p.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
    for theme in ['light','dark']:
     p.locator('.theme-trigger').click();p.locator(f'[data-theme-opt="{theme}"]').click();assert p.evaluate('document.documentElement.dataset.theme')==theme
     for title,name in [('小结','conclusion'),('参考资料','references')]:
      heading=p.locator('.prose h2').filter(has_text=title).first
      o=heading.evaluate(r'''async e=>{
       await document.fonts.ready;e.scrollIntoView({block:'start',behavior:'instant'});let prior='',stable=0;
       for(let i=0;i<120&&stable<4;i++){await new Promise(requestAnimationFrame);const r=e.getBoundingClientRect(),value=[scrollY,r.x,r.y,r.width,r.height].join(',');stable=value===prior?stable+1:0;prior=value;}
       const next=e.nextElementSibling,walker=document.createTreeWalker(next,NodeFilter.SHOW_TEXT);let first;while((first=walker.nextNode())&&!first.textContent.trim()){};if(!first)throw Error('No next reading text');
       const range=document.createRange();range.setStart(first,0);range.setEnd(first,Math.min(first.length,1));const r=e.getBoundingClientRect(),n=next.getBoundingClientRect(),t=range.getBoundingClientRect(),v=document.querySelector('video').getBoundingClientRect(),header=document.querySelector('header').getBoundingClientRect(),hit=document.elementFromPoint(r.x+Math.min(120,r.width)/2,r.y+r.height/2);
       const rect=b=>({x:b.x,y:b.y,width:b.width,height:b.height,bottom:b.bottom,right:b.right});return{scrollTop:scrollY,viewport:{width:innerWidth,height:innerHeight},heading:rect(r),nextBlock:rect(n),nextTextStart:rect(t),nextBlockExtendsBelowViewport:n.bottom>innerHeight,header:rect(header),player:rect(v),stableFrames:stable,headingHitBelongsToHeading:hit===e||e.contains(hit),overlapsPlayer:r.left<v.right&&r.right>v.left&&r.top<v.bottom&&r.bottom>v.top};
      }''')
      o.update(headingTitle=title,theme=theme,width=w);report['readingObservations'].append(o);snap(p,f'{name}-{theme}-{w}');r,n=o['heading'],o['nextBlock']
      assert o['stableFrames']>=4 and o['headingHitBelongsToHeading']and not o['overlapsPlayer'];assert r['y']>=o['header']['bottom']-1 and r['bottom']<=h+1 and r['x']>=0 and r['right']<=w+1
      assert n['y']>=r['bottom']and o['nextTextStart']['y']>=r['bottom']and o['nextTextStart']['bottom']<=h+1;assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
      report['checks'].append({'name':'actual heading and beginning of next content readable','heading':title,'theme':theme,'width':w,'pass':True})
      if name=='references':
       last=heading.locator('xpath=following-sibling::*[self::ul or self::ol][1]').locator('li').last;last.evaluate('(e)=>e.scrollIntoView({block:"end",behavior:"instant"})');p.wait_for_timeout(150);r=last.bounding_box();assert last.is_visible()and r
       ending=last.evaluate(r'''e=>{const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let n,last;while((n=walker.nextNode()))if(n.textContent.trim())last=n;if(!last)throw Error('No reference ending text');const range=document.createRange();range.setStart(last,last.length-1);range.setEnd(last,last.length);const r=range.getBoundingClientRect();return{x:r.x,y:r.y,right:r.right,bottom:r.bottom,headerBottom:document.querySelector('header').getBoundingClientRect().bottom};}''');assert ending['y']>=ending['headerBottom']-1 and ending['bottom']<=h+1 and ending['x']>=0 and ending['right']<=w+1
       snap(p,f'references-end-{theme}-{w}');report['checks'].append({'name':'reference list ending text reached; full item bounds recorded without requiring a long paragraph to fit one viewport','theme':theme,'width':w,'lastItemBounds':r,'endingTextBounds':ending,'pass':True})
     for sid in ['R1','R2']:
      tr=p.locator(f'[data-source-trigger="{sid}"]');tr.scroll_into_view_if_needed();p.mouse.move(0,0);tr.tap()if w<600 else tr.click();panel=p.locator(f'[data-source-panel="{sid}"]');p.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);source=sources[sid]
      assert ' '.join(panel.locator('blockquote').inner_text().split())==' '.join(source['quotation']['text'].split());assert panel.locator('cite a').inner_text()==source['title']and panel.locator('cite a').get_attribute('href')==source['url']
      assert ' '.join(panel.locator('.source-identity').inner_text().split())==' '.join((source.get('author',source['organization'])+' · '+source['version']).split())
      assert ' '.join(source['quotation']['locator'].split())in' '.join(panel.locator('.source-location').inner_text().split());assert panel.locator('.source-access time').inner_text()==source['verification']['checkedAt']and panel.locator('.source-access time').get_attribute('datetime')==source['verification']['checkedAt']
      prior=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');panel.evaluate('(e)=>e.scrollTop=0');states=[]
      for step in range(16):
       state=panel.evaluate(PANEL_STATE);assert state['stableFrames']>=4 and state['scrollWidth']<=state['contentWidth']+1;r=state['panel'];assert r['x']>=0 and r['x']+r['width']<=w+1 and r['y']>=0 and r['y']+r['height']<=h+1
       if not step:assert state['top']==0
       states.append(state);snap(p,f'quote-{sid}-{theme}-{w}-segment-{step:02}')
       if state['scrollHeight']-state['height']-state['top']<=2:break
       top=state['top']
       if w<600:
        cdp=c.new_cdp_session(p);x,start,end=r['x']+r['width']*.7,r['y']+r['height']*.8,r['y']+r['height']*.2;cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':start}]})
        for k in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':start+(end-start)*k/8}]});p.wait_for_timeout(25)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});cdp.detach()
       else:p.mouse.move(r['x']+r['width']*.7,r['y']+r['height']*.7);p.mouse.wheel(0,max(120,r['height']*.6))
       p.wait_for_function('({id,top})=>document.querySelector(`[data-source-panel="${id}"]`).scrollTop>top',arg={'id':sid,'top':top})
      else:raise AssertionError('Source panel did not reach end through bounded real gestures')
      coverage={}
      for state in states:
       for block in state['blocks']:
        entry=coverage.setdefault(block['selector'],{'text':block['text'],'height':block['height'],'intervals':[]});assert entry['text']==block['text']
        if block['visibleEnd']>block['visibleStart']:entry['intervals'].append([block['visibleStart'],block['visibleEnd']])
      assert set(coverage)=={'blockquote','.source-translation','.source-support','cite a','.source-identity','.source-location','.source-access'},'Expected source panel content block missing'
      for entry in coverage.values():entry['coveredHeight']=covered_height(entry['intervals']);assert entry['text'].strip()and entry['height']>0 and entry['height']-entry['coveredHeight']<=2,entry
      report['sourcePanelObservations'].append({'source':sid,'theme':theme,'width':w,'priorPositionBeforeReset':prior,'qaResetScrollTopToZero':True,'states':states,'coverage':coverage,'gestureCount':len(states)-1,'gestureType':'touch'if w<600 else'wheel','overflowing':states[0]['scrollHeight']>states[0]['height']+1});report['checks'].append({'name':'complete source panel covered with real gestures only when needed','source':sid,'theme':theme,'width':w,'segments':len(states),'pass':True});p.keyboard.press('Escape');p.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid)
    c.close()
   b.close()
  report['pass']=True
 except Exception as error:report['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};raise
 finally:
  report['sourceInputsUnchanged']=all(sha(D/n)==value for n,value in before.items());report['pass']=report['pass']and report['sourceInputsUnchanged'];report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if server:server.shutdown();server.server_close()
 print(json.dumps({'pass':report['pass'],'checks':len(report['checks']),'out':str(out)}))
if __name__=='__main__':main()
