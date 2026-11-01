#!/usr/bin/env python3
"""MQ04 finite teaching model, not a Kafka broker/client/network experiment.

Unknown branch: the Broker has appended the original batch, but no successful
ProduceResponse is processed before delivery expiry. Idempotent internal retry
uses the same session/batch identity. After final failure, a new application send
in a new producer session is deliberately shown as a duplicate-business risk.
"""
from copy import deepcopy
import json
from pathlib import Path
D=Path(__file__).resolve().parent
EVENT={'eventId':'E01','orderId':'7042','topic':'orders','partition':'P0'}
CONFIG={'kafkaVersion':'4.4.0','client':'Java KafkaProducer 4.4.0 semantics','acks':'all','enable.idempotence':True,'retries':2147483647,'max.in.flight.requests.per.connection':1,'request.timeout.ms':45000,'delivery.timeout.ms':120000,'linger.ms':0,'max.block.ms':60000,'retry.backoff.ms':100,'retry.backoff.max.ms':1000,'topic.partitionCount':1,'topic.replicationFactor':3,'topic.min.insync.replicas':2,'currentISRCount':3,'replica.lag.time.max.ms':30000,'transactional.id':None}

def fresh_producer(session='A',send_count=0):
 return {'sessionId':session,'active':True,'applicationSendCount':send_count,'currentSendId':None,'batchSequence':None,'sendReturn':'none','futureState':'none','callbackResult':'none','senderObservedResult':'not-called','error':None,'metadata':None,'payloadInAccumulator':False,'recordProduceSent':False}

def initial():
 return {'producer':fresh_producer(),'attempts':[],'log':{'topic':'orders','partition':'P0','records':[],'endOffset':0},'consumer':{'businessComplete':False,'status':'通知待处理','handledEventIds':[]},'automaticRetryCount':0,'links':{'send':'none','response':'none'}}

def current(s):return s['attempts'][-1]
def identity(attempt):return {k:attempt[k] for k in ['applicationSendId','producerSession','batchSequence']}

def sync_current(s):
 a=current(s);p=s['producer']
 for key in ['futureState','error','metadata','senderObservedResult','callbackResult']:
  p[key]=deepcopy(a[key])

def send(s,valid=True):
 p=s['producer']
 if not p['active']:raise ValueError('producer closed')
 p['applicationSendCount']+=1
 send_id='send-'+str(p['applicationSendCount']);p['currentSendId']=send_id
 if not valid:
  # Chosen custom serializer rejects before accumulator.append; no Future returned.
  p.update({'sendReturn':'throws','futureState':'none','senderObservedResult':'definitely-not-sent','error':{'type':'org.apache.kafka.common.errors.SerializationException','surface':'send throws synchronously'},'callbackResult':'none','metadata':None,'payloadInAccumulator':False,'recordProduceSent':False})
  return None
 a={'applicationSendId':send_id,'producerSession':p['sessionId'],'batchSequence':0,'eventId':EVENT['eventId'],'futureState':'pending','callbackResult':'none','senderObservedResult':'pending','error':None,'metadata':None,'terminal':False,'appendOffset':None}
 s['attempts'].append(a);p.update({'batchSequence':0,'sendReturn':'future','payloadInAccumulator':True,'recordProduceSent':False});sync_current(s)
 s['links']={'send':'buffered','response':'none'}
 return a

def broker_append(s,automatic_retry=False):
 a=current(s);p=s['producer'];p['recordProduceSent']=True;p['payloadInAccumulator']=False
 ident=identity(a)
 existing=next((r for r in s['log']['records'] if r['attemptIdentity']==ident),None)
 if existing:
  if not automatic_retry:raise ValueError('same batch identity resubmitted without retry marker')
  offset=existing['offset']
 else:
  offset=s['log']['endOffset'];s['log']['records'].append({**EVENT,'offset':offset,'attemptIdentity':ident});s['log']['endOffset']=offset+1
 a['appendOffset']=offset;s['links']={'send':'retry' if automatic_retry else 'in-flight','response':'withheld'}
 return offset

