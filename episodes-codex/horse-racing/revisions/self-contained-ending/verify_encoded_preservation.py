#!/usr/bin/env python3
"""Read-only media comparison, with reports under this revision and PNGs ignored.

These sampled comparisons support codec/identity preservation and preview fidelity;
they do not establish all-frame perceptual equivalence or full-film listening.
"""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parent
D=R.parents[1]
P=D/'remotion/out/self-contained-ending-stills-v2'
O=D/'remotion/out/ending-root-encoded';O.mkdir(parents=True,exist_ok=True)
VIDEO=D/'video.mp4'
OLD=D/'remotion/out/ending-baseline-v0.55.0.mp4'
THRESHOLD_PREVIEW=3.0
THRESHOLD_PREFIX=1.0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'samples.json').read_text())
rows={r['frame']:r for r in manifest['samples']}
frames=sorted(set(rows)|{5874,5875,5876,8975})

def extract(source,values,out):
    out.mkdir(parents=True,exist_ok=True)
    expression='+'.join(f'eq(n,{n})' for n in values)
    command=['ffmpeg','-y','-v','error','-i',str(source),'-vf',f"select='{expression}',scale=960:540",'-fps_mode','vfr',str(out/'frame-%04d.png')]
    subprocess.run(command,check=True)
    files=sorted(out.glob('frame-*.png'));assert len(files)==len(values),(source,len(files),len(values))
    return dict(zip(values,files)),command

new,command=extract(VIDEO,frames,O/'current')
preview=[]
for frame,row in rows.items():
    a=np.asarray(Image.open(new[frame]).convert('RGB'),dtype=np.int16)
    b=np.asarray(Image.open(row['file']).convert('RGB'),dtype=np.int16)
    diff=float(np.abs(a-b).mean())
    preview.append(dict(frame=frame,shot=row['shot'],meanAbsoluteRGBError=diff,
                        reference=row['file'],referenceSHA256=sha(Path(row['file'])),decoded=str(new[frame])))
prefix_frames=[0,2914,5816,5874]
old,old_command=extract(OLD,prefix_frames,O/'baseline')
prefix=[]
for frame in prefix_frames:
    a=np.asarray(Image.open(new[frame]).convert('RGB'),dtype=np.int16)
    b=np.asarray(Image.open(old[frame]).convert('RGB'),dtype=np.int16)
    prefix.append(dict(frame=frame,meanAbsoluteRGBError=float(np.abs(a-b).mean())))
selected=[0,5816,5874,5875,5876,6255,6662,7027,7358,7735,7743,8136,8144,8568,8577,8968,8975]
contact=Image.new('RGB',(960*3,570*((len(selected)+2)//3)),(8,16,30));draw=ImageDraw.Draw(contact)
for i,frame in enumerate(selected):
    x=(i%3)*960;y=(i//3)*570
    draw.text((x+12,y+6),f'Final MP4 display frame {frame}',fill=(225,232,240))
    contact.paste(Image.open(new[frame]).convert('RGB'),(x,y+30))
contact_path=R/'encoded-contact.jpg';contact.save(contact_path,quality=88)
report={'videoSHA256':sha(VIDEO),'baselineVideoSHA256':sha(OLD),'previewSourceSHA':manifest['sourceSHA'],
        'thresholdMeanRGB':THRESHOLD_PREVIEW,'maximumMeanRGB':max(r['meanAbsoluteRGBError'] for r in preview),
        'previewSamples':preview,'prefixThresholdMeanRGB':THRESHOLD_PREFIX,
        'prefixSamples':prefix,'decodedFrames':frames,'commands':[command,old_command],
        'contactSHA256':sha(contact_path),
        'scope':'43 preview references plus seam/final display frames; 4 old/new encoded prefix samples. Not all frames visually watched or full human listening.'}
report['passed']=report['maximumMeanRGB']<=THRESHOLD_PREVIEW and max(r['meanAbsoluteRGBError'] for r in prefix)<=THRESHOLD_PREFIX
(R/'qa-encoded-preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['videoSHA256','maximumMeanRGB','prefixSamples','passed']},ensure_ascii=False,indent=2))
assert report['passed'],'Inspect the measured mismatch before publication'
