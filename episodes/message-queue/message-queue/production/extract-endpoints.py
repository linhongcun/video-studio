from pathlib import Path
import json,subprocess,hashlib
D=Path(__file__).resolve().parent
s=json.loads((D/'storyboard.json').read_text());shots=[q for a in s['scenes'] for q in a['shots']];frames=[]
for sid in ['03','04','07','08','09']:
 q=next(x for x in shots if x['id']==sid);frames.append((sid+'-end',q['from']+q['durationInFrames']-1))
q=next(x for x in shots if x['id']=='09');frames.append(('09-first',q['from']))
q=next(x for x in shots if x['id']=='05');frames.append(('05-middle',q['from']+round(q['durationInFrames']*.5)))
rows=[]
for name,f in frames:
 out=D/'qa-evidence'/f'final-{name}.png'
 subprocess.run(['ffmpeg','-v','error','-threads','1','-y','-ss',str(f/30),'-i',str(D/'video.mp4'),'-frames:v','1','-vf','scale=960:540','-threads','1',str(out)],check=True)
 rows.append({'name':name,'frame':f,'path':str(out.relative_to(D)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(D/'qa-evidence/final-extra-frames.json').write_text(json.dumps(rows,indent=2)+'\n')
p=D/'delivery.json';d=json.loads(p.read_text());d['actualMp4ReviewFrames']+=rows;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Extracted7 exact final MP4 endpoint/action frames')
