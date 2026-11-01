#!/usr/bin/env python3
"""Independent read-only checks of actual serialized teaching graphs.
No producer import, Redis execution, RNG replay or performance measurement.
"""
from pathlib import Path
from bisect import bisect_left
from copy import deepcopy
from collections import Counter
from datetime import datetime, timezone
import hashlib,json,traceback
D=Path(__file__).resolve().parent
counts=Counter()
def ok(condition, label):
    counts[label]+=1
    if not condition: raise AssertionError(label)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(nodes, level):
    out=[];current='head';seen={'head'}
    while nodes[current]['forward'][level] is not None:
        dest=nodes[current]['forward'][level]
        assert dest in nodes, ('dangling',current,level,dest)
        assert dest not in seen, ('cycle',dest)
        assert nodes[dest]['height']>level, ('short-tower',dest,level)
        seen.add(dest);out.append(dest);current=dest
    return out
def graph(snapshot,label):
    nodes=snapshot['nodes'];L=nodes['head']['height']
    ok(nodes['head']['value'] is None,label+'/head')
    for identity,node in nodes.items():
        ok(node['id']==identity,label+'/identity')
        ok(len(node['forward'])==node['height'] and 1<=node['height']<=L,label+'/height')
        for level,dest in enumerate(node['forward']):
            ok(dest is None or dest in nodes,label+'/all-forward-resolve')
            if dest is not None:
                ok(nodes[dest]['height']>level,label+'/forward-level-exists')
                ok(identity=='head' or node['value']<nodes[dest]['value'],label+'/edge-strictly-ordered')
    actual=[walk(nodes,l) for l in range(L)]
    ok(snapshot['levels']==actual,label+'/declared-levels-equal-real-traversal')
    ok(snapshot['reachableBottom']==actual[0],label+'/bottom-reachability')
    for level,row in enumerate(actual):
        vals=[nodes[n]['value'] for n in row]
        ok(vals==sorted(vals) and len(set(vals))==len(vals),label+'/sorted-chain')
        if level:ok(set(row)<=set(actual[level-1]),label+'/upper-is-lower-subset')
    return actual
def search(nodes,target):
    cursor='head';events=[];pred=[None]*nodes['head']['height']
    for level in reversed(range(len(pred))):
        while nodes[cursor]['forward'][level] is not None:
            candidate=nodes[cursor]['forward'][level];value=nodes[candidate]['value'];advance=value<target
            events.append(dict(id=len(events)+1,level=level,current=cursor,candidate=candidate,candidateValue=value,target=target,canAdvance=advance,outcome='advance' if advance else 'descend' if level else 'stop',cursorAfter=candidate if advance else cursor))
            if not advance:break
            cursor=candidate
        pred[level]=cursor
    return events,pred,nodes[cursor]['forward'][0]
