from pathlib import Path
from playwright.sync_api import sync_playwright
import json,datetime,hashlib
root=Path('/workspace/video-studio');d=root/'episodes-codex/observer-pattern';out=d/'revisions/observer-first/browser-qa'; cases=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 for name,viewport in [('desktop',{'width':1440,'height':900}),('mobile-landscape',{'width':844,'height':390})]:
  c=b.new_context(viewport=viewport,device_scale_factor=1);page=c.new_page();page.set_default_timeout(10000)
  page.goto('http://127.0.0.1:4387/video-studio/episodes/observer-pattern/',wait_until='networkidle')
  page.wait_for_function('()=>document.querySelector("video").readyState>=1')
  page.evaluate('''()=>{const v=document.querySelector('video');v.muted=true;for(const t of v.textTracks)t.mode='showing';const q=document.createElement('button');q.id='qa-fullscreen';q.textContent='QA fullscreen';Object.assign(q.style,{position:'fixed',top:'0',left:'0',zIndex:'100000'});q.addEventListener('click',()=>v.requestFullscreen());document.body.append(q)}''')
  page.locator('#qa-fullscreen').click();page.wait_for_function('()=>document.fullscreenElement===document.querySelector("video")')
  for label,t in [('java',145.2),('references',150.2)]:
   page.evaluate('(t)=>{const v=document.querySelector("video");v.pause();v.currentTime=t}',t)
   page.wait_for_function('()=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=2}')
   page.wait_for_timeout(200)
   state=page.evaluate('''()=>{const v=document.querySelector('video');const r=v.getBoundingClientRect();return {paused:v.paused,time:v.currentTime,duration:v.duration,fullscreen:document.fullscreenElement===v,activeCues:[...v.textTracks].flatMap(t=>[...(t.activeCues||[])].map(c=>c.text)),bounds:{x:r.x,y:r.y,width:r.width,height:r.height},viewport:{width:innerWidth,height:innerHeight}}}''')
   assert state['paused'] and state['fullscreen'] and not state['activeCues']
   page.mouse.move(viewport['width']/2,viewport['height']-30);page.wait_for_timeout(200)
   path=out/(name+'-fullscreen-api-'+label+'.png');page.screenshot(path=str(path))
   cases.append({'case':name+'-'+label,'state':state,'screenshot':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  c.close()
 b.close()
r={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executedBy':'Codex root','method':'Actual browser Fullscreen API entered through trusted button click; paused decoded video at Java and reference cards with native controls enabled.','videoSha256':hashlib.sha256((root/'episodes/observer-pattern/video.mp4').read_bytes()).hexdigest(),'cases':cases,'automatedPassed':True,'visualReview':'Pending actual screenshot inspection','limitations':['Local Chromium only; mobile is an emulated landscape viewport, not a real phone.','Fullscreen API layout was exercised; this does not establish reliable native fullscreen-icon interaction on every phone.']}
(d/'qa-observer-first-fullscreen-api.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':True,'cases':len(cases),'screenshots':[c['screenshot'] for c in cases]}))
