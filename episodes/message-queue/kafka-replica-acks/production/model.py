#!/usr/bin/env python3
"""Finite instruction-order teaching trace, not Kafka/Broker execution or benchmark."""
from pathlib import Path
from copy import deepcopy
import json,hashlib
D=Path(__file__).resolve().parent
EVENT={'eventId':'E01','orderId':'7042','partition':'P0','offset':0,'value':'{"eventId":"E01","orderId":7042}'}
IDS=['B1','B2','B3']; timeline=[]
def refresh(v):
 leader=v['leaderId'];isr=v['isr'];known=v['leaderKnownNext'];live={k for k,r in v['replicas'].items()if r['available']}
 for k,r in v['replicas'].items():
  r['nextOffset']=len(r['records']);r['role']='offline' if not r['available'] else 'leader'if k==leader else'follower';r['inISR']=k in isr
 v['controller']['cleanEligible']=[k for k in IDS if k in isr and k in live]
 v['admission']['currentISRSize']=len(isr)
 if leader is None:v['hwCalculation']={'participants':[],'positions':{},'candidate':None,'underMinISR':len(isr)<2}
 else:
  known[leader]=v['replicas'][leader]['nextOffset'];inputs={k:known[k] for k in isr};candidate=min(inputs.values())
  v['hwCalculation']={'participants':list(isr),'positions':inputs,'candidate':candidate,'underMinISR':len(isr)<2,'scope':'Stable ISR; no pending expansion or additional caught-up eligible replica.'}
 v['totalPhysicalCopies']=sum(bool(r['records'])for r in v['replicas'].values());v['livePhysicalCopies']=sum(bool(r['records'])and r['available']for r in v['replicas'].values());v['activeLeaderHasEvent']=bool(leader and v['replicas'][leader]['records'])
 v['completionConditionNow']=bool(leader and v['requiredOffset'] is not None and v['highWatermark']>=v['requiredOffset'] and len(isr)>=2)
 return v
def begin(branch,acks,isr):
 return refresh({'id':'','label':'','branch':branch,'resetBefore':True,'leaderId':'B1','isr':list(isr),'maximalISR':list(isr),'extraCatchupCandidates':[],'minISR':2,'requiredOffset':None,'highWatermark':0,'leaderKnownNext':{k:0 for k in IDS},'replicas':{k:{'available':k in isr,'records':[],'localHW':0}for k in IDS},'producer':{'acks':acks,'sendCallCount':0,'future':'not-sent','response':'none','error':None,'successMetadata':None,'ackEvidence':None},'admission':{'applies':acks=='all','evaluated':False,'passed':None,'currentISRSize':len(isr),'minimum':2},'delayedProduce':{'created':False,'acksPending':False},'controller':{'mode':'stable','cleanEligible':[],'selected':None,'eligibleLeaderReplicasFeature':0,'uncleanLeaderElection':False},'consumer':{'businessCompleted':False},'fsyncProvenByThisAck':False,'event':{'kind':'initial','record':None}})
def push(v,id,label,kind=None,**event):
 v=deepcopy(v);v['id']=id;v['label']=label
 if timeline and timeline[-1]['branch']==v['branch']:v['resetBefore']=False
 if 'from_' in event:event['from']=event.pop('from_')
 if kind:v['event']={'kind':kind,**event}
 v=refresh(v);timeline.append(v);return deepcopy(v)
def send(v):
 v['producer'].update(sendCallCount=1,future='pending');return v
def admit(v):
 v['admission'].update(evaluated=True,passed=len(v['isr'])>=2);return v
def append_leader(v):
 v['replicas'][v['leaderId']]['records'].append(deepcopy(EVENT));v['requiredOffset']=1
 if v['producer']['acks']=='all':v['delayedProduce'].update(created=True,acksPending=True)
 return refresh(v)