def metadata(a):return {'topic':'orders','partition':'P0','offset':a['appendOffset']}

def complete_success(s):
 a=current(s)
 if a['terminal']:
  # Kafka ProducerBatch final FAILED future is not rewritten by a late response.
  s['links']['response']='late-ignored';return False
 if a['appendOffset'] is None:raise ValueError('this acknowledged example has no appended record')
 a.update({'futureState':'success','callbackResult':'success','senderObservedResult':'confirmed','metadata':metadata(a),'error':None,'terminal':True});sync_current(s);s['links']['response']='received-success';return True

def request_failure(s):
 # A retriable request timeout is not terminal while delivery deadline remains.
 a=current(s)
 if a['terminal']:raise ValueError('cannot retry a terminal attempt')
 s['links']={'send':'none','response':'request-timeout-retriable'}

def auto_retry(s):
 a=current(s)
 if a['terminal']:raise ValueError('cannot auto-retry a terminal attempt')
 s['automaticRetryCount']+=1
 return broker_append(s,automatic_retry=True)

def expire_delivery(s):
 a=current(s)
 if a['terminal']:raise ValueError('attempt already terminal')
 a.update({'futureState':'failed','callbackResult':'delivery-timeout','senderObservedResult':'unknown','metadata':None,'error':{'type':'org.apache.kafka.common.errors.TimeoutException','callbackException':'org.apache.kafka.common.errors.TimeoutException','futureGetException':'java.util.concurrent.ExecutionException','futureGetCause':'org.apache.kafka.common.errors.TimeoutException','reason':'delivery.timeout.ms reached without successful response processed'},'terminal':True});sync_current(s)
 s['links']={'send':'none','response':'delivery-expired'}

def close_producer(s):s['producer']['active']=False;s['links']={'send':'none','response':'none'}
def restart_producer(s):s['producer']=fresh_producer('B',send_count=s['producer']['applicationSendCount'])

