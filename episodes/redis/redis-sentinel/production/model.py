#!/usr/bin/env python3
"""Finite teaching states and meaningful authorization/eligibility invariants.

This model drives animation. Product execution is separately recorded in examples/.
"""
from pathlib import Path
import copy,json,math,hashlib,itertools
D=Path(__file__).resolve().parent

def threshold(known,quorum):
    assert known>0 and 1<=quorum<=known
    return max(known//2+1,quorum)

def election(known,quorum,epoch,votes):
    seen={}
    for voter,vote_epoch,candidate in votes:
        assert voter in known
        key=(voter,vote_epoch)
        assert key not in seen or seen[key]==candidate,'A voter cannot vote twice for different executors in one epoch'
        seen[key]=candidate
    counts={candidate:sum(1 for (v,e),c in seen.items() if e==epoch and c==candidate) for candidate in known}
    qualified=[candidate for candidate,count in counts.items() if count>=threshold(len(known),quorum)]
    assert len(qualified)<=1
    return qualified[0] if qualified else None

def select(replicas,master_sdown_ms=1000,down_after_ms=700):
    eligible=[r for r in replicas if r['reachable'] and not r['down'] and r['last_reply_age_ms']<=5000
              and r['priority']>0 and r['info_age_ms']<=5000
              and r['master_link_down_ms']<=10*down_after_ms+master_sdown_ms]
    return min(eligible,key=lambda r:(r['priority'],-r['offset'],r['runid'])) if eligible else None

BASE={'known':['S1','S2','S3','S4','S5'],'available':['S1','S2','S3','S4','S5'],
      'quorum':2,'majority':3,'diagnosis':0,'objective':False,'votes':[],
      'epoch':7,'authorized':False,'candidate':None,'selected':None,
      'mDown':False,'r1Role':'副本','r2Role':'副本','r1Rejected':False,
      'promotionObserved':False,'r1Follows':'M','clientTarget':'M','chapter':'failure'}

def state(**values):return copy.deepcopy(BASE)|values
def stage(sid,before,after=None,action=None,detail=None):
    return {'id':sid,'before':copy.deepcopy(before),'after':copy.deepcopy(after or before),'action':action,'detail':detail or ''}

def build():
    shots={}
    blocked=state(available=['S1','S2'],diagnosis=2,objective=True,votes=['S1','S2'],mDown=True,candidate='S1')
    shots['01']=[stage('preview-two-reports',blocked,detail='两份故障判断，仍未获得执行授权')]
    base=state()
    shots['02']=[stage('data-copy-r1',base,action='replicateR1'),stage('data-copy-r2',base,action='replicateR2'),stage('separate-roles',base)]
    down=base|{'mDown':True};suspect=down|{'diagnosis':1}
    shots['03']=[stage('probe-no-reply',base,down,'ping'),stage('timeout-elapses',down,action='timeout'),stage('s1-subjective-down',down,suspect)]
    queried=suspect;reported=suspect|{'diagnosis':2};objective=reported|{'objective':True}
    shots['04']=[stage('ask-s2',queried,action='query'),stage('s2-report-arrives',queried,reported,'report'),stage('quorum-two-met',reported,objective)]
    candidate=objective|{'candidate':'S1','chapter':'authorization'}
    shots['05']=[stage('select-executor-object',objective,candidate),stage('epoch-seven',candidate,detail='第7轮：每个哨兵只投一个执行者')]
    two=candidate|{'available':['S1','S2']};onevote=two|{'votes':['S1']};twovote=onevote|{'votes':['S1','S2']}
    shots['06']=[stage('only-two-reachable',candidate,two),stage('s1-self-vote',two,onevote,'selfVote'),stage('s2-votes-s1',onevote,twovote,'voteS2'),stage('known-five-majority-three',twovote)]
    shots['07']=[stage('authorization-blocks',twovote,detail='确认故障 ≠ 获得执行授权'),stage('replica-stays-replica',twovote)]
    reset=candidate|{'available':['S1','S2','S3'],'votes':[]}
    vote1=reset|{'votes':['S1']};vote2=reset|{'votes':['S1','S2']};vote3=reset|{'votes':['S1','S2','S3'],'authorized':True}
    shots['08']=[stage('independent-comparison-reset',reset,detail='独立对照：回到投票前'),stage('majority-self-vote',reset,vote1,'selfVote'),stage('majority-s2-vote',vote1,vote2,'voteS2'),stage('majority-s3-vote',vote2,vote3,'voteS3'),stage('executor-authorized',vote3)]
    eligibility=vote3|{'chapter':'promotion'};reject=eligibility|{'r1Rejected':True};selected=reject|{'selected':'R2'}
    shots['09']=[stage('check-replica-eligibility',eligibility,action='inspectR1'),stage('priority-zero-excluded',eligibility,reject),stage('r2-passes-eligibility',reject,selected,'inspectR2')]
    role=selected|{'r2Role':'主节点'};observed=role|{'promotionObserved':True}
    shots['10']=[stage('promotion-command-travel',selected,action='promoteCommand'),stage('replica-changes-role',selected,role),stage('role-report-travel',role,observed,'roleReport'),stage('promotion-observed',observed)]
    repoint=observed|{'r1Follows':'R2'};client=repoint|{'clientTarget':'R2'}
    shots['11']=[stage('reconfigure-r1',observed,repoint,'repoint'),stage('propagate-address',repoint,action='config'),stage('client-asks-sentinel',repoint,action='clientQuery'),stage('address-reply',repoint,action='clientReply'),stage('client-connects-r2',repoint,client,'clientConnect')]
    caveat=client|{'chapter':'boundary'}
    shots['12']=[stage('async-write-window',caveat,detail='独立边界示例：w42尚未复制'),stage('old-master-offline-bytes-retained',caveat),stage('new-master-missing-write',caveat)]
    shots['13']=[stage('recap-diagnosis',client,detail='先确认故障'),stage('recap-authorize-executor',client,detail='再授权一个哨兵执行'),stage('recap-select-and-promote',client,detail='最后筛选并提升副本')]
    return shots

def verify(shots):
    checks=[]
    def check(name,condition):
        assert condition,name;checks.append(name)
    check('five-known quorum2 requires3',threshold(5,2)==3)
    for n in range(1,10):
        known=[f'S{x}' for x in range(n)]
        for quorum in range(1,n+1):
            for reachable in range(n//2+1):
                votes=[(k,7,known[0]) for k in known[:reachable]]
                check(f'minority cannot authorize n{n} q{quorum} r{reachable}',election(known,quorum,7,votes) is None)
    known=['S1','S2','S3','S4','S5']
    check('two diagnosis reports not leader authorization',election(known,2,7,[('S1',7,'S1'),('S2',7,'S1')]) is None)
    check('third same-epoch vote authorizes executor',election(known,2,7,[(k,7,'S1') for k in known[:3]])=='S1')
    check('stale epoch votes do not combine',election(known,2,8,[('S1',7,'S1'),('S2',7,'S1'),('S3',8,'S1')]) is None)
    check('higher quorum still binds',election(known,5,7,[(k,7,'S1') for k in known[:3]]) is None)
    check('split votes not same as reachable majority',election(known,2,7,[('S1',7,'S1'),('S2',7,'S2'),('S3',7,'S1')]) is None)
    check('repeated same vote is not counted twice',election(known,2,7,[('S1',7,'S1')]*3) is None)
    rejected=False
    try:election(known,2,7,[('S1',7,'S1'),('S1',7,'S2')])
    except AssertionError:rejected=True
    check('reject contradictory same-epoch vote',rejected)
    replica={'id':'R1','reachable':True,'down':False,'priority':100,'offset':800,'runid':'a','info_age_ms':0,'last_reply_age_ms':0,'master_link_down_ms':1000}
    r1=replica|{'priority':0,'offset':900};r2=replica|{'id':'R2','runid':'b'}
    check('priority0 excluded before offset',select([r1,r2])['id']=='R2')
    check('smaller positive priority before offset',select([replica|{'priority':50,'offset':700},r2])['id']=='R1')
    check('higher offset breaks equal priority',select([replica,r2|{'offset':900}])['id']=='R2')
    check('runid breaks same priority and offset',select([replica,r2])['id']=='R1')
    for field,value in [('reachable',False),('down',True),('info_age_ms',5001),('last_reply_age_ms',5001),('master_link_down_ms',8001)]:
        check('eligibility rejects '+field,select([replica|{field:value}]) is None)
    for shot,stages in shots.items():
        for st in stages:
            for phase in ('before','after'):
                s=st[phase]
                check(st['id']+' '+phase+' known5 majority3',len(s['known'])==5 and s['majority']==3)
                if s['authorized']:check(st['id']+' '+phase+' elected enough votes',len(s['votes'])>=3)
                if s['r2Role']=='主节点':check(st['id']+' '+phase+' promotion follows authorization',s['authorized'])
                if s['promotionObserved']:check(st['id']+' '+phase+' observed after role changed',s['r2Role']=='主节点')
                if s['r1Follows']=='R2':check(st['id']+' '+phase+' reconfigure after observed role',s['promotionObserved'])
    check('two-vote final does not promote',shots['07'][-1]['after']['r2Role']=='副本')
    check('independent comparison resets votes before recasting',shots['08'][0]['before']['votes']==[])
    return checks

if __name__=='__main__':
    shots=build();checks=verify(shots)
    model={'schemaVersion':1,'scope':'Finite teaching model; not Redis process simulation or protocol proof','sourceCommit':'60ba86f3c8b4e1ec96451171753a0a38e5c45a0c','shots':shots}
    (D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    report={'passed':True,'assertions':len(checks),'checks':checks,'states':sum(len(s) for s in shots.values()),'modelSHA256':hashlib.sha256((D/'model.json').read_bytes()).hexdigest(),'realProductEvidence':'examples/runtime-latest.json'}
    (D/'qa-model.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
