#!/usr/bin/env python3
"""Deterministic forward-link teaching model; not a Redis RNG/product replay."""
from copy import deepcopy
import json
from pathlib import Path

D=Path(__file__).resolve().parent
VALUES=[10,20,30,40,50,60,70,80]
HEIGHTS={v:2 if v in (40,70) else 1 for v in VALUES}
HEAD='head'
def nid(v): return f'n{v}'
def snapshot(nodes):
    state=deepcopy(nodes); layers=[]
    for level in range(2):
        cursor=HEAD; seen={HEAD}; ids=[]
        while state[cursor]['forward'][level] is not None:
            cursor=state[cursor]['forward'][level]
            assert cursor in state and cursor not in seen
            seen.add(cursor); assert state[cursor]['height']>level
            ids.append(cursor)
        assert [state[k]['value'] for k in ids]==sorted(state[k]['value'] for k in ids)
        layers.append(ids)
    return {'nodes':state,'levels':layers,'reachableBottom':layers[0]}

def build():
    nodes={HEAD:{'id':HEAD,'value':None,'height':2,'forward':[None,None]}}
    nodes.update({nid(v):{'id':nid(v),'value':v,'height':HEIGHTS[v],'forward':[None]*HEIGHTS[v]} for v in VALUES})
    for level in range(2):
        ids=[HEAD]+[nid(v) for v in VALUES if HEIGHTS[v]>level]
        for a,b in zip(ids,ids[1:]):nodes[a]['forward'][level]=b
    before=snapshot(nodes)
    target=55; current=HEAD; comparisons=[]; pred=[None,None]
    for level in (1,0):
        while True:
            nxt=nodes[current]['forward'][level]
            if nxt is None: raise AssertionError('This teaching trace should stop before null')
            advance=nodes[nxt]['value']<target
            event={'id':len(comparisons)+1,'level':level,'current':current,'candidate':nxt,'candidateValue':nodes[nxt]['value'],'target':target,'canAdvance':advance,'outcome':'advance' if advance else 'descend' if level else 'stop','cursorAfter':nxt if advance else current}
            comparisons.append(event)
            if advance:current=nxt
            else:pred[level]=current;break
    linear=[]; c=HEAD
    while True:
        n=nodes[c]['forward'][0];yes=nodes[n]['value']<target
        linear.append({'current':c,'candidate':n,'candidateValue':nodes[n]['value'],'canAdvance':yes,'outcome':'advance' if yes else 'stop','cursorAfter':n if yes else c})
        if not yes:break
        c=n
    assert pred==['n50','n40']
    nodes['n55']={'id':'n55','value':55,'height':2,'forward':[None,None]}
    allocated=snapshot(nodes)
    writes=[]
    for level in (0,1):
        old=nodes[pred[level]]['forward'][level]
        for owner,new,role in [('n55',old,'new-node-successor'),(pred[level],'n55','predecessor-splice')]:
            prior=nodes[owner]['forward'][level];nodes[owner]['forward'][level]=new
            writes.append({'id':len(writes)+1,'level':level,'owner':owner,'oldTarget':prior,'newTarget':new,'role':role,'snapshot':snapshot(nodes)})
    after=snapshot(nodes)
    assert 'n55' not in before['nodes'] and before['nodes']['n40']['forward'][1]=='n70'
    assert before['nodes']['n50']['forward'][0]=='n60'
    assert after['levels']==[[nid(v) for v in [10,20,30,40,50,55,60,70,80]],['n40','n55','n70']]
    assert before['levels']==[[nid(v) for v in VALUES],['n40','n70']]
    return {'schemaVersion':1,'kind':'deterministic-forward-link-skiplist-teaching-model','scope':'Two-level example of search and insertion in a skiplist-encoded structure. Fixed legal heights; not a Redis RNG replay or default eight-member ZSET memory dump. Distinct scores simplify the full score/member ordering. Spans, backward links and dictionary are outside this forward-link visual model.','head':HEAD,'target':55,'levelCount':2,'levelNames':['有序底层','稀疏上层'],'existingValues':VALUES,'fixedHeights':{nid(v):HEIGHTS[v] for v in VALUES},'newNode':{'id':'n55','value':55,'height':2,'heightSelection':'Fixed legal teaching height, not a claimed observed random draw.'},'before':before,'linearSearch':{'events':linear,'comparisonCount':len(linear),'predecessor':'n50','successor':'n60'},'search':{'events':comparisons,'comparisonCount':len(comparisons),'predecessors':pred,'successor':'n60'},'insertion':{'allocated':allocated,'pointerWrites':writes,'order':'For each level bottom-up: set new node successor, then splice predecessor.','completeOnlyAfterWrite':4},'after':after,'limits':['Only this example compares6 linked-list candidates with4 skiplist candidates; no production performance claim.','Extra sparse levels and randomized heights support expected efficiency; fixed two levels do not guarantee logarithmic or per-query improvement.','Redis small sorted sets may use listpack; this is a skiplist-encoding demonstration.','The full Redis structure includes additional bookkeeping not represented here.']}

if __name__=='__main__':
    result=build();encoded=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    assert encoded==json.dumps(build(),ensure_ascii=False,indent=2)+'\n'
    (D/'model.json').write_text(encoded)
    print('Deterministic model written; before/after and every pointer-write snapshot traversed without mutation/cycles/dangling links.')
