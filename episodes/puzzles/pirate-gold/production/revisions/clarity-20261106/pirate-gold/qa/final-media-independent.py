import datetime,hashlib,json,pathlib,subprocess
from PIL import Image,ImageDraw
ROOT=pathlib.Path.cwd();OUT=ROOT/'qa/final-media-independent'
video=ROOT/'video.mp4';sha=hashlib.sha256(video.read_bytes()).hexdigest()
assert sha=='3e23ce93a913352e7ffd743af4548d571d8ddb2b6276e908a5291426f109b09b'
frames=sorted([188,600,950,1280,1591,1840,2090,2530,2765,3240,3610,3960,4108,4650,1573,1574,1665,2197,2198,2210,2234,2859,2860,2872,2896,3010,3874,4002,4003,4275,4276,4312,4800,4801,4950])
assert len(frames)==35 and len(set(frames))==35
p=json.loads((ROOT/'storyboard.json').read_text());shots=[s for c in p['scenes'] for s in c['shots']]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(video)]))
select='+'.join('eq(n\\,%d)'%f for f in frames)
rgb='zscale=matrixin=709:rangein=limited:matrix=gbr:range=full,format=gbrp,format=rgb24'
cmd=['ffmpeg','-v','error','-i',str(video),'-an','-vf','select='+select+','+rgb,'-fps_mode','vfr','-start_number','0',str(OUT/'extract-%03d.png')]
proc=subprocess.run(cmd,capture_output=True,text=True)
assert proc.returncode==0,proc.stderr
records=[]
for i,f in enumerate(frames):
 src=OUT/('extract-%03d.png'%i);dst=OUT/('f%05d.png'%f);src.rename(dst)
 shot=next((s for s in shots if s['from']<=f<s['from']+s['durationInFrames']),None)
 im=Image.open(dst);records.append({'frame':f,'timeSeconds':f/30,'shot':shot['id'] if shot else 'sources','local':f-shot['from'] if shot else f-4801,'file':str(dst.relative_to(ROOT)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'size':im.size,'backgroundRGB':im.getpixel((1900,200))})
for k in range(7):
 sub=records[k*5:(k+1)*5];canvas=Image.new('RGB',(1440,3*430),(33,29,42));d=ImageDraw.Draw(canvas)
 for j,rec in enumerate(sub):
  im=Image.open(ROOT/rec['file']);im.thumbnail((710,399));x=j%2*720;y=j//2*430
  canvas.paste(im,(x,y+26));d.text((x+5,y+5),'frame%d | shot%s | %.3fs'%(rec['frame'],rec['shot'],rec['timeSeconds']),fill=(255,255,255))
 canvas.save(OUT/('contact-%02d.jpg'%(k+1)),quality=94)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':'video.mp4','sha256':sha,'probe':probe,'frames':records,'extraction':{'method':'Actual encoded MP4 via ffmpeg frame-number select; no source rendering','rgbDecoder':rgb,'command':cmd,'returnCode':proc.returncode,'stderr':proc.stderr,'throughLastFrame':4950},'visualReviewStatus':'pending'}
(ROOT/'qa/final-media-independent-extraction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'inputSHA':sha,'frames':len(records),'output':str(OUT),'backgroundRGBs':sorted(set(tuple(r['backgroundRGB']) for r in records))}))
