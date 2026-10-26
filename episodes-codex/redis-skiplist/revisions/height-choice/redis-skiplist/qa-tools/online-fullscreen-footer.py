from pathlib import Path
import hashlib, importlib.util, json, os, shutil, time
from datetime import datetime, timezone
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

D=Path('/workspace/video-studio/episodes-codex/redis-skiplist/revisions/height-choice/redis-skiplist')
spec=importlib.util.spec_from_file_location('height_choice_frozen_qa',D/'qa-tools/site-browser.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT
BASE='https://linhongcun.github.io/video-studio/'
URL=BASE+'episodes/redis-skiplist/'
OUT=D/'qa-online-browser-evidence'
report={'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'episodeRelease':'v0.76.2','deployedSiteVersion':'0.77.0','deploymentRun':40339259076,'deployedHead':'0cd74b3b622ae1aa80516a6c24c4ea45b0fc3e98','runtimeRef':'169cb0c09b16efdc4b5740452c2b225b5e30e841','videoSHA256':'0edf23150bb3a3a00950ebb99547e09e9ede6ba9326e22d46e73d5e2e50f24f9','manifestSHA256':'c2607a0506a616bca777fa90af111ad092856995bb40fe344afcffd65e781813','toolSHA256':m.sha(__file__),'originalSiteToolSHA256':m.sha(D/'qa-tools/site-browser.py'),'originalOnlineToolSHA256':m.sha(D/'qa-tools/online-browser.py'),'originalOnlineReportSHA256':m.sha(D/'qa-online-browser.json'),'limitations':['Headless Chromium viewport/touch emulation; not physical phones.','Supplement only: native fullscreen and actual deployed footer; original 83-check online report is kept unchanged.','Muted selected-frame playback; no semantic full-film audio review.'],'cases':[]}
path=D/'qa-online-fullscreen-footer.json'
def save():path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
save()
assert os.environ.get('SSL_CERT_FILE') and Path(os.environ['SSL_CERT_FILE']).is_file()
launch={'executable_path':shutil.which('chromium'),'headless':True,'args':['--no-sandbox'],'proxy':m.module('height_choice_proxy',m.ONLINE_HELPER).inherited_proxy()}
with sync_playwright() as pw:
    browser=pw.chromium.launch(**launch)
    report['browserVersion']=browser.version
    try:
        for name,viewport in m.VIEWPORTS:
            case={'name':name+'-dark','viewport':viewport,'checks':[],'screenshots':[],'pageErrors':[],'consoleErrors':[],'requestFailures':[]}
            report['cases'].append(case)
            ctx=browser.new_context(viewport=viewport,color_scheme='dark',reduced_motion='reduce',ignore_https_errors=False,has_touch=viewport['width']<768,is_mobile=viewport['width']<768)
            page=ctx.new_page();page.set_default_timeout(20000)
            page.on('pageerror',lambda e:case['pageErrors'].append(str(e)))
            page.on('console',lambda e:case['consoleErrors'].append(e.text) if e.type=='error' else None)
            page.add_init_script("window.__supplementEvents=[];for(const type of ['loadedmetadata','suspend','seeking','seeked','error'])document.addEventListener(type,e=>{const v=e.target;if(v.tagName==='VIDEO')window.__supplementEvents.push({type,epochMS:performance.timeOrigin+performance.now(),preload:v.preload,error:v.error?.message??null})},true)")
            phase={'name':'navigation','since':time.time()*1000}
            def failed(req):
                case['requestFailures'].append({'url':req.url,'resourceType':req.resource_type,'range':req.headers.get('range'),'failure':req.failure,'phase':phase['name'],'since':phase['since'],'epochMS':time.time()*1000})
            page.on('requestfailed',failed)
            res=page.goto(URL,wait_until='networkidle',timeout=60000)
            m.check(case,'canonical page HTTP200',res.status==200 and page.url==URL)
            page.locator('.theme-trigger').click();page.locator('[data-theme-opt="dark"]').click()
            page.wait_for_function('()=>document.documentElement.dataset.theme==="dark"')
            page.wait_for_function('()=>document.querySelector("#player video")?.readyState>=2')
            footer=page.locator('footer.ftr');m.stable(footer)
            text=footer.inner_text();case['footerText']=text
            m.check(case,'actual deployed site footer v0.77.0', 'v0.77.0' in text and '学习系列' in text and 'GitHub 源码' in text)
            p=OUT/(name+'-dark-footer-v0770.png');footer.screenshot(path=str(p));case['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':m.sha(p)})
            page.locator('#player video').evaluate('v=>{v.pause();v.muted=true;v.textTracks[0].mode="hidden"}')
            m.stable(page.locator('#player'))
            phase.update(name='fullscreen-seek',since=time.time()*1000)
            page.evaluate("()=>{const b=document.createElement('button');b.id='qa-native-fullscreen-supplement';b.style.cssText='position:fixed;top:0;left:0;z-index:99999';b.textContent='QA fullscreen';b.onclick=()=>document.querySelector('#player video').requestFullscreen();document.body.append(b)}")
            page.locator('#qa-native-fullscreen-supplement').click()
            page.wait_for_function('()=>document.fullscreenElement===document.querySelector("#player video")')
            m.check(case,'trusted click enters native Fullscreen API',page.evaluate('document.fullscreenElement===document.querySelector("#player video")'))
            if viewport['width']==390:page.set_viewport_size({'width':844,'height':390})
            frame=4633
            pause=page.evaluate(m.SEEK,{'time':(frame+.5)/30,'fps':30,'expectedFrame':frame});case['fullscreenPause']=pause
            m.check(case,'native fullscreen strict4633 and no cue',pause['paintedFrame']==frame and pause['paused'] and pause['error'] is None and not pause['activeCues'],pause)
            case['successfulWitness']={'epochMS':time.time()*1000,**page.locator('#player video').evaluate('v=>({readyState:v.readyState,error:v.error?.message??null})')}
            p=OUT/(name+'-dark-online-native-fullscreen.png');page.screenshot(path=str(p));case['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':m.sha(p)})
            page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.set_viewport_size(viewport)
            m.check(case,'native fullscreen exits to page',page.evaluate('!document.fullscreenElement'))
            case['mediaEvents']=page.evaluate('window.__supplementEvents');case['expectedMediaCancellations']=[];case['unexpectedRequestFailures']=[]
            for f in case['requestFailures']:
                later=case['successfulWitness'];events=case['mediaEvents']
                exact=f['url']==URL+'video.mp4' and f['resourceType']=='media' and bool(f['range']) and f['failure']=='net::ERR_ABORTED'
                seeks=[e for e in events if e['type']=='seeking' and e['error'] is None and f['since']-100<=e['epochMS']<=f['epochMS']+100]
                before=[e for e in events if e['epochMS']<=f['epochMS']+100 and e['error'] is None]
                preload=f['phase']=='navigation' and any(e['type']=='loadedmetadata' for e in before) and any(e['type']=='suspend' and e['preload']=='metadata' for e in before)
                if exact and later['epochMS']>f['epochMS'] and later['readyState']>=2 and later['error'] is None and ((f['phase']=='fullscreen-seek' and seeks) or preload):case['expectedMediaCancellations'].append({**f,'seekEvidence':seeks,'preloadMetadataEvidence':before if preload else [],'subsequentSuccessfulWitness':later})
                else:case['unexpectedRequestFailures'].append(f)
            m.check(case,'no unexpected network or JavaScript error',not case['unexpectedRequestFailures'] and not case['pageErrors'] and not case['consoleErrors'])
            case['status']='passed';page.remove_listener('requestfailed',failed);ctx.close();save();print(case['name'],case['status'],len(case['checks']),flush=True)
        report['status']='passed';report['completedAtUTC']=datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        report['status']='failed';report['error']=repr(exc);raise
    finally:browser.close();save()
