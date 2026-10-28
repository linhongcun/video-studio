"""Bounded final verification after video colour-range normalization.
Prior complete UI report is reused only for byte-identical application runtime,
article/chapters/caption inputs, cover and taxonomy metadata. New video/Figure,
player loading, colour, caption boundaries and fullscreen are exercised again.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,atexit,base64,hashlib,json,subprocess,sys
from playwright.sync_api import sync_playwright
from PIL import Image
import helpers

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--root',default='/workspace/work/video-studio-sitecheck');p.add_argument('--base',default='http://127.0.0.1:4325/video-studio');p.add_argument('--out',required=True);args=p.parse_args();root=Path(args.root);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);helpers.root=root
initial='756f115004774fc0a29086e190932ee451c07c66';priorpath=Path(__file__).parent/'browser/report.json';prior=json.loads(priorpath.read_text());assert prior['status']=='passed' and prior['candidate']==initial
report={'candidate':args.candidate,'initialCandidate':initial,'base':args.base,'startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),'priorFullUIReportSHA256':helpers.sha_file(priorpath),'httpMedia':[],'views':[],'screenshots':[],'errors':[]}
atexit.register(lambda:(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'))
def ex(kind,value,tb):report['errors'].append(str(value));sys.__excepthook__(kind,value,tb)
sys.excepthook=ex
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==args.candidate
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip()
def gitbytes(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=root)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',initial,'site/src','site/scripts','site/astro.config.mjs','episodes/redis-skiplist'],cwd=root,text=True).splitlines();changed=[];equal=[]
allowed={'episodes/redis-skiplist/video.mp4','episodes/redis-skiplist/article/height-one.jpg','episodes/redis-skiplist/meta.json','episodes/redis-skiplist/reference-appendix.json','episodes/redis-skiplist/reference-appendix-media-check.json','episodes/redis-skiplist/render-result.json'}
for path in paths:
 if helpers.git_blob(initial,path)!=helpers.git_blob(args.candidate,path):assert path in allowed,path;changed.append(path)
 else:equal.append(path)
assert 'episodes/redis-skiplist/video.mp4' in changed and 'episodes/redis-skiplist/article/height-one.jpg' in changed
oldmeta=json.loads(gitbytes(initial,'episodes/redis-skiplist/meta.json'));meta=json.loads((root/'episodes/redis-skiplist/meta.json').read_text());metachange=[k for k in set(meta)|set(oldmeta) if meta.get(k)!=oldmeta.get(k)];assert set(metachange)<={'updatedAt'}
report['boundedReuseProof']={'changedPaths':changed,'unchangedPaths':equal,'changedMetadataFields':metachange,'runtimeArticleCaptionsAndCoversUnchanged':True,'reused':'Prior full2viewport taxonomy/chapters/related/sourcequotes/keyboard/theme behavior, limited to unchanged runtime and retained inputs. No old visual or old-media result reused for corrected final.'}
D=root/'episodes/redis-skiplist';result=json.loads((D/'render-result.json').read_text());receipt=json.loads((D/'reference-appendix.json').read_text());assert result['sha256']==receipt['outputSHA256']==helpers.sha_file(D/'video.mp4');assert meta['burnedInCaptions'] is True and meta['finalVideoFrames']==4707
for f in ['video.mp4',meta['poster'],'article/height-one.jpg']:
 r=helpers.full_http_sha(args.base+'/episodes/redis-skiplist/'+f);assert r['sha256']==helpers.sha_file(D/f);report['httpMedia'].append(r)
packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',str(D/'video.mp4')],text=True));pts=sorted(float(x['pts_time']) for x in packets['packets']);assert len(pts)==4707
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(D/'video.mp4')],text=True))['streams'][0];assert probe['pix_fmt']=='yuv420p' and probe['color_range']=='tv' and probe['color_space']==probe['color_transfer']==probe['color_primaries']=='bt709';report['videoColourTags']=probe
framepng=out/'ffmpeg-height-one.png';subprocess.run(['ffmpeg','-v','error','-y','-ss','88','-i',str(D/'video.mp4'),'-vf','select=eq(n\\,27)','-frames:v','1',str(framepng)],check=True)
referencepng=out/'ffmpeg-references.png';subprocess.run(['ffmpeg','-v','error','-y','-ss','154','-i',str(D/'video.mp4'),'-vf','select=eq(n\\,12)','-frames:v','1',str(referencepng)],check=True)
expected=Image.open(framepng).getpixel((960,270));expected_refs=Image.open(referencepng).getpixel((1000,300));report['ffmpegExpectedPixels']={'heightOne':expected,'references':expected_refs}
def snap(page,name):
 helpers.overflow(page);p=out/name;page.screenshot(path=str(p));report['screenshots'].append({'file':str(p),'sha256':helpers.sha_file(p)})
def seek(page,t):
 frame=round(t*30);state=helpers.seek_paused(page,pts[frame]);assert round(state['presentedFrame']['mediaTime']*30)==frame,(t,state);state['targetFrame']=frame;return state
def canvas(page,name,coord,expected):
 d=page.locator('video').evaluate('''(v,c)=>{let s=document.createElement('canvas');s.width=v.videoWidth;s.height=v.videoHeight;let x=s.getContext('2d');x.drawImage(v,0,0);return {pixel:[...x.getImageData(c[0],c[1],1,1).data],png:s.toDataURL('image/png')}}''',coord);p=out/name;p.write_bytes(base64.b64decode(d.pop('png').split(',',1)[1]));d.update(file=str(p),sha256=helpers.sha_file(p));delta=max(abs(d['pixel'][i]-expected[i]) for i in range(3));assert delta<=3,(name,d,expected);d['maximumChannelDifferenceFromFFmpeg']=delta;return d
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']);report['chromiumVersion']=b.version
 for width,height in [(1440,1000),(390,844)]:
  ctx=b.new_context(viewport={'width':width,'height':height},reduced_motion='reduce');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  row={'width':width,'height':height};report['views'].append(row);r=page.goto(args.base+'/episodes/redis-skiplist/',wait_until='networkidle');assert r.status==200
  assert all(args.candidate in u for u in page.locator('.source-links a').evaluate_all('(as)=>as.map(a=>a.href)'));assert page.locator('.episode-version time').get_attribute('datetime')==meta['updatedAt']
  page.wait_for_function('()=>{let v=document.querySelector("video");return v.readyState>=1&&v.textTracks.length===1}')
  video=page.locator('video');vm=video.evaluate('(v)=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,trackDefault:v.querySelector("track").default,mode:v.textTracks[0].mode})');assert vm['width']==1920 and vm['height']==1080 and abs(vm['duration']-156.9)<.034;assert not vm['trackDefault'] and vm['mode']=='disabled';row['metadata']=vm
  row['heightOne']=seek(page,88.9);row['browserColour']=canvas(page,f'height-one-canvas-{width}.png',[960,270],expected);assert max(abs(row['browserColour']['pixel'][i]-[238,241,245][i]) for i in range(3))<=5
  video.evaluate('(v)=>{v.muted=true;return v.play()}');page.wait_for_function('document.querySelector("video").currentTime>89.1');page.keyboard.press('k');page.wait_for_function('document.querySelector("video").paused');row['playbackKeyboardPause']=True
  seek(page,88.9);helpers.visible_video(page);page.evaluate('()=>{let b=document.createElement("button");b.id="qa-fullscreen";b.style="position:fixed;top:0;left:0;z-index:99999";b.textContent="Fullscreen QA";b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.appendChild(b)}');page.locator('#qa-fullscreen').click();page.wait_for_function('document.fullscreenElement===document.querySelector("video")');seek(page,88.9);snap(page,f'height-one-fullscreen-{width}.png');page.evaluate('()=>document.exitFullscreen()');page.wait_for_function('()=>!document.fullscreenElement');page.locator('#qa-fullscreen').evaluate('(b)=>b.remove()');row['fullscreen']={'entered':True,'exited':True}
  row['figureThemes']=[]
  for appearance in ['light','dark']:
   page.locator('.theme-trigger').click();page.locator('[data-theme-opt="'+appearance+'"]').click();assert page.locator('html').get_attribute('data-theme')==appearance
   figure=page.locator('figure.fig').filter(has=page.locator('img[src$="/article/height-one.jpg"]'));figure.scroll_into_view_if_needed();figure.locator('img').evaluate('async i=>{await i.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}');snap(page,f'figure-{appearance}-{width}.png');figure.locator('[data-seek-time]').click();page.wait_for_function('Math.abs(document.querySelector("video").currentTime-88.9)<1.5');video.evaluate('(v)=>v.pause()');assert page.evaluate('location.hash')=='#t=88.9';row['figureThemes'].append({'theme':appearance,'exactFrame':seek(page,88.9),'overflow':helpers.overflow(page)})
  video.evaluate('(v)=>v.textTracks[0].mode="showing"');page.wait_for_function('document.querySelector("video").textTracks[0].cues?.length>0');cues=video.evaluate('(v)=>[...v.textTracks[0].cues].map(c=>({start:c.startTime,end:c.endTime,text:c.text}))');assert len(cues)==20 and cues[-1]['end']<=4557/30;t=(cues[0]['start']+cues[0]['end'])/2;native=seek(page,t);assert native['active']==[cues[0]['text']]
  refs=seek(page,154.4);assert not refs['active'];row['referenceColour']=canvas(page,f'references-canvas-{width}.png',[1000,300],expected_refs);snap(page,f'references-{width}.png');restored=seek(page,t);assert restored['active']==native['active'];video.evaluate('(v)=>v.textTracks[0].mode="disabled"');assert not seek(page,t)['active'];row['captions']={'cueCount':len(cues),'explicitNativeBody':native,'referencesEmpty':refs,'restored':restored,'defaultDisabled':True}
  row['errors']=errors;assert not errors;row['overflow']=helpers.overflow(page);ctx.close();print(json.dumps({'width':width,'status':'passed'}),flush=True)
 b.close()
report['status']='passed';report['finishedAt']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds');report['limits']=['Final complete localHTTP media hashes; canonical online checks are separate.','Viewport simulation and native Fullscreen API, not physical-device testing.','Prior nominal fractional UI seek traces retain original microsecond rounding limitation; final directprobes use exact encodedPTS.','No full-film hearing,ASR or user viewingapproval.'];print('Final limited709 colour/player checks passed',flush=True)
