#!/usr/bin/env python3
"""Finite execution model for the selected Kafka 4.4 recovery/read chain.

This is a teaching model with symbolic file payloads, not a running Kafka log,
wire-format implementation, coordinator, retention scheduler or fault experiment.
"""
from pathlib import Path
from copy import deepcopy
import hashlib,json
D=Path(__file__).resolve().parent
E={'eventId':'E01','orderId':7042,'offset':0,'payload':'notification:order7042'}
PAYLOAD_SHA=hashlib.sha256(E['payload'].encode()).hexdigest()

def initial():
 return {'branch':'read','resetBefore':False,'consumer':{'id':'C1','alive':True,'position':0,'candidatePosition':None,'returned':[],'rawBytesArrived':False},'group':{'id':'notify','committed':0,'persistedBeforeExample':True},'log':{'startOffset':0,'endOffset':1,'segments':[{'baseOffset':0,'active':True,'records':[deepcopy(E)]}],'records':[deepcopy(E)],'payloadSha256':PAYLOAD_SHA},'fetch':{'offset':None,'status':'not-issued','records':[]},'queryReply':None}

def fetch(s,offset):
 s['fetch']={'offset':offset,'status':'issued','records':[]}

def respond(s):
 o=s['fetch']['offset']
 if o<s['log']['startOffset']:
  s['fetch'].update(status='out-of-range',records=[])
 else:
  s['fetch'].update(status='response',records=deepcopy([r for r in s['log']['records']if r['offset']>=o][:1]));s['consumer']['rawBytesArrived']=bool(s['fetch']['records'])

def exit_client(s):
 s['consumer'].update(alive=False,position=None,candidatePosition=None,returned=[],rawBytesArrived=False);s['fetch']={'offset':None,'status':'not-issued','records':[]};s['queryReply']=None

def new_client(s,id):
 s['consumer']={'id':id,'alive':True,'position':None,'candidatePosition':None,'returned':[],'rawBytesArrived':False}

states=[]
def keep(id,s,**extra):
 states.append({'id':id,**deepcopy(s),**extra})
s=initial();keep('initial',s)
fetch(s,s['consumer']['position']);keep('fetch-zero',s);respond(s);keep('bytes-arrived',s)
s['consumer']['candidatePosition']=s['fetch']['records'][-1]['offset']+1;keep('next-position-calculated',s)
s['consumer']['position']=s['consumer']['candidatePosition'];s['consumer']['candidatePosition']=None;s['consumer']['returned']=deepcopy(s['fetch']['records']);keep('position-advanced',s)
after_read=deepcopy(s);keep('uncommitted',s)
exit_client(s);s['branch']='recovery';keep('client-exited',s)
new_client(s,'C2');keep('new-client',s)
s['queryReply']=s['group']['committed'];s['consumer']['candidatePosition']=s['queryReply'];keep('saved-value-fetched',s)
s['consumer']['position']=s['consumer']['candidatePosition'];s['consumer']['candidatePosition']=None;keep('position-restored-zero',s)
fetch(s,s['consumer']['position']);keep('fetch-zero-again',s);respond(s);keep('same-bytes-arrived',s)
s['consumer']['position']=s['fetch']['records'][-1]['offset']+1;s['consumer']['returned']=deepcopy(s['fetch']['records']);keep('same-record-returned',s)
s=deepcopy(after_read);s['branch']='committed-one';s['resetBefore']=True;keep('counterfactual-before',s);s['resetBefore']=False;s['group']['committed']=1;keep('committed-one',s)
exit_client(s);keep('counterfactual-exited',s);new_client(s,'C3');keep('counterfactual-new-client',s);s['queryReply']=s['group']['committed'];s['consumer']['candidatePosition']=s['queryReply'];keep('saved-one-fetched',s)
s['consumer']['position']=s['consumer']['candidatePosition'];s['consumer']['candidatePosition']=None;keep('position-restored-one',s);fetch(s,s['consumer']['position']);respond(s);keep('fetch-one-no-old-record',s)
s=initial();s['branch']='retention';s['resetBefore']=True;s['log']['segments'][0]['active']=False;s['log']['segments'].append({'baseOffset':1,'active':True,'records':[]});keep('retained-closed-segment',s,retentionPremise='delete policy, no tiered storage, closed old segment eligible under retained-source conditions including high watermark; scheduler and real elapsed time not simulated')
s['resetBefore']=False;s['log']['segments']=s['log']['segments'][1:];s['log']['records']=[];s['log']['startOffset']=1;s['log']['payloadSha256']=None;keep('old-segment-deleted',s);fetch(s,0);respond(s);keep('old-offset-invalid',s)
M={x['id']:x for x in states};checks=[]
def check(name,value):
 assert value,name;checks.append({'name':name,'pass':True})
