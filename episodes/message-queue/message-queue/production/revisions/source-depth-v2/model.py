#!/usr/bin/env python3
"""MQ01 source-backed teaching state machine; not a Kafka binary-log emulator."""
from pathlib import Path
from copy import deepcopy
import json
D=Path(__file__).resolve().parent
EVENT={'eventId':'E01','orderId':'7042','task':'notify-order'}
TEXT=json.dumps(EVENT,separators=(',',':'),ensure_ascii=False)
VALUE=TEXT.encode('utf-8')

def initial():
 return {'website':{'orderId':'7042','page':'editing','accepted':False,'queryResult':None},'producer':{'event':None,'valueText':None,'valueHex':None,'buffered':False,'requestSent':False,'confirmed':False},'log':{'topic':'orders','partition':'P0','records':[],'endOffset':0},'consumer':{'paused':True,'position':0,'fetchRequestedOffset':None,'responseValueHex':None,'decodedText':None,'applicationEvent':None,'pollReturned':False},'business':{'status':'waiting','executedEventIds':[],'savedResults':{}},'network':{'send':'none','response':'none','fetch':'none','returnRecord':'none'}}
def encode(s):
 s['producer'].update(event=deepcopy(EVENT),valueText=TEXT,valueHex=VALUE.hex())
def buffer(s):
 if s['producer']['valueHex'] is None:raise ValueError('serialize before buffering')
 s['producer']['buffered']=True

def append(s):
 if not (s['producer']['buffered'] or s['producer']['requestSent']):raise ValueError('no encoded record to send')
 offset=s['log']['endOffset'];s['producer'].update(buffered=False,requestSent=True)
 s['log']['records'].append({'eventId':EVENT['eventId'],'orderId':EVENT['orderId'],'offset':offset,'valueHex':s['producer']['valueHex'],'valueByteCount':len(bytes.fromhex(s['producer']['valueHex']))})
 s['log']['endOffset']=offset+1;s['network']['send']='received'

def confirm(s):
 if not s['log']['records']:raise ValueError('this example confirms only an appended record')
 s['producer']['confirmed']=True;s['network']['response']='received'

def accept(s):
 if not s['producer']['confirmed']:raise ValueError('chosen website policy replies after send success')
 s['website'].update(page='accepted',accepted=True)

def request_fetch(s):
 c=s['consumer']
 if c['paused']:raise ValueError('this chosen paused consumer does not issue a fetch')
 c['fetchRequestedOffset']=c['position'];s['network']['fetch']='sent'
 rs=[r for r in s['log']['records'] if r['offset']>=c['position']]
 if not rs:return None
 c['responseValueHex']=rs[0]['valueHex'];s['network']['returnRecord']='received'
 return deepcopy(rs[0])

def decode_record(s):
 c=s['consumer']
 if c['responseValueHex'] is None:raise ValueError('no fetched bytes')
 c['decodedText']=bytes.fromhex(c['responseValueHex']).decode('utf-8')

def advance_position(s,record):s['consumer']['position']=record['offset']+1

def deliver_record(s):s['consumer']['pollReturned']=True

def parse_application_fields(s):
 c=s['consumer']
 if not c['pollReturned']:raise ValueError('application has not received the string')
 c['applicationEvent']=json.loads(c['decodedText'])

def execute(s):
 c=s['consumer']
 if c['paused'] or not c['pollReturned']:raise ValueError('application cannot execute this task before delivery')
 s['business']['status']='running'

def complete(s):
 if s['business']['status']!='running':raise ValueError('business code has not been called')
 event=s['consumer']['applicationEvent'];s['business']['status']='completed';s['business']['executedEventIds'].append(event['eventId']);s['business']['savedResults'][event['eventId']]='completed'

def query(s):
 s['website']['queryResult']=s['business']['savedResults'].get('E01','waiting')
 s['website']['page']='completed' if s['website']['queryResult']=='completed' else 'accepted'

