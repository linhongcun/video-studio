#!/usr/bin/env python3
"""Plan bounded height-choice QA from the real fresh3/reused17 storyboard."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((D/'storyboard.json').read_text());shots=[x for c in s['scenes'] for x in c['shots']];by={x['id']:x for x in shots}
assert sha(D/'height-options.json')=='ca0abf5dcef32e4cb96cd5912530a6b922a66894461a21d1a6b5be47b0700e50'
assert sum(x['durationInFrames'] for x in shots)==4557
h=by['07'];c=h['cueFrames']['sentences'][1];d=h['voice'][1]['localEnd'];cue=h['cueFrames']['labels']['层高'];reset=c+(d-c)*.2;fade_end=c+(d-c)*.45
first_allocated=math.ceil(reset);first_full=math.ceil(fade_end)
def alpha(f):
 t=max(0,min(1,(f-reset)/(fade_end-reset)));return t*t*(3-2*t)
first_visible=next(f for f in range(first_allocated,first_full+1) if alpha(f)>.04)
hold=min(h['durationInFrames']-1,first_full+round(2.5*s['meta']['fps']))
locals_=sorted(set([0,cue-1,cue,cue+1,c//2,c-1,c,(c+first_allocated-1)//2,first_allocated-1,first_allocated,first_visible-1,first_visible,round((reset+fade_end)/2),math.floor(fade_end),first_full,hold,h['durationInFrames']-1]))
frames={881,955,1382,*[h['from']+f for f in locals_]};events=[]
for identity in ['08','09']:
 shot=by[identity];a=shot['cueFrames']['sentences'][0];b=shot['voice'][0]['localEnd'];start=a+(b-a)*.08;length=(b-a)*.88/2
 for i in [0,1]:
  prepare=shot['from']+math.ceil(start+length*i-1e-9);mid=shot['from']+math.ceil(start+length*(i+.45)-1e-9);arrival=shot['from']+math.ceil(start+length*(i+.72)-1e-9);end=shot['from']+math.ceil(start+length*(i+1)-1e-9);held=arrival+min(10,max(1,end-arrival-1))
  event={'shot':identity,'write':i+1+(2 if identity=='09' else 0),'prepare':prepare,'mid':mid,'beforeArrival':arrival-1,'arrival':arrival,'hold':held,'end':end};events.append(event);frames.update(event[k] for k in ['prepare','mid','beforeArrival','arrival','hold'])
frames.update([by['08']['from']+by['08']['durationInFrames']-1,by['09']['from'],by['09']['from']+by['09']['durationInFrames']-1])
frames=sorted(frames)
clips=[{'name':'height1-complete-reset-and-preselected2','range':[h['from']+c//2,h['from']+hold]},{'name':'conditional-upper-forward-writes','range':[by['09']['from'],events[-1]['hold']]}]
for clip in clips:clip['reviewFrames']=[f for f in frames if clip['range'][0]<=f<=clip['range'][1]]
onsets=json.loads((D/'words.json').read_text())['onsetTable'];actual=next(r['onsetFrame'] for r in onsets if r['sentence']=='07-height-1');formal=h['from']+cue
assert s['meta']['onsetRule']['window']==[-6,2] and -6<=formal-actual<=2
plan={'status':'planned-not-rendered','createdAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Bounded height-choice phases/four-writes and3 unchanged02→04 full-PNG witnesses. No old333-query rerun.','bodyFrames':4557,'storyboardSHA256':sha(D/'storyboard.json'),'mainSourceSHA256':sha(D/'remotion/src/Main.tsx'),'heightOptionsSHA256':sha(D/'height-options.json'),'voiceSHA256':sha(D/'voice.wav'),'wordsSHA256':sha(D/'words.json'),'frames':frames,'smokeFrames':[],'clips':clips,'fourWriteWindows':events,'heightPhases':{'shotFrom':h['from'],'formalCueLocal':cue,'formalCueGlobal':formal,'actualFirstSentenceAcousticOnsetGlobal':actual,'formalMinusAcousticFrames':formal-actual,'height1CompleteLocal':[0,c-1],'resetBeforeLocal':[c,first_allocated-1],'resetHoldFrames':first_allocated-c,'allocatedLogicalLocal':first_allocated,'firstActuallyVisible55Local':first_visible,'fadeFloatWindowLocal':[reset,fade_end],'fullyVisibleLocal':first_full,'allocatedHoldWitnessLocal':hold},'unchangedFullPNGFrames':[881,955,1382],'limits':['Plan alone is no rendered/visual proof.','Fresh20 audio audit contains3 new sentences and17 reused sources, not20-all-exact.']}
(D/'qa-height-preflight-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plannedPNGDOM':len(frames),'bodyFrames':4557,'clips':[(x['name'],x['range'],len(x['reviewFrames'])) for x in clips],'actualWriteArrivalFrames':[e['arrival'] for e in events],'heightPhases':plan['heightPhases']}))
