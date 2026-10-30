#!/usr/bin/env python3
"""Exercise this episode's long source panel without changing production inputs."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--out',type=Path,default=D/'qa/site-supplement');a=ap.parse_args();o=a.out.resolve();o.mkdir(parents=True,exist_ok=True)
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'base':a.base,'scope':'Chromium 390px touch simulation; no physical phone or external-source destination access claim.','checks':[],'screenshots':[],'pass':False,'visualReviewed':False}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
   c=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1);p=c.new_page();p.goto(a.base.rstrip('/')+'/episodes/'+D.name+'/',wait_until='domcontentloaded');p.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
   for theme in ['light','dark']:
    p.evaluate('(t)=>document.documentElement.dataset.theme=t',theme);tr=p.locator('[data-source-trigger="A2"]');tr.scroll_into_view_if_needed();tr.tap();panel=p.locator('[data-source-panel="A2"]');p.wait_for_function('document.querySelector("[data-source-panel=A2]").matches(":popover-open")');before=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');rect=panel.bounding_box();assert before['scrollHeight']>before['height']
    x=rect['x']+rect['width']*.7;y1=rect['y']+rect['height']*.82;y2=rect['y']+rect['height']*.2;cdp=c.new_cdp_session(p)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y1}]})
    for k in range(1,9):
     cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y1+(y2-y1)*k/8}]});p.wait_for_timeout(35)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('document.querySelector("[data-source-panel=A2]").scrollTop>0');after=panel.evaluate('(e)=>({top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})');link=panel.locator('cite a');link.focus();lr=link.bounding_box();pr=panel.bounding_box();assert lr and lr['y']>=pr['y'] and lr['y']+lr['height']<=pr['y']+pr['height'];assert link.get_attribute('href').startswith('https://');assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
    f=o/f'quote-A2-bottom-{theme}-390.png';p.screenshot(path=str(f));report['screenshots'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});report['checks'].append({'name':'A2 actual touch scroll exposes focusable source link','theme':theme,'pass':True,'before':before,'after':after,'sourceLink':link.get_attribute('href')});p.keyboard.press('Escape');p.wait_for_function('!document.querySelector("[data-source-panel=A2]").matches(":popover-open")')
   browser.close()
  report['pass']=True
 finally:
  report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(o/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'pass':report['pass'],'checks':len(report['checks']),'output':str(o)}))
if __name__=='__main__':main()
