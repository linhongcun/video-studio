from pathlib import Path
import importlib.util,json,threading,functools,hashlib,datetime,subprocess
spec=importlib.util.spec_from_file_location('peakqa','/workspace/work/peak-site-qa/check.py');qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
from playwright.sync_api import sync_playwright
R=qa.R;W=qa.W
server=qa.http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(qa.RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
r={'scope':'Two representative paused initial-poster recaptures after readyState4/networkIdle and 800ms UI settling. Actual visual result reviewed separately; no disappearance claim from state alone. Original 26 assertions/18 screenshots unchanged; no CSS/controller hiding, play or media edits.','startedAt':qa.now(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'images':[],'errors':[],'passed':False}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(390,844)]:
   c=b.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=width<600,has_touch=width<600,reduced_motion='reduce');c.add_init_script("localStorage.setItem('vs:sticky-off','1')");p=c.new_page();p.set_default_timeout(20000);p.on('pageerror',lambda e:r['errors'].append(str(e)))
   for slug in ["idempotency","degradation"]:
    p.goto(base+f'/episodes/{slug}/',wait_until='domcontentloaded');v=p.locator('video');v.scroll_into_view_if_needed();p.evaluate('()=>{const v=document.querySelector("video");v.muted=true;v.preload="auto";v.load()}');p.wait_for_function('(()=>{const v=document.querySelector("video");return v.readyState===4&&v.networkState===1&&v.paused&&!v.seeking&&!v.error})()',timeout=8000);p.wait_for_timeout(800);p.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');state=v.evaluate('(v)=>({readyState:v.readyState,networkState:v.networkState,paused:v.paused,currentTime:v.currentTime,poster:v.poster})');assert state['currentTime']==0 and state['paused'];name=f'poster-idle-{slug}-{width}.png';p.screenshot(path=str(W/name));r['images'].append({'file':name,'sha256':qa.sha(W/name),'width':width,'slug':slug,'state':state})
   c.close()
  b.close()
 assert not r['errors'];r['passed']=True
finally:
 r['finishedAt']=qa.now();(W/'idle-poster-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');server.shutdown();server.server_close()
print(json.dumps({'passed':r['passed'],'images':len(r['images'])}))
