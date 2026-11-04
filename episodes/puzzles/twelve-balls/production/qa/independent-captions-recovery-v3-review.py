from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1]
Q=D/'qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
R=json.loads((Q/'independent-captions-v3.json').read_text())
assert R['pass'] and R['sourceUnchanged'] and len(R['samples'])==30
O=Q/'independent-captions-v3-review';O.mkdir(exist_ok=False)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
sheets=[]
for k in range(0,30,6):
 subset=R['samples'][k:k+6];sheet=Image.new('RGB',(1680,len(subset)*148),(23,19,38));draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(subset):
  p=D/r['file'];assert sha(p)==r['sha256'];im=Image.open(p).convert('RGB');assert im.size==(1920,1080)
  draw.text((12,j*148+3),f"Sentence {k+j+1:02d} | shot {r['shot']} | exact frame {r['frame']}",font=font,fill=(240,235,248))
  sheet.paste(im.crop((120,824,1800,930)),(0,j*148+35))
 name=f'caption-band-{k//6+1:02d}.jpg';path=O/name;sheet.save(path,quality=95,subsampling=0)
 sheets.append({'file':str(path.relative_to(D)),'sha256':sha(path),'sourceFrames':[r['frame']for r in subset],'cropPixels':[120,824,1800,930]})
longest=max(range(30),key=lambda i:len(R['samples'][i]['metrics']['caption']['text']))
full=[]
for label,i in [('first',0),('middle',14),('longest',longest),('last',29)]:
 r=R['samples'][i];p=D/r['file'];target=O/f'full-{label}-sentence{i+1:02d}.jpg';Image.open(p).convert('RGB').save(target,quality=95,subsampling=0)
 full.append({'file':str(target.relative_to(D)),'sha256':sha(target),'sourceFile':r['file'],'sourceSHA256':r['sha256'],'sentence':i+1,'frame':r['frame'],'text':r['metrics']['caption']['text']})
assert all(sha(D/p)==h for p,h in R['sourceHashes'].items())
maxBodyBottom=max(t['y']+t['h']for r in R['samples']for t in r['metrics']['texts']if t['w']>0)
result={'executor':'/root/p06_recovery_qa/captions_recovery','createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceReport':'qa/independent-captions-v3.json','sourceReportSHA256':sha(Q/'independent-captions-v3.json'),'sourceSHA256':R['sourceHashes'],'automaticCaptionSamples':30,'exactNarrationAtAllSamples':True,'defaultProps':R['props'],'fontSizePixels':30,'maximumBodyTextBottom':maxBodyBottom,'minimumCaptionPanelTop':min(r['metrics']['caption']['bounds']['y']for r in R['samples']),'minimumSeparationPixels':min(r['metrics']['caption']['bounds']['y']for r in R['samples'])-maxBodyBottom,'sheets':sheets,'fullFrames':full,'visualReviewed':False,'limitations':['Static exact-frame renders and actual image review only; no full realtime playback or semantic audio audition.','No ASR or interior word-alignment claim; no physical phone.','Final encoded boundary and native player chrome remain separate final-media/site QA.']}
(O/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sheets':len(sheets),'fullFrames':len(full),'longestSentence':longest+1,'minimumSeparationPixels':result['minimumSeparationPixels']},ensure_ascii=False))
