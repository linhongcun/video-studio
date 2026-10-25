"""Run the actual submitted solution against an independent pair-enumeration oracle."""
from pathlib import Path
from itertools import product, combinations
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
namespace = {'__name__': '__episode_solution__'}
exec(compile(source, str(D / 'solution.py'), 'exec'), namespace)
solve = namespace['Solution']().twoSum


def oracle(nums, target):
    return [(i, j) for i, j in combinations(range(len(nums)), 2)
            if nums[i] + nums[j] == target]


def check(nums, target, expected):
    before = nums.copy()
    got = solve(nums, target)
    assert nums == before, 'Input array mutated'
    assert isinstance(got, (list, tuple)) and len(got) == 2, (nums, target, got)
    a, b = got
    assert type(a) is int and type(b) is int and a != b
    assert 0 <= a < len(nums) and 0 <= b < len(nums)
    assert nums[a] + nums[b] == target
    assert tuple(sorted(got)) == expected, (nums, target, got, expected)
    return list(got)


counts = {'enumeratedInputs': 0, 'uniqueSolutionInputsChecked': 0,
          'noSolutionInputsExcluded': 0, 'multipleSolutionInputsExcluded': 0}
for size in range(2, 6):
    for values in product(range(-2, 3), repeat=size):
        for target in range(-4, 5):
            counts['enumeratedInputs'] += 1
            pairs = oracle(values, target)
            if not pairs:
                counts['noSolutionInputsExcluded'] += 1
                continue
            if len(pairs) != 1:
                counts['multipleSolutionInputsExcluded'] += 1
                continue
            check(list(values), target, pairs[0])
            counts['uniqueSolutionInputsChecked'] += 1

explicit = [
    ([2, 7, 11, 15], 9), ([3, 2, 4], 6), ([3, 3], 6),
    ([3, 8, 11, 6, 15], 9), ([3, 8, 3], 6),
    ([0, 4, 3, 0], 0), ([-3, 4, 3, 90], 0),
    ([-10**9, 10**9, 5], 0), ([1, 2], 3),
]
records = []
for nums, target in explicit:
    pairs = oracle(nums, target)
    assert len(pairs) == 1
    records.append(dict(nums=nums, target=target, result=check(nums, target, pairs[0])))
large = list(range(9999)) + [-10**9]
large_result = check(large, -10**9, (0, 9999))
for p in files:
    assert p.read_bytes() == initial[p.name], f'Input changed during verification: {p}'
report = dict(status='passed', checkedAtAsiaShanghai=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              method='Direct compile/execute of actual solution.py; independent exhaustive i<j pair enumeration. Only exactly-one-solution inputs count toward official-domain execution tests.',
              sourcesSHA256={n: hashlib.sha256(raw).hexdigest() for n, raw in initial.items()},
              displayAndArticleExact=True, exhaustive=counts, explicit=records,
              maximumLengthCase=dict(length=len(large), target=-10**9, result=large_result),
              properties=['two distinct valid original indices', 'sum equals target', 'input unchanged',
                          'same-valued elements at different indices remain legal'],
              limitations='Finite execution tests do not replace correctness proof, establish average-case hash performance, or validate animation/audio/learning outcomes.')
(D / 'research/algorithm-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status='passed', uniqueExhaustive=counts['uniqueSolutionInputsChecked'], explicit=len(records) + 1), ensure_ascii=False))
