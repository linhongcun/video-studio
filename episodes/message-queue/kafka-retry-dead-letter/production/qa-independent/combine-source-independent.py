from pathlib import Path
import json,hashlib,math
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent.parent;Q=D/'qa-independent';O=Q/'source-contacts';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=[(n,json.loads((Q/n).read_text())) for n in ['frames-final.json','frames-after-06-correction.json']];assert raw[0][1]['sourceHashes']==raw[1][1]['sourceHashes'];assert all(r['sourceUnchanged'] and not r['console'] for _,r in raw)
spec=json.loads((Q/'frame-spec.json').read_text());expected={s['frame']:s for s in spec['samples']};model={s['id']:s for s in json.loads((D/'model.json').read_text())['timeline']};items=[];errors=[]
for name,r in raw:
 for x in r['samples']:
  f=x['frame'];s=expected[f];m=model[s['expectedState']];c=m['consumer'];q=m['dlq'];j=m['journal'];world=[e['attrs'] for e in x['metrics']['data'] if 'data-model-state' in e['attrs']];assert len(world)==1;world=world[0];jd=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
  attrs={**s['expectedDom'],'data-current-result':q['senderObservedResult'] if c['active'] else 'none','data-current-metadata':jd(q['metadata'] if c['active'] else None),'data-last-observed-future':q['futureState'],'data-last-observed-result':q['senderObservedResult'],'data-last-observed-metadata':jd(q['metadata']),'data-consumer-active':str(c['active']).lower(),'data-consumer-paused':str(c['paused']).lower(),'data-consumer-position':str(c['position']) if c['position'] is not None else 'none','data-consumer-held':c['heldEventId'] or 'none','data-business-invocations':str(m['business']['invocations']),'data-business-known-complete':str(m['business']['knownComplete']).lower()}
  mismatches=[{'field':k,'expected':v,'actual':world.get(k)} for k,v in attrs.items() if world.get(k)!=v];text='\n'.join(t['text'] for t in x['metrics']['texts'])
  if 'reserved' in m['id'] and s['shot']!='15' and '本次尚未调用' not in text:mismatches.append({'field':'reserved-current-label','expected':'本次尚未调用','actual':text})
  if m['id']=='dlq-ack-before-journal' and '本机确认尚未保存' not in text:mismatches.append({'field':'ack-before-journal-label','expected':'本机确认尚未保存','actual':text})
  assert sha(D/x['file'])==x['sha256'];issues={'geometry':x['violations'],'collisions':x['metrics']['collisions'],'subtitles':x['metrics']['subtitles'],'semantic':mismatches};bad=bool(issues['geometry'] or issues['collisions'] or issues['subtitles'] or issues['semantic']);
  if bad:errors.append({'frame':f,**issues})
  items.append({'frame':f,'shot':s['shot'],'modelState':m['id'],'file':x['file'],'sha256':x['sha256'],'rawReport':name,'rawExpectedState':x.get('expectedState'),'expectedDom':attrs,'pass':not bad})
items.sort(key=lambda x:x['frame']);assert len(items)==len(expected)==128 and len({x['frame'] for x in items})==128
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);contacts=[]
for offset in range(0,len(items),6):
 chunk=items[offset:offset+6];im=Image.new('RGB',(1280,392*math.ceil(len(chunk)/2)),(20,20,20));draw=ImageDraw.Draw(im)
 for k,x in enumerate(chunk):
  xx=(k%2)*640;yy=(k//2)*392
  with Image.open(D/x['file']) as pic:im.paste(pic.convert('RGB').resize((640,360)),(xx,yy+32))
  draw.text((xx+7,yy+7),'f'+str(x['frame'])+' shot'+x['shot']+' '+x['modelState'],font=font,fill=(255,234,210))
 p=O/('contact-source-'+str(offset//6+1).zfill(2)+'.jpg');im.save(p,quality=92);contacts.append({'file':str(p.relative_to(D)),'sha256':sha(p),'frames':[x['frame'] for x in chunk]})
report={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'kind':'independent-combined-source-DOM-review-after-narrow-QA-reference-correction','sourceHashes':raw[0][1]['sourceHashes'],'freshFrames':128,'bodyStages':46,'visibleModelStates':len({x['modelState'] for x in items}),'rawReports':[{'file':n,'sha256':sha(Q/n),'originalMachinePass':r['machinePass']} for n,r in raw],'firstAttemptCorrection':'06-anchor-expectation-correction.json; original false report/PNG preserved, only stale expected anchor corrected.','currentVsHistoricalResultScope':'Inactive process current Future/result/metadata must be none/none/null; data-last-observed* retains qualified pre-exit history. New process C has no inherited current result.','samples':items,'contacts':contacts,'errors':errors,'machinePass':not errors,'visualReviewed':False,'sourceUnchanged':all(sha(D/n)==h for n,h in raw[0][1]['sourceHashes'].items())}
(Q/'frames-combined-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'machinePass':report['machinePass'],'frames':len(items),'contacts':len(contacts),'errors':errors},ensure_ascii=False))
