#!/usr/bin/env python3
"""Local built-site Chromium QA for Bloom. Does not build, copy or publish."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import traceback
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright


ROOT = Path('/workspace/video-studio').resolve()
D = ROOT / 'episodes-codex/bloom-filter'
SLUG = 'bloom-filter'
CHAPTER_IDS = ['goal', 'write', 'query', 'boundary']
VIEWPORTS = [('desktop', {'width': 1440, 'height': 1000}),
             ('narrow', {'width': 390, 'height': 844})]


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT)


SEEK = """async ({time, fps}) => {
  const v=document.querySelector('#player video'); v.pause();
  const painted=new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('No painted frame after seek')),8000);
    v.requestVideoFrameCallback((now,info)=>{clearTimeout(timer);resolve({mediaTime:info.mediaTime,presentedFrames:info.presentedFrames})});
  });
  const sought=new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('seeked event timed out')),8000);
    v.addEventListener('seeked',()=>{clearTimeout(timer);resolve()}, {once:true});
  });
  v.currentTime=time; await sought; const frame=await painted;
  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  return {requestedTime:time,currentTime:v.currentTime,painted:frame,
    requestedFrame:Math.round(time*fps),paintedFrame:Math.round(frame.mediaTime*fps),
    paused:v.paused,readyState:v.readyState,error:v.error?.message??null,
    activeCues:[...v.textTracks].flatMap(t=>[...(t.activeCues||[])].map(c=>c.text))};
}"""

PLAY_END = """async ({from, duration}) => {
  const v=document.querySelector('#player video');v.pause();v.muted=true;v.playbackRate=1;
  await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('end-playback seek timeout')),8000);
    v.addEventListener('seeked',()=>{clearTimeout(t);resolve()}, {once:true});v.currentTime=from});
  const samples=[];const tick=()=>samples.push({time:v.currentTime,paused:v.paused,ended:v.ended});
  v.addEventListener('timeupdate',tick);const began=performance.now();
  const ended=new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('Playback did not reach video end')),(duration-from+8)*1000);
    v.addEventListener('ended',()=>{clearTimeout(t);resolve()}, {once:true});
    v.addEventListener('error',()=>{clearTimeout(t);reject(new Error(v.error?.message||'media error'))},{once:true})});
  await v.play();await ended;v.removeEventListener('timeupdate',tick);
  return {from,currentTime:v.currentTime,duration:v.duration,ended:v.ended,
    playbackRate:v.playbackRate,muted:v.muted,elapsedSeconds:(performance.now()-began)/1000,samples,error:v.error?.message??null};
}"""


def expected_data(meta, sb):
    fps = sb['meta']['fps']; body = sb['meta']['durationInFrames']
    assert meta['referenceAppendix']['from'] == body
    assert meta['finalVideoFrames'] == body + meta['referenceAppendix']['durationInFrames']
    chapters, cues = [], []
    for scene in sb['scenes']:
        for shot in scene['shots']:
            if not chapters or chapters[-1]['id'] != shot['chapterId']:
                chapters.append({'id': shot['chapterId'], 'start': shot['from'] / fps})
            for cue in shot['subtitles']:
                start = shot['from'] + cue['from']; end = shot['from'] + cue['to'] + 1
                start_ms = (2 * start * 1000 + fps) // (2 * fps)
                end_ms = ((end * 1000 + fps - 1) // fps - 1) if end == body else (2 * end * 1000 + fps) // (2 * fps)
                cues.append({'text': cue['text'], 'startMS': start_ms, 'endMS': end_ms})
    assert [c['id'] for c in chapters] == CHAPTER_IDS and len(cues) == 26
    return fps, body, chapters, cues


def check(case, name, passed, observed=None, expected=None):
    row = {'name': name, 'passed': bool(passed)}
    if observed is not None: row['observed'] = observed
    if expected is not None: row['expected'] = expected
    case['checks'].append(row)
    assert passed, name


def screenshot(page, locator, out, name, case):
    path = out / (name + '.png')
    locator.scroll_into_view_if_needed()
    locator.screenshot(path=str(path))
    case['screenshots'].append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})


def run_case(browser, args, name, viewport, meta, sb, out):
    fps, body, expected_chapters, expected_cues = expected_data(meta, sb)
    case = {'name': name, 'viewport': viewport, 'checks': [], 'screenshots': [],
            'pageErrors': [], 'consoleErrors': [], 'blockedExternalRequests': []}
    context = browser.new_context(viewport=viewport, device_scale_factor=1, color_scheme='dark',
                                  reduced_motion='reduce', permissions=['clipboard-read','clipboard-write'])
    def local_only(route):
        host = urlparse(route.request.url).hostname
        if host in ['127.0.0.1', 'localhost', '::1'] or route.request.url.startswith(('data:', 'blob:')):
            route.continue_()
        else:
            case['blockedExternalRequests'].append(route.request.url);route.abort()
    context.route('**/*', local_only)
    page = context.new_page();page.set_default_timeout(12000)
    page.on('pageerror', lambda error: case['pageErrors'].append(str(error)))
    page.on('console', lambda msg: case['consoleErrors'].append(msg.text) if msg.type == 'error' else None)
    try:
        url = urljoin(args.base_url, f'episodes/{SLUG}/')
        response = page.goto(url, wait_until='networkidle')
        built_html = ROOT / f'site/dist/episodes/{SLUG}/index.html'
        check(case, 'serves exact built episode HTML', response.status == 200 and digest(response.body()) == sha(built_html),
              {'status': response.status, 'sha256': digest(response.body())}, sha(built_html))
        page.wait_for_function("() => {const v=document.querySelector('#player video');return v&&v.readyState>=1&&Number.isFinite(v.duration)}")
        video = page.locator('#player video')
        state = video.evaluate("v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,controls:v.controls,playsInline:v.playsInline,src:v.currentSrc,poster:v.poster,error:v.error?.message??null,defaultModes:[...v.textTracks].map(t=>t.mode)})")
        case['media'] = state
        check(case, 'actual final video duration and dimensions', abs(state['duration']-meta['finalVideoFrames']/fps) < .01 and (state['width'],state['height']) == (1920,1080), state)
        check(case, 'native controls and inline playback retained', state['controls'] and state['playsInline'] and state['error'] is None, state)
        for key, source in [('video',state['src']),('poster',state['poster'])]:
            assert urlparse(source).hostname in ['127.0.0.1','localhost','::1']
            served = context.request.get(source); content = served.body(); expected = ROOT/'episodes'/SLUG/meta[key]
            check(case, 'complete served '+key+' matches publication copy', served.status == 200 and digest(content) == sha(expected),
                  {'url':source,'status':served.status,'bytes':len(content),'sha256':digest(content)},sha(expected));served.dispose()
        chapters = page.locator('#player').evaluate('e=>JSON.parse(e.dataset.chapters)')
        check(case, 'four chapter identities and exact starts', [{k:c[k] for k in ['id','start']} for c in chapters] == expected_chapters, chapters, expected_chapters)
        case['chapters'] = chapters
        video.evaluate("v=>{v.muted=true;v.textTracks[0].mode='showing'}")
        page.wait_for_function("()=>{const t=document.querySelector('#player video').textTracks[0];return t&&t.cues&&t.cues.length===26}")
        actual_cues = video.evaluate("v=>[...v.textTracks[0].cues].map(c=>({text:c.text,startMS:Math.round(c.startTime*1000),endMS:Math.round(c.endTime*1000),start:c.startTime,end:c.endTime}))")
        check(case, '26 native VTT texts and exact millisecond boundaries', [{k:c[k] for k in ['text','startMS','endMS']} for c in actual_cues] == expected_cues, actual_cues, expected_cues)
        case['nativeCues'] = actual_cues
        vtt = context.request.get(urljoin(url, 'captions.vtt')); vtt_path=ROOT/f'site/dist/episodes/{SLUG}/captions.vtt'
        check(case,'served VTT exact built bytes',vtt.status==200 and digest(vtt.body())==sha(vtt_path),{'sha256':digest(vtt.body()),'bytes':len(vtt.body())},sha(vtt_path));vtt.dispose()
        video.evaluate('v=>v.play()');page.wait_for_function("()=>document.querySelector('#player video').currentTime>.25")
        first_play = video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,muted:v.muted,rate:v.playbackRate}}')
        check(case,'actual short 1x playback advanced',first_play['time']>.25 and first_play['paused'] and first_play['rate']==1,first_play)
        screenshot(page,page.locator('#player'),out,name+'-player',case)
        case['chapterSeeks']=[]
        for chapter in chapters:
            selector=(f'#player .ch[data-id="{chapter["id"]}"]' if viewport['width']>=768 else f'#player .chip[data-id="{chapter["id"]}"]')
            page.locator(selector).click()
            page.wait_for_function('(t)=>{const v=document.querySelector("#player video");return !v.seeking&&v.currentTime>=t&&v.currentTime<t+.5}',arg=chapter['start'])
            sought=video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,error:v.error?.message??null}}')
            sought.update(id=chapter['id'],expected=chapter['start']);case['chapterSeeks'].append(sought)
            check(case,'real chapter click seeks '+chapter['id'],sought['paused'] and abs(sought['time']-chapter['start'])<.5 and sought['error'] is None,sought)
        continuous=page.evaluate(PLAY_END,{'from':(body-15)/fps,'duration':meta['finalVideoFrames']/fps});case['appendixPlayback']=continuous
        check(case,'1x playback crosses audio end and reaches video end',continuous['ended'] and continuous['error'] is None and any(x['time']>body/fps+.3 for x in continuous['samples']) and abs(continuous['currentTime']-meta['finalVideoFrames']/fps)<.01,continuous)
        case['referencePauses']=[]
        for label,frame in [('first',body),('middle',body+meta['referenceAppendix']['durationInFrames']//2),('last',meta['finalVideoFrames']-1)]:
            paused=page.evaluate(SEEK,{'time':frame/fps,'fps':fps});paused.update(name=label,requestedFrame=frame);case['referencePauses'].append(paused)
            check(case,'painted reference '+label+' frame has no native caption',paused['paused'] and paused['paintedFrame']==frame and not paused['activeCues'] and paused['error'] is None,paused)
            video.hover();screenshot(page,video,out,name+'-references-'+label,case)
        # A genuine API request under a trusted click; no claim of clicking browser chrome.
        page.evaluate("""()=>{const b=document.createElement('button');b.id='qa-enter-native-fullscreen';b.textContent='Fullscreen QA';
          b.style.cssText='position:fixed;z-index:99999;left:4px;top:4px';b.onclick=()=>{window.__qaFullscreenError=null;document.querySelector('#player video').requestFullscreen().catch(e=>window.__qaFullscreenError=String(e))};document.body.append(b)}""")
        page.locator('#qa-enter-native-fullscreen').click()
        page.wait_for_function("()=>document.fullscreenElement===document.querySelector('#player video')||window.__qaFullscreenError")
        if viewport['width']==390: page.set_viewport_size({'width':844,'height':390})
        full_pause=page.evaluate(SEEK,{'time':(body+76)/fps,'fps':fps})
        fullscreen=video.evaluate("v=>({active:document.fullscreenElement===v,enabled:document.fullscreenEnabled,error:window.__qaFullscreenError,rect:{width:v.getBoundingClientRect().width,height:v.getBoundingClientRect().height},viewport:{width:innerWidth,height:innerHeight}})")
        fullscreen.update(pause=full_pause,invocation='QA-only button click invoking real video.requestFullscreen()',viewportSimulation='Headless landscape viewport, not physical rotation' if viewport['width']==390 else 'Desktop viewport');case['fullscreen']=fullscreen
        check(case,'real native fullscreen API entered with paused reference frame',fullscreen['active'] and fullscreen['error'] is None and full_pause['paused'] and not full_pause['activeCues'],fullscreen)
        full_path=out/(name+'-references-fullscreen.png');page.screenshot(path=str(full_path));case['screenshots'].append({'path':str(full_path.relative_to(ROOT)),'sha256':sha(full_path)})
        page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.set_viewport_size(viewport)
        page.locator('#qa-enter-native-fullscreen').evaluate('b=>b.remove()')
        video.evaluate('(v,modes)=>[...v.textTracks].forEach((t,i)=>t.mode=modes[i])',state['defaultModes'])

        toc=page.locator('.toc');check(case,'four article TOC entries',toc.locator('[data-toc]').count()==4,toc.locator('[data-toc]').count())
        if not toc.evaluate('e=>e.open'):toc.locator('summary').click()
        case['tocClicks']=[]
        for cid in CHAPTER_IDS:
            toc.locator(f'[data-toc="{cid}"]').click();page.wait_for_function('(id)=>location.hash==="#"+id',arg=cid)
            case['tocClicks'].append({'id':cid,'hash':urlparse(page.url).fragment})
            check(case,'TOC anchor resolves '+cid,page.locator('#'+cid).count()==1)
        article=page.locator('#article');svgs=article.locator('figure svg')
        check(case,'two native article SVGs',svgs.count()==2,svgs.count())
        case['svgAudit']=[]
        for index in range(2):
            svg=svgs.nth(index);svg.scroll_into_view_if_needed()
            audit=svg.evaluate("""e=>({title:e.querySelector('title')?.textContent,viewBox:e.getAttribute('viewBox'),width:e.getBoundingClientRect().width,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,
              invalidCamelAttributes:[...e.querySelectorAll('*')].flatMap(n=>n.getAttributeNames().filter(a=>['fontSize','textAnchor','strokeWidth','strokeLinecap'].includes(a))),
              texts:[...e.querySelectorAll('text')].map(t=>({text:t.textContent,fontSize:getComputedStyle(t).fontSize,textAnchor:getComputedStyle(t).textAnchor}))})""")
            case['svgAudit'].append(audit)
            check(case,'SVG '+str(index+1)+' standard attributes and responsive width',not audit['invalidCamelAttributes'] and audit['left']>=-1 and audit['right']<=viewport['width']+1 and all(float(x['fontSize'].removesuffix('px'))>0 for x in audit['texts']) and (viewport['width']!=390 or audit['width']>=310),audit)
            screenshot(page,svg,out,name+'-svg-'+str(index+1),case)
        python=article.locator('pre code');code=python.inner_text()
        check(case,'Python mechanism code readable without QA plumbing',all(t in code for t in ['def positions','def add','def maybe_contains','sku101','sku205','sku001','sku067']) and 'argparse' not in code and '--model' not in code)
        copy=article.locator('.cb-copy');check(case,'Python copy control present',copy.count()==1,copy.count());copy.click();page.wait_for_function('()=>document.querySelector("#article .cb-copy").textContent.includes("已复制")')
        case['code']={'characters':len(code),'copyFeedbackShown':True};screenshot(page,article.locator('.cb').first if article.locator('.cb').count() else article.locator('pre'),out,name+'-python',case)
        page.locator('[data-open-course]').click();page.wait_for_function('()=>document.querySelector("#course-directory").open')
        course=page.locator('#course-directory nav a').evaluate_all('els=>els.map(e=>({href:e.getAttribute("href"),current:e.getAttribute("aria-current")}))')
        check(case,'engineering course directory has two real lessons',len(course)==2 and [x['href'] for x in course]==['/video-studio/episodes/consistent-hashing/','/video-studio/episodes/bloom-filter/'],course)
        dates=page.locator('header.eh time').evaluate_all('els=>els.map(e=>e.dateTime)')
        check(case,'creation and modification timestamps retained',meta['createdAt'] in dates and meta['updatedAt'] in dates,dates)
        check(case,'footer shows actual candidate version',args.version in page.locator('footer.ftr').inner_text(),page.locator('footer.ftr').inner_text())
        dimensions=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
        check(case,'episode document has no horizontal overflow',dimensions['document']<=viewport['width'] and dimensions['body']<=viewport['width'],dimensions)
        case['entries']=[]
        for relative in ['', 'learn/', 'series/engineering-algorithms/', 'library/?series=engineering-algorithms&sort=learning']:
            resp=page.goto(urljoin(args.base_url,relative),wait_until='networkidle');check(case,'entry HTTP200 '+relative,resp.status==200,resp.status)
            entry={'path':relative,'status':resp.status}
            if relative=='':
                entry.update(directions=page.locator('.track-links a.track-link').count(),newLesson=page.locator('.recent a.card[href="/video-studio/episodes/bloom-filter/"]').count())
                check(case,'home retains six directions and new lesson',entry['directions']==6 and entry['newLesson']==1,entry)
            elif relative=='learn/':
                lessons=page.locator('#engineering .chapter-lessons a').evaluate_all('els=>els.map(e=>e.getAttribute("href"))');entry.update(directions=page.locator('.learning-track').count(),engineeringLessons=lessons)
                check(case,'learn retains six directions and two engineering lessons',entry['directions']==6 and lessons==['/video-studio/episodes/consistent-hashing/','/video-studio/episodes/bloom-filter/'],entry)
            elif relative.startswith('series/'):
                lessons=page.locator('.lesson-list a.lesson').evaluate_all('els=>els.map(e=>e.getAttribute("href"))');entry['lessons']=lessons
                check(case,'engineering series shows exactly two lessons',lessons==['/video-studio/episodes/consistent-hashing/','/video-studio/episodes/bloom-filter/'],entry)
            else:
                page.wait_for_function('()=>[...document.querySelectorAll("#library-grid > ul > li")].filter(e=>getComputedStyle(e).display!=="none").length===2')
                lessons=page.locator('#library-grid > ul > li:visible a.card').evaluate_all('els=>els.map(e=>e.getAttribute("href"))');entry['lessons']=lessons
                check(case,'library engineering filter preserves order',lessons==['/video-studio/episodes/consistent-hashing/','/video-studio/episodes/bloom-filter/'],entry)
            case['entries'].append(entry)
        rss=context.request.get(urljoin(args.base_url,'rss.xml'));assert rss.status==200
        root=ET.fromstring(rss.body());item=next(i for i in root.findall('./channel/item') if i.findtext('link','').endswith('/episodes/bloom-filter/'))
        check(case,'RSS contains real first-publication time',parsedate_to_datetime(item.findtext('pubDate'))==datetime.fromisoformat(meta['publishedAt']),{'title':item.findtext('title'),'pubDate':item.findtext('pubDate')},meta['publishedAt']);rss.dispose()
        check(case,'no JavaScript or external-request errors',not case['pageErrors'] and not case['consoleErrors'] and not case['blockedExternalRequests'],{'pageErrors':case['pageErrors'],'consoleErrors':case['consoleErrors'],'blockedExternalRequests':case['blockedExternalRequests']})
        case['status']='passed'
    except Exception as exc:
        case.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
    finally:
        context.close()
    return case


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:4321/video-studio/')
    parser.add_argument('--version',required=True)
    parser.add_argument('--report',type=Path,default=D/'qa-site-browser.json')
    parser.add_argument('--out-dir',type=Path,default=D/'qa-site-browser-evidence')
    args=parser.parse_args();assert urlparse(args.base_url).hostname in ['127.0.0.1','localhost','::1'],'This QA tool only opens local preview URLs'
    assert args.base_url.endswith('/') and args.report.resolve().is_relative_to(D) and args.out_dir.resolve().is_relative_to(D)
    assert read(ROOT/'site/package.json')['version']==args.version.removeprefix('v')
    published=ROOT/'episodes'/SLUG;meta=read(published/'meta.json');sb=read(published/'storyboard.json')
    assert meta['draft'] is False and meta['ep']==39 and sb==read(D/'storyboard.json')
    report={'schemaVersion':1,'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'baseURL':args.base_url,'version':args.version,
        'scope':'Actual local headless Chromium, muted 1x playback, four chapter clicks, exact native captions, painted appendix pauses, real fullscreen API, article and engineering entry checks.',
        'limitations':['390px/landscape viewports are headless desktop Chromium, not physical phone or device rotation.','Short muted playback and end-card playback do not establish full-film listening or ASR.','Actual Release/changelog check runs separately after Release-following public deployment.'],
        'script':{'path':__file__,'sha256':sha(__file__)},'productionManifestSHA256':sha(D/'source-sha256.json'),'environment':{'python':shutil.which('python3'),'playwright':importlib.metadata.version('playwright'),'chromium':shutil.which('chromium')},'inputs':{},'viewports':[]}
    for filename in ['meta.json','article.mdx','storyboard.json','video.mp4','cover-16x9.jpg','references.json','reference-appendix.json']:
        p=published/filename;report['inputs'][str(p.relative_to(ROOT))]=sha(p)
    def save():args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if args.report.exists():
        archive=D/'qa-revisions/site-browser';archive.mkdir(parents=True,exist_ok=True);previous=archive/('previous-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');shutil.copyfile(args.report,previous);report['previousReportArchived']=str(previous.relative_to(ROOT))
    args.out_dir.mkdir(parents=True,exist_ok=True);save()
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
        report['environment']['browserVersion']=browser.version
        try:
            for name,viewport in VIEWPORTS:
                case=run_case(browser,args,name,viewport,meta,sb,args.out_dir);report['viewports'].append(case);save();print(name,case['status'],len(case['checks']),'checks',flush=True)
                if case['status']!='passed':raise AssertionError(case['error'])
            baseline=git('rev-parse','origin/main').decode().strip();tree=git('ls-tree','-r','-z',baseline,'--','episodes').split(b'\0');changed=[];count=0
            for entry in tree:
                if not entry:continue
                info,path=entry.split(b'\t');path=path.decode();expected=info.decode().split()[2]
                if path.startswith('episodes/bloom-filter/'):continue
                count+=1;p=ROOT/path
                if not p.is_file():changed.append(path);continue
                content=p.read_bytes();actual=hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()
                if actual!=expected:changed.append(path)
            report['existingEpisodesRetained']={'baseline':baseline,'baselineSiteVersion':json.loads(git('show',baseline+':site/package.json'))['version'],'trackedFilesChecked':count,'changedFiles':changed};assert not changed,changed
            assert sha(D/'source-sha256.json')==report['productionManifestSHA256'];report['productionManifestFileUnchanged']=True
            report.update(status='passed',completedAtUTC=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            report.update(status='failed',error=repr(exc),completedAtUTC=datetime.now(timezone.utc).isoformat());raise
        finally:browser.close();save()


if __name__=='__main__':main()
