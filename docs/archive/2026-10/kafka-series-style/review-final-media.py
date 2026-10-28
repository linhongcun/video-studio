#!/usr/bin/env python3
"""Read-only Kafka final MP4 sampling. Production input/source is never changed.

--prepare only writes the frame plan. Extraction uses integer decoded-frame n,
not approximate seek timestamps. One sampling pass through the final file is
used; no separate redundant full-decode validation is performed.
"""
import argparse,datetime,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/workspace/video-studio')
D=ROOT/'episodes-codex/message-queue/revisions/kafka-intro/message-queue'
OUT=Path('/workspace/work/kafka-production/final-media-review')
BODY_FRAMES=3697
FINAL_FRAMES=3847
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def make_plan():
 sb=json.loads((D/'storyboard.json').read_text());shots=[s for c in sb['scenes'] for s in c['shots']]
 by={int(s['id']):s for s in shots};frames={}
 def add(n,reason):
  assert isinstance(n,int) and 0<=n<FINAL_FRAMES
  frames.setdefault(n,[]).append(reason)
 for s in shots:add(s['from']+math.floor(s['durationInFrames']*.5+.5),'shot-'+s['id']+'-representative')
 # Inherited current code uses exact unrounded voice windows. At ceil(end)
 # the corresponding interpolation first reaches its completed state.
 s=by[3];v=s['voice'];firstEnd=v[0]['localEnd'];secondStart=v[1]['localStart'];secondEnd=v[1]['localEnd']
 add(s['from']+60,'append-moving-7042')
 for local,label in [(math.ceil(firstEnd-12),'append-offset0-landed'),(math.ceil(secondStart+(secondEnd-secondStart)*.42),'append-offset1-landed'),(math.ceil(secondEnd-12),'append-offset2-landed')]:add(s['from']+local,label)
 s=by[6];end=s['from']+math.ceil(s['voice'][0]['localEnd']-8)
 for n in [s['from']+66,end-1,end,end+1]:add(n,'read-packet-mid-or-arrival-boundary')
 s=by[7];end=s['from']+math.ceil(s['voice'][0]['localEnd']-4)
 for n in [end-1,end,end+1]:add(n,'business-save-boundary')
 for n in [2303,2304,2305]:add(n,'commit-first-1-boundary')
 s=by[10];a=s['voice'][1]['localStart'];b=s['voice'][1]['localEnd'];end=s['from']+math.ceil(a+(b-a)*.66)
 for n in [end-1,end,end+1]:add(n,'page-query-response-complete-boundary')
 s=by[11];a=s['voice'][0]['localEnd'];ss=s['voice'][1]['localStart'];se=s['voice'][1]['localEnd'];zero=s['from']+math.ceil(a-63);resetStart=s['from']+math.ceil(ss-18);resetEnd=s['from']+math.ceil(ss+27)
 for n in [zero-1,zero,zero+1,resetStart-1,resetStart,resetStart+1,resetEnd-1,resetEnd,resetEnd+1]:add(n,'buffer-zero-hold-or-explicit-reset-boundary')
 available=max(80,se-(ss+27)-12)
 for k in range(1,5):add(s['from']+math.ceil(ss+27+available*k/4),'continuous-flow-window-'+str(k))
 for n in [1170,1725,2310,2925]:add(n,'article-figure-exact-planned-frame')
 for n in [3696,3697,3772,3846]:add(n,'body-reference-boundary-or-reference-middle-last')
 plan={'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bodyFrames':BODY_FRAMES,'finalFrames':FINAL_FRAMES,'expectedFinalSeconds':FINAL_FRAMES/30,'sourceMainSha256':sha(D/'remotion/src/Main.tsx'),'storyboardSha256':sha(D/'storyboard.json'),'frozenManifestSha256':sha(D/'source-sha256.json'),'frameCount':len(frames),'frames':[{'frame':n,'reasons':r} for n,r in sorted(frames.items())],'pixelComparisonRoi':[0,0,1920,910],'pixelScope':'Only exact representative frames and cited source images, crop excludes burned subtitles starting y925; H264 compression difference permitted. Not a full-video equivalence claim.'}
 return plan

