#!/usr/bin/env python3
"""Small canonical Pages browser smoke. Run only after confirmed deployment success.

Uses the configured session proxy and normal certificate verification. No local
site build/copy, explicit cache headers, query cache-busting, or automatic retry.
Does not replace full-file canonical HTTP identity checks or the local86 checks.
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
import urllib.request
from urllib.parse import urlsplit,unquote

from playwright.sync_api import sync_playwright


ROOT=Path('/workspace/video-studio').resolve()
D=ROOT/'episodes-codex/bloom-filter'
URL='https://linhongcun.github.io/video-studio/episodes/bloom-filter/'
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


def run_case(browser,name,viewport,meta,sb,out):
    case={'name':name,'viewport':viewport,'chapterSeeks':[],'screenshots':[],
          'pageErrors':[],'consoleErrors':[],'requestFailures':[]}
    context=browser.new_context(viewport=viewport,device_scale_factor=1,color_scheme='dark',
                               reduced_motion='reduce',ignore_https_errors=False)
    page=context.new_page();page.set_default_timeout(20000)
    page.on('pageerror',lambda e:case['pageErrors'].append(str(e)))
    page.on('console',lambda m:case['consoleErrors'].append(m.text) if m.type=='error' else None)
    page.on('requestfailed',lambda r:case['requestFailures'].append({'url':r.url,'failure':r.failure}))
    try:
        response=page.goto(URL,wait_until='networkidle',timeout=60000)
        assert response.status==200 and page.url==URL
        case.update(documentStatus=response.status,finalURL=page.url,title=page.locator('header.eh h1').inner_text())
        assert case['title']==meta['title']
        page.wait_for_function("()=>{const v=document.querySelector('#player video');return v&&v.readyState>=1&&Number.isFinite(v.duration)}")
        video=page.locator('#player video');state=video.evaluate("v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,source:v.currentSrc,controls:v.controls,defaultTrackModes:[...v.textTracks].map(t=>t.mode),error:v.error?.message??null})")
        assert state['source']==URL+meta['video'] and (state['width'],state['height'])==(1920,1080)
        assert abs(state['duration']-meta['finalVideoFrames']/sb['meta']['fps'])<.01
        assert state['controls'] and state['error'] is None;case['media']=state
        video.evaluate('v=>{v.muted=true;v.playbackRate=1;return v.play()}')
        page.wait_for_function("()=>document.querySelector('#player video').currentTime>.25")
        case['shortPlayback']=video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,muted:v.muted,rate:v.playbackRate}}')
        assert case['shortPlayback']['time']>.25 and case['shortPlayback']['paused'] and case['shortPlayback']['rate']==1
        player_path=out/(name+'-player.png');page.locator('#player').screenshot(path=str(player_path));case['screenshots'].append({'path':str(player_path.relative_to(ROOT)),'sha256':sha(player_path)})
        chapters=page.locator('#player').evaluate('e=>JSON.parse(e.dataset.chapters)')
        assert [c['id'] for c in chapters]==['goal','write','query','boundary']
        for chapter in chapters:
            kind='.ch' if viewport['width']>=768 else '.chip';page.locator(f'#player {kind}[data-id="{chapter["id"]}"]').click()
            page.wait_for_function('(t)=>{const v=document.querySelector("#player video");return !v.seeking&&v.currentTime>=t&&v.currentTime<t+.5}',arg=chapter['start'])
            sample=video.evaluate('v=>{v.pause();return {time:v.currentTime,paused:v.paused,error:v.error?.message??null}}');sample.update(id=chapter['id'],expected=chapter['start']);assert sample['paused'] and sample['error'] is None and abs(sample['time']-chapter['start'])<.5;case['chapterSeeks'].append(sample)
        video.evaluate('v=>v.textTracks[0].mode="showing"');page.wait_for_function('()=>document.querySelector("#player video").textTracks[0].cues?.length===26')
        cues=video.evaluate('v=>({count:v.textTracks[0].cues.length,lastEnd:v.textTracks[0].cues[v.textTracks[0].cues.length-1].endTime})');case['nativeCaptions']=cues
        frame=meta['referenceAppendix']['from'];fps=sb['meta']['fps'];assert frame==sb['meta']['durationInFrames'] and cues['lastEnd']<frame/fps
        pause=page.evaluate(FIRST_CARD,{'time':frame/fps,'frame':frame,'fps':fps});assert pause['paused'] and pause['paintedFrame']==frame and not pause['activeCues'] and pause['error'] is None;case['firstReferencePause']=pause
        video.hover();card_path=out/(name+'-references-first.png');video.screenshot(path=str(card_path));case['screenshots'].append({'path':str(card_path.relative_to(ROOT)),'sha256':sha(card_path)})
        case['dimensions']=page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})');assert case['dimensions']['document']<=viewport['width']
        assert not case['pageErrors'] and not case['consoleErrors'] and not case['requestFailures']
        case['status']='passed'
    except Exception as exc:
        case.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
    finally:context.close()
    return case


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',required=True)
    parser.add_argument('--deployment-run',required=True,type=int)
    args=parser.parse_args()
    policy=read('/etc/codex/network-policy.json');assert policy['version']==1
    hosts=[r['host'] for r in policy['http_network_policy']['egress_rules']];assert 'linhongcun.github.io' in hosts
    proxy=inherited_proxy();assert shutil.which('chromium')
    assert os.environ.get('SSL_CERT_FILE') and Path(os.environ['SSL_CERT_FILE']).is_file()
    meta=read(ROOT/'episodes/bloom-filter/meta.json');sb=read(ROOT/'episodes/bloom-filter/storyboard.json')
    assert meta['draft'] is False and meta['firstRelease']==args.release and meta['ep']==39
    report={'schemaVersion':1,'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),
        'page':URL,'release':args.release,'deploymentRun':args.deployment_run,
        'scope':'Small actual canonical Chromium smoke only: short muted1x playback, four real chapter clicks and exact first-reference pause in desktop/narrow viewports.',
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
