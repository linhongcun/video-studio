#!/usr/bin/env python3
"""Observe actual body playback after native fullscreen controls naturally idle.

Never changes controls CSS or video.controls. This complements the separately
recorded controls-visible paused capture, rather than replacing that evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,base64,hashlib,importlib.util,json,traceback
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('p08_native_tools',D/'qa/site-independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 primary=json.loads((D/'qa/site-online-native/report.json').read_text());assert primary['pass']and primary['videoSha256']==sha(D/'video.mp4');board=json.loads((D/'storyboard.json').read_text());rows=[{'text':x['text'],'from':s['from']+x['from'],'toExclusive':s['from']+x['to']+1}for sc in board['scenes']for s in sc['shots']for x in s['subtitles']];cue=max(rows,key=lambda x:len(x['text']));start=cue['from']+15
 report={'startedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':False,'videoSHA256':primary['videoSha256'],'caption':cue,'requestedStartFrame':start,'viewport':[844,390],'nativeIdleWaitMilliseconds':4200,'controlsChanged':False,'controlsCSSChanged':False,'visualReviewed':False,'scope':'Current Chromium touch simulation, actual fullscreen playback and natural native idle UI. Separate prior paused-controls observation remains valid.'}
 try:
  with sync_playwright()as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);c=b.new_context(viewport={'width':844,'height':390},device_scale_factor=1,is_mobile=True,has_touch=True);p=c.new_page();p.goto(a.base.rstrip('/')+'/episodes/hat-parity/',wait_until='domcontentloaded');v=p.locator('video');v.evaluate('async v=>{v.muted=true;await document.fonts.ready;await v.play()}');p.wait_for_function('document.querySelector("video").currentTime>.1');v.evaluate('v=>v.pause()');r=p.evaluate(m.SEEK,{'time':(start+.5)/30,'pts':start/30});assert abs(r['mediaTime']-start/30)<.0000011
   p.evaluate('''()=>{const b=document.createElement('button');b.id='qa-playing-fs';b.textContent='Fullscreen QA';Object.assign(b.style,{position:'fixed',left:'0',top:'0',zIndex:999999});b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b)}''');p.locator('#qa-playing-fs').click();p.wait_for_function('document.fullscreenElement===document.querySelector("video")');v.evaluate('v=>v.play()');p.mouse.move(0,0);p.wait_for_timeout(4200)
   snapshot=p.evaluate('''async()=>{const v=document.querySelector('video');return await new Promise(resolve=>v.requestVideoFrameCallback((t,md)=>{const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);resolve({mediaTime:md.mediaTime,currentTime:v.currentTime,paused:v.paused,controls:v.controls,isVideoFullscreen:document.fullscreenElement===v,viewport:{width:innerWidth,height:innerHeight},nativeModes:Array.from(v.textTracks,t=>t.mode),png:c.toDataURL('image/png')})}))}''');assert snapshot['controls']and not snapshot['paused']and snapshot['isVideoFullscreen'];assert cue['from']/30<=snapshot['mediaTime']<cue['toExclusive']/30;assert all(mode!='showing'for mode in snapshot['nativeModes']);decoded=a.out/'playing-body-decoded.png';decoded.write_bytes(base64.b64decode(snapshot.pop('png').split(',',1)[1]));screenshot=a.out/'playing-body-fullscreen.png';p.screenshot(path=str(screenshot));after=v.evaluate('v=>({currentTime:v.currentTime,paused:v.paused,controls:v.controls})');assert not after['paused']and after['controls']and cue['from']/30<=after['currentTime']<cue['toExclusive']/30;report.update(snapshot=snapshot,afterScreenshot=after,decoded={'file':decoded.name,'sha256':sha(decoded)},screenshot={'file':screenshot.name,'sha256':sha(screenshot)});v.evaluate('v=>v.pause()');p.evaluate('document.exitFullscreen()');c.close();b.close()
  report['passed']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:report['finishedAtUTC']=datetime.now(timezone.utc).isoformat();(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':True,'snapshot':report['snapshot'],'afterScreenshot':report['afterScreenshot'],'out':str(a.out)},ensure_ascii=False))
if __name__=='__main__':main()
