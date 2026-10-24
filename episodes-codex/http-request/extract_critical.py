"""Extract actual encoded action phases for independent visual review."""
from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent
s=json.loads((D/'storyboard.json').read_text());shots=[q for c in s['scenes']for q in c['shots']]
keys={'http-request':[8,9,10,11],'https':[5,7,8,10,11],'dns':[5,6,7,8,9,10,11]}[D.name]
rows={}
for q in shots:
 if int(q['id'])not in keys:continue
 d=q['durationInFrames'];local={0,d-1,*[round(d*p)for p in [.18,.38,.58,.8,.97]]}
 if D.name=='https'and int(q['id'])==8:local.update([149,150,175,185])
 if D.name=='https'and int(q['id'])==10:
  b=q['cueFrames']['sentences'][1];local.update([b+11,b+12,b+81,b+82])
 for f in local:
  if 0<=f<d:rows[q['from']+f]={'shot':q['id'],'localFrame':f,'frame':q['from']+f}
frames=sorted(rows);out=Path('/tmp')/f'{D.name}-encoded-critical';out.mkdir(exist_ok=True)
select='+'.join(f'eq(n,{f})'for f in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(D/'video.mp4'),'-an','-vf',f"select='{select}',scale=960:540",'-fps_mode','vfr',str(out/'frame-%03d.png')],check=True)
records=[]
for i,f in enumerate(frames,1):
 row=rows[f];row['file']=str(out/f'frame-{i:03d}.png');records.append(row)
assert len(list(out.glob('frame-*.png')))==len(records)
obj={'videoSha256':hashlib.sha256((D/'video.mp4').read_bytes()).hexdigest(),'sourceManifestSha256':hashlib.sha256((D/'source-sha256.json').read_bytes()).hexdigest(),'frames':records}
(out/'frames.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(str(out/'frames.json'))
