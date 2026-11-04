#!/usr/bin/env python3
"""Targeted online body-fullscreen controls check, after primary native acceptance.

Select the longest actual subtitle plus the two frozen Figure frames. Exact
rVFC Canvas frames and actual Fullscreen API viewport captures stay separate.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,base64,hashlib,importlib.util,json,traceback
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('p08_native_tools',D/'qa/site-independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 primary=json.loads((D/'qa/site-online-native/report.json').read_text());assert primary['pass'] and primary['videoSha256']==sha(D/'video.mp4')
 board=json.loads((D/'storyboard.json').read_text());cues=[dict(text=c['text'],start=s['from']+c['from'],end=s['from']+c['to']+1)for sc in board['scenes']for s in sc['shots']for c in s['subtitles']];longest=max(cues,key=lambda c:len(c['text']));widest_frame=(longest['start']+longest['end'])//2
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':False,'videoSHA256':primary['videoSha256'],'primaryReportSHA256':sha(D/'qa/site-online-native/report.json'),'purpose':'Actual mobile-landscape body-fullscreen pause captures with native controls visible; longest subtitle selected by current text length plus both frozen Figure frames.','longestSubtitle':longest,'viewport':[844,390],'samples':[],'visualReviewed':False,'limitations':['Chromium touch simulation and Fullscreen API, not physical-phone testing.','A paused controls-visible view is sampled, not every device or every possible controls theme.','Each rVFC exact frame is confirmed inline before Fullscreen; Fullscreen capture requires exactly the same actual paused currentTime returned by the inline seek (API microsecond quantization retained), actual fullscreenElement and controls. No paused rVFC-in-Fullscreen callback guarantee is claimed.']}
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);c=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1,is_mobile=True,has_touch=True);p=c.new_page();p.goto(a.base.rstrip('/')+'/episodes/hat-parity/',wait_until='domcontentloaded');v=p.locator('video');v.evaluate('async v=>{v.muted=true;await document.fonts.ready;await v.play()}');p.wait_for_function('document.querySelector("video").currentTime>.1');v.evaluate('v=>v.pause()');assert not v.evaluate('v=>Array.from(v.textTracks).some(t=>t.mode==="showing")')
   p.evaluate('''()=>{const b=document.createElement('button');b.id='qa-body-fs';b.textContent='Fullscreen QA';Object.assign(b.style,{position:'fixed',left:'0',top:'0',zIndex:999999});b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b)}''');# Follow primary acceptance order: exact inline callback before entering Fullscreen.
   for frame,name in [(widest_frame,'longest-subtitle'),(1740,'first-message-figure'),(3375,'zero-even-figure')]:
    r=p.evaluate(m.SEEK,{'time':(frame+.5)/30,'pts':frame/30});assert r['paused']and not r['seeking']and abs(r['mediaTime']-frame/30)<.0000011;decoded=a.out/f'{name}-decoded-f{frame}.png';decoded.write_bytes(base64.b64decode(r.pop('png').split(',',1)[1]));p.locator('#qa-body-fs').click();p.wait_for_function('document.fullscreenElement===document.querySelector("video")');p.mouse.move(800,345);p.wait_for_timeout(350);actual_after_fs=v.evaluate('(v)=>({currentTime:v.currentTime,paused:v.paused,seeking:v.seeking})');report.setdefault('entryObservations',[]).append({'frame':frame,'requestedTargetTime':(frame+.5)/30,'actualInlineCurrentTime':r['currentTime'],'after':actual_after_fs});assert actual_after_fs['currentTime']==r['currentTime'],actual_after_fs;geom=p.evaluate('''()=>{const v=document.querySelector('video'),r=v.getBoundingClientRect();return{isVideoFullscreen:document.fullscreenElement===v,paused:v.paused,controls:v.controls,viewport:{width:innerWidth,height:innerHeight},rect:{x:r.x,y:r.y,width:r.width,height:r.height}}}''');assert geom['isVideoFullscreen']and geom['controls']and geom['paused'];screen=a.out/f'{name}-fullscreen-f{frame}.png';p.screenshot(path=str(screen));report['samples'].append({'frame':frame,'tag':name,'rVFC':r,'geometry':geom,'decoded':{'file':decoded.name,'sha256':sha(decoded)},'screenshot':{'file':screen.name,'sha256':sha(screen)},'exactFrameVerifiedInlineBeforeFullscreen':True});p.evaluate('document.exitFullscreen()');p.wait_for_function('document.fullscreenElement===null');p.wait_for_timeout(400)
   c.close();b.close()
  report['passed']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':True,'samples':len(report['samples']),'longestSubtitle':longest,'out':str(a.out)},ensure_ascii=False))
if __name__=='__main__':main()
