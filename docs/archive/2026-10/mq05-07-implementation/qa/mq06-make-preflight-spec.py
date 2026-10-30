"""Plan fresh boundary samples from the author's declared real-voice timing table.

The declarations select samples, not prove behavior. Actual DOM/state/text/motion
and images are checked independently against source/model causality afterward.
"""
from pathlib import Path
import argparse,hashlib,json,math
ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True,type=Path);args=ap.parse_args();D=args.dir.resolve();Q=D/'qa-independent';Q.mkdir(exist_ok=True)
assert hashlib.sha256((D/'voice.wav').read_bytes()).hexdigest()=='a4f16ecbbaccc4851dfe794f57c5eaeafc07f00614ce9fc5586fb9c9c03588b8'
assert hashlib.sha256((D/'storyboard.json').read_bytes()).hexdigest()=='e838f630acaa2966337a5fe1eb149b1fd528a530f9ee6a1bd261dc50037f2dd7'
board=json.loads((D/'storyboard.json').read_text());timing=json.loads((D/'qa/state-timing.json').read_text());figures=json.loads((D/'article-figure-plan.json').read_text())['figures']
assert [f['frame']for f in figures]==[1642,2430,3825,4214]
shots=[s for scene in board['scenes']for s in scene['shots']];decl={s['shot']:s for s in timing['shots']};byframe={};cursor=0
for s in shots:assert s['from']==cursor;cursor+=s['durationInFrames']
assert cursor==timing['bodyFrames']==4966
def expected(shot,frame):
 values=[x for x in decl[shot]['states']if x['firstGlobalInteger']<=frame]
 return values[-1]['id']if values else None
def add(shot,frame,reason):
 s=next(s for s in shots if s['id']==shot);frame=max(s['from'],min(s['from']+s['durationInFrames']-1,int(frame)))
 item=byframe.setdefault(frame,{'frame':frame,'shot':shot,'reasons':[]});item['reasons'].append(reason)
 value=expected(shot,frame)
 if value:item['expectedState']=value
for s in shots:
 key=s['id'];d=decl[key];assert d['from']==s['from']and d['duration']==s['durationInFrames']
 for label,local in [('middle',s['durationInFrames']//2)]:add(key,s['from']+local,label)
 if key in ['01','09','12','13','14']:add(key,s['from'],'global or branch first')
 if key in ['08','11','12','14']:add(key,s['from']+s['durationInFrames']-1,'branch or body last')
 for state in d['states'][1:]:
  f=state['firstGlobalInteger']
  for delta in [-1,0]:add(key,f+delta,'adjacent transition into '+state['id'])
  if key in ['05','07','11','12']:add(key,f+1,'critical first+1 hold '+state['id'])
 reset=d.get('resetOverlayEnd')
 if reset is not None:
  # Owner table stores the first global integer where the overlay is absent.
  if isinstance(reset,dict):reset=reset['firstGlobalInteger']
  assert isinstance(reset,int) and s['from']<=reset<s['from']+s['durationInFrames']
  for delta in [-1,0,1]:add(key,reset+delta,'reset overlay boundary')
 for i,state in enumerate(d['states']):
  if 'inflight'in state['id']or state['id']in ['collector-paid','collector-buffered-both','serial-paid-done','ordered-paid-done','async-paid-resumed']:
   last=d['states'][i+1]['firstGlobalInteger']-1 if i+1<len(d['states'])else s['from']+s['durationInFrames']-1
   add(key,(state['firstGlobalInteger']+last)//2,'active movement or causality hold '+state['id'])
for figure in figures:
 frame=figure['frame'];s=next(s for s in shots if s['from']<=frame<s['from']+s['durationInFrames']);assert figure['seconds']==frame/30
 add(s['id'],frame,'exact article Figure '+figure['file'])
spec={'kind':'independent-sample-plan','timingSource':'Author declared measured sentence thresholds, independently checked actual frames afterward','timingTableSHA256':hashlib.sha256((D/'qa/state-timing.json').read_bytes()).hexdigest(),'boardSHA256':hashlib.sha256((D/'storyboard.json').read_bytes()).hexdigest(),'samples':[byframe[f]for f in sorted(byframe)]}
(Q/'preflight-v1-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
clips={'clips':[{'name':'route-result-boundary','from':1515,'to':1625},{'name':'serial-completion-before-next-start','from':2470,'to':2660},{'name':'async-common-input-reset','from':2880,'to':3060}]}
(Q/'continuous-v1-spec.json').write_text(json.dumps(clips,indent=2)+'\n');print('planned',len(spec['samples']),'fresh frames and',len(clips['clips']),'bounded clips')
