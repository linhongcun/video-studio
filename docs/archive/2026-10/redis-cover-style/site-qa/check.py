#!/usr/bin/env python3
"""Bounded Redis cover-only site QA. Writes work evidence, never repository files."""
from pathlib import Path
import argparse, datetime, functools, hashlib, http.server, json, re, subprocess, threading, traceback
from playwright.sync_api import sync_playwright
R=Path('/workspace/video-studio'); W=Path('/workspace/work/redis-site-qa'); BASELINE='2b418a9da0155fb29357c186238ed78feab0b8ed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git_bytes(name):return subprocess.check_output(['git','show',f'{BASELINE}:{name}'],cwd=R)
class RangeHandler(http.server.SimpleHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass
 def translate_path(self,path):
  if path.startswith('/video-studio/'):path=path[len('/video-studio'):]
  return super().translate_path(path)
 def send_head(self):
  self.byte_range=None
  file=Path(self.translate_path(self.path))
  if file.is_file() and 'Range' in self.headers:
   match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
   if match:
    start=int(match[1]);end=min(int(match[2]) if match[2] else file.stat().st_size-1,file.stat().st_size-1)
    if start>=file.stat().st_size:self.send_error(416);return None
    f=file.open('rb');f.seek(start);self.byte_range=(start,end);self.send_response(206);self.send_header('Content-type',self.guess_type(str(file)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{file.stat().st_size}');self.send_header('Content-Length',str(end-start+1));self.end_headers();return f
  return super().send_head()
 def copyfile(self,source,output):
  try:
   if self.byte_range:
    left=self.byte_range[1]-self.byte_range[0]+1
    while left:
     data=source.read(min(65536,left))
     if not data:break
     output.write(data);left-=len(data)
   else:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass

def main(args):
 W.mkdir(exist_ok=True)
 version=json.loads((R/'site/package.json').read_text())['version'];assert version==args.version
 meta=json.loads((R/'episodes/redis-skiplist/meta.json').read_text());assert meta['series']=='redis' and meta['ep']==40
 assert (R/'episodes/redis-skiplist/meta.json').read_bytes()==git_bytes('episodes/redis-skiplist/meta.json')
 cover_report=json.loads(args.render_report.read_text());assert cover_report['passed']
 images=[i for i in cover_report['images'] if i['slug']=='redis-skiplist'];assert len(images)==3
 expected_cover=next(i for i in images if i['size']=='16x9')['jpgSha256']
 static=[]
 for name in ['meta.json','video.mp4','script.md','article.mdx','storyboard.json']:
  rel='episodes/redis-skiplist/'+name;p=R/rel;expected=hashlib.sha256(git_bytes(rel)).hexdigest();assert sha(p)==expected,rel
  static.append({'path':rel,'baselineSha256':expected,'currentSha256':sha(p),'byteIdentical':True})
 for slug in ['db-index','message-queue','two-sum']:
  for name in ['meta.json','video.mp4']:
   rel=f'episodes/{slug}/{name}';p=R/rel;expected=hashlib.sha256(git_bytes(rel)).hexdigest();assert sha(p)==expected,rel
   static.append({'path':rel,'baselineSha256':expected,'currentSha256':sha(p),'byteIdentical':True})
 for rel,expected in [('episodes/redis-skiplist/cover-16x9.jpg',expected_cover),('site/dist/episodes/redis-skiplist/cover-16x9.jpg',expected_cover)]:assert sha(R/rel)==expected,rel
 assert sha(R/'site/dist/episodes/redis-skiplist/video.mp4')==sha(R/'episodes/redis-skiplist/video.mp4')
 report={'schemaVersion':1,'startedAt':now(),'baseline':BASELINE,'headAtExecution':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'version':version,'scope':'Redis cover-only bounded local UI checks on fresh built site; no voice/model/article replay audit or exact decoded-frame identity claim.','viewports':[[1440,1000],[390,844]],'renderReport':str(args.render_report),'renderReportSha256':sha(args.render_report),'expectedCoverSha256':expected_cover,'staticProtectedAssets':static,'checks':[],'screenshots':[],'errors':[],'passed':False,'limits':['Desktop Chromium with emulated mobile viewport, not physical phone.','Fullscreen API entered through temporary audit click, not native video control.','No complete-media semantic listening, ASR, or audience-effect claim.']}
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 def check(name,detail,width):report['checks'].append({'name':name,'width':width,'detail':detail,'passed':True})
 def screen(page,name):
  p=W/(name+'.png');page.screenshot(path=str(p));report['screenshots'].append({'file':p.name,'sha256':sha(p)})
 try:
  with sync_playwright() as pw:
   b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['browserVersion']=b.version
   for width,height in report['viewports']:
    context=b.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=width<600,has_touch=width<600,reduced_motion='reduce');context.add_init_script("localStorage.setItem('vs:sticky-off','1')");page=context.new_page();page.set_default_timeout(20000);page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.goto(base+'/',wait_until='domcontentloaded');tile=page.locator('a.track-redis');assert tile.count()==1 and 'Redis' in tile.inner_text() and '1 篇' in tile.inner_text() and tile.get_attribute('href').endswith('/learn/#redis');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('home independent Redis1 direction',tile.inner_text(),width);tile.scroll_into_view_if_needed();screen(page,f'home-{width}')
    page.goto(base+'/learn/',wait_until='domcontentloaded');track=page.locator('section#redis');assert 'Redis' in track.locator('h2').inner_text() and track.locator('.chapter-lessons a').count()==1 and track.locator('.chapter-lessons a').first.get_attribute('href').endswith('/episodes/redis-skiplist/');track.scroll_into_view_if_needed();check('learn independent Redis only current episode',None,width);screen(page,f'learn-{width}')
    page.goto(base+'/series/redis/',wait_until='domcontentloaded');assert 'Redis' in page.locator('h1').inner_text() and page.locator('a.lesson').count()==1;img=page.locator('.lesson-cover img');img.evaluate('(e)=>{e.loading="eager";return e.decode()}');assert img.evaluate('(e)=>e.naturalWidth===1920');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('series one lesson,new cover decoded; mobile thumb follows CSS',{'coverVisible':img.is_visible(),'coverSrc':img.get_attribute('src')},width);screen(page,f'series-{width}')
    page.goto(base+'/library/?series=redis',wait_until='domcontentloaded');page.wait_for_function('document.querySelector("select[name=series]").value==="redis"');cards=page.locator('li:not([hidden]) > a.card');assert cards.count()==1 and cards.first.get_attribute('data-series')=='redis';img=cards.locator('img');img.evaluate('(e)=>{e.loading="eager";return e.decode()}');assert img.evaluate('(e)=>e.complete&&e.naturalWidth===1920');assert img.is_visible();response=context.request.get(base+'/episodes/redis-skiplist/cover-16x9.jpg');assert response.status==200 and hashlib.sha256(response.body()).hexdigest()==expected_cover;check('library Redis filter1 and exact new cover response',{'coverSha256':expected_cover},width);cards.first.scroll_into_view_if_needed();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');screen(page,f'library-{width}')
    page.goto(base+'/episodes/redis-skiplist/',wait_until='domcontentloaded');assert page.locator('h1').inner_text()==meta['title'];assert 'EP.40' in page.locator('body').inner_text();video=page.locator('video');video.scroll_into_view_if_needed();poster=video.get_attribute('poster');assert poster.endswith('/episodes/redis-skiplist/cover-16x9.jpg');page.evaluate('''async()=>{const v=document.querySelector('video'),im=new Image();im.src=v.poster;await im.decode();return [im.naturalWidth,im.naturalHeight]}''');assert page.locator('#course-directory nav a').count()==1;assert version in page.locator('footer').inner_text();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('episode current EP40,poster exact path,one course,new footer',{'poster':poster},width);screen(page,f'poster-{width}')
    page.evaluate('''()=>{const v=document.querySelector('video');v.muted=true;v.preload='auto';v.load()}''');page.wait_for_function('document.querySelector("video").readyState>=2&&document.querySelector("video").videoWidth===1920');assert abs(video.evaluate('(v)=>v.duration')-meta['finalVideoFrames']/30)<.001;page.evaluate('document.querySelector("video").play()');page.wait_for_function('!document.querySelector("video").paused&&document.querySelector("video").currentTime>.25');page.evaluate('document.querySelector("video").pause()');assert video.evaluate('(v)=>v.paused');check('normal video load,short actualplay andpause',{'duration':video.evaluate('(v)=>v.duration'),'pausedAt':video.evaluate('(v)=>v.currentTime')},width);screen(page,f'paused-{width}')
    page.evaluate('''()=>{const b=document.createElement('button');b.id='qa-enter-fullscreen';b.textContent='Fullscreen API audit';Object.assign(b.style,{position:'fixed',top:'8px',left:'8px',zIndex:'999999'});b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b)}''');page.locator('#qa-enter-fullscreen').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');assert video.evaluate('(v)=>v.readyState>=2&&!v.seeking');screen(page,f'fullscreen-{width}');page.evaluate('document.exitFullscreen()');page.wait_for_function('document.fullscreenElement===null');page.evaluate('document.querySelector("#qa-enter-fullscreen").remove()');check('actual Fullscreen API enter/exit',{'nativeControlTested':False,'physicalDevice':False},width)
    context.close()
   b.close()
  assert not report['errors'];report['passed']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAt']=now();(W/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');server.shutdown();server.server_close()
 print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'screenshots':len(report['screenshots']),'staticProtectedAssets':len(static),'report':str(W/'report.json')}))
if __name__=='__main__':
 p=argparse.ArgumentParser(__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--version',default='0.85.2');p.add_argument('--render-report',type=Path,default=Path('/workspace/work/redis-cover-candidate/render-report.json'));a=p.parse_args()
 if not a.execute:print('Prepared only; await root successful build and installation gate.');raise SystemExit(0)
 main(a)
