"""Execute the sole solution; independent graph BFS oracle and observed DSU trace."""
from pathlib import Path
import ast, hashlib, importlib.util, inspect, itertools, json, random, sys
EP = Path(__file__).resolve().parents[1]
SOURCE = EP / 'solution.py'
spec = importlib.util.spec_from_file_location('province_solution', SOURCE)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
Solution = module.Solution
SHA = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
def save(name, data):
    path = EP / name; path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n');temporary.replace(path)
def matrix(n, edges):
    result = [[int(a == b) for b in range(n)] for a in range(n)]
    for a, b in edges: result[a][b] = result[b][a] = 1
    return result
def oracle(data):
    seen, result = set(), 0
    for start in range(len(data)):
        if start in seen: continue
        result += 1; queue = [start]; seen.add(start)
        for a in queue:
            for b, connected in enumerate(data[a]):
                if connected and b not in seen:
                    seen.add(b); queue.append(b)
    return result
LINES = {text.strip(): index for index, text in enumerate(SOURCE.read_text().splitlines(), 1)}
SPECIAL = {key: LINES[key] for key in [
    'for a in range(n):','if isConnected[a][b] == 0:',
    'if ra == rb:','if size[ra] < size[rb]:',
    'parent[rb] = ra','size[ra] += size[rb]','count -= 1',
    'while parent[city] != city:', 'parent[city] = parent[parent[city]]',
    'city = parent[city]', 'return city', 'return count']}
def traced(data):
    events, finds = [], {}
    initialized = False
    last_link, pending_decrement = None, False
    def emit(kind, line, outer, **extra):
        a, b = outer.get('a'), outer.get('b')
        row = dict(id=len(events), type=kind, sourceLine=line, a=a, b=b,
            pair=[a,b] if a is not None and b is not None else None,
            parent=list(outer.get('parent', [])), size=list(outer.get('size', [])), count=outer.get('count'))
        if row['parent']:
            roots = []
            for start in range(len(row['parent'])):
                current = start; seen = set()
                while row['parent'][current] != current:
                    assert current not in seen; seen.add(current); current = row['parent'][current]
                roots.append(current)
            row['groupRoots'] = roots
            row['groups'] = [[city for city, root in enumerate(roots) if root == representative] for representative in sorted(set(roots))]
        row.update(extra); events.append(row)
        return row
    def watch(frame, event, arg):
        nonlocal initialized, last_link, pending_decrement
        if Path(frame.f_code.co_filename).resolve() != SOURCE.resolve(): return watch
        line, loc = frame.f_lineno, frame.f_locals
        if frame.f_code.co_name == 'findCircleNum':
            if event == 'line':
                if pending_decrement:
                    emit('decrement', line, loc, roots=[loc['ra'],loc['rb']],effectLine=SPECIAL['count -= 1']); pending_decrement=False
                if line == SPECIAL['for a in range(n):'] and not initialized:
                    emit('init', line, loc); initialized=True
                elif line == SPECIAL['if isConnected[a][b] == 0:']:
                    emit('inspect', line, loc, connected=data[loc['a']][loc['b']])
                elif line == SPECIAL['if ra == rb:']:
                    emit('roots', line, loc, roots=[loc['ra'],loc['rb']])
                elif line == SPECIAL['if ra == rb:']+1:
                    emit('already-connected', line, loc, roots=[loc['ra'],loc['rb']],effectLine=SPECIAL['if ra == rb:'])
                elif line == SPECIAL['if size[ra] < size[rb]:']:
                    emit('size-compare', line, loc, roots=[loc['ra'],loc['rb']], rootSizes=[loc['size'][loc['ra']],loc['size'][loc['rb']]])
                elif line == SPECIAL['parent[rb] = ra']:
                    last_link = list(loc['parent'])
                elif line == SPECIAL['size[ra] += size[rb]']:
                    emit('link', line, loc, roots=[loc['ra'],loc['rb']], mergedRoots=[loc['ra'],loc['rb']], parentBefore=last_link,effectLine=SPECIAL['parent[rb] = ra'])
                elif line == SPECIAL['count -= 1']:
                    emit('resize', line, loc, roots=[loc['ra'],loc['rb']],effectLine=SPECIAL['size[ra] += size[rb]']); pending_decrement=True
            elif event == 'return': emit('finish', line, loc, result=arg, pair=None, a=None, b=None)
        elif frame.f_code.co_name == 'find':
            outer = frame.f_back.f_locals
            if event == 'call':
                city = loc['city']; finds[id(frame)] = {'start':city,'path':[],'parentBefore':None}
                emit('find-start',line,outer,city=city,findSide='a' if city==outer['a'] else 'b',path=[city])
            state = finds.get(id(frame))
            if state:
                side = 'a' if state['start']==outer['a'] else 'b'
                if event == 'line' and line == SPECIAL['while parent[city] != city:']:
                    if not state['path'] or state['path'][-1]!=loc['city']:state['path'].append(loc['city'])
                    emit('find-check',line,outer,city=loc['city'],findSide=side,path=list(state['path']))
                elif event == 'line' and line == SPECIAL['parent[city] = parent[parent[city]]']:
                    state['parentBefore'] = list(loc['parent'])
                elif event == 'line' and line == SPECIAL['city = parent[city]']:
                    before = state['parentBefore']; after = list(loc['parent'])
                    emit('compress',line,outer,city=loc['city'],findSide=side,path=list(state['path']),parentBefore=before,changed=before!=after,effectLine=SPECIAL['parent[city] = parent[parent[city]]'])
                elif event == 'return':
                    emit('find-root',line,outer,city=state['start'],root=arg,findSide=side,path=list(state['path']))
                    finds.pop(id(frame),None)
        return watch
    previous = sys.gettrace()
    try:
        sys.settrace(watch); result = Solution().findCircleNum(data)
    finally: sys.settrace(previous)
    return result, events