def request(v,follower,offset):return {'from':follower,'to':v['leaderId'],'requestOffset':offset,'kind':'fetch-request','record':None}
def copy(v,follower):return {'from':v['leaderId'],'to':follower,'kind':'fetch-response-copy','record':deepcopy(EVENT),'originalRetained':True}
def append_follower(v,follower):v['replicas'][follower]['records'].append(deepcopy(EVENT));return refresh(v)
def report(v,follower):
 v['leaderKnownNext'][follower]=v['replicas'][follower]['nextOffset'];v=refresh(v)
 if not v['hwCalculation']['underMinISR']:
  v['highWatermark']=max(v['highWatermark'],v['hwCalculation']['candidate']);v['replicas'][v['leaderId']]['localHW']=v['highWatermark']
 return refresh(v)
def respond(v,success=True):
 v['producer']['response']='in-flight';v['delayedProduce']['acksPending']=False
 return v
def delivered(v):
 p=v['producer'];p['response']='delivered';p['future']='success';p['successMetadata']={'partition':'P0','offset':0};p['ackEvidence']={'leaderId':v['leaderId'],'leaderHadRecord':v['activeLeaderHasEvent'],'highWatermark':v['highWatermark'],'isr':list(v['isr']),'physicalCopies':v['totalPhysicalCopies']};return v
def fail_leader(v):
 old=v['leaderId'];v['replicas'][old]['available']=False;v['leaderId']=None;v['highWatermark']=None;v['leaderKnownNext']={k:None for k in IDS};v['controller'].update(mode='selecting-clean',selected=None);return refresh(v)
def takeover(v,selected):
 v['leaderId']=selected;v['isr']=[k for k in v['isr']if v['replicas'][k]['available']];v['maximalISR']=list(v['isr']);v['leaderKnownNext']={k:(v['replicas'][k]['nextOffset'] if k in v['isr']else None)for k in IDS};v['highWatermark']=v['replicas'][selected]['localHW'];v['controller'].update(mode='stable-after-clean',selected=selected);return refresh(v)
