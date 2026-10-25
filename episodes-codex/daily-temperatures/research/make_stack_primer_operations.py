"""Execute only five elementary stack operations for a labeled concept demo.

This is not dailyTemperatures, not a second solution, and never computes answers.
The chapter deliberately removes and restores day5 to teach the same-end rule.
"""
from pathlib import Path
import hashlib
import json

EP = Path(__file__).resolve().parents[1]
algorithm = json.loads((EP/'research/trace.json').read_text())
values = algorithm['cases']['main']['input']
pending = []
events = [dict(id=0, operation='initial', before=[], after=[], day=None, removed=None)]
for operation, day in [('append', 2), ('append', 3), ('append', 4), ('pop', None), ('append', 4)]:
    before = pending[:]
    if operation == 'append':
        pending.append(day)
        removed = None
        assert pending[-1] == day and pending[:-1] == before
    else:
        removed = pending.pop()
        day = removed
        assert before[-1] == removed and pending == before[:-1]
    events.append(dict(id=len(events), operation=operation, day=day,
                       temperature=values[day], before=before, after=pending[:], removed=removed))
assert events[4]['removed'] == 4
assert events[3]['after'] == events[5]['after'] == [2, 3, 4]
report = dict(schemaVersion=1,
    purpose='Saving-rule concept demonstration only; no waiting-day answers are calculated.',
    visibleLabel='保存规则示意 · 先不写天数',
    execution='Actual Python list.append(day) / list.pop() calls; snapshots are copied after each operation.',
    operationsSource='research/make_stack_primer_operations.py',
    operationsSourceSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    inputSource='research/trace.json', inputSourceSha256=hashlib.sha256((EP/'research/trace.json').read_bytes()).hexdigest(),
    sourceSolutionSha256=algorithm['sourceSha256'],
    dayIndexNote='Stored indices2,3,4 correspond to shown day3,day4,day5.',
    input=values, events=events,
    equalityRelation=dict(source='research/trace.json cases.equality input[:2]', values=algorithm['cases']['equality']['input'][:2],
                          separateExample=True, nonIncreasing=True),
    algorithmExecutionIsSeparate='research/trace.json remains the original exact solution.py execution, unchanged.')
(EP/'research/stack-primer-operations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Executed5 elementary append/pop calls; no algorithm answers computed; pop returns day5 and restore returns the same original order.')
