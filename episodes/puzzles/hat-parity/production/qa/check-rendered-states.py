#!/usr/bin/env python3
"""Check actual rendered P08 DOM states against an independent fixed truth table."""
from pathlib import Path
import argparse,hashlib,json,datetime
D=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--preview',default='preflight-v2');a=p.parse_args()
source=D/'qa'/f'{a.preview}.json';preview=json.loads(source.read_text())
expected={2:(1,2,0,'黑'),3:(0,2,0,'白'),4:(0,1,1,'黑'),5:(1,0,0,'黑')}
colors={1:'白',2:'黑',3:'白',4:'黑',5:'黑'}
rows=[];violations=[];coverage={'speaker':set(),'handoff':set(),'firstSignal':0,'knownLedgers':0,'hypotheses':set(),'twinWorldFrames':0,'hundredFrames':0,'compareBeforeInference':set(),'compareAfterInference':set(),'spokenAnswers':set()}
def check(condition,message,s):
 if not condition:violations.append({'frame':s['frame'],'shot':s['shot'],'message':message})
for s in preview['samples']:
 states=[q['attrs'] for q in s['metrics']['states']];texts=[q['text'] for q in s['metrics']['texts']]
 for st in states:
  if 'data-current-speaker' in st:
   i=int(st['data-current-speaker']);coverage['speaker'].add(i)
   people=[r for r in states if 'data-person' in r]
   check(len(people)==5,'POV must contain exactly the five fixed people',s)
   for person in people:
    j=int(person['data-person']);check(person.get('data-facing')=='right','Person must face right',s)
    check(person['data-physical-hat']==(colors[j] if j>i else 'hidden'),'POV must hide own/behind and show actual front hat',s)
  if 'data-first-signal' in st:
   coverage['firstSignal']+=1;check(st['data-first-signal']=='odd' and st.get('data-first-signal-counted-as-true-hat')=='false','First checksum must remain odd and outside true hat ledger',s)
  if 'data-known-prior-ids' in st:
   ids=list(filter(None,st['data-known-prior-ids'].split(',')));coverage['knownLedgers']+=1
   check('1' not in ids,'First signal cannot be counted as known real hat',s)
   check(st.get('data-known-source')=='deduced','Known true colors must be logically deduced',s)
  if 'data-compare-speaker' in st:
   i=int(st['data-compare-speaker']);target,count,visible,answer=expected[i]
   check((int(st['data-target-parity']),int(st['data-visible-count']),int(st['data-visible-parity']))==(target,count,visible),'Independent visible/target parity tuple differs',s)
   inferred=st['data-inferred']=='true';spoken=st['data-spoken-answer']
   coverage['compareAfterInference' if inferred else 'compareBeforeInference'].add(i)
   check(spoken=='pending' or inferred,'Spoken own answer cannot precede deduction',s)
   check(spoken in ('pending',answer),'Spoken answer differs from independent truth',s)
   if spoken!='pending':coverage['spokenAnswers'].add(i)
   if not inferred:
    premature={'08':['推定白帽','本人必须是白帽','自己必须是白帽'], '10':['本人必须是黑帽','自己必须是黑帽']}.get(s['shot'],[])
    check(not any(phrase in text for phrase in premature for text in texts),'Current-person conclusion appears elsewhere before deduction',s)
  if 'data-handoff-from' in st:
   i=int(st['data-handoff-from']);coverage['handoff'].add(i)
   before,after,color={2:(1,0,'黑'),3:(0,0,'白'),4:(0,1,'黑')}[i]
   check(st['data-removed-color']==color and int(st['data-before'])==before and int(st['data-after']) in (before,after),'Handoff removes wrong color/parity',s)
   check(st.get('data-source-message-remains')=='odd','Remaining parity update must preserve original first message',s)
  if 'data-self-hypothesis' in st:coverage['hypotheses'].add(st['data-self-hypothesis'])
  if st.get('data-twin-worlds')=='true':
   coverage['twinWorldFrames']+=1;check(st.get('data-front-hats-identical')=='true' and st.get('data-first-word-identical')=='true','Twin worlds must preserve front hats/first word',s)
   people=[r for r in states if 'data-person' in r];check([r['data-physical-hat'] for r in people]==['白','黑'],'Twin worlds must differ only in first own hat',s)
  if st.get('data-hundred-schematic')=='true':
   coverage['hundredFrames']+=1;check(st.get('data-middle-explicitly-omitted')=='true','Hundred-person view must explicitly omit middle',s)
 rows.append({'shot':s['shot'],'frame':s['frame'],'stateNodes':len(states)})
for key in ['compareBeforeInference','compareAfterInference','spokenAnswers']:check(coverage[key]=={2,3,4,5},f'Missing actual rendered coverage for {key}',{'shot':'all','frame':-1})
check(coverage['handoff']=={2,3,4},'Missing black/white handoffs',{'shot':'all','frame':-1})
check(coverage['hypotheses']=={'黑','白'} and coverage['twinWorldFrames']>0 and coverage['hundredFrames']>0,'Missing main proof states',{'shot':'all','frame':-1})
report={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':not violations,'sourcePreview':str(source.relative_to(D)),'sourcePreviewSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Read only actual Chromium rendered DOM captured by independent renderStill. Independent truth table, POV masks, first-message exclusion, and observed before/after deduction states checked.','coverage':{k:sorted(v) if isinstance(v,set) else v for k,v in coverage.items()},'rows':rows,'violations':violations,'limitations':['DOM states support correctness but do not replace independent image review.','No word ASR, semantic listening, site or online check.']}
(D/'qa'/f'{a.preview}-states.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':not violations,'coverage':report['coverage'],'violations':violations},ensure_ascii=False));raise SystemExit(bool(violations))
