"""Cross-check the actual stairs program with exact combinatorial counting."""
from pathlib import Path
from math import comb
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
solve = namespace['Solution']().climbStairs


def combinatorial_count(n):
    # With k double-steps, there are n-k total moves; choose which k are doubles.
    return sum(comb(n - k, k) for k in range(n // 2 + 1))


def enumerate_paths(remaining, prefix=()):
    if remaining == 0:
        return [prefix]
    paths = []
    for step in [1, 2]:
        if step <= remaining:
            paths.extend(enumerate_paths(remaining - step, prefix + (step,)))
    return paths


rows = []
for n in range(1, 46):
    expected = combinatorial_count(n)
    got = solve(n)
    assert type(got) is int and got == expected, (n, got, expected)
    rows.append(dict(n=n, expected=expected, actual=got))
small = []
for n in range(1, 13):
    paths = enumerate_paths(n)
    assert len(paths) == len(set(paths)), 'Enumeration contains duplicates'
    assert all(sum(path) == n and set(path) <= {1, 2} for path in paths)
    assert len(paths) == combinatorial_count(n) == solve(n)
    small.append(dict(n=n, orderedPaths=len(paths)))
assert set(enumerate_paths(3)) == {(1, 1, 1), (1, 2), (2, 1)}
assert solve(6) == 13
for p in files:
    assert p.read_bytes() == initial[p.name], f'Input changed during verification: {p}'
report = dict(status='passed', checkedAtAsiaShanghai=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              method='Direct compile/execute of actual solution.py for all official n=1..45; independent exact sum of binomial coefficients, plus explicit ordered path enumeration for n=1..12. Does not mirror the rolling recurrence.',
              sourcesSHA256={n: hashlib.sha256(raw).hexdigest() for n, raw in initial.items()},
              displayAndArticleExact=True, officialDomain=rows, independentlyEnumeratedSmallInputs=small,
              baseAndTeachingCases=dict(n1=solve(1), n2=solve(2), n3=solve(3), n6=solve(6)),
              limitations='All official n values were executed, but this is not animation/audio/learning validation. Mathematical recurrence and complexity are separately argued in research.md; no claims about untested n outside1..45.')
(D / 'research/algorithm-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status='passed', officialInputs=45, enumeratedSmallInputs=12), ensure_ascii=False))
