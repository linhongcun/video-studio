#!/usr/bin/env python3
"""Exact integer-n independent final decode; retains all raw PNGs, contacts, figures and reference evidence."""
import pathlib,json,hashlib,datetime,subprocess,argparse,math,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=next(p for p in pathlib.Path(__file__).resolve().parents if(p/'AGENTS.md').is_file());sys.path.insert(0,str(ROOT/'episodes/_shared'));from episode_paths import episode_slug,production_directory
p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('--spec');p.add_argument('--out-dir',default='qa-final-independent');p.add_argument('--reviewer',default='Independent executor; actual visual reviewer recorded after review');a=p.parse_args();D=pathlib.Path(a.episode).resolve();assert D.is_relative_to(production_directory(episode_slug(D),root=ROOT));Q=(D/a.out_dir).resolve();assert Q.is_relative_to(D)and Q.name.startswith('qa');assert not Q.exists()or not any(Q.iterdir()),'Preserve earlier raw attempt; select fresh --out-dir';OUT=Q/'encoded-evidence';OUT.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identity={name:sha(D/name)for name in ['source-sha256.json','voice.wav','storyboard.json','remotion/src/Main.tsx']}
board=json.loads((D/'storyboard.json').read_text());shots=[s for sc in board['scenes']for s in sc['shots']];receipt=json.loads((D/'reference-appendix.json').read_text());render=json.loads((D/'render-result.json').read_text());video=D/'video.mp4';h=sha(video);assert h==receipt['outputSHA256']==render['sha256'];body=receipt['bodyFrames'];total=receipt['finalVideoFrames'];assert body==sum(s['durationInFrames']for s in shots)
refs=json.loads((D/'references.json').read_text());bibliography=[{'id':s['id'],'title':s['title'],'credit':s.get('author')or s['organization']}for s in refs['sources']];assert receipt['bibliography']==bibliography;assert total==body+150*math.ceil(len(bibliography)/4)
frames={}
def add(n,label):
 assert type(n)is int and 0<=n<total,'Exact integer frame required';frames.setdefault(n,[]).append(label)
for s in shots:add(s['from']+s['durationInFrames']//2,'shot'+s['id']+' representative');add(s['from']+s['durationInFrames']-1,'shot'+s['id']+' end')
for n in [0,60,150,450,body-1,body,body+(total-body)//2,total-1]:add(n,'opening/body/reference boundary')
figs=json.loads((D/'article-figure-plan.json').read_text())['figures']
for f in figs:add(f['frame'],'article:'+f['caption'])
for i in range(len(receipt['appendix']['pages'])):
 for n in [body+i*150,body+i*150+75,body+i*150+149]:add(n,'reference page'+str(i+1)+' first/mid/last')
if a.spec:
 for s in json.loads(pathlib.Path(a.spec).read_text())['samples']:add(s['frame'],s.get('label',','.join(s.get('reasons',[]))))
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams']if s['codec_type']=='video');au=next(s for s in probe['streams']if s['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',total);assert au['codec_name']=='aac'and int(au['sample_rate'])==48000;assert all(v.get(k)==x for k,x in {'codec_name':'h264','pix_fmt':'yuv420p','color_space':'bt709','color_range':'tv','color_transfer':'bt709','color_primaries':'bt709'}.items())
def balanced_sum(parts):
 if len(parts)==1:return parts[0]
 mid=len(parts)//2
 return '('+balanced_sum(parts[:mid])+'+'+balanced_sum(parts[mid:])+')'
select=balanced_sum([f'eq(n,{n})'for n in sorted(frames)]);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19);samples=[]
if True:
 td=str(OUT/'raw');pathlib.Path(td).mkdir()
 cmd=['ffmpeg','-v','error','-xerror','-err_detect','explode','-threads','3','-filter_threads','1','-i',str(video),'-map','0:v:0','-vf',f"select='{select}'",'-fps_mode','vfr',td+'/raw-%03d.png','-map','0:a:0','-f','null','/dev/null'];r=subprocess.run(cmd,capture_output=True,text=True);(Q/'decode.stderr.txt').write_text(r.stderr);(Q/'decode-attempt.json').write_text(json.dumps({'command':cmd,'exit':r.returncode,'stderr':r.stderr,'videoSHA256':h,'inputSHA256':identity},indent=2)+'\n');assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
 raw=sorted(pathlib.Path(td).glob('raw-*.png'));assert len(raw)==len(frames)
 retain={f['frame']for f in figs}|{body,total-1,60,150,body-1}
 for (n,labels),f in zip(sorted(frames.items()),raw):
  dest=OUT/f'frame-{n:05}.png';s={'frame':n,'reasons':labels,'sha256':sha(f),'retainedFile':None}
  s['retainedFile']=str(f.relative_to(D))
  samples.append(s)
 for part in range(math.ceil(len(samples)/8)):
  subset=samples[part*8:(part+1)*8];im=Image.new('RGB',(1920,math.ceil(len(subset)/2)*576),'#181310');draw=ImageDraw.Draw(im)
  for j,s in enumerate(subset):
   f=raw[part*8+j];x=j%2*960;y=j//2*576;im.paste(Image.open(f).convert('RGB').resize((960,540)),(x,y));draw.text((x+6,y+543),str(s['frame'])+' '+','.join(s['reasons'])[:60],font=font,fill='white')
  im.save(OUT/f'contact-{part+1:02}.jpg',quality=94)
assert h==sha(video)and all(sha(D/name)==value for name,value in identity.items())
report={'reviewer':a.reviewer,'inputSHA256':identity,'allRawSamplesRetained':True,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'independent-actual-final-media-audit','videoSHA256':h,'bodyFrames':body,'finalFrames':total,'voiceSHA256':sha(D/'voice.wav'),'mainSHA256':sha(D/'remotion/src/Main.tsx'),'frozenManifestSHA256':sha(D/'source-sha256.json'),'referenceBibliography':bibliography,'format':{k:v.get(k)for k in ['codec_name','width','height','r_frame_rate','nb_frames','pix_fmt','color_space','color_transfer','color_primaries','color_range']},'audio':{k:au.get(k)for k in ['codec_name','sample_rate','channels','duration']},'completeVideoAndAudioDecode':{'exit':r.returncode,'errors':r.stderr,'scope':'One FFmpeg pass decodes complete video and AAC audio while exact integer n samples are extracted; no approximate time seek.'},'samples':samples,'machinePass':True,'visualReviewed':False,'scope':'All raw selected frames and contacts are retained and require actual human image review. No ASR/full semantic listening, real-device or user-understanding study claim.'};(Q/'encoded-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'machinePass':True,'samples':len(samples),'body':body,'total':total,'sha256':h,'out':str(OUT)}))
