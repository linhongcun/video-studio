#!/usr/bin/env python3
"""Read-only exact-n final encoding sampling; all rawPNG in ignored qa/out."""
from pathlib import Path
import datetime,hashlib,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1];OUT=D/'qa/out/encoded';OUT.mkdir(parents=True,exist_ok=True);EVIDENCE=D/'qa/encoded-evidence';EVIDENCE.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sb=json.loads((D/'storyboard.json').read_text());shots=[s for c in sb['scenes']for s in c['shots']];by={int(s['id']):s for s in shots};receipt=json.loads((D/'reference-appendix.json').read_text());result=json.loads((D/'render-result.json').read_text());body=receipt['bodyFrames'];total=receipt['finalVideoFrames'];video=D/'video.mp4';assert sha(video)==receipt['outputSHA256']==result['sha256']
refs=json.loads((D/'references.json').read_text());expected_bibliography=[{'id':s['id'],'title':s['title'],'credit':s.get('author')or s['organization']}for s in refs['sources']];assert receipt['bibliography']==expected_bibliography and len(expected_bibliography)==4
frames={}
def add(n,label):
 n=int(n);assert 0<=n<total;frames.setdefault(n,[]).append(label)
def boundary(id,local,label):
 for d in [-1,0,1]:add(by[id]['from']+math.ceil(local)+d,label)
def voice(id):
 v=by[id]['voice'];return v[0]['localStart'],v[0]['localEnd'],v[1]['localStart'],v[1]['localEnd']
for s in shots:add(s['from']+s['durationInFrames']//2,'shot-'+s['id']+' representative')
for n in [0,1445,2900,3251,3572,body-1]:add(n,'opening/article/last-body')
for id,fractions in [(4,[.5]),(5,[.25,.76]),(6,[.8]),(8,[.22,.46,.77])]:
 a,b,c,e=voice(id)
 for f in fractions:boundary(id,a+(b-a)*f,'poll/process/commit/inactive/reset boundary')
a,b,c,e=voice(7);aa=a+12;ee=max(aa+130,e-65);add(by[7]['from']+math.ceil(aa+(ee-aa)*2.5/4),'points-second-read source focusE03')
a,b,c,e=voice(9);aa=a+12;ee=max(aa+150,b-20)
for f in [1/5,3/5,1]:boundary(9,aa+(ee-aa)*f,'restart/replay first-commit/final boundary')
add(by[9]['from']+math.ceil(aa+(ee-aa)*3.5/5),'replay-second-read source focusE03')
a,b,c,e=voice(10);boundary(10,c+(e-c)*.46,'eligible-closed-segment deletion boundary')
for n in [body,body+75,total-1]:add(n,'reference-first-middle-last')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams']if s['codec_type']=='video');a=next(s for s in probe['streams']if s['codec_type']=='audio');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',total);assert a['codec_name']=='aac'and int(a['sample_rate'])==48000;assert v.get('color_space')=='bt709'and v.get('color_range')=='tv'
select='+'.join(f'eq(n\\,{n})'for n in sorted(frames));subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf','select='+select,'-fps_mode','vfr',str(OUT/'raw-%03d.png')],check=True);raw=sorted(OUT.glob('raw-*.png'));assert len(raw)==len(frames);samples=[]
for(n,labels),p in zip(sorted(frames.items()),raw):
 dest=OUT/f'frame-{n:05}.png';p.replace(dest);samples.append({'frame':n,'reasons':labels,'file':str(dest.relative_to(D)),'sha256':sha(dest)})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
for part in range(math.ceil(len(samples)/8)):
 aa=samples[part*8:(part+1)*8];im=Image.new('RGB',(1920,math.ceil(len(aa)/2)*580),(25,23,22));dr=ImageDraw.Draw(im)
 for i,s in enumerate(aa):
  q=Image.open(D/s['file']);x=i%2*960;y=i//2*580;im.paste(q.resize((960,540)),(x,y));dr.text((x+5,y+543),str(s['frame'])+' '+','.join(s['reasons'])[:70],font=font,fill='white')
 im.save(EVIDENCE/f'contact-{part+1:02}.jpg',quality=94)
for n in [1445,2900,3251,3572,body,total-1]:
 src=OUT/f'frame-{n:05}.png';(EVIDENCE/src.name).write_bytes(src.read_bytes())
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executor':'Codex independentQA','videoSha256':sha(video),'bodyFrames':body,'finalFrames':total,'voiceSha256':sha(D/'voice.wav'),'mainSha256':sha(D/'remotion/src/Main.tsx'),'frozenManifestSha256':sha(D/'source-sha256.json'),'format':{'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'colorSpace':v.get('color_space'),'colorRange':v.get('color_range')},'sampling':'One integer-decoded-n FFmpeg pass through finalMP4; no approximate time seek and no separate duplicate null decode. Root canonical media verifier records full-body/AAC/PCM identity.','samples':samples,'visualReviewed':False,'limitations':['No wordASR, full human semantic listening, realBroker/retention scheduling, physical mobile or novice comprehension study.']};(D/'qa/encoded-independent.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'samples':len(samples),'output':str(EVIDENCE),'sha256':r['videoSha256']}))
