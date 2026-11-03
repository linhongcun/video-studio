#!/usr/bin/env python3
"""One canonical mobile-landscape native-control fullscreen diagnostic."""
from pathlib import Path
import base64, datetime, hashlib, json, traceback
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / 'site-online-fullscreen-targeted'
OUT.mkdir(exist_ok=True)
BASE = 'https://linhongcun.github.io/video-studio'
report = {'startedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'base': BASE, 'pass': False, 'scope': 'Only native-control mobile fullscreen landscape; not a repeat of the full primary suite.',
          'restrictions': 'No response fulfillment, TLS bypass, content injection, control hiding, CSS modification or media changes.',
          'observations': [], 'pageErrors': [], 'visualReviewed': False}

def stats(f):
    im = Image.open(f).convert('RGB')
    return {'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'size': list(im.size),
            'extrema': im.getextrema(), 'mean': ImageStat.Stat(im).mean,
            'nonBlackPixels': sum(p != (0, 0, 0) for p in im.get_flattened_data())}

STATE = '''v=>{const r=v.getBoundingClientRect();return{currentTime:v.currentTime,duration:v.duration,readyState:v.readyState,networkState:v.networkState,seeking:v.seeking,paused:v.paused,ended:v.ended,controls:v.controls,muted:v.muted,videoWidth:v.videoWidth,videoHeight:v.videoHeight,currentSrc:v.currentSrc,fullscreenElement:document.fullscreenElement?.tagName??null,fullscreenIsVideo:document.fullscreenElement===v,fullscreenEnabled:document.fullscreenEnabled,viewport:{width:innerWidth,height:innerHeight},rect:{x:r.x,y:r.y,width:r.width,height:r.height},visibility:document.visibilityState,textTracks:Array.from(v.textTracks,t=>({mode:t.mode,activeCues:t.activeCues?.length??null})),buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)])}}'''
SEEK = '''async(v,frame)=>{v.pause();return await new Promise((resolve,reject)=>{let md=null,seeked=false,handle;const timer=setTimeout(()=>reject(Error('rVFC seek timeout')),15000);function finish(){if(md&&seeked){clearTimeout(timer);resolve({mediaTime:md.mediaTime,presentedFrames:md.presentedFrames,currentTime:v.currentTime})}}function cb(t,m){if(Math.abs(m.mediaTime-frame/30)<.0000011){md=m;finish()}else handle=v.requestVideoFrameCallback(cb)}handle=v.requestVideoFrameCallback(cb);v.addEventListener('seeked',()=>{seeked=true;finish()},{once:true});v.currentTime=(frame+.5)/30})}'''

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        report['browserVersion'] = b.version
        c = b.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
        p = c.new_page(); p.set_default_timeout(20000)
        p.on('pageerror',lambda e:report['pageErrors'].append(str(e)))
        response = p.goto(BASE+'/episodes/pirate-gold/',wait_until='networkidle')
        report['initialNavigationStatus'] = response.status
        assert response.status == 200
        v = p.locator('video'); v.scroll_into_view_if_needed()
        v.evaluate('(v)=>{v.muted=true;v.preload="auto"}')
        p.wait_for_function('document.querySelector("video").readyState>=2')
        report['initialNativeTrackModes'] = v.evaluate('(v)=>Array.from(v.textTracks,t=>t.mode)')
        report['initialReferenceSeek'] = v.evaluate(SEEK,4876)

        def capture(name):
            state=v.evaluate(STATE)
            sf=OUT/(name+'.png');p.screenshot(path=str(sf))
            df=OUT/(name+'-decoded.png')
            data=v.evaluate('''v=>{const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);return c.toDataURL('image/png')}''')
            df.write_bytes(base64.b64decode(data.split(',',1)[1]))
            report['observations'].append({'phase':name,'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'screenshot':{'file':sf.name,**stats(sf)},'decodedCanvas':{'file':df.name,**stats(df)}})

        capture('01-inline-reference-before-native-fullscreen')
        # Native Chromium video control: fullscreen is immediately left of overflow.
        rect=v.bounding_box();assert rect
        x=rect['x']+rect['width']-75;y=rect['y']+rect['height']-29
        report['nativeFullscreenControlTap']={'x':x,'y':y,'videoRect':rect}
        p.touchscreen.tap(x,y)
        p.wait_for_function('document.fullscreenElement===document.querySelector("video")')
        capture('02-native-fullscreen-portrait')
        p.set_viewport_size({'width':844,'height':390})
        capture('03-landscape-immediately-after-resize')
        p.evaluate('''async()=>{let prev='',stable=0;for(let n=0;n<120;n++){await new Promise(requestAnimationFrame);const v=document.querySelector('video'),r=v.getBoundingClientRect(),key=JSON.stringify([innerWidth,innerHeight,r.x,r.y,r.width,r.height]);if(key===prev)stable++;else stable=0;prev=key;if(stable>=4)return;}throw Error('viewport not stable')}''')
        p.wait_for_timeout(750)
        capture('04-landscape-stable-750ms')
        # Seek away then back guarantees a fresh decoded-frame callback.
        v.evaluate(SEEK,4875)
        report['landscapeFreshReferenceSeek']=v.evaluate(SEEK,4876)
        p.wait_for_timeout(300)
        capture('05-landscape-after-fresh-exact-seek')
        v.evaluate(SEEK,4820)
        report['playbackStartTime']=v.evaluate('(v)=>v.currentTime')
        v.evaluate('(v)=>v.play()')
        p.wait_for_function('(start)=>document.querySelector("video").currentTime>start+.6',arg=report['playbackStartTime'])
        v.evaluate('(v)=>v.pause()')
        p.wait_for_timeout(300)
        capture('06-landscape-after-natural-playback-and-pause')
        assert all(x['state']['fullscreenIsVideo'] and x['state']['controls'] and x['state']['readyState']>=2 and not x['state']['seeking'] for x in report['observations'][1:])
        assert all(x['screenshot']['nonBlackPixels']>0 for x in report['observations'])
        p.keyboard.press('Escape');p.wait_for_function('document.fullscreenElement===null')
        report['fullscreenExited']=True;report['pass']=not report['pageErrors'];b.close()
except Exception as e:
    report['failure']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
    raise
finally:
    report['finishedAtUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pass':report['pass'],'captures':len(report['observations']),'out':str(OUT)}))
