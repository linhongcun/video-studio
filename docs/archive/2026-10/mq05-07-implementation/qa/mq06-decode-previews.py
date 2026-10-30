"""Decode independent clips and bounded owner reuse; write only independent QA."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True,type=Path);args=ap.parse_args();D=args.dir.resolve();Q=D/'qa-independent';O=Q/'decoded-continuous-v1';O.mkdir(exist_ok=True)
ROOT=next(p for p in D.parents if(p/'AGENTS.md').is_file());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
owner=json.loads((D/'qa/self-v1/report.json').read_text());prior=json.loads((D/'qa/self-v1/source-sha256.json').read_text());new=json.loads((Q/'continuous-v1.json').read_text());props={'showSubtitles':False,'hideSubtitles':True}
assert owner['pass']and owner['sourceUnchanged']and owner['props']==props and owner['resolvedProps']==props
assert new['machinePass']and new['props']==props and new['resolvedProps']==props
oldboard=ROOT/'docs/archive/2026-10/mq05-07-implementation/qa/cover-metadata-assembly/mq06-before-storyboard.json'
assert sha(oldboard)==prior['storyboard.json']
oldvalue=json.loads(oldboard.read_text());newvalue=json.loads((D/'storyboard.json').read_text());oldvalue['meta'].pop('covers');newvalue['meta'].pop('covers');assert oldvalue==newvalue
for file,value in prior.items():
 if file!='storyboard.json':assert sha(D/file)==value,file
assert(D/'qa/self-v1/Main.tsx').read_bytes()==(D/'remotion/src/Main.tsx').read_bytes()
rows=[{**r,'origin':'author clip, bounded metadata-only reuse'}for r in owner['clips']]+[{**r,'origin':'fresh independent render'}for r in new['clips']]
report={'kind':'independent-real-continuous-decode','sourceHashes':new['sourceHashes'],'props':props,'ownerReuse':{'beforeBoardSHA256':sha(oldboard),'afterBoardSHA256':sha(D/'storyboard.json'),'actualJSONEqualExcept':['meta.covers'],'allOtherOwnerCapturedInputsEqual':True,'ownerReportSHA256':sha(D/'qa/self-v1/report.json')},'clips':[],'machinePass':False,'visualReviewed':False,'scope':'Actual MP4 complete decode and extracted chronological half-second/last-frame samples; independent fresh clips and bounded reused owner clips are explicitly distinguished. Not formal encoded MP4 acceptance or real-time full-body listening.'}
for row in rows:
 movie=D/row['file'];assert sha(movie)==row['sha256'];count=row['to']-row['from']+1
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(movie)]));v=next(x for x in probe['streams']if x['codec_type']=='video');assert int(v['nb_frames'])==count and v['r_frame_rate']=='30/1'
 subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
 frames=sorted(set(range(0,count,15))|{count-1});images=[]
 folder=O/row['name'];folder.mkdir(exist_ok=True)
 for n in frames:
  p=folder/f'frame-{row["from"]+n:05d}.png'
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(movie),'-vf',f'select=eq(n\\,{n})','-frames:v','1',str(p)],check=True);images.append(p)
 contacts=[]
 for start in range(0,len(images),12):
  batch=images[start:start+12];canvas=Image.new('RGB',(1920,3*292),'#171717');draw=ImageDraw.Draw(canvas)
  for i,p in enumerate(batch):
   x=(i%4)*480;y=(i//4)*292;im=Image.open(p).convert('RGB').resize((480,270));canvas.paste(im,(x,y+22));draw.text((x+5,y+4),p.stem,fill='white')
  p=O/(row['name']+f'-contact-{start//12+1}.jpg');canvas.save(p,quality=94);contacts.append(str(p.relative_to(D)))
 report['clips'].append({'name':row['name'],'file':row['file'],'sha256':row['sha256'],'origin':row['origin'],'sourceFrom':row['from'],'sourceTo':row['to'],'frames':count,'width':v['width'],'height':v['height'],'audioPresent':any(x['codec_type']=='audio'for x in probe['streams']),'fullDecode':True,'sampleSourceFrames':[row['from']+n for n in frames],'actualDecodedImages':[str(p.relative_to(D))for p in images],'contacts':contacts})
 print('decoded',row['name'],count,'samples',len(images),flush=True)
report['machinePass']=all(x['fullDecode']for x in report['clips'])and all(sha(D/file)==value for file,value in new['sourceHashes'].items());(Q/'continuous-decoded-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('six clips complete decode',report['machinePass'])
