#!/usr/bin/env python3
"""Bounded built-site checks, without changing production sources or media.

Local mode serves site/dist with byte ranges. --base selects the deployed site.
The Chromium path uses native transport only; no request fulfillment or TLS bypass.
"""
from pathlib import Path
from fractions import Fraction
import argparse,base64,datetime,functools,hashlib,http.server,json,re,subprocess,threading,traceback,urllib.request,ssl
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
D=None
SLUG=None
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class RangeHandler(http.server.SimpleHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass
 def handle(self):
  try:super().handle()
  except (ConnectionResetError,BrokenPipeError):pass
 def translate_path(self,path):
  if path.startswith('/video-studio/'):path=path[len('/video-studio'):]
  return super().translate_path(path)
 def send_head(self):
  self.byte_range=None;file=Path(self.translate_path(self.path))
  if file.is_file() and 'Range' in self.headers:
   m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
   if m:
    start=int(m[1]);end=min(int(m[2]) if m[2] else file.stat().st_size-1,file.stat().st_size-1)
    if start>=file.stat().st_size:self.send_error(416);return None
    f=file.open('rb');f.seek(start);self.byte_range=(start,end);self.send_response(206);self.send_header('Content-type',self.guess_type(str(file)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{file.stat().st_size}');self.send_header('Content-Length',str(end-start+1));self.end_headers();return f
  return super().send_head()
 def copyfile(self,src,dst):
  try:
   if self.byte_range:
    n=self.byte_range[1]-self.byte_range[0]+1
    while n:
     data=src.read(min(65536,n))
     if not data:break
     dst.write(data);n-=len(data)
   else:super().copyfile(src,dst)
  except (BrokenPipeError,ConnectionResetError):pass
SEEK=r'''async({time,pts})=>{const v=document.querySelector('video');v.pause();return await new Promise((resolve,reject)=>{let seeked=false,md=null,cb=null;const t=setTimeout(()=>{if(cb)v.cancelVideoFrameCallback(cb);reject(Error('Exact frame timeout '+time+' expected '+pts))},15000);const finish=()=>{if(!seeked||!md)return;clearTimeout(t);const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);resolve({currentTime:v.currentTime,mediaTime:md.mediaTime,paused:v.paused,seeking:v.seeking,readyState:v.readyState,activeCues:v.textTracks[0]?.activeCues?.length??null,png:c.toDataURL('image/png')})};const next=(t,m)=>{if(Math.abs(m.mediaTime-pts)<.0000011){md=m;finish()}else cb=v.requestVideoFrameCallback(next)};cb=v.requestVideoFrameCallback(next);v.addEventListener('seeked',()=>{seeked=true;finish()},{once:true});v.currentTime=time})}'''
def main():
 global D,SLUG
 ap=argparse.ArgumentParser();ap.add_argument('--base');ap.add_argument('--preview-drafts',action='store_true');ap.add_argument('--production',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();assert not(args.base and args.preview_drafts);D=args.production.resolve();SLUG=json.loads((D/'episode-config.json').read_text())['slug'];OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
 P=R/'episodes'/SLUG;meta=json.loads((P/'meta.json').read_text());receipt=json.loads((D/'reference-appendix.json').read_text());sb=json.loads((D/'storyboard.json').read_text());body=meta['referenceAppendix']['from'];total=meta['finalVideoFrames']
 assert sha(P/'video.mp4')==sha(D/'video.mp4')==receipt['outputSHA256']
 if not args.base:assert sha(R/'site/dist/episodes'/SLUG/'video.mp4')==sha(P/'video.mp4')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base,nb_frames:frame=best_effort_timestamp','-show_frames','-show_streams','-of','json',str(P/'video.mp4')],text=True));tb=Fraction(probe['streams'][0]['time_base']);pts=[Fraction(f['best_effort_timestamp'])*tb for f in probe['frames']];assert len(pts)==total and len(set(pts))==total
 chapters=[]
 for scene in sb['scenes']:
  if not chapters or chapters[-1]['id']!=scene['chapterId']:chapters.append({'id':scene['chapterId'],'start':scene['from']/30})
 published_series=[json.loads(p.read_text())['slug']for p in sorted((R/'episodes').glob('*/meta.json'))if (lambda m:m.get('series')=='message-queue'and (args.preview_drafts or not m.get('draft'))and not m.get('archived'))(json.loads(p.read_text()))]
 sources={s['id']:s for fn in ['references.json','article-sources.json']if(P/fn).exists()for s in json.loads((P/fn).read_text())['sources']}
 report={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executor':'Codex MQ05–MQ07 native-browser QA','draftPreview':args.preview_drafts,'base':args.base or 'local built site','videoSha256':sha(P/'video.mp4'),'bodyFrames':body,'finalFrames':total,'checks':[],'screenshots':[],'exactFrames':[],'errors':[],'verifiedHttpResponses':[],'pass':False,'visualReviewed':False,'limitations':['Chromium simulated desktop/mobile viewport, no physical phone or native mobile video chrome claim.','Fullscreen tested through user-gesture Fullscreen API, not hidden native controls.','No word ASR, full semantic listening or audience comprehension claim.']}
 def check(name,width,detail=None):report['checks'].append({'name':name,'width':width,'pass':True,'detail':detail})
 def snap(page,name):
  f=OUT/(name+'.png');page.screenshot(path=str(f));report['screenshots'].append({'file':f.name,'sha256':sha(f)})
 server=None
 if args.base:base=args.base.rstrip('/')
 else:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['browserVersion']=browser.version
   for w,h in [(1440,1000),(390,844)]:
    ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=w<600,has_touch=w<600,reduced_motion='reduce');ctx.add_init_script("localStorage.setItem('vs:sticky-off','1')");page=ctx.new_page()
    page.set_default_timeout(20000);page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.goto(base+'/series/message-queue/',wait_until='domcontentloaded');assert page.locator(f'a.lesson[href$="/episodes/{SLUG}/"]').count()==1;assert page.locator('a.lesson').count()==len(published_series);assert all(page.locator(f'a.lesson[href$="/episodes/{slug}/"]').count()==1 for slug in published_series);check('series includes all current published MQ lessons',w,{'slugs':published_series,'count':len(published_series)});snap(page,f'series-{w}')
    page.goto(base+f'/episodes/{SLUG}/',wait_until='domcontentloaded');assert page.locator('h1').inner_text()==meta['title'];assert meta['episodePart'] in page.locator('body').inner_text();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('episode identity and no overflow',w)
    for chapter in chapters:assert page.locator('[id="'+chapter['id']+'"]').count()==1
    check('current article chapter anchors remain unique',w,[c['id']for c in chapters])
    v=page.locator('video');v.scroll_into_view_if_needed();v.evaluate("async v=>{v.muted=true;v.preload='auto';const p=new Image();p.src=v.poster;await p.decode();v.load()}");page.wait_for_function('document.querySelector("video").readyState>=2');assert abs(v.evaluate('(v)=>v.duration')-total/30)<.002;check('metadata duration and poster decode',w);snap(page,f'poster-{w}')
    native_default=v.evaluate('(v)=>Array.from(v.querySelectorAll("track")).some(t=>t.default)');assert not native_default;check('native subtitles default off avoids double burned captions',w,{'trackDefault':native_default});page.evaluate('()=>{const v=document.querySelector("video");for(const t of v.textTracks)t.mode="hidden"}');page.wait_for_function('document.querySelector("video").textTracks[0]?.cues?.length>0');assert v.evaluate('(v)=>v.textTracks[0].cues.length')==len(json.loads((D/'voice/build.json').read_text())['sentences']);check('native VTT loaded',w,v.evaluate('(v)=>v.textTracks[0].cues.length'));page.evaluate('''()=>{const v=document.querySelector('video'),d=Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype,'currentTime');window.__qaAssigned=[];Object.defineProperty(v,'currentTime',{configurable:true,get(){return d.get.call(this)},set(t){window.__qaAssigned.push(t);return d.set.call(this,t)}})}''')
    v.evaluate('(v)=>v.play()');page.wait_for_function('!document.querySelector("video").paused&&document.querySelector("video").currentTime>.2');v.evaluate('(v)=>v.pause()');check('actual playback advance and pause',w)
    def exact(n,tag,screenshot=False):
     target=float((pts[n]+(pts[n+1]if n+1<len(pts)else pts[n]+Fraction(1,30)))/2);v.scroll_into_view_if_needed();r=page.evaluate(SEEK,{'time':target,'pts':float(pts[n])});assert r['paused']and not r['seeking']and abs(r['mediaTime']-float(pts[n]))<.0000011
     if n>=body:assert r['activeCues']==0
     f=OUT/f'decoded-{w}-{tag}-f{n}.png';f.write_bytes(base64.b64decode(r.pop('png').split(',',1)[1]));report['exactFrames'].append({'width':w,'frame':n,'pts':str(pts[n]),'decoded':r,'file':f.name,'sha256':sha(f)})
     if screenshot:snap(page,f'player-{w}-{tag}')
    sample_frames=[(0,'first'),(body-1,'last-body'),(body,'first-reference'),(body+75,'mid-reference'),(total-1,'last-reference')]
    page_frames=receipt['appendix']['framesPerPage']
    for reference_page in range(1,len(receipt['appendix']['pages'])):
     first=body+reference_page*page_frames
     sample_frames.extend([(first,f'reference-page-{reference_page+1}-first'),(first+page_frames//2,f'reference-page-{reference_page+1}-mid')])
    for n,tag in sample_frames:exact(n,tag,'reference' in tag)
    selector='.ch'if w>767 else '.chip'
    for i,c in enumerate(chapters):
     link=page.locator(f'{selector}[data-index="{i}"]');link.scroll_into_view_if_needed();page.evaluate('window.__qaAssigned=[]');link.click();page.wait_for_function('window.__qaAssigned.length>0');assert page.evaluate('window.__qaAssigned[0]')==c['start'];page.wait_for_function('!document.querySelector("video").paused');v.evaluate('(v)=>v.pause()');assert abs(v.evaluate('(v)=>v.currentTime')-c['start'])<1.0;check('chapter click seeks and starts playback',w,c)
    figures=page.locator('figure [data-seek-time]');assert figures.count()>=1
    for i in range(figures.count()):
     fig=figures.nth(i);t=float(fig.get_attribute('data-seek-time'));img=fig.locator('xpath=ancestor::figure').locator('img');img.evaluate('(e)=>e.loading="eager"');img.evaluate('(e)=>e.decode()');assert img.evaluate('(e)=>e.naturalWidth>0');fig.scroll_into_view_if_needed();page.evaluate('window.__qaAssigned=[]');fig.click();page.wait_for_function('window.__qaAssigned.length>0');assert page.evaluate('window.__qaAssigned[0]')==t;page.wait_for_function('!document.querySelector("video").paused');v.evaluate('(v)=>v.pause()');assert abs(v.evaluate('(v)=>v.currentTime')-t)<1.0;check('Figure image decode and replay click',w,{'index':i,'seconds':t});exact(round(t*30),f'figure-{i}')
    triggers=page.locator('[data-source-trigger]');assert triggers.count()>=1;page.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
    for i in range(triggers.count()):
     tr=triggers.nth(i);sid=tr.get_attribute('data-source-trigger');panel=page.locator(f'[data-source-panel="{sid}"]');tr.scroll_into_view_if_needed()
     if w>767 and i==0:tr.hover();page.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);assert panel.get_attribute('data-source-state')=='preview';tr.click();assert panel.get_attribute('data-source-state')=='pinned';check('desktop quote hover and click pin',w,sid)
     elif w<600:tr.tap()
     else:tr.click()
     page.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);assert ' '.join(panel.locator('blockquote').inner_text().split())==' '.join(sources[sid]['quotation']['text'].split());assert panel.locator('cite a').inner_text()==sources[sid]['title'];rect=panel.bounding_box();assert rect and rect['x']>=0 and rect['x']+rect['width']<=w+1 and rect['y']>=0 and rect['y']+rect['height']<=h+1;check('actual quote text and viewport',w,{'id':sid,'bounds':rect});snap(page,f'quote-{sid}-{w}');panel.locator('.source-close').click();page.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid)
    tr=triggers.first;sid=tr.get_attribute('data-source-trigger');tr.scroll_into_view_if_needed();page.mouse.move(0,0);tr.focus();page.keyboard.press('Enter');page.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);page.keyboard.press('Escape');page.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=sid);check('quote keyboard Enter Escape',w)
    v.scroll_into_view_if_needed();exact(body+75,'fullscreen-reference');page.evaluate('()=>{const b=document.createElement("button");b.id="qa-fs";b.textContent="Fullscreen QA";Object.assign(b.style,{position:"fixed",top:"0",left:"0",zIndex:999999});b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.append(b)}');page.locator('#qa-fs').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');snap(page,f'fullscreen-reference-{w}')
    if w<600:
     page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(350);snap(page,'fullscreen-reference-mobile-landscape-844');check('mobile landscape Fullscreen API reference view',844,{'initialContextWidth':w,'actualViewport':page.viewport_size})
    page.evaluate('document.exitFullscreen()');page.wait_for_function('document.fullscreenElement===null');page.locator('#qa-fs').evaluate('(e)=>e.remove()');check('Fullscreen API enter/exit actual reference card',w)
    if w<600:page.set_viewport_size({'width':w,'height':h})
    for theme in ['light','dark']:
     page.evaluate('(t)=>{document.documentElement.dataset.theme=t}',theme);assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('theme article no horizontal overflow',w,theme)
    # Exercise the unmodified same-tab original-image link after the media checks.
    original_links=page.locator('figure .fig-image-link')
    assert original_links.count()==figures.count()
    original_link=original_links.first;original_url=original_link.get_attribute('href');expected_original=urljoin(page.url,original_url);original_link.scroll_into_view_if_needed()
    with page.expect_navigation(wait_until='domcontentloaded'):original_link.click()
    assert page.url==expected_original
    page.wait_for_function('document.images.length>0&&document.images[0].complete&&document.images[0].naturalWidth>0')
    check('original Figure image link opens actual decoded image',w,{'url':page.url})
    snap(page,f'original-image-{w}')
    ctx.close()
   browser.close()
  assert not report['errors'];report['pass']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if server:server.shutdown();server.server_close()
 print(json.dumps({'pass':report['pass'],'checks':len(report['checks']),'exactFrames':len(report['exactFrames']),'output':str(OUT)}))
if __name__=='__main__':main()
