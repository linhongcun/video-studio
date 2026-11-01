"""Independent quadratic oracle and source-line trace of the production solution.

The animation imports trace.json; it does not implement dailyTemperatures again.
The tracer observes locals at executed source lines and never changes execution.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import random
import sys

EP = Path(__file__).resolve().parents[1]
SOURCE = EP / 'solution.py'
CODE = SOURCE.read_text()
SHA = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('daily_source', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
solve = module.Solution().dailyTemperatures


def oracle(values):
    result = []
    for day, value in enumerate(values):
        result.append(next((future - day for future in range(day + 1, len(values))
                            if values[future] > value), 0))
    return result


def trace(values):
    events = []
    lines = {text.strip(): index + 1 for index, text in enumerate(CODE.splitlines())}
    while_line = lines['while pending and temperature > temperatures[pending[-1]]:']
    pop_line = lines['previous = pending.pop()']
    resolve_line = lines['answer[previous] = today - previous']
    push_line = lines['pending.append(today)']
    previous_line = None
    last_snapshot = None

    def observe(frame, kind, arg):
        nonlocal previous_line, last_snapshot
        if frame.f_code is not solve.__func__.__code__:
            return observe
        state = frame.f_locals
        if 'pending' not in state:
            return observe
        snapshot = dict(today=state.get('today', -1),
                        temperature=state.get('temperature'),
                        pending=list(state['pending']), answer=list(state['answer']))
        if kind == 'line':
            current = frame.f_lineno
            if previous_line == push_line:
                events.append(dict(type='push', sourceLine=push_line, **snapshot))
            elif previous_line == resolve_line:
                day = state['previous']
                events.append(dict(type='resolve', previous=day,
                                   distance=state['answer'][day],
                                   sourceLine=resolve_line, **snapshot))
            if current == while_line:
                if not state['pending']:
                    reason = 'empty'
                    previous = None
                else:
                    previous = state['pending'][-1]
                    old = values[previous]
                    reason = 'warmer' if state['temperature'] > old else (
                        'equal' if state['temperature'] == old else 'cooler')
                events.append(dict(type='compare', previous=previous,
                                   reason=reason, sourceLine=current, **snapshot))
            elif current == resolve_line:
                events.append(dict(type='pop', previous=state['previous'],
                                   sourceLine=pop_line, **snapshot))
            previous_line = current
            last_snapshot = snapshot
        elif kind == 'return':
            events.append(dict(type='finish', result=list(arg), sourceLine=frame.f_lineno,
                               **snapshot))
        return observe

    sys.settrace(observe)
    try:
        answer = solve(values[:])
    finally:
        sys.settrace(None)
    assert answer == oracle(values)
    for index, event in enumerate(events):
        event['id'] = index
        temperatures = [values[i] for i in event['pending']]
        assert all(a >= b for a, b in zip(temperatures, temperatures[1:]))
        for day, wait in enumerate(event['answer']):
            if wait:
                assert values[day + wait] > values[day]
                assert all(t <= values[day] for t in values[day + 1:day + wait])
    return dict(input=values, expected=oracle(values), actual=answer, events=events)


explicit = [
    ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
    ([30, 40, 50, 60], [1, 1, 1, 0]),
    ([30, 60, 90], [1, 1, 0]),
    ([33, 34, 35, 31, 30, 32, 36, 33], [1, 1, 4, 2, 1, 1, 0, 0]),
    ([30, 30, 31], [2, 1, 0]),
    ([100], [0]), ([100, 99, 98, 97], [0, 0, 0, 0]),
    ([30, 30, 30], [0, 0, 0]),
]
for values, expected in explicit:
    before = values[:]
    assert solve(values) == expected == oracle(values)
    assert values == before
exhaustive = 0
for length in range(1, 8):
    for values in itertools.product(range(30, 34), repeat=length):
        assert solve(list(values)) == oracle(values)
        exhaustive += 1
rng = random.Random(73920261025)
for _ in range(3000):
    values = [rng.randint(30, 100) for _ in range(rng.randint(1, 180))]
    assert solve(values[:]) == oracle(values)
# Maximum-size boundary probes have known results and do not invoke quadratic oracle.
large = [100] * 100000
assert solve(large) == [0] * len(large)
large2 = [30] * 99999 + [100]
assert solve(large2) == list(range(99999, -1, -1))
cases = {'main': trace(explicit[3][0]), 'equality': trace(explicit[4][0])}
for case in cases.values():
    n = len(case['input'])
    assert sum(e['type'] == 'push' for e in case['events']) == n
    assert sum(e['type'] == 'pop' for e in case['events']) <= n


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


save(EP / 'solution.json', dict(source='solution.py', sourceSha256=SHA, lines=CODE.splitlines()))
save(EP / 'research/trace.json', dict(
    schemaVersion=1, source='solution.py', sourceSha256=SHA,
    execution='sys.settrace observes the exact production function; no second stack solver',
    dayLabels='Animation shows day index + 1; differences are unchanged.', cases=cases))
save(EP / 'research/algorithm-check.json', dict(
    status='pass', sourceSha256=SHA,
    oracle='Independent quadratic earliest-future-strictly-greater search',
    officialAndBoundaryCases=len(explicit), exhaustiveCases=exhaustive,
    exhaustiveDomain='length 1..7; temperatures 30,31,32,33',
    randomCases=3000, randomSeed=73920261025,
    maxSizeCases=2, maxSize=100000,
    traceCases={key: dict(events=len(value['events']), input=value['input'],
                         actual=value['actual']) for key, value in cases.items()},
    checked=['same input not mutated', 'full output equality', 'strictness for ties',
             'zero when absent', 'pending temperatures non-increasing at each trace event',
             'every committed answer is earliest warmer', 'exactly n actual pushes and <=n pops'],
    limits='Algorithm/source verification only; no media, ASR, human listening, or learning-effect claim.'))
print(json.dumps({'sourceSha256': SHA, 'exhaustive': exhaustive, 'random': 3000,
                  'traceEvents': {k: len(v['events']) for k, v in cases.items()}}))
