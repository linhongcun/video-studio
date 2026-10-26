#!/usr/bin/env python3
"""Small canonical Pages browser smoke. Run only after confirmed deployment success.

Uses the configured session proxy and normal certificate verification. No local
site build/copy, explicit cache headers, query cache-busting, or automatic retry.
Does not replace full-file canonical HTTP identity checks or the separate local built-site checks.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import traceback
import time
import urllib.request
from urllib.parse import urlsplit,unquote

from playwright.sync_api import sync_playwright


ROOT=Path('/workspace/video-studio').resolve()
D=Path(__file__).resolve().parents[1]
SLUG='redis-skiplist'
URL=f'https://linhongcun.github.io/video-studio/episodes/{SLUG}/'
CHAPTER_IDS=['goal','search','insert','boundary']
EXPECTED_BODY_FRAMES=4482
VIEWPORTS=[('desktop',{'width':1440,'height':1000}),('narrow',{'width':390,'height':844})]


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inherited_proxy():
    values=urllib.request.getproxies();raw=values.get('https') or values.get('http')
    assert raw,'Keep the configured session proxy; direct fallback is not permitted'
    parsed=urlsplit(raw);assert parsed.scheme in ['http','https'] and parsed.hostname
    host=('['+parsed.hostname+']') if ':' in parsed.hostname else parsed.hostname
    proxy={'server':parsed.scheme+'://'+host+(':'+str(parsed.port) if parsed.port else '')}
    if parsed.username is not None:proxy['username']=unquote(parsed.username)
    if parsed.password is not None:proxy['password']=unquote(parsed.password)
    return proxy


FIRST_CARD="""async ({time,frame,fps})=>{
 const v=document.querySelector('#player video');v.pause();
 const painted=new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('No painted reference frame')),10000);
   v.requestVideoFrameCallback((now,info)=>{clearTimeout(t);resolve({mediaTime:info.mediaTime,presentedFrames:info.presentedFrames})})});
 const sought=new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('Reference seek timeout')),10000);
   v.addEventListener('seeked',()=>{clearTimeout(t);resolve()},{once:true})});
 v.currentTime=time;await sought;const actual=await painted;
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 return {requestedTime:time,requestedFrame:frame,currentTime:v.currentTime,painted:actual,
   paintedFrame:Math.round(actual.mediaTime*fps),paused:v.paused,readyState:v.readyState,
   activeCues:[...v.textTracks].flatMap(t=>[...(t.activeCues||[])].map(c=>c.text)),error:v.error?.message??null};
}"""


def expected_data(meta,sb):
    fps=sb['meta']['fps'];body=sb['meta']['durationInFrames'];chapters=[];cues=[]
    assert body==EXPECTED_BODY_FRAMES and meta['referenceAppendix']['from']==body
    for scene in sb['scenes']:
        for shot in scene['shots']:
            if not chapters or chapters[-1]['id']!=shot['chapterId']:
                chapters.append({'id':shot['chapterId'],'start':shot['from']/fps})
            for cue in shot['subtitles']:
                start=shot['from']+cue['from'];end=shot['from']+cue['to']+1
                start_ms=(2*start*1000+fps)//(2*fps)
                end_ms=((end*1000+fps-1)//fps-1) if end==body else (2*end*1000+fps)//(2*fps)
                cues.append({'text':cue['text'],'startMS':start_ms,'endMS':end_ms})
    assert [c['id'] for c in chapters]==CHAPTER_IDS and len(cues)==20
    return chapters,cues


def run_case(browser,name,viewport,meta,sb,out):
    case={'name':name,'viewport':viewport,'chapterSeeks':[],'screenshots':[],
          'pageErrors':[],'consoleErrors':[],'requestFailures':[],'mediaWitnesses':[]}
    phase={'name':'navigation','sinceEpochMS':time.time()*1000};requests={}
    context=browser.new_context(viewport=viewport,device_scale_factor=1,color_scheme='dark',
                               reduced_motion='reduce',ignore_https_errors=False)
    page=context.new_page();page.set_default_timeout(20000)
    page.on('pageerror',lambda e:case['pageErrors'].append(str(e)))
    page.on('console',lambda m:case['consoleErrors'].append(m.text) if m.type=='error' else None)
    page.add_init_script('''window.__qaMediaEvents=[];for(const type of ['loadstart','loadedmetadata','loadeddata','canplay','suspend','abort','error','seeking','seeked','playing','pause'])document.addEventListener(type,e=>{const v=e.target;if(v.tagName==='VIDEO')window.__qaMediaEvents.push({type,epochMS:performance.timeOrigin+performance.now(),time:v.currentTime,readyState:v.readyState,networkState:v.networkState,preload:v.preload,error:v.error?.message??null})},true)''')
    def on_request(request):
        requests[request]={'url':request.url,'resourceType':request.resource_type,'range':request.headers.get('range'),'startedPhase':phase['name'],'startedAtEpochMS':time.time()*1000}
    def on_failed(request):
        case['requestFailures'].append({**requests.get(request,{'url':request.url,'resourceType':request.resource_type,'range':request.headers.get('range')}),'failure':request.failure,'failedPhase':phase['name'],'failedPhaseSinceEpochMS':phase['sinceEpochMS'],'failedAtEpochMS':time.time()*1000})
    page.on('request',on_request);page.on('requestfailed',on_failed)
    try:
        response=page.goto(URL,wait_until='networkidle',timeout=60000)
        assert response.status==200 and page.url==URL
        case.update(documentStatus=response.status,finalURL=page.url,title=page.locator('header.eh h1').inner_text())
        assert case['title']==meta['title']
        page.wait_for_function("()=>{const v=document.querySelector('#player video');return v&&v.readyState>=1&&Number.isFinite(v.duration)}")
        video=page.locator('#player video');state=video.evaluate("v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,source:v.currentSrc,controls:v.controls,preload:v.preload,defaultTrackModes:[...v.textTracks].map(t=>t.mode),error:v.error?.message??null})")
        assert state['source']==URL+meta['video'] and (state['width'],state['height'])==(1920,1080)
        assert abs(state['duration']-meta['finalVideoFrames']/sb['meta']['fps'])<.01
        assert state['controls'] and state['error'] is None;case['media']=state
        phase['name']='short-playback';phase['sinceEpochMS']=time.time()*1000
        video.evaluate('v=>{v.muted=true;v.playbackRate=1;return v.play()}')
        page.wait_for_function("()=>document.querySelector('#player video').currentTime>.25")
        case['shortPlayback']=video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,muted:v.muted,rate:v.playbackRate,error:v.error?.message??null,readyState:v.readyState}}')
        assert case['shortPlayback']['time']>.25 and case['shortPlayback']['paused'] and case['shortPlayback']['rate']==1
        case['mediaWitnesses'].append({'type':'successful-short-playback','atEpochMS':time.time()*1000,**case['shortPlayback']})
        player_path=out/(name+'-player.png');page.locator('#player').screenshot(path=str(player_path));case['screenshots'].append({'path':str(player_path.relative_to(ROOT)),'sha256':sha(player_path)})
        chapters=page.locator('#player').evaluate('e=>JSON.parse(e.dataset.chapters)')
        expected_chapters,expected_cues=expected_data(meta,sb)
        assert [{k:c[k] for k in ['id','start']} for c in chapters]==expected_chapters
        case['chapters']=chapters
        for chapter in chapters:
            phase['name']='chapter-'+chapter['id'];phase['sinceEpochMS']=time.time()*1000
            kind='.ch' if viewport['width']>=768 else '.chip';page.locator(f'#player {kind}[data-id="{chapter["id"]}"]').click()
            page.wait_for_function('(t)=>{const v=document.querySelector("#player video");return !v.seeking&&v.currentTime>=t&&v.currentTime<t+.5}',arg=chapter['start'])
            sample=video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,error:v.error?.message??null,readyState:v.readyState}}');sample.update(id=chapter['id'],expected=chapter['start']);assert sample['paused'] and sample['error'] is None and abs(sample['time']-chapter['start'])<.5;case['chapterSeeks'].append(sample)
        video.evaluate('v=>v.textTracks[0].mode="showing"');page.wait_for_function('()=>document.querySelector("#player video").textTracks[0].cues?.length===20')
        actual_cues=video.evaluate('v=>[...v.textTracks[0].cues].map(c=>({text:c.text,startMS:Math.round(c.startTime*1000),endMS:Math.round(c.endTime*1000)}))')
        assert actual_cues==expected_cues
        cues={'count':len(actual_cues),'lastEnd':actual_cues[-1]['endMS']/1000,'cues':actual_cues};case['nativeCaptions']=cues
        phase['name']='first-reference-seek';phase['sinceEpochMS']=time.time()*1000
        frame=meta['referenceAppendix']['from'];fps=sb['meta']['fps'];assert frame==sb['meta']['durationInFrames'] and cues['lastEnd']<frame/fps
        pause=page.evaluate(FIRST_CARD,{'time':frame/fps,'frame':frame,'fps':fps});assert pause['paused'] and pause['paintedFrame']==frame and not pause['activeCues'] and pause['error'] is None;case['firstReferencePause']=pause
        video.hover();card_path=out/(name+'-references-first.png');video.screenshot(path=str(card_path));case['screenshots'].append({'path':str(card_path.relative_to(ROOT)),'sha256':sha(card_path)})
        case['dimensions']=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})');assert case['dimensions']['document']<=viewport['width']
        current=video.evaluate('v=>({error:v.error?.message??null,readyState:v.readyState,time:v.currentTime})')
        assert current['error'] is None and current['readyState']>=2
        case['mediaWitnesses'].append({'type':'painted-first-reference-screenshot','atEpochMS':time.time()*1000,'paintedFrame':pause['paintedFrame'],**current})
        case['nativeMediaEvents']=page.evaluate('window.__qaMediaEvents')
        case['classifiedMediaCancellations']=[];case['unexpectedRequestFailures']=[]
        for failed in case['requestFailures']:
            witnesses=[w for w in case['mediaWitnesses'] if w['atEpochMS']>failed['failedAtEpochMS'] and w.get('error') is None and w.get('readyState',0)>=2]
            exact_media=(failed['url']==URL+meta['video'] and failed['resourceType']=='media' and failed['failure']=='net::ERR_ABORTED' and bool(failed.get('range')))
            seek_events=[e for e in case['nativeMediaEvents'] if e['type']=='seeking' and e['error'] is None and failed['failedPhaseSinceEpochMS']-100<=e['epochMS']<=failed['failedAtEpochMS']+100]
            active_seek=(failed['failedPhase'] in ['chapter-'+c for c in CHAPTER_IDS]+['first-reference-seek'] and bool(seek_events))
            metadata_events=[e for e in case['nativeMediaEvents'] if e['epochMS']<=failed['failedAtEpochMS']+100 and e['error'] is None]
            metadata_close=(failed['failedPhase'] in ['navigation','short-playback'] and state['preload']=='metadata' and any(e['type']=='loadedmetadata' for e in metadata_events) and any(e['type']=='suspend' and e['preload']=='metadata' for e in metadata_events))
            if exact_media and witnesses and (active_seek or metadata_close):
                failed.update(classification='expected-browser-managed-media-read-cancellation',reason='Old Range read cancelled during active seek' if active_seek else 'Initial preload=metadata read ended after metadata became available',subsequentSuccessfulWitness=witnesses[0],activeSeekEvidence=seek_events[-1:] if active_seek else [],metadataLifecycleEvidence=[e for e in metadata_events if e['type'] in ['loadedmetadata','suspend']] if metadata_close else [])
                case['classifiedMediaCancellations'].append(failed)
            else:
                failed['classification']='unexpected-failure';case['unexpectedRequestFailures'].append(failed)
        case['observedMediaCancellationCount']=len(case['classifiedMediaCancellations'])
        case['networkObservationEndsBeforeIntentionalContextTeardown']=True
        assert not case['pageErrors'] and not case['consoleErrors'] and not case['unexpectedRequestFailures'],case['unexpectedRequestFailures']
        case['status']='passed'
    except Exception as exc:
        case.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
    finally:
        page.remove_listener('request',on_request);page.remove_listener('requestfailed',on_failed);context.close()
    return case


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',required=True)
    parser.add_argument('--first-release',default='v0.72.0')
    parser.add_argument('--deployment-run',required=True,type=int)
    args=parser.parse_args()
    policy=read('/etc/codex/network-policy.json');assert policy['version']==1
    hosts=[r['host'] for r in policy['http_network_policy']['egress_rules']];assert 'linhongcun.github.io' in hosts
    proxy=inherited_proxy();assert shutil.which('chromium')
    assert os.environ.get('SSL_CERT_FILE') and Path(os.environ['SSL_CERT_FILE']).is_file()
    meta=read(ROOT/'episodes'/SLUG/'meta.json');sb=read(ROOT/'episodes'/SLUG/'storyboard.json')
    assert meta['draft'] is False and meta['firstRelease']==args.first_release and meta['ep']==40
    assert meta['referenceAppendix']['from']==sb['meta']['durationInFrames']==EXPECTED_BODY_FRAMES
    assert meta['finalVideoFrames']==EXPECTED_BODY_FRAMES+meta['referenceAppendix']['durationInFrames']
    assert sb==read(D/'storyboard.json')
    report={'schemaVersion':1,'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),
        'page':URL,'release':args.release,'firstRelease':meta['firstRelease'],'deploymentRun':args.deployment_run,
        'scope':'Small actual canonical Chromium smoke only: short muted1x playback, four real chapter clicks, all20 exact native cues and exact painted first-reference pause in desktop/narrow viewports.',
        'limitations':['390px is a headless desktop Chromium viewport, not a physical phone.','No full-film listening, ASR or teaching-effect claim.','Native video loading is browser-managed; full-file canonical HTTP identity checks are separate.'],
        'transport':{'explicitInheritedSessionProxy':True,'tlsVerificationEnabled':True,'ignoreHTTPSErrors':False,'customCacheHeaders':False,'cacheBusting':False,'automaticRetryCount':0,'configuredCAEnvironmentPresent':True,'policyAllowsPagesHost':True},
        'environment':{'python':shutil.which('python3'),'playwright':importlib.metadata.version('playwright'),'chromium':shutil.which('chromium')},
        'script':{'path':__file__,'sha256':sha(__file__)},'productionManifestSHA256':sha(D/'source-sha256.json'),'viewports':[]}
    path=D/'qa-online-browser.json';out=D/'qa-online-browser-evidence';out.mkdir(exist_ok=True)
    if path.exists():
        archive=D/'qa-revisions/online-browser';archive.mkdir(parents=True,exist_ok=True);saved=archive/('previous-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');shutil.copyfile(path,saved);report['previousReportArchived']=str(saved.relative_to(ROOT))
    def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    save()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,proxy=proxy,args=['--no-sandbox'])
        report['environment']['browserVersion']=browser.version
        try:
            for name,viewport in VIEWPORTS:
                case=run_case(browser,name,viewport,meta,sb,out);report['viewports'].append(case);save();print(name,case['status'],flush=True)
                assert case['status']=='passed',case.get('error')
            assert report['productionManifestSHA256']==sha(D/'source-sha256.json')
            report.update(status='passed',completedAtUTC=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            report.update(status='failed',error=repr(exc),completedAtUTC=datetime.now(timezone.utc).isoformat());raise
        finally:browser.close();save()


if __name__=='__main__':main()
