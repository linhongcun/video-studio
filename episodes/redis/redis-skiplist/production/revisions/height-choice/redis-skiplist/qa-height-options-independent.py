#!/usr/bin/env python3
"""Independent height1/height2 legal teaching branches; no producer import.

Audits the formal height-options JSON against independently constructed states
and a separate actual-forward traversal oracle; imports no production builder.
"""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from collections import Counter
from bisect import bisect_left
import hashlib,json,re
D=Path(__file__).resolve().parent
OUT=D/'qa-height-options-independent.json'
checks=Counter()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,name):
    checks[name]+=1
    if not value:raise AssertionError(name)
def canonical(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
model=json.loads((D/'model.json').read_text())
before=deepcopy(model['before']);before_hash=canonical(before)
base=['n10','n20','n30','n40','n50','n60','n70','n80']
inserted_base=['n10','n20','n30','n40','n50','n55','n60','n70','n80']
upper=['n40','n70']
def cache_snapshot(nodes):
    levels=[]
    for level in [0,1]:
        out=[];node='head';guard=set()
        while nodes[node]['forward'][level] is not None:
            node=nodes[node]['forward'][level]
            if node in guard:raise RuntimeError('Cycle in builder')
            guard.add(node);out.append(node)
        levels.append(out)
    return {'nodes':deepcopy(nodes),'levels':levels,'reachableBottom':list(levels[0])}
def construct(height):
    nodes=deepcopy(before['nodes'])
    nodes['n55']={'id':'n55','value':55,'height':height,'forward':[None]*height}
    allocated=cache_snapshot(nodes);writes=[]
    # Fixed predecessors are independently known from the same original chain.
    for level,pred in enumerate(['n50','n40'][:height]):
        successor=nodes[pred]['forward'][level]
        for owner,target,role in [('n55',successor,'new-node-successor'),(pred,'n55','predecessor-splice')]:
            old=nodes[owner]['forward'][level]
            nodes[owner]['forward'][level]=target
            writes.append({'level':level,'owner':owner,'oldTarget':old,'newTarget':target,'role':role,'snapshot':cache_snapshot(nodes)})
    return {'selectedHeightBeforeAnyPointerWrite':height,'before':deepcopy(before),'allocated':allocated,'pointerWrites':writes,'after':cache_snapshot(nodes),'completeOnlyAfterWrite':2*height,'heightSelectionScope':'Legal fixed counterexample, not an observed Redis random draw.'}
branches={str(h):construct(h) for h in [1,2]}
def oracle_snapshot(state,expected_height,expected_levels):
    nodes=state['nodes'];actual=[]
    for node_id,node in nodes.items():
        require(node['id']==node_id,'actual-node-identity')
        require(len(node['forward'])==node['height'],'exact-allocated-port-count')
        for level,target in enumerate(node['forward']):
            if target is not None:
                require(target in nodes,'forward-target-exists')
                require(nodes[target]['height']>level,'target-has-corresponding-port')
                require(node_id=='head' or nodes[target]['value']>node['value'],'actual-forward-values-ordered')
    for level in [0,1]:
        seen={'head'};chain=[];current='head'
        while True:
            target=nodes[current]['forward'][level]
            if target is None:break
            require(target not in seen,'actual-forward-chain-acyclic')
            seen.add(target);chain.append(target);current=target
        actual.append(chain)
    require(actual==expected_levels,'actual-level-chains-equal-independent-explicit-sequences')
    require(state['levels']==actual and state['reachableBottom']==actual[0],'serialized-caches-equal-actual-forward-graph')
    if 'n55' in nodes:
        require(nodes['n55']['height']==expected_height,'selected-height-never-changes-during-insertion')
        require(list(range(nodes['n55']['height']))==list(range(expected_height)),'logical-55-port-set-is-fixed-at-allocation')
    return actual
oracle_snapshot(before,None,[base,upper])
for h in [1,2]:
    branch=branches[str(h)]
    require(branch['before']==before,'both-branches-start-from-the-identical-before')
    oracle_snapshot(branch['allocated'],h,[base,upper])
    previous=branch['allocated']
    for i,write in enumerate(branch['pointerWrites'],1):
        state=write['snapshot'];expected=[inserted_base if i>=2 else base, ['n40','n55','n70'] if h==2 and i>=4 else upper]
        chains=oracle_snapshot(state,h,expected)
        changes=[]
        for identity,node in previous['nodes'].items():
            require(node['height']==state['nodes'][identity]['height'],'no-temporary-height-upgrade')
            for level,target in enumerate(node['forward']):
                if state['nodes'][identity]['forward'][level]!=target:changes.append((identity,level,target,state['nodes'][identity]['forward'][level]))
        require(changes==[(write['owner'],write['level'],write['oldTarget'],write['newTarget'])],'exactly-one-declared-forward-pointer-mutates-per-write')
        require(('n55' in chains[0])==(i>=2),'base-reachability-starts-only-after-predecessor-splice')
        require(('n55' in chains[1])==(h==2 and i>=4),'upper-reachability-conditional-on-preselected-height2-and-write4')
        previous=state
    oracle_snapshot(branch['after'],h,[inserted_base,['n40','n55','n70'] if h==2 else upper])
    require(branch['completeOnlyAfterWrite']==len(branch['pointerWrites'])==2*h,'complete-after-only-the-selected-level-count-writes')
    require(branch['allocated']['nodes']['n50']['forward'][0]=='n60' and branch['allocated']['nodes']['n40']['forward'][1]=='n70','allocated-snapshot-has-no-future-predecessor-write-leak')
require(branches['1']['after']['nodes']['n55']['forward']==['n60'],'height1-new55-has-base-successor-only')
require(branches['1']['after']['nodes']['n40']['forward'][1]=='n70','height1-upper40-still-points-directly-to70')
require(all(w['level']==0 for w in branches['1']['pointerWrites']),'height1-has-no-upper-write')
require(branches['2']['after']==model['after'],'independent-height2-after-matches-current-formal-model')
for a,b in zip(branches['2']['pointerWrites'],model['insertion']['pointerWrites']):require(a['snapshot']==b['snapshot'],'independent-height2-write-snapshots-match-current-formal-model')
require(branches['2']['pointerWrites'][1]['snapshot']['nodes']['n55']['height']==2,'height2-bottom-completion-already-has-selected-upper-slot')
require(branches['1']['after']!=branches['2']['pointerWrites'][1]['snapshot'],'height1-complete-is-not-height2-mid-operation')
def strict_neighbors(state,target):
    nodes=state['nodes'];current='head';comparisons=0
    for level in [1,0]:
        while nodes[current]['forward'][level] is not None:
            candidate=nodes[current]['forward'][level];comparisons+=1
            if nodes[candidate]['value']<target:current=candidate
            else:break
    nxt=nodes[current]['forward'][0]
    return (None if current=='head' else nodes[current]['value'],None if nxt is None else nodes[nxt]['value'],comparisons)
formal=json.loads((D/'height-options.json').read_text())
require(formal['baseModelSHA256']==sha(D/'model.json'),'formal-height-options-binds-base-model-bytes')
require(formal['sameBeforeForBothCases']==before,'formal-cases-share-exact-original-before')
require(formal['levelCountOfWholeSkiplist']==2,'whole-skiplist-still-has-two-levels')
require(formal['forwardLinksOnly'] is True and formal['hiddenRedisSpanUpdatesAreNotClaimedUnchanged'] is True,'formal-forward-only-scope-does-not-misclaim-span-preservation')
require('not a Redis RNG replay' in formal['heightSelection'],'formal-fixed-choice-is-not-an-observed-random-draw')
formal_serialized_states=1
oracle_snapshot(formal['sameBeforeForBothCases'],None,[base,upper])
for h in [1,2]:
    actual=formal['cases']['height'+str(h)];independent=branches[str(h)]
    require(actual['selectedHeightBeforeWiring']==h,'formal-selected-height-before-any-wiring')
    require(actual['completeAfterWrites']==2*h and len(actual['pointerWrites'])==2*h,'formal-completion-depends-on-selected-height')
    oracle_snapshot(actual['allocated'],h,[base,upper]);formal_serialized_states+=1
    require(actual['allocated']==independent['allocated'],'formal-allocation-equals-independent-construction')
    for i,(actual_write,independent_write) in enumerate(zip(actual['pointerWrites'],independent['pointerWrites']),1):
        require(all(actual_write[k]==independent_write[k] for k in ['owner','level','oldTarget','newTarget']),'formal-write-order-and-targets-equal-independent-source-order')
        require(actual_write['role']==('new-successor' if i%2 else 'predecessor-link'),'formal-write-role-matches-forward-pointer-action')
        expected=[inserted_base if i>=2 else base,['n40','n55','n70'] if h==2 and i>=4 else upper]
        oracle_snapshot(actual_write['snapshot'],h,expected);formal_serialized_states+=1
        require(actual_write['snapshot']==independent_write['snapshot'],'formal-per-write-snapshot-equals-independent-one-write-state')
    oracle_snapshot(actual['after'],h,[inserted_base,['n40','n55','n70'] if h==2 else upper]);formal_serialized_states+=1
    require(actual['after']==independent['after'],'formal-after-equals-independent-complete-branch')
query_states={'before':formal['sameBeforeForBothCases'],'height1Complete':formal['cases']['height1']['after'],'height2Complete':formal['cases']['height2']['after']}
query_count=0
for name,state in query_states.items():
    expected_values=sorted(n['value'] for k,n in state['nodes'].items() if k!='head')
    for target in range(-10,101):
        i=bisect_left(expected_values,target);expected=(expected_values[i-1] if i else None,expected_values[i] if i<len(expected_values) else None)
        actual=strict_neighbors(state,target)
        require(actual[:2]==expected,'actual-graph-strict-score-neighbors-equal-independent-bisect-oracle');query_count+=1
require(strict_neighbors(before,55)[:2]==(50,60),'same-query-still-locates50and60')
require(canonical(before)==before_hash and model['before']==before,'original-before-not-mutated')
source=D/'research/sources/t_zset.c';text=source.read_text()
require(sha(source)=='216e757ebd39efcf1d53ff6c576d8a850c6382104be39d4195f1050543e48e0b','official-fixed-source-bytes-preserved')
needles=['int level = 1;','level = zslRandomLevel();','x = zslCreateNode(zsl,level,score,ele);','for (i = 0; i < level; i++) {','x->level[i].forward = update[i]->level[i].forward;','update[i]->level[i].forward = x;','for (i = level; i < zsl->level; i++) {','update[i]->level[i].span++;']
line_evidence=[]
for needle in needles:
    require(needle in text,'fixed-source-required-fact-present')
    line_evidence.append({'exactText':needle,'line':text[:text.index(needle)].count('\n')+1})
start=text.index('zskiplistNode *zslInsert(')
require(text.index('level = zslRandomLevel();',start)<text.index('x = zslCreateNode(zsl,level,score,ele);',start)<text.index('for (i = 0; i < level; i++) {',start),'source-selects-height-before-allocation-and-forward-writes')
report={'status':'passed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Formal actual serialized height-options audited against independent height1/height2 constructions, explicit no-upgrade snapshots and333 actual-graph neighbor queries; no production builder import.','inputModelSHA256':sha(D/'model.json'),'formalHeightOptionsSHA256':sha(D/'height-options.json'),'producerBuilderSHA256':sha(D/'build_height_options.py'),'checkerSHA256':sha(__file__),'actualFormalSerializedStatesAudited':formal_serialized_states,'inputBeforeCanonicalSHA256':before_hash,'officialSourceSHA256':sha(source),'officialSourceURL':'https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/t_zset.c','officialSourceLineEvidence':line_evidence,'branches':branches,'assertionsExecuted':sum(checks.values()),'assertionsByCategory':dict(checks),'actualGraphNeighborQueries':query_count,'facts':['Both branches start from one unchanged before; layer count is selected before allocation and pointer writes.','If selectedheight1, new55 has only a base port and exactly2 forward-pointer writes; the completed upper chain remains head→40→70.','If selectedheight2, new55 already has2 slots while allocated; after the2 base writes its upper slot still exists and the insertion is in progress until the2 upper writes.','In this forward-only drawing, upper forward links stay unchanged forheight1. RealRedis still adjusts spans on untouched levels and backward/length metadata; those fields are outside this drawing.'],'proposedVisualContract':['Display height1 as a complete legal alternative with no55 upper port, then explicitly return to the same before if switching branches.','For the mainheight2 branch, declare the preselected2 before showing any pointer write and keep both55 ports present thereafter.','Do not take the completedheight1 graph and animate an upper slot growing onto55 as if a late optional upgrade.'],'notClaimed':['No actualRedis execution or RNG draw replay.','Model/source audit only; exact-script TTS approval is recorded separately.','No rendering, freezing, TTS, publication or writing into any old episode directory.']}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(D/'qa-height-options-independent.md').write_text('正式height-options实际独立审查通过：从同一before深拷贝验证height1与height2两分支。height1完成态：底层50→55→60，上层head→40→70；55只有底层端口，2写即完成。height2在分配前已选2，分配时就有两个端口；底层2写后仍未完成，随后上层2写。不能把已完成的一层节点演成临时升级为两层。\n\nRedis固定源码先zslRandomLevel，再zslCreateNode(level)，只在i<level内写forward。height1不会写上层forward，但实际Redis还会增加未触碰上层的span，所以片中应精确说上层链接保持，不能说上层所有字段都不变。\n\n实际执行独立图验证、逐写无泄漏/高度恒定检查，以及333次严格分数邻接查询oracle；当前height2四快照也与正式模型一致。正式11个序列化快照均按实际forward独立核对，333查询直接使用正式JSON的before/两after。模型报告本身不授权TTS；脚本审批另行绑定fullSHA。没有改旧目录。\n')
print(json.dumps({'status':report['status'],'assertions':report['assertionsExecuted'],'queries':query_count,'output':str(OUT),'sha256':sha(OUT)}))
