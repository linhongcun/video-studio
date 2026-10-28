#!/usr/bin/env python3
"""Bounded local UI acceptance for rebuilt Kafka MQ01. Work files only."""
from pathlib import Path
from fractions import Fraction
import argparse,base64,datetime,functools,hashlib,http.server,json,re,subprocess,threading,time,traceback
from playwright.sync_api import sync_playwright
R=Path('/workspace/video-studio');W=Path('/workspace/work/mq-site-qa');EXPECTED=json.loads((W/'expected.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
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
                start=int(match[1]);end=int(match[2]) if match[2] else file.stat().st_size-1
                end=min(end,file.stat().st_size-1)
                if start>=file.stat().st_size:self.send_error(416);return None
                f=file.open('rb');f.seek(start);self.byte_range=(start,end)
                self.send_response(206);self.send_header('Content-type',self.guess_type(str(file)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{file.stat().st_size}');self.send_header('Content-Length',str(end-start+1));self.end_headers();return f
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

def setup_media(expected_video_sha):
    meta=json.loads((R/'episodes/message-queue/meta.json').read_text())
    for key,value in EXPECTED['preservedIdentity'].items():assert meta[key]==value,('preserved identity mismatch',key)
    assert meta['sourcePath']==EXPECTED['expectedSourcePath'] and meta['episodePart']==EXPECTED['expectedEpisodePart']
    assert meta['finalVideoFrames']==EXPECTED['expectedFinalFrames']
    assert meta['referenceAppendix']['from']==EXPECTED['expectedBodyFrames'] and meta['referenceAppendix']['durationInFrames']==150
    new=R/Path(meta['sourcePath']).parent
    video=R/'episodes/message-queue/video.mp4';built=R/'site/dist/episodes/message-queue/video.mp4'
    assert sha(video)==expected_video_sha==sha(built)==sha(new/'video.mp4'),'Media source/publication/build gate mismatch'
    poster=R/'episodes/message-queue/cover-16x9.jpg';assert sha(poster)==sha(R/'site/dist/episodes/message-queue/cover-16x9.jpg')
    sb=json.loads((new/'storyboard.json').read_text());assert sum(s['durationInFrames'] for s in sb['scenes'])==3697
    chapters=[{'id':s['chapterId'],'start':s['from']/30,'sourceFrame':s['from']} for s in sb['scenes']]
    assert [x['id'] for x in chapters]==EXPECTED['chapterIds']
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_frames','-show_entries','stream=time_base,nb_frames,width,height,avg_frame_rate:frame=best_effort_timestamp','-of','json',str(video)],text=True))
    stream=probe['streams'][0];tb=Fraction(stream['time_base']);pts=[Fraction(f['best_effort_timestamp'])*tb for f in probe['frames']]
    assert len(pts)==3847 and len(set(pts))==3847 and pts==sorted(pts)
    assert stream['width']==1920 and stream['height']==1080 and Fraction(stream['avg_frame_rate'])==30
    vtt=(R/'site/dist/episodes/message-queue/captions.vtt').read_text()
    stamps=re.findall(r'(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})',vtt)
    seconds=lambda x:sum(float(v)*m for v,m in zip(x.split(':'),[3600,60,1]))
    cues=[{'start':seconds(a),'end':seconds(b)} for a,b in stamps];assert len(cues)==24 and all(c['end']<=float(pts[3697]) for c in cues)
    sources={}
    for name in ['references.json','article-sources.json']:
        for source in json.loads((R/'episodes/message-queue'/name).read_text())['sources']:sources[source['id']]=source
    return meta,pts,chapters,cues,sources,{'videoSha256':expected_video_sha,'posterSha256':sha(poster),'frames':len(pts),'timeBase':str(tb),'fps':30,'vttCues':len(cues),'lastCueEnd':max(c['end'] for c in cues),'referenceStartPts':float(pts[3697]),'chapters':chapters,'preservedIdentityMatched':True}

SEEK_JS=r'''async({targetTime,expectedPts})=>{
 const v=document.querySelector('video');v.pause();
 if(!v.requestVideoFrameCallback)throw Error('requestVideoFrameCallback unavailable');
 return await new Promise((resolve,reject)=>{
  let metadata=null,seeked=false,callbackId=null;
  const limit=setTimeout(()=>{if(callbackId)v.cancelVideoFrameCallback(callbackId);reject(Error('exact frame decode timed out at '+targetTime+' expected '+expectedPts));},15000);
  const finish=()=>{if(!seeked||!metadata)return;clearTimeout(limit);const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);resolve({requestedTime:targetTime,mediaTime:metadata.mediaTime,presentedFrames:metadata.presentedFrames,currentTime:v.currentTime,readyState:v.readyState,paused:v.paused,seeking:v.seeking,width:v.videoWidth,height:v.videoHeight,activeCueCount:v.textTracks[0]?.activeCues?.length??null,canvasPng:c.toDataURL('image/png')});};
  const next=(at,md)=>{if(Math.abs(md.mediaTime-expectedPts)<=0.0000011){metadata=md;finish();}else callbackId=v.requestVideoFrameCallback(next);};
  callbackId=v.requestVideoFrameCallback(next);
  v.addEventListener('seeked',()=>{seeked=true;finish();},{once:true});
  v.currentTime=targetTime;
 });
}'''
def run(expected_video_sha):
    meta,pts,chapters,cues,sources,static=setup_media(expected_video_sha)
    report={'schemaVersion':1,'startedAt':now(),'scope':'Local builtsite MQ01integration only; existing sticky-off preference enabled in ephemeral test context to keep bounded media/article checks independent of unchanged sticky behavior. Player/sourcequote implementation unchanged; physical device and native full-screen control UI not claimed.','static':static,'checks':[],'mediaFrames':[],'screenshots':[],'errors':[],'passed':False,'pixelFrameIdentity':'Exact ffprobe PTS matched against requestVideoFrameCallback mediaTime within1.1microseconds serialization precision; no adjacent-frame tolerance. Snapshot seek targets center of exact requested frame interval, separately recording actual UIcurrentTime assignments for Figure andchapter interactions.'}
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(RangeHandler,directory=str(R/'site/dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/video-studio'
    def check(name,detail=None,width=None):report['checks'].append({'name':name,'width':width,'passed':True,'detail':detail})
    def screenshot(page,name):
        path=W/(name+'.png');page.screenshot(path=str(path),full_page=False);report['screenshots'].append({'file':path.name,'sha256':sha(path)});return path
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['browserVersion']=browser.version
            for width,height in EXPECTED['viewports']:
                context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=width<600,has_touch=width<600,reduced_motion='reduce')
                context.add_init_script("localStorage.setItem('vs:sticky-off','1')");page=context.new_page();page.set_default_timeout(20000);page.on('pageerror',lambda error:report['errors'].append(str(error)))
                page.goto(base+'/',wait_until='domcontentloaded');tile=page.locator('a.track-message-queue');assert tile.count()==1 and 'Kafka' in tile.inner_text() and tile.get_attribute('href').endswith('/learn/#message-queue');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('homepage Kafka direction andstableID',tile.inner_text(),width)
                tile.scroll_into_view_if_needed();screenshot(page,f'home-direction-{width}')
                page.goto(base+'/learn/#message-queue',wait_until='domcontentloaded');track=page.locator('section#message-queue');assert 'Kafka' in track.inner_text();assert track.locator('.chapter-lessons a').count()==1;assert track.locator('.chapter-lessons a').first.get_attribute('href').endswith('/episodes/message-queue/');check('learn independent direction only1published lesson',None,width);track.scroll_into_view_if_needed();screenshot(page,f'learn-direction-{width}')
                page.goto(base+'/library/?series=message-queue',wait_until='domcontentloaded');page.wait_for_function('document.querySelector("select[name=series]").value==="message-queue"');cards=page.locator('li:not([hidden]) > a.card');assert cards.count()==1 and cards.first.get_attribute('data-series')=='message-queue';img=cards.locator('img');img.evaluate('(e)=>e.loading="eager"');img.evaluate('(e)=>e.decode()');assert img.evaluate('(e)=>e.complete&&e.naturalWidth===1920');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('library MQ filter1andnewcover decoded',img.get_attribute('src'),width);cards.first.scroll_into_view_if_needed();screenshot(page,f'library-{width}')
                page.goto(base+'/series/message-queue/',wait_until='domcontentloaded');assert 'Kafka' in page.locator('h1').inner_text();assert page.locator('a.lesson').count()==1;assert '独立观看' in page.locator('.series-overview').inner_text();series_img=page.locator('.lesson-cover img');series_img.evaluate('(e)=>e.loading="eager"');series_img.evaluate('(e)=>e.decode()');check('series title,1lesson,independent reading',{'coverDecoded':series_img.evaluate('(e)=>e.naturalWidth===1920'),'coverVisible':series_img.is_visible()},width);screenshot(page,f'series-{width}')
                page.goto(base+'/episodes/message-queue/',wait_until='domcontentloaded');assert page.locator('h1').inner_text()==meta['title'];body=page.locator('body').inner_text();assert 'EP.10' in body and meta['episodePart'] in body;assert page.locator('nav.pager').count()==0;assert page.locator('#course-directory nav a').count()==1;check('episode EP10, MQ01andno cross-series pager',None,width)
                platform_actual=page.locator('nav.pl a').evaluate_all('(els)=>els.map(e=>e.href)');assert set(platform_actual)==set(meta['platforms'].values());check('original platformlinks preserved',platform_actual,width)
                production_links=page.locator('nav.source-links a').evaluate_all('(els)=>els.map(e=>e.href)');assert any('kafka-intro/message-queue/' in link for link in production_links);check('current production source links',production_links,width)
                video=page.locator('video');video.scroll_into_view_if_needed();page.evaluate('''async()=>{const v=document.querySelector('video');v.muted=true;v.preload='auto';const p=new Image();p.src=v.poster;await p.decode();v.load();}''');page.wait_for_function('document.querySelector("video").readyState>=2&&document.querySelector("video").videoWidth===1920');assert abs(video.evaluate('(v)=>v.duration')-3847/30)<.001;check('video metadata loaded andposterdecoded',{'duration':video.evaluate('(v)=>v.duration'),'readyState':video.evaluate('(v)=>v.readyState')},width);screenshot(page,f'poster-{width}')
                page.evaluate('''()=>{const v=document.querySelector('video'),d=Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype,'currentTime');window.__qaAssignedTimes=[];Object.defineProperty(v,'currentTime',{configurable:true,get(){return d.get.call(this)},set(t){window.__qaAssignedTimes.push(t);return d.set.call(this,t)}});for(const t of v.textTracks)t.mode='hidden';}''')
                page.wait_for_function('document.querySelector("video").textTracks[0]?.cues?.length===24');check('24loaded VTT cues',None,width)
                page.evaluate('document.querySelector("video").play()');page.wait_for_function('!document.querySelector("video").paused&&document.querySelector("video").currentTime>.2');page.evaluate('document.querySelector("video").pause()');assert video.evaluate('(v)=>v.paused');check('actualplay advanced andpause held',video.evaluate('(v)=>v.currentTime'),width)
                async_source=None
                def strict_frame(frame,tag,save_page=False):
                    expected_pts=float(pts[frame]);next_pts=float(pts[frame+1]) if frame+1<len(pts) else expected_pts+1/30;target=(expected_pts+next_pts)/2
                    video.scroll_into_view_if_needed();result=page.evaluate(SEEK_JS,{'targetTime':target,'expectedPts':expected_pts});assert abs(result['mediaTime']-expected_pts)<=.0000011;assert result['readyState']>=2 and result['paused'] and not result['seeking'];png=result.pop('canvasPng');dest=W/f'media-{width}-{tag}-f{frame}.png';dest.write_bytes(base64.b64decode(png.split(',',1)[1]));entry={'width':width,'tag':tag,'expectedFrameIndex':frame,'expectedPts':str(pts[frame]),'decodedMediaTime':result['mediaTime'],'exactFrameMatched':True,'file':dest.name,'sha256':sha(dest),'state':result};report['mediaFrames'].append(entry)
                    if frame>=3697:assert result['activeCueCount']==0
                    if save_page:screenshot(page,f'player-{width}-{tag}-f{frame}')
                    return entry
                for i,t in enumerate(EXPECTED['figureSeconds'],1):
                    link=page.locator(f'figure [data-seek-time="{t}"]');assert link.count()==1;figure=link.locator('xpath=ancestor::figure');picture=figure.locator('img');picture.evaluate('(e)=>e.loading="eager"');picture.evaluate('(e)=>e.decode()');assert picture.evaluate('(e)=>e.naturalWidth===1920');link.scroll_into_view_if_needed();page.evaluate('window.__qaAssignedTimes=[]');link.click();page.wait_for_function('window.__qaAssignedTimes.length>0');assigned=page.evaluate('window.__qaAssignedTimes[0]');assert assigned==t,('Figure assigned time mismatch',i,assigned,t);page.wait_for_function('!document.querySelector("video").paused');page.evaluate('document.querySelector("video").pause()');check('Figureclick seek exactassignment andimage decode',{'figure':i,'assignedTime':assigned,'href':link.get_attribute('href')},width);strict_frame(int(t*30),f'article{i}',True)
                chapter_data=json.loads(page.locator('.vp').get_attribute('data-chapters'));assert [c['id'] for c in chapter_data]==EXPECTED['chapterIds'];assert [c['start'] for c in chapter_data]==[c['start'] for c in chapters]
                selector='.ch' if width>767 else '.chip'
                for i,c in enumerate(chapters):
                    chapter=page.locator(f'{selector}[data-index="{i}"]');chapter.scroll_into_view_if_needed();page.evaluate('window.__qaAssignedTimes=[]');chapter.click();page.wait_for_function('window.__qaAssignedTimes.length>0');assert page.evaluate('window.__qaAssignedTimes[0]')==c['start'];page.wait_for_function(f'document.querySelector("{selector}[data-index=\\"{i}\\"]").getAttribute("aria-current")==="true"');page.evaluate('document.querySelector("video").pause()');check('chapterjump exactassignment',{'chapter':c['id'],'time':c['start']},width)
                for frame,tag in [(2303,'commit-before'),(2304,'commit-first1'),(3696,'last-body'),(3697,'first-reference'),(3772,'reference-mid'),(3846,'last-reference')]:strict_frame(frame,tag,frame in [2304,3697,3846])
                # Fullscreen API via a real temporary audit click, not a claim of
                # using native video control UI or a physical mobile device.
                page.evaluate('''()=>{const b=document.createElement('button');b.id='qa-enter-fullscreen';b.textContent='Fullscreen API audit';Object.assign(b.style,{position:'fixed',top:'8px',left:'8px',zIndex:'999999'});b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b)}''');page.locator('#qa-enter-fullscreen').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');assert video.evaluate('(v)=>v.readyState>=2&&!v.seeking');screenshot(page,f'fullscreen-api-{width}');page.evaluate('document.exitFullscreen()');page.wait_for_function('document.fullscreenElement===null');page.evaluate('document.querySelector("#qa-enter-fullscreen").remove()');check('Fullscreen API actualenter andexit',{'physicalDevice':False,'nativeControlClickTested':False},width)
                # All core new article quotes are verified in their actual panel.
                triggers=page.locator('[data-source-trigger]');assert triggers.count()==4;page.wait_for_function('Array.from(document.querySelectorAll("[data-source-quote]")).every(e=>e.dataset.sourceReady==="true")')
                for source_id in ['R3','R1','A1','R2']:
                    trigger=page.locator(f'[data-source-trigger="{source_id}"]');panel=page.locator(f'[data-source-panel="{source_id}"]');trigger.scroll_into_view_if_needed()
                    if width>767 and source_id=='R3':
                        trigger.hover();page.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=source_id);assert panel.get_attribute('data-source-state')=='preview';trigger.click();assert panel.get_attribute('data-source-state')=='pinned';check('desktophover preview thenpin',source_id,width)
                    elif width<600:trigger.tap()
                    else:trigger.click()
                    page.wait_for_function('(id)=>document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=source_id);assert ' '.join(panel.locator('blockquote').inner_text().split())==' '.join(sources[source_id]['quotation']['text'].split());assert panel.locator('cite a').inner_text()==sources[source_id]['title'];rect=panel.bounding_box();assert rect and rect['x']>=0 and rect['x']+rect['width']<=width+1 and rect['y']>=0 and rect['y']+rect['height']<=height+1;check('SourceQuote actual openoriginal andviewport',{'id':source_id,'title':sources[source_id]['title'],'method':'touch' if width<600 else 'click','bounds':rect},width)
                    if source_id=='A1':screenshot(page,f'sourcequote-A1-{width}')
                    panel.locator('.source-close').click();page.wait_for_function('(id)=>!document.querySelector(`[data-source-panel="${id}"]`).matches(":popover-open")',arg=source_id);assert trigger.get_attribute('aria-expanded')=='false'
                if width>767:
                    page.mouse.move(0,0);trigger=page.locator('[data-source-trigger="A1"]');trigger.scroll_into_view_if_needed();trigger.focus();page.keyboard.press('Enter');page.wait_for_function('document.querySelector("[data-source-panel=A1]").matches(":popover-open")');page.keyboard.press('Escape');page.wait_for_function('!document.querySelector("[data-source-panel=A1]").matches(":popover-open")');page.wait_for_function('document.activeElement===document.querySelector("[data-source-trigger=A1]")');assert trigger.evaluate('(e)=>document.activeElement===e');check('SourceQuote keyboardEnter Escape focusrestore',None,width)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');check('episode article nohorizontal overflow',None,width)
                context.close()
            browser.close()
        assert not report['errors'],report['errors'];report['passed']=True
    except Exception as e:report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()};raise
    finally:
        report['finishedAt']=now();(W/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');server.shutdown();server.server_close()
    print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'strictDecodedFrameChecks':len(report['mediaFrames']),'screenshots':len(report['screenshots']),'report':str(W/'report.json')},ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--expected-video-sha');args=parser.parse_args()
    if not args.execute:print(json.dumps({'prepared':True,'browserOpened':False,'networkRequestsExecuted':0,'execution':'Require explicit root builtsite gate, --execute and --expected-video-sha exactnewmediaSHA.'}));raise SystemExit(0)
    if not args.expected_video_sha or not re.fullmatch(r'[0-9a-f]{64}',args.expected_video_sha):parser.error('ExactfinalvideoSHA required for --execute')
    run(args.expected_video_sha)
