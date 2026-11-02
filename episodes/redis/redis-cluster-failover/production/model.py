#!/usr/bin/env python3
"""Finite teaching model of normal Cluster authorization; not a Redis reimplementation.

Unique voter identity is a model abstraction grounded in the actual voter's
lastVoteEpoch rule. The real ACK receiver does not have this Python set table.
"""
from pathlib import Path
import copy,itertools,json
D=Path(__file__).resolve().parent
MASTERS=('A','B','C')
SLOTS={'A':[0,5460],'B':[5461,10922],'C':[10923,16383]}
def majority(n):return n//2+1
def fresh_reports(self_id,reports,now=100,valid_for=20):
    voters={self_id} if self_id in MASTERS else set()
    voters|={who for who,at in reports if who in MASTERS and now-at<=valid_for}
    return voters
def may_grant(voter,epoch,last_vote=5,knows_fail=True,has_slots=True,config_current=True):
    return voter in MASTERS and has_slots and knows_fail and epoch>last_vote and config_current
def accept_normal_grants(voters,epoch=6,expected=6):
    # Model stores distinct normal voters, not a claim about receiver internals.
    return sorted({v for v in voters if v in MASTERS}) if epoch>=expected else []
def base(id,stage):
    return dict(id=id,stage=stage,masters=list(MASTERS),slots=SLOTS,reachable=list(MASTERS)+['A1','B1','C1'],
                oldMaster='A',candidate='A1',candidateRole='replica',failure='none',reports=[],votes=[],
                electionEpoch=5,configEpoch=1,authorized=False,slotOwner='A',views={'B':'A','C':'A'},
                oldMasterRecords=['copied-1','pending-2'],candidateRecords=['copied-1'],reset=False)
def run():
    checks=[]
    def check(name,ok):
        assert ok,name;checks.append(name)
    check('three-original-slot-masters-need-two',majority(3)==2)
    check('one-local-PFAIL-insufficient',len(fresh_reports('B',[]))<2)
    check('expired-report-excluded',len(fresh_reports('B',[('C',79)]))==1)
    check('replica-report-not-a-master-report',len(fresh_reports('B',[('C1',99)]))==1)
    check('self-and-other-recent-master-form-majority',len(fresh_reports('B',[('C',99)]))==2)
    check('replica-no-self-vote',not may_grant('A1',6))
    check('slotless-master-no-vote',not may_grant('B',6,has_slots=False))
    check('old-master-must-be-FAIL',not may_grant('B',6,knows_fail=False))
    check('older-config-request-refused',not may_grant('B',6,config_current=False))
    check('current-epoch-only-one-grant',not may_grant('B',6,last_vote=6))
    check('old-epoch-ACK-not-counted',accept_normal_grants(['B'],5,6)==[])
    check('normal-two-voters-authorize',len(accept_normal_grants(['B','C']))>=2)
    check('one-master-and-one-replica-not-majority',len(accept_normal_grants(['B','A1']))<2)
    check('original-three-not-online-one-is-denominator',majority(3)!=majority(1))
    for n in range(1,8):
        ids=range(n);need=majority(n)
        for mask in itertools.product((0,1,2),repeat=n):
            # Each voter can give its one vote to candidate X, Y, or neither.
            check(f'majorities-cannot-both-win-n{n}-{sum(v*3**i for i,v in enumerate(mask))}',not(mask.count(1)>=need and mask.count(2)>=need))
    timeline=[]
    def state(id,stage,**kw):
        v=copy.deepcopy(timeline[-1]) if timeline else base(id,stage);v.update(id=id,stage=stage,**kw);timeline.append(v);return v
    state('normal','topology')
    state('offline','problem',reachable=['B','C','A1','B1','C1'])
    state('pfail','suspicion',failure='PFAIL',reports=['B'])
    state('fail','failure',failure='FAIL',reports=['B','C'])
    state('eligible','eligibility',eligible=True,waiting=True)
    state('request','request',electionEpoch=6,waiting=False)
    state('vote-b','first-vote',votes=['B'])
    state('vote-bc','majority',votes=['B','C'],authorized=True)
    state('promoted','takeover',candidateRole='master',configEpoch=6,slotOwner='A1')
    state('announced-b','takeover',views={'B':'A1','C':'A'})
    state('announced-bc','takeover',views={'B':'A1','C':'A1'})
    v=copy.deepcopy(base('minority-reset','minority'));v.update(reachable=['B','A1','B1','C1'],failure='FAIL',reports=['B','C'],electionEpoch=5,reset=True)
    timeline.append(v)
    state('minority-request','minority',electionEpoch=6)
    state('minority-one','minority',votes=['B'])
    check('minority-never-promoted',timeline[-1]['candidateRole']=='replica' and not timeline[-1]['authorized'])
    v=copy.deepcopy(next(x for x in timeline if x['id']=='announced-bc'));v.update(id='success-return',stage='data-boundary',reset=True);timeline.append(v)
    check('promotion-does-not-create-uncopied-record','pending-2' not in v['candidateRecords'])
    check('offline-master-bytes-not-erased','pending-2' in v['oldMasterRecords'])
    check('slots-identical-after-promotion',SLOTS['A']==[0,5460])
    state('summary','recap')
    for s in timeline:
        check(s['id']+'-replica-not-voter',all(v in MASTERS for v in s['votes']))
        check(s['id']+'-promotion-needs-majority',s['candidateRole']!='master' or len(s['votes'])>=majority(len(MASTERS)))
        check(s['id']+'-ownership-not-a-data-transfer',s['candidateRecords']==['copied-1'])
    result=dict(kind='finite teaching abstraction, not Redis runtime',version='Redis8.4.0 normal failover source-grounded',passed=True,checks=len(checks),assertions=checks,timeline=timeline,
                limits=['Normal trusted voter identity and single-vote abstract set; no claim of receiver-side dedup table','Illustrative packet order and epoch5→6, no performance measurement','Only listed stale/majority/role conditions modeled, not all cluster protocol states'])
    (D/'model.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(checks)} finite assertions; {len(timeline)} teaching states')
if __name__=='__main__':run()
