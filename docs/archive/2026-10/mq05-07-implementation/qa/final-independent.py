#!/usr/bin/env python3
"""Exact integer-n independent final decode; retains contacts/4 figures/ref/key evidence, temporary raw set."""
import pathlib,json,hashlib,datetime,subprocess,tempfile,argparse,math
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('--spec');p.add_argument('--out-dir',default='qa-independent');a=p.parse_args();D=pathlib.Path(a.episode).resolve();Q=(D/a.out_dir).resolve();assert Q.is_relative_to(D)and Q.name.startswith('qa');OUT=Q/'encoded-evidence';OUT.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
board=json.loads((D/'storyboard.json').read_text());shots=[s for sc in board['scenes']for s in sc['shots']];receipt=json.loads((D/'reference-appendix.json').read_text());render=json.loads((D/'render-result.json').read_text());video=D/'video.mp4';h=sha(video);assert h==receipt['outputSHA256']==render['sha256'];body=receipt['bodyFrames'];total=receipt['finalVideoFrames'];assert body==sum(s['durationInFrames']for s in shots)
refs=json.loads((D/'references.json').read_text());bibliography=[{'id':s['id'],'title':s['title'],'credit':s.get('author')or s['organization']}for s in refs['sources']];assert receipt['bibliography']==bibliography;assert total==body+150*math.ceil(len(bibliography)/4)
frames={}
def add(n,label):
 n=int(n);assert 0<=n<total;frames.setdefault(n,[]).append(label)
for s in shots:add(s['from']+s['durationInFrames']//2,'shot'+s['id']+' representative');add(s['from']+s['durationInFrames']-1,'shot'+s['id']+' end')
for n in [0,60,150,450,body-1,body,body+(total-body)//2,total-1]:add(n,'opening/body/reference boundary')
figs=json.loads((D/'article-figure-plan.json').read_text())['figures']
for f in figs:add(f['frame'],'article:'+f['caption'])
if a.spec:
 for s in json.loads(pathlib.Path(a.spec).read_text())['samples']:add(s['frame'],s.get('label',','.join(s.get('reasons',[]))))
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams']if s['codec_type']=='video');au=next(s for s in probe['streams']if s['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',total);assert au['codec_name']=='aac'and int(au['sample_rate'])==48000;assert v.get('color_space')=='bt709'and v.get('color_range')=='tv'
def balanced_sum(parts):
 if len(parts)==1:return parts[0]
 mid=len(parts)//2
 return '('+balanced_sum(parts[:mid])+'+'+balanced_sum(parts[mid:])+')'
select=balanced_sum([f'eq(n,{n})'for n in sorted(frames)]);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19);samples=[]
with tempfile.TemporaryDirectory(prefix='mq-final-exact-')as td:
 cmd=['ffmpeg','-v','error','-xerror','-err_detect','explode','-threads','3','-filter_threads','1','-i',str(video),'-map','0:v:0','-vf',f"select='{select}'",'-fps_mode','vfr',td+'/raw-%03d.png','-map','0:a:0','-f','null','/dev/null'];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
 raw=sorted(pathlib.Path(td).glob('raw-*.png'));assert len(raw)==len(frames)
 retain={f['frame']for f in figs}|{body,total-1,60,150,body-1}
 for (n,labels),f in zip(sorted(frames.items()),raw):
  dest=OUT/f'frame-{n:05}.png';s={'frame':n,'reasons':labels,'sha256':sha(f),'retainedFile':None}
  if n in retain:dest.write_bytes(f.read_bytes());s['retainedFile']=str(dest.relative_to(D))
  samples.append(s)
 for part in range(math.ceil(len(samples)/8)):
  subset=samples[part*8:(part+1)*8];im=Image.new('RGB',(1920,math.ceil(len(subset)/2)*576),'#181310');draw=ImageDraw.Draw(im)
  for j,s in enumerate(subset):
   f=raw[part*8+j];x=j%2*960;y=j//2*576;im.paste(Image.open(f).convert('RGB').resize((960,540)),(x,y));draw.text((x+6,y+543),str(s['frame'])+' '+','.join(s['reasons'])[:60],font=font,fill='white')
  im.save(OUT/f'contact-{part+1:02}.jpg',quality=94)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'independent-actual-final-media-audit','videoSHA256':h,'bodyFrames':body,'finalFrames':total,'voiceSHA256':sha(D/'voice.wav'),'mainSHA256':sha(D/'remotion/src/Main.tsx'),'frozenManifestSHA256':sha(D/'source-sha256.json'),'referenceBibliography':bibliography,'format':{k:v.get(k)for k in ['codec_name','width','height','r_frame_rate','nb_frames','pix_fmt','color_space','color_transfer','color_primaries','color_range']},'audio':{k:au.get(k)for k in ['codec_name','sample_rate','channels','duration']},'completeVideoAndAudioDecode':{'exit':r.returncode,'errors':r.stderr,'scope':'One FFmpeg pass decodes complete video and AAC audio while exact integer n samples are extracted; no approximate time seek.'},'samples':samples,'machinePass':True,'visualReviewed':False,'scope':'Contacts and retained exact Figure/appendix/opening frames require actual human image review. No ASR/full semantic listening, real-device or user-understanding study claim.'};(Q/'encoded-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'machinePass':True,'samples':len(samples),'body':body,'total':total,'sha256':h,'out':str(OUT)}))