def build():
 s=initial();out=[]
 def snap(i,label,kind,**details):out.append({'id':i,'label':label,'event':{'kind':kind,**details},**deepcopy(s)})
 snap('initial','提交前，日志为空，消费者暂停','initial')
 s['website']['page']='submitting';snap('submitted','网站收到订单提交，要留下通知任务','submit')
 s['producer']['event']=deepcopy(EVENT);snap('event-created','同一E01是一份任务数据，不是可执行通知程序','event-created')
 encode(s);snap('value-encoded','字段先成为文本，再编码为UTF-8字节','serialize',payloadByteCount=len(VALUE))
 buffer(s);snap('producer-buffered','已编码记录进入生产者本地待发送缓冲','buffer')
 s['producer'].update(buffered=False,requestSent=True);s['network']['send']='in-flight';snap('produce-sent','后台向固定P0发送已编码记录','produce-send')
 append(s);snap('log-appended','从本分区下一编号0追加记录，并将下一编号改1','append',assignedOffset=0)
 confirm(s);snap('write-confirmed','本例按固定配置收到发送成功','confirm')
 accept(s);snap('page-accepted','页面已受理；通知程序暂停且业务仍待处理','accepted')
 query(s);snap('paused-waiting','消费者未执行，查询业务仍为等待','query')
 s['consumer']['paused']=False;s['network']['fetch']='ready';snap('consumer-resumed','恢复消费者，准备从本地读取位置0拉取','resume')
 record=request_fetch(s);snap('record-fetched','Fetch携P0/0，Kafka返回原记录的值字节','fetch',requestedOffset=0)
 decode_record(s);snap('record-decoded','客户端只解码回字符串，尚未交应用解析字段','deserialize')
 advance_position(s,record);snap('client-position-advanced','客户端写下一读取位置1，尚未poll返回','position-update')
 deliver_record(s);snap('record-delivered','poll已把解码文本交给应用','poll-return')
 parse_application_fields(s);snap('decoded-position-advanced','应用解析同一E01字段，读取位置早已为1','application-parse')
 execute(s);snap('business-running','应用业务代码被另行调用，读取位置1不代表完成','business-start')
 complete(s);snap('business-completed','通知模拟处理完成，单独保存E01业务结果','business-complete')
 query(s);snap('page-completed','页面查询业务结果后才显示通知完成','query')
 return {'schemaVersion':1,'episode':'message-queue','revision':'source-depth-v2','kind':'source-backed-finite-teaching-model-not-Kafka-runtime','eventData':EVENT,'encodedValue':{'text':TEXT,'encoding':'UTF-8','hex':VALUE.hex(),'byteCount':len(VALUE),'note':'Actual model value bytes only; not the entire Kafka binary record/batch/log format.'},'conditions':{'version':'Kafka/Java4.4.0','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','group.protocol':'classic','topic':'orders','partitionCount':1,'explicitPartition':'P0','compression.type':'none','recordFormat':'v2','serializer':'StringSerializer UTF-8','deserializer':'StringDeserializer UTF-8 then application JSON parse','acks':'all','enable.idempotence':True,'replicationFactor':1,'min.insync.replicas':1,'currentISRCount':1,'enable.auto.commit':False,'max.poll.records':1,'initialPosition':0,'retention':'source record retained throughout this finite example','websitePolicy':'reply accepted only after successful send; query business store separately','observerEventLabels':'eventId/orderId on log cards are decoded observer trace labels, not Broker interpretation or business dispatch','positionMeaning':'client in-memory next-read offset, not business status or persisted recovery offset','businessImplementation':'fictional app state machine separate from Kafka; notification provider not called','fileWrites':'source code establishes log file append; no per-record fsync guarantee or binary-layout emulation'},'timeline':out}

