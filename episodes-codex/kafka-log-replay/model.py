#!/usr/bin/env python3
"""MQ03 deterministic teaching model. Does not run a Kafka broker or client.

Only the P0 lane is expanded. At the start both groups already completed P1
and committed its next offset 2. Every poll returns exactly one record here.
"""
from copy import deepcopy
import json
from pathlib import Path
D=Path(__file__).resolve().parent
RECORDS={
 'P0':[{'eventId':'E01','orderId':'7042','offset':0},{'eventId':'E03','orderId':'7044','offset':1}],
 'P1':[{'eventId':'E02','orderId':'7043','offset':0},{'eventId':'E04','orderId':'7045','offset':1}]}

def initial():
 return {'groups':{
  'notify':{'activeMembers':['N1','N2','N3'],'assignments':{'N1':['P0'],'N2':['P1'],'N3':[]},'position':{'P0':0,'P1':2},'committed':{'P0':0,'P1':2},'processed':{'P0':[],'P1':['E02','E04']}},
  'points':{'activeMembers':['S1'],'assignments':{'S1':['P0','P1']},'position':{'P0':0,'P1':2},'committed':{'P0':0,'P1':2},'processed':{'P0':[],'P1':['E02','E04']}}},
  'log':{p:{'startOffset':0,'endOffset':2,'records':deepcopy(rs),'segments':[{'baseOffset':0,'endOffset':2,'closed':True,'retentionEligible':False,'deleted':False},{'baseOffset':2,'endOffset':2,'closed':False,'retentionEligible':False,'deleted':False}]} for p,rs in RECORDS.items()}}

def poll_one(state,group,pid):
 g=state['groups'][group]
 if not g['activeMembers'] or g['position'][pid] is None:raise ValueError('group has no active reader')
 pos=g['position'][pid]; log=state['log'][pid]
 if pos<log['startOffset']:raise ValueError('out of range; deleted records are unavailable')
 record=next((r for r in log['records'] if r['offset']>=pos),None)
 if record is None:return None
 g['position'][pid]=record['offset']+1
 return deepcopy(record)

def process(state,group,pid,record):
 # Observation of application handling, NOT proof that side effects commit safely.
 state['groups'][group]['processed'][pid].append(record['eventId'])

def commit(state,group,pid,next_offset):
 g=state['groups'][group]
 if not g['activeMembers']:raise ValueError('no active owner in this teaching scenario')
 if next_offset>g['position'][pid]:raise ValueError('would commit unread records in this scenario')
 g['committed'][pid]=next_offset

def stop_group(state,group):
 g=state['groups'][group];g['activeMembers']=[];g['assignments']={}
 g['position']={p:None for p in g['position']}

def reset_offset(state,group,pid,requested,execute=True):
 g=state['groups'][group]
 if g['activeMembers']:raise ValueError('group must be inactive, including idle members')
 log=state['log'][pid]
 # CLI --to-offset range check clamps to available start/end (fixed-source evidence).
 prepared=max(log['startOffset'],min(requested,log['endOffset']))
 if execute:g['committed'][pid]=prepared
 return {'group':group,'partition':pid,'requestedOffset':requested,'preparedOffset':prepared,'executed':execute}

def restart_notify(state):
 g=state['groups']['notify'];g['activeMembers']=['N1','N2','N3'];g['assignments']={'N1':['P0'],'N2':['P1'],'N3':[]}
 g['position']=deepcopy(g['committed'])

def clean_old_segment(state,pid):
 log=state['log'][pid];old=log['segments'][0]
 if not old['closed'] or not old['retentionEligible']:raise ValueError('old segment not eligible')
 old['deleted']=True
 log['records']=[r for r in log['records'] if r['offset']>=old['endOffset']]
 log['startOffset']=old['endOffset']

