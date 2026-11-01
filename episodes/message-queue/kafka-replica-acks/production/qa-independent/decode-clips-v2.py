from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess
D=Path(__file__).resolve().parent.parent;Q=D/'qa-independent';OUT=Q/'decode-v2';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
handoff=read(D/'qa-self/actual-handoff.json');original=read(Q/'clips-v2/report.json');added={'clips':[],'props':original['props'],'resolvedProps':original['resolvedProps'],'sourceHashes':original['sourceHashes']};entries=[];handoff['sourceHashes']['remotion/src/Main.tsx']='5afaaccd438a9b3a60010bc4c28c4b09ed9d92bcea2937b8497a0da77b787ed8'
assert original['props']==original['resolvedProps']==added['props']==added['resolvedProps']=={'showSubtitles':False,'hideSubtitles':True}
for report in [original,added]:
 for name,h in report['sourceHashes'].items():assert sha(D/name)==h==handoff['sourceHashes'][name],name
for index,clip in enumerate(original['clips']+added['clips'],1):
 p=D/clip['file'];assert sha(p)==clip['sha256'];sub=OUT/f'clip-{index:02}';sub.mkdir()
 frames=clip['to']-clip['from']+1;nums=sorted(set(list(range(0,frames,20))+[frames-1]));expr='+'.join(f'eq(n\\,{n})' for n in nums)
 command=['ffmpeg','-hide_banner','-v','error','-xerror','-threads','2','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-','-map','0:v:0','-vf','select='+expr,'-fps_mode','vfr','-threads','2',str(sub/'f%03d.png')]
 result=subprocess.run(command,capture_output=True,text=True);(sub/'decode.stderr.txt').write_text(result.stderr);assert result.returncode==0,result.stderr
 probe_cmd=['ffprobe','-v','error','-show_streams','-of','json',str(p)];probe=read_json=subprocess.check_output(probe_cmd,text=True);(sub/'ffprobe.json').write_text(probe)
 streams=json.loads(probe)['streams'];video=next(x for x in streams if x['codec_type']=='video');audio=next(x for x in streams if x['codec_type']=='audio');assert int(video['nb_frames'])==frames and video['r_frame_rate']=='30/1' and audio['codec_name']=='aac'
 images=sorted(sub.glob('f*.png'));assert len(images)==len(nums);samples=[{'globalFrame':clip['from']+n,'file':str(i.relative_to(D)),'sha256':sha(i)}for n,i in zip(nums,images)]
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);contacts=[]
 for offset in range(0,len(samples),12):
  group=samples[offset:offset+12];im=Image.new('RGB',(1920,385*4),(30,28,27));dr=ImageDraw.Draw(im)
  for j,s in enumerate(group):
   x=j%3*640;y=j//3*385;im.paste(Image.open(D/s['file']).convert('RGB').resize((640,360)),(x,y+25));dr.text((x+8,y+3),f'clip{index} global {s["globalFrame"]}',font=font,fill='white')
  dest=sub/f'contact-{offset//12+1:02}.jpg';im.save(dest,quality=93);contacts.append({'file':str(dest.relative_to(D)),'sha256':sha(dest)})
 entries.append({'name':clip['name'],'file':clip['file'],'sha256':clip['sha256'],'reusedSameIdentityAuthorRenderedMP4':False,'frameRange':[clip['from'],clip['to']],'frames':frames,'completeVideoAndAACDecode':{'command':command,'exitCode':result.returncode,'stderr':result.stderr},'video':{k:video[k] for k in ['codec_name','width','height','r_frame_rate','nb_frames']},'audio':{k:audio[k]for k in ['codec_name','sample_rate','channels']},'samples':samples,'contacts':contacts,'visualReviewed':False})
 print('decoded',index,frames,'samples',len(samples),flush=True)
report={'kind':'independent-actual-continuous-MP4-decode-and-sequence-review','createdAtUTC':datetime.now(timezone.utc).isoformat(),'sourceHashes':original['sourceHashes'],'props':original['props'],'resolvedProps':original['resolvedProps'],'sourceUnchanged':all(sha(D/n)==h for n,h in original['sourceHashes'].items()),'clips':entries,'completeDecodedFrames':sum(x['frames']for x in entries),'sequenceSamples':sum(len(x['samples'])for x in entries),'machinePass':True,'visualReviewed':False,'limitations':['Bounded actual-source previews, not the final production MP4 or appendix.','Full video/AAC decode proves decodability, not exhaustive semantic audio listening.','Finite chronological visual samples and exact integer DOM/PNG boundaries; not every encoded frame visually viewed.']}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
