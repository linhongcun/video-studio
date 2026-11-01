from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent
sb=json.loads((D/'storyboard.json').read_text());shots=[s for sc in sb['scenes'] for s in sc['shots']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['python3',str(D/'verify-freeze.py')],check=True)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(D/'video.mp4')]))
v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert int(v['nb_frames'])==sb['meta']['durationInFrames']
assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1')
assert abs(float(v['duration'])-int(v['nb_frames'])/30)<.04
subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(D/'video.mp4'),'-f','null','-'],check=True)
E=D/'qa-evidence/final';E.mkdir(parents=True,exist_ok=True)
items=[('first',0),('last',int(v['nb_frames'])-1)]
for s in shots:items.append((s['id']+'-hold',s['from']+round(s['durationInFrames']*.65)))
key={12:['03','05','08'],13:['03','07','09'],14:['04','07','10']}[sb['meta']['episode']]
for s in shots:
 if s['id'] in key:
  for i,p in enumerate([0,.38,.8]):items.append((s['id']+'-phase'+str(i),s['from']+round((s['durationInFrames']-1)*p)))
frames=sorted(set(f for _,f in items));lookup={f:i+1 for i,f in enumerate(frames)}
select='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-i',str(D/'video.mp4'),'-vf',f"select='{select}',scale=960:540",'-vsync','0','-q:v','3',str(E/'%03d.jpg')],check=True)
records=[dict(name=n,frame=f,file=f'{lookup[f]:03d}.jpg') for n,f in sorted(items,key=lambda q:q[1])]
(E/'frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
flow={12:('05','06'),13:('08','09'),14:('03','04')}[sb['meta']['episode']]
first=next(s for s in shots if s['id']==flow[0]);last=next(s for s in shots if s['id']==flow[1]);start=first['from']/30;dur=(last['from']+last['durationInFrames']-first['from'])/30
subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-ss',str(start),'-i',str(D/'video.mp4'),'-t',str(dur),'-vf','crop=1920:900:0:0,scale=960:450','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','1',str(E/'flow-body-silent.mp4')],check=True)
mix=json.loads((D/'remotion/out/mix-report.json').read_text())
media={str(p.relative_to(D)):sha(p) for p in [D/'video.mp4',D/'voice.wav',D/'cover-16x9.jpg',D/'cover-4x3.jpg',D/'cover-3x4.jpg',D/'poster.jpg']}
r=dict(episode=sb['meta']['episode'],title=sb['meta']['title'],date='2026-10-24',width=1920,height=1080,fps=30,frames=int(v['nb_frames']),seconds=int(v['nb_frames'])/30,videoSha256=media['video.mp4'],mediaSha256=media,sourceManifestSha256=sha(D/'source-sha256.json'),frozenInputsVerified=True,fullDecodePassed=True,audioCodec=a['codec_name'],audioChannels=a['channels'],mix=mix,finalFrameRecords='qa-evidence/final/frames.json',finalFlow='qa-evidence/final/flow-body-silent.mp4',decodedFramesReviewed=False,asr=False,independentListening=False)
(D/'render-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['episode','frames','seconds','videoSha256','frozenInputsVerified','fullDecodePassed']},ensure_ascii=False))
