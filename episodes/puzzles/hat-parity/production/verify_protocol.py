#!/usr/bin/env python3
"""Verify the fixed odd/black, even/white hat protocol and export its teaching data."""
from pathlib import Path
from itertools import product
import argparse,datetime,hashlib,json
D=Path(__file__).resolve().parent

def run(hats,wrong_first_as_hat=False,wrong_ignore_prior=False):
    hats=tuple(hats)
    assert hats and all(x in (0,1) for x in hats)
    n=len(hats);signal=sum(hats[1:])%2;remaining=signal
    if wrong_first_as_hat:remaining^=signal
    spoken=[signal];states=[]
    for index in range(1,n):
        seen=sum(hats[index+1:]);before=signal if wrong_ignore_prior else remaining
        answer=before^(seen%2)
        states.append({'speaker':index+1,'visibleIds':list(range(index+2,n+1)),
                       'visibleBlackCount':seen,'visibleParity':seen%2,
                       'remainingParityBefore':before,'answer':answer,
                       'remainingParityAfter':before^answer,
                       'knownPriorIds':list(range(2,index+1)),
                       'knownPriorColors':list(hats[1:index])})
        spoken.append(answer);remaining=before^answer
    return {'signal':signal,'spoken':spoken,'states':states,
            'allLaterCorrect':spoken[1:]==list(hats[1:]),
            'firstCorrect':signal==hats[0],
            'correctCount':sum(x==y for x,y in zip(spoken,hats))}

def verify():
    cases=rounds=pairs=0
    for n in range(1,17):
        for hats in product((0,1),repeat=n):
            value=run(hats);assert value['allLaterCorrect'] and value['correctCount']>=n-1
            assert all(1 not in s['knownPriorIds'] for s in value['states'])
            cases+=1;rounds+=n-1
        for tail in product((0,1),repeat=n-1):
            a=run((0,*tail));b=run((1,*tail))
            assert a['signal']==b['signal'] and a['spoken']==b['spoken']
            assert a['firstCorrect']!=b['firstCorrect'];pairs+=1
    fixtures=[(0,)*100,(1,)*100,tuple(i%2 for i in range(100)),tuple((i+1)%2 for i in range(100))]
    fixtures += [tuple(int(i==j) for i in range(100))for j in range(100)]
    fixtures += [tuple(int(i!=j) for i in range(100))for j in range(100)]
    assert len(fixtures)==204
    for hats in fixtures:
        v=run(hats);assert v['allLaterCorrect'] and v['correctCount']>=99
        for s in v['states']:
            i=s['speaker']-1
            assert s['remainingParityBefore']==sum(hats[i:])%2
            assert s['remainingParityAfter']==sum(hats[i+1:])%2
    hats=(0,1,0,1,1);example=run(hats)
    assert example['spoken']==[1,1,0,1,1] and example['correctCount']==4
    assert not run(hats,wrong_first_as_hat=True)['allLaterCorrect']
    assert not run(hats,wrong_ignore_prior=True)['allLaterCorrect']
    report={'executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'execution':'Actual Python execution in the restored cloud workspace; independent V8 checks recorded separately.',
            'scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'smallNRange':[1,16],'completeAssignments':cases,'laterAnswerRounds':rounds,
            'firstHatFlipPairs':pairs,'deterministic100PersonFixtures':len(fixtures),
            'negativeControls':{'countingFirstSignalAsHat':'detected','ignoringPreviouslyDeducedColors':'detected'},
            'passed':True,'scope':'Finite checks supplement, not replace, the all-100-person invariant proof. No random-assignment or50% claim.'}
    model={'schemaVersion':1,'colors':{'white':0,'black':1},
           'signalWords':{'0':'白','1':'黑'},'signalMeaning':{'0':'前方黑帽数为偶数','1':'前方黑帽数为奇数'},
           'direction':'1号队尾先答，面对右侧；编号增大向队首；只看编号更大的帽子',
           'noPublicJudgmentFeedback':True,'firstSignalIsOwnHatColor':False,
           'smallExample':{'label':'五人教学示例','hats':list(hats),**example},
           'twinWorld':{'hats':[1,1,0,1,1],**run((1,1,0,1,1))},
           'fullProblem':{'people':100,'guaranteedCorrect':99,'guaranteedIds':[2,100],
                          'firstMayAlsoBeCorrect':True,'randomDistributionAssumed':False},
           'invariant':'Before speaker i>=2: R_i=b_i xor ... xor b_n. Answer=R_i xor parity(visible suffix)=b_i; then R_(i+1)=R_i xor answer. First word initializes R_2 only; it is never added as a known first hat.'}
    return report,model

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    report,model=verify()
    if args.write:
        (D/'model-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        (D/'model-data.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
