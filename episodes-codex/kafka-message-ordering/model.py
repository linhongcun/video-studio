#!/usr/bin/env python3
"""Finite teaching states for MQ06. Not Broker, Kafka scheduler or banking simulation."""
from pathlib import Path
import copy,json,hashlib
D=Path(__file__).resolve().parent
EVENTS=[{'eventId':'E01','type':'OrderPaid','orderId':'7042','key':'7042','targetStatus':'PAID'}, {'eventId':'E02','type':'OrderRefunded','orderId':'7042','key':'7042','targetStatus':'REFUNDED'}]
route={'key':'7042','encoding':'UTF-8','hex':'37303432','murmur2Signed':1934056876,'positiveHash':1934056876,'partitionCount':2,'partition':'P0'}
s={'branch':'write','resetBefore':False,'producer':{'sourceOrder':['E01','E02'],'encoded':{},'routing':{},'queue':{'P0':[],'P1':[]},'inflight':[],'sentComplete':[]},'log':{'P0':[],'P1':[]},'consumer':{'position':{'P0':0,'P1':0},'scanOffset':0,'buffer':[],'returned':[]},'application':{'mode':'serial','projection':'PENDING','dispatchOrder':[],'tasks':{'E01':'not-dispatched','E02':'not-dispatched'},'completionOrder':[],'writes':[]},'event':{'kind':'initial'}}
timeline=[]
def snap(id,label,kind=None,reset=False):
 s['resetBefore']=reset
 if kind:s['event']={'kind':kind}
 timeline.append({'id':id,'label':label,**copy.deepcopy(s)})
def queue(e,b):s['producer']['queue']['P0'].append({'batchId':b,'eventIds':[e]})
def drain(e,b):
 first=s['producer']['queue']['P0'].pop(0);assert first=={'batchId':b,'eventIds':[e]};assert not s['producer']['inflight'];s['producer']['inflight'].append(first)
def append(e,b):
 first=s['producer']['inflight'].pop(0);assert first=={'batchId':b,'eventIds':[e]}
 s['log']['P0'].append({**copy.deepcopy(next(x for x in EVENTS if x['eventId']==e)),'partition':'P0','offset':len(s['log']['P0'])});s['producer']['sentComplete'].append(e)
def deliver(e):
 record=s['log']['P0'][s['consumer']['scanOffset']];assert record['eventId']==e;s['consumer']['buffer'].append(e);s['consumer']['scanOffset']=record['offset']+1
def finish_collection():
 s['consumer']['position']['P0']=s['consumer']['scanOffset'];s['consumer']['returned']=copy.deepcopy(s['consumer']['buffer'])
snap('initial','两个已发生的有效事件，确定先支付后退款')
s['producer']['encoded']={e['eventId']:route['hex']for e in EVENTS};snap('same-key-bytes','两条订单7042都序列化成相同字节')
s['producer']['routing']={e['eventId']:'P0'for e in EVENTS};snap('same-partition','1934056876对2取余0，两条都选P0')
queue('E01','B1');snap('paid-queued','B1在P0队列尾，含E01')
drain('E01','B1');snap('paid-inflight','后台取P0队头B1，只有这一请求在途')
append('E01','B1');snap('paid-appended','先完成E01发送，P0写入offset0')
queue('E02','B2');snap('refund-queued','E01完成后B2入P0队列尾')
drain('E02','B2');snap('refund-inflight','E01完成后，后台取P0队头B2')
append('E02','B2');snap('both-appended','P0按先后保留E01@0和E02@1')
log_common=copy.deepcopy(s['log']);log_sha=hashlib.sha256(json.dumps(log_common,sort_keys=True).encode()).hexdigest()
deliver('E01');snap('collector-paid','迭代取记录0，加入内部列表，客户端position仍0')
deliver('E02');snap('collector-buffered-both','记录1接在内部列表后面，客户端position仍0')
finish_collection();snap('collector-both','收集完成，position更新到2，按E01/E02返回应用')
def reset_app(mode,branch,id,label):
 s['branch']=branch;s['consumer']={'position':{'P0':0,'P1':0},'scanOffset':0,'buffer':[],'returned':[]};s['application']={'mode':mode,'projection':'PENDING','dispatchOrder':[],'tasks':{'E01':'not-dispatched','E02':'not-dispatched'},'completionOrder':[],'writes':[]};snap(id,label,'reset-common-log-and-projection',True)
def dispatch(e,status='running'):
 a=s['application'];a['dispatchOrder'].append(e);a['tasks'][e]=status
 if a['mode']!='concurrent':assert not any(v in ['running','paused-before-write']for k,v in a['tasks'].items()if k!=e)
def complete(e):
 a=s['application'];assert a['tasks'][e]=='running';a['tasks'][e]='complete';a['projection']=next(x['targetStatus']for x in EVENTS if x['eventId']==e);a['completionOrder'].append(e);a['writes'].append({'eventId':e,'projection':a['projection'],'writeOrdinal':len(a['writes'])+1})
