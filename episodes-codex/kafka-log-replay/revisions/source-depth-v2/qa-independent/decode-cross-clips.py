from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent.parent;Q=D/'qa-independent';O=Q/'decoded-clips';O.mkdir(exist_ok=True)
clips=[('reuse-04-advance',D/'qa/self-preview/advance-position-final-no-subtitles.mp4',1277,1396),('reuse-07-restore',D/'qa/self-preview/restore-assignment-no-subtitles.mp4',2250,2459)]+[(x['name'],D/x['file'],x['from'],x['to'])for x in json.loads((Q/'cross-clips-render.json').read_text())['clips']]
report=[]
for name,file,start,end in clips:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(file),'-f','null','-'],check=True,capture_output=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,duration','-of','json',str(file)]))['streams'][0]
 assert int(probe['nb_frames'])==end-start+1
 samples=list(range(0,end-start+1,15));samples+=[]if samples[-1]==end-start else[end-start]
 paths=[]
 for i in samples:
  out=O/f'{name}-n{i:03}.png';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(file),'-vf',f'select=eq(n\\,{i})','-frames:v','1','-vsync','0','-y',str(out)],check=True,capture_output=True);paths.append(out)
 contact=Image.new('RGB',(1920,390*((len(paths)+2)//3)),'#111111')
 for j,out in enumerate(paths):
  im=Image.open(out).convert('RGB').resize((640,360));x=(j%3)*640;y=(j//3)*390;contact.paste(im,(x,y+30));ImageDraw.Draw(contact).text((x+10,y+8),f'{name} source f{start+samples[j]} local {samples[j]}',fill='white')
 strip=O/f'{name}-filmstrip.jpg';contact.save(strip,quality=94)
 report.append({'name':name,'file':str(file.relative_to(D)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'frameRange':[start,end],'probe':probe,'fullDecode':'pass','sampleEveryFrames':15,'actualDecodedFrames':[start+i for i in samples],'filmstrip':str(strip.relative_to(D)),'actualSubtitleReview':'pending'})
(Q/'cross-clips-decoded.json').write_text(json.dumps({'clips':report,'scope':'Independent full ffmpeg decode and chronological half-second samples plus last frame. Visual review tracked separately, no realtime human playback claim.'},indent=2)+'\n')
print('decoded',len(clips),'clips',sum(len(c['actualDecodedFrames'])for c in report),'frames')
