"""One bounded observation of each unmodified initial HTML poster state.

No media load/preload override, play, seek, route fulfillment, TLS bypass or UI hiding.
"""
from pathlib import Path
import functools, hashlib, http.server, importlib.util, json, threading
from playwright.sync_api import sync_playwright
R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
BASE=R/'docs/archive/2026-10/mq-source-depth-remake'
spec=importlib.util.spec_from_file_location('native_qa_transport',BASE/'qa-site.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(qa.RangeHandler,directory=str(R/'site/dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/video-studio'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for slug in ['kafka-consumer-groups','kafka-send-confirmation']:
   O=BASE/'site-local'/slug
   report={'browserVersion':browser.version,'nativeTransport':True,'naturalInitialHTML':True,'mediaCalls':[],'preloadOverride':False,'controlsHidden':False,'boundedCaptures':2,'screenshots':[],'errors':[],'visualReviewed':False,'limitations':['Simulated Chromium desktop/mobile viewport, not a physical phone.','Natural initial state observed once per viewport after poster Image.decode, document.fonts.ready and 750ms stability window. No play/seek or media reload.']}
   for w,h in [(1440,1000),(390,844)]:
    ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600,reduced_motion='reduce')
    page=ctx.new_page();page.set_default_timeout(20000);page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.goto(base+f'/episodes/{slug}/',wait_until='domcontentloaded')
    v=page.locator('video');v.scroll_into_view_if_needed()
    v.evaluate("async v=>{const image=new Image();image.src=v.poster;await image.decode();await document.fonts.ready}")
    page.wait_for_timeout(750)
    facts=v.evaluate('(v)=>({preloadAttribute:v.getAttribute("preload"),preload:v.preload,controlsAttribute:v.hasAttribute("controls"),controls:v.controls,readyState:v.readyState,networkState:v.networkState,currentTime:v.currentTime,paused:v.paused,seeking:v.seeking,poster:v.poster})')
    assert facts['paused'] and not facts['seeking'] and facts['currentTime']==0 and facts['controls']
    output=O/f'poster-natural-native-{w}.png';page.screenshot(path=str(output))
    report['screenshots'].append({'width':w,'facts':facts,'file':output.name,'sha256':sha(output)})
    ctx.close()
   assert not report['errors'];report['observationComplete']=True
   (O/'poster-natural-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  browser.close()
finally:
 server.shutdown();server.server_close()
