from pathlib import Path
from html.parser import HTMLParser
import ast,json,hashlib,time,datetime
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/work/video-studio');W=ROOT/'work/leetcode-video-style/siteqa';OUT=W/'caption-final';BASE='http://127.0.0.1:4324/video-studio';CANDIDATE=(W/'caption-candidate.txt').read_text().strip()
old=json.loads((W/'final-43d662e/browser/report.json').read_text());assert old['status']=='passed'
# Reuse only the tested browser presentation waiters, not production logic.
tree=ast.parse((W/'check-final.py').read_text());namespace={};functions=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in {'visible_video','seek_paused','overflow'}];exec(compile(ast.Module(body=functions,type_ignores=[]),'previous-qa-waiters','exec'),namespace);seek=namespace['seek_paused']
slugs=old['scope'];prior={e['slug']:e for e in old['viewports'][0]['episodes']}
class Tracks(HTMLParser):
 def __init__(self):super().__init__();self.tracks=[]
 def handle_starttag(self,tag,attrs):
  if tag=='track':self.tracks.append(dict(attrs))
before=json.loads((W/'caption-before-track-defaults.json').read_text());after={}
for f in Path('/workspace/work/video-studio-sitecheck/site/dist/episodes').glob('*/index.html'):
 p=Tracks();p.feed(f.read_text());after[f.parent.name]=[{'default':'default' in t,'kind':t.get('kind'),'src':t.get('src')} for t in p.tracks]
assert set(before)==set(after)
changed=[]
for s in after:
 if s in slugs:
  assert len(after[s])==len(before[s])==1 and before[s][0]['default'] and not after[s][0]['default'];assert {k:v for k,v in after[s][0].items() if k!='default'}=={k:v for k,v in before[s][0].items() if k!='default'};changed.append(s)
 else:assert after[s]==before[s],s
assert len(changed)==11
report={'candidate':CANDIDATE,'base':BASE,'startedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorFullBrowserCandidate':old['candidate'],'priorFullReportSHA256':hashlib.sha256((W/'final-43d662e/browser/report.json').read_bytes()).hexdigest(),'reason':'Narrow default native-caption fix after a real duplicate-caption issue was seen in fullscreen screenshots. Existing full interaction/HTTP/cover checks remain valid for unchanged media and behavior.','staticTrackDefaults':{'htmlEpisodeRoutes':len(after),'changedOnlyElevenLeetCodePages':changed,'allOtherTrackDefaultsAndSourcesUnchanged':True},'views':[],'errors':[],'screenshots':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 report['chromiumVersion']=browser.version
 for width,height in [(1440,1000),(390,844)]:
  for s in slugs:
   context=browser.new_context(viewport={'width':width,'height':height});page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   response=page.goto(f'{BASE}/episodes/{s}/',wait_until='networkidle');assert response.status==200
   page.wait_for_function('()=>{const v=document.querySelector("video");return v&&v.readyState>=1&&v.textTracks.length===1}')
   initial=page.locator('video').evaluate('(v)=>({default:v.querySelector("track").default,mode:v.textTracks[0].mode,src:v.currentSrc})');assert initial['default'] is False and initial['mode']=='disabled',(s,initial)
   assert CANDIDATE in page.locator('a[href*="/revisions/leetcode-style"]').first.get_attribute('href')
   t=prior[s]['player']['bodySubtitleSeek']['time'];default=seek(page,t);assert not default['active'],(s,default)
   if width==1440 and s in ['number-of-islands','daily-temperatures']:
    page.evaluate('()=>{let b=document.createElement("button");b.id="qa-fs";b.textContent="qa fullscreen";b.style="position:fixed;top:0;left:0;z-index:99999";b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.appendChild(b)}');page.locator('#qa-fs').click();page.wait_for_function('()=>document.fullscreenElement===document.querySelector("video")');seek(page,t);page.wait_for_timeout(400);f=OUT/f'{s}-default-fullscreen-1440.png';page.screenshot(path=str(f));report['screenshots'].append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'nativeTrackMode':'disabled'});page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.locator('#qa-fs').evaluate('(e)=>e.remove()')
   page.locator('video').evaluate('(v)=>v.textTracks[0].mode="showing"');page.wait_for_function('()=>{const t=document.querySelector("video").textTracks[0];return t.cues&&t.cues.length>0}')
   enabled=seek(page,t);assert enabled['active']==prior[s]['player']['bodySubtitleSeek']['active'],(s,enabled)
   code=seek(page,prior[s]['pythonCard']['fromSeconds']+2.5);assert not code['active']
   refs=seek(page,prior[s]['references']['fromSeconds']+2.5);assert not refs['active']
   restored=seek(page,t);assert restored['active']==enabled['active']
   page.locator('video').evaluate('(v)=>v.textTracks[0].mode="disabled"');disabled=seek(page,t);assert not disabled['active'];overflow=namespace['overflow'](page);assert not errors,(s,errors)
   report['views'].append({'slug':s,'width':width,'height':height,'initial':initial,'defaultBody':default,'explicitNativeEnabledBody':enabled,'python':code,'references':refs,'restoredBody':restored,'explicitNativeDisabledBody':disabled,'overflow':overflow,'errors':errors});(OUT/'checkpoint.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'slug':s,'width':width,'status':'passed'}),flush=True);context.close()
 browser.close()
report['status']='passed';report['finishedAtUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['limits']=['Fresh Chromium contexts test publisher default; an explicit saved browser caption preference may override it.','Native track enable/disable uses the standard TextTrack API, not a claim of physical-device or native-menu manual testing.','Full media decode, hearing/ASR and canonical hosting checks were not repeated.']
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('All22 fresh defaults and explicit native-caption transitions passed.',flush=True)
