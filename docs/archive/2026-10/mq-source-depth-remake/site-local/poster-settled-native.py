"""Supplement the initial native poster captures after media loading settles.

Only writes QA artifacts. No source/media changes, route fulfillment or TLS bypass.
"""
from pathlib import Path
import functools, hashlib, http.server, importlib.util, json, threading
from playwright.sync_api import sync_playwright

R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
BASE=R/'docs/archive/2026-10/mq-source-depth-remake'
spec=importlib.util.spec_from_file_location('native_mq_site_qa',BASE/'qa-site.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(qa.RangeHandler,directory=str(R/'site/dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}/video-studio'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  for slug in ['kafka-consumer-groups','kafka-send-confirmation']:
   report={'browserVersion':browser.version,'nativeTransport':True,'noTLSBypass':True,'noRequestFulfillment':True,'initialPosterCapturesRetained':True,'checks':[],'errors':[],'visualReviewed':False,'limitations':['Simulated Chromium viewport, not a physical mobile device.','Initial poster screenshots captured transient native loading marks and remain in the main report. These additional captures wait for loaded and idle media.']}
   O=BASE/'site-local'/slug
   for w,h in [(1440,1000),(390,844)]:
    ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600,reduced_motion='reduce')
    ctx.add_init_script("localStorage.setItem('vs:sticky-off','1')")
    page=ctx.new_page();page.set_default_timeout(20000)
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.goto(origin+f'/episodes/{slug}/',wait_until='domcontentloaded')
    v=page.locator('video');v.scroll_into_view_if_needed()
    v.evaluate("async v=>{v.muted=true;v.preload='auto';const p=new Image();p.src=v.poster;await p.decode();v.load()}")
    page.wait_for_function('(()=>{const v=document.querySelector("video");return v.readyState===4&&v.networkState===1&&!v.seeking&&v.paused&&v.currentTime===0})()')
    page.wait_for_timeout(750)
    facts=v.evaluate('(v)=>({readyState:v.readyState,networkState:v.networkState,currentTime:v.currentTime,paused:v.paused,seeking:v.seeking,poster:v.poster,buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)])})')
    assert facts['readyState']==4 and facts['networkState']==1 and facts['paused'] and not facts['seeking'] and facts['currentTime']==0
    output=O/f'poster-settled-native-{w}.png';page.screenshot(path=str(output))
    report['checks'].append({'width':w,'pass':True,'facts':facts,'file':output.name,'sha256':sha(output)})
    ctx.close()
   assert not report['errors'];report['pass']=True
   (O/'poster-settled-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  browser.close()
finally:
 server.shutdown();server.server_close()