def load_sources(path):
 if not path:return {}
 doc=json.loads(path.read_text());return {int(k):Path(v) for k,v in doc['frames'].items()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--source-map',type=Path);args=ap.parse_args();OUT.mkdir(exist_ok=True)
 plan=make_plan();(OUT/'frame-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 if args.prepare:print(json.dumps({'prepared':True,'sampleCount':plan['frameCount'],'plan':str(OUT/'frame-plan.json')}));return
 video=D/'video.mp4';receipt=json.loads((D/'reference-appendix.json').read_text());result=json.loads((D/'render-result.json').read_text());media=json.loads((D/'reference-appendix-media-check.json').read_text())
 assert receipt['bodyFrames']==BODY_FRAMES and receipt['finalVideoFrames']==FINAL_FRAMES
 assert receipt['appendix']['from']==BODY_FRAMES and receipt['appendix']['durationInFrames']==150 and len(receipt['appendix']['pages'])==1
 actual=sha(video);assert actual==receipt['outputSHA256']==result['sha256'];assert media['passed'] is True
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',FINAL_FRAMES)
 assert v['codec_name']=='h264' and a['codec_name']=='aac' and int(a['sample_rate'])==48000
 assert abs(float(v['duration'])-FINAL_FRAMES/30)<1e-5
 expectedTitles=[{'id':'R1','title':'Introduction','credit':'Apache Kafka'},{'id':'R2','title':'Design','credit':'Apache Kafka'},{'id':'R3','title':'Producer Configs','credit':'Apache Kafka'}]
 assert receipt['bibliography']==expectedTitles and receipt['presentation']=='title-author' and receipt['layout']['quotesRendered'] is False
 extraction=OUT/'encoded-frames';extraction.mkdir(exist_ok=True)
 for p in extraction.glob('sample-*.png'):p.unlink()
 select='+'.join('eq(n\\,'+str(x['frame'])+')' for x in plan['frames'])
 command=['ffmpeg','-v','error','-i',str(video),'-vf','select='+select,'-fps_mode','vfr',str(extraction/'sample-%03d.png')]
 subprocess.run(command,check=True)
 raw=sorted(extraction.glob('sample-*.png'));assert len(raw)==plan['frameCount'],(len(raw),plan['frameCount'])
 samples=[];sources=load_sources(args.source_map)
 for entry,p in zip(plan['frames'],raw):
  frame=entry['frame'];dest=extraction/f'frame-{frame:05d}.png';p.replace(dest);record={**entry,'file':str(dest),'sha256':sha(dest)}
  with Image.open(dest) as im:assert im.size==(1920,1080)
  if frame in sources:
   source=sources[frame];record['sourceImage']={'path':str(source),'sha256':sha(source)}
   with Image.open(dest) as im,Image.open(source) as original:
    aa=np.asarray(im.convert('RGB').crop((0,0,1920,910)),dtype=np.int16);bb=np.asarray(original.convert('RGB').crop((0,0,1920,910)),dtype=np.int16);delta=np.abs(aa-bb)
   record['sourceComparison']={'roi':[0,0,1920,910],'meanAbsoluteRgbError':float(delta.mean()),'p99AbsoluteRgbError':float(np.quantile(delta,.99)),'maxAbsoluteRgbError':int(delta.max()),'screeningPassed':float(delta.mean())<=3 and float(np.quantile(delta,.99))<=35}
  if frame>=BODY_FRAMES:
   reference=D/'revisions/reference-endcards'/receipt['appendix']['pages'][0]['file'];assert sha(reference)==receipt['appendix']['pages'][0]['sha256']
   with Image.open(dest) as im,Image.open(reference) as original:
    aa=np.asarray(im.convert('RGB'),dtype=np.int16);bb=np.asarray(original.convert('RGB'),dtype=np.int16);delta=np.abs(aa-bb)
   record['referenceCardComparison']={'fullFrameMeanAbsoluteRgbError':float(delta.mean()),'p99AbsoluteRgbError':float(np.quantile(delta,.99)),'screeningPassed':float(delta.mean())<=3 and float(np.quantile(delta,.99))<=35}
  if frame in [1170,1725,2310,2925]:
   index=[1170,1725,2310,2925].index(frame)+1
   with Image.open(dest) as im:im.convert('RGB').save(OUT/f'article-{index:02}.jpg',quality=95)
   record['articleFigureJpeg']=str(OUT/f'article-{index:02}.jpg')
  samples.append(record)
 # Contact sheets are review aids; exact originals remain beside them.
 font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
 for key,chosen in [('representatives',[s for s in samples if any('representative' in r for r in s['reasons'])]),('boundaries',[s for s in samples if not any('representative' in r for r in s['reasons'])])]:
  for group in range((len(chosen)+7)//8):
   subset=chosen[group*8:(group+1)*8];sheet=Image.new('RGB',(1920,math.ceil(len(subset)/2)*580),(25,23,22));draw=ImageDraw.Draw(sheet)
   for i,r in enumerate(subset):
    x=(i%2)*960;y=(i//2)*580
    with Image.open(r['file']) as im:sheet.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+10,y+544),f"frame {r['frame']}  "+','.join(r['reasons'])[:65],font=font,fill='#FFF1E8')
   sheet.save(OUT/f'{key}-{group+1:02}.jpg',quality=94)
 report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'encoded sampling produced; actual visual review remains required','video':str(video),'sha256':actual,'format':{'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'videoSeconds':float(v['duration']),'audioCodec':a['codec_name'],'audioSampleRate':a['sample_rate']},'renderResultSha256':sha(D/'render-result.json'),'receiptSha256':sha(D/'reference-appendix.json'),'canonicalMediaCheckSha256':sha(D/'reference-appendix-media-check.json'),'priorCanonicalFullMediaChecksPassed':media['passed'],'notRepeated':'No independent full decode/null run or full frame/audio-packet/PCM comparison. Inherited full media report is recorded; a single exact integer-n sampling extraction was run.','bibliography':expectedTitles,'plan':plan,'samples':samples,'sourceComparisonCount':sum('sourceComparison' in s for s in samples),'sourcePixelScreeningPassed':all(s.get('sourceComparison',{}).get('screeningPassed',True) and s.get('referenceCardComparison',{}).get('screeningPassed',True) for s in samples),'visualReviewed':False,'limitations':'No word ASR, full semantic listening or physical mobile-device claim.'}
 assert plan['frozenManifestSha256']==sha(D/'source-sha256.json') and plan['sourceMainSha256']==sha(D/'remotion/src/Main.tsx')
 (OUT/'encoded-sampling-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sampled':len(samples),'sourceComparisons':report['sourceComparisonCount'],'pixelScreeningPassed':report['sourcePixelScreeningPassed'],'report':str(OUT/'encoded-sampling-report.json')}))
if __name__=='__main__':main()
