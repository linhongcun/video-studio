"""Validate identities, original values and links of the actual reversal function."""
from pathlib import Path
from itertools import product
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re

D = Path(__file__).resolve().parents[1]
files = [D / name for name in ['solution.py', 'solution.json', 'article.mdx']]
initial = {p.name: p.read_bytes() for p in files}
source = initial['solution.py'].decode()
assert json.loads(initial['solution.json'])['lines'] == source.splitlines()
blocks = re.findall(r'```python[ \t]*\n(.*?)\n```', initial['article.mdx'].decode(), re.S)
assert len(blocks) == 1, 'Article must contain exactly one complete Python source block'
assert blocks[0].strip() == source.strip(), 'Article/executable mismatch'


class ListNode:
    __slots__ = ('val', 'next')
    constructed = 0

    def __init__(self, val=0, next=None):
        type(self).constructed += 1
        self.val, self.next = val, next


namespace = {'__name__': '__episode_solution__', 'ListNode': ListNode}
exec(compile(source, str(D / 'solution.py'), 'exec'), namespace)
solve = namespace['Solution']().reverseList


def check(values):
    nodes = [ListNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    head = nodes[0] if nodes else None
    constructed_before = ListNode.constructed
    result = solve(head)
    assert ListNode.constructed == constructed_before, 'Solution constructed new ListNodes'
    assert result is (nodes[-1] if nodes else None), 'Returned object is not original tail'
    seen = set()
    current = result
    output_values = []
    for expected in reversed(nodes):
        assert current is expected, 'Node identity/order mismatch'
        assert id(current) not in seen, 'Cycle or repeated node'
        seen.add(id(current))
        output_values.append(current.val)
        current = current.next
    assert current is None, 'Extra output node or cycle after expected tail'
    assert [n.val for n in nodes] == list(values), 'Input node values were exchanged/modified'
    for i, node in enumerate(nodes):
        assert node.next is (nodes[i - 1] if i else None), 'Incorrect reversed link'
    assert output_values == list(reversed(values))
    return dict(length=len(nodes), returnedOriginalTail=True, nodesPreserved=True,
                valuesUnchanged=True, acyclic=True, extraNodeConstructions=0,
                output=output_values if len(nodes) <= 10 else None)


count = 0
for length in range(0, 8):
    for values in product([-1, 0, 1], repeat=length):
        check(values)
        count += 1
explicit_inputs = [[], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4, 5],
                   [1, 1, 1], [5000, -5000, 0], [2, 0, 2, -1, 0]]
explicit = [dict(input=values, **check(values)) for values in explicit_inputs]
maximum = check(list(range(5000)))
for p in files:
    assert p.read_bytes() == initial[p.name], f'Input changed during verification: {p}'
report = dict(status='passed', checkedAtAsiaShanghai=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              method='Direct compile/execute of actual solution.py with independently constructed ListNode objects; expected result is reversed original object identity sequence, not merely reversed values.',
              sourcesSHA256={n: hashlib.sha256(raw).hexdigest() for n, raw in initial.items()},
              displayAndArticleExact=True, exhaustive=dict(lengths='0..7', values=[-1, 0, 1], inputsChecked=count),
              explicit=explicit, maximumLengthCase=maximum,
              limitations='Finite execution verifies these identity/link/value cases; general O(n)/O(1) is justified by source/proof. It does not validate animation, audio, or measured learning outcomes.')
(D / 'research/algorithm-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status='passed', exhaustive=count, explicit=len(explicit) + 1), ensure_ascii=False))