def run():
    tested = 0
    for n in range(1,6):
        edges = list(itertools.combinations(range(n),2))
        for mask in range(1<<len(edges)):
            data=matrix(n,[edge for bit,edge in enumerate(edges) if mask>>bit&1])
            original=json.loads(json.dumps(data)); actual=Solution().findCircleNum(data)
            assert actual==oracle(data) and data==original;tested+=1
    rng=random.Random(547)
    for _ in range(3000):
        n=rng.randint(1,30); probability=rng.random()
        data=matrix(n,[pair for pair in itertools.combinations(range(n),2) if rng.random()<probability])
        assert Solution().findCircleNum(data)==oracle(data)
    for data in [matrix(200,[]),matrix(200,list(itertools.combinations(range(200),2))),matrix(200,[(i,i+1) for i in range(199)])]:
        assert Solution().findCircleNum(data)==oracle(data)
    cases={}
    descriptions={
        'main':(6,[(0,1),(1,2),(3,4)],3),
        'extraCycle':(6,[(0,1),(1,2),(3,4),(0,2)],3),
        'compressionCheck':(6,[(0,5),(1,2),(2,5),(3,5)],2),
    }
    for name,(n,edges,expected) in descriptions.items():
        data=matrix(n,edges);actual,events=traced(data);assert actual==expected==oracle(data)
        inspect_events=[e for e in events if e['type']=='inspect'];assert len(inspect_events)==n*(n-1)//2
        assert all(e['a']<e['b'] for e in inspect_events)
        assert len([e for e in events if e['type']=='decrement'])==n-expected
        if name=='extraCycle':assert any(e['type']=='already-connected' and e['pair']==[1,2] for e in events)
        if name=='compressionCheck':assert any(e['type']=='compress' and e['changed'] for e in events)
        cases[name]=dict(cityLabels=[chr(65+i) for i in range(n)],inputMatrix=data,edges=[list(e) for e in edges],actual=actual,expected=expected,events=events)
    save('solution.json',dict(language='python',source='solution.py',sourceSha256=SHA,lines=SOURCE.read_text().splitlines()))
    save('research/trace.json',dict(schemaVersion=1,source='solution.py',sourceSha256=SHA,method='Python sys.settrace observes actual executed lines, locals and return values; no observer or second solver in solution.',eventTiming='Line events occur before sourceLine executes. link/resize/decrement snapshots describe completed prior assignments; sourceLine identifies the observation location.',cases=cases))
    report=dict(status='passed',sourceSha256=SHA,exhaustiveGraphs=tested,exhaustiveMaxCities=5,deterministicRandomGraphs=3000,randomSeed=547,maxConstraintCases=3,maxCities=200,oracle='Independent BFS on the input relation matrix; matrix immutability checked exhaustively.',mainResult=cases['main']['actual'],cycleResult=cases['extraCycle']['actual'],compressionResult=cases['compressionCheck']['actual'],observedCompressionChanged=True,traceEvents={k:len(v['events']) for k,v in cases.items()})
    save('research/algorithm-check.json',report);print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':run()
