"""Meaningful independent oracle: horizontally enumerate legal unit-water cells."""
from pathlib import Path
from itertools import product
import hashlib
import importlib.util
import json
import random
from generate_demo_trace import generate

EP = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rain_solution', EP / 'solution.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
solver = module.Solution().trap

def layered_oracle(height):
    # A cell at integer level y traps water iff it is above its column,
    # and some real bar reaches y on each strict side. No prefix/suffix maxima.
    cells = []
    for level in range(1, max(height, default=0) + 1):
        for i, bar in enumerate(height):
            if bar < level and any(x >= level for x in height[:i]) and any(x >= level for x in height[i + 1:]):
                cells.append([i, level])
    return len(cells), cells

cases = [([], 0), ([0], 0), ([5], 0), ([4, 0], 0), ([0, 1, 2, 3], 0),
         ([3, 2, 1, 0], 0), ([2, 2, 2], 0), ([2, 0, 2], 2),
         ([5, 0, 1, 0, 2], 5), ([3, 0, 2, 0, 4, 0, 1], 8),
         ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6), ([4, 2, 0, 3, 2, 5], 9)]
checked = 0
for height, expected in cases:
    original = height[:]
    assert solver(height) == layered_oracle(height)[0] == expected, height
    assert height == original
    checked += 1
for n in range(8):
    for values in product(range(4), repeat=n):
        height = list(values)
        assert solver(height) == layered_oracle(height)[0], height
        checked += 1
rng = random.Random(42)
for _ in range(400):
    height = [rng.randrange(15) for _ in range(rng.randrange(1, 45))]
    assert solver(height) == layered_oracle(height)[0], height
    checked += 1
sample = generate([3, 0, 2, 0, 4, 0, 1])
assert len(sample['events']) == 21
for e in sample['events']:
    if e['stage'] == 'left':
        assert e['left'][e['i']] == max(e['height'][:e['i'] + 1])
    if e['stage'] == 'right':
        assert e['right'][e['i']] == max(e['height'][e['i']:])
    if e['stage'] == 'fill':
        assert sum(e['water']) == e['total']
        assert e['depth'] >= 0
        assert e['total'] - e['totalBefore'] == e['depth']
        assert e['depth'] == e['level'] - e['height'][e['i']]
expected_water = [0, 3, 1, 3, 0, 1, 0]
assert sample['events'][-1]['water'] == expected_water
assert sample['events'][-1]['left'] == [3, 3, 3, 3, 4, 4, 4]
assert sample['events'][-1]['right'] == [4, 4, 4, 4, 4, 1, 1]
# Actual constraint-scale checks with independently known closed-form outcomes.
large = [100000] + [0] * 19998 + [100000]
assert solver(large) == 1999800000
assert solver(list(range(20000))) == 0
report = dict(sourceSha256=hashlib.sha256((EP / 'solution.py').read_bytes()).hexdigest(),
              oracle='Horizontal unit-cell enumeration; strict barriers on both sides; independent from prefix/suffix solver.',
              oracleCaseCount=checked, exhaustive='All arrays length 0..7 over heights 0..3',
              seededRandomCases=400, officialExamples=2, constraintScaleCases=2,
              traceEvents=21, traceChecks='L/R inclusive current column; sum(water)==total at every committed fill; nonnegative depth; delta total == depth; final expected arrays.',
              sampleResult=sample['result'], sampleWater=expected_water,
              layeredWaterCells=layered_oracle(sample['height'])[1], status='passed',
              limits='Algorithm/source checks only; no audio, visual render, ASR, listening, encoded-media or site claim.')
(EP / 'research/algorithm-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f"Passed {checked} independent-oracle cases + 2 full-constraint cases + 21 trace event invariants.")
