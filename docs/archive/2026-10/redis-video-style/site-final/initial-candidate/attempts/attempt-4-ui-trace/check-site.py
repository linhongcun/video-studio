"""Read-only exact-candidate Redis UI and complete local HTTP media validation."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin, quote
from html.parser import HTMLParser
import argparse,atexit,hashlib,json,re,subprocess,sys
from playwright.sync_api import sync_playwright
import helpers

p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--candidate',required=True);p.add_argument('--baseline',default='8d30ec3954297cc9aad6412c417ece8da4ceb9f7');p.add_argument('--base',default='http://127.0.0.1:4325/video-studio');p.add_argument('--out',required=True);args=p.parse_args()
root=Path(args.root);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);helpers.root=root
slug='redis-skiplist';directory=root/'episodes'/slug
meta=json.loads((directory/'meta.json').read_text());article=helpers.article_data((directory/'article.mdx').read_text());receipt=json.loads((directory/'reference-appendix.json').read_text());result=json.loads((directory/'render-result.json').read_text())
report={'candidate':args.candidate,'baseline':args.baseline,'base':args.base,'startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),'scope':[slug],'browser':'Headless system Chromium, desktop and mobile viewport simulations','httpMedia':[],'views':[],'errors':[],'screenshots':[]}
atexit.register(lambda:(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'))
def ex(kind,value,tb):report['errors'].append(str(value));sys.__excepthook__(kind,value,tb)
sys.excepthook=ex
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==args.candidate
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip()
assert meta['series']=='redis' and meta['ep']==40 and meta['burnedInCaptions'] is True
assert meta['sourcePath']=='episodes-codex/redis-skiplist/revisions/height-choice/redis-skiplist/remotion'
assert meta['finalVideoFrames']==4707 and meta['referenceAppendix']['from']==4557
assert result['sha256']==receipt['outputSHA256']==helpers.sha_file(directory/'video.mp4')
assert (directory/'article.mdx').read_bytes()==subprocess.check_output(['git','show',args.baseline+':episodes/redis-skiplist/article.mdx'],cwd=root)
cover_blobs={}
for name in ['cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','cover-style.json']:
 now=helpers.git_blob(args.candidate,f'episodes/{slug}/{name}');before=helpers.git_blob(args.baseline,f'episodes/{slug}/{name}');assert now==before;cover_blobs[name]=now
report['preservedCoverGitBlobs']=cover_blobs
report['reusedCompleteHTTP']='All3 complete media HTTP responses from unchanged candidate/base in preserved attempt2; browser-only correction.'
for f in ['video.mp4',meta['poster'],'article/height-one.jpg']:
 prior=json.loads((Path(__file__).parent/'attempt-2-offscreen-source/report.json').read_text());assert prior['candidate']==args.candidate and prior['base']==args.base;r=next(x for x in prior['httpMedia'] if x['url']==f'{args.base}/episodes/{slug}/{f}');assert r['sha256']==helpers.sha_file(directory/f);report['httpMedia'].append(r)
packet_pts=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',str(directory/'video.mp4')],text=True));encoded_pts=sorted(float(v['pts_time']) for v in packet_pts['packets']);assert len(encoded_pts)==4707
report['seekPrecision']='Direct paused probes use actual encoded packet PTS rounded as stored by ffprobe; callback accepts only the exact requested frame index, never adjacent frames. UI click hash/time independently verified.'
assert article['figures']==[{'src':'/video-studio/episodes/redis-skiplist/article/height-one.jpg','seek':88.9}]
class TrackParser(HTMLParser):
 def __init__(self):super().__init__();self.tracks=[]
 def handle_starttag(self,tag,attrs):
  if tag=='track':self.tracks.append(dict(attrs))
tracks={}
for f in (root/'site/dist/episodes').glob('*/index.html'):
 parser=TrackParser();parser.feed(f.read_text());tracks[f.parent.name]=parser.tracks
assert len(tracks[slug])==1 and 'default' not in tracks[slug][0]
report['staticNativeTrack']=tracks[slug]
def snap(page,name):
 helpers.overflow(page);path=out/name;page.screenshot(path=str(path));report['screenshots'].append({'file':str(path),'sha256':helpers.sha_file(path)})
def seek(page,t):
 target=encoded_pts[round(float(t)*30)];state=helpers.seek_paused(page,target);assert round(state['presentedFrame']['mediaTime']*30)==round(target*30),(t,target,state);state['requestedSeconds']=t;state['targetFrame']=round(target*30);return state
UI_ARM="""()=>{const v=document.querySelector('video');v.pause();const trace={frames:[],events:[]};window.__qaUIClick=new Promise((resolve,reject)=>{let sought=false,paint=null,done=false;const timer=setTimeout(()=>{done=true;reject(new Error('UI seek paint timeout '+JSON.stringify({trace,time:v.currentTime})))},12000);const finish=()=>{if(done||!sought||!paint||Math.abs(paint.mediaTime-v.currentTime)>1/30+.00001)return;done=true;clearTimeout(timer);requestAnimationFrame(()=>requestAnimationFrame(()=>resolve({currentTime:v.currentTime,paused:v.paused,hash:location.hash,painted:paint,trace})))};const callback=(now,m)=>{paint={mediaTime:m.mediaTime,presentedFrames:m.presentedFrames};trace.frames.push({...paint,time:v.currentTime,afterSeeked:sought});finish();if(!done)v.requestVideoFrameCallback(callback)};v.requestVideoFrameCallback(callback);v.addEventListener('seeking',()=>trace.events.push({event:'seeking',time:v.currentTime}),{once:true});v.addEventListener('seeked',()=>{v.pause();sought=true;trace.events.push({event:'seeked',time:v.currentTime});finish()},{once:true})});return true}"""
def click_seek(page,link,t):
 seek(page,2 if t>5 else 10);page.evaluate(UI_ARM);link.click();trace=page.evaluate('()=>window.__qaUIClick');assert abs(trace['currentTime']-t)<.05,(t,trace);assert trace['hash']=='#t='+str(t).removesuffix('.0'),(t,trace);trace['requestedNominalSeconds']=t;trace['nominalExpectedFrame']=round(t*30);trace['paintedFrame']=round(trace['painted']['mediaTime']*30);trace['nominalClickPresentedExactFrame']=trace['nominalExpectedFrame']==trace['paintedFrame'];return trace

def theme(page,value):
 page.locator('.theme-trigger').click();page.locator(f'[data-theme-opt="{value}"]').click();assert page.locator('html').get_attribute('data-theme')==value

def taxonomy(page,width):
 data={}
 r=page.goto(args.base+'/series/redis/',wait_until='networkidle');assert r.status==200
 assert page.locator('h1').inner_text().strip()=='Redis 系列'
 entries=page.locator('ol.lesson-list a.lesson');assert entries.count()==1 and entries.first.get_attribute('href').endswith('/episodes/redis-skiplist/')
 assert entries.locator('.lesson-meta .num').inner_text().strip()=='EP.40';data['series']={'entries':1,'overflow':helpers.overflow(page)};snap(page,f'series-{width}.png')
 page.goto(args.base+'/learn/#redis',wait_until='networkidle');track=page.locator('section#redis');assert track.locator('h2').inner_text().strip()=='Redis 系列';assert track.locator('a.chapter-heading').get_attribute('href').endswith('/series/redis/');data['learn']={'overflow':helpers.overflow(page)}
 page.goto(args.base+'/library/?track=redis&series=redis',wait_until='networkidle');visible=page.locator('#library-grid > ul > li:not([hidden]) a.card');assert visible.count()==1 and visible.first.get_attribute('href').endswith('/episodes/redis-skiplist/');data['library']={'visible':1,'overflow':helpers.overflow(page)};snap(page,f'library-{width}.png')
 return data
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['chromiumVersion']=browser.version
 for width,height in [(1440,1000),(390,844)]:
  context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  row={'width':width,'height':height,'taxonomy':taxonomy(page,width)};report['views'].append(row)
  r=page.goto(args.base+'/episodes/'+slug+'/',wait_until='networkidle');assert r.status==200
  assert page.locator('header.eh h1').inner_text().strip()==meta['title']
  bc=page.locator('nav[aria-label="面包屑"]');assert bc.get_by_role('link',name='Redis 系列',exact=True).count()==1
  assert page.locator('.episode-version time').get_attribute('datetime')==meta['updatedAt']
  source=page.locator('.source-links a').evaluate_all('(as)=>as.map(a=>a.href)');assert len(source)==3 and all(args.candidate in u for u in source);assert source[-1].endswith(quote(meta['sourcePath'],safe='/'));row['sourceLinks']=source
  assert page.locator('nav.pager a').count()==0
  links=helpers.links(page.locator('#course-directory nav a'));assert len(links)==1 and links[0].endswith('/episodes/redis-skiplist/')
  related=[]
  for href in helpers.links(page.locator('aside.rel a.rc')):
   response=page.request.get(urljoin(args.base+'/',href));assert response.status==200;related.append({'href':href,'status':200});response.dispose()
  row['related']=related
  video=page.locator('video');page.wait_for_function('()=>{const v=document.querySelector("video");return v&&v.readyState>=1&&v.textTracks.length===1}')
  vm=video.evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,trackDefault:v.querySelector("track").default,mode:v.textTracks[0].mode})');assert vm['width']==1920 and vm['height']==1080 and abs(vm['duration']-4707/30)<.034;assert vm['trackDefault'] is False and vm['mode']=='disabled';row['initialPlayer']=vm
  default=seek(page,2);assert not default['active'];row['bodyDefault']=default
  video.evaluate('(v)=>{v.muted=true;return v.play()}');page.wait_for_function('(t)=>!document.querySelector("video").paused&&document.querySelector("video").currentTime>t+.2',arg=2);page.keyboard.press('k');page.wait_for_function('document.querySelector("video").paused');row['playbackKeyboardPause']=True
  seek(page,88.9);helpers.visible_video(page)
  page.evaluate('()=>{let b=document.createElement("button");b.id="qa-fullscreen";b.style="position:fixed;left:0;top:0;z-index:99999";b.textContent="Fullscreen QA";b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.appendChild(b)}');page.locator('#qa-fullscreen').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');seek(page,88.9);snap(page,f'height-one-fullscreen-{width}.png');page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.locator('#qa-fullscreen').evaluate('(b)=>b.remove()');row['fullscreen']={'entered':True,'exited':True,'nativeTrackMode':'disabled'}
  chapters=json.loads(page.locator('#player').get_attribute('data-chapters'));assert [c['id'] for c in chapters]==['goal','search','insert','boundary'];assert [(c['id'],c['title']) for c in chapters]==[(c['id'],c['title']) for c in article['frontmatter']['chapters']]
  row['chapterSeeks']=[];row['articleChapterSeeks']=[]
  for i,c in enumerate(chapters):
   selector='.vp .side a.ch' if width>=768 else '.vp .chips a.chip';link=page.locator(selector+f'[data-index="{i}"]');trace=click_seek(page,link,c['start']);state=seek(page,c['start']);row['chapterSeeks'].append({**c,'uiClick':trace,'exactPacketPTSProbe':state})
   button=page.locator('article.article-body [data-seek="'+c['id']+'"]');assert button.count()==1;trace=click_seek(page,button,c['start']);row['articleChapterSeeks'].append({'id':c['id'],'uiClick':trace,'exactPacketPTSProbe':seek(page,c['start'])})
  for h in article['headings']:assert page.locator('article.article-body [id="'+h['id']+'"]').count()==1
  row['articleAnchors']=[h['id'] for h in article['headings']]
  row['themes']=[]
  for appearance in ['light','dark']:
   theme(page,appearance);figure=page.locator('figure.fig').filter(has=page.locator('img[src$="/article/height-one.jpg"]'));figure.scroll_into_view_if_needed();figure.locator('img').evaluate('async i=>{await i.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}');snap(page,f'figure-{appearance}-{width}.png')
   trace=click_seek(page,figure.locator('[data-seek-time]'),88.9);state=seek(page,88.9);assert page.evaluate('location.hash')=='#t=88.9'
   row['themes'].append({'appearance':appearance,'figureUIClick':trace,'exactPacketPTSProbe':state,'overflow':helpers.overflow(page)})
  row['sourceQuotes']=[]
  for i in range(page.locator('[data-source-trigger]').count()):
   trigger=page.locator('[data-source-trigger]').nth(i);ident=trigger.get_attribute('data-source-trigger');trigger.scroll_into_view_if_needed();page.mouse.move(0,0);page.wait_for_timeout(120);trigger.focus();page.keyboard.press('Enter');panel=page.locator('[data-source-panel="'+ident+'"]');panel.wait_for(state='visible');assert panel.locator('blockquote').inner_text().strip();identity=panel.locator('.source-identity').inner_text();snap(page,f'source-{i+1}-{width}.png');page.keyboard.press('Escape');panel.wait_for(state='hidden');row['sourceQuotes'].append({'sourceId':ident,'keyboardOpened':True,'escapedClosed':True,'identity':identity})
  video.evaluate('(v)=>v.textTracks[0].mode="showing"');page.wait_for_function('document.querySelector("video").textTracks[0].cues?.length>0')
  cues=video.evaluate('(v)=>[...v.textTracks[0].cues].map(c=>({start:c.startTime,end:c.endTime,text:c.text}))');assert len(cues)==20 and cues[-1]['end']<=4557/30
  t=(cues[0]['start']+cues[0]['end'])/2;active=seek(page,t);assert active['active']==[cues[0]['text']]
  refs=seek(page,4557/30+2.5);assert not refs['active'];snap(page,f'references-{width}.png');restored=seek(page,t);assert restored['active']==active['active'];video.evaluate('(v)=>v.textTracks[0].mode="disabled"');disabled=seek(page,t);assert not disabled['active']
  row['nativeCaptions']={'cueCount':len(cues),'lastEnd':cues[-1]['end'],'explicitEnabled':active,'referencesEmpty':refs,'restored':restored,'explicitDisabled':disabled}
  row['overflow']=helpers.overflow(page);row['errors']=errors;assert not errors;context.close();print(json.dumps({'width':width,'status':'passed'}),flush=True)
 browser.close()
report['status']='passed';report['finishedAt']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds');report['limits']=['Local complete HTTP hashes, not canonical online bytes.','Viewport simulation and Fullscreen API, not physical mobile devices or native menu manual testing.','No full-film hearing, ASR, or learning-effect validation.']
print('Redis final site QA passed',flush=True)
