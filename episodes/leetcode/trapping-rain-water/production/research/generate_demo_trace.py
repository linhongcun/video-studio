"""Observe the actual solution AST after its assignments; no second solver."""
from pathlib import Path
import ast
import hashlib
import json

EP = Path(__file__).resolve().parents[1]
SOURCE = EP / 'solution.py'
HEIGHT = [3, 0, 2, 0, 4, 0, 1]

def generate(height):
    events = []
    def observe(stage, local):
        previous = events[-1] if events else None
        total = local.get('total', 0)
        event = dict(index=len(events) + 1, stage=stage, i=local['i'],
                     height=height[:], left=local['left'][:], right=local['right'][:],
                     highest=local['highest'], total=total,
                     totalBefore=previous['total'] if previous else 0,
                     level=local.get('level') if stage == 'fill' else None,
                     depth=local.get('depth') if stage == 'fill' else None)
        if stage == 'fill':
            event['water'] = [0] * len(height)
            for old in events:
                if old['stage'] == 'fill':
                    event['water'][old['i']] = old['depth']
            event['water'][event['i']] = event['depth']
        else:
            event['water'] = [0] * len(height)
        events.append(event)
    class ObserveAssignments(ast.NodeTransformer):
        def visit_Assign(self, node):
            self.generic_visit(node)
            target = node.targets[0]
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                if target.value.id in ('left', 'right'):
                    return [node, self.callback(target.value.id)]
            return node
        def visit_AugAssign(self, node):
            self.generic_visit(node)
            if isinstance(node.target, ast.Name) and node.target.id == 'total':
                return [node, self.callback('fill')]
            return node
        @staticmethod
        def callback(stage):
            return ast.Expr(value=ast.Call(func=ast.Name(id='_observe', ctx=ast.Load()),
                            args=[ast.Constant(stage), ast.Call(func=ast.Name(id='locals', ctx=ast.Load()), args=[], keywords=[])], keywords=[]))
    tree = ObserveAssignments().visit(ast.parse(SOURCE.read_text()))
    ast.fix_missing_locations(tree)
    namespace = {'_observe': observe}
    exec(compile(tree, str(SOURCE), 'exec'), namespace)
    actual_input = height[:]
    result = namespace['Solution']().trap(actual_input)
    assert actual_input == height
    return dict(height=height[:], result=result, events=events)

if __name__ == '__main__':
    data = generate(HEIGHT)
    data.update(schemaVersion=1, provisional=False, source='solution.py',
                sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                observation='AST observer inserted after actual left/right assignments and total += depth; snapshots are observed execution, not hand-authored animation answers.',
                indexConvention='Python zero-based; screen columns are i+1.',
                expectedLeft=[3, 3, 3, 3, 4, 4, 4], expectedRight=[4, 4, 4, 4, 4, 1, 1],
                expectedWater=[0, 3, 1, 3, 0, 1, 0])
    for path in [EP / 'research/demo-trace.json', EP / 'remotion/src/lesson.json']:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    display = dict(title='完整 Python 解法', source='solution.py',
                   sourceSha256=data['sourceSha256'], lines=SOURCE.read_text().splitlines())
    (EP / 'solution.json').write_text(json.dumps(display, ensure_ascii=False, indent=2) + '\n')
    print(f"Observed {len(data['events'])} events, result={data['result']}; source={data['sourceSha256']}")
