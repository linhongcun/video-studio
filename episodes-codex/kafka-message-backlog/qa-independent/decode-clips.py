from pathlib import Path
import subprocess,json,hashlib,datetime
from PIL import Image,ImageDraw
D=Path('/workspace/video-studio/episodes-codex/kafka-message-backlog'); O=D/'qa-independent'; R=O/'clips';R.mkdir(exist_ok=True)
author=json.loads((D/'qa-self-finaltiming/clip-decode-review.json').read_text())
rows=[]
starts=[920,1875,2840,3500,5155]
for ix,c in enumerate(author['clips']):
 p=D/'qa-self-finaltiming'/c['clip'];sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==c['sha256']
 dec=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-map','0:v:0','-map','0:a:0?','-f','null','-'],capture_output=True,text=True);assert dec.returncode==0,dec.stderr
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
 frames=int(next(s for s in probe['streams'] if s['codec_type']=='video')['nb_frames'])
 # independent chronological half-second samples + transition-adjacent points already chosen by author
 nums=sorted(set([0,frames-1]+list(range(0,frames,15))+[s['localFrame'] for s in c['samples']]))
 out=R/p.stem;out.mkdir(exist_ok=True);expr='+'.join(f'eq(n,{n})' for n in nums)
 ext=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-vf',f'select={expr.replace(",",chr(92)+",")}', '-vsync','0','-an',str(out/'frame-%04d.png')],capture_output=True,text=True);assert ext.returncode==0,ext.stderr
 fs=sorted(out.glob('frame-*.png'));assert len(fs)==len(nums)
 samples=[];sheets=[]
 for n,f in zip(nums,fs):samples.append({'localFrame':n,'globalFrame':starts[ix]+n,'file':str(f.relative_to(D)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 for j in range(0,len(fs),12):
  chunk=list(zip(nums,fs))[j:j+12];w,h=480,270;im=Image.new('RGB',(w*3,(h+26)*((len(chunk)+2)//3)),(35,30,28));draw=ImageDraw.Draw(im)
  for k,(n,f) in enumerate(chunk):
   a=Image.open(f).convert('RGB');a.thumbnail((w,h));x=k%3*w;y=k//3*(h+26);im.paste(a,(x,y));draw.text((x+6,y+h+5),f'global {starts[ix]+n} local {n}',fill='white')
  sh=R/(p.stem+f'-{j//12+1:02}.jpg');im.save(sh,quality=94);sheets.append(str(sh.relative_to(D)))
 row={'clip':str(p.relative_to(D)),'sha256':sha,'globalFrom':starts[ix],'globalTo':starts[ix]+frames-1,'frames':frames,'decodeReturnCode':dec.returncode,'stderr':dec.stderr,'streams':[{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate','sample_rate','nb_frames']} for s in probe['streams']],'samples':samples,'contactSheets':sheets,'visualReviewed':False};rows.append(row);print(p.name,'DECODED',frames,'SAMPLED',len(samples),flush=True)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent full video+AAC xerror decode of source-matched authored short clips and chronological actual PNG review; no whole-film semantic listening.','identity':author['identity'],'clips':rows,'visualReviewed':False}
(O/'clip-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
