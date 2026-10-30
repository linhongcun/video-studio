#!/usr/bin/env python3
"""Finite teaching trace constrained by source; this is not a Broker/network test."""
from pathlib import Path
from copy import deepcopy
import json,hashlib
D=Path(__file__).resolve().parent
states={}
def initial(name):
 return {'id':name,'call':{'returned':False,'error':None},'batch':{'id':'B1','eventId':'E01','orderId':'7042','partition':0,'producerId':None,'epoch':None,'firstSeq':None,'lastSeq':None},'queue':[],'inflight':[],'request':None,'future':{'id':'F1','state':'absent','partition':None,'offset':None,'error':None},'callback':'not-called','log':[],'logEnd':0,'brokerStates':{},'business':'pending','duplicate':False,'newFuture':None}
def keep(s,name):
 s['id']=name;states[name]=deepcopy(s);return s

def give_identity(s,pid=501,epoch=0,seq=0):
 s['batch'].update(producerId=pid,epoch=epoch,firstSeq=seq,lastSeq=seq)
def request(s,rid):
 s['queue']=[];s['inflight']=[s['batch']['id']];s['request']={'id':rid,'recordsByPartition':{'P0':s['batch']['id']}}
def accept(s):
 b=s['batch'];pid=str(b['producerId']);old=s['brokerStates'].get(pid)
 duplicate=next((x for x in old['batches']if x['firstSeq']==b['firstSeq']and x['lastSeq']==b['lastSeq']),None)if old and old['epoch']==b['epoch']else None
 if duplicate:
  s['duplicate']=True;return duplicate['offset']
 # This trace only admits valid first batches and contiguous valid next batches.
 assert (old is None and b['firstSeq']==0) or (old and old['epoch']==b['epoch'] and b['firstSeq']==old['batches'][-1]['lastSeq']+1)
 off=s['logEnd'];s['log'].append({'eventId':b['eventId'],'offset':off,'producerId':b['producerId'],'epoch':b['epoch'],'firstSeq':b['firstSeq'],'lastSeq':b['lastSeq']});s['logEnd']+=1
 if old is None:old={'epoch':b['epoch'],'batches':[]};s['brokerStates'][pid]=old
 old['batches'].append({'firstSeq':b['firstSeq'],'lastSeq':b['lastSeq'],'offset':off});old['batches']=old['batches'][-5:]
 s['duplicate']=False;return off
s=initial('normal-start');keep(s,'normal-start');s['queue']=['B1'];keep(s,'normal-buffer');s['call']['returned']=True;s['future']['state']='pending';keep(s,'normal-returned');give_identity(s);request(s,'R1');keep(s,'normal-inflight');off=accept(s);keep(s,'normal-appended');s['future'].update(partition=0,offset=off);keep(s,'normal-response');s['callback']='success';keep(s,'normal-callback');s['future']['state']='success';s['inflight']=[];keep(s,'normal-complete')
s=initial('unknown-start');keep(s,'unknown-start');s['queue']=['B1'];s['future']['state']='pending';s['call']['returned']=True;give_identity(s);request(s,'R2');keep(s,'unknown-inflight');accept(s);keep(s,'unknown-appended');s['inflight']=[];s['queue']=['B1'];keep(s,'unknown-requeued');request(s,'R3');keep(s,'unknown-retry-inflight');off=accept(s);assert off==0;keep(s,'unknown-duplicate');s['future'].update(state='failed',error='TimeoutException',partition=None,offset=None);s['callback']='failure';s['inflight']=[];keep(s,'unknown-expired')
# Application closes A and creates a new non-transactional producer B; old F1 remains failed.
s['newFuture']={'id':'F2','state':'pending','partition':None,'offset':None,'error':None};s['batch'].update(id='B2',producerId=902,epoch=0,firstSeq=0,lastSeq=0);request(s,'R4');s['callback']='new-pending';s['duplicate']=False;keep(s,'new-inflight');off=accept(s);assert off==1;keep(s,'new-appended');s['newFuture'].update(state='success',partition=0,offset=off);s['inflight']=[];s['callback']='new-success';keep(s,'new-complete')
s=initial('local-start');keep(s,'local-start');s['call']['error']='SerializationException';keep(s,'local-failed')
checks=[]
def check(name,value):
 assert value,name;checks.append(name)
