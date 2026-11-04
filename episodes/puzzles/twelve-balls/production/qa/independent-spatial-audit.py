#!/usr/bin/env python3
"""Inspect actual preview DOM circles versus foreign text; report candidates, do not infer visual approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math
D=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--preview',required=True);p.add_argument('--out-name',required=True);a=p.parse_args()
source=D/'qa'/f'{a.preview}.json';target=D/'qa'/f'{a.out_name}.json';assert not target.exists()
r=json.loads(source.read_text());circle_text=[];text_text=[];pairs=0
for sample in r['samples']:
 for candidate in sample['metrics']['overlapCandidates']:
  text_text.append({'frame':sample['frame'],'shot':sample['shot'],**candidate})
 balls=[s for s in sample['metrics']['states'] if 'data-ball' in s['attrs'] and s['circle']]
 for ball in balls:
  c=ball['circle'];cx=c['x']+c['w']/2;cy=c['y']+c['h']/2;radius=min(c['w'],c['h'])/2
  for t in sample['metrics']['texts']:
   pairs+=1
   if t['text'].strip()==ball['attrs']['data-ball']:continue
   nearx=max(t['x'],min(cx,t['x']+t['w']));neary=max(t['y'],min(cy,t['y']+t['h']));distance=math.hypot(cx-nearx,cy-neary)
   if distance<radius-1:
    circle_text.append({'frame':sample['frame'],'shot':sample['shot'],'ball':ball['attrs']['data-ball'],'foreignText':t['text'],'distanceToTextRectangle':distance,'radius':radius,'textBounds':t})
result={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'executor':'AI agent independent actual-DOM spatial audit','preview':str(source.relative_to(D)),'previewSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'samples':len(r['samples']),'circleTextPairChecks':pairs,'foreignCircleTextCandidates':circle_text,'textTextRectangleCandidates':text_text,'scope':'Geometric candidates from actual browser DOM. Text ranges include font ascender/descender space; actual raster review is separate and no automatic visual approval is asserted.'}
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'samples':len(r['samples']),'foreignCircleTextCandidates':len(circle_text),'textTextRectangleCandidates':len(text_text)}))
