#!/usr/bin/env python3
"""Observe natural paused poster loading without load, play, seek or controls edits."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, functools, hashlib, http.server, importlib.util, json, threading, time, traceback
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('p10_site',D/'qa/site-independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 assert sha(D/'video.mp4')==sha(D.parent/'publication/video.mp4')
 server=None
 if a.base:base=a.base.rstrip('/')
 else:
  assert sha(m.R/'site/dist/episodes/prisoners-light/video.mp4')==sha(D/'video.mp4')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.RangeHandler,directory=str(m.R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':False,'visualReviewed':False,'base':base,'videoSHA256':sha(D/'video.mp4'),'scope':'Natural fresh Chromium initial poster observation only. No load/play/currentTime assignment, source change, controls change or CSS hiding. Screenshots need separate actual visual classification.','samples':[],'events':{},'limitations':['Current Chromium desktop/mobile simulation, not physical devices.','No automatic native shadow-control spinner detector claimed.']}
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);report['browserVersion']=b.version
   for w,h in [(1440,1000),(390,844)]:
    c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600);c.add_init_script("localStorage.setItem('vs:sticky-off','1');window.__qaPosterEvents=[];document.addEventListener('loadedmetadata',e=>{if(e.target.tagName==='VIDEO')window.__qaPosterEvents.push({name:'loadedmetadata',at:performance.now()})},true);for(const name of ['loadstart','loadeddata','canplay','canplaythrough','suspend','progress','waiting','stalled'])document.addEventListener(name,e=>{if(e.target.tagName==='VIDEO')window.__qaPosterEvents.push({name,at:performance.now()})},true)")
    p=c.new_page();p.goto(base+'/episodes/prisoners-light/',wait_until='domcontentloaded');v=p.locator('video');v.scroll_into_view_if_needed();v.evaluate('async v=>{v.muted=true;const p=new Image();p.src=v.poster;await p.decode();await document.fonts.ready}');p.wait_for_function('document.querySelector("video").readyState>=1');start=time.monotonic()
    for delay in [.7,3,8,15]:
     p.wait_for_timeout(max(0,delay-(time.monotonic()-start))*1000)
     state=v.evaluate('v=>({currentTime:v.currentTime,paused:v.paused,seeking:v.seeking,readyState:v.readyState,networkState:v.networkState,preload:v.preload,controls:v.controls,poster:v.poster,buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)])})');assert state['paused']and state['currentTime']==0 and not state['seeking']and state['controls'];f=a.out/f'poster-natural-{w}-{delay:g}s.png';p.screenshot(path=str(f));report['samples'].append({'width':w,'requestedIdleSecondsAfterMetadata':delay,'actualIdleSecondsAfterMetadata':time.monotonic()-start,'state':state,'file':f.name,'sha256':sha(f)})
    report['events'][str(w)]=p.evaluate('window.__qaPosterEvents');c.close()
   b.close()
  report['passed']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if server:server.shutdown();server.server_close()
 print(json.dumps({'passed':report['passed'],'samples':len(report['samples']),'out':str(a.out)}))
if __name__=='__main__':main()