check('buffer precedes send return',states['normal-buffer']['future']['state']=='absent' and states['normal-buffer']['queue']==['B1'])
check('returned same F1 pending',states['normal-returned']['future']['id']=='F1' and states['normal-returned']['future']['state']=='pending')
check('no batch identity assigned before first drain',states['normal-returned']['batch']['producerId']is None)
check('first drain assigns identity and sequence',states['normal-inflight']['batch']['producerId']==501 and states['normal-inflight']['batch']['firstSeq']==0)
check('queue membership changes into Sender inflight',not states['normal-inflight']['queue'] and states['normal-inflight']['inflight']==['B1'])
check('request context maps P0 to B1',states['normal-inflight']['request']['recordsByPartition']=={'P0':'B1'})
check('actual append before response leaves F1 pending',states['normal-appended']['logEnd']==1 and states['normal-appended']['future']['state']=='pending')
check('broker caches identity epoch range and offset',states['normal-appended']['brokerStates']['501']=={'epoch':0,'batches':[{'firstSeq':0,'lastSeq':0,'offset':0}]})
check('callback then release Future wait in normal chain',states['normal-callback']['callback']=='success' and states['normal-callback']['future']['state']=='pending' and states['normal-complete']['future']['state']=='success')
check('same Future object identity throughout',all(states[x]['future']['id']=='F1'for x in states))
check('business not completed by producer response',all(states[x]['business']=='pending'for x in states))
check('independent unknown reset starts empty',states['unknown-start']['log']==[] and states['unknown-start']['future']['state']=='absent')
check('retry is same batch object identity',states['unknown-appended']['batch']==states['unknown-retry-inflight']['batch'])
check('retry uses fresh request R3 but same P0-B1 mapping',states['unknown-retry-inflight']['request']=={'id':'R3','recordsByPartition':{'P0':'B1'}})
check('duplicate branch does not change log or end',states['unknown-retry-inflight']['log']==states['unknown-duplicate']['log'] and states['unknown-duplicate']['logEnd']==1 and states['unknown-duplicate']['duplicate'])
check('duplicate response still unobserved by sender in this scenario',states['unknown-duplicate']['future']['state']=='pending' and states['unknown-duplicate']['callback']=='not-called')
check('delivery failure does not undo broker record',states['unknown-expired']['logEnd']==1 and states['unknown-expired']['future']['state']=='failed')
check('new session gets different producer identity',states['new-inflight']['batch']['producerId']==902 and '902'not in states['new-inflight']['brokerStates'])
check('new valid session append is position one',states['new-appended']['log'][-1]['offset']==1 and states['new-appended']['logEnd']==2)
check('business event IDs remain equal across new application send',len({x['eventId']for x in states['new-appended']['log']})==1)
check('old failed Future not rewritten by B success',states['new-complete']['future']['state']=='failed' and states['new-complete']['newFuture']['state']=='success')
check('local error before accumulator creates no Future or Produce',states['local-failed']['log']==[]and states['local-failed']['future']['state']=='absent'and not states['local-failed']['request'])
for name,s in states.items():
 check(name+' logEnd matches count',s['logEnd']==len(s['log']))
 check(name+' batch not simultaneously queued and inflight',not(set(s['queue'])&set(s['inflight'])))
 check(name+' expected offsets', [r['offset']for r in s['log']]==list(range(s['logEnd'])))
model={'schemaVersion':1,'episode':'kafka-send-confirmation','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','scope':'Finite teaching trace; actual source-level state-entry unit probe is separately documented in experiments/result.json, no Broker/network execution.','example':{'topic':'orders','partition':0,'eventId':'E01','orderId':'7042','producerA':{'producerId':501,'epoch':0},'producerB':{'producerId':902,'epoch':0},'oneRecordPerBatch':True},'states':states}
(D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');(D/'model-verification.json').write_text(json.dumps({'passed':True,'checks':len(checks),'assertions':checks,'modelSHA256':hashlib.sha256((D/'model.json').read_bytes()).hexdigest(),'scope':model['scope']},ensure_ascii=False,indent=2)+'\n');print(len(checks),'model assertions')
