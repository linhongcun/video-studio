#!/usr/bin/env python3
"""Read-only exact-n final encoding sampling; all rawPNG in ignored qa/out."""
from pathlib import Path
import datetime,hashlib,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1];OUT=D/'qa/out/encoded';OUT.mkdir(parents=True,exist_ok=True);EVIDENCE=D/'qa/encoded-evidence';EVIDENCE.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sb=json.loads((D/'storyboard.json').read_text());shots=[s for c in sb['scenes']for s in c['shots']];by={int(s['id']):s for s in shots};receipt=json.loads((D/'reference-appendix.json').read_text());result=json.loads((D/'render-result.json').read_text());body=receipt['bodyFrames'];total=receipt['finalVideoFrames'];video=D/'video.mp4';assert sha(video)==receipt['outputSHA256']==result['sha256']
assert body==sum(s['durationInFrames'] for s in shots)==3417 and total==body+150==3567
refs=json.loads((D/'references.json').read_text());expected_bibliography=[{'id':s['id'],'title':s['title'],'credit':s.get('author')or s['organization']}for s in refs['sources']];assert receipt['bibliography']==expected_bibliography and len(expected_bibliography)==2
frames={}
def add(n,label):
 n=int(n);assert 0<=n<total;frames.setdefault(n,[]).append(label)
def boundary(id,local,label):
 for d in [-1,0,1]:add(by[id]['from']+math.ceil(local)+d,label)
def voice(id):
 v=by[id]['voice'];return v[0]['localStart'],v[0]['localEnd'],v[1]['localStart'],v[1]['localEnd']
for s in shots:add(s['from']+s['durationInFrames']//2,'shot-'+s['id']+' representative')
for n in [0,60,150,450,1220,2405,2713,3040,body-1]:add(n,'opening/article/last-body')
def adjacent(id,local,label):
 first=by[id]['from']+math.ceil(local)
 for n in [first-1,first]:add(n,label)
a,b,c,e=voice(3);adjacent(3,a+(b-a)*.57,'Future returns and first term appears')
a,b,c,e=voice(4);app=a+(b-a)*.42;confirmed=max(app+30,b-12)
adjacent(4,app,'append and guarded write headline');adjacent(4,confirmed,'response arrives then metadata success')
a,b,c,e=voice(6);adjacent(6,0,'reset normal to unknown');adjacent(6,c-8,'unknown reset leaves empty log');adjacent(6,c+(e-c)*.58,'unknown append and footer truth')
a,b,c,e=voice(7);adjacent(7,a+(b-a)*.76,'same batch automatic retry retains one record')
a,b,c,e=voice(8);adjacent(8,a+(b-a)*.62,'final delivery failure and guarded headline/tag')
a,b,c,e=voice(9);app=c+(e-c)*.26;confirmed=max(app+35,e-65)
adjacent(9,a+(b-a)*.2,'old A closes with failed result');adjacent(9,a+(b-a)*.64,'new B application send retains old record');adjacent(9,app,'same E01 new offset1');adjacent(9,confirmed,'new B success preserves old A failure')
a,b,c,e=voice(10);adjacent(10,0,'reset to serialization comparison');adjacent(10,c-8,'local reset returns to empty log');adjacent(10,c+(e-c)*.38,'synchronous local failure no Future or Produce')
adjacent(11,0,'recap returns to three independent results')
for n in [body,body+75,total-1]:add(n,'reference-first-middle-last')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams']if s['codec_type']=='video');a=next(s for s in probe['streams']if s['codec_type']=='audio');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',total);assert a['codec_name']=='aac'and int(a['sample_rate'])==48000;assert v.get('color_space')=='bt709'and v.get('color_range')=='tv'
select='+'.join(f'eq(n\\,{n})'for n in sorted(frames));subprocess.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(video),'-vf','select='+select,'-fps_mode','vfr',str(OUT/'raw-%03d.png')],check=True);raw=sorted(OUT.glob('raw-*.png'));assert len(raw)==len(frames);samples=[]
for(n,labels),p in zip(sorted(frames.items()),raw):
 dest=OUT/f'frame-{n:05}.png';p.replace(dest);samples.append({'frame':n,'reasons':labels,'file':str(dest.relative_to(D)),'sha256':sha(dest)})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
for part in range(math.ceil(len(samples)/6)):
 aa=samples[part*6:(part+1)*6];im=Image.new('RGB',(1920,math.ceil(len(aa)/2)*580),(25,23,22));dr=ImageDraw.Draw(im)
 for i,s in enumerate(aa):
  q=Image.open(D/s['file']);x=i%2*960;y=i//2*580;im.paste(q.resize((960,540)),(x,y));dr.text((x+5,y+543),str(s['frame'])+' '+','.join(s['reasons'])[:70],font=font,fill='white')
 im.save(EVIDENCE/f'contact-{part+1:02}.jpg',quality=94)
for n in [1220,2405,2713,3040,body,total-1]:
 src=OUT/f'frame-{n:05}.png';(EVIDENCE/src.name).write_bytes(src.read_bytes())
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executor':'Codex independentQA','videoSha256':sha(video),'bodyFrames':body,'finalFrames':total,'voiceSha256':sha(D/'voice.wav'),'mainSha256':sha(D/'remotion/src/Main.tsx'),'frozenManifestSha256':sha(D/'source-sha256.json'),'format':{'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'colorSpace':v.get('color_space'),'colorRange':v.get('color_range')},'sampling':'One integer-decoded-n FFmpeg pass with xerror/err_detect through all video frames of finalMP4; no approximate time seek and no separate duplicate null decode. Root canonical media verifier records full-body/AAC/PCM identity.','samples':samples,'visualReviewed':False,'limitations':['No wordASR, full human semantic listening, real Kafka Broker/producer/serializer/network/consumer side-effect experiment, physical mobile or novice comprehension study.']};(D/'qa/encoded-independent.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'samples':len(samples),'output':str(EVIDENCE),'sha256':r['videoSha256']}))
