#!/usr/bin/env python3
"""Bounded peak-series cover-only site QA. Writes work evidence, never repository files."""
from pathlib import Path
import argparse, datetime, functools, hashlib, http.server, json, re, subprocess, threading, traceback
from playwright.sync_api import sync_playwright
R=Path('/workspace/video-studio'); W=Path('/workspace/work/peak-site-qa'); BASELINE='d3c163eff2a550255e8c81c1eea631178b7aaa58'
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

SLUGS=['rate-limit','idempotency','circuit-breaker','degradation']
TITLE='高并发、高可用、高性能'
def main(args):
 W.mkdir(parents=True,exist_ok=True)
 version=json.loads((R/'site/package.json').read_text())['version'];assert version==args.version,(version,args.version)
 metas={s:json.loads((R/'episodes'/s/'meta.json').read_text()) for s in SLUGS}
 assert [(metas[s]['series'],metas[s]['ep']) for s in SLUGS]==[('peak',n) for n in [11,12,13,14]]
 render=json.loads(args.render_report.read_text());assert render['passed']
 assert {i['slug'] for i in render['images']}==set(SLUGS) and len(render['images'])==12
 expected={s:next(i for i in render['images'] if i['slug']==s and i['size']=='16x9')['jpgSha256'] for s in SLUGS}
 static=[]
 for slug,names in [(s,['meta.json','video.mp4','script.md','article.mdx','storyboard.json']) for s in SLUGS]+[(s,['meta.json','video.mp4']) for s in ['db-index','message-queue','redis-skiplist','number-of-provinces']]:
  for name in names:
   rel=f'episodes/{slug}/{name}';expected_old=hashlib.sha256(git_bytes(rel)).hexdigest();assert sha(R/rel)==expected_old,rel
   static.append({'path':rel,'baselineSha256':expected_old,'currentSha256':sha(R/rel),'byteIdentical':True})
 for s in SLUGS:
  for rel in [f'episodes/{s}/cover-16x9.jpg',f'site/dist/episodes/{s}/cover-16x9.jpg']:assert sha(R/rel)==expected[s],rel
  assert sha(R/f'site/dist/episodes/{s}/video.mp4')==sha(R/f'episodes/{s}/video.mp4')
 report={'schemaVersion':1,'startedAt':now(),'baseline':BASELINE,'headAtExecution':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'version':version,'scope':'Four peak-series cover-only bounded local UI checks on fresh built site. No media remake, model, full listening, ASR, article replay audit or exact decoded-frame claim.','viewports':[[1440,1000],[390,844]],'renderReport':str(args.render_report),'renderReportSha256':sha(args.render_report),'expectedCoverSha256':expected,'staticProtectedAssets':static,'checks':[],'screenshots':[],'errors':[],'passed':False,'limits':['Desktop Chromium with emulated mobile viewport, not physical phone.','Fullscreen API entered through temporary audit click, not native video control.','Mobile series thumbnails hidden by existing CSS; library thumbnails checked visible.','Native paused controls may overlap the lower poster region; actual screenshot review bounds conclusions.','No complete-media semantic listening, ASR, or audience-effect claim.']}
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
 def check(name,detail,width):report['checks'].append({'name':name,'width':width,'detail':detail,'passed':True})
 def screen(page,name):
  p=W/(name+'.png');page.screenshot(path=str(p));report['screenshots'].append({'file':p.name,'sha256':sha(p)})
 def no_overflow(page):assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['browserVersion']=browser.version
   for width,height in report['viewports']:
    context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=width<600,has_touch=width<600,reduced_motion='reduce');context.add_init_script("localStorage.setItem('vs:sticky-off','1')");page=context.new_page();page.set_default_timeout(20000);page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.goto(base+'/',wait_until='domcontentloaded');tile=page.locator('article.series-peak');assert tile.count()==1 and TITLE in tile.inner_text() and '4 篇视频与图文' in tile.inner_text();assert tile.locator('a.series-entry').get_attribute('href').endswith('/series/peak/');tile.scroll_into_view_if_needed();no_overflow(page);check('home direct four-video peak series entry',tile.inner_text(),width);screen(page,f'home-{width}')
    page.goto(base+'/learn/',wait_until='domcontentloaded');series=page.locator('section#peak');assert TITLE in series.locator('h2').inner_text();links=series.locator('ol.series-lessons a');assert links.count()==4;assert {Path(h.rstrip('/')).name for h in links.evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))')}==set(SLUGS);series.scroll_into_view_if_needed();no_overflow(page);check('series catalog direct four lessons without nested learning tracks',None,width);screen(page,f'learn-{width}')
    page.goto(base+'/series/peak/',wait_until='domcontentloaded');assert page.locator('h1').inner_text()==TITLE;lessons=page.locator('a.lesson');assert lessons.count()==4
    for s in SLUGS:
     lesson=page.locator(f'a.lesson[href$="/episodes/{s}/"]');assert metas[s]['title'] in lesson.inner_text();img=lesson.locator('img');img.evaluate('(e)=>{e.loading="eager";return e.decode()}');assert img.evaluate('(e)=>e.complete&&e.naturalWidth===1920');assert img.get_attribute('src').endswith(f'/episodes/{s}/cover-16x9.jpg')
    page.locator('.curriculum').scroll_into_view_if_needed();no_overflow(page);check('series four lessons and all new covers decoded; mobile thumb follows CSS',{'visibleCoverCount':sum(lessons.nth(i).locator('img').is_visible() for i in range(4))},width);screen(page,f'series-{width}')
    page.goto(base+'/library/?series=peak',wait_until='domcontentloaded');page.wait_for_function('document.querySelector("select[name=series]").value==="peak"');cards=page.locator('#library-grid li:not([hidden]) > a.card');assert cards.count()==4;assert {Path(h.rstrip("/")).name for h in cards.evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))')}==set(SLUGS)
    cover_http=[]
    for s in SLUGS:
     card=page.locator(f'#library-grid li:not([hidden]) > a.card[href$="/episodes/{s}/"]');assert card.get_attribute('data-series')=='peak';img=card.locator('img');img.evaluate('(e)=>{e.loading="eager";return e.decode()}');assert img.is_visible() and img.evaluate('(e)=>e.complete&&e.naturalWidth===1920');response=context.request.get(base+f'/episodes/{s}/cover-16x9.jpg');actual=hashlib.sha256(response.body()).hexdigest();assert response.status==200 and actual==expected[s];cover_http.append({'slug':s,'sha256':actual,'status':response.status})
    cards.first.scroll_into_view_if_needed();no_overflow(page);check('library filter four cards and exact four new cover HTTP SHA',cover_http,width);screen(page,f'library-{width}')
    for s in SLUGS:
     meta=metas[s];page.goto(base+f'/episodes/{s}/',wait_until='domcontentloaded');assert page.locator('h1').inner_text()==meta['title'];assert f'EP.{meta["ep"]:02d}' in page.locator('body').inner_text();video=page.locator('video');video.scroll_into_view_if_needed();poster=video.get_attribute('poster');assert poster.endswith(f'/episodes/{s}/cover-16x9.jpg');dims=page.evaluate('async()=>{const v=document.querySelector("video"),im=new Image();im.src=v.poster;await im.decode();return [im.naturalWidth,im.naturalHeight]}');assert dims==[1920,1080];assert page.locator('#course-directory nav a').count()==4;assert version in page.locator('footer').inner_text();no_overflow(page);check('episode original identity and new decoded poster '+s,{'poster':poster,'dimensions':dims},width);screen(page,f'poster-{s}-{width}')
     page.evaluate('()=>{const v=document.querySelector("video");v.muted=true;v.preload="auto";v.load()}');page.wait_for_function('document.querySelector("video").readyState>=2&&document.querySelector("video").videoWidth===1920');assert abs(video.evaluate('(v)=>v.duration')-meta['finalVideoFrames']/30)<.001;page.evaluate('document.querySelector("video").play()');page.wait_for_function('!document.querySelector("video").paused&&document.querySelector("video").currentTime>.25');page.evaluate('document.querySelector("video").pause()');assert video.evaluate('(v)=>v.paused');check('original media short normal play/pause '+s,{'duration':video.evaluate('(v)=>v.duration'),'pausedAt':video.evaluate('(v)=>v.currentTime')},width)
     if s=='rate-limit':
      page.evaluate('()=>{const b=document.createElement("button");b.id="qa-enter-fullscreen";b.textContent="Fullscreen API audit";Object.assign(b.style,{position:"fixed",top:"8px",left:"8px",zIndex:"999999"});b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.append(b)}');page.locator('#qa-enter-fullscreen').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');assert video.evaluate('(v)=>v.readyState>=2&&!v.seeking');screen(page,f'fullscreen-{width}');page.evaluate('document.exitFullscreen()');page.wait_for_function('document.fullscreenElement===null');page.evaluate('document.querySelector("#qa-enter-fullscreen").remove()');check('representative actual Fullscreen API enter/exit',{'slug':s,'nativeControlTested':False,'physicalDevice':False},width)
    context.close()
   browser.close()
  assert not report['errors'];report['passed']=True
 except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
 finally:
  report['finishedAt']=now();(W/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');server.shutdown();server.server_close()
 print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'screenshots':len(report['screenshots']),'staticProtectedAssets':len(static),'report':str(W/'report.json')}))
if __name__=='__main__':
 p=argparse.ArgumentParser(__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--version',required=True);p.add_argument('--render-report',type=Path,default=Path('/workspace/work/peak-cover-candidate/render-report.json'));a=p.parse_args()
 if not a.execute:print('Prepared only; await root successful build and installation gate.');raise SystemExit(0)
 main(a)
