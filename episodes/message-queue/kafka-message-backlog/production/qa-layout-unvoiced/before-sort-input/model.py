#!/usr/bin/env python3
"""Finite per-partition teaching execution; never a Kafka throughput benchmark."""
from pathlib import Path
import copy,json,hashlib
D=Path(__file__).resolve().parent
members=[{'alias':f'C{i:02}','memberId':f'member-{i:02}','old':i in [7,12]}for i in range(1,13)]
parts=['P0','P1'];timeline=[];checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
def assign(rows):
 rows=sorted(rows,key=lambda x:x['memberId']);q,r=divmod(2,len(rows));out={m['alias']:[]for m in rows};left=list(parts)
 for i,m in enumerate(rows):
  n=q+(i<r);out[m['alias']]=left[:n];left=left[n:]
 return out
old=assign([m for m in members if m['old']]);full=assign(members)
s={'phase':'assignment-comparison-only','members':[m for m in members if m['old']],'assignments':old,'localAssignments':{},'calculation':{'base':1,'remainder':0,'remaining':[]},'businessTrackingStarted':False,'timeSeconds':0,'arrived':0,'completed':[],'log':{p:[]for p in parts},'unread':{p:[]for p in parts},'inFlight':{p:[]for p in parts},'positions':{p:0 for p in parts},'committed':{p:0 for p in parts},'lastStep':None}
def snap(id,label):
 v=copy.deepcopy(s);v.update(id=id,label=label,unfinished=v['arrived']-len(v['completed']));timeline.append(v)
snap('old-two-assignment','Only compare allocation; old members have P0/P1, no business task has begun')
s['members']=members;s['assignments']={m['alias']:[]for m in members};s['calculation']={'base':None,'remainder':None,'remaining':parts.copy()};snap('twelve-empty','Twelve subscribed members start with empty allocation lists')
snap('rank-sorted','C01..C12 are aliases after member.id lexical sorting, not client.id or join order')
s['calculation'].update(base=0,remainder=2);snap('quota-zero-two','Integer quotient zero; two extra allocations remain')
s['assignments']['C01']=['P0'];s['calculation'].update(remainder=1,remaining=['P1']);snap('assign-first','Assign P0 once; remove its candidate')
s['assignments']['C02']=['P1'];s['calculation'].update(remainder=0,remaining=[]);snap('assign-second','P1 assigned once; ten lists remain empty')
check('finite allocation equals independently computed Range example',s['assignments']==full)
s['localAssignments']=copy.deepcopy(full);s['phase']='stable-business-tracking';s['businessTrackingStarted']=True;snap('installed-stable','Independent common starting point: assignment stable, no old in-flight task is erased or transferred')
next_id=1
owner={p:a for a,ps in full.items()for p in ps}
def arrive(destinations):
 global next_id
 for p in destinations:
  rec={'eventId':f'E{next_id:02}','orderId':7041+next_id,'partition':p,'offset':len(s['log'][p])};next_id+=1;s['log'][p].append(rec);s['unread'][p].append(copy.deepcopy(rec));s['arrived']+=1

def poll_one(p):
 if not s['inFlight'][p] and s['unread'][p]:
  check('poll only installed partition for '+owner[p],p in s['localAssignments'][owner[p]])
  rec=s['unread'][p].pop(0);s['inFlight'][p].append(rec);s['positions'][p]=rec['offset']+1

def complete_one(p):
 if s['inFlight'][p]:s['completed'].append(s['inFlight'][p].pop(0));return 1
 return 0