s['branch']='serial';dispatch('E01');snap('serial-paid-running','应用先处理支付投影')
complete('E01');snap('serial-paid-done','支付处理实际写成PAID')
dispatch('E02');snap('serial-refund-running','上一条写完才处理退款')
complete('E02');snap('serial-refund-done','最后写成REFUNDED')
reset_app('concurrent','concurrent','async-reset','独立对照：同一保留日志、投影回PENDING、读取从0开始')
deliver('E01');deliver('E02');finish_collection();snap('async-delivered','客户端依旧返回E01在前E02在后')
dispatch('E01','paused-before-write');snap('async-paid-paused','先提交的支付任务已启动，在实际写入前等待屏障')
dispatch('E02');snap('async-refund-running','后提交的退款任务并发运行')
complete('E02');snap('async-refund-done','退款先完成，投影REFUNDED，支付任务尚未结束')
s['application']['tasks']['E01']='running';snap('async-paid-resumed','释放屏障，支付任务继续')
complete('E01');snap('async-paid-done','支付后完成覆盖投影为PAID；日志与交付顺序都没变')
reset_app('per-order-serial','per-order','ordered-reset','正确对照：再次固定相同日志和起始页面，只改为按订单串行')
deliver('E01');deliver('E02');finish_collection();snap('ordered-delivered','同样E01/E02返回，在7042的应用队列中等候')
dispatch('E01');snap('ordered-paid-running','仅放行7042当前一条支付任务')
complete('E01');snap('ordered-paid-done','支付实际写完才能放行下一条')
dispatch('E02');snap('ordered-refund-running','现在放行退款任务')
complete('E02');snap('ordered-refund-done','按订单完成E01/E02，最终REFUNDED')
checks=0;complete_log_seen=False
for i,x in enumerate(timeline):
 assert x['producer']['sourceOrder']==['E01','E02'];checks+=1
 for part,records in x['log'].items():
  assert [r['offset']for r in records]==list(range(len(records)));assert all(r['partition']==part for r in records);checks+=2
 assert len({e['eventId']for records in x['log'].values()for e in records})==sum(len(v)for v in x['log'].values());checks+=1
 assert x['consumer']['returned']in [[],['E01'],['E01','E02']];checks+=1
 assert x['consumer']['buffer']in [[],['E01'],['E01','E02']];checks+=1
 assert x['consumer']['position']['P0']==(2 if x['consumer']['returned']else 0);checks+=1
 assert not x['consumer']['returned']or x['consumer']['returned']==x['consumer']['buffer'];checks+=1
 if x['id']=='both-appended':complete_log_seen=True
 if complete_log_seen:assert x['log']==log_common;checks+=1
 assert len(x['producer']['inflight'])<=1;checks+=1
 a=x['application'];assert a['projection']==(a['writes'][-1]['projection']if a['writes']else'PENDING');checks+=1
 assert a['completionOrder']==[w['eventId']for w in a['writes']];checks+=1
 assert a['dispatchOrder']in [[],['E01'],['E01','E02']];checks+=1
 if a['mode']!='concurrent':assert a['completionOrder']in [[],['E01'],['E01','E02']];checks+=1
 if x['resetBefore']:assert x['log']==log_common and a['projection']=='PENDING'and not a['completionOrder']and x['consumer']['position']['P0']==0;checks+=1
assert route['positiveHash']%2==0;checks+=1
assert next(x for x in timeline if x['id']=='async-paid-done')['application']['completionOrder']==['E02','E01'];checks+=1
assert next(x for x in timeline if x['id']=='ordered-refund-done')['application']['projection']=='REFUNDED';checks+=1
real=(D/'experiments/key-route.stdout.txt').read_text();assert 'utf8Hex=37303432 murmur2Signed=1934056876 positive=1934056876 partitions=2 selected=0'in real;checks+=1
model={'schemaVersion':1,'episode':'kafka-message-ordering','kind':'finite-teaching-model-not-Kafka-runtime','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','events':EVENTS,'keyRoute':route,'conditions':{'sourceBusinessOrder':'Paid happened before Refunded; events notify downstream projection only','singleProducer':True,'singleSendThread':True,'E01SendCompleteBeforeE02':True,'partitionCountStable':2,'explicitPartition':None,'customPartitioner':False,'partitioner.ignore.keys':False,'keySerializer':'StringSerializer UTF-8','acks':'all','enable.idempotence':True,'max.in.flight.requests.per.connection':1,'consumerProtocol':'classic','partition.assignment.strategy':'RangeAssignor','consumerMembers':1,'enable.auto.commit':False,'initialFetchOffset':0,'projectionMeaning':'State read model for order7042; no funds transfer','asyncInterleaving':'latch-controlled teaching interleaving; not a latency measurement'},'commonRetainedLogSHA256':log_sha,'timeline':timeline}
(D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');(D/'model-verification.json').write_text(json.dumps({'passed':True,'checks':checks,'snapshots':len(timeline),'actualKeyRouteEvidence':{'file':'experiments/key-route.stdout.txt','sha256':hashlib.sha256(real.encode()).hexdigest()},'scope':'Finite ownership/order/state checks plus actual built-in key-route class output. Not Broker/runtime concurrency or comprehension proof.'},ensure_ascii=False,indent=2)+'\n');print(checks,'checks',len(timeline),'snapshots')
