"""Audit immutable final bytes and extract review frames; never changes media input."""
from pathlib import Path
import hashlib,json,subprocess,shutil
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'source-sha256.json').read_text())
assert not [p for p,h in manifest.items() if sha(D/p)!=h]
video=D/'video.mp4'
# Explicit single-thread decoder so post-render audit stays light on the shared host.
r=subprocess.run(['ffmpeg','-v','error','-xerror','-threads','1','-i',str(video),'-f','null','-'],capture_output=True,text=True)
(D/'qa-evidence').mkdir(exist_ok=True)
(D/'qa-evidence/full-decode.log').write_text(r.stderr)
assert r.returncode==0,r.stderr
sb=json.loads((D/'storyboard.json').read_text());shots=[q for s in sb['scenes'] for q in s['shots']]
frames=[('first',0)]+[(q['id'],q['from']+round(q['durationInFrames']*.65)) for q in shots]+[('last',sb['meta']['durationInFrames']-1)]
records=[]
for name,fr in frames:
 out=D/'qa-evidence'/f'final-{name}.png'
 subprocess.run(['ffmpeg','-v','error','-threads','1','-y','-ss',str(fr/30),'-i',str(video),'-frames:v','1','-vf','scale=960:540','-threads','1',str(out)],check=True)
 records.append({'name':name,'frame':fr,'path':str(out.relative_to(D)),'sha256':sha(out)})
(D/'qa-evidence/final-frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
for size in ['16x9','4x3','3x4']:
 subprocess.run(['ffmpeg','-v','error','-threads','1','-y','-i',str(D/f'cover-{size}.png'),'-frames:v','1','-q:v','2','-threads','1',str(D/f'cover-{size}.jpg')],check=True)
shutil.copy2(D/'cover-3x4.jpg',D/'poster.jpg')
media=['video.mp4','voice.wav','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','captions.srt','storyboard.json','words.json','source-sha256.json']
result=json.loads((D/'render-result.json').read_text());proposal=json.loads((D/'site-meta-proposal.json').read_text())
delivery={'slug':D.name,'episode':proposal['ep'],'title':proposal['title'],'finalVideoFrames':result['videoFrames'],'durationSeconds':result['seconds'],'width':result['width'],'height':result['height'],'fps':30,'mediaSha256':{p:sha(D/p) for p in media},'sourceInputsVerified':len(manifest),'fullDecodePassed':True,'actualMp4ReviewFrames':records,'captionCheckBasis':'Storyboard subtitles equal frozen narration text with measured sentence envelopes; no ASR claim.','audioReviewLimit':'No word-level ASR or full human listening completed.','actualFrameReviewStatus':'Awaiting model inspection of extracted final MP4 frames.','siteMetadata':'site-meta-proposal.json','siteIntegrationAndPublication':'Pending root; this worker has not modified episodes/ or published.'}
(D/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'slug':D.name,'frames':result['videoFrames'],'sha256':sha(video),'fullDecodePassed':True,'reviewFrames':len(records)},ensure_ascii=False))