for a in states:
 check(a['id']+' snapshot owns copied records',a['consumer']['returned']is not a['log']['records'])
 check(a['id']+' committed persistent numeric value',a['group']['committed']in(0,1))
 check(a['id']+' inactive client has no persistent position',a['consumer']['alive']or a['consumer']['position']is None)
 if a['branch']!='retention':check(a['id']+' original immutable E01 retained',a['log']['records']==[E]and a['log']['payloadSha256']==PAYLOAD_SHA)
check('initial saved zero is explicit premise',M['initial']['group']['persistedBeforeExample'])
check('read moves position but not committed',M['position-advanced']['consumer']['position']==1 and M['position-advanced']['group']['committed']==0)
check('new client has no old memory position',M['new-client']['consumer']['id']=='C2'and M['new-client']['consumer']['position']is None)
check('queried value does not itself update client position',M['saved-value-fetched']['queryReply']==0 and M['saved-value-fetched']['consumer']['candidatePosition']==0 and M['saved-value-fetched']['consumer']['position']is None)
check('explicit assignment installs persisted zero',M['position-restored-zero']['consumer']['position']==M['position-restored-zero']['group']['committed']==0)
check('Fetch reads restored client value',M['fetch-zero-again']['fetch']['offset']==M['fetch-zero-again']['consumer']['position']==0)
check('same byte payload and record returned twice',M['bytes-arrived']['fetch']['records']==M['same-bytes-arrived']['fetch']['records']==[E])
check('counterfactual uses same after-read starting values',{k:v for k,v in M['counterfactual-before'].items()if k not in ['id','branch','resetBefore']}=={k:v for k,v in M['position-advanced'].items()if k not in ['id','branch','resetBefore']})
check('only changing saved commit changes restart fetch',M['position-restored-one']['consumer']['position']==1 and M['fetch-one-no-old-record']['fetch']=={'offset':1,'status':'response','records':[]})
check('committed one does not delete E01',M['fetch-one-no-old-record']['log']['records']==[E])
check('closed old segment removed as whole unit',M['old-segment-deleted']['log']['segments']==[{'baseOffset':1,'active':True,'records':[]}])
check('removed old bytes cannot be re-created by offset',M['old-offset-invalid']['fetch']['status']=='out-of-range'and M['old-offset-invalid']['log']['records']==[])
model={'schemaVersion':1,'episode':'kafka-log-replay','revision':'source-depth-v2','kind':'finite teaching execution model, not a Kafka runtime experiment','kafkaVersion':'4.4.0','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','payloadIdentityMeaning':'SHA of symbolic teaching payload only, not actual Kafka file encoding or measured disk bytes','event':E,'timeline':states}
(D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');(D/'model-check.json').write_text(json.dumps({'passed':True,'checks':checks,'checkCount':len(checks),'snapshots':len(states),'scope':model['kind']},ensure_ascii=False,indent=2)+'\n');print(len(states),'snapshots',len(checks),'finite checks passed')
