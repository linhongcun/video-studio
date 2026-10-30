#!/usr/bin/env python3
"""Finite teaching snapshots; cross-check actual separately executed Kafka classes."""
from pathlib import Path
import copy,json,hashlib,re
D=Path(__file__).resolve().parent
parts=[{'id':'P0','records':[{'eventId':'E01','orderId':'7042','offset':0},{'eventId':'E03','orderId':'7044','offset':1}]},{'id':'P1','records':[{'eventId':'E02','orderId':'7043','offset':0},{'eventId':'E04','orderId':'7045','offset':1}]}]
def group(gid,aliases,memberids):
 return {'id':gid,'members':[{'id':a,'memberId':m,'subscription':['orders'],'active':True} for a,m in zip(aliases,memberids)],'leader':aliases[0],'computed':False,'assignments':{a:[] for a in aliases},'syncResponses':{},'localAssignments':{a:None for a in aliases},'received':{a:[] for a in aliases},'requests':[]}
st={'groups':{'notify':group('notify',['N1','N2','N3'],['member-01','member-02','member-03']),'points':group('points',['S1'],['member-s1'])},'partitions':parts,'coordinator':{'phase':'not-joined','group':None,'leader':None,'subscriptions':[],'receivedWholeTable':False},'calculation':{'group':'notify','inputMembers':['N3','N1','N2'],'sortedMembers':[],'sortedPartitions':[],'base':None,'remainder':None,'unassigned':[],'activeMember':None}}
timeline=[]
def snap(id,label):
 timeline.append({'id':id,'label':label,**copy.deepcopy(st)})
def calculated(gid):
 g=st['groups'][gid];members=sorted(g['members'],key=lambda m:m['memberId']);q,r=divmod(len(parts),len(members));left=[p['id'] for p in parts];out={m['id']:[] for m in members}
 for m in members:
  n=q+(1 if r else 0);out[m['id']]=left[:n];left=left[n:];r=max(0,r-1)
 return out
snap('initial','同一日志，通知组与积分组尚未完成本次分配')
st['coordinator'].update(phase='joined',group='notify',leader='N1',subscriptions=['N3:orders','N1:orders','N2:orders']);snap('notify-joined','协调者收集同组订阅，N1取得完整本组名单')
st['calculation'].update(sortedPartitions=['P0','P1'],unassigned=['P0','P1']);snap('notify-inputs','组内分配者拿到分区元数据与订阅列表')
st['calculation'].update(sortedMembers=['N1','N2','N3'],base=0,remainder=2);snap('notify-divided','分区和成员排序，整数商0，余数2')
st['groups']['notify']['assignments']['N1']=['P0'];st['calculation'].update(remainder=1,unassigned=['P1'],activeMember='N1');snap('notify-assigned-n1','N1取得P0，候选剩P1，余数1')
st['groups']['notify']['assignments']['N2']=['P1'];st['groups']['notify']['computed']=True;st['calculation'].update(remainder=0,unassigned=[],activeMember='N2');snap('notify-assigned-n2','N2取得P1，候选为空，N3仍空')
assert st['groups']['notify']['assignments']==calculated('notify')
st['coordinator'].update(phase='sync-table',receivedWholeTable=True);snap('notify-sync-table','完整归属表交回协调者')
st['groups']['notify']['syncResponses']=copy.deepcopy(st['groups']['notify']['assignments']);st['coordinator']['phase']='responses-ready';snap('notify-responses','各自的返回列表已形成，尚未当成本地安装状态')
st['groups']['notify']['localAssignments']=copy.deepcopy(st['groups']['notify']['assignments']);snap('notify-installed','消费者安装自己的分区列表，N3安装空列表')
def request(gid,member,partition):
 assert partition in st['groups'][gid]['localAssignments'][member]
 st['groups'][gid]['requests'].append({'member':member,'partitions':[partition],'startOffsets':{partition:0}})
def receive(gid,member,partition):
 st['groups'][gid]['received'][member]+=copy.deepcopy(next(p for p in parts if p['id']==partition)['records'])
