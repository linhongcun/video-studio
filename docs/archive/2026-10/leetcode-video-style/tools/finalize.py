from pathlib import Path
import json,hashlib,subprocess,shutil,time,gzip,importlib.util,re
from datetime import datetime,timezone,timedelta
ROOT=Path.cwd().resolve();W=ROOT/'work/leetcode-video-style';A=ROOT/'docs/archive/2026-10/leetcode-video-style';BASE='d04a30c12b1ce0fb5743f20ce61f9db8908311ad'
EPISODES=json.loads((ROOT/'episodes-codex/_shared/leetcode-video/identities-v1.json').read_text())['episodes']
OUT=W/'delivery';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('leetcode_reference_adapter',ROOT/'episodes-codex/_shared/leetcode-video/references.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def run(args):subprocess.run([str(x) for x in args],check=True,stdout=subprocess.DEVNULL)
def frame(video,f,path):
 # CFR/PTS has already been checked by the append engine. Seek to the exact
 # preceding integer second, then decode at most 30 selected frames, not the
 # whole file again merely to obtain a still.
 second,offset=divmod(int(f),30)
 run(['ffmpeg','-v','error','-y','-ss',second,'-i',video,'-vf',f'select=eq(n\\,{offset})','-frames:v','1','-fps_mode','vfr',*(['-q:v','2'] if path.suffix.lower() in ('.jpg','.jpeg') else []),path])
summary=A/'final-media-summary.json';reports=read(summary) if summary.exists() else [];done={r['slug'] for r in reports};deadline=time.monotonic()+14400
while len(done)<len(EPISODES):
 if (W/'render-failed.json').exists():raise SystemExit('Renderer failed; preserved partial outputs, stop installation')
 if time.monotonic()>deadline:raise SystemExit('Timed out waiting for LeetCode renders')
 for ep in EPISODES:
  s=ep['slug']
  if s in done or not (W/'render-complete'/f'{s}.json').exists():continue
  src=ROOT/'episodes-codex'/s;rev=src/'revisions/leetcode-style';pub=ROOT/'episodes'/s;result=read(rev/'render-result.json');old=read(rev/'baseline-publication.json');receipt=read(rev/'reference-appendix.json')
  marker=read(W/'render-complete'/f'{s}.json')
  assert marker['slug']==s and marker['exitCode']==0 and marker['status']=='render-complete'
  assert marker['sha256']==result['sha256'] and marker['frames']==result['frames']
  assert result['episode']==receipt['episode']==s
  assert result['visualRevision']=='leetcode-style-v1'
  assert result['newProductionManifestSHA256']==sha(rev/'source-sha256.json')
  video=rev/'video.mp4';baseline=W/'baseline'/f'{s}.mp4'
  assert sha(video)==result['sha256']==receipt['outputSHA256']
  media_check=read(rev/'reference-appendix-media-check.json')
  assert media_check['passed'] is True
  assert media_check['outputSHA256']==result['sha256']
  assert media_check['bodySHA256']==receipt['inputs']['bodySHA256']==sha(rev/'body.mp4')
  assert media_check['bodyFrames']==receipt['bodyFrames']==result['bodyFrames']==old['publishedMetadata']['referenceAppendix']['from']
  assert media_check['finalFrames']==receipt['finalVideoFrames']==result['frames']==old['publishedMetadata']['finalVideoFrames']
  assert media_check['appendedFrames']==old['publishedMetadata']['referenceAppendix']['durationInFrames']==result['frames']-result['bodyFrames']==150
  assert all(media_check[k] is True for k in ['bodyDecodedFramesAndTimestampsEqual','outputVideoTimelineContinuous','audioPacketsAndTimingEqual'])
  meta=read(pub/'meta.json');before_meta_sha=sha(pub/'meta.json');assert meta==old['publishedMetadata'],s+' metadata changed before installation'
  assert (pub/'article.mdx').read_bytes()==(rev/'article.mdx').read_bytes(),s+' article changed after freeze'
  before_packets=adapter.engine.audio_packets(baseline);after_packets=adapter.engine.audio_packets(video);assert before_packets==after_packets,s+' AAC/timing changed'
  pcm_before=adapter.engine.audio_hash(baseline);pcm_after=adapter.engine.audio_hash(video);assert pcm_before==pcm_after,s+' PCM changed'
  stream=adapter.engine.stream(adapter.engine.probe(video),'video');assert int(stream['nb_frames'])==result['frames']==old['publishedMetadata']['finalVideoFrames']
  article=(pub/'article.mdx').read_text();seek=float(re.search(r'<Figure[^>]*seekTo=\{([0-9.]+)\}',article).group(1));figure_frame=round(seek*30);body=result['bodyFrames'];code_start=body-150
  frames=sorted(set([0,code_start//2,figure_frame,code_start-1,code_start,code_start+75,body-1,body,body+75,result['frames']-1]));dest=A/'final'/s;dest.mkdir(parents=True,exist_ok=True)
  samples=[]
  for n,f in enumerate(frames,1):
   p=dest/f'frame-{n:02d}.png';frame(video,f,p);samples.append({'frame':f,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
  figure=pub/'article/01.jpg';figure.parent.mkdir(parents=True,exist_ok=True);previous_image_sha=hashlib.sha256(subprocess.check_output(['git','show',BASE+':'+str(figure.relative_to(ROOT))])).hexdigest()
  frame(video,figure_frame,figure)
  for target in [src,pub]:
   for name in ['reference-appendix.json','reference-appendix-media-check.json','render-result.json']:shutil.copyfile(rev/name,target/name)
   shutil.copyfile(video,target/'video.mp4')
   assert sha(target/'video.mp4')==result['sha256']
   for name in ['reference-appendix.json','reference-appendix-media-check.json','render-result.json']:assert sha(target/name)==sha(rev/name)
  meta.update(result['publicationMetadata']);meta['updatedAt']=datetime.fromisoformat(result['createdAtUTC']).astimezone(timezone(timedelta(hours=8))).isoformat(timespec='seconds');meta['sourcePath']=f'episodes-codex/{s}/revisions/leetcode-style';write(pub/'meta.json',meta)
  changed={key for key in set(meta)|set(old['publishedMetadata']) if meta.get(key)!=old['publishedMetadata'].get(key)}
  assert changed <= set(result['publicationMetadata'])|{'updatedAt','sourcePath'},(s,changed)
  for key in ['slug','title','problemNumber','ep','createdAt','publishedAt','firstRelease','platforms','series','tags','summary','description','related']:
   assert meta.get(key)==old['publishedMetadata'].get(key),(s,key)
  output=OUT/(f'LC{ep["number"]}-'+''.join(ep['title'])+'.mp4');shutil.copyfile(video,output);assert sha(output)==result['sha256']
  r={'slug':s,'problemNumber':ep['number'],'method':ep['method'],'installedAtUTC':datetime.now(timezone.utc).isoformat(),'sha256':sha(video),'bytes':video.stat().st_size,'frames':result['frames'],'bodyFrames':body,'codeRange':[code_start,body-1],'referenceRange':[body,result['frames']-1],
   'fullBaselineAACPacketsAndTimingEqual':True,'audioPacketCount':len(after_packets),'decodedPCM':pcm_after,'bodyFramesAndPTSVerifiedByAppendixEngine':True,'preservedBodyIncludesCompletePythonCard':True,'stillsMethod':'Accurate integer-second input seek plus exact relative CFR frame select; avoids a repeat full stream decode.',
   'preMediaMetadataSHA256':before_meta_sha,'installedMetadataSHA256':sha(pub/'meta.json'),'changedMetadataFields':sorted(changed),'originalArticleSHA256':sha(pub/'article.mdx'),'articleFigure':{'file':str(figure.relative_to(ROOT)),'seconds':seek,'frame':figure_frame,'previousSHA256':previous_image_sha,'sha256':sha(figure)},'samples':samples,'delivery':str(output.relative_to(ROOT))}
  write(dest/'final-media-check.json',r);reports.append(r);write(summary,reports)
  log=W/(s+'-render.log')
  if log.exists():(dest/'render.log.gz').write_bytes(gzip.compress(log.read_bytes(),mtime=0))
  done.add(s);print(json.dumps({'slug':s,'status':'installed-complete-audio-and-metadata-verified','sha256':r['sha256']}),flush=True)
 if len(done)<len(EPISODES):time.sleep(5)
print('All11 LeetCode outputs installed.',flush=True)