def main():
    model=json.loads((D/'model.json').read_text());before=model['before'];after=model['after'];values=model['existingValues']
    ok(model['target']==55 and model['levelCount']==2,'teaching-identity')
    ok(values==list(range(10,81,10)),'actual-input-values')
    expected={}
    expected['head']=dict(id='head',value=None,height=2,forward=['n10','n40'])
    for i,v in enumerate(values):
        height=2 if v in (40,70) else 1
        expected['n'+str(v)]=dict(id='n'+str(v),value=v,height=height,forward=[('n'+str(values[i+1])) if i+1<len(values) else None]+(['n70' if v==40 else None] if height==2 else []))
    ok(before['nodes']==expected,'before-independent-node-and-edge-oracle')
    ok('n55' not in before['nodes'],'no-future-node-in-before')
    rows=graph(before,'before');ok(rows==[['n'+str(v) for v in values],['n40','n70']],'before-independent-level-oracle')
    e,p,s=search(before['nodes'],55)
    ok(model['search']['events']==e,'actual-recorded-search-trace')
    ok(p==model['search']['predecessors']==['n50','n40'],'independent-predecessors')
    ok(s==model['search']['successor']=='n60','independent-successor')
    ok(len(e)==model['search']['comparisonCount']==4,'four-logical-candidate-comparisons')
    ok([x['candidateValue'] for x in e]==[40,70,50,60],'actual-candidate-sequence')
    ok(e[1]['cursorAfter']=='n40' and e[1]['outcome']=='descend','overshoot-does-not-move-into70')
    linear=[];cursor='head'
    for candidate in rows[0]:
        v=before['nodes'][candidate]['value'];advance=v<55
        linear.append(dict(current=cursor,candidate=candidate,candidateValue=v,canAdvance=advance,outcome='advance' if advance else 'stop',cursorAfter=candidate if advance else cursor))
        if not advance:break
        cursor=candidate
    ok(model['linearSearch']['events']==linear,'actual-linear-trace')
    ok(model['linearSearch']['comparisonCount']==len(linear)==6,'six-linear-candidate-comparisons-only-example')
    state=deepcopy(before['nodes']);state['n55']=dict(id='n55',value=55,height=2,forward=[None,None])
    allocated=model['insertion']['allocated'];ok(allocated['nodes']==state,'allocated-unlinked-node')
    graph(allocated,'allocated')
    specs=[(0,'n55',None,'n60'),(0,'n50','n60','n55'),(1,'n55',None,'n70'),(1,'n40','n70','n55')]
    reaches=[]
    for i,(level,owner,old,new) in enumerate(specs):
        write=model['insertion']['pointerWrites'][i]
        ok((write['level'],write['owner'],write['oldTarget'],write['newTarget'])==(level,owner,old,new),'pointer-write-order-and-target')
        ok(state[owner]['forward'][level]==old,'old-pointer-actually-retained-until-write')
        previous=deepcopy(state);state[owner]['forward'][level]=new
        ok(write['snapshot']['nodes']==state,'actual-snapshot-equals-one-pointer-mutation')
        differences=[(n,l) for n in state for l,v in enumerate(state[n]['forward']) if v!=previous[n]['forward'][l]]
        ok(differences==[(owner,level)],'exactly-one-pointer-changes')
        actual=graph(write['snapshot'],'write'+str(i+1));reaches.append(['n55' in row for row in actual])
    ok(reaches==[[False,False],[True,False],[True,False],[True,True]],'partial-insertion-reachability-phases')
    ok(model['insertion']['completeOnlyAfterWrite']==4,'insertion-completes-only-after-both-levels')
    ok(after['nodes']==state,'final-actual-nodes-match-four-writes')
    graph(after,'after')
    ok(after==model['insertion']['pointerWrites'][-1]['snapshot'],'final-snapshot-retained')
    ok(before['nodes']==expected,'before-still-pristine-after-all-checks')
    queries=0
    for name,ss in [('before',before),('after',after)]:
        ns=ss['nodes'];levels=[walk(ns,l) for l in range(ns['head']['height'])]
        for target in range(-10,101):
            trace,pred,succ=search(ns,target);queries+=1
            for level,row in enumerate(levels):
                vals=[ns[n]['value'] for n in row];idx=bisect_left(vals,target)
                expected_pred='head' if idx==0 else row[idx-1]
                ok(pred[level]==expected_pred,'all-query-predecessor-agrees-with-bisect')
            basevals=[ns[n]['value'] for n in levels[0]];idx=bisect_left(basevals,target)
            ok(succ==(levels[0][idx] if idx<len(levels[0]) else None),'all-query-successor-agrees-with-bisect')
            for row in trace:
                ok(row['candidate']==ns[row['current']]['forward'][row['level']],'all-query-follows-real-forward-edge')
                ok(row['canAdvance']==(row['candidateValue']<target),'all-query-comparison-correct')
                ok(row['cursorAfter']==(row['candidate'] if row['canAdvance'] else row['current']),'all-query-cursor-does-not-overshoot')
    slow,_,_=search(before['nodes'],5)
    ok(len(slow)==2,'guard-two-layer-can-cost-more-than-linear-one')
    bad=deepcopy(before['nodes']);bad['n40']['forward'][1]='n55'
    try:walk(bad,1)
    except AssertionError:ok(True,'checker-rejects-observed-candidate-future-pointer-bug')
    else:ok(False,'checker-rejects-observed-candidate-future-pointer-bug')
    bad=deepcopy(before['nodes']);bad['n80']['forward'][0]='n10'
    try:walk(bad,0)
    except AssertionError:ok(True,'checker-rejects-cycle')
    else:ok(False,'checker-rejects-cycle')
    report=dict(status='passed',checkedAtUTC=datetime.now(timezone.utc).isoformat(),scope='Independent actual serialized graph/trace/snapshot verification; no producer import, Redis run, RNG replay or performance experiment.',inputs={n:sha(D/n) for n in ['model.json','build_model.py']},assertionsExecuted=sum(counts.values()),assertionsByCategory=dict(counts),actualSnapshotsChecked=7,actualGraphQueriesChecked=queries,teachingCase={'searchCandidates':[40,70,50,60],'predecessors':['n50','n40'],'successor':'n60','pointerWrites':specs,'partialReachability':reaches,'beforePristine':True},guardCounterexample={'target':5,'linearCandidateComparisons':1,'twoLevelCandidateComparisons':2,'meaning':'Extra levels do not improve every individual lookup.'},limits=['Values in this teaching model are distinct; full Redis score/member byte order is reviewed against fixed C source separately.','222 bounded integer queries validate these two actual graphs, not all possible skiplist implementations.','Raw candidate prior11269 checks are not reused as independent evidence.'])
    (D/'qa-model.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (D/'qa-model.md').write_text(f"# 跳表独立模型复核\n\n通过：实际执行{sum(counts.values()):,}项断言，直接核验新正式model的7个序列化状态和222个真实图查询。没有导入制作builder或临时候选算法。\n\n实际forward逐层遍历与声明levels一致；初始40上层指70、50底层指60且无55，避免候选浅拷贝污染。查55的候选40→70→50→60、前驱底50/上40、后继60成立。四次写入每次恰好一个指针改变；55在第二写才从底层起点可达，第四写才两层可达，其他链接与初始快照保持。\n\n固定图的全部整数目标−10至100由独立bisect oracle验证前驱与后继。目标5需跳表2次、链表1次，证明不能声称每次更快。此为教学模型检查，不是Redis产品实验、随机层高回放或概率/性能测量；未复用候选11269通过数字。\n")
    print(json.dumps({'status':'passed','assertions':sum(counts.values()),'queries':queries}))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        (D/'qa-model.json').write_text(json.dumps({'status':'failed','error':repr(exc),'traceback':traceback.format_exc(),'assertionsExecuted':sum(counts.values())},ensure_ascii=False,indent=2)+'\n');raise
