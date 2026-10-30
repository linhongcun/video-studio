#!/usr/bin/env python3
"""Read-only re-audit of declared source-matched preview clips; actual FFmpeg decode/contact sheets."""
import argparse, pathlib, json, hashlib, subprocess, tempfile, concurrent.futures, datetime
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('source_report');p.add_argument('--name',default='clip-independent');a=p.parse_args();D=pathlib.Path(a.episode).resolve();R=json.loads(pathlib.Path(a.source_report).read_text());Q=D/'qa-independent';Q.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={}
for n,h in R['sourceIdentity'].items():
 f=(D/'remotion'/n if n.startswith('src/') or n.startswith('../') else D/n).resolve();source[n]={'sha256':sha(f),'expected':h,'match':sha(f)==h}
clips=[]
for x in R['clips']:
 if 'file'in x:f=D/x['file'];first=x['from'];last=x['to']
 else:
  f=pathlib.Path(a.source_report).parent/(x['name']+'.mp4');first=x['first'];last=x['last']
  if not f.exists():f=f.with_name(x['name']+'-no-subtitles.mp4')
 clips.append((x,f.resolve(),first,last))
def run(v):
 x,f,first,last=v;probe=subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(f)],capture_output=True,text=True,check=True);streams=json.loads(probe.stdout)['streams'];video=next(s for s in streams if s['codec_type']=='video');decode=subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],capture_output=True,text=True);n=last-first+1
 picked=sorted(set([0,n-1,*range(0,n,30)]));select='+'.join('eq(n,%d)'%k for k in picked)
 with tempfile.TemporaryDirectory(prefix='mq-independent-')as td:
  subprocess.run(['ffmpeg','-v','error','-threads','2','-filter_threads','1','-i',str(f),'-vf',f"select='{select}',scale=480:270",'-vsync','0',td+'/%04d.png'],check=True,capture_output=True)
  ims=sorted(pathlib.Path(td).glob('*.png'));rows=(len(ims)+3)//4;contact=Image.new('RGB',(1920,rows*296),'#181310');draw=ImageDraw.Draw(contact)
  for i,png in enumerate(ims):
   im=Image.open(png).convert('RGB');ox=(i%4)*480;oy=(i//4)*296;contact.paste(im,(ox,oy));draw.text((ox+8,oy+273),f'global n={first+picked[i]} / clip n={picked[i]}',fill='white')
  out=Q/(a.name+'-'+f.stem+'.jpg');contact.save(out,quality=92)
 h=sha(f);return {'file':str(f.relative_to(D)),'sha256':h,'declaredSHA':x.get('sha256'),'shaMatches':not x.get('sha256') or x['sha256']==h,'first':first,'last':last,'expectedFrames':n,'video':{k:video.get(k)for k in ['codec_name','width','height','r_frame_rate','nb_frames','pix_fmt']},'fullDecodeExit':decode.returncode,'decodeErrors':decode.stderr,'sampledGlobalFrames':[first+k for k in picked],'contact':str(out.relative_to(D)),'visualReviewed':False,'actualNoSubtitlesVisuallyConfirmed':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as e:out=list(e.map(run,clips))
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'independent-source-matched-actual-clip-decode','sourceIdentity':source,'clips':out,'machinePass':all(s['match']for s in source.values())and all(c['shaMatches']and c['fullDecodeExit']==0 and not c['decodeErrors'] and int(c['video']['nb_frames'])==c['expectedFrames']for c in out),'scope':'Reuses other author actual encoded clips after source byte identity check. Complete FFmpeg decode plus every-second/end decoded frame contacts. Human visual review must be recorded separately; not full realtime playback or ASR.'};(Q/(a.name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'machinePass':report['machinePass'],'clips':len(out),'report':str(Q/(a.name+'.json'))}))
