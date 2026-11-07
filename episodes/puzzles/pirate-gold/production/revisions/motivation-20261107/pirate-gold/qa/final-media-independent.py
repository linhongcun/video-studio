import datetime,hashlib,json,pathlib,subprocess
from PIL import Image,ImageDraw
ROOT=pathlib.Path.cwd();OUT=ROOT/'qa/final-media-independent';video=ROOT/'video.mp4'
sha=hashlib.sha256(video.read_bytes()).hexdigest();assert sha=='228ec5fbc886bd1fb536664f7cea59ffe45b93a787d45a66a5a7a8039fd493f4'
frames=[1076,1077,1200,1299,1395,1405,1431,1487,1545,1604,1667,1697,1717,1796,1797,3420,4785,5226,5227,5376]
p=json.loads((ROOT/'storyboard.json').read_text());shots=[s for c in p['scenes'] for s in c['shots']]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(video)]))
select='+'.join('eq(n\\,%d)'%f for f in frames);rgb='zscale=matrixin=709:rangein=limited:matrix=gbr:range=full,format=gbrp,format=rgb24'
cmd=['ffmpeg','-v','error','-i',str(video),'-an','-vf','select='+select+','+rgb,'-fps_mode','vfr','-start_number','0',str(OUT/'extract-%03d.png')]
proc=subprocess.run(cmd,capture_output=True,text=True);assert proc.returncode==0,proc.stderr
records=[]
for i,f in enumerate(frames):
 src=OUT/('extract-%03d.png'%i);dst=OUT/('f%05d.png'%f);src.rename(dst);shot=next((s for s in shots if s['from']<=f<s['from']+s['durationInFrames']),None)
 im=Image.open(dst);records.append({'frame':f,'timeSeconds':f/30,'shot':shot['id'] if shot else 'sources','local':f-shot['from'] if shot else f-5227,'file':str(dst.relative_to(ROOT)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'size':im.size,'backgroundRGB':im.getpixel((1900,200))})
for k in range(5):
 canvas=Image.new('RGB',(1440,860),(33,29,42));d=ImageDraw.Draw(canvas)
 for j,rec in enumerate(records[k*4:(k+1)*4]):
  im=Image.open(ROOT/rec['file']);im.thumbnail((710,399));x=j%2*720;y=j//2*430;canvas.paste(im,(x,y+26));d.text((x+5,y+5),'frame%d | shot%s | local%d'%(rec['frame'],rec['shot'],rec['local']),fill='white')
 canvas.save(OUT/('contact-%02d.jpg'%(k+1)),quality=94)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':'video.mp4','sha256':sha,'probe':probe,'frames':records,'extraction':{'method':'Actual encoded MP4 via ffmpeg frame-number select; no source rendering','rgbDecoder':rgb,'command':cmd,'returnCode':proc.returncode,'stderr':proc.stderr,'throughLastFrame':5376},'visualReviewStatus':'pending'}
(ROOT/'qa/final-media-independent-extraction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sha256':sha,'frames':len(records),'probe':probe},ensure_ascii=False))
