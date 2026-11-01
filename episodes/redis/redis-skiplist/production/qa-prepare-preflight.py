#!/usr/bin/env python3
"""Build bounded real-timing QA sample plan after the actual storyboard exists.
No production import; phase choices are read from final animation source design.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
D=Path(__file__).resolve().parent
sb=json.loads((D/'storyboard.json').read_text());shots=[s for c in sb['scenes'] for s in c['shots']];total=sb['meta']['durationInFrames'];points=set();smoke=set();keypoints=set();events=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def span(s,i):
 a=s.get('cueFrames',{}).get('sentences',[None,None])[i]
 if a is None:a=s['voice'][i]['localStart']
 return float(a),float(s['voice'][i]['localEnd'])
def add(s,x,kind='boundary',key=False):
 f=s['from']+max(0,min(s['durationInFrames']-1,int(x)))
 points.add(f)
 if key:keypoints.add(f)
 return f
def event(s,sentence,count,fr,to,label):
 a,b=span(s,sentence);start=a+(b-a)*fr;length=((b-a)*(to-fr))/count
 for i in range(count):
  timing={}
  for phase in [0,.18,.45,.72,1]:
   f=start+length*(i+phase);boundary=math.ceil(f-1e-9);timing[str(phase)]=add(s,boundary,key=phase in [0,.45,.72,1])
   if phase in [.72,1]:add(s,boundary-1)
   if phase==.72:add(s,boundary+1)
  events.append({'shot':s['id'],'visualType':s['visualType'],'sentence':sentence,'operation':i,'label':label,'predictedPhases':timing})
for s in shots:
 for x in [0,s['durationInFrames']-1,s['durationInFrames']//2]:add(s,x)
 for i in [0,1]:
  a,b=span(s,i)
  for x in [math.floor(a),math.ceil(a),math.floor(b),math.ceil(b)]:add(s,x)
  smoke.add(add(s,(a+b)/2))
 for appear in s.get('cueFrames',{}).get('labels',{}).values():
  for x in [appear-1,appear,appear+63]:add(s,x)
 for cue in s.get('labels',[]):
  if 'appearFrame' in cue:
   for x in [cue['appearFrame']-1,cue['appearFrame'],cue['appearFrame']+63]:add(s,x)
 t=s['visualType']
 if t=='linear':event(s,0,5,.08,.96,'linear-forward');event(s,1,1,.08,.96,'linear-stop')
 elif t=='sparse':
  a,b=span(s,0)
  for p in [0,.22,.35,.5,.75,.94,1]:add(s,a+(b-a)*p,key=True)
 elif t=='upper':event(s,1,1,.08,.91,'upper-to40')
 elif t=='descend':event(s,0,1,.08,.91,'reject70');event(s,1,1,.08,.91,'same40-descend')
 elif t=='locate':event(s,0,1,.08,.93,'bottom-to50');event(s,1,1,.08,.93,'reject60')
 elif t=='height':
  a,b=span(s,1)
  for p in [0,.05,.1,.2,.3,.5,1]:add(s,a+(b-a)*p,key=True)
 elif t in ['splice-bottom','splice-upper']:event(s,0,2,.08,.96,'ordered-pointer-write')
by={s['visualType']:s for s in shots}
clips=[]
for name,first,last in [('search-forward-descend-locate','upper','locate'),('allocate-and-splice-both-levels','height','splice-upper')]:
 start=by[first]['from'];end=by[last]['from']+by[last]['durationInFrames']-1
 selected=sorted({start,end,*[f for f in keypoints if start<=f<=end]})
 # Keep genuine phase-adjacent frames for all arrivals, bounded to these two critical clips.
 for e in events:
  if start<=by[e['visualType']]['from']<=end:
   selected.extend([e['predictedPhases']['0.72']-1,e['predictedPhases']['0.72']])
 selected=sorted({f for f in selected if start<=f<=end})
 clips.append({'name':name,'range':[start,end],'reviewFrames':selected})
report={'status':'planned-not-rendered','scope':'Real sentence-window and event-boundary plan; silent continuous search and insertion clips supplement sampled DOM.','createdAtUTC':datetime.now(timezone.utc).isoformat(),'bodyFrames':total,'storyboardSHA256':sha(D/'storyboard.json'),'mainSourceSHA256':sha(D/'remotion/src/Main.tsx'),'frames':sorted(points),'smokeFrames':sorted(smoke),'events':events,'clips':clips,'limits':['Phase sampling is source-informed, not internal-word alignment.','Plan creation itself proves neither DOM correctness nor visual/motion quality.']}
(D/'qa-preflight-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'plannedFrames':len(points),'smokeFrames':len(smoke),'continuousClips':[(c['name'],c['range'],len(c['reviewFrames'])) for c in clips]}))