def build():
 s=initial();timeline=[]
 def snap(stage_id,label,kind,branch='main',**event):
  timeline.append({'id':stage_id,'label':label,'branch':branch,'event':{'kind':kind,**event},**deepcopy(s)})
 snap('initial','两组P1已完成，聚焦P0的下一条位置0','initial')
 for eid,offset in [('E01',0),('E03',1)]:
  r=poll_one(s,'notify','P0');assert r['eventId']==eid
  snap('notify-poll-'+eid.lower(),'通知收到'+eid+'，读取位置推进，恢复点尚未变','poll',group='notify',partition='P0',record=r)
  process(s,'notify','P0',r)
  snap('notify-process-'+eid.lower(),'应用处理'+eid+'，尚未提交消费进度','process',group='notify',partition='P0',record=r)
  commit(s,'notify','P0',offset+1)
  snap('notify-commit-'+eid.lower(),'通知提交下一条位置'+str(offset+1),'commit',group='notify',partition='P0',nextOffset=offset+1)
 for eid,offset in [('E01',0),('E03',1)]:
  r=poll_one(s,'points','P0');assert r['eventId']==eid
  snap('points-poll-'+eid.lower(),'积分独立读取'+eid,'poll',group='points',partition='P0',record=r)
  process(s,'points','P0',r);commit(s,'points','P0',offset+1)
  snap('points-commit-'+eid.lower(),'积分独立处理并提交'+str(offset+1),'process-commit',group='points',partition='P0',record=r,nextOffset=offset+1)
 stop_group(s,'notify');snap('notify-inactive','停止通知组全部实例，包括空闲N3','stop-group',group='notify')
 event=reset_offset(s,'notify','P0',0,execute=False)
 snap('reset-dry-run','预览：仅通知组P0计划重置到0，尚未修改','reset-dry-run',**event)
 event=reset_offset(s,'notify','P0',0)
 snap('reset-p0','执行：仅通知组P0恢复点由2变0','reset-execute',**event)
 restart_notify(s);snap('notify-restart','重新启动，P0从已提交位置0恢复读取','restart',group='notify')
 for eid,offset in [('E01',0),('E03',1)]:
  r=poll_one(s,'notify','P0');assert r['eventId']==eid
  snap('replay-poll-'+eid.lower(),'通知再次读取原日志中的'+eid,'poll',group='notify',partition='P0',record=r,replay=True)
  process(s,'notify','P0',r);commit(s,'notify','P0',offset+1)
  snap('replay-commit-'+eid.lower(),'本例重新处理并提交'+str(offset+1),'process-commit',group='notify',partition='P0',record=r,nextOffset=offset+1,replay=True)
 s['log']['P0']['segments'][0]['retentionEligible']=True
 snap('retention-eligible','另一边界：旧封闭段满足保留条件，尚未完成清理','retention-eligible',branch='retention',partition='P0')
 clean_old_segment(s,'P0')
 snap('retention-cleaned','旧封闭段整段已清理，最早可用位置成为2','retention-cleaned',branch='retention',partition='P0')
 return {'schemaVersion':1,'episode':'kafka-log-replay','kind':'deterministic-teaching-model-not-broker-measurement','topic':'orders','partitions':[{'id':p,'records':deepcopy(rs)} for p,rs in RECORDS.items()],
  'conditions':{'kafkaVersion':'4.4.0','client':'Java KafkaConsumer 4.4.0 semantics','group.protocol':'classic','max.poll.records':1,'enable.auto.commit':False,'cleanup.policy':'delete','retention.ms':604800000,'retention.bytes':-1,'remote.storage.enable':False,'assignment':'one chosen legal stable assignment; N3 is an active but idle member','positionDefinition':'snapshot of the active partition owner client in-memory next-read position, not broker-persisted group-level read state','initialP1':'both groups processed E02/E04 and committed next offset 2 before this video starts','initialP0':'both groups have valid committed next offset 0; auto.offset.reset is not a rewind instruction','retentionBranch':'closed old P0 segment [0,2) has met deletion conditions and cleanup completes; not immediate per-record expiry','resetScope':'inactive notify only, orders:0 only; requested next offset 0; dry-run then execute','businessSideEffects':'not executed; repeated handling observations are not safe repeated external effects','crossPartitionOrder':'not asserted'},'timeline':timeline}