def build():
 timeline=[]
 def snap(stage_id,branch,label,kind,reset=False,**details):
  timeline.append({'id':stage_id,'branch':branch,'resetBefore':reset,'label':label,'event':{'kind':kind,**details},**deepcopy(s)})
 s=initial();snap('normal-initial','normal','正常：从共同空日志起点开始','initial',True)
 send(s);snap('normal-buffered','normal','send返回结果对象，本例此时待后台发送','send-return')
 broker_append(s);s['links']['response']='in-flight';snap('normal-appended','normal','实际日志已追加E01@0，成功响应返回途中','append')
 complete_success(s);snap('normal-confirmed','normal','成功结果带回P0/offset0','success')
 snap('normal-business-pending','normal','发送确认已到，下游通知仍待处理','business-boundary')
 s=initial();snap('unknown-initial','unknown','重置到同样的空日志起点，只改变响应条件','initial',True)
 send(s);snap('unknown-buffered','unknown','同一事件再次演示，Future仍待定','send-return')
 broker_append(s);snap('unknown-appended','unknown','已追加E01@0，但成功响应不可见','append',successfulResponseProcessed=False)
 request_failure(s);snap('unknown-request-timeout','unknown','请求级可重试失败，尚未到总发送期限','request-timeout',deliveryDeadlineReached=False)
 auto_retry(s);snap('unknown-auto-retry','unknown','同会话同批次自动重试，日志仍仅一条','automatic-retry',representativeRetry=True,waitingOmitted=True)
 expire_delivery(s);snap('unknown-delivery-timeout','unknown','总期限到，发送结果最终失败；日志实际已有记录','delivery-timeout',elapsedDeliveryMs=120000,successfulResponseProcessed=False)
 close_producer(s);snap('unknown-producer-closed','unknown','关闭旧producer A，旧Future保持失败','producer-close')
 restart_producer(s);send(s);snap('unknown-app-resend-buffered','unknown','应用新producer B再次send同eventId，为新发送','application-resend')
 broker_append(s);s['links']['response']='in-flight';snap('unknown-app-resend-appended','unknown','新的应用发送追加E01@1，原@0仍在','append')
 complete_success(s);snap('unknown-app-resend-confirmed','unknown','第二次应用发送成功，两条具有相同eventId','success')
 s=initial();snap('serialization-initial','serialization','再回共同空日志起点，本地内容无法编码','initial',True)
 send(s,valid=False);snap('serialization-thrown','serialization','序列化同步抛错，该记录未入缓冲且日志空','serialization-error')
 return {'schemaVersion':1,'episode':'kafka-send-confirmation','kind':'deterministic-teaching-model-not-broker-measurement','event':EVENT,'partitions':[{'id':'P0','records':[]}],
  'conditions':{**CONFIG,'serializer':'chosen custom event serializer accepts valid payload; rejects the local-error payload with SerializationException before accumulator.append','initialState':'same empty orders/P0 log and pending consumer business in all three branches','sendReturnScheduling':'this normal/unknown example returns Future while pending; not an API guarantee that Future is always pending at return','unknownFault':'all successful ProduceResponses for original batch and its automatic retries remain unprocessed by client until delivery expiry; actual Broker append succeeds','automaticRetrySchedule':'one representative retry is expanded; additional waiting/retries are omitted, not an exact network/client timing simulation','deliveryFailure':'terminal Kafka TimeoutException in callback; Future.get wraps cause in ExecutionException; not Future.get(timeout) waiting timeout','failedCallbackMetadata':'no valid success metadata is used; callback metadata is not asserted always null','applicationResend':'after original attempt terminal failure, old producer A is closed; new producer B calls send again with same eventId','consumerBusiness':'never executed; confirmation does not imply business completion','timePresentation':'waiting compressed and explicitly marked non-real-time; no latency measurement','idempotenceScope':'automatic retry identity is producer session plus batch sequence, not eventId/key; no application/business exactly-once claim'},
  'branches':[{'id':'normal','title':'发送成功','initialSnapshot':'normal-initial','finalSnapshot':'normal-business-pending'}, {'id':'unknown','title':'结果未知','initialSnapshot':'unknown-initial','unknownSnapshot':'unknown-delivery-timeout','finalSnapshot':'unknown-app-resend-confirmed'}, {'id':'serialization','title':'确定未发送','initialSnapshot':'serialization-initial','finalSnapshot':'serialization-thrown'}],
  'timeline':timeline}

