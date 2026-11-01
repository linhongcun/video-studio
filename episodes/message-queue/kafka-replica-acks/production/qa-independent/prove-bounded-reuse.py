from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
from datetime import datetime,timezone
import json,hashlib,re
D=Path(__file__).resolve().parent.parent;Q=D/'qa-independent';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());old=(Q/'previous-main-title-v1.tsx').read_text();new=(D/'remotion/src/Main.tsx').read_text();before="8:'第二份写好了，主副本还要收到下一次进度报告'";after="8:(v.id==='all3-b2-reported'||v.id==='all3-wait-third')?'第二份进度已知，第三份仍在同步名单中':'第二份写好了，主副本还要收到下一次进度报告'";assert old.count(before)==1 and old.replace(before,after)==new;assert sha(D/'remotion/src/Main.tsx')=='5afaaccd438a9b3a60010bc4c28c4b09ed9d92bcea2937b8497a0da77b787ed8'
oldReports=[read(Q/'dynamic-v1.json'),read(Q/'motion-edges-v1.json')];oldSamples={s['frame']:s for r in oldReports for s in r['samples']};fresh=read(Q/'title-guard-v2.json');cmp=[]
for sample in fresh['samples']:
 f=sample['frame'];prior=oldSamples.get(f)
 if prior:
  a=Image.open(D/prior['file']).convert('RGB');b=Image.open(D/sample['file']).convert('RGB');bbox=ImageChops.difference(a,b).getbbox();expectedChange=2965<=f<=3300
  assert (bbox is not None)==expectedChange,(f,bbox)
  if bbox:assert bbox[0]>=98 and bbox[1]>=130 and bbox[2]<=1822 and bbox[3]<=192,(f,bbox)
  assert prior['metrics']['data']==sample['metrics']['data'],('NontextDOM',f)
  cmp.append({'frame':f,'oldPNG':prior['file'],'oldSHA256':prior['sha256'],'newPNG':sample['file'],'newSHA256':sample['sha256'],'pixelsEqual':bbox is None,'changedBBox':bbox,'nonTextDOMExactlyEqual':True})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for name in ['title-guard-v2','title-guard-caption-v2']:
 x=read(Q/(name+'.json'))
 for offset in range(0,len(x['samples']),12):
  im=Image.new('RGB',(1920,1540),(30,28,27));dr=ImageDraw.Draw(im)
  for j,s in enumerate(x['samples'][offset:offset+12]):
   xx=j%3*640;yy=j//3*385;im.paste(Image.open(D/s['file']).convert('RGB').resize((640,360)),(xx,yy+25));dr.text((xx+8,yy+3),str(s['frame'])+' '+str(s['metrics']['modelState']),font=font,fill='white')
  im.save(Q/(name+f'-contact-{offset//12+1:02}.jpg'),quality=93)
proof={'kind':'exact-source-difference-and-bounded-reuse-proof','atUTC':datetime.now(timezone.utc).isoformat(),'oldMainSHA256':sha(Q/'previous-main-title-v1.tsx'),'newMainSHA256':sha(D/'remotion/src/Main.tsx'),'exactOnlyReplacement':{'before':before,'after':after},'affectedVisualFrames':[2965,3300],'otherHandoffInputsUnchanged':all(sha(D/p)==h for p,h in read(Q/'dynamic-v1-spec.json')['sourceHashes'].items() if p!='remotion/src/Main.tsx'),'currentMatchingFrameComparisons':cmp,'beforeGuardExpectedFullPixelEquality':True,'afterGuardChangesConfinedToHeadingBBox':True,'nonTextDOMExactlyEqual':True,'primaryRawSamples':198,'wholePNGCurrentReusableSamples':sum(not 2965<=f<=3300 for f in oldSamples),'supersededHeadingPNGFrames':[f for f in oldSamples if 2965<=f<=3300],'oldFirstClipAffectedTail':[2965,3005],'oldFirstClipUnaffectedReusablePrefix':[2554,2964],'otherFiveClipsCompletelyOutsideAffectedFrames':True,'replacementContinuousWindow':[2847,3300],'limitations':'Original reports/artifacts retain e7dd identity. Only named unaffected whole PNG/clip scope and identical non-heading DOM/model values are reused; superseded title pixels are not accepted as current.'};assert proof['otherHandoffInputsUnchanged'];(Q/'bounded-reuse-title-v2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('proof comparisons',len(cmp),'reusablePNG',proof['wholePNGCurrentReusableSamples'],'superseded',proof['supersededHeadingPNGFrames'])