def verify(m):
 by={q['id']:q for q in m['timeline']};checks=[]
 def ck(n,v):assert v,n;checks.append({'name':n,'pass':True})
 ck('UTF-8 roundtrip returns exact same event',json.loads(bytes.fromhex(m['encodedValue']['hex']).decode('utf-8'))==EVENT)
 ck('sending leaves local buffer before Broker receive',by['produce-sent']['producer']['requestSent'] and not by['produce-sent']['producer']['buffered'])
 ck('decoded string precedes application fields',by['record-decoded']['consumer']['decodedText']==TEXT and by['record-decoded']['consumer']['applicationEvent'] is None and not by['record-decoded']['consumer']['pollReturned'])
 ck('client position advances before poll returns',by['client-position-advanced']['consumer']['position']==1 and not by['client-position-advanced']['consumer']['pollReturned'])
 ck('poll string return precedes app JSON parse',by['record-delivered']['consumer']['pollReturned'] and by['record-delivered']['consumer']['applicationEvent'] is None)
 ck('producer has no assigned Kafka offset before Broker append','offset' not in by['producer-buffered']['producer'])
 ck('payload enters buffer only after encoding',by['producer-buffered']['producer']['valueHex']==VALUE.hex() and by['producer-buffered']['producer']['buffered'])
 ck('Broker assigns current partition end0 then advances end1',by['log-appended']['log']['records'][0]['offset']==0 and by['log-appended']['log']['endOffset']==1)
 ck('log record preserves encoded payload',by['log-appended']['log']['records'][0]['valueHex']==VALUE.hex())
 ck('storage does not execute notification code',by['page-accepted']['business']==initial()['business'])
 ck('accepted follows send confirmation',by['page-accepted']['website']['accepted'] and by['page-accepted']['producer']['confirmed'])
 ck('paused consumer has no fetch and waiting business',by['paused-waiting']['consumer']['fetchRequestedOffset'] is None and by['paused-waiting']['website']['queryResult']=='waiting')
 ck('fetch request actually contains current next position0',by['record-fetched']['consumer']['fetchRequestedOffset']==0 and by['record-fetched']['consumer']['responseValueHex']==VALUE.hex())
 ck('client returns decoded same event and advances position1',by['decoded-position-advanced']['consumer']['applicationEvent']==EVENT and by['decoded-position-advanced']['consumer']['position']==1)
 ck('read position1 not business complete',by['decoded-position-advanced']['business']['status']=='waiting')
 ck('application separate execution required',by['business-running']['business']['status']=='running' and by['business-completed']['business']['savedResults']=={'E01':'completed'})
 ck('website only completes after business query',by['business-completed']['website']['page']=='accepted' and by['page-completed']['website']['page']=='completed')
 log=by['log-appended']['log']
 for st in m['timeline'][6:]:ck(st['id']+' preserves original log while reading/executing',st['log']==log)
 s=initial();encode(s);buffer(s);append(s);before=deepcopy(s)
 try:request_fetch(s);ck('paused fetch rejected',False)
 except ValueError:ck('paused consumer cannot fetch but stored record remains',s==before and len(s['log']['records'])==1)
 s['consumer']['paused']=False;s['consumer']['position']=1
 ck('changing read position to1 excludes earlier record0',request_fetch(s) is None)
 try:execute(s);ck('execute before delivery rejected',False)
 except ValueError:ck('log existence alone cannot execute business',s['business']['status']=='waiting')
 s=initial()
 try:accept(s);ck('accept before send success rejected',False)
 except ValueError:ck('chosen website cannot accept before confirmed write',s['website']['accepted'] is False)
 return {'schemaVersion':1,'status':'pass','checkCount':len(checks),'checks':checks,'limitations':['Finite teaching state machine, not Broker, Java runtime, filesystem durability or notification-provider experiment.','Encoded bytes are the model JSON value only; Kafka batch overhead and offset deltas are not emulated.','No commit/recovery, idempotence, replication or real notification side effects are tested.']}
if __name__=='__main__':
 m=build();v=verify(m)
 (D/'model.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(D/'model-verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(f"PASS {v['checkCount']} model checks")
