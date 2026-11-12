"""Classic logical heap swaps; each operation result is checked against heapq.

The frames illustrate valid abstract heap operations, not CPython's temporary
hole assignments. Tuple order is (frequency, number); ties use number.
"""
from collections import Counter
from pathlib import Path
import heapq,json
P=Path(__file__).resolve().parent
nums=[1,1,1,2,2,3,4,4,4,4,5,5,5,5,5,6];k=3
heap=[];oracle=[];events=[];operations=[]
def emit(kind,before=None,**kw):
    row=dict(id=len(events),kind=kind,before=[list(x) for x in (heap if before is None else before)],heap=[list(x) for x in heap],**kw)
    events.append(row);return row['id']
def push(item):
    start=len(events);before=heap[:];heap.append(item);emit('append',before,indices=[len(heap)-1],candidate=item[1])
    child=len(heap)-1
    while child:
        parent=(child-1)//2;emit('compare-up',indices=[parent,child],candidate=item[1])
        if heap[parent]<=heap[child]:break
        before=heap[:];heap[parent],heap[child]=heap[child],heap[parent];emit('swap-up',before,indices=[parent,child],candidate=item[1]);child=parent
    heapq.heappush(oracle,item);assert heap==oracle,(heap,oracle)
    emit('push-done',candidate=item[1]);operations.append(dict(kind='push',num=item[1],start=start,end=len(events)-1))
def pop():
    start=len(events);removed=heap[0];before=heap[:];last=heap.pop();emit('remove-root',before,removed=list(removed),replacement=list(last),indices=[0])
    if heap:
        before=heap[:];heap[0]=last;emit('replace-root',before,removed=list(removed),replacement=list(last),indices=[0])
        parent=0
        while parent*2+1<len(heap):
            left=2*parent+1;right=left+1;child=right if right<len(heap) and heap[right]<heap[left] else left
            emit('compare-children',indices=[i for i in (left,right) if i<len(heap)],chosen=child)
            emit('compare-down',indices=[parent,child],chosen=child)
            if heap[parent]<=heap[child]:break
            before=heap[:];heap[parent],heap[child]=heap[child],heap[parent];emit('swap-down',before,indices=[parent,child]);parent=child
    assert removed==heapq.heappop(oracle);assert heap==oracle,(heap,oracle)
    emit('pop-done',removed=list(removed));operations.append(dict(kind='pop',num=removed[1],start=start,end=len(events)-1))
emit('init')
for num,cnt in Counter(nums).items():
    push((cnt,num))
    if len(heap)>k:pop()
assert set(num for cnt,num in heap)=={1,4,5}
# Independent randomized check of the complete public solution.
import importlib.util,random
solution=P.parent/'solution.py'
if solution.exists():
    spec=importlib.util.spec_from_file_location('topk',solution);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    rng=random.Random(347)
    for _ in range(500):
        a=[rng.randrange(-10,11) for i in range(rng.randrange(1,80))];c=Counter(a);kk=rng.randint(1,len(c));actual=mod.Solution().topKFrequent(a,kk)
        assert len(actual)==kk and len(set(actual))==kk
        assert min(c[x] for x in actual)>=max((c[x] for x in c if x not in actual),default=0)
out=dict(sample=nums,k=k,counts=[dict(num=num,cnt=cnt) for num,cnt in Counter(nums).items()],tupleOrder=['frequency','number'],semantics='Classic logical swaps, not CPython temporary hole assignments; completed operations exactly match heapq.',events=events,operations=operations,finalHeap=[list(x) for x in heap],result=[num for cnt,num in heap])
(P/'trace.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(f'{len(events)} logical states; {len(operations)} exact heapq operation results checked; final {heap}')