request('notify','N1','P0');snap('notify-fetch-n1','N1从本地列表取P0，形成P0起点0请求')
receive('notify','N1','P0');snap('notify-received-n1','N1按请求取得E01/E03，原日志保留')
request('notify','N2','P1');snap('notify-fetch-n2','N2只形成P1请求')
receive('notify','N2','P1');snap('notify-received-n2','N2收到E02/E04，N3列表空且无分区Fetch')
st['calculation'].update(group='points',inputMembers=['S1'],sortedMembers=['S1'],sortedPartitions=['P0','P1'],base=None,remainder=None,unassigned=['P0','P1'],activeMember=None);st['coordinator'].update(phase='joined',group='points',leader='S1',subscriptions=['S1:orders'],receivedWholeTable=False);snap('points-inputs','另一个group只用自己的S1名单计算')
st['groups']['points']['assignments']=calculated('points');st['groups']['points']['computed']=True;st['calculation'].update(base=2,remainder=0,unassigned=[],activeMember='S1');snap('points-calculated','2除以1，S1得到P0和P1')
st['groups']['points']['syncResponses']=copy.deepcopy(st['groups']['points']['assignments']);st['groups']['points']['localAssignments']=copy.deepcopy(st['groups']['points']['assignments']);snap('points-installed','S1安装两个分区，notify归属不变')
request('points','S1','P0');snap('points-fetch-p0','S1请求P0')
receive('points','S1','P0');snap('points-received-p0','S1独立收到P0两条')
request('points','S1','P1');snap('points-fetch-p1','S1另请求P1')
receive('points','S1','P1');snap('points-received-all','两个group合计各得四条，N3保持空')
checks=0;log_hash=hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest()
for s in timeline:
 assert hashlib.sha256(json.dumps(s['partitions'],sort_keys=True).encode()).hexdigest()==log_hash;checks+=1
 for gid,g in s['groups'].items():
  if g['computed']:
   owned=[p for values in g['assignments'].values() for p in values];assert sorted(owned)==['P0','P1'];checks+=1
  for r in g['requests']:
   assert set(r['partitions'])<=set(g['localAssignments'][r['member']] or []);checks+=1
  for m,events in g['received'].items():
   expected=set(p for r in g['requests'] if r['member']==m for p in r['partitions']);assert all(any(e in p['records'] for p in parts if p['id'] in expected) for e in events);checks+=1
 assert not any(r['member']=='N3' for r in s['groups']['notify']['requests']);checks+=1
assert len(st['groups']['notify']['received']['N1'])==len(st['groups']['notify']['received']['N2'])==2
assert len(st['groups']['points']['received']['S1'])==4;checks+=3
actual=D/'experiment/actual.stdout.txt';cross=[]
if actual.exists():
 rows={}
 for line in actual.read_text().splitlines():
  if line.startswith('ASSIGN\t'):
   _,case,member,values=line.split('\t');rows.setdefault(case,{})[member]=json.loads(values)
 assert rows['notify-shuffled']=={'member-01':[0],'member-02':[1],'member-03':[]}
 assert rows['points-independent']=={'member-s1':[0,1]};checks+=2
 cross=[{'kind':'actual-unmodified-Kafka-class-output','path':'experiment/actual.stdout.txt','sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'scope':'Range assignment and SubscriptionState eligibility, not full Broker/protocol execution'}]
model={'schemaVersion':1,'episode':'kafka-consumer-groups','kind':'finite-teaching-model-not-broker-experiment','commit':'1156b2752aaa28eafc0b4c4d387e63356793268d','conditions':{'group.protocol':'classic','partition.assignment.strategy':'RangeAssignor','group.instance.id':None,'client.rack':None,'subscription':['orders'],'positions':'valid starting offset0; unpaused; no delivery buffer; node available','memberAliases':{'N1':'member-01','N2':'member-02','N3':'member-03','S1':'member-s1'},'leaderChoice':'N1 chosen for this example independently of Range member sorting','retention':'all four records retained throughout'},'partitions':parts,'timeline':timeline,'crossCheckedAgainst':cross}
(D/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');(D/'model-verification.json').write_text(json.dumps({'passed':True,'checks':checks,'snapshots':len(timeline),'crossCheckedAgainst':cross,'scope':'Finite data/ownership/request invariants plus separately produced actual-class output; not Broker execution or teaching-comprehension evidence'},ensure_ascii=False,indent=2)+'\n');print(checks,'finite checks;',len(timeline),'snapshots')
