"""Extract exact encoded frame numbers for independent visual review.

Writes only this task's motion evidence directory. It does not render sources,
change production inputs, judge legibility, or claim full realtime viewing.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[5]
EVIDENCE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--slug',choices=['twelve-balls','prisoners-light'],required=True)
parser.add_argument('--frames',required=True,help='Comma separated integer frame numbers')
parser.add_argument('--label',default='encoded-v1')
args=parser.parse_args()
revision=ROOT/'episodes/puzzles'/args.slug/'production/revisions/logic-20261111'/args.slug
video=revision/'video.mp4'
result=json.loads((revision/'render-result.json').read_text())
sha=hashlib.sha256(video.read_bytes()).hexdigest()
assert sha==result['sha256'],'Encoded media identity does not match actual render receipt'
frames=sorted(set(map(int,args.frames.split(','))))
assert frames and frames[0]>=0 and frames[-1]<result['frames']
out=EVIDENCE/args.slug/args.label
out.mkdir(parents=True,exist_ok=False)
storyboard=json.loads((revision/'storyboard.json').read_text())
shots=[shot for scene in storyboard['scenes'] for shot in scene['shots']]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
 'format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_transfer,color_primaries',
 '-of','json',str(video)]))
select='+'.join('eq(n\\,%d)'%f for f in frames)
rgb='zscale=matrixin=709:rangein=limited:matrix=gbr:range=full,format=gbrp,format=rgb24'
cmd=['ffmpeg','-v','error','-i',str(video),'-an','-vf','select='+select+','+rgb,
 '-fps_mode','vfr','-start_number','0',str(out/'extract-%03d.png')]
proc=subprocess.run(cmd,capture_output=True,text=True)
assert proc.returncode==0,proc.stderr
records=[]
for i,f in enumerate(frames):
 source=out/('extract-%03d.png'%i)
 target=out/('f%05d.png'%f)
 source.rename(target)
 shot=next((s for s in shots if s['from']<=f<s['from']+s['durationInFrames']),None)
 im=Image.open(target)
 records.append({'frame':f,'timeSeconds':f/30,'shot':shot['id'] if shot else 'sources',
  'local':f-shot['from'] if shot else f-result['bodyFrames'],
  'file':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
  'size':im.size,'backgroundRGB':im.getpixel((1900,200))})
contacts=[]
for k in range((len(records)+3)//4):
 canvas=Image.new('RGB',(1440,860),(33,29,42))
 draw=ImageDraw.Draw(canvas)
 for j,rec in enumerate(records[k*4:(k+1)*4]):
  im=Image.open(ROOT/rec['file'])
  im.thumbnail((710,399))
  x=j%2*720;y=j//2*430
  canvas.paste(im,(x,y+26))
  draw.text((x+5,y+5),'frame%d | shot%s | local%d'%(rec['frame'],rec['shot'],rec['local']),fill='white')
 target=out/('contact-%02d.jpg'%(k+1))
 canvas.save(target,quality=94)
 contacts.append(str(target.relative_to(ROOT)))
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'input':str(video.relative_to(ROOT)),'sha256':sha,'probe':probe,
 'sourceSHA256':{p:hashlib.sha256((revision/p).read_bytes()).hexdigest() for p in
  ['storyboard.json','remotion/src/Main.tsx','remotion/src/model.ts']},
 'frames':records,'contacts':contacts,
 'extraction':{'method':'Actual encoded MP4 via exact ffmpeg frame-number select; no source rendering',
  'rgbDecoder':rgb,'command':cmd,'returnCode':proc.returncode,'stderr':proc.stderr},
 'visualReviewStatus':'pending',
 'scope':'Selected encoded frames only. Review findings are written separately after images are actually viewed.'}
report_path=out/'extraction.json'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha256':sha,'frames':len(records),'report':str(report_path.relative_to(ROOT))}))
