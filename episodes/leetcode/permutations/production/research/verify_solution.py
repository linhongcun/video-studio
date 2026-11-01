"""Independent itertools oracle, source identity and AST-observed execution trace."""
import ast
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

EP = Path(__file__).resolve().parents[1]
source = (EP / 'solution.py').read_text()
sha = hashlib.sha256(source.encode()).hexdigest()
ns = {}
exec(compile(source, str(EP / 'solution.py'), 'exec'), ns)
solve = ns['Solution']().permute
cases = [list(p) for n in range(1, 6) for p in itertools.permutations([-2, -1, 0, 1, 2], n)]
rng = random.Random(46)
cases += [rng.sample(range(-10, 11), rng.randint(1, 6)) for _ in range(900)]
cases += [[1, 2, 3], [0, 1], [1], [-10, -5, 0, 3, 7, 10]]
for nums in cases:
    before = nums.copy()
    result = solve(nums)
    expected = set(itertools.permutations(nums))
    assert nums == before
    assert {tuple(row) for row in result} == expected
    assert len(result) == math.factorial(len(nums)) == len(expected)
    assert len({tuple(row) for row in result}) == len(result)
    assert len({id(row) for row in result}) == len(result)
    assert all(row is not nums and sorted(row) == sorted(nums) for row in result)
    if len(result) > 1:
        saved = copy.deepcopy(result[1:])
        result[0][0] = 999
        assert result[1:] == saved
    assert nums == before

# Observe the actual solution AST. No second DFS implementation exists here.
class Observe(ast.NodeTransformer):
    @staticmethod
    def call(action):
        return ast.Expr(value=ast.Call(func=ast.Name(id='_observe', ctx=ast.Load()), args=[ast.Constant(action), ast.Call(func=ast.Name(id='locals', ctx=ast.Load()), args=[], keywords=[])], keywords=[]))

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if ast.unparse(node.test) == 'used[i]':
            node.body.insert(0, self.call('skip-used'))
            return [self.call('check'), node]
        return node

    def visit_Expr(self, node):
        text = ast.unparse(node.value)
        if text == 'ans.append(path.copy())':
            return [node, self.call('save-copy')]
        if text == 'path.append(nums[i])':
            return [node, self.call('choose')]
        return node

    def visit_Assign(self, node):
        if ast.unparse(node) == 'used[i] = False':
            return [node, self.call('unchoose')]
        return node

module = Observe().visit(ast.parse(source))
outer = module.body[0].body[0]
for index, node in enumerate(outer.body):
    if isinstance(node, ast.Expr) and ast.unparse(node.value) == 'dfs()':
        outer.body[index:index+1] = [Observe.call('initial'), node, Observe.call('done')]
        break
ast.fix_missing_locations(module)
events = []

def observe(action, loc):
    i = loc.get('i')
    events.append({'index': len(events), 'action': action, 'candidateIndex': i,
        'candidate': loc['nums'][i] if i is not None else None,
        'path': loc['path'].copy(), 'used': loc['used'].copy(),
        'answers': copy.deepcopy(loc['ans']), 'depth': len(loc['path'])})

traced = {'_observe': observe}
exec(compile(module, str(EP / 'solution.py'), 'exec'), traced)
nums = [1, 2, 3]
result = traced['Solution']().permute(nums)
assert result == solve(nums)
assert events[-1]['path'] == [] and events[-1]['used'] == [False]*3
for event in events:
    assert len(event['path']) == len(set(event['path']))
    assert sorted(event['path']) == sorted(nums[i] for i, used in enumerate(event['used']) if used)
    assert all(len(row) == 3 for row in event['answers'])
    if event['action'] == 'skip-used':
        assert event['used'][event['candidateIndex']]
    if event['action'] == 'save-copy':
        assert event['answers'][-1] == event['path']
report = {'status':'passed','sourceSha256':sha,'oracle':'stdlib itertools.permutations; result sets compared independent of order',
    'cases':len(cases),'nRange':[1,6],'valueRange':[-10,10],
    'checks':['oracle equality','n! output count','no duplicate permutations','each result is an independent list','mutation isolation across answers','input remains unchanged','trace used/path invariant','six copied results survive final empty path'],
    'traceEvents':len(events),'limitations':'Programmatic source/algorithm checks only; no audio or rendered visual QA in phase 1.'}
(EP/'research/solution-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(EP/'remotion/src/lesson.json').write_text(json.dumps({'source':'solution.py','sourceSha256':sha,'observation':'AST inserted snapshots around original operations; no alternate solver','input':nums,'events':events,'result':result},ensure_ascii=False,indent=2)+'\n')
(EP/'solution.json').write_text(json.dumps({'title':'完整 Python 解法','source':'solution.py','sourceSha256':sha,'lines':source.splitlines()},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