# acks=1: selected legal scheduling window before either follower has copied this record.
v=begin('leader-only','1',IDS);v=push(v,'acks1-initial','三份空日志，稳定ISR3')
v=push(send(v),'acks1-sent','单条发送等待回复','producer-send',record=EVENT)
v=push(append_leader(v),'acks1-appended','主日志E01@0，另外两份仍空','leader-append',to='B1',record=EVENT)
v=push(respond(v),'acks1-response','主追加后即可发成功响应','produce-response',from_='B1',to='website')
v=push(delivered(v),'acks1-success','网站收到成功；本例只有主日志有E01','response-delivered',to='website')
v=push(fail_leader(v),'acks1-leader-down','只停原主，离线字节保留','single-broker-failure',broker='B1')
v=push(takeover(v,'B2'),'acks1-takeover-missing','clean接管后的新主日志没有E01','clean-election',selected='B2',scope='Stable result after control-plane recovery, not controller-vote simulation.')
# acks=all with fixed stable ISR3. Fetch and report are separate states.
v=begin('all-three','all',IDS);v=push(v,'all3-initial','同E01/配置，从三份空日志重置')
v=push(send(v),'all3-sent','等待同步副本的单条发送','producer-send',record=EVENT)
v=push(admit(v),'all3-admitted','3>=2，追加前准入通过','admission-check')
v=push(append_leader(v),'all3-appended','主追加E01@0；requiredOffset1/HW0','leader-append',to='B1',record=EVENT)
v=push(v,'all3-b2-fetch0','B2从自己末尾0拉取',**request(v,'B2',0))
v=push(v,'all3-b2-copy','响应携带记录副本，原主日志不动',**copy(v,'B2'))
v=push(append_follower(v,'B2'),'all3-b2-appended','B2实际末尾1，Leader暂知0','follower-append',to='B2',record=EVENT)
v=push(report(v,'B2'),'all3-b2-reported','下一次Fetch1使Leader获知B2已追齐','fetch-progress-report',from_='B2',to='B1',requestOffset=1)
v=push(v,'all3-wait-third','已知[1,1,0]；HW0，min2不等于只等2份','check-common-progress')
v=push(v,'all3-b3-fetch0','第三份仍从末尾0拉取',**request(v,'B3',0))
v=push(v,'all3-b3-copy','第三份响应副本在途中',**copy(v,'B3'))
v=push(append_follower(v,'B3'),'all3-b3-appended','第三份已写1，Leader尚未知','follower-append',to='B3',record=EVENT)
v=push(report(v,'B3'),'all3-hw-ready','下次Fetch1报告后HW推进1，涵盖E01@0','fetch-progress-report-and-hw',from_='B3',to='B1',requestOffset=1)
v=push(respond(v),'all3-response','完成检查已满足，成功响应在途','produce-response',from_='B1',to='website')
v=push(delivered(v),'all3-success','成功回复已到达网站','response-delivered',to='website')
# Before the fault comparison, normal follow-up Fetch responses propagate HW; not an extra ack prerequisite.
for k in ['B2','B3']:v['replicas'][k]['localHW']=1
v=push(v,'all3-settled','成功后的后续拉取已使副本进度收敛','follow-up-hw-propagation',scope='Selected settled fault injection point; not an additional condition for producer success.')
v=push(fail_leader(v),'all3-leader-down','只停原主，另外两份保留记录','single-broker-failure',broker='B1')
v=push(takeover(v,'B2'),'all3-takeover-retained','clean接管后新主保留E01','clean-election',selected='B2',scope='Stable result, not controller vote simulation.')
# Stable ISR2, missing replica not an extra recently caught-up eligible candidate.
v=begin('all-two','all',['B1','B2']);v=push(v,'all2-initial','再次同数据空日志重置，稳定ISR2')
v=push(send(v),'all2-sent','两份名单上的单条all发送','producer-send',record=EVENT)
v=push(admit(v),'all2-admitted','2>=2，准入通过','admission-check')
v=push(append_leader(v),'all2-appended','主追加但共同进度仍0','leader-append',to='B1',record=EVENT)
v=push(v,'all2-b2-fetch0','当前第二份Fetch0',**request(v,'B2',0))
v=push(v,'all2-b2-copy','响应记录副本',**copy(v,'B2'))
v=push(append_follower(v,'B2'),'all2-b2-appended','第二份已写，但Leader尚未知','follower-append',to='B2',record=EVENT)
v=push(report(v,'B2'),'all2-hw-ready','当前两份已知1，HW1','fetch-progress-report-and-hw',from_='B2',to='B1',requestOffset=1)
v=push(respond(v),'all2-response','当前集合完成，成功响应在途','produce-response',from_='B1',to='website')
v=push(delivered(v),'all2-success','当前稳定ISR2的all成功','response-delivered',to='website')
# Pre-append rejection is this case only. Runtime verification is tracked separately.
v=begin('all-one-rejected','all',['B1']);v=push(v,'all1-initial','同数据空日志重置，稳定ISR1')
v=push(send(v),'all1-sent','单条all请求到达，尚未追加','producer-send',record=EVENT)
v=admit(v);v['producer'].update(response='in-flight',error='NOT_ENOUGH_REPLICAS');v=push(v,'all1-response','1<2，在append调用前拒绝','pre-append-rejection')
v['producer'].update(future='failed',response='delivered');v=push(v,'all1-rejected','本次失败回复到网站，日志仍空','failure-delivered')
# Independent finite invariants, counts are evidence scope not a correctness/teaching-depth score.
checks=[]
def ck(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
by={v['id']:v for v in timeline}
for v in timeline:
 prefix=v['id'];p=v['producer'];leader=v['leaderId']
 ck(prefix+': single append per replica',all(len(r['records'])<=1 for r in v['replicas'].values()))
 ck(prefix+': same bytes/event/offset retained',all(x==EVENT for r in v['replicas'].values()for x in r['records']))
 ck(prefix+': next offset follows physical append',all(r['nextOffset']==len(r['records'])for r in v['replicas'].values()))
 ck(prefix+': exactly stable declared wait set',v['isr']==v['maximalISR'] and not v['extraCatchupCandidates'])
 ck(prefix+': single send without dedup/retry effects',p['sendCallCount']<=1)
 ck(prefix+': no business completion from ack',not v['consumer']['businessCompleted'])
 ck(prefix+': no fsync guarantee inferred',not v['fsyncProvenByThisAck'])
 ck(prefix+': ELR and unclean disabled',v['controller']['eligibleLeaderReplicasFeature']==0 and not v['controller']['uncleanLeaderElection'])
 ck(prefix+': clean candidate must be live ISR member',all(k in v['isr']and v['replicas'][k]['available']for k in v['controller']['cleanEligible']))
 if leader:
  ck(prefix+': active leader is available',v['replicas'][leader]['available'])
  ck(prefix+': known progress cannot outrun physical append',all(n is None or n<=v['replicas'][k]['nextOffset']for k,n in v['leaderKnownNext'].items()))
  ck(prefix+': HW does not outrun declared known stable set',v['highWatermark']<=v['hwCalculation']['candidate'])
 else:ck(prefix+': inactive leader does not have active progress',v['highWatermark']is None and all(x is None for x in v['leaderKnownNext'].values()))
 if v['resetBefore']:ck(prefix+': branch explicitly starts empty',v['totalPhysicalCopies']==0 and p['sendCallCount']==0)
 if p['future']=='success':
  ck(prefix+': success only delivered response',p['response']=='delivered'and bool(p['successMetadata']))
  ev=p['ackEvidence'];ck(prefix+': leader had record at confirmation',ev['leaderHadRecord'])
  if p['acks']=='all':ck(prefix+': all success evidence has reached target and minISR',ev['highWatermark']>=1 and len(ev['isr'])>=2)
 if p['acks']=='1':ck(prefix+': ack1 does not install replica-wait operation',not v['delayedProduce']['created'])
 if p['future']=='failed':ck(prefix+': selected preappend rejection leaves logs untouched',p['error']=='NOT_ENOUGH_REPLICAS'and v['totalPhysicalCopies']==0 and not v['admission']['passed'])
ck('B2 append precedes leader knowledge',by['all3-b2-appended']['replicas']['B2']['nextOffset']==1 and by['all3-b2-appended']['leaderKnownNext']['B2']==0)
ck('B3 append precedes leader knowledge',by['all3-b3-appended']['replicas']['B3']['nextOffset']==1 and by['all3-b3-appended']['leaderKnownNext']['B3']==0)
ck('min2 still waits while ISR3 third missing',by['all3-wait-third']['totalPhysicalCopies']==2 and by['all3-wait-third']['highWatermark']==0 and by['all3-wait-third']['producer']['future']=='pending')
ck('all3 HW1 covers record0',by['all3-hw-ready']['highWatermark']==1 and by['all3-hw-ready']['requiredOffset']==1)
ck('acks1 fault preserves offline bytes, active leader missing',by['acks1-takeover-missing']['replicas']['B1']['records']==[EVENT]and not by['acks1-takeover-missing']['activeLeaderHasEvent'])
ck('all3 fault retains live record',by['all3-takeover-retained']['activeLeaderHasEvent']and by['all3-takeover-retained']['livePhysicalCopies']==2)
ck('all2 succeeds without third physical copy',by['all2-success']['totalPhysicalCopies']==2 and by['all2-success']['producer']['future']=='success')
ck('all1 is before append and HW stays0',by['all1-rejected']['totalPhysicalCopies']==0 and by['all1-rejected']['highWatermark']==0)
out={'schemaVersion':1,'episode':'kafka-replica-acks','kind':'finite-teaching-model','sourceCommit':'1156b2752aaa28eafc0b4c4d387e63356793268d','event':EVENT,'conditions':json.loads((D/'example-config.json').read_text()),'stateScope':'Instruction-order explanatory snapshots, not timestamps or a complete broker/controller implementation. State quantities/source/scheduling assumptions must not be called measured runtime.','timeline':timeline}
encoded=json.dumps(out,ensure_ascii=False,indent=2)+'\n';(D/'model.json').write_text(encoded);report={'pass':True,'kind':'finite-teaching-invariant-checks','modelSHA256':hashlib.sha256(encoded.encode()).hexdigest(),'states':len(timeline),'checks':len(checks),'results':checks,'runtime':'Not executed by this model. External actual Kafka fixture scope and receipts remain separate.'};(D/'model-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['pass','modelSHA256','states','checks']}))