def verify(model):
 checks=[]
 def check(name,ok):
  assert ok,name;checks.append({'name':name,'pass':True})
 stages={x['id']:x for x in model['timeline']}
 baseline=stages['initial']; full_logs=baseline['log']
 check('four unique events',len({r['eventId'] for p in model['partitions'] for r in p['records']})==4)
 check('three notify members only two assigned',len(baseline['groups']['notify']['activeMembers'])==3 and baseline['groups']['notify']['assignments']['N3']==[])
 for st in model['timeline']:
  for name,g in st['groups'].items():
   if g['activeMembers']:
    assigned=[p for ps in g['assignments'].values() for p in ps]
    check(st['id']+'/'+name+' each partition one active owner',sorted(assigned)==['P0','P1'])
   else:check(st['id']+'/'+name+' inactive positions absent',all(v is None for v in g['position'].values()))
   check(st['id']+'/'+name+' P1 remains complete and next2',g['committed']['P1']==2 and g['processed']['P1']==['E02','E04'])
  if st['id']!='retention-cleaned':check(st['id']+' source logs retained',st['log']==full_logs or (st['id']=='retention-eligible' and st['log']['P0']['records']==full_logs['P0']['records']))
  if st['id'].startswith('points-'):check(st['id']+' notify unaffected',st['groups']['notify']==stages['notify-commit-e03']['groups']['notify'])
  if st['id'] in ['notify-inactive','reset-dry-run','reset-p0','notify-restart','replay-poll-e01','replay-commit-e01','replay-poll-e03','replay-commit-e03']:
   check(st['id']+' points unaffected',st['groups']['points']==stages['points-commit-e03']['groups']['points'])
 for eid,before,after in [('e01',0,1),('e03',1,2)]:
  p=stages['notify-poll-'+eid]['groups']['notify'];c=stages['notify-commit-'+eid]['groups']['notify']
  check('poll '+eid+' advances read but not committed',p['position']['P0']==after and p['committed']['P0']==before)
  check('poll '+eid+' is not business completion',eid.upper() not in p['processed']['P0'])
  check('commit '+eid+' stores next offset',c['committed']['P0']==after)
 s=initial();before=deepcopy(s)
 try:reset_offset(s,'notify','P0',0);check('active reset rejected',False)
 except ValueError:check('active reset rejected unchanged',s==before)
 s['groups']['notify']['activeMembers']=['N3'];s['groups']['notify']['assignments']={'N3':[]};before=deepcopy(s)
 try:reset_offset(s,'notify','P0',0);check('idle member reset rejected',False)
 except ValueError:check('idle member is still active reset rejected unchanged',s==before)
 check('dry run does not change state',stages['reset-dry-run']['groups']==stages['notify-inactive']['groups'])
 check('reset only notify P0 changes',stages['reset-p0']['groups']['notify']['committed']=={'P0':0,'P1':2})
 check('restart recovers from committed0',stages['notify-restart']['groups']['notify']['position']=={'P0':0,'P1':2})
 check('replay same identity and offset E01',stages['replay-poll-e01']['event']['record']==stages['notify-poll-e01']['event']['record'])
 check('replay same identity and offset E03',stages['replay-poll-e03']['event']['record']==stages['notify-poll-e03']['event']['record'])
 check('replay processing observations include duplicates',stages['replay-commit-e03']['groups']['notify']['processed']['P0']==['E01','E03','E01','E03'])
 s=initial();before=deepcopy(s)
 try:clean_old_segment(s,'P0');check('ineligible cleanup rejected',False)
 except ValueError:check('ineligible cleanup rejected unchanged',s==before)
 cleaned=stages['retention-cleaned'];check('cleanup old segment together new start2 no renumber',cleaned['log']['P0']['records']==[] and cleaned['log']['P0']['startOffset']==2 and cleaned['log']['P0']['endOffset']==2 and cleaned['log']['P0']['segments'][0]['deleted'])
 check('cleanup leaves P1 records',cleaned['log']['P1']==baseline['log']['P1'])
 s=deepcopy(cleaned);stop_group(s,'notify');event=reset_offset(s,'notify','P0',0)
 check('CLI request deleted offset clamps to earliest2',event['preparedOffset']==2 and s['groups']['notify']['committed']['P0']==2)
 restart_notify(s);check('earliest after cleanup does not restore deleted events',poll_one(s,'notify','P0') is None)
 return {'schemaVersion':1,'status':'pass','kind':'teaching-model-verification-not-Kafka-runtime-test','checkCount':len(checks),'checks':checks,'limitations':['No broker/client process, real offset admin command, segment deletion or business side effects were run.','One explicitly selected legal stable assignment; no rebalance timing or assignor implementation.','The retention branch assumes an eligible closed segment and completed cleanup; no real-time expiry guarantee.']}

if __name__=='__main__':
 m=build();r=verify(m)
 (D/'model.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 (D/'model-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(f"PASS {r['checkCount']} teaching-model checks")
