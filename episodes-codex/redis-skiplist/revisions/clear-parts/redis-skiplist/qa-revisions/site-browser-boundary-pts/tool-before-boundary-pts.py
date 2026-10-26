#!/usr/bin/env python3
"""Bounded local browser QA for the EP40 first-transition revision. Does not build, copy or publish."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import importlib.metadata
import json
import re
from pathlib import Path
import shutil
import subprocess
import traceback
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright


ROOT = Path('/workspace/video-studio').resolve()
D = Path(__file__).resolve().parents[1]
O = ROOT/'episodes-codex/redis-skiplist'
OLD_RUNTIME_COMMIT = '656b525f533037f1c0dff6383c4afa69926e612c'
SLUG = 'redis-skiplist'
CHAPTER_IDS = ['goal', 'search', 'insert', 'boundary']
COURSE_SLUGS = ['consistent-hashing', 'bloom-filter', SLUG]
COURSE_HREFS = [f'/video-studio/episodes/{slug}/' for slug in COURSE_SLUGS]
EXPECTED_BODY_FRAMES = 4482
VIEWPORTS = [('desktop', {'width': 1440, 'height': 1000}),
             ('narrow', {'width': 390, 'height': 844})]


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT)


SEEK = """async ({time, fps, expectedFrame}) => {
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
    requestedFrame:expectedFrame,paintedFrame:Math.round(frame.mediaTime*fps),
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
    assert body == EXPECTED_BODY_FRAMES, 'Unexpected reviewed body frame count'
    assert meta['referenceAppendix']['from'] == body
    assert meta['finalVideoFrames'] == body + meta['referenceAppendix']['durationInFrames']
    chapters, cues = [], []
    for scene in sb['scenes']:
        for shot in scene['shots']:
            if not chapters or chapters[-1]['id'] != shot['chapterId']:
                chapters.append({'id': shot['chapterId'], 'title': article_titles(ROOT/'episodes'/SLUG/'article.mdx')[shot['chapterId']], 'start': shot['from'] / fps})
            for cue in shot['subtitles']:
                start = shot['from'] + cue['from']; end = shot['from'] + cue['to'] + 1
                start_ms = (2 * start * 1000 + fps) // (2 * fps)
                end_ms = ((end * 1000 + fps - 1) // fps - 1) if end == body else (2 * end * 1000 + fps) // (2 * fps)
                cues.append({'text': cue['text'], 'startMS': start_ms, 'endMS': end_ms})
    assert [c['id'] for c in chapters] == CHAPTER_IDS and len(cues) == 20
    return fps, body, chapters, cues


def article_titles(path):
    front=Path(path).read_text().split('---',2)[1]
    rows=re.findall(r'^\s*-\s*\{\s*id:\s*([^,]+),\s*title:\s*(.*?)\s*\}',front,re.MULTILINE)
    result={key.strip():title.strip().strip('"\'') for key,title in rows}
    assert list(result)==CHAPTER_IDS
    return result


def phase_frames(sb):
    shots={s['id']:s for scene in sb['scenes'] for s in scene['shots']}
    return [('linear-complete',shots['02']['from']+shots['02']['durationInFrames']-25,False),
            ('bridge-first',shots['03']['from'],True),
            ('upper-growing',shots['03']['from']+105,False),
            ('upper-ready',shots['03']['from']+307,False),
            ('requery-first',shots['04']['from'],True)]


def protection():
    path=D/'qa-revision-baseline-protection.json';b=read(path)
    assert b['originalTopLevelFileCount']==492 and b['existingPublishedFileCount']==878
    allowed={'episodes/'+SLUG+'/'+n for n in ['article.mdx','script.md','research.md','storyboard.json','video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','references.json','reference-appendix.json','reference-appendix-media-check.json','meta.json']}
    changed=[];protected=[]
    for name,expected in b['originalTopLevelFiles'].items():
        assert sha(ROOT/name)==expected, 'Historical original source changed: '+name
    for name,expected in b['existingPublishedFiles'].items():
        current=sha(ROOT/name)
        if current!=expected:
            assert name in allowed,'Non-whitelisted published change: '+name
            changed.append(name)
        else:protected.append(name)
    slugs={name.split('/')[1] for name in b['existingPublishedFiles']}
    tracked={p for p in git('ls-files','--','episodes').decode().splitlines() if len(p.split('/'))>2 and p.split('/')[1] in slugs and (ROOT/p).is_file()}
    assert tracked==set(b['existingPublishedFiles']), 'Published tracked file membership changed'
    untracked=[p for p in git('ls-files','--others','--exclude-standard','--','episodes').decode().splitlines() if len(p.split('/'))>2 and p.split('/')[1] in slugs]
    assert not untracked,untracked
    return {'baseline':b['baselineSHA'],'proofSHA256':sha(path),'historicalFilesChecked':492,'publishedFilesChecked':878,'otherPublishedFilesProtected':len([p for p in protected if p not in allowed]),'allowedWhitelist':sorted(allowed),'changedWhitelistedFiles':changed,'unexpectedChanges':[],'trackedFileMembershipExact':True}


def reuse_proof(published):
    old_path=O/'qa-site-browser.json';old=read(old_path)
    assert old['status']=='passed' and old['localSiteReviewComplete'] and len(old['viewports'])==2
    assert sha(published/'article.mdx')==sha(D/'article.mdx')==old['inputs']['episodes/redis-skiplist/article.mdx']
    assert sha(D/'references.json')==old['inputs']['episodes/redis-skiplist/references.json']
    runtime_names=['site/src/components/CodeBlock.astro','site/src/components/ChapterHeading.astro','site/src/components/ChapterHeading3.astro','site/src/components/Toc.astro','site/src/components/Figure.astro','site/src/pages/episodes/[slug]/index.astro','site/src/styles/global.css','site/src/layouts/BaseLayout.astro']
    runtime={}
    for name in runtime_names:
        expected=digest(git('show',OLD_RUNTIME_COMMIT+':'+name));actual=sha(ROOT/name)
        assert actual==expected,'Article runtime changed: '+name
        runtime[name]=actual
    current=read(ROOT/'site/package-lock.json');previous=json.loads(git('show',OLD_RUNTIME_COMMIT+':site/package-lock.json'))
    current.pop('version');previous.pop('version');current['packages'][''].pop('version');previous['packages'][''].pop('version')
    assert current==previous,'Dependency lock changed beyond root package version'
    covers=read(O/'qa-covers.json');binding=read(O/'qa-covers-metadata-binding.json')
    assert covers['status']==binding['status']=='passed' and binding['sixImageSHA256AllMatchViewedFirstPass']
    for row in covers['images']:
        assert sha(O/row['file'])==sha(D/row['file'])==row['sha256']
        if row['format']=='jpeg':assert sha(published/row['file'])==row['sha256']
    return {'oldLocalQA':{'path':str(old_path.relative_to(ROOT)),'sha256':sha(old_path),'originalChecks':90,'scopeReused':'Unchanged article, actual43-line code/copy/clipboard and SVG; no rerun or new DOM-copy claim.'},'articleSHA256':sha(D/'article.mdx'),'runtimeBaselineCommit':OLD_RUNTIME_COMMIT,'sameRuntimeSourceSHA256':runtime,'lockDependencyProjectionExact':True,'lockExcludedOnly':['$.version','$.packages[""].version'],'oldEnvironment':old['environment'],'coverQA':{'path':str((O/'qa-covers.json').relative_to(ROOT)),'sha256':sha(O/'qa-covers.json'),'bindingSHA256':sha(O/'qa-covers-metadata-binding.json'),'sixImagesExact':covers['images']},'originalScreenshots':[x for case in old['viewports'] for x in case['screenshots']],'articleAlgorithmExecutedAgain':False,'clipboardExecutedAgain':False,'svgDOMExecutedAgain':False}


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
        check(case, 'four chapter identities and exact starts', [{k:c[k] for k in ['id','title','start']} for c in chapters] == expected_chapters, chapters, expected_chapters)
        case['chapters'] = chapters
        video.evaluate("v=>{v.muted=true;v.textTracks[0].mode='hidden'}")
        page.wait_for_function("()=>{const t=document.querySelector('#player video').textTracks[0];return t&&t.cues&&t.cues.length===20}")
        actual_cues = video.evaluate("v=>[...v.textTracks[0].cues].map(c=>({text:c.text,startMS:Math.round(c.startTime*1000),endMS:Math.round(c.endTime*1000),start:c.startTime,end:c.endTime}))")
        check(case, '20 native VTT texts and exact millisecond boundaries', [{k:c[k] for k in ['text','startMS','endMS']} for c in actual_cues] == expected_cues, actual_cues, expected_cues)
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
        case['transitionPauses']=[]
        for label,frame,boundary in phase_frames(sb):
            paused=page.evaluate(SEEK,{'time':frame/fps+(0 if boundary else .5/fps),'fps':fps,'expectedFrame':frame})
            paused.update(name=label,boundary=boundary);case['transitionPauses'].append(paused)
            check(case,'exact painted transition '+label,paused['paused'] and paused['paintedFrame']==frame and paused['error'] is None,paused)
            screenshot(page,video,out,name+'-transition-'+label,case)
        paused=page.evaluate(SEEK,{'time':body/fps,'fps':fps,'expectedFrame':body});case['firstReferencePause']=paused
        check(case,'exact first-reference4482 and no native cue',paused['paused'] and paused['paintedFrame']==body and not paused['activeCues'] and paused['error'] is None,paused)
        video.hover();screenshot(page,video,out,name+'-references-first-exact',case)
        # A genuine API request under a trusted click; no claim of clicking browser chrome.
        page.evaluate("""()=>{const b=document.createElement('button');b.id='qa-enter-native-fullscreen';b.textContent='Fullscreen QA';
          b.style.cssText='position:fixed;z-index:99999;left:4px;top:4px';b.onclick=()=>{window.__qaFullscreenError=null;document.querySelector('#player video').requestFullscreen().catch(e=>window.__qaFullscreenError=String(e))};document.body.append(b)}""")
        page.locator('#qa-enter-native-fullscreen').click()
        page.wait_for_function("()=>document.fullscreenElement===document.querySelector('#player video')||window.__qaFullscreenError")
        if viewport['width']==390: page.set_viewport_size({'width':844,'height':390})
        full_frame=body+min(76,meta['referenceAppendix']['durationInFrames']-1)
        full_pause=page.evaluate(SEEK,{'time':(full_frame+.5)/fps,'fps':fps,'expectedFrame':full_frame})
        fullscreen=video.evaluate("v=>({active:document.fullscreenElement===v,enabled:document.fullscreenEnabled,error:window.__qaFullscreenError,rect:{width:v.getBoundingClientRect().width,height:v.getBoundingClientRect().height},viewport:{width:innerWidth,height:innerHeight}})")
        fullscreen.update(pause=full_pause,invocation='QA-only button click invoking real video.requestFullscreen()',viewportSimulation='Headless landscape viewport, not physical rotation' if viewport['width']==390 else 'Desktop viewport');case['fullscreen']=fullscreen
        check(case,'real native fullscreen API entered with paused reference frame',fullscreen['active'] and fullscreen['error'] is None and full_pause['paused'] and full_pause['paintedFrame']==full_frame and not full_pause['activeCues'] and full_pause['error'] is None,fullscreen)
        full_path=out/(name+'-references-fullscreen.png');page.screenshot(path=str(full_path));case['screenshots'].append({'path':str(full_path.relative_to(ROOT)),'sha256':sha(full_path)})
        page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.set_viewport_size(viewport)
        page.locator('#qa-enter-native-fullscreen').evaluate('b=>b.remove()')
        video.evaluate('(v,modes)=>[...v.textTracks].forEach((t,i)=>t.mode=modes[i])',state['defaultModes'])

        source_url='https://github.com/linhongcun/video-studio/tree/main/'+meta['sourcePath']
        check(case,'new nested production-source link',page.locator('a[href="'+source_url+'"]').count()==1,source_url)
        dates=page.locator('header.eh time').evaluate_all('els=>els.map(e=>e.dateTime)')
        check(case,'content dates match current publication metadata',meta['createdAt'] in dates and meta['updatedAt'] in dates,dates)
        check(case,'footer candidate patch version',args.version in page.locator('footer.ftr').inner_text())
        dimensions=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
        check(case,'no document horizontal overflow',dimensions['document']<=viewport['width'] and dimensions['body']<=viewport['width'],dimensions)
        case['reusedArticleCodeSVGAndCovers']='See top-level reuseProof; these interactions were not rerun.'
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
    parser.add_argument('--first-release',default='v0.72.0',help='Confirmed first release for this new episode')
    parser.add_argument('--report',type=Path,default=D/'qa-site-browser.json')
    parser.add_argument('--out-dir',type=Path,default=D/'qa-site-browser-evidence')
    args=parser.parse_args();assert urlparse(args.base_url).hostname in ['127.0.0.1','localhost','::1'],'This QA tool only opens local preview URLs'
    assert args.base_url.endswith('/') and args.report.resolve().is_relative_to(D) and args.out_dir.resolve().is_relative_to(D)
    assert read(ROOT/'site/package.json')['version']==args.version.removeprefix('v')
    published=ROOT/'episodes'/SLUG;meta=read(published/'meta.json');sb=read(published/'storyboard.json')
    assert meta['draft'] is False and meta['ep']==40 and meta['firstRelease']==args.first_release and sb==read(D/'storyboard.json')
    assert sha(published/'article.mdx') == sha(D/'article.mdx')
    baseline_protection=protection()
    reuse=reuse_proof(published)
    startup=read(D/'startup.json')
    for key in ['createdAt','publishedAt','firstRelease']:assert meta[key]==startup[key], 'Retain historical publication identity: '+key
    assert meta['sourcePath']==str(D.relative_to(ROOT))+'/remotion'
    assert sha(published/'video.mp4')==sha(D/'video.mp4')
    assert sha(published/'video.mp4')!=read(D/'qa-revision-baseline-protection.json')['existingPublishedFiles']['episodes/redis-skiplist/video.mp4']
    old_cues=[{k:x[k] for k in ['text','startMS','endMS']} for x in read(O/'qa-site-browser.json')['viewports'][0]['nativeCues']]
    assert expected_data(meta,sb)[3]==old_cues
    expected_data(meta,sb)
    assert (D/'source-sha256.json').is_file(), 'Wait for freeze and publication copy before browser QA'
    report={'schemaVersion':1,'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'baseURL':args.base_url,'version':args.version,
        'scope':'Bounded revision browser QA: new-media identity/playback, existing article-priority chapter titles and exact starts,20 original cues, five exact painted transition states,4482 references and nativeFullscreen; unchanged article/code/SVG/covers are reused by exact source/runtime evidence.',
        'limitations':['390px/landscape viewports are headless desktop Chromium, not physical phone or device rotation.','Short muted playback does not establish full-film listening or ASR; no repeated article/copy/SVG/entry90-check matrix.','Actual Release/changelog check runs separately after Release-following public deployment.'],
        'script':{'path':__file__,'sha256':sha(__file__)},'productionManifestSHA256':sha(D/'source-sha256.json'),'reuseProof':reuse,'baselineProtectionBefore':baseline_protection,'publicationIdentity':{k:meta[k] for k in ['createdAt','publishedAt','firstRelease','updatedAt','sourcePath']},'environment':{'python':shutil.which('python3'),'playwright':importlib.metadata.version('playwright'),'chromium':shutil.which('chromium')},'inputs':{},'viewports':[]}
    for filename in ['meta.json','article.mdx','storyboard.json','video.mp4','cover-16x9.jpg','references.json','reference-appendix.json']:
        p=published/filename;report['inputs'][str(p.relative_to(ROOT))]=sha(p)
    def save():args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if args.report.exists():
        archive=D/'qa-revisions/site-browser';archive.mkdir(parents=True,exist_ok=True);previous=archive/('previous-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');shutil.copyfile(args.report,previous);report['previousReportArchived']=str(previous.relative_to(ROOT))
    args.out_dir.mkdir(parents=True,exist_ok=True);save()
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
        report['environment']['browserVersion']=browser.version
        assert browser.version==reuse['oldEnvironment']['browserVersion'] and importlib.metadata.version('playwright')==reuse['oldEnvironment']['playwright'], 'Browser runtime changed; reassess reuse'
        try:
            for name,viewport in VIEWPORTS:
                case=run_case(browser,args,name,viewport,meta,sb,args.out_dir);report['viewports'].append(case);save();print(name,case['status'],len(case['checks']),'checks',flush=True)
                if case['status']!='passed':raise AssertionError(case['error'])
            report['baselineProtectionAfter']=protection()
            assert sha(D/'source-sha256.json')==report['productionManifestSHA256'];report['productionManifestFileUnchanged']=True
            report.update(status='passed',completedAtUTC=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            report.update(status='failed',error=repr(exc),completedAtUTC=datetime.now(timezone.utc).isoformat());raise
        finally:browser.close();save()


if __name__=='__main__':main()
