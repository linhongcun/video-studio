#!/usr/bin/env python3
"""Exact frame extraction from formal MP4. Only QA outputs are written."""
from pathlib import Path
import datetime,hashlib,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1];Q=D/'qa/encoded-independent';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sb=json.loads((D/'storyboard.json').read_text());shots=[s for c in sb['scenes']for s in c['shots']];by={int(s['id']):s for s in shots};receipt=json.loads((D/'reference-appendix.json').read_text());result=json.loads((D/'render-result.json').read_text());body=receipt['bodyFrames'];total=receipt['finalVideoFrames'];video=D/'video.mp4';assert sha(video)==receipt['outputSHA256']==result['sha256']
frames={}
def add(n,label):
 n=int(n);assert 0<=n<total;frames.setdefault(n,[]).append(label)
for s in shots:add(s['from']+s['durationInFrames']//2,'shot-'+s['id']+' representative')
for n in [0,1,1304,2232,2956,3444]:add(n,'opening/article/final-watermark')
for id in [4,6,7,9]:
 s=by[id];v=s['voice'];a=v[0]['localStart']+18 if id==4 else v[1]['localStart']+8;b=v[0]['localEnd']-8 if id==4 else v[1]['localEnd']-65
 for local in [a+(b-a)*.25,a+(b-a)*.5,a+(b-a)*.75,b]:
  for delta in [-1,0,1]:add(s['from']+math.ceil(local)+delta,'read-moving-or-count-boundary')
for id in [5,8]:
 s=by[id];reset=s['from']+math.ceil(s['voice'][1]['localStart']-6)
 for n in [reset-1,reset,reset+1]:add(n,'explicit-reset-to-new-scenario-boundary')
for n in [body-1,body,body+75,total-1]:add(n,'body/reference-first-middle-last')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams']if s['codec_type']=='video');a=next(s for s in probe['streams']if s['codec_type']=='audio');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',total);assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
assert v.get('color_space')=='bt709' and v.get('color_range')=='tv'
select='+'.join(f'eq(n\\,{n})'for n in sorted(frames));subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf','select='+select,'-fps_mode','vfr',str(Q/'raw-%03d.png')],check=True);raw=sorted(Q.glob('raw-*.png'));assert len(raw)==len(frames);samples=[]
for (n,labels),p in zip(sorted(frames.items()),raw):
 dest=Q/f'frame-{n:05}.png';p.replace(dest);samples.append({'frame':n,'reasons':labels,'file':dest.name,'sha256':sha(dest)})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
for part in range(math.ceil(len(samples)/8)):
 aa=samples[part*8:(part+1)*8];out=Image.new('RGB',(1920,math.ceil(len(aa)/2)*580),(25,23,22));dr=ImageDraw.Draw(out)
 for i,s in enumerate(aa):
  im=Image.open(Q/s['file']);x=i%2*960;y=i//2*580;out.paste(im.resize((960,540)),(x,y));dr.text((x+5,y+543),str(s['frame'])+' '+','.join(s['reasons'])[:60],font=font,fill='white')
 out.save(Q/f'contact-{part+1:02}.jpg',quality=94)
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executor':'Codex independent QA agent','videoSha256':sha(video),'bodyFrames':body,'finalFrames':total,'voiceSha256':sha(D/'voice.wav'),'mainSha256':sha(D/'remotion/src/Main.tsx'),'frozenManifestSha256':sha(D/'source-sha256.json'),'format':{'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'colorSpace':v.get('color_space'),'colorRange':v.get('color_range')},'sampling':'One integer-decoded-n FFmpeg pass through finalMP4; no seek-time approximation and no separate redundant null decode. Existing canonical media verification independently records full body/AAC/PCM identity.','samples':samples,'visualReviewed':False,'limitations':['No ASR, full human semantic listening, physical mobile or novice comprehension study.']}
(Q/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'samples':len(samples),'output':str(Q),'sha256':r['videoSha256']}))