def verify(m):
 checks=[]
 def check(name,ok):
  assert ok,name;checks.append({'name':name,'pass':True})
 by={s['id']:s for s in m['timeline']}
 check('delivery timeout satisfies request plus linger',CONFIG['delivery.timeout.ms']>=CONFIG['request.timeout.ms']+CONFIG['linger.ms'])
 check('idempotence requirements valid',CONFIG['enable.idempotence'] and CONFIG['acks']=='all' and CONFIG['retries']>0 and CONFIG['max.in.flight.requests.per.connection']<=5)
 check('ISR meets min and RF',CONFIG['currentISRCount']>=CONFIG['topic.min.insync.replicas'] and CONFIG['currentISRCount']<=CONFIG['topic.replicationFactor'])
 initials=[by[b['initialSnapshot']] for b in m['branches']]
 check('three branches reset same empty log',all(x['resetBefore'] and x['log']==initials[0]['log'] for x in initials))
 check('three branches same business initially pending',all(x['consumer']==initials[0]['consumer'] for x in initials))
 for st in m['timeline']:
  p=st['producer'];rs=st['log']['records']
  check(st['id']+' all records same logical event',all(r['eventId']=='E01' and r['orderId']=='7042' and r['partition']=='P0' for r in rs))
  check(st['id']+' contiguous example offsets', [r['offset'] for r in rs]==list(range(len(rs))) and st['log']['endOffset']==len(rs))
  check(st['id']+' confirmation not business success',st['consumer']['businessComplete'] is False and st['consumer']['handledEventIds']==[])
  if p['senderObservedResult']=='confirmed':
   check(st['id']+' valid confirmed metadata locates own append',p['futureState']=='success' and p['metadata'] is not None and any(r['offset']==p['metadata']['offset'] and r['attemptIdentity']['applicationSendId']==p['currentSendId'] for r in rs))
  if p['senderObservedResult']=='unknown':check(st['id']+' unknown is terminal delivery failure',p['futureState']=='failed' and p['error']['type']=='org.apache.kafka.common.errors.TimeoutException')
 check('Future return before append not confirmation',by['normal-buffered']['producer']['futureState']=='pending' and by['normal-buffered']['log']['records']==[])
 check('append before response still pending',by['normal-appended']['producer']['futureState']=='pending' and len(by['normal-appended']['log']['records'])==1)
 check('normal success metadata P0@0',by['normal-confirmed']['producer']['metadata']=={'topic':'orders','partition':'P0','offset':0})
 check('request timeout not immediately terminal',by['unknown-request-timeout']['producer']['futureState']=='pending')
 check('automatic retry same identity no second append',by['unknown-auto-retry']['log']==by['unknown-appended']['log'] and by['unknown-auto-retry']['producer']['applicationSendCount']==1 and by['unknown-auto-retry']['automaticRetryCount']==1)
 u=by['unknown-delivery-timeout'];check('delivery failure while actual record exists',u['producer']['futureState']=='failed' and len(u['log']['records'])==1)
 check('old producer closed before new send',by['unknown-producer-closed']['producer']['active'] is False and by['unknown-app-resend-buffered']['producer']['sessionId']=='B')
 r=by['unknown-app-resend-confirmed'];check('application resend second same event new offset',len(r['log']['records'])==2 and {x['eventId'] for x in r['log']['records']}=={'E01'} and r['producer']['metadata']['offset']==1)
 check('resend has distinct producer identity',r['log']['records'][0]['attemptIdentity']!=r['log']['records'][1]['attemptIdentity'])
 check('original failed Future not rewritten on second success',r['attempts'][0]['futureState']=='failed' and r['attempts'][1]['futureState']=='success')
 local=by['serialization-thrown'];check('chosen local serialization synchronous no Future or Produce',local['producer']['sendReturn']=='throws' and local['producer']['futureState']=='none' and local['producer']['callbackResult']=='none' and local['producer']['recordProduceSent'] is False and local['log']['records']==[] and local['attempts']==[])
 s=deepcopy(u);before=deepcopy(current(s));accepted=complete_success(s)
 check('late success cannot change failed Future',accepted is False and current(s)==before and s['producer']['futureState']=='failed')
 # Same terminal sender observation is compatible with no Broker append as well.
 no_append=initial();send(no_append);expire_delivery(no_append)
 check('timeout alone cannot prove append or absence',no_append['producer']['senderObservedResult']==u['producer']['senderObservedResult'] and no_append['producer']['error']==u['producer']['error'] and no_append['log']['records']==[] and len(u['log']['records'])==1)
 no_send=initial();send(no_send);before=deepcopy(no_send)
 try:complete_success(no_send);check('success without append rejected',False)
 except ValueError:check('success without append rejected unchanged',no_send==before)
 terminal=deepcopy(u);before=deepcopy(terminal)
 try:auto_retry(terminal);check('retry terminal rejected',False)
 except ValueError:check('retry terminal rejected unchanged',terminal==before)
 return {'schemaVersion':1,'status':'pass','kind':'teaching-model-verification-not-Kafka-runtime-test','checkCount':len(checks),'checks':checks,'limitations':['No real Kafka Broker/client, serializer plugin or network fault injection ran.','Selected legal schedules only; no claim to reproduce complete producer retry/sequence implementation.','The displayed representative automatic retry preserves one batch identity; application resend is a separate new producer session.','Consumer business effects never run; no delivery or business exactly-once guarantee is inferred.']}

if __name__=='__main__':
 m=build();v=verify(m)
 (D/'model.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 (D/'model-verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 print(f"PASS {v['checkCount']} teaching-model checks")
