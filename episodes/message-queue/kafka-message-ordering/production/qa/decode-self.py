from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
D=Path(__file__).resolve().parent.parent;O=D/'qa/self-v1';r=json.loads((O/'report.json').read_text());selected=[x for x in r['samples']if any('voice-'in t or'stable-tail'in t for t in x['labels'])]
for k in range(0,len(selected),6):
 sheet=Image.new('RGB',(1920,1170),'#171310')
 for j,s in enumerate(selected[k:k+6]):
  im=Image.open(D/s['file']).convert('RGB').resize((640,360));x=(j%2)*960+160;y=(j//2)*390;sheet.paste(im,(x,y+30));ImageDraw.Draw(sheet).text((x,y+8),f"f{s['frame']} {s['labels'][0]} {s['metrics']['state']}",fill='white')
 sheet.save(O/f'contact-{k//6+1:02}.jpg',quality=94)
clips=[];decoded=O/'decoded';decoded.mkdir(exist_ok=True)
for c in r['clips']:
 file=D/c['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==c['sha256'];subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(file),'-f','null','/dev/null'],check=True,capture_output=True)
 count=c['to']-c['from']+1;indices=list(range(0,count,15));indices+=[]if indices[-1]==count-1 else[count-1];paths=[]
 for n in indices:
  target=decoded/f'{c["name"]}-n{n:03}.png';subprocess.run(['ffmpeg','-v','error','-i',str(file),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-vsync','0','-y',str(target)],check=True,capture_output=True);paths.append(target)
 contact=Image.new('RGB',(1920,390*((len(paths)+2)//3)),'#171310')
 for j,p in enumerate(paths):
  im=Image.open(p).convert('RGB').resize((640,360));x=(j%3)*640;y=(j//3)*390;contact.paste(im,(x,y+30));ImageDraw.Draw(contact).text((x+8,y+8),f'{c["name"]} f{c["from"]+indices[j]} local{indices[j]}',fill='white')
 strip=decoded/f'{c["name"]}-filmstrip.jpg';contact.save(strip,quality=94);clips.append({**c,'fullDecode':'pass','sampleSourceFrames':[c['from']+n for n in indices],'filmstrip':str(strip.relative_to(D)),'visualReview':'pending'})
(O/'decode-report.json').write_text(json.dumps({'source':r['source'],'clips':clips,'scope':'Actual clips fully decoded, chronological0.5second samples and lastframe. No realtime continuous human playback claim.'},ensure_ascii=False,indent=2)+'\n');print('contact',len(selected),'clip samples',sum(len(c['sampleSourceFrames'])for c in clips))
