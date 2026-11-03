"""Independent semantic checks on DOM collected from actual Remotion PNG renders."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent.parent
name=sys.argv[1] if len(sys.argv)>1 else 'preflight-v3'
render=json.loads((D/'qa'/f'{name}.json').read_text())
oracle={
 2: {'players':[4,5],'quota':1,'allocation':{'4':100,'5':0},'previous':{'5':100}},
 3: {'players':[3,4,5],'quota':2,'allocation':{'3':99,'4':0,'5':1},'previous':{'4':100,'5':0}},
 4: {'players':[2,3,4,5],'quota':2,'allocation':{'2':99,'3':0,'4':1,'5':0},'previous':{'3':99,'4':0,'5':1}},
 5: {'players':[1,2,3,4,5],'quota':3,'allocation':{'1':98,'2':0,'3':1,'4':0,'5':1},'previous':{'2':99,'3':0,'4':1,'5':0}},
}
checked=[]
for sample in render['samples']:
 states=sample['metrics']['states']
 boards=[s['attrs'] for s in states if 'data-round' in s['attrs']]
 if not boards: continue
 assert len(boards)==1
 b=boards[0];n=int(b['data-round']);expected=oracle[n]
 assert int(b['data-quota'])==expected['quota']
 people={s['attrs']['data-pirate']:s['attrs'] for s in states if 'data-pirate' in s['attrs']}
 assert set(people)==set('12345')
 for person,p in people.items():
  assert p['data-active']==('true' if int(person) in expected['players'] else 'false')
 accepted=b['data-confirmed']=='true'
 if accepted:
  assert b['data-phase']=='confirmed'
  assert int(b['data-votes-yes'])>=expected['quota']
  assert sum(int(people[str(i)]['data-realized-coins']) for i in expected['players'])==100
  for person,money in expected['allocation'].items():
   assert int(people[person]['data-realized-coins'])==money
   assert int(people[person]['data-proposal-coins'])==money
 else:
  assert all(p['data-realized-coins']=='none' for p in people.values())
  if b['data-phase']=='trial':
   assert n==5 and b['data-proposal-sum']=='1'
   assert people['4']['data-proposal-coins']=='1'
  elif b['data-phase']=='proposal':
   assert b['data-proposal-sum']=='100'
   for person,money in expected['allocation'].items():
    assert int(people[person]['data-proposal-coins'])==money
 texts=[t['text'] for t in sample['metrics']['texts']]
 if '若否决本轮提案，下一轮所得' in texts:
  assert people[str(expected['players'][0])]['data-reject-coins']=='out'
  for person,money in expected['previous'].items():
   assert people[person]['data-reject-coins']==str(money)
 if int(sample['shot'])==12:
  assert people['4']['data-proposal-coins'] in ('none','0')
 checked.append({'frame':sample['frame'],'shot':sample['shot'],'people':n,'phase':b['data-phase'],'yes':int(b['data-votes-yes']),'quota':expected['quota'],'confirmed':accepted})
assert checked
assert any(s['shot']=='13' and s['yes']==2 and not s['confirmed'] for s in checked), 'Need an actual two-yes unconfirmed five-person sample'
assert any(s['shot']=='13' and s['confirmed'] for s in checked)
report={'executor':'Independent motion QA','passed':True,'renderReport':f'qa/{name}.json','scope':'Actual rendered DOM proposal/rejection/realized allocations, quorum, identities and trial withdrawal; visual legibility is reviewed separately.','samplesChecked':len(checked),'states':checked}
(D/'qa'/f'{name}-semantic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'actualRenderedSamplesChecked':len(checked)}))
