#!/usr/bin/env python3
"""Fresh height-choice site QA after the article/figure/player runtime update.

Preparation is safe via --help. A real run requires the final preview URL,
version, complete video SHA and frozen-manifest SHA supplied after the build.
Does not edit production files, fetch source documents, build or publish.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import traceback
from urllib.parse import urljoin, urlsplit
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

D=Path(__file__).resolve().parents[1]
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file() and (p/'site/package.json').is_file())
SLUG='redis-skiplist'
BODY=4557
FINAL=4707
FIGURE_FRAME=2667
FIGURE_TIME=88.9
VIEWPORTS=[('desktop',{'width':1440,'height':1000}),('narrow',{'width':390,'height':844})]
RUNTIME_FILES=['site/src/components/SourceQuote.astro','site/src/components/Figure.astro','site/src/components/VideoPlayer.astro','site/src/components/SiteHeader.astro','site/src/components/ThemeToggle.astro','site/src/layouts/BaseLayout.astro','site/src/pages/episodes/[slug]/index.astro','site/src/styles/global.css','site/src/styles/tokens.css','site/scripts/article-sources.mjs']


def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

# Reuse only the inspected video seek implementation, never old timing constants
# or old runtime/article approval. Its exact source is recorded in this report.
SEEK_HELPER=ROOT/'episodes-codex/redis-skiplist/revisions/clear-parts/redis-skiplist/qa-tools/site-browser.py'
SEEK=module('height_choice_seek_helper',SEEK_HELPER).SEEK
ONLINE_HELPER=SEEK_HELPER.with_name('online-browser.py')


def check(case,name,ok,observed=None):
    case['checks'].append({'name':name,'passed':bool(ok),'observed':observed})
    assert ok,name


def stable(locator,block='center'):
    return locator.evaluate("""async (e,block)=>{e.scrollIntoView({block,behavior:'instant'});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const b=e.getBoundingClientRect();return {left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth}}""",block)


def shot(page,locator,out,name,case):
    stable(locator);p=out/(name+'.png');locator.screenshot(path=str(p));case['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})


def expected_inputs(args):
    pub=ROOT/'episodes'/SLUG;meta=read(pub/'meta.json');sb=read(D/'storyboard.json');startup=read(D/'startup.json')
    assert meta['draft'] is False and meta['ep']==40 and meta['firstRelease']==args.first_release
    for k in ['createdAt','publishedAt','firstRelease']:assert meta[k]==startup[k]
    assert meta['sourcePath']==str(D.relative_to(ROOT))+'/remotion'
    assert read(ROOT/'site/package.json')['version']==args.version.removeprefix('v')
    assert sha(D/'source-sha256.json')==args.expected_manifest_sha256
    assert sha(D/'video.mp4')==sha(pub/'video.mp4')==args.expected_video_sha256
    assert read(pub/'storyboard.json')==sb and sb['meta']['durationInFrames']==BODY
    assert meta['referenceAppendix']['from']==BODY and meta['finalVideoFrames']==FINAL
    assert meta['referenceAppendix']['durationInFrames']==FINAL-BODY==150
    assert sha(pub/'article.mdx')==sha(D/'article.mdx')
    assert sha(pub/'article-sources.json')==sha(D/'article-sources.json')
    article=(pub/'article.mdx').read_text();front=article.split('---',2)[1]
    titles={a.strip():b.strip().strip('"\'') for a,b in re.findall(r'^\s*-\s*\{\s*id:\s*([^,]+),\s*title:\s*(.*?)\s*\}',front,re.M)}
    chapters=[];cues=[];fps=sb['meta']['fps']
    for scene in sb['scenes']:
        for s in scene['shots']:
            if not chapters or chapters[-1]['id']!=s['chapterId']:chapters.append({'id':s['chapterId'],'title':titles[s['chapterId']],'start':s['from']/fps})
            for c in s['subtitles']:
                start=s['from']+c['from'];end=s['from']+c['to']+1
                cues.append({'text':c['text'],'startMS':(2*start*1000+fps)//(2*fps),'endMS':((end*1000+fps-1)//fps-1) if end==BODY else (2*end*1000+fps)//(2*fps)})
    assert len(cues)==20 and [x['id'] for x in chapters]==['goal','search','insert','boundary']
    sources={}
    for n in ['references.json','article-sources.json']:
        for s in read(pub/n)['sources']:assert s['id'] not in sources;sources[s['id']]=s
    quote_attrs=re.findall(r'<SourceQuote\s+sourceId="([^"]+)"\s+supports="([^"]+)"\s*/>',article)
    assert [x[0] for x in quote_attrs]==['R1','A1']
    evidence={}
    for sid,support in quote_attrs:
        s=sources[sid];assert s['quotation']['text'] in (ROOT/s['quotation']['evidence']).read_text()
        evidence[sid]={'quotationEvidenceSHA256':sha(ROOT/s['quotation']['evidence']),'verificationEvidenceSHA256':sha(ROOT/s['verification']['evidence']),'historicalCheckedAtRetained':s['verification']['checkedAt'],'fetchedByThisTool':False}
    fig=re.search(r'<Figure\s+(.*?)\s*/>',article,re.S).group(1)
    attrs={k:re.search(k+r'="([^"]+)"',fig).group(1) for k in ['src','alt','caption']}
    attrs['seekTo']=float(re.search(r'seekTo=\{([^}]+)\}',fig).group(1));assert attrs['seekTo']==FIGURE_TIME
    figure_file=pub/'article/height-one.jpg';assert attrs['src']=='/video-studio/episodes/'+SLUG+'/article/height-one.jpg' and figure_file.is_file()
    fence=re.findall(r'^```python[^\n]*\n(.*?)\n```',article,re.M|re.S);assert len(fence)==1
    execution=read(D/'research/article-snippet-verification.json')
    assert execution['status']=='passed' and execution['exitCode']==0 and execution['articleSHA256']==sha(pub/'article.mdx')
    assert execution['snippetSHA256']==digest((fence[0]+'\n').encode())
    pts_raw=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(D/'video.mp4')]))
    pts=[float(f['best_effort_timestamp_time']) for f in pts_raw['frames']];assert len(pts)==FINAL and pts[FIGURE_FRAME]==FIGURE_TIME
    h7=next(s for c in sb['scenes'] for s in c['shots'] if s['id']=='07');c=h7['cueFrames']['sentences'][1];d=h7['voice'][1]['localEnd']
    stage_frames={'height1':FIGURE_FRAME,'reset-before-height2':h7['from']+int(c+(d-c)*.1),'height2-allocated':h7['from']+math.ceil(c+(d-c)*.65)}
    runtime={}
    for n in RUNTIME_FILES:
        expected=digest(git('show',args.runtime_ref+':'+n));actual=sha(ROOT/n);assert actual==expected,'Runtime differs from selected reviewed baseline: '+n;runtime[n]=actual
    return {'pub':pub,'meta':meta,'sb':sb,'fps':fps,'chapters':chapters,'cues':cues,'sources':sources,'quote_attrs':quote_attrs,'evidence':evidence,'figure':attrs,'figure_file':figure_file,'code':fence[0],'execution':execution,'pts':pts,'stage_frames':stage_frames,'runtime':runtime}


def source_frame_check(data,out):
    p=out/'decoded-final-frame-002667.png'
    cmd=['ffmpeg','-v','error','-y','-i',str(D/'video.mp4'),'-vf','select=eq(n\\,2667)','-frames:v','1',str(p)]
    subprocess.run(cmd,check=True)
    with Image.open(p) as a,Image.open(data['figure_file']) as b:
        assert a.size==b.size==(1920,1080)
        aa=a.convert('RGB');bb=b.convert('RGB');metrics={}
        for name,box in [('whole',(0,0,1920,1080)),('graph',(60,230,1790,800))]:
            rms=ImageStat.Stat(ImageChops.difference(aa.crop(box),bb.crop(box))).rms;metrics[name]=sum(x*x for x in rms)**.5/3**.5
        assert all(x<8 for x in metrics.values()),'Article JPEG does not match selected final frame'
    return {'videoSHA256':sha(D/'video.mp4'),'frame':FIGURE_FRAME,'encodedPTS':data['pts'][FIGURE_FRAME],'JPEGFile':str(data['figure_file'].relative_to(ROOT)),'JPEG_SHA256':sha(data['figure_file']),'decodedPNG':str(p.relative_to(ROOT)),'decodedPNG_SHA256':sha(p),'command':cmd,'lossyRGB_RMSE':metrics,'scope':'Decoded exact final frame compared with JPEG using lossy-image tolerance; JPG/PNG bytes are not expected equal. Actual visual review remains required.'}


ARM_FIGURE="""({fps})=>{const v=document.querySelector('#player video');v.pause();const trace={events:[],frames:[]};window.__qaFigureClickTrace=trace;window.__qaFigureClick=new Promise((resolve,reject)=>{let paint=null,sought=false,done=false,finishing=false;const timer=setTimeout(()=>{done=true;reject(new Error('Figure completed-seek paint timeout: '+JSON.stringify({time:v.currentTime,paused:v.paused,trace})))},12000);const finish=()=>{if(done||finishing||!sought||!paint||Math.round(paint.mediaTime*fps)!==Math.round(v.currentTime*fps))return;finishing=true;requestAnimationFrame(()=>requestAnimationFrame(()=>{finishing=false;if(done)return;if(Math.round(paint.mediaTime*fps)!==Math.round(v.currentTime*fps)){finish();return}done=true;clearTimeout(timer);resolve({time:v.currentTime,paused:v.paused,painted:paint,hash:location.hash,live:document.querySelector('#player [data-live]').textContent,error:v.error?.message??null,trace})}))};const onpaint=(now,info)=>{paint={mediaTime:info.mediaTime,presentedFrames:info.presentedFrames};trace.frames.push({...paint,time:v.currentTime,afterSeeked:sought,epochMS:performance.timeOrigin+performance.now()});finish();if(!done)v.requestVideoFrameCallback(onpaint)};v.requestVideoFrameCallback(onpaint);v.addEventListener('seeking',()=>trace.events.push({type:'seeking',time:v.currentTime,epochMS:performance.timeOrigin+performance.now()}),{once:true});v.addEventListener('seeked',()=>{v.pause();sought=true;trace.events.push({type:'seeked',time:v.currentTime,paused:v.paused,epochMS:performance.timeOrigin+performance.now()});finish()},{once:true})});return true}"""


def run_case(browser,args,data,out,label,viewport,theme,online):
    case={'name':label,'viewport':viewport,'theme':theme,'checks':[],'screenshots':[],'pageErrors':[],'consoleErrors':[],'requestFailures':[],'blockedExternalRequests':[],'mediaWitnesses':[]}
    ctx=browser.new_context(viewport=viewport,color_scheme=theme,reduced_motion='reduce',device_scale_factor=1,ignore_https_errors=False)
    if not online:
        def local_only(route):
            if urlsplit(route.request.url).hostname in ['127.0.0.1','localhost','::1'] or route.request.url.startswith(('data:','blob:')):route.continue_()
            else:case['blockedExternalRequests'].append(route.request.url);route.abort()
        ctx.route('**/*',local_only)
    page=ctx.new_page();page.set_default_timeout(16000);phase={'name':'navigation','since':time.time()*1000};requests={}
    page.on('pageerror',lambda e:case['pageErrors'].append(str(e)));page.on('console',lambda m:case['consoleErrors'].append(m.text) if m.type=='error' else None)
    page.add_init_script("window.__qaMediaEvents=[];for(const type of ['loadedmetadata','suspend','seeking','seeked','error'])document.addEventListener(type,e=>{const v=e.target;if(v.tagName==='VIDEO')window.__qaMediaEvents.push({type,epochMS:performance.timeOrigin+performance.now(),preload:v.preload,error:v.error?.message??null})},true)")
    def requested(req):requests[req]={'url':req.url,'resourceType':req.resource_type,'range':req.headers.get('range')}
    def failed(req):case['requestFailures'].append({**requests.get(req,{'url':req.url,'resourceType':req.resource_type,'range':req.headers.get('range')}),'failure':req.failure,'phase':phase['name'],'since':phase['since'],'epochMS':time.time()*1000})
    if online:page.on('request',requested);page.on('requestfailed',failed)
    def setphase(name):phase.update(name=name,since=time.time()*1000)
    def witness(kind):case['mediaWitnesses'].append({'kind':kind,'epochMS':time.time()*1000,**page.locator('#player video').evaluate('v=>({readyState:v.readyState,error:v.error?.message??null})')})
    try:
        url=urljoin(args.base_url,'episodes/'+SLUG+'/');res=page.goto(url,wait_until='networkidle',timeout=60000)
        check(case,'actual canonical/preview episode HTTP200',res.status==200 and page.url==url)
        if not online:check(case,'served exact fresh built HTML',digest(res.body())==sha(ROOT/'site/dist/episodes'/SLUG/'index.html'))
        page.locator('.theme-trigger').click();page.locator('[data-theme-opt="'+theme+'"]').click()
        page.wait_for_function('(t)=>document.documentElement.dataset.theme===t',arg=theme)
        check(case,'actual appearance control selects theme',page.evaluate('document.documentElement.dataset.themePref')==theme)
        brand=page.locator('header.hdr .logo img.brand-mark');brand.wait_for();page.wait_for_function("()=>{const i=document.querySelector('header.hdr .brand-mark');return i.complete&&i.naturalWidth>0}")
        check(case,'current brand avatar loaded',brand.get_attribute('src').endswith('favicon.svg?v=code-village'))
        shot(page,page.locator('header.hdr'),out,label+'-brand-header',case)
        page.wait_for_function("()=>{const v=document.querySelector('#player video');return v&&v.readyState>=2&&Number.isFinite(v.duration)}")
        video=page.locator('#player video');media=video.evaluate('v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,controls:v.controls,playsInline:v.playsInline,src:v.currentSrc,error:v.error?.message??null})');case['media']=media
        check(case,'new4707-frame video metadata',abs(media['duration']-FINAL/data['fps'])<.01 and (media['width'],media['height'])==(1920,1080) and media['controls'] and media['playsInline'] and media['error'] is None,media)
        expected_source='https://github.com/linhongcun/video-studio/tree/main/'+data['meta']['sourcePath']
        check(case,'new height-choice source link',page.locator('a[href="'+expected_source+'"]').count()==1)
        chapters=page.locator('#player').evaluate('e=>JSON.parse(e.dataset.chapters)');check(case,'current article-priority chapters and SB starts',chapters==data['chapters'],chapters)
        video.evaluate('v=>{v.muted=true;v.textTracks[0].mode="hidden";v.playbackRate=1}')
        page.wait_for_function("()=>document.querySelector('#player video').textTracks[0].cues?.length===20")
        cues=video.evaluate('v=>[...v.textTracks[0].cues].map(c=>({text:c.text,startMS:Math.round(c.startTime*1000),endMS:Math.round(c.endTime*1000)}))');check(case,'20 current native cue texts/windows',cues==data['cues'])
        if theme=='dark':
            setphase('short-playback');video.evaluate('v=>v.play()');page.wait_for_function("()=>document.querySelector('#player video').currentTime>.25");sample=video.evaluate('v=>{v.pause();return {time:v.currentTime,rate:v.playbackRate}}');check(case,'actual muted1x short playback',sample['time']>.25 and sample['rate']==1,sample);witness('short-playback')
            case['chapterClicks']=[]
            for c in chapters:
                setphase('chapter-'+c['id']);kind='.ch' if viewport['width']>=768 else '.chip';page.locator('#player '+kind+'[data-id="'+c['id']+'"]').click()
                page.wait_for_function('(t)=>{const v=document.querySelector("#player video");return !v.seeking&&v.currentTime>=t&&v.currentTime<t+.5}',arg=c['start']);sample=video.evaluate('v=>{v.pause();return {time:v.currentTime,error:v.error?.message??null}}');case['chapterClicks'].append({'id':c['id'],**sample});check(case,'actual chapter click '+c['id'],abs(sample['time']-c['start'])<.5 and sample['error'] is None)
        article=page.locator('#article');check(case,'R1 and A1 source modules present',article.locator('.source-quote').count()==2)
        case['quotes']=[]
        for sid,support in data['quote_attrs']:
            s=data['sources'][sid];q=article.locator('[data-source-quote="'+sid+'"]');rect=stable(q)
            actual=q.locator('blockquote p').text_content();identity=q.locator('.source-identity').inner_text().strip();date=q.locator('.source-access time').get_attribute('datetime')
            ok=actual==s['quotation']['text'] and q.locator('cite a').text_content()==s['title'] and q.locator('cite a').get_attribute('href')==s['url'] and q.locator('blockquote').get_attribute('cite')==s['verification'].get('sourceUrl',s['url']) and identity==(s.get('author') or s['organization'])+' · '+s['version'] and s['quotation']['locator'] in q.locator('.source-location').inner_text() and date==s['verification']['checkedAt'] and support in q.locator('.source-support').inner_text()
            check(case,'exact quotation identity/support/date '+sid,ok,{'historicalCheckedAt':date,'characters':len(actual),'rect':rect})
            check(case,'source text wraps within viewport '+sid,rect['left']>=-1 and rect['right']<=viewport['width']+1 and rect['scrollWidth']<=rect['clientWidth']+1)
            case['quotes'].append({'id':sid,'quoteSHA256':digest(actual.encode()),'checkedAt':date});shot(page,q,out,label+'-quote-'+sid,case)
        fig=article.locator('figure.fig[data-figure-kind="video"]');check(case,'one planned height1 screenshot Figure',fig.count()==1)
        stable(fig);img=fig.locator('img');page.wait_for_function("()=>{const i=document.querySelector('#article figure.fig img');return i&&i.complete&&i.naturalWidth===1920&&i.naturalHeight===1080}")
        check(case,'Figure exact alt/caption/time links',img.get_attribute('alt')==data['figure']['alt'] and data['figure']['caption'] in fig.locator('figcaption').inner_text() and fig.locator('.fig-image-link').get_attribute('href')==data['figure']['src'] and fig.locator('figcaption a').first.get_attribute('href')==data['figure']['src'] and fig.locator('[data-seek-time]').get_attribute('data-seek-time')==str(FIGURE_TIME))
        served=ctx.request.get(urljoin(args.base_url,data['figure']['src']));check(case,'served complete final-frame JPEG identity',served.status==200 and digest(served.body())==sha(data['figure_file']));served.dispose();shot(page,fig,out,label+'-article-height1',case)
        if not online:
            setphase('image-original');fig.locator('.fig-image-link').click();page.wait_for_url('**/article/height-one.jpg');page.wait_for_function('()=>document.querySelector("img")?.naturalWidth===1920');check(case,'real image click opens original JPEG',page.url==urljoin(args.base_url,data['figure']['src']));page.go_back(wait_until='networkidle');page.wait_for_function("()=>document.querySelector('#player video')?.readyState>=2");video=page.locator('#player video');video.evaluate('v=>{v.muted=true;v.textTracks[0].mode="hidden"}')
        setphase('figure-time-click');link=page.locator('#article [data-seek-time="88.9"]');stable(link);page.evaluate(ARM_FIGURE,{'fps':data['fps']});link.click();jump=page.evaluate('()=>window.__qaFigureClick');jump['paintedFrame']=round(jump['painted']['mediaTime']*data['fps']);case['figureTimeClick']=jump
        check(case,'real Figure time click paints exact2667',jump['paintedFrame']==FIGURE_FRAME and jump['paused'] and jump['error'] is None and jump['hash']=='#t=88.9' and '88.9' in jump['live'],jump);witness('figure-time-click');shot(page,page.locator('#player'),out,label+'-player-height1',case)
        if theme=='dark':
            case['heightStagePauses']=[]
            for name,frame in data['stage_frames'].items():
                if name=='height1':continue
                setphase(name);pause=page.evaluate(SEEK,{'time':(frame+.5)/data['fps'],'fps':data['fps'],'expectedFrame':frame});case['heightStagePauses'].append({'name':name,**pause});check(case,'exact new stage paint '+name,pause['paintedFrame']==frame and pause['paused'] and pause['error'] is None,pause);shot(page,video,out,label+'-'+name,case)
        setphase('reference-first');pause=page.evaluate(SEEK,{'time':BODY/data['fps'],'fps':data['fps'],'expectedFrame':BODY});case['firstReferencePause']=pause;check(case,'exact4557 reference frame no active cue',pause['paintedFrame']==BODY and pause['paused'] and not pause['activeCues'] and pause['error'] is None,pause);witness('reference-first');shot(page,video,out,label+'-references-first',case)
        if theme=='dark' and not online:
            page.evaluate("()=>{const b=document.createElement('button');b.id='qa-native-fullscreen';b.style.cssText='position:fixed;top:0;left:0;z-index:99999';b.textContent='QA fullscreen';b.onclick=()=>document.querySelector('#player video').requestFullscreen();document.body.append(b)}");page.locator('#qa-native-fullscreen').click();page.wait_for_function('()=>document.fullscreenElement===document.querySelector("#player video")')
            if viewport['width']==390:page.set_viewport_size({'width':844,'height':390})
            frame=BODY+76;pause=page.evaluate(SEEK,{'time':(frame+.5)/data['fps'],'fps':data['fps'],'expectedFrame':frame});case['fullscreen']={'active':True,'pause':pause,'invocation':'Trusted QA button calling real video.requestFullscreen; headless viewport only'};check(case,'real fullscreen exact reference and no cue',pause['paintedFrame']==frame and not pause['activeCues'] and pause['error'] is None)
            fp=out/(label+'-fullscreen.png');page.screenshot(path=str(fp));case['screenshots'].append({'path':str(fp.relative_to(ROOT)),'sha256':sha(fp)});page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.set_viewport_size(viewport);page.locator('#qa-native-fullscreen').evaluate('e=>e.remove()')
        code=page.locator('#article pre code').text_content();check(case,'actual43-line code remains exact source',code==data['code'],{'lines':len(code.splitlines()),'codeSHA256':digest(code.encode()),'executionRerun':False})
        check(case,'four article TOC destinations',page.locator('.toc [data-toc]').count()==4 and all(page.locator('#article #'+c['id']).count()==1 for c in chapters))
        dims=page.evaluate('({width:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth})');check(case,'reading page has no horizontal overflow',dims['document']<=viewport['width'] and dims['body']<=viewport['width'],dims)
        case['mediaEvents']=page.evaluate('window.__qaMediaEvents');case['expectedMediaCancellations']=[];case['unexpectedRequestFailures']=[]
        for f in case['requestFailures']:
            later=[w for w in case['mediaWitnesses'] if w['epochMS']>f['epochMS'] and w['error'] is None and w['readyState']>=2]
            exact=f['url']==urljoin(url,data['meta']['video']) and f['resourceType']=='media' and bool(f['range']) and f['failure']=='net::ERR_ABORTED'
            seeks=[e for e in case['mediaEvents'] if e['type']=='seeking' and e['error'] is None and f['since']-100<=e['epochMS']<=f['epochMS']+100]
            seek_phase=f['phase'].startswith('chapter-') or f['phase'] in ['figure-time-click','reset-before-height2','height2-allocated','reference-first']
            before=[e for e in case['mediaEvents'] if e['epochMS']<=f['epochMS']+100 and e['error'] is None]
            preload=f['phase'] in ['navigation','short-playback'] and any(e['type']=='loadedmetadata' for e in before) and any(e['type']=='suspend' and e['preload']=='metadata' for e in before)
            if exact and later and ((seek_phase and seeks) or preload):case['expectedMediaCancellations'].append({**f,'subsequentSuccessfulWitness':later[0],'seekEvidence':seeks,'preloadMetadataEvidence':before if preload else []})
            else:case['unexpectedRequestFailures'].append(f)
        check(case,'no unexpected network/JavaScript errors',not case['pageErrors'] and not case['consoleErrors'] and not case['blockedExternalRequests'] and not case['unexpectedRequestFailures'])
        case['status']='passed'
    except Exception as exc:case.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
    finally:
        if online:page.remove_listener('request',requested);page.remove_listener('requestfailed',failed)
        ctx.close()
    return case


def main(online=False):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',required=not online,default='https://linhongcun.github.io/video-studio/' if online else None)
    parser.add_argument('--version',required=True)
    parser.add_argument('--expected-video-sha256',required=True)
    parser.add_argument('--expected-manifest-sha256',required=True)
    parser.add_argument('--first-release',default='v0.72.0')
    parser.add_argument('--runtime-ref',default='29dc6461')
    parser.add_argument('--themes',nargs='+',choices=['light','dark'],default=['dark'] if online else ['light','dark'])
    parser.add_argument('--deployment-run',type=int,required=online)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args();host=urlsplit(args.base_url).hostname
    assert (host=='linhongcun.github.io' and args.base_url=='https://linhongcun.github.io/video-studio/') if online else host in ['127.0.0.1','localhost','::1']
    assert args.base_url.endswith('/')
    data=expected_inputs(args);out=D/('qa-online-browser-evidence' if online else 'qa-site-browser-evidence');out.mkdir(exist_ok=True);path=args.report or D/('qa-online-browser.json' if online else 'qa-site-browser.json');assert path.resolve().is_relative_to(D)
    if path.exists():
        archive=D/'qa-revisions'/('online-browser' if online else 'site-browser');archive.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,archive/('previous-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'))
    report={'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'version':args.version,'firstRelease':args.first_release,'baseURL':args.base_url,'deploymentRun':args.deployment_run,'videoSHA256':args.expected_video_sha256,'manifestSHA256':args.expected_manifest_sha256,'bodyFrames':BODY,'finalFrames':FINAL,'figureFrame':FIGURE_FRAME,'runtimeRef':args.runtime_ref,'runtimeSHA256':data['runtime'],'sourceEvidence':data['evidence'],'publicationIdentity':{k:data['meta'][k] for k in ['createdAt','publishedAt','firstRelease','updatedAt','sourcePath']},'scriptSHA256':sha(__file__),'seekHelperSHA256':sha(SEEK_HELPER),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [data['pub']/'article.mdx',data['pub']/'article-sources.json',data['figure_file'],D/'storyboard.json']},'viewports':[],'limitations':['Headless desktop Chromium viewports, not physical devices.','Muted short playback and selected exact-frame tests; no full-film semantic listening/ASR.','Historical source evidence is reused with original dates; no source-document fetch by this tool.','Oldsame-runtime approval is not reused; current SourceQuote/Figure/VideoPlayer are exercised.']}
    if not online:report['figureSourceFrameCheck']=source_frame_check(data,out)
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    save()
    launch={'executable_path':shutil.which('chromium'),'headless':True,'args':['--no-sandbox']}
    if online:
        assert os.environ.get('SSL_CERT_FILE') and Path(os.environ['SSL_CERT_FILE']).is_file();launch['proxy']=module('height_choice_proxy_helper',ONLINE_HELPER).inherited_proxy()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch);report['environment']={'browserVersion':browser.version,'playwright':importlib.metadata.version('playwright')}
        try:
            for name,viewport in VIEWPORTS:
                for theme in args.themes:
                    case=run_case(browser,args,data,out,name+'-'+theme,viewport,theme,online);report['viewports'].append(case);save();print(case['name'],case['status'],len(case['checks']),'checks',flush=True);assert case['status']=='passed',case.get('error')
            assert sha(D/'video.mp4')==args.expected_video_sha256 and sha(D/'source-sha256.json')==args.expected_manifest_sha256
            report.update(status='passed',completedAtUTC=datetime.now(timezone.utc).isoformat(),productionInputsUnchanged=True)
        except Exception as exc:report.update(status='failed',error=repr(exc),completedAtUTC=datetime.now(timezone.utc).isoformat());raise
        finally:browser.close();save()


if __name__=='__main__':main()