arrive(['P0','P1','P0','P1']);snap('first-four-arrived','First teaching second begins with two new records per partition')
for p in parts:poll_one(p)
snap('first-two-polled','E01/E02 returned to application, positions advanced, neither business effect completed')
snap('notify-waiting','Each partition serially awaits its notification API success; no extra application workers assumed')
completed={p:complete_one(p)for p in parts};s['timeSeconds']=1;s['lastStep']={'input':{'P0':2,'P1':2},'completed':completed};snap('first-business-done','Both first notification calls succeeded at end of teaching second1; E01 completed')
def step(destinations,id,label):
 before={p:len(s['unread'][p])+len(s['inFlight'][p])for p in parts};incoming={p:destinations.count(p)for p in parts};arrive(destinations)
 for p in parts:poll_one(p)
 actual={p:complete_one(p)for p in parts};s['timeSeconds']+=1;s['lastStep']={'input':incoming,'completed':actual}
 for p in parts:check('per-partition actual completion bounded by available '+id+p,actual[p]==min(before[p]+incoming[p],1))
 snap(id,label)
for t in range(2,6):step(['P0','P1','P0','P1'],f'growth-tick-{t}','Two arrivals per partition per teaching second, one actual completion each')
check('five-second arithmetic',s['arrived']==20 and len(s['completed'])==10 and all(len(s['unread'][p])==5 for p in parts))
snap('lower-rate-start','Change only input: one event per second alternating P0/P1; each starts with five unfinished')
for t in range(1,11):step(['P0'if t%2 else'P1'],f'drain-tick-{t}','One alternating arrival, per-partition min(available,1) completions')
check('ten-second drain under explicit alternating routing',s['arrived']==30 and len(s['completed'])==30 and all(not s['unread'][p]for p in parts))
step(['P0'],'after-clear-next-tick','Only one available event is completed; no negative unfinished count')
check('not completing nonexistent second task',sum(s['lastStep']['completed'].values())==1)
for v in timeline:
 allrecords=[r for p in parts for r in v['log'][p]];pending=[r for p in parts for r in v['unread'][p]+v['inFlight'][p]]
 check(v['id']+' arrived equals preserved log records',v['arrived']==len(allrecords))
 check(v['id']+' unfinished bookkeeping',v['unfinished']==len(pending)>=0)
 check(v['id']+' every event in exactly one business state',sorted(r['eventId']for r in pending+v['completed'])==sorted(r['eventId']for r in allrecords))
 check(v['id']+' no duplicate completion',len(v['completed'])==len({r['eventId']for r in v['completed']}))
 check(v['id']+' at most one application notification per partition',all(len(v['inFlight'][p])<=1 for p in parts))
 if v['businessTrackingStarted']:
  check(v['id']+' only two nonempty stable lists',sum(bool(ps)for ps in v['localAssignments'].values())==2)
  check(v['id']+' old identities not guaranteed owners',v['localAssignments']['C07']==v['localAssignments']['C12']==[])
first=next(v for v in timeline if v['id']=='first-two-polled');check('poll is not completion',sum(first['positions'].values())==2 and len(first['completed'])==0 and first['unfinished']==4)
cleared=next(v for v in timeline if v['id']=='drain-tick-10');check('committed lag not business pending',sum(len(cleared['log'][p])-cleared['committed'][p]for p in parts)==30 and cleared['unfinished']==0)
model={'schemaVersion':1,'episode':'kafka-message-backlog','kind':'finite-teaching-model-not-benchmark','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','conditions':{'protocol':'classic','assignor':'RangeAssignor','group':'notify','subscription':['orders'],'partitions':2,'group.instance.id':None,'client.rack':None,'max.poll.records':1,'enable.auto.commit':False,'stableAssignmentOnly':True,'failuresAndRetries':False,'application':'one serial notification call per partition; success response completes business; no application worker offload','routing':'4/s: two per partition; reduced1/s: one each teaching second alternating P0/P1','rates':'Teaching assumptions only, each partition one successful notification per teaching second; not measured throughput','clock':'At each teaching interval left edge append arrivals; right edge finish min(available,1) per partition; animation seconds are independent','identity':'C01..C12 aliases of sorted example member-id rank, not client.id, arrival order or expected runtime-generated names'},'timeline':timeline}
(D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');(D/'model-verification.json').write_text(json.dumps({'passed':True,'assertions':len(checks),'snapshots':len(timeline),'checks':checks,'scope':'Finite per-partition accounting and source-constrained allocation; no real Kafka or throughput test'},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'snapshots':len(timeline),'checks':len(checks)}))
