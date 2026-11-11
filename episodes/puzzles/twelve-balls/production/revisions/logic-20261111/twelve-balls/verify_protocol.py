#!/usr/bin/env python3
"""Independent exact-rational verification of the adaptive twelve-ball protocol."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import argparse, hashlib, itertools, json
D=Path(__file__).resolve().parent
OUTCOMES=('L','B','R')
CASES=[f'{i}{s}' for i in range(1,13) for s in ('H','L')]
def case(c): return int(c[:-1]), 1 if c[-1]=='H' else -1

def weigh(c,left,right,base=F(10),delta=F(1)):
    ball,sign=case(c)
    assert base>delta>0
    def total(pan): return sum((base+(sign*delta if i==ball else 0) for i in pan),F(0))
    diff=total(left)-total(right)
    return 'L' if diff>0 else 'R' if diff<0 else 'B'

def node(left,right,refs=()): return {'left':left,'right':right,'normalReferences':list(refs)}
NODES={
 '':node([1,2,3,4],[5,6,7,8]),
 'B':node([9,10,11],[1,2,3],[1,2,3]),
 'L':node([1,2,5],[3,6,9],[9]),
 'R':node([1,2,5],[3,6,9],[9]),
 'BB':node([12],[1],[1]),'BL':node([9],[10]),'BR':node([9],[10]),
 'LL':node([1],[2]),'LR':node([3],[9],[9]),'LB':node([7],[8]),
 'RL':node([3],[9],[9]),'RR':node([1],[2]),'RB':node([7],[8]),
}
TERMINALS={
 'BB':{'L':'12H','R':'12L','B':None},
 'BL':{'L':'9H','R':'10H','B':'11H'},
 'BR':{'L':'10L','R':'9L','B':'11L'},
 'LL':{'L':'1H','R':'2H','B':'6L'},
 'LR':{'L':'3H','B':'5L','R':None},
 'LB':{'L':'8L','R':'7L','B':'4H'},
 'RL':{'R':'3L','B':'5H','L':None},
 'RR':{'L':'2L','R':'1L','B':'6H'},
 'RB':{'L':'7H','R':'8H','B':'4L'},
}

def build_tree():
    candidates={'':list(CASES)};rows=[]
    for prefix in sorted(NODES,key=lambda p:(len(p),p)):
        n=NODES[prefix];left,right=n['left'],n['right'];pool=candidates[prefix]
        assert len(left)==len(right)>0 and not set(left)&set(right)
        assert len(set(left+right))==len(left+right) and set(left+right)<=set(range(1,13))
        normal=sorted(set(range(1,13))-{case(c)[0] for c in pool})
        assert set(n['normalReferences'])<=set(normal),'Normal reference smuggled before deduction'
        groups={o:[c for c in pool if weigh(c,left,right)==o] for o in OUTCOMES}
        assert sum(map(len,groups.values()))==len(pool)
        if len(prefix)<2:
            for o,group in groups.items():
                assert group;candidates[prefix+o]=group
        else:
            for o,group in groups.items():
                answer=TERMINALS[prefix][o]
                assert group==([answer] if answer else [])
        rows.append({'id':'w'+str(len(prefix)+1)+'-'+(prefix or 'root'),'prefix':prefix,'number':len(prefix)+1,
                     **n,'candidates':pool,'knownNormal':normal,'partitions':groups,
                     'answers':TERMINALS.get(prefix)})
    assert len(rows)==13
    return rows

def trace(c,tree,base=F(10),delta=F(1)):
    prefix='';steps=[]
    lookup={n['prefix']:n for n in tree}
    for k in range(3):
        n=lookup[prefix];o=weigh(c,n['left'],n['right'],base,delta)
        after=n['partitions'][o]
        steps.append({'number':k+1,'node':n['id'],'prefixBefore':prefix,'left':n['left'],'right':n['right'],
                      'normalReferences':n['normalReferences'],'knownNormalBefore':n['knownNormal'],
                      'candidatesBefore':n['candidates'],'outcome':o,'candidatesAfter':after})
        prefix+=o
    answer=TERMINALS[prefix[:2]][prefix[-1]]
    assert answer==c and len(steps)==3 and steps[-1]['candidatesAfter']==[c]
    return {'case':c,'ball':case(c)[0],'kind':'heavy' if case(c)[1]>0 else 'light','path':prefix,'answer':answer,'steps':steps}

def verify():
    tree=build_tree();traces=[trace(c,tree)for c in CASES]
    assert len({r['path']for r in traces})==24
    impossible=sorted(''.join(p)for p in itertools.product(OUTCOMES,repeat=3)if ''.join(p)not in{r['path']for r in traces})
    assert impossible==['BBB','LRR','RLL']
    fixtures=[(F(1),F(1,10)),(F(1),F(1,2)),(F(10),F(1)),(F(10),F(9)),(F(123,7),F(1,13)),(F(1000),F(1,10000))]
    for base,delta in fixtures:
        for original in traces:assert trace(original['case'],tree,base,delta)['path']==original['path']
    rootL=next(n for n in tree if n['prefix']=='L')
    bad_second={o:[c for c in rootL['candidates']if weigh(c,[1,2,3],[9,10,11])==o]for o in OUTCOMES}
    bad_first_balanced=[c for c in CASES if weigh(c,[1,2,3],[4,5,6])=='B']
    assert len(bad_first_balanced)==12>9 and len(bad_second['B'])==5>3
    assert 9 not in tree[0]['knownNormal']
    wrong_direction=[c for c in ['7L','8L']if weigh(c,[7],[8])==('L' if c=='7L' else 'R')]
    assert not wrong_direction
    hero=next(r for r in traces if r['case']=='6L');assert hero['path']=='LLB'
    model={'schemaVersion':1,'slug':'twelve-balls','rules':{'balls':12,'exactlyOneAbnormal':True,'unknownLightOrHeavy':True,'externalNormalBalls':0,'maximumWeighings':3,'adaptive':True,'mustDetermineBallAndDirection':True},
           'outcomes':{'L':'左重','B':'平衡','R':'右重'},'cases':CASES,'nodes':tree,'traces':traces,
           'mainExample':hero,'impossibleHistories':impossible,
           'construction':{'firstPartitionCounts':{o:8 for o in OUTCOMES},'remainingTwoWeighingsCapacity':9,'remainingOneWeighingCapacity':3,
             'unbalancedLeftCandidates':['1H','2H','3H','4H','5L','6L','7L','8L'],
             'secondOffCandidates':['4H','7L','8L'],'secondLeftBeforeNormal':[1,2,5],'secondRightBeforeNormal':[3,6],
             'normalPaddingBall':9,'secondLeft':[1,2,5],'secondRight':[3,6,9],'secondPartitionCounts':{o:len(rootL['partitions'][o])for o in OUTCOMES}},
           'proof':{'equalPanSizeInvariant':'Equal numbers cancel the unknown normal mass. With one abnormal ball the difference is sign(delta) times its left/right membership, or zero when off both pans.',
             'capacityBoundary':'Two adaptive three-outcome weighings have at most9 leaves <24. Three have at most27 leaves; 24<=27 alone does not prove a legal construction exists.',
             'normalBallOrigin':'A balanced first4v4 proves1..8 normal; an unbalanced first4v4 proves9..12 normal. No reference is available before the first result.'}}
    report={'executedAtUTC':datetime.now(timezone.utc).isoformat(),'engine':'Python3 fractions.Fraction exact-rational mass sums','scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'passed':True,'completeCases':24,'uniqueHistories':24,'internalWeighingNodes':13,'maximumDepth':3,
            'allPansEqualCount':True,'allBallIdsFromOriginal12':True,'allNormalReferencesDerivedFromHistory':True,
            'impossibleHistories':impossible,'parameterFixtures':[{'normalMass':str(b),'deltaMagnitude':str(d)}for b,d in fixtures],
            'fixtureCaseRuns':len(fixtures)*24,
            'negativeControls':{'threeVsThreeFirstBalanceLeaves12':len(bad_first_balanced),'sameTypeSecondBalanceLeaves5':len(bad_second['B']),'normal9UnavailableInitially':True,'lighterSideDirectionMisreadDetected':True},
            'scope':'Complete24 discrete ball/direction cases and exact rational parameter fixtures; arbitrary legal positive masses additionally follow the symbolic equal-pan invariant, not from finite fixtures alone.'}
    return model,report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    model,report=verify()
    if args.write:
        for name,value in [('model-data.json',model),('model-verification.json',report)]:
            p=D/name;assert not p.exists(),'Preserve previous evidence; verify without --write'
            p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
